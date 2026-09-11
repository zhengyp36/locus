# task-7 验证：attach + TUI 唤醒通道（2026-09-12）

来源：工位 B `../../checkpoint/task-7-handoff-4.md`。本文件为 locus 记忆快照。

## 结论

- **窗口必须 attach 到常驻 server**：独立 TUI 是进程内 server、无监听，CLI 给插件的 `serverUrl` 回落到占位 `http://localhost:4096`（`serverUrl(){return D.url??new URL("http://localhost:4096")}`）→ 桥接 wake `fetch failed`。
- attach 到 4097 后插件 `serverUrl` 可达；terminal 完成事件**原生可唤醒**。
- **QUEUED 孤儿根因**：桥接用服务端 `prompt_async` 注入；attach 的 TUI 收到"非本客户端发起"的 user 消息 → 标记 QUEUED 且**永不出队**（服务端其实跑了回合，窗口不合并）。
- **修法**：`wake.mode: "tui"` → `POST /tui/append-prompt` + `/tui/submit-prompt`（带 `?directory=`），探测确认新 user 消息后返回其真实 id（供飞书回复路由），未确认回退 `prompt_async`。
- 实测：注入消息 id 为 TUI 生成的 `msg_<hex>`，窗口正常出队并触发模型回合。

## 机理要点

- 3 个 TUI 端点：`append-prompt {text}`、`submit-prompt`、`clear-prompt`；无窗口时都返回 200 `true`（no-op），**不能靠返回码判断窗口是否在场** → 只能探测（轮询 session 新消息）。
- 忙时注入仍会滞留：桥接只对飞书 runtime 做 busy/队列，对窗口 terminal owner 是盲注入；tui 模式下 TUI 忙时 append+submit 可能本地排队，探测超时回退 async 有重复投递风险。
- `clientFor` 需归一化尾斜杠：插件上报 `http://127.0.0.1:4097/`，与 `daemonUrl http://127.0.0.1:4097` 字符串不等 → 会误建无鉴权 client 吃 401。
- `kilo attach` 默认目录 = serve 进程 cwd（非客户端 cwd），必须显式 `--dir "$PWD"`；`TERM=xterm-256color` 否则显示问题。

## 收尾修复：timer 窗口 origin

- 现象：attach 窗口设的 timer 准点触发，但桥接日志 `fired without a delivery channel`，会话没被唤醒。
- 根因：`originFor()` 对本会话（未登记进 `runtimes`）返回字面量 `"window"`；`onTimerFire()` 只处理 `feishu|`/`session|`，`window` 无分支 → 静默丢弃。terminal 唤醒未受影响，因 `wakeSession()` 对未知 session 有 `if (!rt) 直接 deliver()` 兜底。
- 修法：`originFor(sessionID, directory)` 在无 runtime 但有 sessionID 时返回 `session|<dir>|<id>`（plugin 已传 `directory`），复用已有 `deliver()` TUI 通道。
- 实测：窗口 timer（10s）唤醒 ✅；terminal 长命令（`sleep 60`）唤醒 ✅。

## 本轮改动（已提交 `4bae464`）

- `src/bridge.ts`：`wakeMode`、`deliver()`/`tuiDeliver()`、`promptWake()` 回退、`clientFor` 归一化；`inject/deliverWake/wakeSession/onTimerFire` 改走 `deliver()`；`originFor()` 兜底 `session|<dir>|<id>`。
- `src/types.ts`：`wake?: { mode?: "async"|"tui" }`；`config.example.json` 默认 async；本机 `config.json`=tui。
- `scripts/residentctl.sh`：`attach [session|new] [dir]`、`bridge-restart`。
- `scripts/attach-kilo`（自包含，装到 `~/.local/bin/attach-kilo`）：`attach-kilo [session|new|-] [dir]`。

## 待办（交接给新会话）

1. 忙时会话排队（对所有被观注 session 订阅 idle/status）。
2. 飞书入站 / timer 走 tui 的**真机验证**（路由已接线）。
3. 飞书真机往返：terminal 回复转飞书、`/timer`、`ask` 审批 `/allow` `/deny`、`/pending`。

细节见 `../../checkpoint/task-7-handoff-4.md`。
