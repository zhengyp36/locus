# kilo-resident — 当前印象

Kilo 常驻 + 飞书/窗口双通道桥接；源码工程在 `../kilo-resident`（remote `zhengyp36/kilo-resident`）。承接工位 B task-7。

## 状态（2026-09-12 task-7 收尾，代码已提交）

- **task-7 收尾**：attach + TUI 唤醒通道打通并实测，terminal 完成事件以窗口正常"本地回合"注入（不再 QUEUED 孤儿）。
- 关键结论：**窗口必须 attach 到常驻 server(4097)**；独立 TUI 是进程内 server，插件 `serverUrl` 回落到占位 `localhost:4096`，唤醒打不通。
- 新机制：`wake.mode:"tui"` → `/tui/append-prompt`+`/tui/submit-prompt`，探测确认 + 回退 `prompt_async`；本机 `config.json` 已设 tui。
- 收尾修复：`originFor()` 对未注册 session（attach 窗口）由字面量 `"window"` 改为 `session|<dir>|<id>`，修 timer "fired without a delivery channel"（timer 之前被静默丢弃；terminal 因 `wakeSession` 有未知 session 兜底不受影响）。
- 实测：terminal 长命令（sleep 60）唤醒 ✅；窗口 timer（10s）唤醒 ✅。
- 本体代码已提交 `4bae464`（terminal/permission 工具、TUI 唤醒通道、attach 脚本一并入库）。
- 宿主仍暂用 `kilo serve`；栈 Node/TS。
- 未实现/待验：忙时会话排队、飞书入站/timer 走 tui 真机验、飞书真机往返（terminal→飞书、审批、`/pending`）、自动压缩阈值、真常驻宿主。
- 待 YZ 裁决：真常驻宿主形态（修 daemon / systemd）。

## 锚点

- 新会话入口: `../checkpoint/task-7-handoff-4.md`
- 上一轮交接: `../checkpoint/task-7-handoff-3.md`、`task-7-handoff-2.md`、`task-7-handoff.md`
- 设计+决议: `../checkpoint/task-7-design.md`
- 报告: `../checkpoint/task-7-report.md`
- 细节: `entries/2026-09-12-task7-tui-wake.md`、`entries/2026-09-11-task7-implementation.md`、`entries/2026-09-11-task7-design-decisions.md`
- spike: `../kilo-spike/`
