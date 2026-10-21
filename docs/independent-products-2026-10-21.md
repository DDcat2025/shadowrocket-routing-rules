# Instagram / Facebook / Google 独立分流

日期：2026-10-21。分类版本：v2026.10.21.1。

## 订阅

| 分类 | Shadowrocket RULE-SET | Mihomo classical |
|---|---|---|
| Instagram | [Instagram.list](https://raw.githubusercontent.com/DDcat2025/shadowrocket-routing-rules/main/rule/Shadowrocket/Instagram/Instagram.list) | [Instagram.yaml](https://raw.githubusercontent.com/DDcat2025/shadowrocket-routing-rules/main/rule/Mihomo/Instagram/Instagram.yaml) |
| Facebook | [Facebook.list](https://raw.githubusercontent.com/DDcat2025/shadowrocket-routing-rules/main/rule/Shadowrocket/Facebook/Facebook.list) | [Facebook.yaml](https://raw.githubusercontent.com/DDcat2025/shadowrocket-routing-rules/main/rule/Mihomo/Facebook/Facebook.yaml) |
| Google | [Google.list](https://raw.githubusercontent.com/DDcat2025/shadowrocket-routing-rules/main/rule/Shadowrocket/Google/Google.list) | [Google.yaml](https://raw.githubusercontent.com/DDcat2025/shadowrocket-routing-rules/main/rule/Mihomo/Google/Google.yaml) |

为三类分别创建手动 `select` 分组，放在国内、国际通用和最终规则之前。Google 应在 Claude 的共享依赖与旧 Gemini 提供方之前；如果全部 Google 产品统一出口，将旧 Gemini 规则改为 Google，或移除重复的 Gemini 引用。旧 Gemini 订阅仍保留，供其他用户兼容使用。

```yaml
# rule-providers 定义见上述链接，behavior 均为 classical。
rules:
  # 原本 Claude / Codex 的按应用固定出口规则仍放在这里之前。
  - RULE-SET,Instagram,Instagram
  - RULE-SET,Facebook,Facebook
  - RULE-SET,Google,Google
  # 后接其他服务、国内/国际集合、MATCH。
```

这只是接入片段，不是含节点的完整配置。完整节点配置只保存在用户的私有部署仓库。

## 覆盖与边界

- Instagram：网站、API、`cdninstagram.com`、`instagr.am`、`ig.me`、专属图片/CDN 主机。
- Facebook：网站、Facebook Graph、Messenger、`fbcdn.net` / `fbsbx.com` 等共用资源。没有继承旧 Facebook 大表中的 WhatsApp、Oculus、React、Instagram 以及大量关键词/相似拼写域名。
- Google：v2fly Google 主列表的所有 include 递归展开，并合并既有 Google / Search / Drive / Voice / Earth / YouTube / YouTube Music 和精确 Gemini 补充。包括 Workspace、Gmail、Drive、Docs、Meet、Maps、Photos、Translate、Search、YouTube、Play、Android/FCM、Gemini、AI Studio、NotebookLM、Cloud、Firebase、Kaggle、DeepMind、Flutter、Dart、Go 等已知产品域名及公共服务。来源更新后可继续增加，不保证穷尽未来新域名。
- Google 的广告、统计、字体及 Cloud 托管域名也会影响其他网站对这些主机的请求。不会因为 Chrome 是 Google 产品就把浏览器全部网页强制走 Google，更不会把所有 `.app` / `.dev` 租户域名归入 Google。
- Instagram 与 Facebook 可能使用相同的 `fbcdn.net`、`graph.facebook.com` 等域名。此处明确把这些共用主机归到 Facebook；仅靠域名无法辨别每一条请求属于哪个产品。Instagram 专用域名优先。
- 应用路径规则优先于产品域名规则：Claude / Codex 发出的 Google 字体、GitHub 等依赖仍跟随各自固定出口，保留现有保护策略。
- 不加入整个 Google/Meta 的 ASN 或共享 IP 段；新独立集合不使用 `DOMAIN-KEYWORD`。原国际综合集合继续保留兼容覆盖，尚未接入新提供方的旧客户端不会因为本次拆分失去原规则。

## 来源与验证

Google 输入固定提交、每个包含文件的 URL 与 SHA-256 在 [dedicated-source-lock.json](../data/dedicated-source-lock.json)。展开文件清单及两条由现成后缀完全覆盖的 Play 正则在 [google-source-expansion.json](google-source-expansion.json)。遇到新正则/有条件 include 会报错，要求明确审查，不静默丢弃。

其余输入及许可证沿用 [source-lock.json](../data/source-lock.json)。社交专用规则记录于 `data/custom/*-dedicated.list`，保留核心服务边界；Google/Meta 服务运营情况不能仅凭历史社区清单保证。

- [Google Workspace 官方防火墙主机清单](https://knowledge.workspace.google.com/admin/security/firewall-and-proxy-settings)
- [v2fly Google 源列表](https://github.com/v2fly/domain-list-community/blob/master/data/google)
- [blackmatrix7 Google](https://github.com/blackmatrix7/ios_rule_script/tree/master/rule/Shadowrocket/Google)
- [Meta Instagram 平台说明](https://developers.facebook.com/docs/instagram-platform/)
- [Mozilla Facebook Container 主机清单](https://github.com/mozilla/contain-facebook/blob/main/src/background.js)

构建/边界/兼容回归使用 `scripts/build_rules.py --check` 与 `scripts/check_routes.py`；完整配置另经真实 Mihomo 内核离线匹配测试。测试通过不代表所有产品的登录、媒体、通话或未来新域名已经逐一实测。
