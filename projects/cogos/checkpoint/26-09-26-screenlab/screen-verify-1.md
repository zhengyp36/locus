# screen 验证批次 1｜假设清单 + 计划 + 步骤（2026-09-21）

> **用途**：把「agent = 一个普通 Linux 用户」设计里**所有还没被证实/证伪的假设**一次性列清，按环境分批验证，逐条落结果。
> **前序**：`handoff-screen-11.md`（目标重置 + 设计骨架 + §六概念结论）、`handoff-screen-12.md`（本 VM 垂直切片实测：切片 1/2）。
> **脚本**：本目录 `slice1..4.sh`（切片 1/2 已跑过，3/4 是探测）；原始证据 `ev-slice2-mutter.log`。
> **纪律**：不写生产代码；每条假设给出判据；结论先落本稿。

> ❌ **作废（2026-09-21 23:2x）**：本文 **A8（自持，需 reboot）**、**A11（user unit 集群自启）** 两条假设**已作废**——"自持 / 自启"需求撤销。§「A8 自持」整节、§一 表格 A8/A11 行、Phase 2 均已失效。见 `handoff-screen-17.md` §十一·11.3。
> **目标（唯一约束）见 `spec-screen-1.md` §0.0。**

## ⚠️ 已定案（2026-09-21，勿再当待验/待裁决）

- **浏览器后端默认 = Xwayland(X11) + XTEST**；文本输入走键盘合成，坐标靠 X11 全局坐标（详见 `screen-exp-log.md` §B1）。
- 由此：**A4 懒开不生效**（`--force-renderer-accessibility` 必需）、**A2 单消费者独占**、**A1 同坐标空间仅 X11 成立** 均已定性。
- 环境：headless 里 Xwayland 一直在，`--ozone-platform=wayland` 是当初没探对 display 的误判，**应去掉**。

## 0. 每条的记录模板

```
A#  假设：<一句话、可判真假>
    方法：<最小实验>
    判据：<什么算证实 / 证伪>
    结果：<证实 | 证伪 | 受限>  + 证据（命令/日志/截图）
    影响：<对设计/裁决的改动>
```

## 1. 假设清单（A1–A11）

| # | 假设 | 环境 | 现状 |
|---|---|---|---|
| A1 | mutter `ScreenCast`(v4)+PipeWire 能取到帧，且与 **a11y bounds 同一坐标空间** | 本 VM | **✅ 已验**：`RecordMonitor` 出 1920×1080；同空间**仅 X11 成立**（Wayland 局部坐标已证伪） |
| A2 | **同一路 ScreenCast 流**能复用来"给人看"，不新开显示、不改分辨率 | 本 VM | **❌ 证伪**：mutter 流**单消费者独占**；"不新开显示/不改分辨率"成立 → 改 **agent 单消费者 + fan-out**（**fan-out 已验 3/3**，见 `screen-exp-log.md` §P1） |
| A3 | `act element` 按 **id 重解析 bounds** 可行；**per-op 树/像素切换 + deadline** 可行 | 本 VM | **✅ 已验**（重解析 / 子树 vs 全树 / deadline 回退三项全过，见 `screen-exp-log.md` §P1） |
| A4 | Chromium 大 DOM 上 a11y 树**可用**；`--force-renderer-accessibility` 代价可控；**懒开**可行 | 本 VM（装 chromium） | **✅ 覆盖率已验**（自造页 + react.dev 227 可动作节点）；❌ **懒开不生效**（flag 必需）；代价待补 |
| A5 | headless 会话**不占 DRM master、不切 VT** | 本 VM | **已验**（合成器起来时 active VT 仍 `tty1`；`fuser /dev/dri/card0` 无持有者） |
| A6 | **tangyu 无 seat 也能让 mutter 拿到 `renderD128`**（不落 surfaceless） | 本 VM | **✅ 机制证实**（`card0` ACL → `Created gbm renderer`）；真 3D 归 A9 |
| A7 | **seat/VT 图形登录** → logind `graphical` + `card0` ACL；是否**切屏**（可否在**非活跃 VT**上登录而不抢） | 需切 VT，**要 YZ** | **部分验（抢屏已证，见 §3）** |
| ~~A8~~ | autologin/linger → **重启后无人介入**即有会话/合成器/服务 | 需 **reboot**，**要 YZ** | ❌ **作废**（自持非需求） |
| A9 | **真 GPU 渲染下浏览器指纹与真人一致**（非 SwiftShader/llvmpipe） | **需有 3D 的机器** | 本 VM 无 3D，做不了 |
| A10 | 多人/多 seat 协调 | 实操受限 | **留概念**（§六10） |
| ~~A11~~ | **user unit 集群**随会话自动起（a11y 总线+compositor+服务），不与旧 `screenlab` system 服务冲突 | 本 VM | ❌ **作废**（自启非需求） |

