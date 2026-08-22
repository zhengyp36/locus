# 2026-08-22 — Phone 实现策略定稿 + impl-plan 落地（阶段 A 待实现）

> 本体：`~/codex/cogos`。Phone 设计（docs/phone-design.md）+ 使用（docs/phone-usage.md）已定稿，本次定实现策略并落 impl-plan。

## 实现策略（YZ 认可）

- 先「使用角度」实现领域层 + 持久化，再对接 telecom：阶段 A 只做 Phone 领域层 + 持久化 + FakeTelecomClient，不碰 FeishuTelecomClient。
- 理由：`TelecomClient` 已是抽象（依赖倒置就位）；Phone 大头在领域逻辑 + 持久化不在传输；`add_card(number, pin)` 一步对接（`FeishuTelecomClient` 只吃 number+pin，app_id 在 daemon 侧解析）。
- 关键风险：fake 必须忠实 telecom 语义（send fire-and-forget + 自己消息回显）；方向判定 = sender.number 命中某张卡。

## 阶段划分

- A：领域层 + 持久化 + FakeTelecomClient（全单测）
- B：接 FeishuTelecomClient，单卡 p2p
- C：群聊链路真机（create_group / bound_card / send(chat)）
- D：端到端 + 补遗留（create_group title 空值、群改名软链接）

## impl-plan

- 本体 `docs/phone-impl-plan.md`（函数级清单 + Step 1-5 + subagent 切分 + 易漏点）。
- 新包 `cogos/phone/`（model.py / store.py / fake.py / phone.py），只 import telecom 抽象，数据零交叉 feishu。
- 阶段 B 注入点：`phone.py` `self._factory`（FakeTelecomClient → FeishuTelecomClient，同 `__init__(contact, pin)` 签名）。

## 待实现（新会话）

- 阶段 A 按 impl-plan 落地：Step 1 主会话亲自做 model，subagent 做 store/fake，主会话做 phone + 全量测试。
