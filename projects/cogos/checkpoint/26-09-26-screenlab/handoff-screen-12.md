# handoff｜Linux「agent = 一个普通用户」垂直切片实测 · 2026-09-20 #12

> **前序**：`handoff-screen-11.md`（目标重置 + 设计骨架 + §六概念结论）。本会话把 §五/§二 的骨架**在本 VM 上打了第一次实测**。
> **一句话**：把"agent 账号 = tangyu / 真 PAM 登录 / 非 seat 的 headless GPU 合成器 / a11y 优先"中最险的一枪打通了——**a11y 树 + XTEST 输入在同一非 seat 会话里闭环成立**；**像素抓屏**是唯一被打回且已定位的缺口。

## 一、本会话做了什么

1. 环境探查（GPU/会话/包/绑定，见 §二）。
2. **打通 tangyu 通路**：给 tangyu 加 zhengyp 的 pubkey → `ssh tangyu@localhost` 免密 → 经 **PAM/logind** 拿到 `/run/user/1001` + `systemctl --user`（**这就是"真 PAM 登录"路径**，无需 reboot/seat/linger）。
3. 装 `python3-pillow`（系统级）。
4. **垂直切片**（4 个脚本，见 §三、§四）。
5. 清理（进程/unit 全清）。

## 二、环境事实（本 VM，实测）

- `zhengyp`(1000) ∈ `wheel`+`video`，有 user manager；`tangyu`(1001) **仅组 tangyu**。
- `sudo` 经 `~/.secrets/centos.key`（**纪律**：密码只喂 `sudo` 的 stdin；本会话曾因重定向顺序写反**泄漏一次**，见 §六）。
- DRM：`card0` 0660 root:video(+ACL)、`renderD128` 0666。
- 关键件：`mutter 40.9`（**有 `--virtual-monitor WxH`**）、`Xwayland`、`xdotool`、`at-spi2-core`、**`Atspi-2.0.typelib`（GI 可用）**、`pipewire 1.4.9`、`wireplumber`、`xdg-desktop-portal-gnome 41.2`、`gst-launch`。
  - **无**：`xpra`/`x11vnc`/`grim`/`weston`/`sway`/`wlroots`/`python3-pyatspi`（**pyatspi 不需要**，GI 直连 Atspi）。
- **本 VM 无 3D**：vmwgfx `No 3D enabled` → llvmpipe/软件。→ **指纹目标（真 GPU 渲染躲 SwiftShader）在此不可验证**，需换有 3D 的机器。
- 旧装配仍在：`screenlab.service`(**User=tangyu**, `:99`) + `screenlab-xvfb.service`（root Xvfb）已 enabled——被否定的旧模型，**未动**。

## 三、切片结果（结论先行）

| 环节 | 结果 | 证据 |
|---|---|---|
| tangyu 免密 ssh → user manager | ✅ | `/run/user/1001` 在，`systemctl --user is-system-running`=running |
| AT-SPI user unit（**免 root**） | ✅ | `at-spi-dbus-bus.service` active；`org.a11y.Bus` 在 tangyu 总线 |
| headless 合成器 | ✅ | `mutter --headless --virtual-monitor 1280x720` 起；日志 `Added virtual monitor Meta-0` |
| Xwayland | ✅ | 自动起 `:1`；`xdotool getdisplaygeometry` = **1280 720** |
| **AT-SPI 树（GI 直读）** | ✅ | `application 'wl-slice-app.py' > frame 'SliceApp'(8,25,420,321) > push button 'CLICK-ME'(8,63,420,34)` |
| **a11y bounds → XTEST 点击** | ✅ | 按 bounds 算 (218,80) → `xdotool` 点击 → 应用打 **`BTN-CLICKED`** |
| user unit 拉起合成器 | ✅ | `systemd-run --user --unit=wl-slice` → unit active |
| **像素抓屏** | ❌ | Pillow `ImageGrab` on Xwayland root：`X get_image failed: error 8 (BadMatch)` |

**核心闭环（a11y 看 + 输入点）在"非 seat 会话 + 无输出 GPU 合成器"上成立。**

## 四、三个关键发现（别再重推）

