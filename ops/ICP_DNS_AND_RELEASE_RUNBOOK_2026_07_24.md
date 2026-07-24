# JiRipple 网站备案停站、恢复与后续迁移 Runbook

最后更新：2026-07-24

## 当前状态

- 备案主体：坐等唯美艺术生活（沈阳）有限公司
- 腾讯云新公司账号 ID：`100050793272`
- 备案订单号：`30178435263099260`
- 订单类型：新增服务（原备案不在腾讯云）
- 同一订单包含：
  - APP：`ReliableReader`
  - 网站：`www.jiripple.com`
- Apple App Store 状态：ReliableReader 1.0 Build 7 已审核通过，当前等待开发者手动发布
- 腾讯云备案退回原因：备案期间 `www.jiripple.com` 仍可对外访问
- DNS 当前仍由旧腾讯云账号管理；备案与 SCF 资源包在新公司账号下

## 当前 DNS 基线

`jiripple.com` 当前可见记录：

| 主机记录 | 类型 | 记录值 | 优先级 | TTL | 用途 |
|---|---|---|---:|---:|---|
| `@` | MX | `mxbiz2.qq.com.` | 10 | 600 | 企业邮箱 |
| `@` | MX | `mxbiz1.qq.com.` | 5 | 600 | 企业邮箱 |
| `@` | TXT | `v=spf1 include:spf.mail.qq.com ~all` | - | 600 | 邮件 SPF |
| `www` | CNAME | `davidqyc.github.io.` | - | 600 | GitHub Pages 网站 |

## 备案整改：唯一允许暂停的记录

备案重新提交前，只暂停：

```text
主机记录：www
记录类型：CNAME
记录值：davidqyc.github.io.
```

严禁暂停、删除或修改：

- 两条 `@` MX 记录；
- `@` TXT / SPF 记录；
- 任何 DKIM、DMARC、域名验证记录；
- NS 服务器；
- 与企业邮箱相关的其他记录。

当前基线中不存在用于网站访问的 `@` A / AAAA / CNAME 记录，因此本轮只需暂停 `www` CNAME。若后续记录集发生变化，必须重新审计后再操作。

## 执行顺序

### A. 暂停网站

1. 登录仍持有 DNS 的旧腾讯云账号。
2. 进入：云解析 DNS → 权威解析 → `jiripple.com` → 记录管理。
3. 对 `www` CNAME `davidqyc.github.io.` 点击“暂停”。
4. 不改其他记录。
5. 等待至少一个 TTL 周期；当前 TTL 为 600 秒，建议等待 10–15 分钟。

### B. 独立验证停站

必须至少用两种独立客户端验证：

1. DNS 查询：确认 `www.jiripple.com` 不再返回有效 CNAME / 地址；
2. HTTP / 浏览器：确认以下地址均不可访问，而不是展示维护页：
   - `https://www.jiripple.com/`
   - `https://www.jiripple.com/reliablereader/`
   - `https://www.jiripple.com/reliablereader/privacy/`

若任一地址仍可访问，不得重新提交备案；继续等待缓存失效并复核。

### C. 重新提交腾讯云备案

1. 切换到新公司腾讯云账号 `100050793272`。
2. 打开备案订单 `30178435263099260`。
3. 确认网站已不可访问。
4. 勾选必要协议。
5. 重新提交审核。
6. 备案审核期间保持 `www` CNAME 暂停，不提前恢复。

### D. 等待与核验

- 保持备案联系人电话可接通；
- 收到工信部短信后，在 24 小时内完成核验；
- 等待通信管理局最终审核结果；
- 公安联网备案已授权，管局通过后再取得数据码并完成后续流程。

### E. 备案通过后恢复网站

1. 在旧腾讯云账号恢复 `www` CNAME `davidqyc.github.io.`；
2. 等待 TTL 生效；
3. 使用两种独立客户端确认：
   - 首页恢复；
   - ReliableReader 产品页恢复；
   - 隐私政策页恢复；
   - HTTPS 正常；
   - 页面标题仍为 `坐等唯美艺术生活｜JiRipple 产品与服务`；
4. 在网站页脚加入网站 ICP 备案号及工信部链接；
5. 完成公安联网备案后，再加入公安备案号和对应链接。

### F. App 与发布顺序

1. Build 7 在备案期间保持“等待开发者发布”，不要提前发布；
2. APP 备案号下发后，在后续 Build 8 / 1.0.1 中：
   - 展示 APP 备案号及工信部链接；
   - 完成旧账号 CloudBase → 新公司账号环境切换；
   - 用生产 Harness、双客户端、正反向测试和独立 release gate 完成验证；
3. 旧 CloudBase 环境不得在 Build 8 发布当天立即删除，应保留兼容期，直到旧 Build 无实际流量。

## 备案完成后的账号归并

网站恢复并确认稳定后，再处理账号归并：

1. 将 `jiripple.com` 的域名注册管理权和 DNS 解析从旧腾讯云账号迁移到新公司账号；
2. 若域名注册与 DNS 可一起转移，优先一次完成；
3. 迁移前导出当前 DNS 记录；
4. 迁移后核对 MX、SPF、DKIM、DMARC、网站 CNAME、自动续费和扣费账户；
5. 完成独立 DNS 与 HTTP 验证后，才把旧账号从日常运维链路中移除。

## 禁止事项

- 不为备案创建维护页替代停站；
- 不删除网站文件或 GitHub Pages 仓库；
- 不修改企业邮箱记录；
- 不在 Apple 审核或备案窗口中迁移 ReliableReader 正式反馈后端；
- 不因“用掉 SCF 额度”而把正文、TTS 音频或大文件代理到 SCF；
- 不在备案完成前手动发布 Build 7。
