# handoff｜交接：从"验证假设"继续 · 2026-09-21 #13

> **新会话读本文件即可开工。**
> 细节：`handoff-screen-12.md`（本 VM 垂直切片实测全文）；**假设清单 + 计划 + 步骤：`screen-verify-1.md`（最重要）**；设计骨架/概念结论：`handoff-screen-11.md`；脚本与原始证据：`screen-lab-verify/`。

## 一、现在到哪了（一句话）

目标（agent = 一个普通 Linux 用户，不抢显示、按需可见、a11y 优先像素兜底、重启自持）**尚未实现**；本会话只做了一次**可行性实验**，证明了其中最险的一环可行，其余仍是**待验假设**。**没写任何生产代码。**

## 二、本会话（#12）已证实（实测，不是推断）

- tangyu 经 **真 PAM 登录**（`ssh tangyu@localhost`，pubkey 已装）→ `/run/user/1001` + `systemctl --user` running。
- `at-spi-dbus-bus.service` **user unit 免 root** 起；**AT-SPI 树经 GI（`Atspi-2.0.typelib`）直读**（无需 pyatspi）。
- `mutter --headless --virtual-monitor 1280x720` + Xwayland：屏 1280×720，**不占 DRM master**。
- **看→点闭环**：a11y bounds → `xdotool` XTEST 点击 → 应用打 `BTN-CLICKED`。
- `systemd-run --user` 可让合成器**常驻**（user unit 拉起会话的雏形）。

**核心发现**：`--virtual-monitor` 是 headless 有屏的关键；rootless Xwayland 根窗口 `XGetImage BadMatch`（像素必须走 Wayland 侧）；`card0` 权限来自 **seat** 而非 ssh；本 VM **无 3D**，指纹不可验。

## 三、从哪继续（按环境分批，逐条落 `screen-verify-1.md` 的模板）

| Phase | 假设 | 需谁 |
|---|---|---|
| **0（可立即做）** | A1 像素(ScreenCast+PipeWire)、A2 复用同一路输出、A3 act element/per-op、A4 Chromium a11y 质量、A5 不占 master、A6 tangyu 无 seat 拿 `renderD128`、A11 user unit 集群 | 无需 YZ |
| **1** | A7 seat/VT 图形登录（类型/ACL/**是否抢屏**） | **YZ 在场**（切 VT） |
| **2** | A8 重启自持（linger+user unit 或图形 autologin） | **YZ**（reboot；**reboot 会结束当前会话**，故先落记录再重启） |
| **3** | A9 真 GPU 指纹 | **需 3D 机器**（本 VM 无 3D） |
| — | A10 多人/多 seat | 留概念（handoff-11 §六10） |

**建议**：先跑 Phase 0（一枪 A1/A2 同源、一次实验连验 A5/A6），落表；A7/A8 等 YZ；A9 等机器。**A6 比 A7 更关键**（若"seat 登录必抢屏"，设计就转"无 seat headless + 单独解决 GPU 权限"）。

## 三·五、⚠️ 并发冲突（新会话开工前**必须先处理**）

> **更新（2026-09-21 #14）**：经 YZ 确认，那两个 `kilo attach`（PID 13019/13588）是**同一个会话**（手机 + 电脑同时 attach），**不是并发会话**，可忽略。本节其余内容仅作历史记录。

**现象**：同一台机器上**两个 Kilo attach 会话**同时挂着同一 server、同一目录（PID `13019` 约 17 分钟、`13588` 约 13 分钟），在做**同一件事**：

- 另一会话的 `/tmp/kilo/probe-pixel.sh`（00:05）与 `slice1/2` 同类：`systemctl --user stop wl-slice` + 起 mutter + 调 `ScreenCast`。
- 另一会话还 **`systemctl stop gdm`** 且 **`loginctl terminate-session 15`**（zhengyp 的图形会话）。
- terminal 列表疑似 **server 级共享**（本会话能看到另一个会话的 terminal 13/14）。

**后果**：本会话 Phase 0 起的合成器 unit `wl` 被杀并回收；A1 报 `org.gnome.Mutter.ScreenCast: The name is not activatable`——**假失败**（`slice4.sh` 里同一调用成功过），是**抢 D-Bus 名**导致。

**当前环境状态（另一会话改的，非我所为）**：
- `gdm` **inactive**；zhengyp 图形会话 `15` 已终止；seat0 上**没有 greeter**了（原 tty1）。
- tangyu 只剩 `loginctl` 里的 `n/a` 用户管理器会话。

**开工前请先定**：
1. **只保留一个会话做实验**（否则 mutter/pipewire/单元名会互踩）。
2. 是否 `systemctl start gdm` 恢复图形登录。
3. 统一**单元命名**（如 `screenlab-*`），别再用 `wl` / `wl-slice` 这类会撞的名字。

## 四、入口与纪律

```bash
ssh tangyu@localhost                     # 真 PAM 登录 → user manager
export XDG_RUNTIME_DIR=/run/user/1001 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
ssh tangyu@localhost 'bash -s' < screen-lab-verify/slice2.sh   # 已验证可跑
```
- **sudo**：`sudo ... < ~/.secrets/centos.key`（**密码只喂 stdin**，禁 `| tail < key`）。
- **`pkill -f <pattern>` 会自伤**（匹配到自己命令行）→ 用 `-x` 或 PID。
- 每条结论**先落 `screen-verify-1.md`**，定案再回写 spec / `cogos/docs`。

## 五、系统现状与改动

- 唯一持久改动：`/home/tangyu/.ssh/authorized_keys` 加了 zhengyp pubkey；装了 `python3-pillow`。
- 旧 `screenlab.service`(User=tangyu,`:99`) / `screenlab-xvfb.service` **仍 enabled、未动**。
- 临时进程/unit 已清（mutter=0）。
- `/tmp/kilo/` 下还有本次的临时脚本副本（`slice1..4.sh`），**权威副本已在 `screen-lab-verify/`**。
