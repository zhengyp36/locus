# screen 实验日志｜M2 虚拟桌面 + 反检测（2026-09-21 起）

> **用途**：把 M2（agent 自己用图形界面）要验的点**逐条实验、逐条记录**。
> **关系**：`screen-verify-1.md` 是假设清单与计划；本文件是**执行日志**。结论定案后回写 verify / spec。
> **目标（对齐版）**：
> - M1 ssh shell（已满足）。
> - **M2 = agent 有一套自己的图形桌面 + 真浏览器，给 IP/账号即可远程操作，不上物理屏**。
> - M3 = 向日葵式接管真人桌面、真人围观（另案）。
> - "像真人" = **过反自动化检测 / 指纹**（F1）。**出口 IP 暂不考虑**（个人开发，VPN 所致）。

## 纪律与前置

- 只保留**一个** Kilo 会话做实验；单元统一命名 `screenlab-*`（弃用 `wl`/`wl-slice`）。
- 目标账号 `tangyu(1001)`；入口 `ssh tangyu@localhost`，`export XDG_RUNTIME_DIR=/run/user/1001 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus`。
- sudo：`sudo ... < ~/.secrets/centos.key`（**密码只喂 stdin**）。
- `pkill -f <pattern>` 会自伤 → 用 `-x` 或 PID。
- 不写生产代码；每条实验先给判据，结果落本文件。

## 实验清单

| # | 目的 / 假设 | 方法 | 判据 | 机器 | 状态 |
|---|---|---|---|---|---|
| **E2** | **完整桌面**（gnome-shell）能在虚拟后端起来，且能跑 Wayland 客户端 | `gnome-shell --headless --virtual-monitor 1280x720`（tangyu user unit）；再起一个 Gtk/Wayland 客户端 | shell 常驻不崩；客户端能连上并开窗 | 本 VM | ✅ 证实 |
| **E3** | 虚拟显示器**暴露给客户端的屏幕参数**（尺寸/型号/EDID/多屏），可否定制 | 客户端读 `Gdk.Monitor` / DisplayConfig；试 `--virtual-monitor` 变体、多屏 | 拿到参数；能改动或确认不能 | 本 VM | ✅ 参数拿到，定制性待查 |
| **E4** | a11y 树可读；a11y 激活**是否留可探测痕迹** | 壳内起客户端，读 AT-SPI 树找按钮 | 找到按钮并拿到 bounds；痕迹待 Chromium | 本 VM | ✅ 读树证实；痕迹待验 |
| **E5** | **输入注入**：headless 会话里怎么点击/移动 | XTEST(X11) vs Mutter RemoteDesktop(Wayland) | 客户端收到 enter/press/clicked | 本 VM | ✅ X11 证实；Wayland 待解 |
| **E6** | **行为 humanization** 可行性与设计 | 造带轨迹/时序的注入，测页面响应 | 有轨迹、时序自然、页面逻辑正常 | 本 VM | ✅ 证实（初步，见下） |
| **A1** | ScreenCast+PipeWire 取帧，且与 a11y bounds **同坐标空间** | `RecordMonitor` 取帧 + Gtk 客户端读 a11y bounds 比对 | 拿到 1920×1080 PNG ✅；同空间**仅 X11 成立** | 本 VM | ✅ 取帧成功；Wayland 坐标证伪 |
| **A2** | **同一路流**能复用"给人看"，不改分辨率、不新开显示 | 同一流挂第二个 `pipewiresrc` | 两路都能取帧；尺寸不变 | 本 VM | 待做（依赖 A1） |
| **A3** | `act element` 按 id **重解析 bounds**；per-op 树/像素切换 + deadline | 20 行原型：先移窗再点；全树 vs 子树耗时；200ms deadline | 移窗后仍点中；子树显著快；能回退 | 本 VM | 待做 |
| **A4** | Chromium 大 DOM 上 a11y **质量/代价/懒开** | 装 chromium；离线大 DOM；(a) 带 `--force-renderer-accessibility` (b) 不带 | 树可读、子树查询在预算内；懒开可靠 | 本 VM | 🔶 覆盖率已验（见下）；代价/懒开待做 |
| **A6** | 无 seat 时为何 fallback surfaceless；能否拿真 GPU | 试 setfacl card0 / 组 video / EGL 变量；看日志 | 日志出现 `gbm renderer for renderD128` | 本 VM | ✅ 机制证实（真 3D 待 E1） |
| **E1/A12** | **反检测基线**：真 GPU 下指纹与真人一致 | 3D 机器上采 A12 清单（WebGL/outer/inner/UA-CH/tz/字体/WebRTC…） | 非 SwiftShader/llvmpipe；各项自洽 | **需 3D 机器** | 条件触发，暂缓 |
| **A8** | 重启后**无人介入**图形栈自动就绪（或 agent ssh 拉起） | linger + user units；或 autologin | reboot 后 `pgrep gnome-shell` + user units 全绿 | 需 reboot，要 YZ | 待做 |

**执行顺序（本 lab）**：E2 → E3 → E4 → A1 → A2 → A3 → A4 → E5 → A6；E1 条件触发；A8 需 YZ。

---

## 记录

### E0 基线（2026-09-21 15:05）

- Kilo 会话：**仅 1 个 attach**（PID 5922，server 4097）→ 并发冲突已消失。
- `gdm` active，greeter 占 **seat0/tty1**（`User=gdm, Type=wayland, Class=greeter, VTNr=1, active`）。
- zhengyp 只有远程 tty 会话（pts/0、pts/1，无 seat）。
- `/dev/dri/card0` = `0660 root:video` + ACL 给 **gdm**（活跃会话）→ 再次印证"ACL 随活跃"。
- `/dev/dri/renderD128` = **0666** 世界可写。
- zhengyp ∈ `video` 组；tangyu 不在。
- `gnome-shell 40.10`；`mutter` 支持 `--headless --virtual-monitor`、`gnome-shell` 同样支持 `--headless/--display-server/--nested/--virtual-monitor`。
- 已装 `gnome-remote-desktop 40.0`（GNOME 40 无 remote-login 系统会话特性）；**chromium 未装**；weston/sway 未装。
- tangyu ssh 可进，`XDG_RUNTIME_DIR=/run/user/1001`，user manager running。

### E2 完整 headless 桌面（gnome-shell）— 2026-09-21 15:07 · ✅ 证实

