# CHANGELOG

## 2026-09-12

- task-7 收尾：attach + TUI 唤醒通道打通并实测，terminal 长命令与窗口 timer 均能唤醒会话。
- 修 `originFor()`：未注册 session（attach 窗口）origin 由字面量 `"window"` 改为 `session|<dir>|<id>`，解决 timer "fired without a delivery channel" 静默丢弃。
- 本体 `../kilo-resident` 提交 `4bae464`（terminal/permission 工具、TUI 唤醒通道、attach 脚本一并入库）。

## 2026-09-11

- 立项 `kilo-resident`，承接工位 B task-7（Kilo 常驻 + 飞书/窗口双通道）spike。
- 设计决议冻结（9 条）；三项验证待补；未动 cogos / Kilo 本体。
- 转实现：本体 `../kilo-resident` 建库并 push（remote `zhengyp36/kilo-resident`）。
- 实测通：飞书文本往返、`/new` 重 pin、timer 全链路（准点投递+唤醒）、控制 API、模型 timer 工具。
- 宿主暂用 `kilo serve`（`kilo daemon` 本机启动超时未解决）。
