import hashlib
from pathlib import Path
import re
import tempfile
import unittest

import yaml

from scripts.build import ROOT, build, load_services, parse_rule, parse_text, split_rules


class RuleTests(unittest.TestCase):
    def test_semantics_and_normalization(self):
        self.assertEqual(parse_rule("Example.COM."), "DOMAIN-SUFFIX,example.com")
        self.assertEqual(parse_rule("full:Example.COM"), "DOMAIN,example.com")
        self.assertEqual(parse_rule("domain:example.com"), parse_rule("example.com"))
        self.assertEqual(parse_rule("keyword:video"), "DOMAIN-KEYWORD,video")
        self.assertEqual(parse_rule("IP-CIDR,10.1.2.3/8,no-resolve"), "IP-CIDR,10.0.0.0/8,no-resolve")
        domains, extra = split_rules({parse_rule("example.com"), parse_rule("full:exact.com"), parse_rule("keyword:video")})
        self.assertEqual(domains, ["+.example.com", "exact.com"])
        self.assertEqual(extra, ["DOMAIN-KEYWORD,video"])

    def test_regex_quantifier_preserves_matches(self):
        for expression in (r"^x[0-9]{0,3}\.com$", r"^[a-z]{1,2}\d{2,}\.net$"):
            rewritten = parse_rule("regexp:" + expression).split(",", 1)[1]
            self.assertEqual(rewritten, expression)
            for candidate in ("x.com", "x1.com", "x123.com", "x1234.com", "ab12.net", "a123456.net", "abc12.net", "a1.net"):
                self.assertEqual(bool(re.search(expression, candidate)), bool(re.search(rewritten, candidate)))

    def test_invalid_rules_fail_with_line_number(self):
        for invalid in ("https://example.com", "DOMAIN,example.com,DIRECT", "DOMAIN-SUFFIX,*.example.com", "MATCH,DIRECT", "IP-CIDR6,10.0.0.0/8", "regexp:[", "<html>error</html>", "keyword:x,y"):
            with self.subTest(invalid=invalid), self.assertRaisesRegex(ValueError, "input:2:"):
                parse_text("# comment\n" + invalid, "input")

    def test_comments_dedup(self):
        self.assertEqual(parse_text("# hello\n\nEXAMPLE.COM\ndomain:example.com", "input"), {"DOMAIN-SUFFIX,example.com"})


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.custom = self.root / "rules"
        self.custom.mkdir()
        for name in ("direct", "proxy", "reject", "exclude"):
            (self.custom / (name + ".txt")).write_text("")
        self.output = self.root / "dist"
        self.upstream = {"direct": "cn.example\nshared.example", "proxy": "world.example\nshared.example", "reject": "ads.example\nfull:login.example\nkeyword:tracking"}
        self.services = load_services(ROOT / "services.yaml")
        self.service_texts = {s["id"]: s["id"] + ".example" for s in self.services}

    def run_build(self):
        return build(self.upstream, self.custom, self.output, "owner/repo", "a" * 40,
                     services=self.services, service_texts=self.service_texts, geodata_hashes={})

    def payload(self, name):
        return yaml.safe_load((self.output / (name + ".yaml")).read_text())["payload"]

    def test_override_exclude_and_priority(self):
        (self.custom / "direct.txt").write_text("full:login.example\nshared.example")
        (self.custom / "exclude.txt").write_text("ads.example")
        manifest = self.run_build()
        self.assertNotIn("+.shared.example", self.payload("proxy"))
        self.assertNotIn("login.example", self.payload("reject"))
        self.assertNotIn("+.ads.example", self.payload("reject"))
        self.assertIn("login.example", self.payload("direct"))
        fragment = yaml.safe_load((self.output / "rules-config.yaml").read_text())
        self.assertEqual(fragment["rules"][:3], ["RULE-SET,pr-custom-reject,REJECT", "RULE-SET,pr-custom-direct,DIRECT", "RULE-SET,pr-custom-proxy,Global"])
        self.assertEqual(fragment["rules"][-1], "MATCH,Global")
        self.assertTrue(all("owner/repo/release/" in p["url"] for p in fragment["rule-providers"].values()))
        self.assertEqual(manifest["counts"]["custom-proxy"], 0)
        for filename, digest in manifest["sha256"].items():
            self.assertEqual(hashlib.sha256((self.output / filename).read_bytes()).hexdigest(), digest)

    def test_subdomain_override_is_kept_ahead_of_parent(self):
        (self.custom / "direct.txt").write_text("full:login.ads.example")
        self.run_build()
        self.assertIn("+.ads.example", self.payload("reject"))
        self.assertIn("DOMAIN,login.ads.example", self.payload("custom-direct"))

    def test_conflicting_local_rules_fail(self):
        (self.custom / "direct.txt").write_text("example.com")
        (self.custom / "proxy.txt").write_text("domain:example.com")
        with self.assertRaisesRegex(ValueError, "重复策略"):
            self.run_build()
        self.assertFalse(self.output.exists())

    def test_bad_upstream_preserves_last_output(self):
        self.run_build()
        previous = (self.output / "manifest.json").read_bytes()
        for invalid in ("", "<html>error</html>"):
            self.upstream["direct"] = invalid
            with self.assertRaises(ValueError):
                self.run_build()
            self.assertEqual((self.output / "manifest.json").read_bytes(), previous)

    def test_repeat_build_is_deterministic_except_manifest_time(self):
        first = self.run_build()
        second = self.run_build()
        self.assertEqual(first["sha256"], second["sha256"])

    def test_service_priority_and_telegram_ip(self):
        self.service_texts["telegram"] += "\nIP-CIDR,91.108.0.0/16,no-resolve"
        self.run_build()
        fragment = yaml.safe_load((self.output / "rules-config.yaml").read_text())
        rules = fragment["rules"]
        self.assertLess(rules.index("RULE-SET,pr-reject,REJECT"), rules.index("RULE-SET,pr-telegram,Telegram"))
        self.assertLess(rules.index("RULE-SET,pr-google,Google"), rules.index("RULE-SET,pr-telegram-extra,Telegram"))
        self.assertLess(rules.index("RULE-SET,pr-telegram-extra,Telegram"), rules.index("RULE-SET,pr-proxy,Global"))
        self.assertEqual(self.payload("telegram-extra"), ["IP-CIDR,91.108.0.0/16,no-resolve"])
        self.assertEqual(len(fragment["rule-providers"]), 19)

    def test_global_overrides_and_exclusions_apply_to_services(self):
        self.service_texts["apple"] += "\nblocked.example"
        (self.custom / "proxy.txt").write_text("apple.example")
        (self.custom / "exclude.txt").write_text("blocked.example")
        self.run_build()
        self.assertEqual(self.payload("apple"), [])
        self.assertIn("DOMAIN-SUFFIX,apple.example", self.payload("custom-proxy"))

    def test_missing_or_empty_service_never_overwrites_output(self):
        self.run_build()
        previous = (self.output / "manifest.json").read_bytes()
        self.service_texts["telegram"] = ""
        with self.assertRaisesRegex(ValueError, "服务规则为空"):
            self.run_build()
        self.assertEqual((self.output / "manifest.json").read_bytes(), previous)

    def test_service_configuration_rejects_collisions_and_invalid_targets(self):
        for change in ({"id": "direct"}, {"name": "Global"}, {"default": "missing"}, {"name": "bad,name"}, {"geoip": "../bad"}):
            services = [dict(self.services[0], **change)]
            path = self.root / "services.yaml"
            path.write_text(yaml.safe_dump(services, allow_unicode=True))
            with self.subTest(change=change), self.assertRaises(ValueError):
                load_services(path)


if __name__ == "__main__":
    unittest.main()
