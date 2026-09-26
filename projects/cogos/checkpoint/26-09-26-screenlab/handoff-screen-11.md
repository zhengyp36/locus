# handoff｜目标重置：Linux 上"agent = 一个普通用户"，a11y 优先 · 2026-09-20 #11

> **新会话任务**：本会话后半段由 YZ **重置了目标**（见 §二，最重要）。新会话应从"**Linux + 非无头 + 真人使用场景**"重新设计，而不是在现有 `screenlab` 上打补丁。
> **交接语**：读本文件即可开会话；网络坑的结论细节在 `handoff-screen-10.md`；P4 Windows 落码见 `handoff-screen-09.md`。
> **前序**：`handoff-screen-10.md` → 本文件。

## 一、本会话做了什么

1. **网络**：定位"大图慢"根因（VBox 7.2.x 桥接收包 bug），并**实测 Tailscale 可绕行**（详见 §三）；已标注进 locus：`entries/2026-09-20-cogos-screen-net-vbox-bridge.md`。
2. **Windows 现状盘点**：查了 Surface 的真实会话/账户/安装状态（§四）。
3. **一大段概念推演**（会话 vs 桌面 vs 显卡 vs 进程 vs 显示服务器；Windows/Linux 对比；a11y；headless 识别）。
4. **YZ 重置目标**（§二）+ 收敛出一版 Linux 设计骨架（§五）。
5. 顺带：一次仓库外实验（headless Chrome 指纹），结论见 §六。

**未改任何代码。** 工作区仅 `screenlab/install/install.ps1` 未提交（端口策略，09-20 #10 就欠着）。

## 二、目标重置（YZ 拍定，最重要）

### 原话与含义

> "给 agent 真人一样的操作电脑，**不是像真人，就是和真人操作一样**。给真人一个账号，它能登陆怎么用，那么 agent 也这么用。"

**含义**：**agent 不是"被模拟的人"，它就是一个用户。** 系统对它一视同仁：

| | 真人 | agent |
|---|---|---|
| 账户 | 有 | 同一套账户体系 |
| 登录 | 凭据 → PAM → logind 建会话 | **同一条 PAM 路径** |
| 桌面 | seat + VT + compositor + **真 GPU** | 同一个图形栈 |
| 应用 | 真浏览器/字体/音频 | 同一套 |
| 操作 | 手 → 键鼠 → X server | 同一条输入路径（XTEST） |

**推论：凡是"因为它是 agent 所以特殊"的东西都该删掉**——Xvfb、"服务必须住会话里"、loopback 特例、agent 专用通道。

### 目标声明（YZ 拍定，三条）

1. **与真人完全一样，只是不抢显示**：账户、PAM、图形栈、输入路径全部同构（见上表）；**唯一区别是不占物理显示**。YZ 主动告知后，它把桌面显示出来（同会话加输出，§六9）。
2. **开机自持**：系统重启后**无需 YZ 介入**，agent 自动登录自己的图形会话并开始操作。
3. **a11y 优先、像素兜底**：能读无障碍树就读树；像素用于交叉确认，或 a11y 覆盖不到时（自绘/游戏/未开标志的 Chromium → `mode=auto`，§5.4）。

要点：

- "不抢显示"与"完全一样"**不矛盾**：多会话并存、一次一个上屏（VT 切换）是 Linux 原生行为（§六10）；agent 只是**从不主动占 seat 的物理输出**，不是特殊化。
- 第 2 条**排除**"真人先登录再 attach"，只能是机器可读凭据（文件 + `SSH_ASKPASS`，符合纪律）或 autologin。→ 实质回答 §5.2：**不是"linger 还是 PAM"二选一，而是"开机即有一条到它图形会话的路，凭据由文件提供"。**
- 第 1 条 + §六8：**可以不显示，但仍用 `renderD128` 渲染**——零显示竞争，且不露软件渲染的馅。
- 第 3 条复用已有 `mode=tree`/`op=element` 形状，**只换实现**，不改协议。

