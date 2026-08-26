# checkpoint-3 — 定稿推进思路 + 第 1 件产出（通信能力清单）

## 定稿思路（YZ 确认）

1. 第 1 件照做：整理通信记忆 → 产出能力清单（做小，不展开）。
2. 定 D1：智能系统设计第一目标 + 边界。
3. 用 D1 定向加载 agent-study 对应概念（替代无目标加载）。
4. 进入设计。

实质：把「2→3」改成「定 D1 → 定向加载 → 设计」。设计不是从零，是「agent-study 理论映射到 cogos 现状」。

## 工作方式调整（YZ 定）

- 过程记录只写 `../checkpoint/`（/undo 不回退），不写 locus 记忆文件（会被 /undo 回退）。
- checkpoint 作为会话内记忆锚点；会话结束时再整理 checkpoint 更新记忆。

## 第 1 件产出：通信能力清单（agent 靠什么与 agent/真人交流）

一句话：agent 通过 `Phone` 抽象（底层飞书 Telecom 总线）与 agent/真人交流，能力如下——

1. **消息收发**：p2p（agent↔agent、agent↔真人）+ 群聊（收发 + @成员 `@number`/`@all`）。
2. **群管理**：建群 / 拉人（真人 + agent 分批 me_join）/ 查成员（get_members）/ 成员变化感知（`members_changed` 帧：真人进退群、bot 进退群统一信号）。
3. **命令机制**：`/` 单命令、`//` 普通文本，多 handler 注册表（agent_cmd）。
4. **账号/身份链路**：provider 三身份（admin / bs / agent）、`AccountRef` 解析 `provider:number`、PIN 校验、账号失效/刷新（12h TTL + 心跳重校验）。
5. **领域 API**：`Phone()` → `add_card(number, pin)` → `listen(on_msg)`；`send` / `create_group` / `sync_groups` / `shutdown`。底层 Telecom 可换 client（真机 / Fake）。
6. **可观测性**：`events.log` ndjson + 事件流（观测=读盘）。

细节锚点：cogos `CHANGELOG.md`（权威流水账）+ `entries/`。真机验证见 `projects/cogos/checkpoint/`。

## 关键结论/决策

- YZ 确认三件事推进思路（含「定 D1 → 定向加载 → 设计」微调）。
- YZ 定工作方式：过程只写 checkpoint，记忆待会话结束更新。

## 遗留

- D1 未定（下一步：智能系统设计第一目标 + 边界）。
