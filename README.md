# Shadowrocket 综合分流规则

国内直连、Claude / Anthropic、X 和国际通用规则集中维护；继续使用原有 OpenAI、Adobe、腾讯、字节与 Pinterest 仓库的订阅地址。

适用于 Shadowrocket；同时生成 Mihomo classical rule-provider。这里提供规则集合，不包含节点、密码或完整客户端配置。

## 先选规则

| 类别 | 主规则 | 作用 |
|---|---|---|
| 国内直连 | [ChinaDirect.list](rule/Shadowrocket/ChinaDirect/ChinaDirect.list) | China 常规集合＋腾讯／中国区字节＋人工核验的国内素材站；移除专属服务与 Adobe 条目 |
| 国内扩展 | [ChinaDirectFull.list](rule/Shadowrocket/ChinaDirectFull/ChinaDirectFull.list) | ChinaMax 扩展集合＋同一批国内补充；与常规版二选一，上游 ChinaMax 是实验性分类 |
| Claude / Anthropic | [Claude.list](rule/Shadowrocket/Claude/Claude.list) | 社区域名、官网／Desktop／Code／下载及精确共享依赖 |
| Anthropic 别名 | [Anthropic.list](rule/Shadowrocket/Anthropic/Anthropic.list) | 与 Claude.list 内容相同，二选一 |
| X | [X.list](rule/Shadowrocket/X/X.list) | X、Twitter、媒体、短链接以及上游关联的 Grok / xAI 域名 |
| 国际通用 | [International.list](rule/Shadowrocket/International/International.list) | 搜索、影音、社交、办公、创意、开发、游戏等；Adobe 已独立移交 |
| 国际优先 | [InternationalPriority.list](rule/Shadowrocket/InternationalPriority/InternationalPriority.list) | 一组明确的海外服务，放在国内大集合之前，避免误归国内 |

规则条数及排除明细见 [counts.json](docs/counts.json) 和 [exclusions.json](docs/exclusions.json)。一条 DOMAIN-SUFFIX 已覆盖根域与全部子域，条目数不是网站数量。

## 原有仓库继续使用