- **假设**：完整桌面能在虚拟后端起来，且能跑 Wayland 客户端。
- **方法**：tangyu user unit `screenlab-shell` 跑
  `gnome-shell --headless --virtual-monitor 1280x720 --wayland-display=screenlab-0`；再跑 Gtk3 Wayland 客户端（`screen-lab-verify/e2-client.py`）。
- **结果 ✅**：
  - shell 常驻，`systemctl --user is-active screenlab-shell` = active；socket `/run/user/1001/screenlab-0`。
  - 总线服务在：`org.gnome.Mutter.DisplayConfig.GetResources` 正常返回。
  - Gtk 客户端连上（`GdkWaylandDisplay`），开窗成功（400x300 → surface 452x375，即有装饰）。
  - shell 日志关键行：`Created surfaceless renderer without GPU`、`Added virtual monitor Meta-0`、`Using public X11 display :0`。
- **影响**：M2 架构可走「**完整 gnome-shell（面板/装饰/portal 依赖）× 虚拟显示器**」，不必自造合成器。
- **坑**：
  - tangyu **无 linger** 时 ssh 断开 → user manager 停 → unit 被杀。已 `sudo -S loginctl enable-linger tangyu`（可逆：`disable-linger`）。
  - tangyu 不在 `systemd-journal` 组，`journalctl --user` 读不到 → 用 `--property=StandardError=file:/tmp/screenlab-shell.err` 落文件。
  - 日志有 `Registering session with GDM ... 无可用的显示`（非阻塞，忽略）。

### E3 虚拟显示器参数 — 2026-09-21 15:08 · ✅ 参数拿到，定制性受限

- **方法**：Gtk 客户端读 `Gdk.Monitor`；单屏 / 双屏两种。
- **结果**：
  - 单屏：`model='MetaVirtualMonitor' manuf='MetaVendor' geom=1280x720+0+0 scale=1 refresh=60000 primary=False`
  - 双屏：`--virtual-monitor 1920x1080 --virtual-monitor 1280x720` → n=2，`1920x1080+0+0`、`1280x720+1920+0`，screen=`3200x1080`
  - **无 EDID**；所有虚拟显示器都 `primary=False`。
- **影响 / 待办**：
  - 多屏可造（对"像真人"有用）。
  - `MetaVirtualMonitor`/`MetaVendor`、`primary=False`、无 EDID 是**特征**；GNOME 40 的 `--virtual-monitor` 只给 `WxH@R`，**改名/设 primary/EDID 待确认能否做到**（可能需要 DisplayConfig ApplyMonitorsConfig 或换机制）。

### E4 a11y 读树 — 2026-09-21 15:12 · ✅ 读树证实

- **方法**：tangyu 会话起 `at-spi-dbus-bus.service`；起 GTK 客户端；用 GI `Atspi` 遍历桌面找 `CLICK-ME`，取 `extents`。
- **结果 ✅**：树可读，找到按钮，`extents x=26 y=46 w=400 h=300`（按钮填满窗口内容区），中心 `226,196`。
- **观察**：gnome-shell 自己的 a11y 树**巨大**（面板/概览/日历/顶栏全在里面），全树遍历明显慢 → 支持 A3「子树查询 + deadline」的必要性。
- **待验**：a11y 激活是否给网页 JS 留可探测痕迹（需 Chromium → 归 A4）。

### E5 输入注入 — 2026-09-21 15:2x · ✅ 部分（X11 证实；Wayland 待解）

- **核心结论**：**注入路径与客户端后端强耦合**。
  1. **Xwayland/X11 客户端** → `xdotool` XTEST **有效**（复现 slice2 的成功）：
     - 客户端 `GdkX11Display`，事件序列 `BTN-ENTER` → `BTN-PRESS 200,150` → `BTN-CLICKED` ✅
     - 注意：X11 客户端的 `Gdk.Monitor` 报 `model='Meta-0' manuf=None primary=True`（**比 Wayland 侧多一个 primary=True**）。
  2. **原生 Wayland 客户端** → XTEST **无效**（事件不进入 Wayland 输入流，`xdotool rc=0` 但客户端零事件）。
  3. **Mutter RemoteDesktop**（`org.gnome.Mutter.RemoteDesktop`）：
     - `CreateSession()` **无参数**；**session 对象只对创建它的那条 D-Bus 连接暴露接口** → 必须同一连接（Python/Gio）内完成；`gdbus call` 每次都换连接，故报 UnknownMethod。
     - 方法名：`NotifyPointerMotionRelative`（**不是** NotifyPointerMotion）、`NotifyPointerButton(i button, b state)`；另有 `NotifyPointerMotionAbsolute(s stream, d x, d y)`、`NotifyPointerAxis`、`NotifyKeyboardKeycode/Keysym`、`NotifyTouch*`。
     - `Start()` 成功、相对移动调用成功，但**原生 Wayland 客户端仍未收到事件** → 怀疑相对移动不 clamp（指针可能被移到屏外）或需要 absolute+stream。**待解**。
- **发现的环境坑**：
  - headless gnome-shell 的 Xwayland 同时在 `:0`、`:1`；**`:0` 会挂**（`xdotool` 超时），**用 `:1`**；需 `XAUTHORITY=/run/user/1001/.mutter-Xwaylandauth.*`。
  - 目录里另有历史 X socket（`X99`=旧 Xvfb、`X1024/X1025`=gdm 的 Xwayland）。
- **对设计的影响**：M2 若走「浏览器跑 X11/Xwayland」则注入简单（XTEST 已证）；若走「原生 Wayland 浏览器」则必须用 Mutter RemoteDesktop + ScreenCast stream（absolute），与 A1 同源。

### A1 ScreenCast 取帧 — 2026-09-21 15:22–15:45 · ✅ 取帧成功；「a11y↔像素同空间」对 **Wayland 客户端证伪**

- **VBox 3D 配置生效**（YZ 改配置并重启 VM）：`dmesg` 显示 `Capabilities: ... 3D, gbobject, dx ...`（之前是 `No 3D enabled`）；mutter 日志 `Created gbm renderer for '/dev/dri/renderD128'`。
- **取帧成功的关键：用 `RecordMonitor(connector)`，不要用 `RecordVirtual`**：
  - `RecordVirtual` → caps 只有 `BGRx 1×1, framerate 0/1` → 1×1 灰图（坏）。
  - `RecordMonitor('Meta-0')` → caps `BGRx 1920×1080, max-framerate 60/1` → **真实 PNG（1920×1080, 2.4MB）** ✅。
  - `gst-launch-1.0 pipewiresrc path=<node> num-buffers=1 ! videoconvert ! pngenc ! filesink`，node id 从 `wpctl status` 的 Video Streams 取（`pipewiresrc path=` 要 **node id**，不是 `output_N` 的 id）。
