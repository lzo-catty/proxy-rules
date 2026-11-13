const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const test = require("node:test");

const fragment = { "rule-providers": { "pr-direct": { type: "http", behavior: "domain", url: "https://example.com/direct.yaml" } }, rules: ["RULE-SET,pr-direct,DIRECT", "MATCH,自定义分流"] };
const script = fs.readFileSync("templates/flclash.js", "utf8").replace("__RULE_CONFIG__", JSON.stringify(fragment));
function apply(config) {
  const context = vm.createContext({ config });
  vm.runInContext(script + "\nresult = main(config);", context);
  return JSON.parse(JSON.stringify(context.result));
}

test("preserves subscription nodes, groups and DNS while replacing routing", () => {
  const original = { proxies: [{ name: "节点 A", type: "ss" }], "proxy-groups": [{ name: "机场选择", type: "select", proxies: ["节点 A"] }], dns: { enable: true }, rules: ["MATCH,DIRECT"], "rule-providers": { existing: { type: "file" } } };
  const result = apply(structuredClone(original));
  assert.deepEqual(result.proxies, original.proxies);
  assert.deepEqual(result.dns, original.dns);
  assert.deepEqual(result["proxy-groups"][0], original["proxy-groups"][0]);
  assert.equal(result["proxy-groups"][1].proxies[0], "机场选择");
  assert.deepEqual(result.rules, fragment.rules);
  assert.deepEqual(result["rule-providers"].existing, original["rule-providers"].existing);
  assert.equal(result.mode, "rule");
});

test("accepts proxy-provider-only subscriptions", () => {
  const result = apply({ "proxy-providers": { airport: { type: "http" } } });
  assert.deepEqual(result["proxy-groups"][0].use, ["airport"]);
  assert.deepEqual(result["proxy-groups"][0].proxies, []);
});

test("accepts subscriptions with nodes only", () => {
  const result = apply({ proxies: [{ name: "节点 A" }] });
  assert.deepEqual(result["proxy-groups"][0].proxies, ["节点 A", "DIRECT"]);
});

test("reports missing nodes and group-name collisions", () => {
  assert.throws(() => apply({}), /包含代理节点/);
  assert.throws(() => apply({ proxies: [{ name: "自定义分流" }] }), /重命名/);
  assert.throws(() => apply({ "proxy-groups": [{ name: "自定义分流" }] }), /重命名/);
});