1. **`--virtual-monitor WxH` 是关键**：`mutter --headless` **不带它就没有输出 → Xwayland 根窗口 0×0**（第一次切片就是栽在这：`xdotool geometry=0 0`，点击无意义）。带上即得真实屏尺寸，a11y bounds 才有意义。
2. **像素抓屏在 rootless Xwayland 上就是不行**（复现 `spec-screen-1.md` §5.1 早记的 `XGetImage BadMatch`）。**像素兜底必须走 Wayland 侧** → 已定位路线：mutter `org.gnome.Mutter.ScreenCast`(v4) `CreateSession` → RecordVirtual/Monitor → `PipeWireStreamAdded(node)` → `gst-launch-1.0 pipewiresrc path=<node>`；现成件齐（pipewire/wireplumber/portal/gst）。
3. **GPU 权限来自 seat，不来自 ssh**：tangyu 经 ssh（无 seat）打不开 `card0`（0660 root:video）→ mutter 落 "surfaceless **without GPU**"；zhengyp 有 seat（logind 给 ACL）→ 能开 `renderD128`。→ **card0 的 ACL 由 seat 登录授予**；这给"agent 登自己的 seat"一个**天然的 GPU 权限来源**（无需把 tangyu 塞进 video 组）。
   - 注：即便不谈指纹，本 VM 也没 3D，两种都落到软件。

## 五、对系统的改动（可回滚）

- `/home/tangyu/.ssh/authorized_keys`：加入 `zhengyp` 的 pubkey（**唯一持久改动**）。
- 安装 `python3-pillow 10.0.1`（系统级）。
- 临时进程/unit 已全清（mutter=0、app=0、`wl-slice` unit 已停）。
- **未动**旧 `screenlab*.service`。

## 六、纪律备忘（本会话踩的坑）

- **`pkill -f <pattern>` 会匹配到自己所在的命令行** → 自伤（本地/远端各踩一次，一次把命令挂住）。**杀进程用 `pkill -x <精确名>` 或按 PID**。
- **sudo 密码只喂 stdin**：`sudo ... < key 2>&1 | tail` 顺序要正确；`| tail < key` 会把 key 打出来（本会话泄漏一次）。
- **`sudo` 不缓存凭据**（`timestamp_timeout=0`）：`sudo -n` 永远报"需要密码"，`-v` 也不留缓存。轮换密码的正解是**密码行先给 sudo、余下喂 chpasswd**：
  `{ cat oldkey; printf 'zhengyp:%s\n' "$NEW"; } | sudo -k -S -p '' /usr/sbin/chpasswd`
  成功后覆盖 `~/.secrets/centos.key`，再用 `sudo -k -S -p '' true < key` 复验。**密码已于 09-20 轮换**（`centos.key` 33B / 0600，待 YZ 备份）。

## 七、下一步（TODO）

1. **像素兜底**：ScreenCast(v4)+PipeWire 打通 → 复验 **a11y bounds ↔ 像素坐标同一空间**（§5.4 的 `bounds` 枢纽）。← 唯一未闭的切片环节。
2. **重启环节（autologin）**：**待 YZ**（需 reboot，本会话按要求跳过）。
3. **定 X11/XWayland vs 原生 Wayland**：本切片走 **XWayland 已验证可行**（a11y 与 XTEST 都通）；原生 Wayland 的输入/像素要走 libei/portal，件多。
4. **按新模型重写服务内部**：**保** `proto/`(protocol/framing/client) 与 `cogos/agent/impl/graphics.py`（协议与 agent 侧不动）；**换** `service/backends*` 与生命周期层（账号/compositor/a11y 总线供给）。
5. 停用旧 `screenlab` system 服务（root）。
6. 服务形态：**agent 账号的 user unit 集群**（compositor + 服务），本会话已用 `systemd-run --user` 验证可行。

## 八、命令速查（本会话验证过的形状）

```bash
# 进 tangyu（真 PAM 登录 → user manager）
ssh tangyu@localhost

# 会话内起合成器（user unit，常驻）
export XDG_RUNTIME_DIR=/run/user/1001 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
systemctl --user start at-spi-dbus-bus.service
systemd-run --user --unit=wl-slice --collect -- \
  mutter --headless --virtual-monitor 1280x720 --wayland-display=wl-slice
# 取 Xwayland 显示号：grep 'Using public X11 display' <日志>
# a11y 树：python3 gi -> Atspi.get_desktop(0)，walk get_child_at_index
# 注入：DISPLAY=:1 xdotool mousemove --sync X Y click 1
```
