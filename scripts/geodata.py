"""Read the routing fields of V2Ray GeoSiteList / GeoIPList using protobuf.

Wire schema reference:
https://github.com/v2fly/v2ray-core/blob/master/app/router/routercommon/common.proto
Attributes and resource metadata are deliberately left as unknown fields: service
categories include all their domains, without filtering @cn or other attributes.
The small descriptor avoids requiring protoc on every daily build.
"""
import ipaddress

from google.protobuf import descriptor_pb2, descriptor_pool, message_factory
from google.protobuf.message import DecodeError


def message_classes():
    field = descriptor_pb2.FieldDescriptorProto
    schema = descriptor_pb2.FileDescriptorProto(
        name="routing_subset.proto", package="proxy_rules", syntax="proto3"
    )
    definitions = {
        "Domain": [("type", 1, field.TYPE_INT32, False, None),
                   ("value", 2, field.TYPE_STRING, False, None)],
        "GeoSite": [("country_code", 1, field.TYPE_STRING, False, None),
                    ("domain", 2, field.TYPE_MESSAGE, True, "Domain")],
        "GeoSiteList": [("entry", 1, field.TYPE_MESSAGE, True, "GeoSite")],
        "CIDR": [("ip", 1, field.TYPE_BYTES, False, None),
                 ("prefix", 2, field.TYPE_UINT32, False, None)],
        "GeoIP": [("country_code", 1, field.TYPE_STRING, False, None),
                  ("cidr", 2, field.TYPE_MESSAGE, True, "CIDR"),
                  ("inverse_match", 3, field.TYPE_BOOL, False, None)],
        "GeoIPList": [("entry", 1, field.TYPE_MESSAGE, True, "GeoIP")],
    }
    for name, fields in definitions.items():
        message = schema.message_type.add(name=name)
        for label, number, kind, repeated, target in fields:
            item = message.field.add(
                name=label, number=number, type=kind,
                label=field.LABEL_REPEATED if repeated else field.LABEL_OPTIONAL,
            )
            if target:
                item.type_name = ".proxy_rules." + target
    pool = descriptor_pool.DescriptorPool()
    pool.Add(schema)
    return tuple(message_factory.GetMessageClass(pool.FindMessageTypeByName("proxy_rules." + name))
                 for name in ("GeoSiteList", "GeoIPList"))


GeoSiteList, GeoIPList = message_classes()


def select_entries(data, message_class, categories, source):
    message = message_class()
    try:
        message.ParseFromString(data)
    except DecodeError as error:
        raise ValueError(f"{source}: 无效 protobuf 数据") from error
    selected = {}
    wanted = set(categories)
    for entry in message.entry:
        key = entry.country_code.lower()
        if key in wanted:
            if key in selected:
                raise ValueError(f"{source}: 分类重复: {key}")
            selected[key] = entry
    missing = wanted - selected.keys()
    if missing:
        raise ValueError(f"{source}: 缺少分类: {sorted(missing)}")
    return selected


def service_rules(geosite, geoip, services):
    sites = select_entries(geosite, GeoSiteList, [s["geosite"] for s in services], "geosite.dat")
    ips = select_entries(geoip, GeoIPList, [s["geoip"] for s in services if s.get("geoip")], "geoip.dat")
    prefixes = {0: "keyword:", 1: "regexp:", 2: "domain:", 3: "full:"}
    result = {}
    for service in services:
        entry = sites[service["geosite"]]
        if not entry.domain:
            raise ValueError("geosite 分类为空: " + service["geosite"])
        rules = []
        for item in entry.domain:
            if item.type not in prefixes:
                raise ValueError(f"{service['geosite']}: 未知域名类型 {item.type}")
            rules.append(prefixes[item.type] + item.value)
        if service.get("geoip"):
            entry = ips[service["geoip"]]
            if entry.inverse_match or not entry.cidr:
                raise ValueError("不支持反向或空 geoip 分类: " + service["geoip"])
            for cidr in entry.cidr:
                address = ipaddress.ip_address(cidr.ip)
                network = ipaddress.ip_network(f"{address}/{cidr.prefix}", strict=False)
                kind = "IP-CIDR6" if address.version == 6 else "IP-CIDR"
                rules.append(f"{kind},{network},no-resolve")
        result[service["id"]] = "\n".join(rules)
    return result