- **重大发现：Wayland 客户端的 AT-SPI `SCREEN` 坐标不是全局坐标**
  - 受控实验：清场、单客户端、1920×1080 单屏。窗口在帧里**居中于 (≈774,384)**，但 a11y 报 `extents (26,46) 400×300`，帧上 (226,196) 是**背景色**（40,40,40）。
  - 原因：**Wayland 客户端不知道自己窗口的全局位置**，AT-SPI 给的是"窗口局部坐标 + 装饰边距"，无法直接当像素坐标。
  - 对比：**X11(Xwayland) 客户端**给的是全局坐标（此前 `e5b` 里 XTEST 按 a11y bounds 点击**命中**可证）。
- **可取窗口全局位置的接口被封**：`org.gnome.Shell.Introspect.GetWindows` 存在但返回 `AccessDenied`。
- **其它环境事实**：
  - `ScreenCast.Stream.Start` 不存在（流随 `Session.Start` 自动开始）。
  - mutter 对 `vmwgfx` **硬编码禁用 DMA buffer 共享**（`Disabling DMA buffer screen sharing for driver 'vmwgfx'`），`MUTTER_DEBUG_USE_KMS_MODIFIERS=1` 也绕不过；但**不影响 RecordMonitor 走 CPU 路径出帧**。
  - `MUTTER_DEBUG_FORCE_EGL_STREAM=1` 会直接起不来（`Missing required EGLDevice extension`）。
  - **关闭 ScreenCast session 会崩掉整个 headless shell**（可复现）→ 实验间要重启 shell。
  - headless shell 的 Xwayland 在 `:0`/`:1` 间飘；**`:0` 常挂**，`xdotool` 要么超时要么报 `No protocol specified`。
- **对设计的影响**：
  1. 像素兜底在本 VM **可行**（RecordMonitor）——不卡在 3D 上了。
  2. "a11y bounds 直接映射像素坐标"这条**只在 X11 客户端成立**；用 Wayland 客户端必须另找窗口全局位置（或干脆让被测应用跑 X11）。
  3. 这条直接影响 A3（按 a11y 重解析 bounds 点击）与"a11y 优先 + 像素兜底"的坐标对齐设计。

### A6 无 seat 拿 GPU — 2026-09-21 15:20 · ✅ 机制证实（真 3D 待 E1）

- **方法**：`sudo -S setfacl -m u:tangyu:rw /dev/dri/card0 < key` → 重启 headless `screenlab-shell` → 看 `/tmp/screenlab-shell.err`。
- **结果 ✅**：日志从 `Created surfaceless renderer without GPU` 变为
  `Adding device '/dev/dri/renderD128' (from '/dev/dri/card0', vmwgfx)` →
  **`Created gbm renderer for '/dev/dri/renderD128'`**；`Boot VGA GPU ... selected as primary`。
- **关键结论**：即使 `renderD128` 是 0666，**mutter 仍需 `card0` 才能发现 GPU** → 无 seat 拿 GPU 的钥匙是 **`card0` 的 ACL/组权限**。
- **限制**：本 VM 无 3D，`falling back to CPU copy path` + `Disabling DMA buffer screen sharing`，所以只拿到 gbm renderer，**验不到真 3D 渲染**。
- **安全提示**：给 `card0` 读权限 ≈ 可申请 DRM master（与"不抢显示"是两回事，但要有意识）。

### E5 补充：Mutter RemoteDesktop 注入报错 — 2026-09-21 15:14

- RD 注入后 shell 日志出现：`Unknown/invalid virtual device button 0x1 pressed`。
- → RD 的**虚拟指针设备没挂 stream**，按钮被丢弃；Wayland 原生注入必须走 **`NotifyPointerMotionAbsolute(stream, x, y)`**，stream 来自 ScreenCast。与 A1 同源。

### 持久改动登记

> ❌ 表中 **linger / `screenlab-shell` user unit / tangyu gsettings** 等条目**随自持·自启作废**（见 `handoff-screen-17.md` §十一·11.3），**待清理**——"回滚"列即清理命令。

| 改动 | 回滚 |
|---|---|
| **VBox 主机侧：开启 3D 加速**（YZ 改，已重启 VM 生效） | VBox 设置里关回 |
| `loginctl enable-linger tangyu` | `sudo -S loginctl disable-linger tangyu < ~/.secrets/centos.key` |
| 临时 ACL `setfacl -m u:tangyu:rw /dev/dri/card0` | `sudo -S setfacl -x u:tangyu /dev/dri/card0 < key`（重启即失效） |
| 运行中 tangyu user unit `screenlab-shell`（gnome-shell headless） | `systemctl --user stop screenlab-shell` |
| tangyu 会话 `idle-delay=0` + `screensaver lock-enabled=false`（否则 ScreenCast 被 inhibited） | `gsettings set ... idle-delay 300` / `lock-enabled true` |
| `/tmp/screenlab-shell.err` 等临时文件 | 删 |

### 脚本索引（本目录 `screen-lab-verify/`）

| 文件 | 用途 |
|---|---|
| `e2-client.py` | Gtk3 客户端，打印显示器信息、CLICK-ME 按钮、事件探针、`--blink` |
| `e4-atspi.py` | AT-SPI 遍历找 `CLICK-ME`，输出 `CENTER x y` |
| `e4.sh` / `e4b.sh` / `e5.sh` / `e5b.sh` | 注入实验（X11 XTEST / Wayland RD） |
| `e5-rd-inject.py` | Mutter RemoteDesktop 注入（同一 D-Bus 连接） |
| `a1.sh`–`a1i.sh`、`screencast-hold.py` | ScreenCast 取帧实验 |
| `p0-screencast.py`、`p0-setup.sh` | 旧 Phase 0 脚本 |
| `a4-page.html` / `a4-serve.py` | A4 可控测试页 + 命中计数服务 |
| `a4-atspi.py` | A4 扫描 chrome a11y 树并 `doAction` |
| `a4-run.sh` / `a4-alice*.sh` | A4 启动/扫描（tangyu / alice 会话） |

