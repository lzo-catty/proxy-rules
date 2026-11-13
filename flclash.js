// 从 FlClash 的脚本管理导入此文件 URL，再在节点订阅的扩展中选用。
// 此脚本接管 rules，保留节点、原策略组、DNS 和其他连接配置。
const RULE_CONFIG = {
  "rule-providers": {
    "pr-reject": {
      "type": "http",
      "behavior": "domain",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/reject.yaml",
      "path": "./ruleset/proxy-rules/reject.yaml",
      "interval": 86400
    },
    "pr-reject-extra": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/reject-extra.yaml",
      "path": "./ruleset/proxy-rules/reject-extra.yaml",
      "interval": 86400
    },
    "pr-custom-reject": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/custom-reject.yaml",
      "path": "./ruleset/proxy-rules/custom-reject.yaml",
      "interval": 86400
    },
    "pr-direct": {
      "type": "http",
      "behavior": "domain",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/direct.yaml",
      "path": "./ruleset/proxy-rules/direct.yaml",
      "interval": 86400
    },
    "pr-direct-extra": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/direct-extra.yaml",
      "path": "./ruleset/proxy-rules/direct-extra.yaml",
      "interval": 86400
    },
    "pr-custom-direct": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/custom-direct.yaml",
      "path": "./ruleset/proxy-rules/custom-direct.yaml",
      "interval": 86400
    },
    "pr-proxy": {
      "type": "http",
      "behavior": "domain",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/proxy.yaml",
      "path": "./ruleset/proxy-rules/proxy.yaml",
      "interval": 86400
    },
    "pr-proxy-extra": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/proxy-extra.yaml",
      "path": "./ruleset/proxy-rules/proxy-extra.yaml",
      "interval": 86400
    },
    "pr-custom-proxy": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/custom-proxy.yaml",
      "path": "./ruleset/proxy-rules/custom-proxy.yaml",
      "interval": 86400
    }
  },
  "rules": [
    "RULE-SET,pr-custom-reject,REJECT",
    "RULE-SET,pr-custom-direct,DIRECT",
    "RULE-SET,pr-custom-proxy,自定义分流",
    "DOMAIN-SUFFIX,lan,DIRECT",
    "DOMAIN-SUFFIX,local,DIRECT",
    "IP-CIDR,0.0.0.0/8,DIRECT,no-resolve",
    "IP-CIDR,10.0.0.0/8,DIRECT,no-resolve",
    "IP-CIDR,127.0.0.0/8,DIRECT,no-resolve",
    "IP-CIDR,169.254.0.0/16,DIRECT,no-resolve",
    "IP-CIDR,172.16.0.0/12,DIRECT,no-resolve",
    "IP-CIDR,192.168.0.0/16,DIRECT,no-resolve",
    "IP-CIDR,100.64.0.0/10,DIRECT,no-resolve",
    "IP-CIDR6,::1/128,DIRECT,no-resolve",
    "IP-CIDR6,fc00::/7,DIRECT,no-resolve",
    "IP-CIDR6,fe80::/10,DIRECT,no-resolve",
    "RULE-SET,pr-reject,REJECT",
    "RULE-SET,pr-reject-extra,REJECT",
    "RULE-SET,pr-proxy,自定义分流",
    "RULE-SET,pr-proxy-extra,自定义分流",
    "RULE-SET,pr-direct,DIRECT",
    "RULE-SET,pr-direct-extra,DIRECT",
    "MATCH,自定义分流"
  ]
};
const GROUP = "自定义分流";

function main(config) {
  const groups = config["proxy-groups"] || [];
  const nodes = (config.proxies || []).map(function (node) { return node.name; });
  const providers = Object.keys(config["proxy-providers"] || {});
  if (nodes.indexOf(GROUP) !== -1 || groups.some(function (g) { return g.name === GROUP; })) {
    throw new Error("订阅已有“" + GROUP + "”名称，请先重命名以避免冲突");
  }
  // 优先沿用订阅的第一个策略组；同时兼容只有节点或 proxy-providers 的订阅。
  const choices = groups.map(function (g) { return g.name; }).concat(nodes);
  if (!choices.length && !providers.length) {
    throw new Error("请将分流脚本绑定到包含代理节点的订阅");
  }
  const group = { name: GROUP, type: "select", proxies: choices };
  if (providers.length) group.use = providers;
  if (choices.length) group.proxies.push("DIRECT");
  config["proxy-groups"] = groups.concat([group]);
  config["rule-providers"] = Object.assign({}, config["rule-providers"] || {}, RULE_CONFIG["rule-providers"]);
  config.rules = RULE_CONFIG.rules.slice();
  config.mode = "rule";
  return config;
}
