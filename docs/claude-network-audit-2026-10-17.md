# Claude 网络规则核对（2026-10-17）

对照用户提供的 [Net.Coffee 清单](https://ip.net.coffee/claude/site.html)，以 [Claude Code 网络要求](https://code.claude.com/docs/en/network-config#network-access-requirements)、[Desktop 网络要求](https://code.claude.com/docs/en/desktop#network-access-requirements)、[官方 IP 文档](https://platform.claude.com/docs/en/api/ip-addresses) 和公开官网依赖为复核依据。覆盖域名、走代理、走 Claude 专属分组是三件不同的事。

## 逐项结论

| 参考项 | 原规则 | 本次处理 |
|---|---|---|
| anthropic.com、claude.ai、claude.com、clau.de、claudemcpclient.com、claudemcpcontent.com、claudeusercontent.com | Claude_Core 已有后缀规则 | 保留；后缀已覆盖 API、下载、CDN、桥接和动态子域 |
| cdn.anthropic.com | 被 anthropic.com 后缀覆盖 | 不重复添加 |
| servd-anthropic-website.b-cdn.net | Claude_Core 已有精确规则 | 保留 |
| anthropic.com.cdn.cloudflare.net | 国际通用代理，未在 Claude_Core | 新增精确兼容规则；本次 DNS 返回 160.79.104.10，位于官方 API 入站范围 |
| anthropic.auth0.com、anthropic-com.ghost.io | 国际代理，未在 Claude_Core | 新增精确历史兼容规则；均能解析，但未证实当前 Claude 仍会调用，Auth0 的公开 OIDC 元数据路径返回 404，不把它们称为当前必需登录端点 |
| browser-intake-us5-datadoghq.com | Claude_Dependencies 已有精确规则 | 保留；另已有官方列出的 http-intake.logs.us5.datadoghq.com |
| sentry.io | 国际优先/通用规则已有后缀覆盖 | 保留现有代理分类，不把全部租户绑定到 Claude；当前官方 Code 列的是两项可关闭的 Datadog 上报 |
| statsigapi.net | events.statsigapi.net 已在国际代理；根域没有专用规则，会进入后续通用/IP/兜底匹配 | 不扩大成整个根域的 Claude 规则；当前官方 Code 的功能开关/事件记录由 api.anthropic.com 承载，已有覆盖 |
| datadog、sentry、sift 关键词 | 未纳入 Claude 规则 | 不添加：会匹配其他产品的监控或任意同名域名，不能据此识别 Claude 请求 |
| intercom.io、intercomcdn.com | 既有 OpenAI 规则优先代理这些共享服务 | 在 Claude_Dependencies 补入官网实际引用的精确主机，供单独使用 Claude 集合的客户端；不改变既有 OpenAI 优先级 |
| cdn.usefathom.com | Claude_Core 已有精确规则 | 保留 |
| 160.79.104.0/21 | 没有 Claude 专用 IP 规则 | 使用官方入站 /23；/21 在官方文档中是 Anthropic 对外发起连接的地址范围，不当作客户端 API 目标范围照搬 |
| 2607:6bc0::/32 | 没有 Claude 专用 IP 规则 | 使用官方入站 /48；/32 注册归属不能等同于全部地址都是当前 API 入口 |
| AS399358 | 没有 Claude ASN 规则 | 采用两条明确 IP 网段，不引入依赖客户端 ASN 数据库的更大范围匹配 |
| category-ntp | 未设置 Claude 专属 NTP 规则 | 不添加；未找到官方要求 Claude Code 用 NTP 获取所在地时区的依据 |

## 新增的精确客服依赖

从 `https://support.claude.com/en/` 的公开 HTML 中确认：

```text
api-iam.intercom.io
widget.intercom.io
downloads.intercomcdn.com
static.intercomassets.com
```

该页加载的 Intercom widget 脚本还引用 `js.intercomcdn.com`。只保存公开域名和来源，不保存登录态、Cookie、聊天或认证内容。这些是共享主机，其他应用访问相同地址时也会匹配；在推荐顺序中，`api-iam.intercom.io`、`widget.intercom.io`、`downloads.intercomcdn.com`、`js.intercomcdn.com` 由更早的 OpenAI 规则接管，`static.intercomassets.com` 进入 Claude_Dependencies。需要同出口时应让相关分组选用同一节点，而不是靠调整规则顺序宣称能区分应用。

## 独立 IP 兜底

新增 `Claude_IP`，只包含官方明示的 API / Console 入站网段：

```text
IP-CIDR,160.79.104.0/23,no-resolve
IP-CIDR6,2607:6bc0::/48,no-resolve
```

Shadowrocket 在 Claude 域名规则之后、国际通用和 GEOIP / FINAL 之前加入（策略名按客户端已有分组填写）：

```ini
RULE-SET,https://raw.githubusercontent.com/DDcat2025/shadowrocket-routing-rules/main/rule/Shadowrocket/Claude_IP/Claude_IP.list,Claude-Anthropic,no-resolve
```

Mihomo 使用 `behavior: classical`，URL 为 `https://raw.githubusercontent.com/DDcat2025/shadowrocket-routing-rules/main/rule/Mihomo/Claude_IP/Claude_IP.yaml`，规则为：

```yaml
- RULE-SET,Claude_IP,Claude-Anthropic,no-resolve
```

`no-resolve` 表示不为匹配这条 IP 规则额外发起域名的正向解析，不是“避免反向 DNS”。这两条只补已知 API IP 目标，不能覆盖所有 CDN、第三方服务或未来地址。开启或关闭 IPv6 是客户端网络接管问题，本次不改变该设置。

## 不能照搬的解释

[NTP 标准 RFC 5905](https://www.rfc-editor.org/rfc/rfc5905.html) 定义 UTC 时间戳和时钟同步，不返回“代理所在地区的时区”。把 NTP 转到境外不会改变系统时区，禁用 IPv6 也不能“彻底消除时区泄露”。WebRTC 测试只能观察其测试连接，不能证明所有 UDP / NTP 都走同一路径。

没有找到官方依据支持“任意客服或监控请求与主 API 出口不同就必然触发账号风控”。官方明确要求特定组织 IP 白名单场景下，桥接域名使用同一出口或加入正确白名单；不能把该场景扩展成对所有账号、所有第三方服务的保证。本次补全不承诺账号风控结果。

## 部署和验证边界

原 Claude 域名订阅 URL 不变，刷新可取得域名补充；新 IP 提供方需要额外加一行接入。离线 YAML 需重新导入更新快照。已有 BrowserLeaks 修正保留，节点、DNS、TUN、Gemini 和 OpenAI 等其他策略不调整。

自动检查包括域名覆盖、共享主机优先级、相似域名负例、IPv4/IPv6 网段边界、Shadowrocket/Mihomo 导出一致性。客户端是否实际接管、既有连接是否更新、真实出口和故障时阻断，仍需对应设备的运行时验证。