### A4 Chromium a11y 覆盖率 —— 2026-09-21 17:48，18:02 修正 · ✅ 跑通

- **"chrome 必须有 seat"的初稿结论已推翻（有误）。** 真正原因：**chrome 启动时去问 Secret Service（gnome-keyring），密钥库锁着/不应答 → 所有 http(s) 请求一直 pending**（本地文件正常、无报错、`curl` 同机正常）。属已知症状，见 Arch 论坛 `tid=312408`。
  - **与 seat / logind 无关**：tangyu 的**无 seat headless 会话**里，给 chrome 加 **`--password-store=basic`** 后即可正常加载页面（实测 `requests: /`、`/favicon.ico`）。
  - tangyu 会话总线上**有** `org.freedesktop.secrets` / `org.gnome.keyring`（进程也在），但**不应答** → 所以表现为"挂着"而非报错。
  - **M2 结论：headless / 无 seat 可行**，只需 `--password-store=basic`（或修好 keyring）。
  - （alice=正常桌面会话里 chrome 也正常，但那只是"keyring 恰好可用"，不是 seat 的功劳。）
- **方法**：headless 会话内起 chrome（`--force-renderer-accessibility --password-store=basic`），打开可控页（14 个已知控件，激活时 `fetch('/hit?c=NAME')` 回执）；`org.a11y.Status.IsEnabled=true`；AT-SPI 遍历 `Google Chrome` 树并 `doAction`，用回执判真触发。
  - **重要：a11y 树是渐进建立的，必须等稳定再扫。** 本次连扫 3 遍均为 **19 个 A4 节点**（chrome 全树 382 节点）才算稳定；早扫会漏（这就是初稿"ARIA 不在树"的假象来源）。
- **结果（3 遍一致，可复现）**：

| 控件 | 树中 role | action | `doAction` 真触发 |
|---|---|---|---|
| button | push button | `press` | ✅ |
| a(href) | link | `jump` | ✅ |
| checkbox | check box | `check` | ✅ |
| radio | radio button | `check` | ✅ |
| submit | push button | `press` | ✅ |
| **div role=button** | push button | `press` | ✅ |
| span onclick | static | `clickAncestor` | ✅ |
| canvas onclick | static | `clickAncestor` | ✅ |
| img onclick | image | `click` | ✅ |
| details/summary | toggle button | `press` | 未埋回执，未验 |
| text | entry | `activate` | ❌（需 `setText`） |
| range | slider | `doDefault`/increment/decrement | ❌（需 `setValue`） |
| select | combo box | `open` | ❌（需展开 + 选项） |
| textarea | entry | `activate` | ❌（需 `setText`） |

- **结论（修正）**：
  1. 办法二覆盖**比初判宽**：原生控件 + **ARIA `div role=button`** + **带 onclick 的 span/canvas（走 `clickAncestor`）** + **img（`click`）**，都能被 `doAction` 真正驱动页面 JS。
  2. **值类控件**（text/range/select/textarea）在树里，但 `doAction` 不产生值变化，需 `setText`/`setValue`。
  3. 初稿"ARIA/自绘不在树"是**测量假象**（树未建全就扫）——**结论：a11y 方法可行，但扫描必须等到树稳定**。
- **caveat**：测试页自造；真实站点（React SPA）覆盖率待验；`doAction` 取 prefer 命中项（未必最优 action）；`--force-renderer-accessibility` 对树完整度的影响未系统验证。
- **待办**：真实站点复测；"懒开"（不带强制开关）的可靠性；E4 的 a11y 痕迹。

### A4 余下：真实站点 + 懒开 —— 2026-09-21 19:06–19:08 · ✅ 真实站点跑通；❌ 懒开不生效

- **环境**：`screenlab-shell` 重启后（PID 9807，1920×1080）；card0 ACL 重设；**chrome 走原生 Wayland 后端**。
- **新坑（重要）**：headless 会话里 chrome **默认选 X11 后端**，但 Xwayland 的 auth 对不上（`Invalid MIT-MAGIC-COOKIE-1 key` → `Missing X server or $DISPLAY`）→ 必须显式 **`--ozone-platform=wayland`**（比配 XAUTHORITY 稳）。
- **真实站点（https://react.dev/，React SPA）· 带 `--force-renderer-accessibility`**：
  - 树 **1376 节点 / 227 个带 action 的交互节点**（2.1s 扫完）。
  - role 分布：`static 757, section 136, panel 112, push button 106, link 71, heading 53, notification 47, image 37, paragraph 17, entry 3, slider 3, combo box 3, check box 1, …, document web 1, article 1`。
  - 覆盖**浏览器 UI（标签页/地址栏/翻译/最大化…）+ 网页内容（link/heading/button/…）**都在树里、都带 action。→ **真实站点覆盖率与自造页结论一致，办法二可用于真实 SPA**。
- **懒开（同 URL、不带 `--force-renderer-accessibility`，AT-SPI `IsEnabled=true`）**：
  - 树**只有 1 个节点**（`frame`），连扫 3 遍一致；chrome 已注册进 AT-SPI（`apps` 里有 `Google Chrome`）但**不建树**。
  - → **本设置下"懒开"不生效，`--force-renderer-accessibility` 目前必需**。这与 F1（flag 本身可能是可探测特征）形成张力：要么带 flag 冒指纹风险，要么找别的触发方式（待查：`--enable-features`/pref/由客户端触发）。
- **脚本**：`a4-real.sh`（headless+wayland 启动，`LAZY=1` 切无 flag）、`a4-real-probe.py`（真实站点树统计 + role 直方图 + action 采样）。

### A1 复核 + A2 流复用 —— 2026-09-21 19:14–19:17 · ✅ 取帧复核通；❌ A2「同流多消费者」证伪

- **A1 复核（shell 重启后）**：`RecordMonitor('Meta-0')` 恢复出帧，**1920×1080 PNG**（5.3MB），分辨率未变。
- **新坑（阻塞过 A1/A2）**：`ScreenCast.CreateSession` 报 **`AccessDenied: Session creation inhibited`**——真因是 headless shell **自己进了屏保/锁定**（`org.gnome.ScreenSaver.GetActive=true`，`idle-delay=300`、`lock-enabled=true`）。
  - 修：`gsettings set org.gnome.desktop.session idle-delay 0`、`gsettings set org.gnome.desktop.screensaver lock-enabled false`、`ScreenSaver.SetActive false`。
  - → **记录为持久改动**（见下表）；headless 会话必须先关空闲锁定，否则 ScreenCast 一律被拒。