## 2. Phase 计划（按环境切，不按编号）

- **Phase 0（本 VM，无需 YZ）**：A1、A2、A3、A5、A6、~~A11~~ ❌作废 + A4（装 chromium）
- **Phase 1（需 YZ，切 VT）**：A7
- **Phase 2（需 YZ，reboot）**：A8
- **Phase 3（需 3D 机器）**：A9
- **留概念**：A10

## 3. 各条的方法 / 判据

### A1 像素兜底（ScreenCast + PipeWire）
- **方法**（tangyu 会话内）：
  1. `systemctl --user start pipewire wireplumber`
  2. `systemd-run --user --unit=wl --collect -- mutter --headless --virtual-monitor 1280x720 --wayland-display=wl`
  3. python + Gio：`org.gnome.Mutter.ScreenCast.CreateSession({})` → session path → 在 session 上调 `RecordVirtual`/`RecordMonitor`（**注意：session 对象 introspection 返回空，别依赖 introspect，按已知 API 调用**）→ 收 `PipeWireStreamAdded(u node)` 信号 → `Stream.Start()` → `Session.Start()`
  4. `gst-launch-1.0 pipewiresrc path=<node> num-buffers=1 ! videoconvert ! pngenc ! filesink location=/tmp/f.png`
- **判据**：拿到 1280×720 PNG；且把 a11y 给的 `CLICK-ME` bounds 中心换算成像素坐标后，**图像上该处确实是按钮**（人工/裁剪比对）。→ 证实「树与像素同空间」。

### A2 可见 = 同一路输出
- **方法**：对同一 ScreenCast 流**再挂一个消费者**（第二个 `pipewiresrc`），观察能否同时取帧；确认**不改分辨率、不新开 compositor**。
- **判据**：两路消费者都能取到帧，且 `screen.width` 等未变（后续用 Chromium 采）。"给人看"的最小形态成立（真正的 live viewer 可后置）。

### A3 act element + per-op 选择
- **方法**：在 slice 基础上写一个 20 行原型：按 a11y 元素路径重新 `get_extents` → 点；**先移动窗口再点**（验证"重解析"而非用旧坐标）。另测：全树遍历耗时 vs 子树查询（`getAccessibleAtPoint`/按 children 下钻），设 200ms deadline 看超时回退。
- **判据**：窗口移动后仍点中；子树查询耗时显著小于全树；超时能触发回退。

### A4 Chromium a11y 质量/代价
- **方法**：`sudo dnf install --disablerepo=tailscale-stable chromium`；本地造一个**大 DOM** 页面（离线，避免网络变量），分别用 (a) 带 `--force-renderer-accessibility`、(b) 不带（观察是否因 AT-SPI 存在而**懒开**）跑；测：树节点数、全树遍历耗时、子树查询耗时、页面加载耗时对比。
- **判据**：树可读且子树查询在预算内；flag 代价有数；懒开是否可靠。
- **注意**：本 VM 无 3D，WebGL 会露 llvmpipe → **指纹部分归 A9**。

### A5 不抢显示（硬证据）
- **方法**：compositor 跑起来后：`sudo fuser -v /dev/dri/card0`（无人持有）、`cat /sys/class/tty/tty0/active`（前后不变）、确认没有新 VT 被激活。
- **判据**：`card0` 无持有者；active VT 不变。
- **结果（2026-09-21，已验）**：`wl`(mutter `--headless --virtual-monitor 1280x720`) 起来时 **active VT 仍为 `tty1`**；`sudo fuser -v /dev/dri/card0` **无输出=无持有者**。→ headless 合成器**不占 DRM master、不切 VT**。证据见 `screen-lab-verify/`（`p0-setup.sh` 输出）。