**一句话**：agent 是一个**从不登录到物理屏、但随时能被叫来看一下**的普通图形用户；重启后自己上来；能读无障碍树就读树，读不到才看像素。

### 范围与优先级

- **先做 Linux，不考虑无头，考虑真人使用场景。**
- **a11y 优先，像素兜底**（AT-SPI 元素树为主，抓屏/坐标注入为备）。

### 唯一保留的"选择"（且不是 agent 特殊性）

一个 seat 一次只有一个会话上屏——**两个真人共用一台机器也一样**。所以只需选"它的桌面输出到哪"：

| 选法 | 等价于 | 适用 |
|---|---|---|
| console 的 VT | 人就坐这儿用 | **机器是它自己的**（最对等） |
| 第二块 GPU 输出 / 虚拟连接器 | 接了第二台显示器 | 人要自己那块屏 |
| 无输出的 GPU 合成器 | 没接显示器的机器跑图形会话 | 单人一机 |

三个都**不是"无头"**，也都**不可被网站检测**（见 §六）。

## 三、网络：VBox 桥接 bug + Tailscale 绕行（本会话实测）

| 路径 | 1MB | 4MB |
|---|---|---|
| 桥接 IP `192.168.1.112`（原始 TCP） | **16.4s** | ~70s |
| Tailscale `100.112.50.115` | **0.74s** | **1.05–1.20s** |

- 根因 = **VBox 7.2.x 桥接模式收包 bug**（宿主 RSC 把 TCP 合并成超长帧 → guest e1000 丢；`rx_errors` 随传输涨）。
- **反直觉的关键点**：Tailscale 传输**仍走 enp0s8**（4MB 传输后 `enp0s8` rx +4.6MB，`enp0s3` +7KB；`tailscale ping` 报 `via 192.168.1.112:41641` 直连）。
- 真正原因：**WireGuard 线上是 UDP，而 RSC 只合并 TCP** → 超长帧路径不触发。增量对照：原始 TCP 使 `rx_errors` +165，Tailscale ~0。
- **结论：不需要 YZ 去宿主关 RSC**（原 handoff-10 §五 待办降级为"想根治原始 TCP 再考虑"）。
- 尾部残留：`/tmp/kilo/bw/`、Surface 家目录 `bw*.bin`（可清）。

## 四、Linux / Windows 现场事实（新会话会用到）

### Linux（本机 VM，CentOS Stream 9）

- **只有 seat0**。当前上屏的是 **gdm greeter**（`c2`, tty1, wayland, class=greeter, active）；**zhengyp 的图形会话 `15`(tty2, x11) 活着但 Active=no**（`/sys/class/tty/tty0/active` = tty1）—— 这是"两桌面并存、只换上屏"的活样本。
- **greeter 会被 GDM 拆了重建**（观测到 `c1` 消失 → `c2` 出现）。greeter 是 gdm 账户的、**GDM 的客户端**，不是我们桌面的"父亲"。
- **`screenlab` 正以 granted 跑在 zhengyp 的 `:0` 里**：
  `python -m screenlab.service.cli daemon --display :0 --socket /run/user/1000/screen/screen.sock --authority granted --xauth /run/user/1000/gdm/Xauthority`
- **root 的 `Xvfb :99 -auth /etc/screenlab/Xauthority`**；`/etc/screenlab/Xauthority` = 0600 归 `tangyu`，**zhengyp 读不到** → 连不上 `:99`；但 `/tmp/.X11-unix/X99` 是 **0777**（门开着、钥匙没有）。
- DRM：`/dev/dri/card0` 0660 root:video(+ACL)、`/dev/dri/renderD128` **0666**；**`card0-Virtual-1..8`**（Virtual-1 connected，其余 disconnected）。
- ZDOTDIR 无关；`loginctl` 里 zhengyp 有 6 个会话（5 tty + 1 x11）。

### Windows（Surface `192.168.1.112`）