- **A2（同一路流再挂第二消费者）· ❌ 证伪**：
  - 对照：单消费者 C → ✅ 1920×1080。
  - 并发：A 持续持有该流时，B（`pipewiresrc path=<同一 node>`）**超时 0 帧**（rc=124）；A 一出，再取即成功。
  - → **mutter 导出的 ScreenCast 流是单消费者（独占）**，不能同时被两路 `pipewiresrc` 拉。
  - 但 A2 命题的另一半**成立**：**不新开显示、不改分辨率**（单消费者与 A 都是 1920×1080）。
- **对"给人看"设计的修正**（对齐第四节"人要看才给屏"）：
  - 不能靠"同流多消费者"。可行解是 **agent 单消费者 + 自己 fan-out 给观看端**，或 **切换持有者**（agent 让出/共享）。
  - 这反而和"按需给屏"一致：默认 agent 持有流（也够抓帧），人要看时由 agent 转发，而非再挂一路。
- **脚本**：`a2.sh`、`a2b.sh`（单消费者对照 / 并发持有竞争者）、`screencast-mon.py`（持 session 拿 node id）。

### P1 值类控件（a11y）—— 2026-09-21 20:36 · range/select ✅；text/textarea ❌

- **环境**：本地可控页（`a4-page.html`，14 控件）+ chrome（headless + `--ozone-platform=wayland` + `--force-renderer-accessibility`），回执服务 8765。
- **树里找到 4 个**：`A4-TEXT`(entry)、`A4-RANGE`(slider)、`A4-SELECT`(combo box)、`A4-TEXTAREA`(entry)。
- **range ✅**：`Value.set_current_value` 成功，页面 **`onchange` 真触发**（hits: `RANGE`）。接口：`value=yes`。
- **select ✅**：combo box action `open` → 展开后出现 `menu item`（one/two），其 action 为 **`select`** → `do_action('select')` **真触发页面 `onchange`**（hits: `SELECT` ×2）。→ **选择类控件可全 a11y 驱动**。
- **text / textarea ❌**：chrome 的 entry **没有 `editable_text` 接口**（`get_editable_text_iface`=None）；`action=activate` 不改值。
  - 改用 **`Atspi.generate_keyboard_event`**（先 `component.grab_focus()`=True，键 h/i/! 均返回 True）→ **页面无任何反应**（无 `TEXT` hit）→ **AT-SPI 合成键盘事件不生效**。
  - → **文本输入是 a11y 路径的唯一缺口**：需真键盘注入（= P2/E5），或另找 chrome `EditableText` 的触发条件。
- **接口清单（本页 chrome）**：entry → `text=yes, editable=no, value=no, action=yes`；slider → `value=yes`；combo box → `action=yes`。
- **坑**：`/tmp/a4-hits.log`/`a4-requests.log` 曾被 **alice 占属主**，服务写不进（`rm` 也不许）→ 改用 **`/tmp/a4t-*.log` + `a4-serve-t.py`**。
- **脚本**：`a4-values.sh`（启动+回执）、`a4-values.py`（接口探测 + 值设置）、`a4-values2.py`（键盘事件 + select 展开选子项）、`a4-serve-t.py`。

### 调研：文本输入的根因与可选路线 —— 2026-09-21 20:40

- **根因（网上佐证）**：**Chromium 的 AT-SPI 映射里，entry 实现 `Text` 但〔不〕实现 `EditableText`** → `setTextContents` 无从调用（正是我们实测的 `editable_text=no`）。
  - 佐证：greentic-desktop PR#29「Entries implement Text but not EditableText → typing needs keyboard synthesis (X11/XTest)」；xa11y 文档：accesskit 桥只暴露 `Value.SetCurrentValue`，`EditableText.SetTextContents` 被 `UnknownInterface` 拒绝。
  - → **纯 a11y 无法做文本输入，必须合成键盘事件**。
- **键盘合成路线（GNOME/Wayland）**：

| 方式 | 原理 | GNOME 支持 | 备注 |
|---|---|---|---|
| `xdotool`/XTEST | X11 注入 | 仅 **Xwayland 客户端** | 本机 E5 **已验证** |
| `wtype` | `zwp_virtual_keyboard_v1` | ❌ **Mutter 不支持** | 直接死 |
| `ydotool` | `/dev/uinput`（内核） | ✅ 与合成器无关 | 需 root daemon `ydotoold` + uinput 权限 |
| 门户/Mutter `RemoteDesktop.NotifyKeyboardKeycode` | 合成器侧 | ✅ | 新版建立 EIS(libei) 后 `Notify*` 会报错 |
| libei（`eitype`/`wdotool`） | EI | 需较新 GNOME（45+） | 本机 GNOME 40 用不上 |
| 剪贴板 + 粘贴 | — | — | 仍需一次 Ctrl+V 注入，不能独立解决 |

- **已知 mutter bug**：GNOME ≤40 "remote input events **需物理键盘每 boot 至少连过一次**"（mutter #1671）；MR !1688 在 **GNOME 40 修复**（本机 40.10，应已修）。
- **结论/建议**：两条路都可行，倾向 **(a) 被测浏览器跑 Xwayland**——XTEST 键鼠注入已验证，且 X11 客户端 a11y 给**全局坐标**（A1）→ **一次解掉"文本输入 + 坐标"两个缺口**；代价是 XAUTHORITY/DISPLAY 探测（已知坑）+ X11/Wayland 指纹差异（归 F1）。
  - (b) 原生 Wayland 则需合成器侧键盘注入（`NotifyKeyboardKeycode` 或 ydotool），指针 absolute 仍需 stream。
  - 参考：<https://gitlab.gnome.org/GNOME/mutter/-/work_items/1671>、<https://github.com/greenticai/greentic-desktop/pull/29>、<https://xa11y.dev/explanation/accessibility-quirks/>、<https://github.com/atx/wtype/issues/45>

### 复核：文本编辑是 **Chromium 特有**，非 AT-SPI 缺陷 —— 2026-09-21 20:45 · ✅ 对照实验

- **直接证据（同一 a11y 栈、同一时刻）**：

