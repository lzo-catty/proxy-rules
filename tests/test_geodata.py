import unittest

from scripts.geodata import GeoIPList, GeoSiteList, service_rules


class GeodataTests(unittest.TestCase):
    def setUp(self):
        self.sites = GeoSiteList()
        entry = self.sites.entry.add(country_code="TELEGRAM")
        for kind, value in ((0, "telegram"), (1, r"^t[0-9]{1,3}\.example$"), (2, "telegram.org"), (3, "exact.example")):
            entry.domain.add(type=kind, value=value)
        self.ips = GeoIPList()
        entry = self.ips.entry.add(country_code="TELEGRAM")
        entry.cidr.add(ip=bytes([91, 108, 0, 0]), prefix=16)
        entry.cidr.add(ip=bytes.fromhex("20010b28000000000000000000000000"), prefix=32)
        self.services = [{"id": "telegram", "geosite": "telegram", "geoip": "telegram"}]

    def extract(self):
        return service_rules(self.sites.SerializeToString(), self.ips.SerializeToString(), self.services)

    def test_extracts_four_domain_types_and_ipv4_ipv6(self):
        self.assertEqual(self.extract()["telegram"].splitlines(), [
            "keyword:telegram", r"regexp:^t[0-9]{1,3}\.example$", "domain:telegram.org", "full:exact.example",
            "IP-CIDR,91.108.0.0/16,no-resolve", "IP-CIDR6,2001:b28::/32,no-resolve",
        ])

    def test_corrupted_data_fails(self):
        with self.assertRaisesRegex(ValueError, "protobuf"):
            service_rules(b"<html>error</html>", b"", self.services)

    def test_missing_category_fails(self):
        self.services[0]["geosite"] = "missing"
        with self.assertRaisesRegex(ValueError, "缺少分类"):
            self.extract()

    def test_empty_category_fails(self):
        self.sites.entry[0].ClearField("domain")
        with self.assertRaisesRegex(ValueError, "分类为空"):
            self.extract()

    def test_unsupported_domain_type_fails(self):
        self.sites.entry[0].domain[0].type = 99
        with self.assertRaisesRegex(ValueError, "未知域名类型"):
            self.extract()

    def test_inverse_ip_category_fails(self):
        self.ips.entry[0].inverse_match = True
        with self.assertRaisesRegex(ValueError, "反向"):
            self.extract()

    def test_invalid_cidr_fails(self):
        self.ips.entry[0].cidr[0].prefix = 33
        with self.assertRaises(ValueError):
            self.extract()

    def test_duplicate_category_fails(self):
        self.sites.entry.add(country_code="telegram")
        with self.assertRaisesRegex(ValueError, "分类重复"):
            self.extract()