- 会话：`0`(服务,138 procs) / `3`(**zhengyp**) / `4`(**screen**)，**两个交互会话各有 csrss/dwm/explorer/winlogon/LogonUI**。
- `LogonUI` **跑在每个会话内部** → 这是与 Linux greeter（独立会话）的结构性差别。
- `zhengyp` ∈ **Administrators**（同组的还有 `surface`/`Administrator`）；`screen` 是标准账户。`AutoAdminLogon=1`, `DefaultUserName=screen`。
- **`screenlab` 是装着的**（`%LOCALAPPDATA%\screenlab`，18:05 装；任务 enabled，daemon 曾在 session 4 跑，pythonw 10052/14480，日志端口 60776）——**handoff-10 写的"已 uninstall"不准**。
- ssh 落在 **Session 0**；`tasklist /fi` 被拒；`query`/`quser`/`qwinsta` **在 Windows 客户端上不存在**；读会话/进程要用 PowerShell（`Get-Process | Group-Object SessionId`、注册表 `...\Authentication\LogonUI\SessionData`）。
- 配 ssh 免密给**管理员账户**要走 `C:\ProgramData\ssh\administrators_authorized_keys`（非 `~/.ssh`）。

## 五、Linux 设计骨架（我的提案，**未经 YZ 裁决**）

### 5.1 关键发现：AT-SPI 本来就是一条 user unit

本机实证：

```
/usr/lib/systemd/user/at-spi-dbus-bus.service        ← user unit
/usr/share/dbus-1/services/org.a11y.Bus.service      → Exec=at-spi-bus-launcher
                                                       SystemdService=at-spi-dbus-bus.service
/etc/xdg/autostart/at-spi-dbus-bus.desktop
/usr/lib64/libatspi.so.0
```

→ **a11y 侧几乎不用新造东西**：有 `systemd --user` 就有 `systemctl --user start at-spi-dbus-bus.service`；`org.a11y.Bus` 还是 D-Bus 激活的（首调自动拉起）。
→ **目前 AT-SPI 只活在 gdm 的 greeter 会话里**，我们的 `:99` 上没有（因为没总线）。

### 5.2 "登录"的两种解法

| | 做法 | 代价 / 适用 |
|---|---|---|
| **A. linger** | `loginctl enable-linger <acct>` → 开机即有 `systemd --user` + `/run/user/<uid>` + 会话总线 + user 单元；**无需 PAM、密码、seat、VT，不上屏** | 最省；但要 root 一次；"登录"语义弱化 |
| **B. 真 PAM 登录** | agent 自己走 PAM → logind 建会话 → seat/VT → compositor | 更贴合"和真人一样"；要管凭据 |

**这是新会话要先裁决的第一件事。**

### 5.3 会话里要什么

- 显示：**真 GPU 后端**（不要 Xvfb）。候选：headless compositor（mutter `--headless` / wlroots headless，用 `renderD128`，**不占 DRM master**）+ XWayland（保住 X11 应用与 a11y）／或真 Xorg 跑在独立 DRM 连接器上。
- WM（保证 `outerWidth/Height` 合理、`_NET_ACTIVE_WINDOW` 存在）。
- 会话环境（**没有这些，a11y 总线起来也是空的**）：
  `NO_AT_BRIDGE=0`、`GTK_MODULES=gail:atk-bridge`、`QT_LINUX_ACCESSIBILITY_ALWAYS_ON=1`、Chromium `--force-renderer-accessibility`、`org.a11y.Status.IsEnabled=true`。
- 真字体、音频（PipeWire + dummy sink）、合理分辨率/DPR/时区、真实浏览器 profile。

### 5.4 a11y 面怎么落（协议形状保留，实现替换）

- 服务**在会话内做 AT-SPI 客户端**（`pyatspi`），把元素树序列化回传；**远程只认一种传输**，D-Bus 边界留在服务侧。
- 元素模型：`{id, role, name, description, bounds, states, actions, value}`。
- **`bounds` 是枢纽**：元素树与像素**共用同一坐标空间**，可互相校验、可平滑降级。
- `snapshot_id` 绑树版本（AT-SPI 无稳定 id，按路径合成，元素会变）。
- `mode=auto`：先 tree，应用没暴露（游戏/自绘/未开标志的 Chromium）→ 回退 pixels。
- 协议里已有的 `mode=tree` / `op=element` **形状是对的，保留**（这不是妥协）；但 `daemon.py` 里的 stub 与平台后端要重写。