| 对象 | `get_editable_text_iface` | `Atspi.EditableText.set_text_contents` | `Text.get_text` | 结果 |
|---|---|---|---|---|
| **Chrome `<input type=text>`（A4-TEXT）** | **None** | **返回 False** | `''` | 文本未变 ❌ |
| **GTK `GtkEntry`（EDIT-ME，对照）** | **OBJ** | **返回 True** | 写入后 → `'GTK-EDIT'` | 真的被改写 ✅ |

- **结论**：**AT-SPI 的 `EditableText` 通道本身可用**（GTK 控件实测写成功）；**是 Chromium 不暴露可用的 `EditableText`**（`get_editable_text_iface=None` + `set_text_contents=False`，两法一致）。`Text` 只读接口在 chrome 上是好的（textarea 读出页面内容 `seed`）。
  - → 网上两处旁证成立，且现在是**本机一手实测**。
- **对 M2 的含义**：目标若是 **Chrome/Electron**（正是 M2 的场景），**文本输入必须靠键盘合成**；若是 GTK 等原生控件，a11y 直接能写。→ 进一步支持"**被测浏览器跑 Xwayland + XTEST**"这条低成本路线。
- **脚本**：`a4-iface-probe.py`、`a4-iface2.py`（chrome 接口探测 + D-Bus）、`gtk-entry.py` + `gtk-run.sh`（GTK 对照）。

### B1 后端默认：Xwayland(X11) 路线验证 —— 2026-09-21 21:12 · ✅ 三项全过

- **目的**：证实/证伪"被测浏览器跑 Xwayland + XTEST"这条建议（它同时决定 P2 文本输入与 E5 坐标）。
- **方法**：headless 会话里 chrome **不加** `--ozone-platform=wayland`，配好 `DISPLAY/XAUTHORITY` 走 X11；脚本 `a4-x11.sh` + `a4-extents.py` + `a4-keytest.py` + `a4-xtest.sh`。
- **结果**：
  1. **X11 后端起得来**：Xwayland 可达 `DISPLAY=:2`（auth `.mutter-Xwaylandauth.YG87V3`）→ 1920×1080；chrome 12 进程，页面正常（仅无关 vaapi 告警）。
  2. **a11y 树完整**：382 节点 / 19 个 A4 节点，与原生 Wayland 一致；`doAction` 命中 BUTTON/LINK/CHECK/RADIO/SUBMIT/DIVROLE/SPANCLICK/CANVAS/IMG。
  3. **坐标是全局坐标（关键）**：`xdotool windowmove` 把窗口 (10,42)→(300,200)（Δ+290,+158），a11y extents **同步平移同一 Δ**（A4-BUTTON 46→336、282→440）→ **X11 客户端 a11y bounds 直接就是屏幕像素坐标**。
  4. **XTEST 键盘注入命中**：a11y `grab_focus` A4-TEXT → `xdotool mousemove+click` 中心 → `xdotool type 'X11KEY'` → 页面 `oninput` **6 次 TEXT hit**（逐字触发）→ **文本输入打通**。
- **结论**：**"被测浏览器跑 Xwayland + XTEST" 三项判据全过**——一次解决"文本输入 + 全局坐标"两个缺口；且不占用 ScreenCast 流，与 A1/A2 不冲突。
- **反检测备注（未验，归 F1）**：Chrome 在 Linux 默认 ozone 后端即 X11；原生 Wayland 才是少数派配置。
- **坑（重要）**：headless 会话里 Xwayland 有多个实例：`:2/:3` 可通、`:4/:5` 坏、`:0/:1` 是 alice 的（auth 不匹配 → `Invalid MIT-MAGIC-COOKIE-1 key`）。**这正是当初被迫上 `--ozone-platform=wayland` 的原因**——不是"没有 X"，是没探对 display。
- **脚本**：`a4-x11.sh`、`a4-extents.py`、`a4-keytest.py`、`a4-xtest.sh`。

### P1·A3 act element（按 id 重解析 + 子树 + deadline）—— 2026-09-21 21:22 · ✅ 三项全过

- **环境**：chrome X11（`DISPLAY=:2`）+ a4 测试页；脚本 `p1-a3.py` / `p1-a3.sh` / `p1-start.sh`。
- **结果**：
  - **重解析 ✅**：窗口 (10,42)→(250,120)（Δ+240,+78），a11y 重取 `A4-BUTTON` extents (46,282)→(286,360)（**同步同一 Δ**），按新中心 XTEST 点击 → **两次点击都命中 BUTTON**。
  - **子树 vs 全树 ✅**：全桌面遍历 **1760 节点 / 2545ms**；chrome 子树 **382 节点 / 573ms**（≈4.4×；真实站点差距更大）。
  - **deadline 回退 ✅**：`200ms` → 走 105–208 节点后 `aborted=True`；`20ms` → 13–22 节点即中止。→ **200ms 只能覆盖全树一小部分，必须回退**（点查询 / 缓存路径 / 像素）。
- **设计含义**：全树遍历不可用（>2s）；≈**1.5ms/节点**（DBus 往返）→ 需"**按 id 缓存路径** + point query + per-op 预算 + 回退"，而非每次全扫。

### P1·分发验证（1 服务 fan-out N 路）—— 2026-09-21 21:22 · ✅ 3/3

- **背景**：A2 已证 mutter ScreenCast 流**单消费者独占**。
- **方法**：一个进程持 ScreenCast session（`RecordMonitor`），**只有一个 `pipewiresrc`**（单消费者），经 GStreamer `tee` 在**进程内 fan-out 给 N=3 个 appsink 订阅者**，统计各路收帧。
- **结果**：**3/3 订阅者都拿到帧**，caps 一致（`BGRx 1920×1080`、`max-framerate 60/1`）、同一 PTS。
  - 注：6s 内每路仅 **1 帧**——ScreenCast 只在**画面有变化**时出帧（静止屏无新帧），非 fan-out 问题。
- **结论**：**"能分发"从推断变事实**：mutter 流保持单消费者，服务内部 fan-out 给 N 路可行 → **模式 A 调试口 / 场景3 的底座成立**。
- **坑**：**D-Bus 信号（`PipeWireStreamAdded`）必须迭代 `GLib.MainContext` 才送达**（纯 `time.sleep` 轮询收不到 → `NODE=None`）；已修（pump main context + `wpctl` 兜底）。
- **脚本**：`p1-fanout.py`、`p1-fanout.sh`。

