#!/usr/bin/env python3
"""Load every generated rule in a real Mihomo process and check provider counts."""
import argparse
import json
from pathlib import Path
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from urllib.parse import quote

import yaml


def verify(output, binary):
    output = output.resolve()
    manifest = json.loads((output / "manifest.json").read_text())
    # Validate the actual generated script and its policy groups, not a stand-in.
    profile = {
        "proxies": [
            {"name": name, "type": "http", "server": "127.0.0.1", "port": 9}
            for name in ("测试节点A", "测试节点B")
        ],
        "proxy-groups": [{"name": "Apple", "type": "select", "proxies": ["测试节点A"]}],
    }
    rendered = subprocess.run(
        ["node", str(Path(__file__).with_name("render-profile.cjs")), str(output / "flclash.js")],
        input=json.dumps(profile), text=True, capture_output=True, check=True,
    )
    fragment = json.loads(rendered.stdout)
    with tempfile.TemporaryDirectory(prefix="proxy-rules-check-") as directory:
        home = Path(directory)
        for name, provider in fragment["rule-providers"].items():
            filename = name.removeprefix("pr-") + ".yaml"
            (home / filename).write_bytes((output / filename).read_bytes())
            provider.update(type="file", path="./" + filename)
            provider.pop("url")
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        config = {**fragment, "mode": "rule", "log-level": "warning", "external-controller": f"127.0.0.1:{port}", "secret": "local-validation"}
        config_path = home / "config.yaml"
        config_path.write_text(yaml.safe_dump(config, allow_unicode=True))
        subprocess.run([binary, "-t", "-d", directory, "-f", str(config_path)], check=True)
        # -t alone does not prove all provider entries parsed successfully.
        with (home / "core.log").open("w+") as log:
            process = subprocess.Popen([binary, "-d", directory, "-f", str(config_path)], stdout=log, stderr=log)
            try:
                expected = {"pr-" + name: count for name, count in manifest["counts"].items()}
                actual = {}
                opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
                for _ in range(150):
                    if process.poll() is not None:
                        break
                    try:
                        request = urllib.request.Request(f"http://127.0.0.1:{port}/providers/rules", headers={"Authorization": "Bearer local-validation"})
                        with opener.open(request, timeout=1) as response:
                            data = json.load(response)
                        actual = {name: item["ruleCount"] for name, item in data["providers"].items()}
                        if actual == expected:
                            verify_groups(opener, port, manifest["services"])
                            print("Mihomo loaded all providers:", actual)
                            return
                    except (urllib.error.URLError, TimeoutError):
                        pass
                    time.sleep(0.2)
                log.seek(0)
                raise RuntimeError(f"Provider counts differ: expected={expected}, actual={actual}\n{log.read()}")
            finally:
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()


def verify_groups(opener, port, services):
    def api(path, data=None):
        request = urllib.request.Request(
            f"http://127.0.0.1:{port}/{path}",
            headers={"Authorization": "Bearer local-validation", "Content-Type": "application/json"},
            data=None if data is None else json.dumps(data).encode(),
            method="GET" if data is None else "PUT",
        )
        with opener.open(request, timeout=3) as response:
            return json.load(response) if data is None else None

    before = api("proxies")["proxies"]
    for service in services:
        group = before[service["name"]]
        if group["type"] != "Selector" or group["now"] != service["default"]:
            raise RuntimeError("服务组类型或默认出口错误: " + service["name"])
        if not {"测试节点A", "测试节点B", "DIRECT", "自定义分流"}.issubset(group["all"]):
            raise RuntimeError("服务组缺少可选出口: " + service["name"])
    # Every group must be independently switchable without changing its peers.
    for service in services:
        api("proxies/" + quote(service["name"], safe=""), {"name": "测试节点B"})
        after = api("proxies")["proxies"]
        for other in services:
            expected = "测试节点B" if other == service else other["default"]
            if after[other["name"]]["now"] != expected:
                raise RuntimeError("服务组不能独立切换: " + other["name"])
        api("proxies/" + quote(service["name"], safe=""), {"name": service["default"]})
    print("Mihomo verified independent selectors:", [s["name"] for s in services])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("dist"))
    parser.add_argument("--mihomo", required=True)
    args = parser.parse_args()
    verify(args.output, args.mihomo)
