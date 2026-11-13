#!/usr/bin/env python3
"""Build Mihomo providers from one upstream snapshot and local overrides."""
import argparse
from datetime import datetime, timezone
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import time
import urllib.error
import urllib.request
from urllib.parse import urlsplit

import yaml

if __package__:
    from .geodata import service_rules
else:
    from geodata import service_rules

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SERVICES = ROOT / "config" / "services.yaml"
UPSTREAM = "Loyalsoldier/v2ray-rules-dat"
CATEGORIES = ("reject", "direct", "proxy")
GROUP = "Global"


def load_services(path):
    services = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(services, list) or not services:
        raise ValueError(f"{path}: 必须包含至少一个服务")
    ids, names = set(CATEGORIES) | {"manifest", "rules-config", "flclash"}, {GROUP, "DIRECT", "REJECT"}
    for service in services:
        if not isinstance(service, dict) or set(service) - {"id", "name", "geosite", "geoip", "default", "icon"}:
            raise ValueError("服务配置包含未知字段")
        for key in ("id", "name", "geosite", "default", "icon"):
            if not isinstance(service.get(key), str) or not service[key].strip():
                raise ValueError("服务缺少有效字段: " + key)
        identifier, name = service["id"], service["name"]
        if not re.fullmatch(r"[a-z][a-z0-9]*", identifier) or identifier in ids:
            raise ValueError("服务 id 非法或重复: " + identifier)
        if name in names or any(c in name for c in ",\n\r") or name != name.strip():
            raise ValueError("服务组名称非法或重复: " + name)
        for key in ("geosite", "geoip"):
            if key in service and (not isinstance(service[key], str) or not re.fullmatch(r"[a-z0-9!_-]+", service[key])):
                raise ValueError("服务分类非法: " + key)
        if service["default"] not in (GROUP, "DIRECT"):
            raise ValueError("服务 default 必须为 DIRECT 或 " + GROUP)
        icon = urlsplit(service["icon"])
        if icon.scheme != "https" or not icon.hostname or any(c.isspace() for c in service["icon"]):
            raise ValueError("服务 icon 必须为有效的 HTTPS 图标链接")
        ids.add(identifier)
        names.add(name)
    return services


def download(url):
    headers = {"User-Agent": "proxy-rules-builder"}
    if url.startswith("https://api.github.com/") and os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError):
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)


def domain(value):
    value = value.rstrip(".").encode("idna").decode("ascii").lower()
    if len(value) > 253 or not all(re.fullmatch(r"[a-z0-9_](?:[a-z0-9_-]{0,61}[a-z0-9_])?", label) for label in value.split(".")):
        raise ValueError("非法域名: " + value)
    return value


def parse_rule(line):
    """Canonical classical rule; a bare domain includes its subdomains."""
    aliases = {"domain": "DOMAIN-SUFFIX", "full": "DOMAIN", "keyword": "DOMAIN-KEYWORD", "regexp": "DOMAIN-REGEX"}
    prefix, sep, value = line.partition(":")
    if prefix in aliases and sep:
        kind = aliases[prefix]
    elif "," in line:
        kind, value = line.split(",", 1)
    else:
        kind, value = "DOMAIN-SUFFIX", line
    if kind in ("DOMAIN", "DOMAIN-SUFFIX"):
        return kind + "," + domain(value)
    if kind in ("DOMAIN-KEYWORD", "DOMAIN-REGEX"):
        if not value or any(c.isspace() for c in value) or (kind == "DOMAIN-KEYWORD" and "," in value):
            raise ValueError("非法关键词/正则: " + line)
        if kind == "DOMAIN-REGEX":
            # Mihomo treats the entire remainder as regex, including commas.
            re.compile(value)
        return kind + "," + value
    if kind in ("IP-CIDR", "IP-CIDR6"):
        parts = value.split(",")
        if len(parts) > 2 or (len(parts) == 2 and parts[1] != "no-resolve"):
            raise ValueError("IP 规则不应包含策略名: " + line)
        network = ipaddress.ip_network(parts[0], strict=False)
        if network.version != (6 if kind == "IP-CIDR6" else 4):
            raise ValueError("IP 版本与类型不匹配: " + line)
        return kind + "," + str(network) + (",no-resolve" if len(parts) == 2 else "")
    raise ValueError("不支持的规则类型: " + line)


