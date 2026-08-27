# checkpoint-8 — Jina 注册完成 + key 验证 + 精确计数闸门

## 当前问题

注册 Jina 免费 key 并验证可用，落实防超支（fail-closed）方案。

## 已完成

- 注册完成，key 存 `~/.secrets/jina.key`（65 字节，`jina_` 前缀，600 权限）。
- 未绑卡、未开 auto top-up（防超支根开关，YZ 已执行）。

## 验证结果（08-27）

- `curl -x 代理 -H "Authorization: Bearer <key>" https://r.jina.ai/https://example.com` → HTTP 200，返回干净 markdown。
- 响应头关键信息：
  - `x-usage-tokens: 29` — 本次输出 token 消耗（计费依据，精确）。
  - `x-ratelimit-limit: 500, 500;w=60` — 免费 key 档 500 RPM（非无 key 20 RPM）。
  - `x-ratelimit-remaining: 499`。
  - 有 5 分钟服务端缓存（响应带 "cached snapshot" 提示）。

## 修正：dashboard「每日额度」提示 ≠ 真实阻断（08-27）

- YZ 在 dashboard 看到「已用完免费试用密钥的每日额度，需充值」横幅，但剩余 token 显示 10M、使用为 0。
- 实测 API：HTTP 200 正常返回，`x-usage-tokens` 正常计数 → **未被挡，提示是未刷新的历史状态 / 另一维度**。
- 结论：**fail-closed 判断依据 = API 实时响应**（402 余额不足 / 429 限流 / 401 才停），**不信 dashboard 横幅**。
- 但「每日额度」这层概念确实存在（dashboard 明示、官方 docs 未公开数值），长期用需留意，当前未触发。

## 关键结论：精确计数闸门（fail-closed 落地）

- Jina 响应头 `x-usage-tokens` 提供**每次调用精确输出 token**，工具层读它累计即可，无需本地粗估。
- fail-closed 方案：本地落盘累计 `x-usage-tokens`，阈值 ~9M（90%）停用 + 飞书通知 YZ；计费类错误（余额不足/429）显式停用，**不静默回退 curl**（否则重新引入共享 IP 拉黑）。
- 账户层防线（根）：预付费 + 不绑卡 + 不开 auto top-up = 物理上不可能超支。

## 遗留

- fetch 接入 proxy-fetch 待 YZ 指令（仿 proxy-search.ts `BACKENDS` 模式，端点只 `r.jina.ai`，header 白名单不发 `X-Respond-With`）。
- 缓存（TTL / JSON vs sqlite）仍待定。
