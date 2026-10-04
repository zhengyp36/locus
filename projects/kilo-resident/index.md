# 索引

- 2026-09-11: 立项（承接工位 B task-7 spike）→ README.md
- 2026-09-11: task-7 设计决议冻结（9 条）+ 三项待验证 → entries/2026-09-11-task7-design-decisions.md
- 2026-09-11: 上下文轮换决议（原地 summarize + 阈值触发；`/new` 需重 pin）→ entries/2026-09-11-task7-design-decisions.md
- 2026-09-11: 命令执行/定时器决议（借鉴 cogos terminal + timer；timer 与命令解耦、用户可见可控）→ entries/2026-09-11-task7-design-decisions.md
- 2026-09-11: 转实现；最小飞书双通道 + timer 实测通，宿主暂用 kilo serve → entries/2026-09-11-task7-implementation.md
- 2026-09-12: 验证 attach + TUI 唤醒通道；QUEUED 孤儿根因与修法、attach 坑 → entries/2026-09-12-task7-tui-wake.md
- 2026-09-12: task-7 收尾；修 timer 窗口 origin（"fired without a delivery channel"），terminal/timer 唤醒实测，本体提交 4bae464
- 2026-09-30: feat/kilo-phone：飞书 image/file 入站（3c91429、997bc6d）、/new /pin 重 arm autoWatch（70b5290）→ 见 current.md 与 git log
- 2026-09-30: /new /pin 忙碌保护（7bfcd0a）：正忙拒绝切换，在途回复不再静默丢；补发方案被否 → entries/2026-09-30-switch-busy-guard.md
- 2026-10-04: 富文本 post 入站被静默丢（飞书自动编号→post）+ 入站必有回执；解析 post/内嵌图、不支持类型回执、ack always/delayed/off（88c8ac4，已部署）→ entries/2026-10-04-inbound-rich-text-and-ack.md
