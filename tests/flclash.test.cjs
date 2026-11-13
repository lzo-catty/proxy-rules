const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const test = require("node:test");

const fragment = { "rule-providers": { "pr-direct": { type: "http", behavior: "domain", url: "https://example.com/direct.yaml" } }, rules: ["RULE-SET,pr-direct,DIRECT", "MATCH,Global"] };
const services = [
  { name: "Telegram", default: "Global", icon: "https://example.com/telegram.png" },
  { name: "Apple", default: "DIRECT", icon: "https://example.com/apple.png" },
];
const script = fs.readFileSync("templates/flclash.js", "utf8")
  .replace("__RULE_CONFIG__", JSON.stringify(fragment))
  .replace("__SERVICES__", JSON.stringify(services));
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
  const preserved = { ...result["proxy-groups"][0] };
  delete preserved.icon;
  assert.deepEqual(preserved, original["proxy-groups"][0]);
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
  assert.throws(() => apply({ proxies: [{ name: "Global" }] }), /重命名/);
  assert.throws(() => apply({ "proxy-groups": [{ name: "Global" }] }), /重命名/);
  assert.throws(() => apply({ "proxy-groups": [{ name: "Apple" }] }), /重命名/);
  assert.throws(() => apply({ proxies: [{ name: "Telegram" }] }), /重命名/);
});

test("each service independently offers every node and the configured default", () => {
  const result = apply({ proxies: [{ name: "香港" }, { name: "日本" }], "proxy-groups": [{ name: "机场选择", type: "select", proxies: ["香港"] }] });
  for (const service of services) {
    const group = result["proxy-groups"].find(g => g.name === service.name);
    assert.equal(group.type, "select");
    assert.equal(group.icon, service.icon);
    assert.equal(group.proxies[0], service.default);
    for (const name of ["香港", "日本", "机场选择", "DIRECT", "Global"]) assert.ok(group.proxies.includes(name));
    assert.equal(new Set(group.proxies).size, group.proxies.length);
    for (const other of services) assert.ok(!group.proxies.includes(other.name));
  }
  const fallback = result["proxy-groups"].find(g => g.name === "Global");
  assert.ok(!fallback.proxies.some(name => services.some(s => s.name === name)));
});

test("adds icons to all groups while preserving original custom icons", () => {
  const original = {
    proxies: [{ name: "节点 A" }],
    "proxy-groups": [
      { name: "机场选择", type: "select", proxies: ["节点 A"], icon: "https://example.com/custom.svg" },
      { name: "自动选择", type: "select", proxies: ["节点 A"] },
      { name: "直连", type: "select", proxies: ["DIRECT"], icon: "" },
    ],
  };
  const result = apply(structuredClone(original));
  for (const group of result["proxy-groups"]) assert.match(group.icon, /^https:\/\//);
  assert.deepEqual(result["proxy-groups"][0], original["proxy-groups"][0]);
  assert.equal(original["proxy-groups"][1].icon, undefined);
  assert.match(result["proxy-groups"].find(g => g.name === "Global").icon, /Global\.png$/);
});

test("every service can select nodes from proxy-provider-only subscriptions", () => {
  const result = apply({ "proxy-providers": { airportA: { type: "http" }, airportB: { type: "file" } } });
  for (const service of services) {
    const group = result["proxy-groups"].find(g => g.name === service.name);
    assert.deepEqual(group.use, ["airportA", "airportB"]);
    assert.equal(group.proxies[0], service.default);
    assert.deepEqual(new Set(group.proxies), new Set(["DIRECT", "Global"]));
  }
});
