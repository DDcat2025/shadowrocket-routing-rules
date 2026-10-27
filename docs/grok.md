# Grok / xAI 独立分流

版本：v2026.10.26.1，核验日期：2026-10-26。

Grok 原先包含在 X 集合中。本次新增独立集合，原 X 集合继续保留原覆盖，旧用户不需要迁移。使用独立集合时，把它放在 X、国际通用和国内大集合之前。

## 订阅地址

- Shadowrocket：`https://raw.githubusercontent.com/DDcat2025/shadowrocket-routing-rules/main/rule/Shadowrocket/Grok/Grok.list`
- Mihomo：`https://raw.githubusercontent.com/DDcat2025/shadowrocket-routing-rules/main/rule/Mihomo/Grok/Grok.yaml`
- DOMAIN-SET：同目录 `Grok_Domain.list`；为统一客户端接口保留 `Grok_Keyword.list`，当前没有关键词规则。

## 覆盖与边界

- `grok.com`、`grok.x.com`、`grokipedia.com`、`x.ai`：根域和子域，包括网站、API、资源与原有登录服务。
- `grokusercontent.com`：内容与认证子域。
- `accounts.spacex.ai`：官方文档列明的共用认证端点，使用精确域名匹配。
- 不使用 `grok` 或 `xai` 关键词；不接管整个 `spacex.ai`、`x.com`、`twitter.com`、公共 CDN、Google 登录或其他 Cursor 专用服务。
- Grok 集成在 X 页面中时，发往 `x.com` 的请求仍由 X 分组处理；域名分流无法区分同一 HTTPS 主机下的页面路径。
- `accounts.spacex.ai` 与 `accounts.x.ai` 是共用认证端点，匹配这些端点的其他产品登录请求也会经过 Grok 分组。

## Mihomo 接入

在现有配置中新增手动 `Grok` 策略组；可先沿用 X 分组的当前出口，再单独选择。增加 HTTP classical rule-provider：

```yaml
rule-providers:
  Grok:
    type: http
    behavior: classical
    format: yaml
    interval: 86400
    path: ./ruleset/Grok.yaml
    url: https://raw.githubusercontent.com/DDcat2025/shadowrocket-routing-rules/main/rule/Mihomo/Grok/Grok.yaml
rules:
  - RULE-SET,Grok,Grok
  # 放在现有 X 规则及通用规则之前。
```

Shadowrocket 在现有规则中加入：

```ini
RULE-SET,https://raw.githubusercontent.com/DDcat2025/shadowrocket-routing-rules/main/rule/Shadowrocket/Grok/Grok.list,Grok
```

## 依据

- 仓库锁定的上游 `data/sources/v2fly/xai`，版本见 `data/source-lock.json`。
- [官方登录域名说明](https://docs.x.ai/x-subscription/sign-in-domains)：内容域名及精确认证端点。仅采用与 Grok 相关的域名，不把整套 Cursor 域名清单复制进来。
- [Grok 官方介绍](https://docs.x.ai/grok/overview)与[官方 API 状态页](https://status.x.ai/)。

本集合验证的是域名匹配及优先级，不代表账号登录、套餐权限、地区可用性或所有图像、视频和语音流程都已实测。
