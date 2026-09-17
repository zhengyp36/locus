# handoff｜号码 / 联系人 / Kilo 唤醒（09-13 会话 #9 末）

> 并行支线，**与 v0 主线分开做**（`handoff-build-agent-v0.md`）。本文件是"谁有号、谁能唤醒谁"落到实机的交接。
> 与 v0 的改动**不要混**：这条只动 cogos phone / kilo-resident。

## 背景事实（会话 #9 已查实）

- **唐钰 agent 已存在**：`~/.cogos/agent/tangyu/`
  - `memory/profile.md`：name `唐钰` / phone_number `COGOS002:A0005` / pin `967b6fa7` / contacts: `YZ → COGOS002:H0002`
  - `phone/phone-data/cards.json`：状态 **`failed: failed to connect to daemon`**（phone daemon 没起）→ 真跑前必须先解决
  - 已有会话：`COGOS002:A0001`（李恪）、`COGOS002:H0002`（YZ）
- **cogos 账号**（`~/.cogos/feishu/accounts/`）：
  - COGOS002 bots：A0001 李恪 / A0002 元芳 / A0003 剑平 / A0004 陈留(init) / **A0005 唐钰** / A0006+ 空
  - COGOS002 humans：H0001 SL / H0002 YZ
- **Kilo 飞书身份**（kilo-resident；creds 在 `~/.secrets/feishu.key`）：`KILO-LOCUS-A`（work/A/locus）/ `KILO-LOCUS-B` / `KILO-DOCTOR`。
  **入站→唤醒已通**：`work/B/kilo-resident/src/feishu.ts:34` WSClient 收 `im.message.receive_v1` → bridge → TUI 注入唤醒会话。→ "被事件唤醒"机制已成立。
- kilo-resident 现状/遗留：`work/B/checkpoint/task-7-handoff-4.md`（HEAD `4bae464`）。

## 要做的三件

1. **修唐钰卡状态**：让 `COGOS002:A0005` 能收发（`cards.json` 不再 failed）。**这是 v0 真跑的前置。**
2. **加第二联系人**：候选 ① 李恪 `COGOS002:A0001`（现成、已有会话，能立刻验 agent↔agent）② Kilo 的号（语义最顺）。**YZ 未定。**
3. **给 Kilo 注册 cogos 号码**（kilo-resident 支线）：
   - 给 Kilo 一张 cogos 卡（建议 `COGOS002:A0006`），creds 指向现有 Kilo bot。
   - 接法：唐钰 `add_contact("Kilo", ["COGOS002:A0006"])` → `send` → Kilo bridge 收到 → 唤醒 Kilo 会话；反向 Kilo 用 `sendText` 发唐钰。
   - **身份表述**：号码给"Kilo 这个常驻实例"，不是给唐钰；两者别混成一个身份。

## 护栏 / 坑

- **两 agent 互发可自激**（同"空转"问题）→ 需回合上限 / 预算 / 不自动回环。
- 只动 kilo-resident / cogos phone，**不动 v0 的 consciousness/memory**。
- Kilo 宿主仍靠 `scripts/residentctl.sh` 手动起；`wake.mode:"tui"` 依赖窗口 attach，纯 headless 设 `async`。
- 跑 cogos 一律 `python3.11`、从 checkout 用 `-m`。

## 锚

- v0 主线：`handoff-build-agent-v0.md`
- kilo-resident 交接：`work/B/checkpoint/task-7-handoff-4.md`
- 架构结论：`locus/projects/cogos/entries/2026-09-13-cogos-v0-arch.md`
