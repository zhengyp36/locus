# handoff｜交接给新会话 · 2026-09-24 #44

> 接 #43。本会话 = **落码 slice 1（认证）+ slice 2（事件确认）**，并**讨论"认证之后的连接管理"（会话/席位/模式/抢占）**；代码改动**未 commit**。**下一会话先继续讨论连接管理**，未定项在 `design-screen-assist.md` **§3.2**。
> **规则 / 环境不在本文件**——见 **`screenlab-rules.md`**（先读）。

## 给新会话的第一句话

> 先读 **`screenlab-rules.md`** → 本文件 → **`design-screen-assist.md`**（**§3.2 连接管理（讨论中）** / §2 流程 / §3 + §3.1 认证 / §4.1 附着 / §4.2 / §4.5 / §4.7）→ **`spec-screen-1.md` §0.0**（唯一约束）。
> 本会话**已把 slice 1 + slice 2 落码并本机验证**（未 commit）；**没做** slice 3、附着真人会话、抢占、部署。
> 接下来 = **连接管理**：先把 §3.2 的未定项定下来，再落码。讨论已达成的三条关键：
> - **连接是管子 / 会话持状态（附着 + 单控制者 + 抢占）/ 席位持 role**；身份与模式挂连接，但**逻辑归 server**。
> - **只有真人是绝对抢占；agent 之间不互抢**（§0.0"显式 `yield` 他人才能接"），**空闲自动让出**防锁死。
> - 取得控制权即**作废 snapshot 世代**；进入前倾向加"物理输入静默 ≥ SETTLE"门槛。

## 本会话已做（代码，未 commit）

**slice 1 — 认证（新独立包 `screenlab/auth/`）**
- `auth/{protocol,registry,server,client,__init__}.py`：`hello→challenge→verify→result`；`Registry`(add/get/list/remove)、`AuthServer(consent)`、`AuthClient.attach`、`Key`(generate/load/sign)；错误码 `unknown_key/bad_sign/expired/denied/malformed`。
- `service/daemon.py`：仅 `--tcp --auth <reg>` 时 `_serve_conn` 走 0 阶段，过验把 `Record` 挂 `ConnState.identity`。
- `service/cli.py`：`keygen` / `register` / `attach` + `--auth`。
- `proto/client.py`：**不依赖 auth**；加 `from_channel`；G3：断流/重置 → `channel_closed`，超时 → `timeout`。

**slice 2 — 事件确认（新 `screenlab/auth/consent.py`）**
- `ConsentEndpoint`：真人机本地 Unix socket，`request`/`resolved` 事件 + `answer` 回传；有界等待、无人应答即 deny、断开清理。
- `service/daemon.py`：`--consent event` 建 endpoint、`endpoint.ask` 当 consent 回调；新增 `--consent-socket` / `--consent-timeout`。
- `service/cli.py`：`consent` 子命令（真人入口）；`--auth-timeout`（把"认证等待"与"同意等待"拆开，默认 300s）。

**验证（本机 127.0.0.1，一律 `/usr/bin/python3.11`）**
- 正向：`keygen→register→attach→capture`（Xvfb 1280×800 PNG）。
- 负向：`unknown_key` / `bad_sign` / `expired` / `channel_closed`（连接被拒 + 活连接被断）全对。
- slice2：同意→ok；拒绝→`denied`；无人应答→约 `consent-timeout` 后 `denied`；`auto` 回归正常。
- 未回归：非 auth TCP 路径照常；`--auth` 不给 `--tcp` 直接拒（Goal 1 unix 路径未动）。

## 本会话已讨论（连接管理，未定案 → 详 `design-screen-assist.md` §3.2）

- 三层：**连接=管道 / 会话=附着+单控制者+抢占 / 席位=role**；身份与模式挂连接，但逻辑归 server。
- 控制权：**真人绝对抢占**；**agent 之间不互抢**（§0.0）；**空闲自动让出**防锁死；取得控制权即作废 snapshot。
- 进入门槛：只把"物理输入静默 ≥ SETTLE"当 mechanical；**不**替 agent 判断"看清没看清"。
- 反例记牢：曾想"其他连接可立即打断"——与 §0.0 冲突，**已否**。
- 未定项：`SETTLE`/`IDLE`、`input_taken` 拒绝 vs 排队、generation 归属、动词（复用 `open(role)` vs 新增 `mode`）、控制者数量、分源实现（XI2 raw vs evdev vs 轮询）、consent 措辞、是否取消权限档。

## 状态 / 环境

- **代码** `../cogos` @ `feat/screenlab-p2`（`aa07964`）。
- **本会话未提交**：新增 `screenlab/auth/`；改 `proto/client.py`、`service/daemon.py`、`service/cli.py`。另 `screenlab/install/{screenlab,session-start.sh,session-stop.sh}` 有**非本会话**的未 commit 变更。
- **本会话文档改动**：`design-screen-assist.md`（新增 §3.2，未 commit）＋ 本文件。
- **依赖**：Ed25519 用已有 `cryptography`（49.0.0），**不新增依赖**。
- **环境坑**：开发机 `DISPLAY=localhost:11.0` 已失效（`xrandr`/`xdotool` 均挂）→ 本会话用 `Xvfb :99` 跑通采集；`import -window root` 本机没有，**地面真值留靶机**。
- **未决（不挡连接管理讨论）**：G4 clip 写路径；agent-tool 侧暴露 `attach`；靶机 tailnet 部署。

## 纪律（沿用 `screenlab-rules.md`，本线重点）

- **由目标裁决**（§0.0）；能推的**自决并记录**，真不清才飞书升级后停下等。
- **命令走 `terminal_exec`**（非阻塞）；不用 `sleep`；**不提交**。
- 验收用**公开入口 + 地面真值**（`import -window root`），不用自写 e2e。
- 交接阈值：上下文 ≥200K 或路径偏 → 写 handoff + 通知。

## 入口

- **规则 + 环境（先读）**：`screenlab-rules.md`
- **本线方案（本会话已改）**：`design-screen-assist.md`（**§3.2 = 连接管理**）
- **目标（唯一约束）**：`spec-screen-1.md` §0.0
- **#41 实验记录**：`screen-assist-exp-log.md`（三闸门 + G1–G4）
- 体系：`design-screen-system.md`；生命周期/命令层：`issue-screen-surface-lifecycle.md`
- 代码：`../cogos` @ `feat/screenlab-p2`
- 上一轮：#43 `handoff-screen-43.md`
