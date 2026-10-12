# 国内创意素材平台补充

2026-10-12 核验并补充。选择常规国内库加平台专用域名的方式，未将客户端切换到实验性的 ChinaMax 扩展分类。

源清单为 [`data/custom/domestic-creative.list`](../data/custom/domestic-creative.list)。生成器将它合入 `ChinaDirect` 和 `ChinaDirectFull`，再统一进行专属服务隔离、去重和客户端格式导出。自动更新仅替换 `data/sources`，人工补充清单会保留。

## 平台与来源

| 平台 | 后缀规则 | 核验来源 |
|---|---|---|
| 光厂 VJshi | `vjshi.com` | [官网关于页](https://www.vjshi.com/about)、[开放平台](https://www.vjshi.com/open/introduction)及公开页面内嵌运行配置 |
| 新片场 | `xinpianchang.com` | [官方介绍](https://www.xinpianchang.com/aboutus/aboutus)、[素材协议](https://www.xinpianchang.com/aboutus/agreement?t=10) |
| 摄图网 | `699pic.com` | [官网](https://699pic.com/)及其页面资源 |
| 视觉中国 | `vcg.com` | [官网首页](https://www.vcg.com/home)、[官方 AIGC 产品](https://www.vcg.com/aigcHelp/) |
| 站酷海洛 | `hellorf.com` | [官网](https://www.hellorf.com/) |
| 图虫 | `tuchong.com` | [官方介绍](https://stock.tuchong.com/landing-page/about?from=footer)、[首页](https://stock.tuchong.com/) |
| 花瓣 | `huaban.com` | [官网](https://huaban.com/)及其图片资源引用 |
| 稿定 | `gaoding.com` | [官网](https://www.gaoding.com/)及其资源引用 |
| 创客贴 | `chuangkit.com` | [官网](https://www.chuangkit.com/)及其静态资源引用 |

包图 `ibaotu.com`、千图 `58pic.com`、站酷 `zcool.com.cn` 已由原有规则覆盖，本次加入路由回归检查，不重复添加。这里的条目数是匹配条件数量，不是网站数量或覆盖率百分比。

## VJshi 专用资源

一条 `DOMAIN-SUFFIX,vjshi.com` 覆盖主站、API、开放平台，以及 `restatic`、`s1`、`pic`、`dimg`、`mp4`、`dmp4`、`lmp4`、`ma`、`od`、`pp`、`spic`、`svideo` 等第一方子域。

官网客服链接确认 `vjshi.soboten.com`。当前官网公开页面的运行配置确认 11 个上传桶及 1 个未启用图片预览桶；完整主机名保存在源清单中，全部使用 `DOMAIN` 精确匹配。没有添加共享的 `aliyuncs.com`、区域 OSS 根域或 `soboten.com` 后缀规则。

图虫的 `static-prod.ituchong.com`、花瓣的 `gd-hbimg.huabanimg.com` 和 `hbimg.huabanimg.com`，以及稿定页面引用的 7 个 `dancf.com` 资源主机，同样只补充本次实际观察到的精确主机名。没有泛化到这些资源服务的根域或未观察到的其他租户主机。

本说明只保存公共域名及来源，不保存用户会话、Cookie、令牌或完整页面脚本。

## 生效与验证

保持原来的 `ChinaDirect.list` 订阅地址和 `DIRECT` 策略；客户端更新远程规则并重新编译或使用配置后，即可识别新增域名。若客户端使用 `direct-dns-server`，新增域名命中域名直连规则后即可使用对应的直连 DNS。GitHub 更新本身不会替客户端保存配置、刷新本地规则缓存或清空 DNS 缓存。

路由检查覆盖主站、任意第一方子域、客服、上传、图片、媒体资源和既有海外专属服务；另外检查相似域名、其他 OSS 桶、其他客服租户及共享资源根域不会被新增清单捕获。Shadowrocket RULE-SET、DOMAIN-SET 加关键词伴随文件，以及 Mihomo 导出由同一源生成并检查一致性。

这是规则与生成产物的验证；实际访问、上传下载速度和 DNS 路径仍需以客户端更新后的连接日志为准。平台新增第三方资源时需要继续补充，静态列表不能保证永久穷尽。
