# 索引

- 2026-09-11: 立项（承接工位 B task-7 spike）→ README.md
- 2026-09-11: task-7 设计决议冻结（9 条）+ 三项待验证 → entries/2026-09-11-task7-design-decisions.md
- 2026-09-11: 上下文轮换决议（原地 summarize + 阈值触发；`/new` 需重 pin）→ entries/2026-09-11-task7-design-decisions.md
- 2026-09-11: 命令执行/定时器决议（借鉴 cogos terminal + timer；timer 与命令解耦、用户可见可控）→ entries/2026-09-11-task7-design-decisions.md
- 2026-09-11: 转实现；最小飞书双通道 + timer 实测通，宿主暂用 kilo serve → entries/2026-09-11-task7-implementation.md
- 2026-09-12: 验证 attach + TUI 唤醒通道；QUEUED 孤儿根因与修法、attach 坑 → entries/2026-09-12-task7-tui-wake.md
- 2026-09-12: task-7 收尾；修 timer 窗口 origin（"fired without a delivery channel"），terminal/timer 唤醒实测，本体提交 4bae464
