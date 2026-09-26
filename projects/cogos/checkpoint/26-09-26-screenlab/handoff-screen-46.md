# handoff｜交接给新会话 · 2026-09-24 #46

> 接 #45。本会话 = **落码并靶机验证 ③（附着真人现有会话 = tailnet + auth + consent + 收回）＋ ① 核心（分源 + 真人抢占）**。
> **全部改动未 commit**（YZ 未定）。**下一会话从 ① 收尾 / ② 或 真人机 起（待 YZ 定序）**。
> **规则 / 环境不在本文件**——见 **`screenlab-rules.md`**（先读）。

## 给新会话的第一句话

> 先读 **`screenlab-rules.md`** → 本文件 → **`design-screen-assist.md`**（§3.2 已定 + 后置状态已更新）→ **`spec-screen-1.md` §0.0**（唯一约束）。
> 代码 `../cogos` @ `feat/screenlab-p2`，**工作区有未提交改动**（6 改 + 1 新，见下），**先别 commit**。
> 靶机 `surface-centos-9` 的 `human@:0` 现被 attach，daemon 带 `--presence` 跑在 `100.100.137.78:8911`（auth + consent event）。

## 本会话已完成（**未 commit**）

**③ 附着真人现有会话端到端（tailnet + auth + consent + 收回）**
- `screenlab/install/session-start.sh`：attach 支持 `--tcp/--auth/--consent/--consent-socket/--consent-timeout`，写进 `session.env`，`serve.sh` 按 env 拼 daemon 参数；新增 `ready()`（TCP 或 unix 探测）；`--tcp` 必配 `--auth`、且仅 `--attach`。
- `screenlab/install/screenlab`：usage；新增 `consent` 子命令（真人本地入口）。
- `install-machine`：增装并校验 `python3-cryptography`（daemon 无条件 import auth = 硬依赖；靶机原缺 → attach service crash-loop）。
- `screenlab/install/session-create.md`：CLI / 依赖 / attach 说明同步。
- 靶机侧：`tailscale0` 入 `firewall --zone=trusted`（runtime + permanent）。

**① 分源 + 真人抢占（核心）**
- 新增 `screenlab/service/presence.py`：`PresenceMonitor` 子进程跑 `xinput test-xi2 --root`，按 `device: (<source>)` 的 source id 分源（source ∈ XTEST 设备 id = 我方注入，忽略；否则 = 物理 → 回调，带去抖）。
- `screenlab/service/channels.py`：新增 `Channels.preempt()`（当前 input holder → observer + 滚代；无 holder 时 no-op）。
- `screenlab/service/daemon.py` / `cli.py`：`--presence`（全局），`presence=True` 且有 `xinput` 时起 monitor；回调 → `preempt()`。
- attach 的 `session.env` 写 `SCREENLAB_PRESENCE=1`，`serve.sh` 据此加 `--presence`。

## 验证（靶机 `human@:0`；agent = 开发机 `acer-centos-9`，tailnet `100.79.86.84`）

- **同意→capture**：consent 入口显示**登记表**里的 `alias=kilocode`（不采信客户端自报）；capture 1920x1093，与 `import -window root` 尺寸一致。
- **act**：`act pointer 0.5,0.5` → 靶机 `xdotool getmouselocation` = `x:960 y:546` **命中**。
- **收回**：`screenlab consent --cancel` → `revoked=1`；**持有中**的 agent 连接下一次调用**立即 `channel_closed`**。
- **负例**：未登记 pubkey → `unknown_key`（不过 consent）；真人拒绝 → `denied`。
- **close 语义**：`screenlab close human` 停服务/关端口，`human` 的 Xorg 桌面**不受影响**；再 `open` 复用 `session.env` 的 tcp/auth。
- **抢占**：物理键（宿主 `VBoxManage … keyboardputscancode`）后 → `state` = `role=observer`、`gen+1`，下一次 `act` → **`no_input_bit`**。
- 详见 `screen-assist-exp-log.md` §5/§6/§7。

## 未决 / 下一会话候选（**待 YZ 定序**）

- **① 收尾**：`SETTLE`（进 controller 前物理静默门槛）、`IDLE`（空闲自动让出）、**物理热键**取消入口（§4.7）。均为"倾向"，非 §0.0 硬要求。
- **② 弹窗（slice 3）**——同一 consent hook，接口不变。
- **真人机（非靶机）端到端**：靶机是人类"模拟"（§7 偏差），体验未验；真机才是 3a 终点。
- **观察（待裁决）**：同一真人机挂**多个** consent 入口会竞争、**先答者生效**；测试残留 `yes` 进程曾误批准。是否限一个入口？
- Wayland 先不做；G4 clip 写路径仍未决；agent-tool 侧暴露 `attach` 后置。

## 状态 / 环境

- **代码** `../cogos` @ `feat/screenlab-p2`，**未 commit**：改 `install/session-start.sh`、`install/screenlab`、`install/session-create.md`、`service/channels.py`、`service/cli.py`、`service/daemon.py`；新 `service/presence.py`。
- **靶机**：`human@:0` attached；daemon = `python3 -m screenlab.service.cli --presence --tcp 100.100.137.78:8911 --auth /home/human/.config/screenlab/registry --consent event …`；注册表含 agent pubkey（alias `kilocode`）；防火墙 trusted 含 tailscale0。
- **依赖**：靶机 `dnf install python3-cryptography`（36.0.1，已装）；开发机 `cryptography 49.0.0`。
- **环境坑**：
  - 宿主 VBox `VBoxManage.exe` 在 `C:\Program Files\Oracle\VirtualBox\`，ssh 里须全路径；宿主是 `100.112.50.115`（**rules 里写成 `100.100.112.50.115` 是笔误**，已修）。
  - 跑 consent 测试**别留 `yes y` 残留进程**（会误批准后续请求）；清理按 pid（`pkill -f "service.cli.*consent"` 会匹配到自身命令行）。
  - 靶机 python3 = 3.9；本机一律 `/usr/bin/python3.11`。
- agent 侧 key 在开发机 `/tmp/kilo/agent.key`（测试用，可弃）。

## 纪律（沿用 `screenlab-rules.md`）

- **由目标裁决**（§0.0）；能推的自决并记录，真不清才飞书升级后停下等。
- **命令走 `terminal_exec`**（非阻塞）；不用 `sleep` 收尾；**不提交**（本轮改动等 YZ 定）。
- 验收用**公开入口 + 地面真值**（`import -window root` / `xdotool getmouselocation`），不用自写 e2e 当验收。
- 10 分钟闹钟 / 交接阈值（本轮在 200k 触阈值 → 写本文件 + 通知）。

## 入口

- **规则 + 环境（先读）**：`screenlab-rules.md`
- **本线方案**：`design-screen-assist.md`（**§3.2 已定**；后置状态已更新）
- **目标（唯一约束）**：`spec-screen-1.md` §0.0
- **实验记录**：`screen-assist-exp-log.md`（§5 3a e2e / §6 XI2 分源 / §7 抢占）
- **代码**：`../cogos` @ `feat/screenlab-p2`（**未 commit**）
- 上一轮：#45 `handoff-screen-45.md`
