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
    },
    "pr-bilibili": {
      "type": "http",
      "behavior": "domain",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/bilibili.yaml",
      "path": "./ruleset/proxy-rules/bilibili.yaml",
      "interval": 86400
    },
    "pr-bilibili-extra": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/bilibili-extra.yaml",
      "path": "./ruleset/proxy-rules/bilibili-extra.yaml",
      "interval": 86400
    },
    "pr-telegram": {
      "type": "http",
      "behavior": "domain",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/telegram.yaml",
      "path": "./ruleset/proxy-rules/telegram.yaml",
      "interval": 86400
    },
    "pr-telegram-extra": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/telegram-extra.yaml",
      "path": "./ruleset/proxy-rules/telegram-extra.yaml",
      "interval": 86400
    },
    "pr-youtube": {
      "type": "http",
      "behavior": "domain",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/youtube.yaml",
      "path": "./ruleset/proxy-rules/youtube.yaml",
      "interval": 86400
    },
    "pr-youtube-extra": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/youtube-extra.yaml",
      "path": "./ruleset/proxy-rules/youtube-extra.yaml",
      "interval": 86400
    },
    "pr-chatgpt": {
      "type": "http",
      "behavior": "domain",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/chatgpt.yaml",
      "path": "./ruleset/proxy-rules/chatgpt.yaml",
      "interval": 86400
    },
    "pr-chatgpt-extra": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/chatgpt-extra.yaml",
      "path": "./ruleset/proxy-rules/chatgpt-extra.yaml",
      "interval": 86400
    },
    "pr-claude": {
      "type": "http",
      "behavior": "domain",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/claude.yaml",
      "path": "./ruleset/proxy-rules/claude.yaml",
      "interval": 86400
    },
    "pr-claude-extra": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/claude-extra.yaml",
      "path": "./ruleset/proxy-rules/claude-extra.yaml",
      "interval": 86400
    },
    "pr-gemini": {
      "type": "http",
      "behavior": "domain",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/gemini.yaml",
      "path": "./ruleset/proxy-rules/gemini.yaml",
      "interval": 86400
    },
    "pr-gemini-extra": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/gemini-extra.yaml",
      "path": "./ruleset/proxy-rules/gemini-extra.yaml",
      "interval": 86400
    },
    "pr-github": {
      "type": "http",
      "behavior": "domain",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/github.yaml",
      "path": "./ruleset/proxy-rules/github.yaml",
      "interval": 86400
    },
    "pr-github-extra": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/github-extra.yaml",
      "path": "./ruleset/proxy-rules/github-extra.yaml",
      "interval": 86400
    },
    "pr-steam": {
      "type": "http",
      "behavior": "domain",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/steam.yaml",
      "path": "./ruleset/proxy-rules/steam.yaml",
      "interval": 86400
    },
    "pr-steam-extra": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/steam-extra.yaml",
      "path": "./ruleset/proxy-rules/steam-extra.yaml",
      "interval": 86400
    },
    "pr-netflix": {
      "type": "http",
      "behavior": "domain",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/netflix.yaml",
      "path": "./ruleset/proxy-rules/netflix.yaml",
      "interval": 86400
    },
    "pr-netflix-extra": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/netflix-extra.yaml",
      "path": "./ruleset/proxy-rules/netflix-extra.yaml",
      "interval": 86400
    },
    "pr-disney": {
      "type": "http",
      "behavior": "domain",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/disney.yaml",
      "path": "./ruleset/proxy-rules/disney.yaml",
      "interval": 86400
    },
    "pr-disney-extra": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/disney-extra.yaml",
      "path": "./ruleset/proxy-rules/disney-extra.yaml",
      "interval": 86400
    },
    "pr-spotify": {
      "type": "http",
      "behavior": "domain",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/spotify.yaml",
      "path": "./ruleset/proxy-rules/spotify.yaml",
      "interval": 86400
    },
    "pr-spotify-extra": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/spotify-extra.yaml",
      "path": "./ruleset/proxy-rules/spotify-extra.yaml",
      "interval": 86400
    },
    "pr-onedrive": {
      "type": "http",
      "behavior": "domain",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/onedrive.yaml",
      "path": "./ruleset/proxy-rules/onedrive.yaml",
      "interval": 86400
    },
    "pr-onedrive-extra": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/onedrive-extra.yaml",
      "path": "./ruleset/proxy-rules/onedrive-extra.yaml",
      "interval": 86400
    },
    "pr-apple": {
      "type": "http",
      "behavior": "domain",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/apple.yaml",
      "path": "./ruleset/proxy-rules/apple.yaml",
      "interval": 86400
    },
    "pr-apple-extra": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/apple-extra.yaml",
      "path": "./ruleset/proxy-rules/apple-extra.yaml",
      "interval": 86400
    },
    "pr-microsoft": {
      "type": "http",
      "behavior": "domain",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/microsoft.yaml",
      "path": "./ruleset/proxy-rules/microsoft.yaml",
      "interval": 86400
    },
    "pr-microsoft-extra": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/microsoft-extra.yaml",
      "path": "./ruleset/proxy-rules/microsoft-extra.yaml",
      "interval": 86400
    },
    "pr-google": {
      "type": "http",
      "behavior": "domain",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/google.yaml",
      "path": "./ruleset/proxy-rules/google.yaml",
      "interval": 86400
    },
    "pr-google-extra": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/google-extra.yaml",
      "path": "./ruleset/proxy-rules/google-extra.yaml",
      "interval": 86400
    }
  },
  "rules": [
    "RULE-SET,pr-custom-reject,REJECT",
    "RULE-SET,pr-custom-direct,DIRECT",
    "RULE-SET,pr-custom-proxy,Global",
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
    "RULE-SET,pr-bilibili,Bilibili",
    "RULE-SET,pr-bilibili-extra,Bilibili",
    "RULE-SET,pr-telegram,Telegram",
    "RULE-SET,pr-telegram-extra,Telegram",
    "RULE-SET,pr-youtube,YouTube",
    "RULE-SET,pr-youtube-extra,YouTube",
    "RULE-SET,pr-chatgpt,ChatGPT",
    "RULE-SET,pr-chatgpt-extra,ChatGPT",
    "RULE-SET,pr-claude,Claude",
    "RULE-SET,pr-claude-extra,Claude",
    "RULE-SET,pr-gemini,Gemini",
    "RULE-SET,pr-gemini-extra,Gemini",
    "RULE-SET,pr-github,GitHub",
    "RULE-SET,pr-github-extra,GitHub",
    "RULE-SET,pr-steam,Steam",
    "RULE-SET,pr-steam-extra,Steam",
    "RULE-SET,pr-netflix,Netflix",
    "RULE-SET,pr-netflix-extra,Netflix",
    "RULE-SET,pr-disney,Disney+",
    "RULE-SET,pr-disney-extra,Disney+",
    "RULE-SET,pr-spotify,Spotify",
    "RULE-SET,pr-spotify-extra,Spotify",
    "RULE-SET,pr-onedrive,OneDrive",
    "RULE-SET,pr-onedrive-extra,OneDrive",
    "RULE-SET,pr-apple,Apple",
    "RULE-SET,pr-apple-extra,Apple",
    "RULE-SET,pr-microsoft,Microsoft",
    "RULE-SET,pr-microsoft-extra,Microsoft",
    "RULE-SET,pr-google,Google",
    "RULE-SET,pr-google-extra,Google",
    "RULE-SET,pr-proxy,Global",
    "RULE-SET,pr-proxy-extra,Global",
    "RULE-SET,pr-direct,DIRECT",
    "RULE-SET,pr-direct-extra,DIRECT",
    "MATCH,Global"
  ]
};
const SERVICES = [
  {
    "id": "bilibili",
    "name": "Bilibili",
    "geosite": "bilibili",
    "default": "DIRECT",
    "icon": "https://raw.githubusercontent.com/Koolson/Qure/master/IconSet/Color/bilibili.png"
  },
  {
    "id": "telegram",
    "name": "Telegram",
    "geosite": "telegram",
    "geoip": "telegram",
    "default": "Global",
    "icon": "https://raw.githubusercontent.com/Koolson/Qure/master/IconSet/Color/Telegram.png"
  },
  {
    "id": "youtube",
    "name": "YouTube",
    "geosite": "youtube",
    "default": "Global",
    "icon": "https://raw.githubusercontent.com/Koolson/Qure/master/IconSet/Color/YouTube.png"
  },
  {
    "id": "chatgpt",
    "name": "ChatGPT",
    "geosite": "openai",
    "default": "Global",
    "icon": "https://raw.githubusercontent.com/Koolson/Qure/master/IconSet/Color/ChatGPT.png"
  },
  {
    "id": "claude",
    "name": "Claude",
    "geosite": "anthropic",
    "default": "Global",
    "icon": "https://raw.githubusercontent.com/lobehub/lobe-icons/master/packages/static-svg/icons/claude-color.svg"
  },
  {
    "id": "gemini",
    "name": "Gemini",
    "geosite": "google-deepmind",
    "default": "Global",
    "icon": "https://raw.githubusercontent.com/lobehub/lobe-icons/master/packages/static-svg/icons/gemini-color.svg"
  },
  {
    "id": "github",
    "name": "GitHub",
    "geosite": "github",
    "default": "Global",
    "icon": "https://raw.githubusercontent.com/Koolson/Qure/master/IconSet/Color/GitHub.png"
  },
  {
    "id": "steam",
    "name": "Steam",
    "geosite": "steam",
    "default": "Global",
    "icon": "https://raw.githubusercontent.com/Koolson/Qure/master/IconSet/Color/Steam.png"
  },
  {
    "id": "netflix",
    "name": "Netflix",
    "geosite": "netflix",
    "default": "Global",
    "icon": "https://raw.githubusercontent.com/Koolson/Qure/master/IconSet/Color/Netflix.png"
  },
  {
    "id": "disney",
    "name": "Disney+",
    "geosite": "disney",
    "default": "Global",
    "icon": "https://raw.githubusercontent.com/Koolson/Qure/master/IconSet/Color/Disney.png"
  },
  {
    "id": "spotify",
    "name": "Spotify",
    "geosite": "spotify",
    "default": "Global",
    "icon": "https://raw.githubusercontent.com/Koolson/Qure/master/IconSet/Color/Spotify.png"
  },
  {
    "id": "onedrive",
    "name": "OneDrive",
    "geosite": "onedrive",
    "default": "DIRECT",
    "icon": "https://raw.githubusercontent.com/Koolson/Qure/master/IconSet/Color/OneDrive.png"
  },
  {
    "id": "apple",
    "name": "Apple",
    "geosite": "apple",
    "default": "DIRECT",
    "icon": "https://raw.githubusercontent.com/Koolson/Qure/master/IconSet/Color/Apple.png"
  },
  {
    "id": "microsoft",
    "name": "Microsoft",
    "geosite": "microsoft",
    "default": "DIRECT",
    "icon": "https://raw.githubusercontent.com/Koolson/Qure/master/IconSet/Color/Microsoft.png"
  },
  {
    "id": "google",
    "name": "Google",
    "geosite": "google",
    "default": "Global",
    "icon": "https://raw.githubusercontent.com/Koolson/Qure/master/IconSet/Color/Google.png"
  }
];
const GROUP = "Global";
const DEFAULT_ICON = "https://raw.githubusercontent.com/Koolson/Qure/master/IconSet/Color/Global.png";

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
  const group = { name: GROUP, type: "select", proxies: choices.slice(), icon: DEFAULT_ICON };
  if (providers.length) group.use = providers;
  if (choices.length) group.proxies.push("DIRECT");
  const serviceGroups = SERVICES.map(function (service) {
    // Never reference other generated service groups: prevents routing loops.
    const candidates = [service.default, GROUP, "DIRECT"].concat(choices);
    const result = { name: service.name, type: "select", proxies: Array.from(new Set(candidates)), icon: service.icon };
    if (providers.length) result.use = providers.slice();
    return result;
  });
  const originalGroups = groups.map(function (original) {
    return original.icon ? original : Object.assign({}, original, { icon: DEFAULT_ICON });
  });
  config["proxy-groups"] = originalGroups.concat([group], serviceGroups);
  config["rule-providers"] = Object.assign({}, config["rule-providers"] || {}, RULE_CONFIG["rule-providers"]);
  config.rules = RULE_CONFIG.rules.slice();
  config.mode = "rule";
  return config;
}