def parse_text(text, source):
    result = set()
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        try:
            result.add(parse_rule(line))
        except (ValueError, UnicodeError, re.error) as error:
            raise ValueError(f"{source}:{number}: {error}") from error
    return result


def split_rules(rules):
    domains, extra = set(), set()
    for rule in rules:
        kind, value = rule.split(",", 1)
        if kind == "DOMAIN-SUFFIX":
            domains.add("+." + value)
        elif kind == "DOMAIN":
            domains.add(value)
        else:
            extra.add(rule)
    return sorted(domains), sorted(extra)


def build(upstream_texts, custom_dir, output, repository, upstream_ref,
          *, services, service_texts, geodata_hashes):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("repository 必须是 owner/repo")
    upstream = {c: parse_text(upstream_texts[c], c + "-list.txt") for c in CATEGORIES}
    if any(not value for value in upstream.values()):
        raise ValueError("上游列表为空，停止构建")
    custom = {}
    for category in CATEGORIES:
        path = custom_dir / (category + ".txt")
        custom[category] = parse_text(path.read_text(encoding="utf-8"), str(path))
    excluded = parse_text((custom_dir / "exclude.txt").read_text(), "exclude.txt")
    # Reject contradictory exact local entries. Overlapping suffixes use ordering.
    for index, category in enumerate(CATEGORIES):
        for other in CATEGORIES[index + 1:]:
            overlap = custom[category] & custom[other]
            if overlap:
                raise ValueError(f"自定义 {category}/{other} 存在重复策略: {sorted(overlap)[:5]}")
    all_custom = set().union(*custom.values())
    payloads, behaviors = {}, {}
    for category in CATEGORIES:
        merged = (upstream[category] - excluded - all_custom) | custom[category]
        domains, extra = split_rules(merged)
        payloads[category] = domains
        behaviors[category] = "domain"
        payloads[category + "-extra"] = extra
        behaviors[category + "-extra"] = "classical"
        payloads["custom-" + category] = sorted(custom[category])
        behaviors["custom-" + category] = "classical"
    for service in services:
        identifier = service["id"]
        entries = parse_text(service_texts[identifier], "geosite/" + identifier)
        if not entries:
            raise ValueError("服务规则为空: " + identifier)
        domains, extra = split_rules(entries - excluded - all_custom)
        payloads[identifier], payloads[identifier + "-extra"] = domains, extra
        behaviors[identifier], behaviors[identifier + "-extra"] = "domain", "classical"
    base = f"https://raw.githubusercontent.com/{repository}/release"
    providers = {
        "pr-" + name: {
            "type": "http",
            "behavior": behaviors[name],
            "format": "yaml",
            "url": f"{base}/{name}.yaml",
            "path": f"./ruleset/proxy-rules/{name}.yaml",
            "interval": 86400,
        }
        for name in payloads
    }
    targets = {"reject": "REJECT", "direct": "DIRECT", "proxy": GROUP}
    rules = [f"RULE-SET,pr-custom-{c},{targets[c]}" for c in CATEGORIES]
    # No external geo database required. Local network stays reachable.
    rules += ["DOMAIN-SUFFIX,lan,DIRECT", "DOMAIN-SUFFIX,local,DIRECT"]
    for cidr in ("0.0.0.0/8", "10.0.0.0/8", "127.0.0.0/8", "169.254.0.0/16", "172.16.0.0/12", "192.168.0.0/16", "100.64.0.0/10"):
        rules.append(f"IP-CIDR,{cidr},DIRECT,no-resolve")
    for cidr in ("::1/128", "fc00::/7", "fe80::/10"):
        rules.append(f"IP-CIDR6,{cidr},DIRECT,no-resolve")
    rules.extend(f"RULE-SET,pr-reject{suffix},REJECT" for suffix in ("", "-extra"))
    # Keep each service's regex/IP rules ahead of later broad domain categories.
    # Extracted IP rules use no-resolve, so they don't trigger extra DNS lookups.
    for service in services:
        rules.extend(f"RULE-SET,pr-{service['id']}{suffix},{service['name']}" for suffix in ("", "-extra"))
    for category in ("proxy", "direct"):
        rules.extend(f"RULE-SET,pr-{category}{suffix},{targets[category]}" for suffix in ("", "-extra"))
    rules.append("MATCH," + GROUP)
    fragment = {"rule-providers": providers, "rules": rules}
    files = {
        name + ".yaml": yaml.safe_dump({"payload": payload}, allow_unicode=True, sort_keys=False)
        for name, payload in payloads.items()
    }
    files["rules-config.yaml"] = yaml.safe_dump(fragment, allow_unicode=True, sort_keys=False)
    script = (ROOT / "templates/flclash.js").read_text()
    files["flclash.js"] = script.replace(
        "__RULE_CONFIG__", json.dumps(fragment, ensure_ascii=False, indent=2)
    ).replace("__SERVICES__", json.dumps(services, ensure_ascii=False, indent=2))
    files["NOTICE.txt"] = (ROOT / "NOTICE").read_text()
    files["LICENSE"] = (ROOT / "LICENSE").read_text()
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository": repository,
        "source_revision": os.environ.get("GITHUB_SHA", "local"),
        "upstream": {
            "repository": UPSTREAM,
            "revision": upstream_ref,
            "sha256": {**geodata_hashes, **{
                category: hashlib.sha256(text.encode()).hexdigest()
                for category, text in upstream_texts.items()
            }},
        },
        "services": services,
        "counts": {name: len(payload) for name, payload in payloads.items()},
        "sha256": {
            name: hashlib.sha256(content.encode()).hexdigest()
            for name, content in files.items()
        },
    }
    files["manifest.json"] = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    # All input validation finishes before existing output is touched.
    output.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        temporary = output / (name + ".tmp")
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(output / name)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", "lzo-catty/proxy-rules"))
    parser.add_argument("--upstream-dir", type=Path, help="本地 upstream release 快照目录（离线构建）")
    parser.add_argument("--upstream-ref", help="本地快照版本，或要下载的上游 commit SHA")
    parser.add_argument("--custom-dir", type=Path, default=ROOT / "rules")
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    parser.add_argument("--services", type=Path, default=DEFAULT_SERVICES,
                        help="服务策略配置（默认：config/services.yaml）")
    args = parser.parse_args()
    services = load_services(args.services)
    if args.upstream_dir:
        revision = args.upstream_ref or "local"
        texts = {c: (args.upstream_dir / (c + "-list.txt")).read_text(encoding="utf-8") for c in CATEGORIES}
        geodata = {name: (args.upstream_dir / name).read_bytes() for name in ("geosite.dat", "geoip.dat")}
    else:
        revision = args.upstream_ref or json.loads(download(f"https://api.github.com/repos/{UPSTREAM}/commits/release"))["sha"]
        if not re.fullmatch(r"[0-9a-f]{40}", revision):
            parser.error("远程上游版本必须是完整 commit SHA")
        texts = {c: download(f"https://raw.githubusercontent.com/{UPSTREAM}/{revision}/{c}-list.txt").decode("utf-8") for c in CATEGORIES}
        geodata = {name: download(f"https://raw.githubusercontent.com/{UPSTREAM}/{revision}/{name}")
                   for name in ("geosite.dat", "geoip.dat")}
    extracted = service_rules(geodata["geosite.dat"], geodata["geoip.dat"], services)
    manifest = build(
        texts, args.custom_dir, args.output, args.repository, revision,
        services=services, service_texts=extracted,
        geodata_hashes={name: hashlib.sha256(data).hexdigest() for name, data in geodata.items()},
    )
    print(json.dumps(manifest["counts"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
