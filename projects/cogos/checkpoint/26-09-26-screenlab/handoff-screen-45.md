# handoff｜交接给新会话 · 2026-09-24 #45

> 接 #44。本会话 = **落码 §3.2（会话管理）+ 定案文档**，并**提交 + 推送**本线全部未 commit 工作；会话管理已本机验证。**下一会话从"后置项"起**（见下）。
> **规则 / 环境不在本文件**——见 **`screenlab-rules.md`**（先读）。

## 给新会话的第一句话

> 先读 **`screenlab-rules.md`** → 本文件 → **`design-screen-assist.md`**（**§3.2 已定** / §2 流程 / §3 + §3.1 认证 / §4.1 附着 / §4.4 / §4.7）→ **`spec-screen-1.md` §0.0**（唯一约束）。
> 本会话把 **§3.2 会话管理**落码并本机验证、**已 commit + push**（`../cogos` @ `feat/screenlab-p2`，`a8f4044` + `0697c27`）。
> 接下来 = **后置项**，请 YZ 定序：① 自动抢占 / 分源 / `SETTLE`/`IDLE`/物理热键；② 弹窗（slice 3）；③ 附着真人现有会话端到端 + 靶机 tailnet 部署。
> 三条已定基调（§3.2）：**连接=管子 / 会话持状态（单控制者 + 滚代 + 收回）/ 席位持 role**；**真人绝对抢占，agent 不互抢，空闲自动让出**（后置）；**取得控制权即作废快照世代**。

## 本会话已完成（已 commit + push）

- **提交**：`a8f4044` `feat(screenlab): authenticate and manage assist sessions`；`0697c27` `feat(screenlab): serve an existing display with open --attach`。
- **会话管理（§3.2 本轮）**：
  - 席位身份 = **server 验证的 auth `Record`**（不采信客户端自报）；`open`/`state` 暴露 `seat`（`role`/`subject`/`identity`），`screen.generation`。
  - **generation 归 Session**：释放控制即滚代；`capture` 盖章、`act` 校验 → 跨代 `stale_snapshot`；`act` **先验快照再取控制**（被拒不会偷锁）。
  - `input_taken` **拒绝不排队**；**复用 `open(role)`**，不新增 `mode`；**单控制者**。
  - **显式收回**：断连释放 + consent socket `cancel` → `revoke_all`（清席位、关连接；agent 下次调用即 `channel_closed`）。
  - consent 措辞改"**加入本次协助会话**"；**取消权限档**（一次同意即带操作权）。
- **文档**：`design-screen-assist.md` **§3.2 改"已定"**，§2 step5 / §6 对齐（去"默认只读起步"）。
- **健壮性**（来自并发会话，本会话复核并一并提交）：`backends.py`/`backends_android.py` 子进程加超时、去掉 `xdotool --sync`；`proto/framing.py` 加 `Channel.close()`，`ScreenClient`/`AuthClient.close()` 真正释放 fd。
- **install**：`open --attach`（附着已存在 display，不再拥有 Xvfb，`close` 不碰桌面）+ `screenlab-attach.user.service`。

## 验证（本机 `Xvfb :99`，一律 `/usr/bin/python3.11`）

- 会话语义 **13/13**：席位身份=登记 alias、act 取控制、消费后 stale、他席 `input_taken`、yield 滚代→旧快照 stale、observer 无 input 位、断连释放控制。
- 本地收回 **5/5**：`--consent event` 下同意→加入→操作→`cancel`→连接被关，agent 下次调用 `channel_closed`。
- 回归：`--auth` 不给 `--tcp` 直接拒；unix（Goal 1）路径 `capture` 得 1280×800 PNG；全包 `compileall` 通过。

## 未决 / 下一会话候选（后置，**待 YZ 定序**）

- **自动抢占 / 分源**（XI2 raw 主、轮询降级）＋ **`SETTLE`/`IDLE`** ＋ 物理热键（§3.2"后置"、§4.7）。
- **弹窗（slice 3）**——同一 `consent` hook，接口不变。
- **附着真人现有会话端到端**（install `--attach` 已落，未在真人机/靶机跑）＋ **靶机 tailnet 部署**。
- Wayland 先不做；G4 clip 写路径仍未决；agent-tool 侧暴露 `attach` 后置。

## 状态 / 环境

- **代码** `../cogos` @ `feat/screenlab-p2`（`0697c27`，已 push `origin`）。
- **工作区干净**（仅 `__pycache__` 忽略项）。
- **依赖**：Ed25519 用已有 `cryptography`（49.0.0），**不新增依赖**。
- **环境坑**：开发机 `:0` 失效 → 用 `Xvfb :99`；`import -window root` 本机没有，**地面真值留靶机**；`xdotool mousemove --sync` 曾在指针已到位时挂死（已改为不带 `--sync`）。
- **注意**：本会话期间发现**并发来源**的工作区改动（疑另一会话在修同一问题）；提交前工作区同时含本会话与他会话改动，已分两个 commit 一并提交。若他会话仍在跑，请注意别重复改。

## 纪律（沿用 `screenlab-rules.md`，本线重点）

- **由目标裁决**（§0.0）；能推的**自决并记录**，真不清才飞书升级后停下等。
- **命令走 `terminal_exec`**（非阻塞）；不用 `sleep`；本会话经 YZ 明确指示后**已提交**（此前纪律为"不提交"）。
- 验收用**公开入口 + 地面真值**，不用自写 e2e。
- 交接阈值：上下文 ≥200K 或路径偏 → 写 handoff + 通知。

## 入口

- **规则 + 环境（先读）**：`screenlab-rules.md`
- **本线方案**：`design-screen-assist.md`（**§3.2 = 会话管理，已定**）
- **目标（唯一约束）**：`spec-screen-1.md` §0.0
- **#41 实验记录**：`screen-assist-exp-log.md`（三闸门 + G1–G4）
- 体系：`design-screen-system.md`；生命周期/命令层：`issue-screen-surface-lifecycle.md`
- 代码：`../cogos` @ `feat/screenlab-p2`
- 上一轮：#44 `handoff-screen-44.md`
