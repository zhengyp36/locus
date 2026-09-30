# kilo-resident — 当前印象

Kilo 常驻 + 飞书/窗口双通道桥接；源码工程在 `../kilo-resident`（remote `zhengyp36/kilo-resident`），栈 Node/TS，宿主 `kilo serve`（4097）。承接工位 B task-7。

## 状态（2026-09-30，feat/kilo-phone 已 push）

- 现役分支 `feat/kilo-phone`；两个飞书 bot：`KILO-LOCUS-A`（dir `locus`）、`KILO-DOCTOR`（dir `withdrawal-reactions`）。
- 飞书 image/file 入站：下载到 `~/.local/state/kilo-resident/inbox/`，本地路径注入会话（`3c91429`）；失败回执 + 重投去重 + 异常兜底（`997bc6d`）。
- `/new`、`/pin` 切换后重 arm autoWatch（`70b5290`）；忙碌保护：正忙拒绝切换 + `switchSession` 防御 warn（`7bfcd0a`），在途回复不再静默丢。
- task-7 代结论仍成立：**窗口必须 attach 到常驻 server(4097)**，独立 TUI 唤醒打不通；terminal/timer 唤醒通道已实测。
- 验证入口：`npm run typecheck`、`npm run test:switch-busy-guard`、`npm run test:inbound-attachment`。

## 运维红线

- **严禁重启 `kilo serve`**（杀在跑会话）；只许 `ctrl-kilo bridge-restart`，且从**非 bridge 托管的 shell** 跑（重启脚本会随 bridge 一起被杀，已踩过）。
- 重启后 `ctrl-kilo status` 确认；日志在 `~/.local/state/kilo-resident/log/bridge.log`（`ctrl-kilo logs` 是跟随式，会阻塞）。

## 已知限制

- 两个飞书账号共用一个 bot → 同一 runtime/session；`inflight`、`lastChatId` 单值，一账号在跑另一只能排队，通知类发给最后发言的 chat。
- idle 事件若丢失（事件流重连间隙），busy 卡 true → 切换/注入类命令全被拒；逃生口 = bridge-restart（详见 entries）。
- 会话列表的 K 数是**累计 input**，非上下文长度。
- 待 YZ 裁决：真常驻宿主形态（修 daemon / systemd）。

## 锚点

- 忙碌保护（根因/why/被否补发）: `entries/2026-09-30-switch-busy-guard.md`
- task-7 细节: `entries/2026-09-12-task7-tui-wake.md` 等；旧交接/设计/报告在 `checkpoint/`（历史保留，不作活记忆）
- spike: `../kilo-spike/`