- [OpenAI / ChatGPT / Codex / Sora](https://github.com/DDcat2025/openai-shadowrocket-rules)：现有完整兼容版保留，新增官方精确依赖版与可选语音 IP。
- [Adobe](https://github.com/DDcat2025/adobe-shadowrocket-rules)：AI、Behance、Stock 代理；账户、Creative Cloud、字体及普通 Adobe 服务直连。代理在前、直连在后。
- [腾讯](https://github.com/DDcat2025/tencent-shadowrocket-rules)、[中国区字节](https://github.com/DDcat2025/douyin-bytedance-shadowrocket-rules)：已经合入这里的国内集合，旧订阅仍有效，不必重复引用。
- [Pinterest](https://github.com/DDcat2025/pinterest-shadowrocket-rules)：保留独立订阅和专用策略能力。

## Shadowrocket 推荐接入顺序

把片段合入已有配置的 `[Rule]`，不要直接替换整个配置。`ADOBE`、`OPENAI`、`CLAUDE`、`X`、`PINTEREST`、`PROXY` 是你要在客户端手动选择的策略组；OpenAI、Claude、X 可绑定同一个固定自建节点。

```ini
# 局域网（已有配置通常已有这些规则，不必重复）
IP-CIDR,127.0.0.0/8,DIRECT,no-resolve
IP-CIDR,10.0.0.0/8,DIRECT,no-resolve
IP-CIDR,172.16.0.0/12,DIRECT,no-resolve
IP-CIDR,192.168.0.0/16,DIRECT,no-resolve
DOMAIN-SUFFIX,local,DIRECT

# Adobe 的专属规则必须领先于国内/国际通用集合
RULE-SET,https://raw.githubusercontent.com/DDcat2025/adobe-shadowrocket-rules/main/rule/Shadowrocket/AdobeProxy/AdobeProxy.list,ADOBE
RULE-SET,https://raw.githubusercontent.com/DDcat2025/adobe-shadowrocket-rules/main/rule/Shadowrocket/AdobeDirect/AdobeDirect.list,DIRECT

# OpenAI：精确依赖版；如需沿用旧兼容版，把 OpenAI_Precise.list 换成 OpenAI.list
RULE-SET,https://raw.githubusercontent.com/DDcat2025/openai-shadowrocket-rules/main/rule/Shadowrocket/OpenAI/OpenAI_Precise.list,OPENAI
# 可选语音 IP，需要时取消下一行注释
# RULE-SET,https://raw.githubusercontent.com/DDcat2025/openai-shadowrocket-rules/main/rule/Shadowrocket/OpenAI/OpenAI_Voice.list,OPENAI

RULE-SET,https://raw.githubusercontent.com/DDcat2025/shadowrocket-routing-rules/main/rule/Shadowrocket/Claude/Claude.list,CLAUDE
RULE-SET,https://raw.githubusercontent.com/DDcat2025/shadowrocket-routing-rules/main/rule/Shadowrocket/X/X.list,X
RULE-SET,https://raw.githubusercontent.com/DDcat2025/pinterest-shadowrocket-rules/main/rule/Shadowrocket/Pinterest/Pinterest.list,PINTEREST

# 明确的海外服务优先，再国内，再国际综合补漏
RULE-SET,https://raw.githubusercontent.com/DDcat2025/shadowrocket-routing-rules/main/rule/Shadowrocket/InternationalPriority/InternationalPriority.list,PROXY
RULE-SET,https://raw.githubusercontent.com/DDcat2025/shadowrocket-routing-rules/main/rule/Shadowrocket/ChinaDirect/ChinaDirect.list,DIRECT
RULE-SET,https://raw.githubusercontent.com/DDcat2025/shadowrocket-routing-rules/main/rule/Shadowrocket/International/International.list,PROXY
GEOIP,CN,DIRECT
FINAL,PROXY
```

固定出口策略组使用手动 `select`。国内扩展版用 ChinaDirectFull 替换 ChinaDirect，不叠加两份。国际优先与国际综合有有意重叠：前者负责优先级，后者补漏。

## 国内素材站补充

常规版已补入光厂 VJshi、新片场、摄图网、视觉中国、站酷海洛、图虫、花瓣、稿定和创客贴；同时补入官网公开引用的专用资源主机。VJshi 使用根域后缀覆盖全部第一方子域，客服和 12 个专用 OSS 域名使用精确匹配。

这些补充保存在 [domestic-creative.list](data/custom/domestic-creative.list)，构建时合入两种国内集合，自动刷新上游不会覆盖它们。已经订阅 `ChinaDirect.list` 的客户端只需更新规则并重新编译或使用配置，订阅地址不变。来源、边界和验收范围见 [国内素材站补充说明](docs/domestic-creative.md)。

## OpenAI 和 Anthropic 本次补全

OpenAI 保留上游 ChatGPT、API、Sora、语音与 CDN 规则，补入官方 WorkOS、验证码、设备验证、上报及 WebSocket 主机。完整兼容版不删除原有共享父域；精确依赖版用官方明确主机减少影响范围。语音还涉及 UDP 3478 / TCP 443，域名规则本身不保证协议可达。

Claude 同时合并 blackmatrix7 的 Claude / Anthropic、v2fly 的 anthropic，以及官方 Desktop / Code 说明。核心范围包括：

```text
anthropic.com
clau.de
claude.ai
claude.com
claude.dev
claude.app
claudemcpclient.com
claudemcpcontent.com
claudeusercontent.com
```

后缀已经覆盖 `api.anthropic.com`、`platform.claude.com`、`downloads.claude.ai`、动态 Artifact / MCP 内容、桌面预览和扩展桥接；社区附带的专用 CDN / 统计主机也保留。

Claude.list 还含官方文档点名的安装、字体、JS 库和商店精确主机。这些也服务其他应用。若不希望固定这些共享依赖，可改用 [Claude_Core.list](rule/Shadowrocket/Claude_Core/Claude_Core.list)，把 [Claude_Dependencies.list](rule/Shadowrocket/Claude_Dependencies/Claude_Dependencies.list) 分配给国际代理。不要把整个 Google、GitHub 或 Microsoft 企业域都绑定到 Claude。

自定义 MCP、企业 SSO 和第三方模型平台的租户地址无法穷举；需要结合实际连接日志。网站改版与新域名仍要更新，不能保证未来不出现新地址。

## Adobe 如何从国际通用规则中分离

生成时不合并社区 Adobe 模块；同时从国内常规、国内扩展、国际和国际优先集合中删除由现有 AdobeProxy / AdobeDirect / AdobeStockLegacy 接管的具体规则，防止这些条目被其他模块重复带回。`DOMAIN-KEYWORD,adobe` 也不放入通用清单。

Adobe 官方新确认的 Firefly / Sensei 应用后端、训练推理和专用模型资源已加入原 Adobe 仓库的 AI 分类。社区 Adobe 总表逐项归档：普通家族域名并入直连，历史 Stock 别名单列可选，共享第三方提供商保留参考。

共享基础设施父域（例如 amazonaws.com、cloudfront.net）可能仍在国际综合源中，因为它们也承载其他网站。**“Adobe 独立”不等于删除整个 AWS/CDN；应靠前面的专用主机规则保证路由。**

## DOMAIN-SET 与客户端格式

主 `.list` 是完整类型化域名规则，使用 RULE-SET。与上游 blackmatrix7 的某些拆分集合不同，本仓库主 `.list` 已合并全部域名，不需要再叠加 `_Domain.list`。

如果使用 `_Domain.list`：前导点表示后缀，不带点表示精确主机；还需配合 `_Keyword.list` 才能获得该集合的关键词覆盖。单独的 DOMAIN-SET 不能表达关键词。Mihomo 输出为 `behavior: classical`。

这些新集合专注域名，不批量导入上游共享 ASN、IP 或 USER-AGENT 条件。国内 IP 使用客户端 GeoIP；OpenAI 官方语音 IP 已在原仓库提供可选集合。规则顺序与模块优先级以客户端实际编译及连接日志为准。

## 更新、构建和验收

```bash
python3 scripts/build_rules.py
python3 scripts/build_rules.py --check
python3 scripts/check_routes.py
# 显式联网更新输入快照
python3 scripts/refresh_sources.py
python3 scripts/build_rules.py
python3 scripts/check_routes.py
```

生成不联网，使用已提交的固定版本输入。刷新时重新发现主文件及 `_Domain.list`，锁定各仓库提交，下载全部通过后才替换快照。自动流程每周刷新并通过检查后提交；网络/格式/路由检查失败则不发布生成结果。

已覆盖两种国内集合下的代表性路由、Adobe 分类与隔离、精确主机边界、不同客户端导出一致性和源覆盖检查。自动检查不是 Shadowrocket / Mihomo 真机验收；部署后仍需测试实际登录、文件、图片、下载、流式回复与语音。

## 来源

- 原帖：[蔚蓝 WEILANX](https://x.com/zureA255062/status/2107655494034989058)
- [blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script)
- [v2fly/domain-list-community](https://github.com/v2fly/domain-list-community)
- [LOWERTOP / Shadowrocket 手册](https://github.com/LOWERTOP/Shadowrocket)
- [OpenAI 官方网络说明](https://help.openai.com/en/articles/9247338-network-recommendations-for-chatgpt-errors-on-web-and-apps)
- [Claude 下载页](https://claude.com/download)、[Code 网络要求](https://code.claude.com/docs/en/network-config)、[Desktop 网络要求](https://code.claude.com/docs/en/desktop#network-access-requirements)
- [Adobe 官方网络端点](https://helpx.adobe.com/business/enterprise/manage-services/configure-services/network-endpoints.html)

完整文件来源、提交与 SHA-256 见 [source-lock.json](data/source-lock.json)。blackmatrix7 派生内容按 [GPL v2](LICENSE) 保留；v2fly 来源及其 MIT 许可见 `licenses`。本仓库是重新分类、补充、过滤与格式转换的派生整理，不是上述项目的原版。