### A6 tangyu 无 seat 拿到 GPU
- **现状**：`ssh`（无 seat）→ mutter 打不开 `card0`（0660 root:video）→ 日志 `Created surfaceless renderer without GPU`；zhengyp（有 seat，logind 给 ACL）→ `Created gbm renderer for '/dev/dri/renderD128'`。
- **方法**（逐个试，记哪个生效）：
  1. 临时 ACL：`sudo setfacl -m u:tangyu:r /dev/dri/card0`（重启/relogin 会掉）
  2. udev 规则给 `renderD128`/`card0` 固定 ACL
  3. 环境变量/EGL 选择（试 `EGL_PLATFORM`、`MESA_LOADER_DRIVER_OVERRIDE` 等，记录实际生效项）
- **判据**：mutter 日志出现 `Created gbm renderer for '/dev/dri/renderD128'`（而非 surfaceless）。
- **影响**：决定"要不要给 agent `card0` 读权限"——注意读权限 ≈ 可申请 master，**与"不抢显示"是两回事但要有意识**。本 VM 无 3D，只验"设备获取"，不验 3D。

### A7 图形登录路径（**要 YZ**）
- **问题**：seat0 只有一个；`Ctrl+Alt+F*` 会切物理屏。要判两件事：
  1. tangyu 图形登录 → logind 会话类型是否 `graphical`、`card0` ACL 是否到手；
  2. **能否在非活跃 VT 上跑图形会话而不抢屏**（若可以，则"seat 登录拿权限"与"不抢显示"可两全）。
- **方法**（可逆）：在 tty3/tty4 上让 tangyu 起图形会话，观察 `loginctl list-sessions`、`getfacl /dev/dri/card0`、`/sys/class/tty/tty0/active`。
- **判据**：得到 `graphical` + ACL，且 active VT 不变 → 两全；若 active VT 被切 → 证伪"seat 登录不抢屏"，需转 A6 路线。
- **回滚**：`Ctrl+Alt+F1` 或 `sudo chvt 1`。

- **结果（2026-09-21，本 VM，部分）**：
  1. **创建图形会话必抢屏**：`start gdm`（当时配了 zhengyp 的 autologin）→ active VT `tty1→tty2`；关 autologin 重启 gdm → active VT 回 `tty1`（greeter）。VT 切换由会话创建直接触发。
  2. **ACL 随"活跃"实时收放**：`chvt 3` 走开 → 会话 `Active=no / State=online`，`card0` 上 `user:zhengyp` ACL **被收回**；`chvt 2` 切回 → 立即恢复。→ **非活跃会话没有 ACL**。
  3. 会话属性实例：autologin 桌面 = `User=zhengyp / Type=x11 / Seat=seat0 / VTNr=2 / active`；greeter = `User=gdm / Type=wayland / Class=greeter / VTNr=1 / seat0 / active`。
  4. 设备现状：`card0` = `0660 root:video`，可靠 logind 的 uaccess 给**活跃 seat 会话**；`renderD128` = **0666 世界可读写**，本就不需要 ACL。
- **影响**：seat 路线上「不抢屏 + 拿权限」**不能两全**（本机证伪，需转 A6）。且 **A6 的真正问题不是"权限从哪来"**——`renderD128` 本就 0666；而是"**无 seat 时 mutter 为何 fallback 到 surfaceless**"（见 handoff-12 的 `Created surfaceless renderer`）。
- **备注**：fuser 里 card0 的 `m` 是 **mmap**，不是 DRM master（一度看错）；判活跃/权限只看 `Active/State` + `getfacl`。

### ~~A8 自持（**要 YZ / reboot**）~~ ❌ 作废
- **两个机制，先做 i**：
  - **i. linger + user unit（无 seat，最不侵入，不动 gdm/zhengyp 登录）**：`sudo loginctl enable-linger tangyu`；建 `~/.config/systemd/user/wl-compositor.service`（`mutter --headless --virtual-monitor ...`）与 `screenlab.service`（user），并令 `at-spi-dbus-bus.service` 起。→ reboot → `ssh tangyu@localhost` 验链路。
  - **ii. 图形 autologin（gdm/getty，会动登录行为，风险高）**：仅在需要"真·图形登录"时做，需明确回滚（改 `/etc/gdm/custom.conf`）。
