# 自用 FlClash 分流规则

将 `rules/` 中的个人规则与 [Loyalsoldier/v2ray-rules-dat](https://github.com/Loyalsoldier/v2ray-rules-dat) 的直连、代理、广告拦截列表合并，从同一版本的 `geosite.dat` / `geoip.dat` 提取服务分类，通过 GitHub Actions 每日构建，发布为手机 FlClash 可以通过链接更新的 Mihomo 规则集。支持为 Bilibili、Telegram、Apple、Microsoft、Google 分别选择出口节点。

## 手机怎么用

首次将本项目推送到 GitHub **公开仓库** `lzo-catty/proxy-rules` 的 `main` 分支。进入 **Actions → Build and publish rules**，确认首次构建成功；也可以点击 **Run workflow** 手动触发。成功后自动生成 `release` 分支，无须开启 GitHub Pages，也不需要配置 PAT 或 Secrets。组织策略或分支保护需要允许 Actions 向 `release` 写入。

**推荐：将扩展脚本绑定到现有节点订阅。**

```text
https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/flclash.js
```

1. 在 FlClash 中先导入你已有的机场/节点订阅。
2. 打开脚本管理（新版可从订阅的「扩展 → 脚本 → 配置脚本」进入），选择新增、从 URL 导入，粘贴上面的链接。
3. 返回该节点订阅的扩展设置，选择脚本模式并启用刚导入的脚本，重新应用配置。
4. 在代理页面分别打开 **分流-Bilibili / 分流-Telegram / 分流-Apple / 分流-Microsoft / 分流-Google**，为每个组选择节点。**自定义分流** 是通用代理及兜底出口，默认优先使用原订阅第一个策略组；请检查其选择符合你的需求。
5. 使用**规则模式**。规则提供者的更新间隔为 86400 秒，客户端运行时由内核更新；需要立即更新时，在资源/规则集页面手动更新或重新加载配置。

不同版本菜单名称可能不同，需要支持 `function main(config)` 的扩展脚本功能。脚本保留节点、节点提供者、原策略组和 DNS 等设置，**替换原订阅的路由规则 `rules`**。原有订阅的专用业务分流将由本项目策略替代。脚本本身改动后，在脚本管理中同步一次；只修改自定义规则时，无须重新导入脚本。

**`flclash.js` 是扩展脚本，单个 `*.yaml` 是规则集，都不是包含节点的完整机场订阅。** 不要将它们直接作为新的节点订阅导入。节点订阅地址仅保留在你的 FlClash 中，不需要提交到本仓库。

如果没有远程脚本入口，可以下载 `flclash.js` 后通过文件导入，或复制脚本内容。高级用法：将生成的 `rules-config.yaml` 中的 `rule-providers` 与 `rules` 合入已有配置，并为所有规则目标创建对应策略组（`自定义分流` 和五个 `分流-…` 组），或替换为已存在的组名。这个 YAML 片段本身不包含策略组或节点。

## 独立服务策略组

| 策略组 | 初次应用默认出口 | 规则来源 |
| --- | --- | --- |
| 分流-Bilibili | DIRECT（直连） | geosite: bilibili |
| 分流-Telegram | 自定义分流 | geosite: telegram + geoip: telegram（IPv4/IPv6） |
| 分流-Apple | DIRECT（直连） | geosite: apple |
| 分流-Microsoft | DIRECT（直连） | geosite: microsoft |
| 分流-Google | 自定义分流 | geosite: google |

每个服务组都提供 **DIRECT、自定义分流、原订阅策略组、所有内嵌节点、所有节点提供者中的节点**。例如 Telegram 选新加坡节点、Google 选日本节点、Apple 保持直连，互不影响。组中选择“自定义分流”时才跟随该组变化；直接选择某个节点则独立使用该节点。FlClash 已保存的手动选择可能覆盖初始默认值。

名称使用 `分流-` 前缀，允许与原机场中的 `Apple`、`Google` 等策略组共存。如果订阅恰好已有同名 `分流-…` 或 `自定义分流` 组/节点，脚本会报错，请先改名。各新服务组不互相引用，避免循环依赖。

**从旧版单组配置升级：更新远程扩展脚本并重新应用订阅一次。** 只更新规则集不会自动创建新策略组。入口仍是原来的 `flclash.js` 链接。

在 `services.yaml` 中管理服务及默认出口。例如新增 YouTube 时，可加入：

```yaml
- id: youtube
  name: 分流-YouTube
  geosite: youtube
  default: 自定义分流
```

`geosite` / 可选 `geoip` 必须是上游 DAT 中存在的分类；缺失或为空会让构建失败。更具体的服务应排在宽泛服务前面，例如 YouTube 放在 Google 前。`id` 使用小写英文字母开头的字母/数字，`name` 必须唯一，`default` 可选 `DIRECT` 或 `自定义分流`。服务列表/组名/默认值调整后，发布并同步一次扩展脚本。

## 自定义规则

编辑以下文件后提交到 `main` 即触发构建。初始文件仅包含注释示例，默认完全使用上游分类，不擅自添加个人偏好。

| 文件 | 用途 |
| --- | --- |
| `rules/direct.txt` | 强制直连 |
| `rules/proxy.txt` | 强制走代理策略组 |
| `rules/reject.txt` | 强制拦截 |
| `rules/exclude.txt` | 从全部上游分类中移除完全相同的规则 |

每行一条，不带最终策略名称，支持空行和整行 `#` 注释：

```text
# 裸域名和 domain: 匹配自身及全部子域名
example.com
domain:example.net
# 仅精确域名
full:login.example.org
# 关键词、正则
keyword:example
regexp:^api[0-9]+\.example\.com$
# Mihomo 写法也支持
DOMAIN-SUFFIX,example.cn
DOMAIN,login.example.cn
IP-CIDR,203.0.113.0/24,no-resolve
IP-CIDR6,2001:db8::/32,no-resolve
```

支持的 Mihomo 类型为 `DOMAIN`、`DOMAIN-SUFFIX`、`DOMAIN-KEYWORD`、`DOMAIN-REGEX`、`IP-CIDR`、`IP-CIDR6`。不接受末尾的 `DIRECT`/`REJECT`/策略组名，也不接受 URL、`MATCH`、嵌套 `RULE-SET`。正则先经过 Python 语法检查，再由实际内核验证 Go 正则兼容性；带逗号的量词如 `[0-9]{1,3}` 原样保留。使用支持 `DOMAIN-REGEX` 的近期 FlClash/Mihomo 版本。

匹配顺序（从上到下，首次命中即停止）：

1. 自定义拦截 → 自定义直连 → 自定义代理。
2. 本地网络域名 `lan`/`local` 和常用私有 IPv4/IPv6 网段直连。
3. 合并后的上游拦截（服务分组不会绕过广告拦截）。
4. 独立服务规则：先按 `services.yaml` 顺序匹配所有服务的域名集，再按相同顺序匹配补充规则（关键词、正则及 IP）。
5. 通用上游代理 → 直连。
6. 未命中流量走 **自定义分流** 策略组。

自定义规则会从其他上游分类中移除完全相同的条目，并单独作为优先规则集。例如上游拦截 `ads.example.com`，自定义直连 `full:login.ads.example.com`，仍然能让该精确域名优先直连。三个自定义文件之间出现相同规则但不同策略时构建失败；不同但重叠的域名/正则按上述顺序处理，不自动按域名长度排序。

`exclude.txt` 是**精确删除条目**，对通用分类和服务分类都生效，不会自动删除覆盖它的父域名、关键词或正则。若要为某个网站解除拦截，请优先将它写入 `direct.txt` 或 `proxy.txt`。这三个自定义文件仍优先于服务策略，例如 `direct.txt` 中的 Google 域名会强制直连，不再交给 Google 组。

本项目合并上游 `direct-list.txt`、`proxy-list.txt`、`reject-list.txt`，并读取 `geosite.dat`/`geoip.dat` 中选定的服务分类，不重新生成或发布完整 DAT 文件。服务分类包含全部属性的域名，不按 `@cn` 等标记过滤。普通域名使用 `behavior: domain`，关键词、正则和 IP 使用 `classical`，保留精确匹配/后缀匹配差异。提取的服务 IP 使用 `no-resolve`，避免为了服务 IP 匹配提前进行 DNS 查询。**不包含中国 IP 数据库兜底**：没有命中域名或服务 IP 规则的公网 IP 默认走代理；已有订阅的 DNS 设置继续保留。

## 发布文件与链接

以下链接仅在首次 Actions 发布成功后可用：

| 文件 | 内容 / behavior |
| --- | --- |
| `flclash.js` | 手机扩展脚本入口 |
| `rules-config.yaml` | 手动合并配置用的片段 |
| `direct.yaml` / `proxy.yaml` / `reject.yaml` | 已合并自定义规则的域名集 / `domain` |
| `direct-extra.yaml` / `proxy-extra.yaml` / `reject-extra.yaml` | 关键词、正则、IP 等 / `classical` |
| `custom-direct.yaml` / `custom-proxy.yaml` / `custom-reject.yaml` | 优先匹配的个人规则 / `classical` |
| `bilibili.yaml` / `telegram.yaml` / `apple.yaml` / `microsoft.yaml` / `google.yaml` | 对应服务域名 / `domain` |
| `bilibili-extra.yaml` / `telegram-extra.yaml` / `apple-extra.yaml` / `microsoft-extra.yaml` / `google-extra.yaml` | 对应服务关键词、正则、IP 等 / `classical` |
| `manifest.json` | 构建时间、上游 commit、输入/输出 SHA-256、规则数量、服务组配置 |

链接格式：

```text
https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/<文件名>
```

例如直连规则：

```text
https://raw.githubusercontent.com/lzo-catty/proxy-rules/release/direct.yaml
```

**默认配置需要完整的 19 个规则提供者及顺序**（9 个基础规则集 + 5 个服务各 2 个规则集），只导入部分域名文件会缺少关键词/正则、Telegram IP 或跨分类的自定义优先级。使用扩展脚本可以自动处理。

Raw 域名无法访问时，需要先使用可用网络或现有代理完成首次下载。脚本 URL 能下载不代表规则提供者 URL 也可访问；所有默认链接均使用 `raw.githubusercontent.com`。

Fork 后 Actions 会根据 `GITHUB_REPOSITORY` 自动生成自己的链接；README 中的示例地址需要换成你的 `owner/repo`。

## 自动构建

- 每日北京时间 **07:35**（UTC 23:35）计划执行，GitHub 可能延迟。
- 推送到 `main` 和手动触发也会构建；PR 只检查，不发布。
- 每次先解析上游 `release` 对应的 commit，再按同一个 commit 下载三个列表及两份 DAT，避免混用不同发布批次。
- 测试通过后，执行实际生成的扩展脚本，以固定版本 Mihomo **v1.19.34** 加载全部规则集，核对内核规则数量，并通过内核 API 验证每个服务组能独立切换节点、其他组不受影响。
- 全部检查通过才写入 `release`；失败保留上一次线上结果。无需 force push，保留发布历史。
- 定时工作流必须存在于默认分支；Fork 可能需要手动启用 Actions，公开仓库长期无活动时 GitHub 可能暂停定时任务。

## 本地开发

需要 Python 3.10+；测试扩展脚本和运行内核验证需要 Node.js 22+。Python 依赖包含 PyYAML 和 protobuf。

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
node --test tests/flclash.test.cjs
python scripts/build.py --repository lzo-catty/proxy-rules
```

输出在 `dist/`，不提交生成文件到 `main`。如果遇到 GitHub API 限流，可通过环境变量 `GITHUB_TOKEN` 提供令牌，或使用本地快照：

```bash
python scripts/build.py --upstream-dir /path/to/upstream-release --upstream-ref <commit-sha>
python scripts/verify.py --mihomo /path/to/mihomo
```

本地快照目录须包含 `direct-list.txt`、`proxy-list.txt`、`reject-list.txt`、`geosite.dat`、`geoip.dat`，且来自同一上游发布版本。`verify.py` 会短暂启动仅监听回环地址的内核 API，使用指向本机的测试节点验证策略组切换（不会通过这些节点访问外网），验证后关闭进程。

## 来源

- [Loyalsoldier/v2ray-rules-dat](https://github.com/Loyalsoldier/v2ray-rules-dat)：规则数据及其来源说明。
- [Mihomo 规则提供者文档](https://wiki.metacubex.one/config/rule-providers/)及[内容格式](https://wiki.metacubex.one/config/rule-providers/content/)。
- [FlClash](https://github.com/chen08209/FlClash)：客户端及扩展脚本实现。

本项目采用 GPL-3.0 许可，见 `LICENSE`。上游规则遵循其 GPL-3.0 许可和相关数据来源条款，参见 `NOTICE`。发布产物同时携带完整许可和来源声明。
