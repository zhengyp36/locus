# handoff｜交接：M2 图形路线实验（第一轮）· 2026-09-21 #14

> **新会话读本文件即可开工。**
> **最重要的细节文件**：`screen-exp-log.md`（实验清单 + 逐条记录 + 脚本索引）；假设清单/计划：`screen-verify-1.md`；上一轮：`handoff-screen-13.md`；脚本：`screen-lab-verify/`。

## 一、一句话现状

M2（agent 自己的 headless 图形桌面）的**技术链路已验通大半**：完整 headless 桌面、a11y 读树、X11 注入、ScreenCast 取帧、无 seat 拿 GPU 全部成立；但暴露**两个关键限制**：① 原生 Wayland 客户端的 AT-SPI 坐标**不是全局坐标**；② 原生 Wayland 下的输入注入**没通**。结论是**被测应用跑 X11/Xwayland** 最省。**没写任何生产代码。**

## 二、本轮已证实（实测）

| 项 | 结果 |
|---|---|
| **E2 完整 headless 桌面** | ✅ `gnome-shell --headless --virtual-monitor WxH` 常驻，含 Xwayland、DisplayConfig，Wayland/X11 客户端都能开窗 |
| **E3 虚拟显示器参数** | ✅ `MetaVirtualMonitor/MetaVendor`、`primary=False`、**无 EDID**；多屏可造 |
| **E4 a11y 读树** | ✅ AT-SPI 可读、元素可定位取 bounds；gnome-shell 全树很大 → 需子树查询 + deadline |
| **E5 输入注入** | ✅ **X11(Xwayland)+XTEST 命中**（`BTN-PRESS`→`BTN-CLICKED`）；❌ 原生 Wayland（XTEST 无效、RD 报 `invalid virtual device button`） |
| **A1 ScreenCast 取帧** | ✅ 用 **`RecordMonitor(connector)`** 拿到真实 1920×1080 帧（`RecordVirtual` 只出 1×1）；❌ 但「a11y↔像素同空间」**仅 X11 成立** |
| **A6 无 seat 拿 GPU** | ✅ 给 `card0` ACL → 日志变 `Created gbm renderer for renderD128`（**钥匙是 card0 权限**，renderD128 虽是 0666 不够） |
| VBox 3D | ✅ YZ 改配置后 `Capabilities: ... 3D, gbobject, dx`，非 `No 3D enabled` |

## 三、两个关键新发现（本轮的真正产出）

1. **Wayland 客户端的 AT-SPI `SCREEN` 坐标是"窗口局部坐标"，不是全局坐标。**
   受控实验：窗口在帧里居中于 (≈774,384)，a11y 却报 (26,46)（= toplevel 表面内的内容偏移）。因为 **Wayland 客户端不知道自己窗口的全局位置**。
   → 影响 A3 与"a11y 优先 + 像素兜底"的坐标对齐。`org.gnome.Shell.Introspect.GetWindows` 被封（AccessDenied）。
2. **注入路径与客户端后端强耦合**：X11=XTEST 通；Wayland 需 Mutter RemoteDesktop 的 `NotifyPointerMotionAbsolute(stream, …)`（仍需补 stream/原点）。

## 四、现在要讨论的两条路线（YZ 定的议题）

| | **A. 布局/结构路线** | **B. 坐标/像素路线** |
|---|---|---|
| 依据 | AT-SPI 树结构（路径/角色/名字/状态） | 屏幕像素坐标 |
| 动作 | 调 **`Action.doAction`**（不碰坐标） | 算坐标 → 注入点击 |
| 需要全局坐标 | **不需要** | 需要（Wayland 需补窗口原点；X11 天然有） |
| 受 Wayland 限制 | 不受 | 受（坐标 + 注入） |
| 强度 / 短板 | 稳、抗布局变化；但 a11y 覆盖不全（canvas/自绘/部分浏览器控件） | 万能；但脆（布局/滚动变化即失效） |

**要钉的三件事**：
1. **A 的覆盖率**：浏览器里 `Action` 到底能点多少东西；
2. **B 的可靠性**：X11 全链（a11y bounds → 坐标 → 点击）vs Wayland 补窗口原点；
3. **A/B 的切换判据**（何时从 A 退到 B）。

## 五、待做实验（`screen-exp-log.md` 清单为准）

- 待做：**A2**（同一路流复用/给人看）、**A3**（按 id 重解析 bounds 点击 + 子树/deadline）、**A4**（Chromium a11y 质量/代价/懒开，需装 chromium）、**E6**（行为 humanization）。
- 条件触发：**E1/A12**（过指纹基线，需真 3D/可用 DMA 的机器）。
- 需 YZ：**A8**（重启自持，linger+user unit）。

## 六、环境现状与改动（开工前先核对）

- 目标账号 `tangyu(1001)`；`gdm` **active**（greeter 占 seat0/tty1）。
- **持久改动**：
  - `loginctl enable-linger tangyu`（可逆 `disable-linger`）
  - 临时 ACL `setfacl -m u:tangyu:rw /dev/dri/card0`（**重启即失效**，重启后需重加）
  - VBox 主机侧 **3D 加速已开**（YZ 改）
  - 运行中 user unit `screenlab-shell`（headless gnome-shell）
- **注意**：关 ScreenCast session 会**崩掉整个 headless shell**（可复现）→ 实验间要重启 shell。

## 七、入口与纪律

```bash
ssh tangyu@localhost
export XDG_RUNTIME_DIR=/run/user/1001 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
# 起 headless 桌面（单元名统一 screenlab-*）
systemd-run --user --unit=screenlab-shell --collect --setenv=NO_AT_BRIDGE=0 \
  --property=StandardError=file:/tmp/screenlab-shell.err \
  -- gnome-shell --headless --virtual-monitor 1920x1080 --wayland-display=screenlab-0
```
- **sudo**：`sudo -S ... < ~/.secrets/centos.key`（本机必须 `-S`，密码只喂 stdin）。
- **`pkill -f <pattern>` 会自伤**（匹配到自己命令行）→ 用 `-x` 或 PID。
- tangyu 不在 `systemd-journal` 组 → 读 shell 日志靠 `--property=StandardError=file:/tmp/...`。
- 每条结论**先落 `screen-exp-log.md`**。

## 八、已知坑（省时间）

- headless Xwayland 在 `:0`/`:1` 飘，**`:0` 常挂**；`xdotool` 报 `No protocol specified` 或超时。
- `ScreenCast.Stream.Start` **不存在**（流随 `Session.Start` 自动开始）。
- `pipewiresrc path=` 要 **node id**（`wpctl status` 里的 Video Streams），不是 `output_N` 的 id。
- mutter 对 `vmwgfx` **硬编码禁用 DMA buffer 共享**（`MUTTER_DEBUG_USE_KMS_MODIFIERS=1` 绕不过），但不影响 RecordMonitor 走 CPU 路径出帧。
- `MUTTER_DEBUG_FORCE_EGL_STREAM=1` 会直接起不来。
- mutter/gnome-shell 的 ScreenCast/RemoteDesktop **session 对象只对创建它的 D-Bus 连接暴露接口** → 必须同一 Python/Gio 连接内完成。

## 九、建议的首次动作

1. 核对第六节环境（linger、card0 ACL、shell 是否在跑；不在就重启）。
2. 先和 YZ 把第四节的三件事定下来，再挑一条实验跑（建议：**X11 客户端上的 A3 全链**，或 **A 的 `Action` 覆盖率**）。
