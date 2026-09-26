# screen-assist 实验日志（Goal 2 / 关系 3a · X11 闸门）· 2026-09-24

> 判据 = `spec-screen-1.md` §0.0 + 通用规则（易用性）；方案 = `design-screen-assist.md` §7。
> 纪律见 `screenlab-rules.md`。逐条记：判据 / 方法 / 结果 / 结论。
> 靶机 `surface-centos-9`（100.100.137.78），宿主 VBox `zhengyp@100.112.50.115`（VM `centos9`，`VBoxManage.exe` 在 `C:\Program Files\Oracle\VirtualBox\`）。
> 代码：`/opt/screenlab` 与 repo `feat/screenlab-p2`（tag `screenlab-goal1-2026-09-24`）逐文件 md5 一致，未改动。
> 结论：X11 闸门**机制通**；三处**方案/实现缺口**见文末。

## 0. 环境（真实 X11 桌面）

- 现状：GDM 在 `:0`（`WaylandEnable=false` → X11）；账户 `sva`(1001，纯 headless，无 XFCE 配置)、`zhengyp`(1000，管理用)；**无真实桌面登录**。
- 动作：按 §7「新建账户 + GDM autologin 更稳」建专用真人账户 **`human`**（uid 1002，密码 `human123`），写 `AccountsService` `XSession=xfce`，`AutomaticLoginEnable=True`；`systemctl restart gdm`（**未 reboot**）。
- 结果：得到**真实 XFCE/X11 会话** `human@:0`（`xfce4-session`/`xfwm4`/`xfce4-panel`/`xfdesktop`），`XAUTHORITY=/run/user/1002/gdm/Xauthority`。`import -window root` 抓屏 OK。
- 记录：屏幕 **1920x1093**（VBox 动态分辨率；rules 里 sva 的 1600x900 是其 Xvfb，两者不同）。

## 1. 闸门①：附着现有真实会话（capture + act 闭环）

- **判据**：能在**已存在的真实会话**上 capture + act 闭环，退出不破坏真人会话。
- **方法**：
  - 写 `human:~/.config/screenlab/session.env` → `SCREENLAB_DISPLAY=:0`、`SCREENLAB_XAUTH=/run/user/1002/gdm/Xauthority`；
  - **不用 `screenlab open`**（它写死 Xvfb），改用**临时 systemd user 单元** `screenlab-attach` 起 daemon：`python3 -m screenlab.service.cli daemon --display :0 --xauth… --socket /run/user/1002/screenlab.sock`；
  - 以 agent 身份只用公开入口：`python -m screenlab.service.cli …`（协议）、`surface windows/run/close`（命令面）；地面真值 `import -window root`。
- **结果**：
  - `info` → `screen/1`、`pillow`+`xdotool`；`displays` → `Virtual-1` 1920x1093。
  - `capture` → 1920x1093，与 `import -window root` **逐像素相同**（`ImageChops.difference` bbox=None）。✅
  - `surface run xfce4-terminal` → `started alive:true`，新窗口出现；协议 `act key ctrl+alt+t` → 新 Terminal 窗口 + `frame_hash` 变化。**capture→act→capture 闭环成立** ✅。
  - `surface windows` ✅。
  - `surface close <name>` **失败** ❌：`resolve_window` 用不带 `--onlyvisible` 的 `xdotool search --name`，命中 xfce4-terminal 的**隐藏 leader 窗口**（"Terminal" 有 2 个匹配，取到隐藏那个）；对其 `xdotool windowactivate --sync` **挂死**（`timeout 12` 后 rc=124）；可见窗口（另一 id）激活正常 rc=0。故 `surface close` 未关掉终端（最终靠 alt+F4 才关）。
  - 退出/停 daemon 后**真人桌面完好**（`xfce4-session`/`xfwm4`/`xfdesktop` 均在）。✅
- **结论**：附着真实会话的**采集+注入机制成立**。缺口见 §G1。

## 2. 闸门②：物理 / 注入分源

- **判据**：取消/抢占只认"非我注入"的事件（`design-screen-assist.md` §4.7）。
- **方法**：物理键盘设备 = **`/dev/input/event2`**（`AT Translated Set 2 keyboard`，PS/2）。自写 evdev 读取器（flush）；
  - **真人** = VBox 宿主 `VBoxManage controlvm centos9 keyboardputscancode …`（guest 内 = i8042 物理设备）；
  - **agent** = `xdotool key …`（XTEST）。
- **结果**：
  - VBox 注入 `1e 9e / 1f 9f / 20 a0 / 21 a1` → `event2` 上 **8 个 `EV_KEY`**（codes 30/31/32/33 按下+抬起）。✅
  - `xdotool key a b c d e`（rc=0）→ `event2` 上 **0 个事件**。✅
  - X 层：XI2 列表含 `Virtual core XTEST keyboard`(id=5) 与 `AT Translated Set 2 keyboard`(id=11)。
- **结论**：**X11 上"物理 vs XTEST 注入"可分**（evdev 层）。§4.7「取消热键只认真人 / 物理输入触发抢占」在 X11 成立；且 **VM 里 VBox 注入忠实模拟真人**（恰如 §7 预期）。旁证：读取器在 X 运行时可读 `event2`（X/libinput 未独占 grab）。
- 坑：`libinput debug-events` 重定向到文件时被 stdio 缓冲，`timeout` 杀掉即丢输出（首测为空）→ 用自写非缓冲读取器。

## 3. 闸门③：收回立即可见

- **判据**：停会话后 agent 下次调用**立即**报 `revoked`/`channel_closed`，**不挂死**（F1 反面教材）。
- **方法**：`systemctl --user stop screenlab-attach`（模拟真人收回），前后测 `info`/`capture` 延迟。
- **结果**：
  - 前：`info` rc=0，**162ms**。
  - 停后：socket 文件**仍在**（残留）；`capture` rc=1 **115ms** `connect_failed [Errno 111] Connection refused`；`info` rc=1 **154ms** 同。**快速失败、不挂死** ✅；真人桌面完好 ✅。
- **结论**：收回**即时可见（~0.1s）**成立；但**信号是通用 `connect_failed`，非语义化 `revoked`/`channel_closed`**，且 socket 残留。缺口见 §G3。

## 4. 续做（#40 之后）：修 G2 + 退场/剪贴板验证

- **修 G2**：`screenlab/install/surface` 的 `resolve_window` 改用 `xdotool search --onlyvisible --name`（与 `windows` 一致）。靶机部署后：`surface run xfce4-terminal` → `surface close Terminal` **rc=0、491ms** 成功关闭一个窗口（原对隐藏 leader 窗口 `windowactivate --sync` 挂死、并被 `timeout` 记 rc=124）。⚠️ repo 改动**未 commit**。
  - 副作用/边界：`--onlyvisible` 只认可见窗口 → 最小化/切到别的工作区的窗口按名字关不掉（本属合理；显式 id 不受影响）。
- **退场语义 = 松手**：`cli close` → `{ok:true, screen:{channels:0}}`；随后**新客户端仍可 `capture`**（daemon 存活），真人桌面（xfce4-session/xfwm4/panel/xfdesktop）完好。→ `close` ≠ 关桌面 ✅。
- **剪贴板（G4，新 bug）**：`surface clip "hello-from-agent"` 报 `clipboard_set chars:16`，但**立即无 owner**（`xclip: There is no owner for the CLIPBOARD selection`），读回为空。原因是写路径 `printf | xclip -loops 1` 的 selection-owner 随命令退出而亡（仅重定向 stdio 不足以存活）。候选：`setsid`/去掉 `-loops 1`/常驻 owner 进程。

## 缺口 / 待办（供 YZ 裁决，非本会话结论）

- **G1｜attach 现有 display 无公开入口**：`screenlab open` 写死 Xvfb；3a 需一条"附着已有 `:N`"的路径（session.env + 不起 Xvfb/desktop）。本会话用临时单元绕过。
- **G2｜`surface close` 选错窗口 → 已修（未 commit）**：`resolve_window` 的 `xdotool search --name` 缺 `--onlyvisible`，命中隐藏 leader 窗口 → `windowactivate --sync` 挂死。已加 `--onlyvisible`（与 `windows` 一致），靶机验证见 §4。
- **G3｜收回信号非语义化**：停会话后为通用 `connect_failed`，socket 残留。建议停时 unlink socket，客户端把"socket 消失/拒绝"映射为 `revoked`/`channel_closed`。
- **G4｜`surface clip` 写入不持久（新）**：写入报 `clipboard_set`，但 owner 立即消失、读回为空。见 §4。
- 备注：libinput 直读有缓冲坑（见 §2 坑）。

## 5. 3a 端到端：tailnet + auth + consent + 收回（2026-09-24 #45）

- **判据**：3a = agent 经通道附着真人**现有**会话，真人本地同意、可随时拿回（§0.0 关系 3a；§3.1/§3.2）。
- **方法（全用公开入口）**：
  - 靶机 `human@:0`：`screenlab open human --attach --display :0 --xauth /run/user/1002/gdm/Xauthority --tcp 100.100.137.78:8911 --auth <regdir> --consent event`（`tailscale0` 入 `firewall --zone=trusted`）。
  - agent（开发机 `acer-centos-9` / tailnet `100.79.86.84`）：`python3.11 -m screenlab.service.cli --tcp 100.100.137.78:8911 --auth <agent.key> …`；真人入口 `screenlab consent --auth <regdir> [--cancel]`。
  - 地面真值：`import -window root`、`xdotool getmouselocation`。
- **结果**：
  - **同意→capture**：consent 入口显示**登记表里的** `alias=kilocode`（不采信客户端自报）；capture 1920x1093，与 `import -window root` 尺寸一致（frame_hash 与 Goal 1 attach 路径同）。✅
  - **act**：`act pointer 0.5,0.5` → 靶机 `xdotool getmouselocation` = `x:960 y:546`**命中**（注入进真人真实会话）。✅
  - **收回**：`consent --cancel` → `revoked=1`；**持有中的** agent 连接下一次调用**立即 `channel_closed`**。✅
  - **负例**：未登记 pubkey → `unknown_key`（不过 consent）；真人拒绝 → `denied`。✅
  - **close**：`screenlab close human` 停服务、关端口，`human` 的 Xorg 桌面**不受影响**；再 `open` 复用 `session.env` 里的 tcp/auth。✅
- **实现改动（未 commit）**：
  - `session-start.sh`：attach 支持 `--tcp/--auth/--consent/--consent-socket/--consent-timeout`（写进 `session.env`，`serve.sh` 按 env 拼 daemon 参数）；`ready()` 按 TCP 或 unix 探测；`--tcp` 必须配 `--auth`，且仅 `--attach`。
  - `install-machine`：增装/校验 `python3-cryptography`（daemon 无条件 import auth，属硬依赖；此前靶机缺失导致 attach service 直接 crash-loop）。
  - `screenlab`：usage + `consent` 子命令；`session-create.md` 同步。
- **结论**：3a 在 X11 靶机（模拟真人）**机制全链通**。真机/真人是模拟的（§7 偏差），体验未验。
- **观察**：同一真人机若挂**多个** consent 入口，请求广播给全部、**先答者生效**（测试残留的 `yes` 进程曾误批准）→ 待定是否限一个入口。

## 6. 分源（XI2 视角，补充 §2）：不读 evdev 也能分

- **判据**：`service/presence` 需判别"物理 vs 我方 XTEST 注入"（§4.7）。
- **背景**：§2 用自写 evdev 读取器（需 root/`input` 组；`human` 不在 `input` 组）。daemon 以账户身份运行，读不了 `/dev/input/event*`。
- **方法**：`xinput test-xi2 --root`（`xinput` 靶机已装）；对照注入源。
- **结果**：
  - agent `xdotool key a` / `mousemove` → raw 事件 `device: 3 (5)` / `device: 5 (5)` / `Motion device: 4`（即 **XTEST 虚拟键盘 id=5 / 指针 id=4**）。✅
  - 宿主 `VBoxManage controlvm centos9 keyboardputscancode 1e 9e`（guest 内=物理）→ `device: 3 (11)` / `device: 11 (11)`（**AT Translated Set 2 keyboard**）。✅
- **结论**：**XI2 raw 事件的 source device id 即可分源，无需 evdev/root**：源 ∈ {XTEST 设备 id} → 注入；否则 → 物理。可行的 `presence` 实现（子进程 `xinput test-xi2 --root` + 按 device id 解析），与既有 shell-out（xdotool）风格一致。
- 待定：`xinput` 文本解析的稳健性；SETTLE/IDLE 与自动抢占的阈值。

## 7. 真人抢占落地（presence + preempt，2026-09-24 #45）

- **判据**：§0.0「真人可随时拿回」＋「任一时刻至多一个有效操作者」；§3.2「真人一上手 → agent 自动转观察态」。
- **实现**（未 commit）：
  - `service/presence.py`：`PresenceMonitor` 子进程跑 `xinput test-xi2 --root`，按 `device: (<source>)` 的 source id 判别；source ∈ XTEST 设备 id（`xinput list` 里含 `XTEST` 的 d）→ 我方注入，忽略；否则 → 物理 → 回调（`debounce` 去抖）。
  - `channels.Channels.preempt()`：把当前 input holder **降为 observer**（丢 input 位）**并滚代**；无 holder 时 no-op。
  - `daemon.ScreenDaemon`：`presence=True`（且有 `xinput`）时起 monitor，回调 → `channels.preempt()`；`--presence` 为全局 daemon 选项；attach 的 `session.env` 写 `SCREENLAB_PRESENCE=1`，`serve.sh` 据此加 `--presence`。
- **方法**：agent 连接（consent `--once` 批准）→ `open controller` + `capture`（gen=0）→ `act pointer 0.5,0.5`（持锁）→ 宿主 `VBoxManage controlvm centos9 keyboardputscancode 1e 9e`（物理）→ 再 `state`/`act`。
- **结果**：物理键后 `state` = `role=observer`、`gen=1`；下一次 `act` → **`no_input_bit`**。✅（`ps` 确认 daemon 带 `--presence`、`xinput test-xi2 --root` 存活。）
- **结论**：**真人物理输入即时夺回控制**在 X11 靶机成立。
- **未做（后置参数，待定）**：进入 controller 前的 **SETTLE** 静默门槛；**IDLE** 空闲自动让出；**物理热键**取消入口（§4.7）。以上均为「倾向」，非 §0.0 硬要求。

## 锚

- 目标：`spec-screen-1.md` §0.0；方案：`design-screen-assist.md`；规则：`screenlab-rules.md`。