**"尽量用 a11y"的确切含义（YZ 定调）**：**能用就用、不好用就像素，哪个方便用哪个**——a11y 是**加速器不是门槛**，像素对"像真人"的 agent 是**完备**的基线（真人本就只有眼+手）。所以"AT-SPI 不够好"不是风险，只是少赚。判断粒度 **per-op，不是 per-session**：同任务里"点按钮"用树、"拖滑块"用像素可并存。判断成本只三件事：**带 deadline 的探针**、**`bounds` 对齐**、能力探测。

**开销与缓解（两笔账）**：浏览器端（强制建树 CPU/内存）与客户端（D-Bus 遍历，大树上秒级、可能挂住）——**大头通常在客户端**。

- 客户端：**别全树序列化**，用 `bounds` + `getAccessibleAtPoint` / 按需子树只取当前操作相关部分；配 `snapshot_id` 缓存；探针带 deadline，超时切像素。
- 浏览器端：`--force-renderer-accessibility` **不阻塞加载**，只加 CPU，只有**病态大 DOM** 才明显慢。优先**懒开**（会话 AT-SPI 启用 + 客户端现身 → Chromium 自开，画像=屏幕阅读器真人；**需实测可靠性**），不灵再退 flag；或只在需要语义的任务里带 flag 启动。可控则用**最轻 AX 模式**。
- **默认策略先实测再定**（带 flag vs 不带、全树 vs 子树），别预优化。

### 5.5 要能被人看见（YZ 追加要求）

- **把显示服务器本身换成自带远程输出的那种**，不要外挂第二套：推荐 `xpra`，备选 `Xvnc`。
- 接入走 **loopback + ssh 隧道**（复用同一扇外门，不新增暴露面）；**默认关、按需开**；**默认 readonly**，可升级为接管。
- 接管时 **agent 停手**（协作规则，不是技术限制）。

### 5.6 已核实的包可用性

**注意：`dnf` 必须带 `--disablerepo=tailscale-stable`**（该 repo 的 GPG 校验坏了，会卡在交互确认）。

| 包 | 版本 | 仓库 |
|---|---|---|
| `python3-pyatspi` | 2.38.1-3.el9 | appstream |
| `at-spi2-core` | 2.40.3-1.el9 | appstream（已装） |
| `tigervnc-server` | 1.16.2-4.el9 | appstream |
| `x11vnc` | 0.9.17-1.el9 | epel |
| `xpra` | 5.0.10-3.el9.next | epel-next |

### 5.7 实测：mutter headless + Xwayland（会话末的一次 spike）

以 zhengyp 身份跑 `mutter`（Wayland 显示名 `wayland-spike`），结果：

**机制通了**：
```
Using Wayland display name 'wayland-spike'
Using public X11 display :1, (using :2 for managed services)   ← Xwayland 起来了
socket: wayland-spike, /tmp/.X11-unix/X1, X2
```
→ **"无输出 compositor + XWayland 保住 X11 应用与 a11y"这条路结构上可行**（X11 应用照跑）。

**但 GPU 是软件**：
```
VMware: No 3D enabled (0, 成功)
Failed to initialize accelerated iGPU/dGPU framebuffer sharing: Do not want to use
  software renderer (llvmpipe (LLVM 21.1.7, 128 bits)), falling back to CPU copy path
Xwayland glamor: GBM Wayland interfaces not available → Failed to initialize glamor, falling back to sw
Created gbm renderer for '/dev/dri/renderD128'  (vmwgfx, no mode setting)
```
→ 宿主（VirtualBox）**没开 3D 加速**，所以整条链落到 llvmpipe。**这就是 §六.4 说的那个天花板：VM 里"像真人"的上限由宿主 GPU 决定。**

