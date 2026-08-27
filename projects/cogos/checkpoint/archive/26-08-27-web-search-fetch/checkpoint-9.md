# checkpoint-9 — Jina/Brave 费用超支风险评估

## 当前问题

评估两个已接入服务的费用超支风险：Jina（谷歌账号注册）与 Brave（绑 visa 卡），确认是否存在无意超支。

## 结论

### Jina — 无超支风险（可确定）

- 余额制（预付费）：账户无余额即无可扣之钱。
- 未绑卡、未开 auto top-up（checkpoint-8 已确认）= 物理上不可能超支。
- 余额耗尽最多返回 402 停服，不欠费。

### Brave — 有超支根源，但有防线

- **Postpaid 后付费**（官方 pricing 原话 "pay as you go; usage is billed at the end of each period"），绑 visa 卡 = 超额会期末扣卡。
- 免费 $5/月（≈1000 次 web search），超出按 $5/1k 计费。
- 防线 = dashboard "usage limits" 面板的 **"Free credits only" + Enabled**：官方 X 帖确认 "set your usage limits to be equal to the amount of your free credits to avoid unexpected charges"。
- 该上限生效时 fail-closed（超额 429 停服），不产生超额账单。
- 性质差异：Jina 是硬防线（不绑卡=物理不可能）；Brave 是软防线（订阅设置层，若被重置/升级付费档则失效）。

### 纠正 checkpoint-6 的坑

- checkpoint-6 "每月不限次数" = **rate limit 层**（月度窗口 limit=0，技术不限流），**≠ 计费层**。计费仍是 postpaid 超额扣费，勿混淆。

## 待 YZ 确认（要 100% 安心）

1. Brave dashboard 订阅档位 = Free credits（未升级付费档）。
2. usage limit 保持 "Free credits only" + Enabled。

## Jina auto top-up 开关关不掉（补充，08-27 晚）

- YZ 在 "API Key & Billing" 页发现"余额不足时自动充值"打勾，取消后刷新仍打勾、无保存按钮。
- 官方机制（jina.ai/reader FAQ）：auto top-up = "余额低于阈值时从 **saved payment method** 自动充值"；扣费物理前提 = 有已保存支付方式（经 Stripe，支持信用卡/Google Pay/PayPal）。
- 账户用谷歌 OAuth 登录、未充值/未绑卡 → **无 saved payment method** → 开关打勾也扣不到钱（UI 未持久化属前端行为）。
- 结论：仍安全（余额制 + 无支付方式 = 不可能超支）。谷歌 OAuth 登录 ≠ Google Pay 自动扣费，两者无自动关联。
- 官方明确：auto top-up 可在该 tab 关闭、saved payment methods 可移除。待 YZ 确认该 tab 内 payment method 列表为空。

## 遗留

- 无代码改动。纯评估结论。
