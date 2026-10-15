# Gemini 独立代理规则

新增一个可单独选择代理节点的 `Gemini` 规则集。范围是 Gemini 网页、Google AI Studio、Gemini API 及清单中的特定入口和服务主机，不是 Google 全家桶，也不是所有 Google AI 产品的完整网络清单。

## Shadowrocket 接入

在已有 `[Proxy Group]` 段添加以下一行，随后在客户端为 Gemini 选择需要的节点。`PROXY` 代表首页当前代理，尚未选择具体节点时会跟随它。

```ini
Gemini = select,PROXY,policy-regex-filter=.*,policy-select-name=PROXY
```

在已有 `[Rule]` 段添加以下一行，放在 Google 通用规则、`InternationalPriority`、国内集合、IP 判断和 `FINAL` 前面：

```ini
RULE-SET,https://raw.githubusercontent.com/DDcat2025/shadowrocket-routing-rules/main/rule/Shadowrocket/Gemini/Gemini.list,Gemini
```

两个片段分别合入已有段落，不要复制第二个同名段或覆盖整份配置。也可以在客户端界面创建同名手动策略组，再添加规则集 URL 并把策略设为 Gemini。之后更新规则集、编译并使用配置。

仅刷新现有的国际规则不会创建新的策略组或订阅行；这次需要添加一次上述入口，之后可沿用远程规则更新方式。

## 匹配范围与来源

人工清单位于 [`data/custom/gemini-core.list`](../data/custom/gemini-core.list)，由生成器输出 Shadowrocket RULE-SET、DOMAIN-SET 及 Mihomo classical 格式。核验日期为 2026-10-14。

| 域名 | 用途／来源 |
|---|---|
| `gemini.google.com` | [Google 官方 Gemini 登录说明](https://support.google.com/gemini/answer/13278668)确认的网页入口；后缀匹配 |
| `gemini.google` | [官方产品入口](https://gemini.google/)，本次访问重定向到 Gemini 网页；后缀匹配 |
| `aistudio.google.com`、`ai.google.dev` | [Google AI Studio 官方介绍](https://ai.google.dev/aistudio)列出的产品入口与开发文档 |
| `generativelanguage.googleapis.com` | [Gemini API 官方参考](https://ai.google.dev/api/all-methods)列明的服务端点；精确匹配 |
| `bard.google.com`、`makersuite.google.com` | 当前已锁定的社区 Gemini/BardAI 源中保留的历史入口 |
| `alkalimakersuite-pa.clients6.google.com`、`proactivebackend-pa.googleapis.com` | 同一锁定源中的具体服务主机；精确匹配，非官方完整网络要求 |

社区输入的版本和来源见 [`data/source-lock.json`](../data/source-lock.json) 及 `data/sources/blackmatrix/Gemini`、`BardAI`。独立集合使用人工精选范围，不自动照搬上游所有条目；需要新主机时应先核验再补入。

## 共享依赖边界

没有加入 `google.com`、`googleapis.com`、`googleusercontent.com`、`gstatic.com` 整个父域，也没有使用 `colab`、`developerprofiles`、`generativelanguage` 这类宽泛关键词。`accounts.google.com` 登录、Google Photos/Drive、通用图片、字体和 CDN 继续匹配其他既有规则。

因此，这份规则能独立选择核心服务的出口，但不能保证一次 Gemini 操作中的所有共享请求都走同一个出口。Gemini CLI / Code Assist 的 `cloudcode-pa.googleapis.com`、Vertex AI、Workspace 内嵌 Gemini、Flow 等产品未纳入这次范围。若后续需要扩展，应按实际使用的产品和连接日志明确补充。

原有 `International` 和 `InternationalPriority` 的规则内容保持兼容，未添加独立 Gemini 入口的客户端继续沿用原来的国际／兜底路由。已添加时，必须把具体 Gemini 规则放在宽泛 Google 规则前面，否则先匹配的规则会接管流量。

## 验证范围

自动检查覆盖 Gemini 网页、AI Studio、API、历史入口、具体服务主机和子域匹配；同时检查搜索、YouTube、Drive、登录、共享资源、相似域名及其他 API 不会被这份集合误匹配。两种国内集合下的优先级、未启用 Gemini 独立分组时的兼容路由，以及客户端导出格式一致性均纳入检查。

这些检查验证规则内容与匹配逻辑，不等于已完成 Gemini 登录、生成图片、实时音视频或下载的客户端验收。没有调用 Gemini API、提交生成请求或修改用户的客户端配置。