- 可改：VirtualBox Display → **Enable 3D Acceleration**（guest 已是 `vmwgfx`），能解决"软件渲染"这一条。
- **但改不掉**：VBox 的 3D 是 SVGA3D/virgl，WebGL 串仍是 `SVGA3D`/`virgl` 之类，**不是消费级显卡**。要真像真机只能 GPU 直通或物理机。

**另一个必须记的坑**：
```
mutter-WARNING: Lost or failed to acquire name org.gnome.Mutter.ScreenCast
mutter-WARNING: Lost or failed to acquire name org.gnome.Mutter.RemoteDesktop
```
→ 这两个 D-Bus 名字**是每条用户的会话总线上的单例**。spike 里 mutter 以 zhengyp 跑、和 zhengyp 自己桌面的 mutter 共用一条总线 → **抢名字失败，屏录/远程桌面接口不可用**。
→ **推论：agent 的会话必须有自己的会话总线**（独立 uid → 独立 `/run/user/<uid>/bus`）。用 linger 方案天然满足；用"借人的会话"（granted 档）时这条要另想办法。

### 5.8 实测：以**非 seat 用户**跑 headless mutter + Xwayland，a11y 读到树、按 bounds 点击成功

会话末跑的一轮完整 spike（以 **uid 1001 = `tangyu`**，即"agent 自己的账户"那个形态）。**这一轮把 §5.3/§5.4 从提案变成了实证。**

**① 非 seat 用户也能起 headless compositor —— 且不需要 card0**
```
(mutter): Failed to open gpu '/dev/dri/card0': Failed to open DRM device: 权限不够
```
→ 如 §六.2 所料：`card0` 的 ACL 只给 seat 的活跃会话，非 seat 用户开不了；但 **`renderD128` 是 0666**，mutter 照样起来。
→ **"不占 DRM master、不上屏、仍是真会话"这个设计成立**（这正是我们要的那个夹缝）。

**② Xwayland 保住 X11 应用**
```
Using Wayland display name 'wl-slice'
Using public X11 display :1, (using :2 for managed services)
### xdisplay=:1
xdotool geometry: 0 0            ← xdotool 在 Xwayland 上可用
```

**③ a11y 树读出来了（这是关键）**
用 **GI 的 `Atspi`（PyGObject）**，不是 `pyatspi`：
```
application      name='wl-slice-app.py'
  frame            name='SliceApp' ext=(0,0,420,321)
      label            name='hello-slice' ext=(0,21,420,17)
      push button      name='CLICK-ME' ext=(0,38,420,34)
```
→ **AT-SPI 在这套"headless compositor + Xwayland + 非 seat 用户"里完全可用**，无需 seat、无需物理屏。
→ 顺带：**依赖只要 `python3-gobject` + `gir1.2-atspi-2.0`**，`python3-pyatspi` 不是必需的（§5.6 的清单可以简化）。

**④ a11y 优先 + 像素注入的组合跑通**
```
### act: click CLICK-ME via a11y bounds
click at 210 55
xdotool click done
```
→ **按 a11y 树给出的 bounds，用 X11 注入点中** —— §5.4 的"元素树与像素共用同一坐标空间、可互相校验"得到验证。

**⑤ 已知未验证 / 环境噪声**
- `pixels (PIL on Xwayland)` → `ModuleNotFoundError: No module named 'PIL'`：uid 1001 的 python 没装 Pillow，**像素面这轮没验**（环境问题，trivial）。
- 仍是软件渲染：`VMware: No 3D enabled` + `Failed to initialize glamor, falling back to sw`（同 §5.7，天花板不变）。
- `Failed to set environment variable … for gnome-session: Destination does not exist`：没跑 gnome-session 的正常噪声。
- app 自己报了 `impl_GetExtents: assertion 'ATK_IS_COMPONENT (user_data)' failed`（那个测试脚本的 ATK 实现问题，不影响 extents 读出）。
- cleanup 干净：`remaining mutter: 0  app: 0`。

**结论：核心架构已被证实**——**非 seat 用户 + headless compositor + Xwayland + AT-SPI** 这条路，a11y 与像素两扇门都开着，且不占物理屏、不占 DRM master。