- **判据**：reboot 后**无人介入**，`pgrep -x mutter` + `systemctl --user is-active ...` 全绿。
- **回滚**：`disable-linger` + 删 user unit。

### A9 指纹（**需 3D 机器**）
- **方法**：用 `handoff-screen-11.md` §六4 的采样脚本，在"headless compositor 会话"与"真桌面会话"分别采同一浏览器（WebGL renderer / outer / inner / hc / tz …）。
- **判据**：两者一致，且**非** `SwiftShader`/`llvmpipe`、`outer≠[0,0]`。
- **本 VM 结论**：不可验（vmwgfx `No 3D enabled`）。

### ~~A11 user unit 集群 & 旧服务~~ ❌ 作废
- **方法**：定义 tangyu 的 user units（compositor + a11y + 服务），确认随会话起来；`sudo systemctl stop/disable screenlab screenlab-xvfb`，确认新链不受影响、`/run/screen` 不撞。
- **判据**：新链 up；旧服务停后无副作用。

## 4. 入口与环境（复现）

```bash
# 进 tangyu（真 PAM 登录 → user manager）
ssh tangyu@localhost
export XDG_RUNTIME_DIR=/run/user/1001 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
# 跑本目录脚本
ssh tangyu@localhost 'bash -s' < screen-lab-verify/slice2.sh
```
- **sudo**：`sudo ... < ~/.secrets/centos.key`（**密码只喂 stdin**；`| tail < key` 会把 key 打出来，禁）。
- **`pkill -f <pattern>` 会自伤**（匹配到自己命令行）：杀进程用 `-x` 或 PID。

## 5. 已得线索（切片 1/2，详见 handoff-12）

- `--virtual-monitor WxH` 是 headless 有屏的关键（不带 → Xwayland 根窗口 0×0）。
- AT-SPI 树经 **GI（`Atspi-2.0.typelib`）** 直读，无需 pyatspi；按 bounds `xdotool` 点击**命中**（`BTN-CLICKED`）。
- rootless Xwayland 根窗口 `XGetImage BadMatch` → 像素**必须走 Wayland 侧**。
- `card0` 权限来自 **seat** 而非 ssh。

## 6. 会改设计的点（验证的真正产出）

- **A7** → 决定「seat 图形登录」还是「无 seat headless」；若 seat 登录必抢屏，则走 A6。
- **A6** → GPU 权限从哪来（udev/组/ACL），以及"给不给 card0"的安全取舍。
- **A8** → "自持"用 linger+user unit 还是图形 autologin。
- **A1/A4** → 像素与 a11y 的实际可用性，决定 `mode=auto` 的默认策略。

## 7. 系统改动与回滚

| 改动 | 回滚 |
|---|---|
| `/home/tangyu/.ssh/authorized_keys` 加 zhengyp pubkey | 删该行 |
| 装 `python3-pillow` | `sudo dnf remove python3-pillow` |
| gdm：关 autologin（`AutomaticLoginEnable=true→false`，原为 zhengyp）并重启；gdm 由 inactive→active | 备份 `/etc/gdm/custom.conf.autologin-on.20260921-002912`；`sudo cp` 回 + `sudo systemctl restart gdm`（恢复原状），或 `sudo systemctl stop gdm`（回到无 gdm） |
| （未动）旧 `screenlab.service` / `screenlab-xvfb.service` | —— |
| 临时进程/unit | 已清 |

## 8. Phase 0 首次尝试记录（2026-09-21，被并发打断）

- **A5 已验**（见 §3）：合成器起来时未占 `card0`、未切 VT。
- **环境就绪部分已验**：tangyu 会话内 `pipewire`/`wireplumber`/`at-spi-dbus-bus` 均可起；DisplayConfig 虚拟监视器 `Meta-0` 1280×720@60 正常。
- **A1 被打断（假失败）**：`ScreenCast.CreateSession` 报 `name is not activatable`，原因是**另一个并发会话**停掉了本会话的 mutter 并抢 D-Bus 名；同一调用在 `slice4.sh` 曾成功。
- **脚本**：`screen-lab-verify/p0-setup.sh`、`p0-screencast.py`（未完成，可续跑）。
- **新会话开工前先看 `handoff-screen-13.md` §三·五（并发冲突）**，并确认只保留一个会话做实验、以及是否恢复 `gdm`。
