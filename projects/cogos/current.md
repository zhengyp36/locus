# cogos

多 agent 运行时，飞书作通信总线，前身 agent-study。通信层 + agent 账号链路已真机调通，Phone 抽象已接真实 Telecom 全链路。

## 当前状态

- get_members 30s 自阻塞根治并提交（`3976401`，643 passed）：reader 回调异步分发（2A），ack 仍同步读，自阻塞解除；真机验证未做。
- Phone 默认 client 改真机（`Phone()` 即接真机）；可观测性落地（`events.log` ndjson + 9 事件，观测=读盘）。
- Phone 接入 Telecom 完成并提交（`1e48652`+`a6e7cfc`+`44ab65c`，642 passed）：send 同步化 / members_changed 帧 / client_factory 注入 / list_chats + sync_groups / 异常感知 + 自动重连 / /LEAVE 事件即事实。真机场景 6~18 全绿。
- 会话 1~5 真机验证收尾全绿（真人进退群驱动 members 增减），过程见 checkpoint/。
- 群聊（Telecom 真群）已落地（`835bc3e`）：收发 / chat_registry / agent_cmd / group 区分 / tracker / group_event。
- Phone 即 agent 侧可 import API（`Phone()` → `add_card(number, pin)` → `listen`，`send`/`create_group`/`sync_groups`/`shutdown` 齐备）；旧裸 `startup(号码, on_msg, PIN)` 草图已废弃。

## 未决

- load_bot 与 AccountRef.ensure 分层错位（未实施）→ entries/2026-08-20-cogos-load-bot-vs-ensure.md
- phone-term（Phone 交互终端 TUI）待 YZ 讨论 → ROADMAP.md + entries/2026-08-23-cogos-phone-term.md
- 真机验证 2A 未做（真人进退群驱动 members_changed，确认 30s 消失）→ checkpoint/checkpoint-28.md

## 锚点

- 约定 / 关键文件 / 设计决策: README.md
- 阶段记录（权威流水账）: CHANGELOG.md
- 遗留问题: ISSUES.md · 候选方向: ROADMAP.md
- 认知地图: entries/project-map.md · 历史细节: index.md → entries/
- 真机验证过程: checkpoint/