## 六、概念结论（本会话澄清的，别再重复推导）

1. **会话 vs 桌面**：会话 = logind 的**登记/资格**；桌面 = **compositor + 窗口 + 缓冲 + 总线**。**可配对也可脱钩**（ssh = 有会话无桌面；`Xvfb` = 有桌面无会话）。
2. **显卡只"读"，不"画"**：渲染是内存里的事；显卡负责把 framebuffer **扫描输出**（需要 **DRM master**，每卡同时只有一个）。`renderD128`（渲染门，0666）与 `card0`（显示门，0660+ACL）**是两扇门**。**借 GPU 渲染 ≠ 需要 master**。
3. **Windows 的桌面是会话内的内核对象**（Session → Window Station → Desktop → Window），交互会话只能由**登录**产生；`LogonUI` 住在会话内部（而 Linux greeter 是独立会话）。Windows 锁屏**真换桌面**（切到 `WinSta0\Winlogon` 安全桌面），GNOME 锁屏只是同桌面画层 UI。
4. **headless 识别的实质不是"没有物理屏"**，而是**软件渲染 + 缺家具**。实测（Chrome 148 headless，本机）：

   ```
   outer:[0,0]  inner:[780,441]  chromeObj:"object"
   webgl:"NO-WEBGL"(带 --disable-gpu；不带则 SwiftShader)
   hc:2  tz:"Asia/Shanghai"
   ```
   （`ua`/`webdriver` 未采到，第二次跑超时。）
5. **"agent 操作"本身没有"假"的成分**：XTEST/`SendInput` 走内核输入路径，浏览器侧 `isTrusted=true`（只有 JS `dispatchEvent` 是 false）。
6. **Linux 上"截屏"和"a11y"是两扇独立的门**（X cookie vs 会话总线）；**Windows 上它们被同一套墙管**（session/desktop/integrity）。
7. **Wayland 下 AT-SPI 照样工作**（不依赖显示服务器）；Wayland 的难处只在**像素**。
8. **网站感知不到"显示"这一层，只感知"家具"**：有没有帧被扫描输出、接没接显示器、有没有 compositor、占没占 DRM master——全在浏览器可见面之下。§六第 4 条的"headless 识别"实质是**缺家具**（`outer:[0,0]`、SwiftShader、无 WM）。推论：**"不上屏"≠"露馅"**；但**"不用 GPU 渲染"会露馅**（WebGL 暴露 `SwiftShader`/`llvmpipe` + 时序异常）。正解：**渲染走 `renderD128`（真 GPU），显示不碰 `card0`（不取 master）**——零显示竞争，同时保住真 GPU 指纹。即 §二"无输出的 GPU 合成器"。
9. **可见性 = 同一会话加输出，不是新开显示**：想看时（YZ 告知后）给现有会话加 xpra/Xvnc 输出；**必须镜像现有 framebuffer、保持同一分辨率**，否则 `screen.width`/`innerWidth` 变化会被网站看到（视口抖动）。这样"看/不看"对网站透明。触发点在协作层（YZ 告知 → 它开），默认关、默认 readonly、接管时停手（§5.5 形状不变）。推论：**"你看着它"与"它自己跑"是同一会话的两种观察方式，不是两种模式。**
10. **"抢显示"的正解是分配，不是仲裁**：并发会话是内核默认能力（每账号各自 logind 会话 + `systemd --user` + compositor + a11y 总线，真并行；一个 seat 一次只一个会话上屏 = VT 切换，非互斥，后台会话照跑）。要"同时可见"只有 **multiseat**（多 seat 各绑自己的 GPU 输出 + 输入设备；单卡同时只一个 DRM master，实际要两块 GPU/独立输出）或**远程导出**（各会话各自导出）。故 seat/VT 归属是一次性配置，运行期不抢；真人的 fast-user-switching 就是现成协作规则。→ 串起 §七 第 3、6 条：**granted 档 = 两人共用同一会话**，只有这时"抢"才回来，退化为 §5.5 协作规则。
11. **a11y 是加速器，不是能力门槛**：像素对"像真人"的 agent **完备**（人本就只有眼+手），a11y 只赢在语义/鲁棒（元素身份、屏外可读、坐标不漂）。故"AT-SPI 不够好"不是风险，只需一个**带超时的选择器**；`mode=auto` 落在**每次操作**，非每会话。细节与开销缓解见 §5.4。
12. **`--force-renderer-accessibility` 不暴露自动化**：a11y 树在 **DOM 之下**，无标准 Web API 可查；仅有的侧信道是性能，且画像 = **屏幕阅读器真人**（加分项，非破绽）。真正的自动化信号是家具层那批（§六 4/8：`webdriver`、CDP、`HeadlessChrome`、SwiftShader、无字体/音频/WM、`outer:[0,0]`），**a11y 不在其中**。其开销分**浏览器端（建树）与客户端（遍历）两笔，大头常在客户端**。