### E4/F1 反检测（本机部分）—— 2026-09-21 21:27 · ✅ 静态指纹无差异；性能侧信道未量化

- **目的**：验证 `handoff-screen-11.md` §六12 的推理——`--force-renderer-accessibility`（及 a11y 激活）是否留**页面可探测痕迹**。
- **方法**：三配置各起一次 chrome X11 打开指纹页（`e4-fp.html` + `e4-serve.py`），采 JS 可见指纹 + DOM/rAF 基准：
  - **A**：不带 flag（a11y 关）
  - **B**：带 flag（a11y 开，无客户端）
  - **C**：带 flag + AT-SPI 客户端并行接入（`e4-atspi.py`）
- **结果**：
  - **静态字段三配置逐字段完全一致**：`ua`/`uaData`/`webdriver=false`/platform/hc/dm/tz/langs/screen(1920×1080, avail 1048, cd24, dpr1)/`outer[1200,900]`/`inner[1168,770]`/`screenXY[10,42]`/maxTouch/webgl(null)。
  - → **flag 与 a11y 激活不改变任何页面可见静态指纹**（与 §六12 一致）："flag 必需"的张力在**页面可见面**上不成立。
  - **性能侧信道存在但噪声大**：`benchDomMs` A=42.7 / B=25.0 / C=57.8，rAF max 104–353ms —— **非单调、VM 噪声主导，未能量化**；要定论须多轮中位数。
- **家具层观察（本机）**：
  - ✅ X11+WM 下 `outer`/`screenXY` 是**真实值**（非 headless 的 `[0,0]`）。
  - ❌ **`webgl=null`**：本 VM 无 3D，且此次未带 `--disable-gpu` 时 GPU 进程没起来（连 SwiftShader 都没露）→ **真家具缺口，归 E1/A12（换 3D 机）**。
- **结论**：**F1 的"flag 可指纹"担忧在本机页面可测面上被证伪**；剩余风险集中在**家具层（真 GPU/WebGL）**，不在 a11y。
- **脚本**：`e4-fp.html`、`e4-serve.py`、`e4-fp.sh`。

### E6 行为 humanization —— 2026-09-21 21:29 · ✅ 可行（初步）

- **目的**：验证"注入不是瞬移/等间隔"这一层可行（判据：有轨迹、时序自然、页面逻辑正常）。
- **方法**：`e6-page.html` 记录 `mousemove` 序列并回执；`e6-move.py` 用 smoothstep 缓动 + 抖动 + **末端过冲回正**，经 XTEST 逐点注入并点击目标（目标坐标由 a11y 取）；`e6-serve.py` 收轨迹。
- **结果**：
  - **有轨迹 ✅**：页面收到 **73 个 `mousemove` 点**（非瞬移），path_len=544.5。
  - **时序自然 ✅（初步）**：注入侧步进间隔 27–52ms，页面侧 dt 18–298ms、**非等间隔**；捕捉到**末端过冲回正**（[993,637]→[980,629]）。
  - **页面逻辑正常 ✅**：点击命中 `#t`（回执 `kind=click`），end=(980,629) 正是目标中心。
  - 附：a11y 屏幕中心 (1006,821) 与页面 client (980,629) 差 **(26,192)=窗口内容区原点偏移**，稳定一致。
- **局限**：轨迹是"一阶缓动 + 抖动 + 过冲"的初步模型；未含停顿/思考时间/多点曲率 —— 属**设计细化**，非能力问题。
- **脚本**：`e6-page.html`、`e6-serve.py`、`e6-move.py`、`e6.sh`。

> ❌ **作废（2026-09-21 23:2x）**：以下 **A11 两段 + `:2` 隐患定位段整体作废**（"自持 / 自启"需求已撤）。**B2 段只保留"X11 上起 chrome"，其探活 / `:3` 相关作废**。保留为历史证据，**勿据此复工**。详见 `handoff-screen-17.md` §十一·11.3。

### A11 user unit 集群 / 自启收尾 —— 2026-09-21 21:34 · ✅ 通过（无需 reboot）

- **目的**：把"headless 桌面"从临时 `systemd-run` 变成**随用户会话自动起**的持久 user unit，并确认不与旧 system 服务冲突。
- **做法**：写 `~/.config/systemd/user/screenlab-shell.service`（`Type=simple`，`gnome-shell --headless --virtual-monitor 1920x1080 --wayland-display=screenlab-0`，`StandardError=append:/tmp/screenlab-shell.err`，`Restart=on-failure`，`WantedBy=default.target`）→ `daemon-reload` + 停旧 transient + `enable` + `start`。
- **结果**：
  - unit `active` + `enabled`；`default.target Wants=screenlab-shell.service`。
  - **自启验证（不用 reboot）**：`loginctl terminate-user tangyu`（**zhengyp sudo**，rc=0）→ 用户管理器随 `Linger=yes` **自动重拉** → 新 PID **17107**，socket `screenlab-0` + Xwayland `:2/:3` 重建，新 logind 会话 100（**无 seat**）→ **无人介入自动就绪**。
  - **旧 system 服务**：`screenlab.service` / `screenlab-xvfb.service` 存在且 `active + enabled`，占 `/run/screen/screen.sock`；**与新链不冲突**（新链只用 `/run/user/1001/screenlab-0` + Xwayland，不碰 `/run/screen`）。**未动它们**（是否退役待 YZ）。
- **坑**：误在 **tangyu 身份**下 `sudo`（tangyu 非 sudoer）→ 报密码错误；正确做法是用 **zhengyp 的 sudo**（`sudo -S -k ... < ~/.secrets/centos.key`）。
- **脚本**：`a11-setup.sh`；unit 文件 `~/.config/systemd/user/screenlab-shell.service`。
- **注**：真正 **reboot** 后的自持（A8）仍需 YZ 验；本条只验"用户管理器级自启"。

### A11 补充：自启后 **`:2`（public）不可达** —— 2026-09-21 21:45 · ⚠️ 隐患（未解）

- **现象**：`loginctl terminate-user tangyu` 自启、以及其后 `systemctl --user restart screenlab-shell`（MainPID 20907，21:42:38）**都**出现：
  - `/run/user/1001/.mutter-Xwaylandauth.*` 只剩**一个**文件（如 `AB2FW3`），且**只对 `:3` 有效**；
  - `DISPLAY=:2`（mutter 自称的 **public** 显示）`xdotool getdisplaygeometry` **返回空 = 连不上**；`DISPLAY=:3` 正常（1920×1080）。
  - shell 日志明确：`Using public X11 display :2, (using :3 for managed services)`。
