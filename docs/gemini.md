# Gemini 网页与桌面端统一出口

`Gemini.list` 合并 Gemini 网页、Mac 桌面端、AI Studio、公开 API 核心域名，以及已识别的登录、图片、字体、静态资源和相关共享请求。让它们匹配同一个手动策略组，可以统一到该组选择的节点。

这是域名分流：共享 Google 域名无法按请求来自哪个应用区分。其他应用访问本清单中的登录、字体、图片或 API 主机时，也会使用 Gemini 分组的节点。Google 搜索、YouTube、Drive 主站和整个 `googleapis.com` 父域没有因此整体加入，但这些服务访问被收录的共享资源时仍会受到影响。

## Shadowrocket 接入

在已有 `[Proxy Group]` 段添加一行，随后为它选择需要的节点。`PROXY` 代表首页当前代理，未选具体节点时会跟随它。已有分组可以沿用原名称，例如 `Gemini-Google`，不必新建或重命名。

```ini
Gemini = select,PROXY,policy-regex-filter=.*,policy-select-name=PROXY
```

在已有 `[Rule]` 段添加以下一行。**它必须位于 Claude/其他共享依赖、Google 通用规则、InternationalPriority、国内集合、IP 判断和 FINAL 前面**，才能优先接管相同的 Google 字体与共享主机。

```ini
RULE-SET,https://raw.githubusercontent.com/DDcat2025/shadowrocket-routing-rules/main/rule/Shadowrocket/Gemini/Gemini.list,Gemini
```

末尾策略名必须与自己的分组对应；若使用 `Gemini-Google`，末尾也填写 `Gemini-Google`。两个片段分别合入已有段，不要覆盖整份配置。

如果使用客户端的“添加规则”界面：类型选 `RULE-SET`，URL 栏只填写下方网址，策略另选 Gemini 对应分组。不要把包含 `RULE-SET,` 和策略名的整行粘进 URL 栏。

```text
https://raw.githubusercontent.com/DDcat2025/shadowrocket-routing-rules/main/rule/Shadowrocket/Gemini/Gemini.list
```

已有 Gemini 订阅地址不变。更新规则集、调整优先级、编译并使用配置后，新的连接才会按新规则匹配；此前已建立的长连接不会因此证明已切换。没有 Gemini 入口的客户端仍需添加一次分组与规则，单纯刷新国际规则不会自动创建它们。

## 来源与覆盖

核验日期：2026-10-14。核心入口位于 [`gemini-core.list`](../data/custom/gemini-core.list)，共享依赖位于 [`gemini-shared.list`](../data/custom/gemini-shared.list)；生成器合并输出同一个 Gemini 订阅，自动刷新上游时保留人工清单。

| 范围 | 规则 | 依据 |
|---|---|---|
| Gemini 网页与产品入口 | `gemini.google.com`、`gemini.google` 后缀 | [官方登录说明](https://support.google.com/gemini/answer/13278668)、[产品入口](https://gemini.google/) |
| AI Studio 与公开 API | `aistudio.google.com` 后缀；`ai.google.dev`、`generativelanguage.googleapis.com` 精确主机 | [AI Studio](https://ai.google.dev/aistudio)、[API 服务端点](https://ai.google.dev/api/all-methods) |
| Mac 桌面接口 | `robinfrontend-pa.googleapis.com` | 本地 Gemini Mac 1.128.14.1166（`com.google.GeminiMacOS`）进程网络日志实测 |
| 桌面共享 API、图片 | `www.googleapis.com`；`googleusercontent.com` 后缀 | 同一进程实测 `www.googleapis.com`、`lh3.googleusercontent.com`；资源后缀覆盖分片变化 |
| 登录与令牌刷新 | `accounts.google.com`、`oauth2.googleapis.com` | [Google 官方桌面 OAuth 文档](https://developers.google.com/identity/protocols/oauth2/native-app) |
| 静态资源与字体 | `gstatic.com` 后缀、`fonts.googleapis.com` | Gemini 公开网页引用 `gemini.gstatic.com`、`www.gstatic.com`；字体 API 为共享兼容项 |
| 网页声明的服务与统计 | `ogads-pa.clients6.google.com`、`waa-pa.clients6.google.com`、`www.googletagmanager.com` | Gemini 网页的 DNS 预取声明、标签管理脚本及 iframe；预取声明不等于已经观察到具体业务调用 |
| 历史入口与 SDK | `bard.google.com`、`makersuite.google.com`、`alkalimakersuite-pa.clients6.google.com`、`proactivebackend-pa.googleapis.com`、`apis.google.com` | 已锁定的社区 Gemini/BardAI 源中的具体主机；不是官方完整网络要求 |

网页来源通过公开页面的链接及资源属性核验；桌面来源只保留公共主机名、应用版本和匹配结果，不记录会话、令牌、聊天正文或完整请求 URL。社区快照出处见 [`data/source-lock.json`](../data/source-lock.json)。

## 验证边界

自动检查覆盖上述范围的分组优先级、共享依赖的有意接管、未接入 Gemini 时的兼容路由、相似域名不误匹配，以及 Shadowrocket/Mihomo 导出一致性。原有国际和国内集合保持原内容，只有选择接入 Gemini 统一规则的配置会使用新策略。

域名列表不能保证永久穷尽未来的新接口，也不能覆盖用户主动访问的任意第三方链接、外部 MCP/工具服务。Gemini CLI / Code Assist、Vertex AI、Workspace 内嵌 Gemini 和 Flow 等独立产品的专用接口仍需按实际使用范围另外核验，不能把本规则称为所有 Google AI 产品的完整清单。

入口的 HTTP 200/302/404 只表明得到相应 HTTP 响应，不能直接证明出口 IP。Google 端点未回显客户端 IP 时，只能结合客户端规则命中及同节点回显交叉核对；不把服务器/CDN 地址或另一节点的地址冒充 Gemini 出口。