## 七、待 YZ 裁决（新会话的入口）

1. **登录模型**：linger（无需密码）还是真 PAM 登录？（§5.2）——**仍开放**；§5.8 是以已存在的 uid 1001 直接跑的，linger 本身没测。
2. ~~**X11 还是 Wayland**~~ → **已收敛（§5.8）**：**headless mutter(Wayland) + Xwayland**，X11 应用与 a11y 都在。
3. ~~**桌面输出模型**~~ → **已收敛（§5.8）**：**无输出的 GPU 合成器**（用 `renderD128`，不占 `card0`/master、不上屏）。
4. **看屏方案**：xpra 还是 Xvnc；默认 readonly 是否够。
5. **是否保留现有 `screenlab` 的协议形状**（我的建议：保留 `mode=tree`/`op=element`，重写实现）。
6. **granted 档**（借人正在用的桌面）要不要一起设计（同一会话 → a11y 天然可读）。

## 八、遗留（与本次目标无关，别丢）

1. `screenlab/install/install.ps1` **未提交**（端口策略：默认 9911 + 占用回退）。
2. 回写权威分册 `cogos/docs/design-agent-tools.md`（Windows 装配 + VBox 桥接坑）。
3. P2/P3：断连即终态、granted 的 `stop` —— 未做。
4. 测试残留可清（§三末尾）。
5. Surface 状态：screenlab 装着但 daemon 未运行（screen 会话在锁屏）；`~\screenlab-p4\`、旧原型 `~\screenlab\` 仍在。

## 九、环境与命令速查

- **VM（本机）**：`10.0.2.15`(NAT, enp0s3) / `192.168.1.13`(桥接, enp0s8) / tailscale `100.79.86.84`；CentOS Stream 9，`e1000`，firewalld active，**无免密 sudo**。
- **Surface**：`ssh screen@192.168.1.112`（key 免密）；tailnet `100.112.50.115`。默认 shell 是 **cmd**（`;` 不分句、多命令用 `&`）；`%SystemRoot%\System32\query.exe` **不存在**。
- **cogos**：`/home/zhengyp/work/A/cogos`，分支 `feat/screenlab-p2`；测试 `python3.11 -m pytest tests/ -q`。
- **dnf**：一律加 `--disablerepo=tailscale-stable`。

## 纪律

- 跑测试用 `python3.11 -m pytest`；结论先落 checkpoint/spec，定案再回写 `cogos/docs/design-agent-tools.md`。
- 目标侧叫"**服务**"不叫 agent；**认证不在协议里**；`screenlab/` 禁止 import cogos。
- 密码类只经文件与 `SSH_ASKPASS`，绝不落进命令行或工具输出。
- ⚠️ **本会话末有一次凭据值进入工具输出**（spike 期间的某个 terminal 输出，值不复述；来源未定）。已知临时 Xwayland `-auth` 文件已随 spike 删除、`tangyu` 无 logind 会话，故若来源是临时 cookie 则已失效；**若来源是持久凭据（`/etc/screenlab/Xauthority` 或某账户密码）→ 需轮换**。取凭据的命令今后必须重定向/截断。
- **验证重启**：本机（会断会话）不用；Surface 用注入 UI 或人工。