- **对照**：`terminate-user` **之前**（19:0x–21:0x）有**两个** auth 文件，`:2`/`:3` 都能连（B1/P1/E6 都跑在 `:2` 上、拿到 382 节点）。
- **影响**：X11 客户端被挤到 `:3`（**managed services** 显示），而 chrome 在该显示上**起来后自己退出**（`pid count=0`）→ a11y 无页面节点。→ **M2 的"浏览器跑 X11"路径在自启后不可用**。
- **待查**：① reboot（A8）后是否恢复两个 auth；② `:2` 的 auth 生成条件（是否 lazy、需首个客户端触发）；③ 是否 mutter 把 public auth 放在了别处。
- **规避（临时）**：改用**探活优先 public 显示**（解析日志 `Using public X11 display :N`）——但若 `:2` 真的连不上，规避无效，得先解决根因。

### B2 X11 启动器落地 —— 2026-09-21 21:45 · 🔶 代码就位，**验证未收口**

- **交付**（源码 `screen-lab-verify/`，已装 tangyu `~/screenlab/`，均 +x）：
  - `screenlab-x11.sh`：`screenlab_x11_probe()` —— 依序试 `:2 :3 :1 :0` × auth 文件（新→旧），`xdotool getdisplaygeometry` 探活，导出 `DISPLAY/XAUTHORITY/WAYLAND_DISPLAY`，可选写 env 文件。
  - `screenlab-chrome.sh`：source 探活后 `exec google-chrome --no-sandbox --disable-gpu --disable-dev-shm-usage --no-first-run --no-default-browser-check --password-store=basic --user-data-dir=$PROFILE --window-size=1200,900 $EXTRA <url>`（`EXTRA` 默认 `--force-renderer-accessibility`；**故意不带 `--ozone-platform=wayland`**）。
  - `b2.sh` / `b2-diag.sh`：验证 / 诊断。
- **通的部分**：探活可跑、chrome 能起（12+ 进程）、页面确实被请求（server 收到 `/`）。
- **卡的部分**：探活落到 **`:3`（managed services）** → chrome **起来后退出**（诊断 `pid count=0`）→ a11y 只 236 节点、无 A4 节点。
  - **根因 = A11 的 `:2` 不可达**（见上）；之前 B1/P1/E6 都在 `:2` 上、稳定 382 节点。
  - **排除**：`382 vs 236` **不是** flag 问题。
- **修法（未实施）**：探活**优先 public 显示**（解析 shell 日志），再重验（chrome 存活 + 382 节点 + doAction 命中）。
- **坑（重要，新增）**：
  - **`/tmp` 下脚本不能"原地 exec"**（`setsid /tmp/xxx.sh` → `权限不够`；SELinux/noexec）→ 必须装到家目录、或 `bash <file>`。
  - `pkill -f` / `pgrep -f` **自伤**：连 **ssh 的整条命令行**也算（`pgrep -f "[b]2.sh"` 会匹配到自己命令行里的 `bash /tmp/b2.sh` → 死循环）。**用 `[x]` 写法、`-x`、PID，或放进脚本文件**。
  - **D-Bus 信号需迭代 `GLib.MainContext`**（`PipeWireStreamAdded` 纯 sleep 收不到）。
  - **脚本**：`screenlab-x11.sh`、`screenlab-chrome.sh`、`b2.sh`、`b2-diag.sh`。

### A11 隐患定位（第一轮证据）—— 2026-09-21 22:40–22:55 · 🔶 部分定位（未收口）

> 只读排查：auth 文件 / `xauth list` / `fuser` + `/proc/<pid>/fd` / `/proc/net/unix` / shell 日志。**未做任何修复动作。**

- **复核现象**：带唯一 auth 文件时，`DISPLAY=:3` → `1920 1080` 正常；`DISPLAY=:2` → `xdotool getdisplaygeometry` **不返回（连接挂住）**，不是"拒绝"。
- **实物状态**：
  - `/run/user/1001/.mutter-Xwaylandauth.*` **只有 1 个**（`AB2FW3`）；`xauth list` 里 cookie 绑定 host = **`10.0.2.15`**，正是本机 `hostname` → **认证不匹配不是原因**。
  - **只有 1 个 Xwayland 进程**（PID 21114，cmdline `:2`，`-auth AB2FW3`），其 `-listenfd 4 -listenfd 5` 对应 **同时持有 `/tmp/.X11-unix/X2` 与 `X3`**；`X3` 另被 gnome-shell 自身持有。
  - **socket 都生成了**（X2/X3 均 21:42 新建），进程也在 → 不是"生成不了 `:2/:3`"，是 **public 显示半初始化**。
- **关键日志**（两次启动各 1 次，均在启动后 ~2.5 分钟）：
  ```
  Error starting X11 services: Systemd job completed with status "dependency"
  mutter-WARNING: Failed to initialize X11 display: Unknown error
  ```
  - 时序（21:34:02 起 → 21:36:47 报错）= 启动时只**登记显示号 + 建 socket**，Xwayland **后来才起**（疑似**按需 / systemd 激活**），起时依赖失败 → 半初始化。
- **推断（未证）**：mutter/gnome-shell 经 **systemd** 启动 Xwayland，不是启动即起。可疑 dependency：同批日志中 `xdg-desktop-portal-gnome.service` / `xdg-desktop-portal-gtk.service` 均 **failed**。对应 unit 在 `/usr/lib/systemd/user/` 下**搜不到静态文件** → 疑似运行时创建的临时 unit，**名字未确认**。
- **与"已跑通"的对照**：B1/P1/E6 跑通的是**手工 `systemd-run --user` 临时起**；失败的是 `enable` 的**持久 unit**。两条都经 systemd → **差别在启动时机/初始状态，不在 systemd**。推断"按需/延后起可绕开"（未实测）。
- **待收口**：① 那个 systemd job 的真实 unit 名 + dependency 项；② `reboot`（=A8）后是否恢复两个 auth / `:2` 可用；③ 用"起前清场 + 按需起"复验能否稳定拿 382 节点。
- **残留**：排查中在 `:2` 上挂住的一条 `xdotool`（root 起）**可能未回收**。
