# kilo-resident

Kilo 常驻 + 飞书/窗口双通道桥接（工位 B task-7 的落点工程）。

- 类型: 代码工程
- 本体路径: `../kilo-resident`
- remote: `git@github.com:zhengyp36/kilo-resident.git`（public）
- 来源: 工位 B `../checkpoint/task-7-*`（spike 完成，设计决议 9 条已定）

## 文件

工程管理：
- projects/kilo-resident/CHANGELOG.md — 阶段/变更记录

记忆：
- projects/kilo-resident/current.md / index.md / entries/

## 阶段

- 2026-09-11: 立项。设计决议冻结（9 条），补三项验证后转实现。实现前不碰 cogos / Kilo 本体。
- 2026-09-11: 转实现。本体建库并 push；最小飞书双通道 + timer 实测通；宿主暂用 `kilo serve`。
- 2026-09-12: task-7 收尾。attach + TUI 唤醒通道打通实测；修 timer 窗口 origin；本体提交 `4bae464`。
