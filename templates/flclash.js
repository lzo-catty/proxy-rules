// 从 FlClash 的脚本管理导入此文件 URL，再在节点订阅的扩展中选用。
// 此脚本接管 rules，保留节点、原策略组、DNS 和其他连接配置。
const RULE_CONFIG = __RULE_CONFIG__;
const SERVICES = __SERVICES__;
const GROUP = "自定义分流";

function main(config) {
  const groups = config["proxy-groups"] || [];
  const nodes = (config.proxies || []).map(function (node) { return node.name; });
  const providers = Object.keys(config["proxy-providers"] || {});
  const existing = groups.map(function (g) { return g.name; }).concat(nodes);
  [GROUP].concat(SERVICES.map(function (s) { return s.name; })).forEach(function (name) {
    if (existing.indexOf(name) !== -1) {
      throw new Error("订阅已有“" + name + "”名称，请先重命名以避免冲突");
    }
  });
  // 优先沿用订阅的第一个策略组；同时兼容只有节点或 proxy-providers 的订阅。
  const choices = Array.from(new Set(existing));
  if (!choices.length && !providers.length) {
    throw new Error("请将分流脚本绑定到包含代理节点的订阅");
  }
  const group = { name: GROUP, type: "select", proxies: choices.slice() };
  if (providers.length) group.use = providers;
  if (choices.length) group.proxies.push("DIRECT");
  const serviceGroups = SERVICES.map(function (service) {
    // Never reference other generated service groups: prevents routing loops.
    const candidates = [service.default, GROUP, "DIRECT"].concat(choices);
    const result = { name: service.name, type: "select", proxies: Array.from(new Set(candidates)) };
    if (providers.length) result.use = providers.slice();
    return result;
  });
  config["proxy-groups"] = groups.concat([group], serviceGroups);
  config["rule-providers"] = Object.assign({}, config["rule-providers"] || {}, RULE_CONFIG["rule-providers"]);
  config.rules = RULE_CONFIG.rules.slice();
  config.mode = "rule";
  return config;
}
