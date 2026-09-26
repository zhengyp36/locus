# handoff｜图形电脑：Android 实验起步（看屏 / 操作）· 2026-09-20 #3

> **新会话任务**：继续"图形化看电脑"，本会话已把 `screen/1` 在 **Linux/X11（两机）+ Windows** 上跑通并落了最小原型；下一步是 **Android 验证场**（本会话已确认本机/212 均无 `adb`/`scrcpy`，未开工）。
> **交接语**：读 `work/A/checkpoint/handoff-screen-03.md`；细节读 `spec-screen-1.md`（设计稿）、`checkpoint-4.md`（本会话实测/系统改动）、`checkpoint-3.md`（X11/Wayland 实测）、`screen-lab/README.md`（原型用法与验收）。
> **前序**：`handoff-screen-01.md`（图形面讨论 + 阶段划分）→ `handoff-screen-02.md`（X11 实测）→ `checkpoint-4.md`（落码 + Windows）。

## 本会话性质

**讨论 + 实测 + 落码。** cogos 代码基线仍 `45ab216`、工作区干净；**改了 Windows `192.168.1.112` 的系统配置**（`checkpoint-4.md` §五，可回退）。

## 本会话成果（一句话）

`screen/1` 从"两台机上的手工闭包"变成 **三平台 + 有设计稿 + 有最小 daemon/CLI 原型**：`spec-screen-1.md` + `screen-lab/`（1082 行），Windows（Surface）新打通并修掉 DPI 坐标错位。

## 已收敛结论（可当既定）

- **三平台已通**：本机 `:0`（GNOME/Xorg）、212 `Xvfb :99`（+openbox）、Windows Surface `screen` 标准账户交互会话。
- **daemon 必须在目标会话内部**（Linux/Wayland 与 Windows 同结论）：GNOME Shell D-Bus 抓屏跨会话 `AccessDenied`；rootless Xwayland 根窗口 `BadMatch`；Windows Session 0（sshd 所在）**没有桌面**，抓屏直接失败。
- **`snapshot_id` 必需**：窗口装饰使坐标漂移（y 158→185）；`act(pointer)` 必须绑当次快照，过期即拒。
- **`act` 的返回世代只当提示**：即时抓帧可能早于 UI 渲染，判稳定态必须再 `see --wait-stable`。
- **WM 是 `act` 可靠性的前置**（X11）；Windows 由系统保证。
- **工具选型**：X11 = Pillow `ImageGrab(xdisplay=)` + `xdotool`；Windows = Pillow GDI `all_screens` + `SendInput`(ctypes) + **per-monitor DPI 感知**（不开则图像坐标与注入空间差一个缩放比，实测 1.5×）。
- **传输**：Linux 用 Unix socket；Windows 用 **loopback TCP + `ssh -L`**（Windows OpenSSH 不支持 AF_UNIX 转发）。
- **不推事件**：靠 `frame_hash` + `wait_stable`；blob 内容寻址去重；图是原语、不做第五域。
- **客户端薄 = 不含平台逻辑、但含 agent 语义**（mechanical vs semantic）；a11y 不是另一族工具，是 `see` 的一条 `mode` 与 `act` 的一种宾语（**尚未实现**）。
- Wayland 原生通道存在（`org.gnome.Mutter.RemoteDesktop` 可 `CreateSession`），看屏要叠 ScreenCast + PipeWire，暂缓。

## 待 YZ 裁决（11 项，均未动）

1. 图 = 持久资产（`image_ctx` 有根）还是临时介质（`img-tool` 无根）——两条 lineage 未并。
2. 自建电脑 vs E2B 类云桌面。
3. 客户端薄到哪（纯管道 vs 带薄语义层）——原型按"带薄语义层"写。
4. 先做哪个平台（Linux/Windows 已通、Android 未试）。
5. 是否给 212 sudo（本机已给）。
6. 旧遗留 4b 装配 / 按需加载与本线的关系。
7. **代码放哪**：新仓 `screen-lab` vs cogos 子包。
8. 是否做 Wayland 适配（YZ 日常是 Wayland）。
9. Xfce 会话 XSMP 残留：根修还是弃用 Xfce。
10. 密码轮换 / 关 SSH 密码登录 / 收紧 firewalld（`checkpoint-3.md` §七）；**Windows 侧新增暴露面**：`screen` 账户可被局域网密码登录（`sshd` 默认 `PasswordAuthentication yes`），其密码明文放在本机 `/tmp/kilo/screen.win.pw`。
11. Windows 线已重启并打通（本会话）；后续是否收编 `zhengyp` 自身桌面为第二个 Windows 场，待定。

## 下一步：Android 验证场

### 为什么是 Android

`handoff-screen-01` 已判定 `scrcpy`/`adb` 是**最便宜的 adapter 验证场**：看/动都有现成通道，且**没有"daemon 必须在目标会话内"的坑**——设备侧只有 `adbd`，daemon 可跑在宿主（Linux/Windows），经 adb 驱动。

### 可选通道（待选型）

| 能力 | 通道 | 备注 |
|---|---|---|
| 看（像素） | `adb exec-out screencap -p` | PNG 走 stdout；无需 root |
| 看（树） | `uiautomator dump` / a11y | Android 的"元素树"比 AT-SPI 好用 |
| 动（输入） | `adb shell input tap/swipe/text/keyevent` | 无需 root；`text` 对中文/特殊字符有限制 |
| 低延迟看+动 | `scrcpy`（server 推到 `/data/local/tmp`） | H.264 流 + 控制通道；重，但接近"真机手感" |

### 坐标系（要提前想清，Windows 的教训）

`screencap` 给**设备物理像素**，`input tap` 也吃设备像素 → 同一空间，比 Windows 简单。要注意：**旋转**（`dumpsys input` / `wm size`）、**density**、**刘海/挖孔**、多屏（折叠屏）。

### daemon 形态（与 Windows 的差异）

- Android **不需要**"在设备会话内起 daemon"；`screen-lab` 只需加一个 `backends_android.py`（capture/act 走 `adb` 子进程），daemon 仍跑在宿主。
- 传输：宿主上照旧 Unix socket（Linux）或 TCP（Windows）；`adb forward` 在需要设备侧监听时才用。

### 设备/环境待确认（**需 YZ 定**）

1. **用哪台设备**：YZ 的 Android 手机（已在 `~/.ssh/authorized_keys` 里、走 tailscale，但**是天天用的真机**，有隐私与误操作风险）／ 一台备机 ／ **Surface 上的 Android 模拟器**（Android Studio AVD，需确认 Hyper-V/WHPX）。
2. **连接方式**：USB（需开 USB 调试）／ 无线调试（Android 11+ 配对码，或 `adb tcpip 5555`）／ tailscale 上直连。
3. **是否接受 root**：不 root 也能跑 `screencap`/`input`/`uiautomator`，建议先不 root。
4. **装机位置**：本机（locus VM，需装 `android-tools`）还是 Surface（Windows 侧装 platform-tools）。

### 候选取路（供 YZ 选）

1. **最窄切口**：宿主装 `android-tools` → `adb devices` 通 → 写 `backends_android.py`（`screencap` + `input`）→ 复用现有 client/CLI 跑 LLM 在环"看→点→再看"。
2. **先评估 scrcpy 路线**：`dnf install scrcpy` 是否可得（CentOS Stream 9 可能在 rpmfusion），评估流式看屏的收益/复杂度。
3. **先补 a11y**：Android 的 `uiautomator dump` 顺手把 `mode=tree` / `act element` 通路验证掉（Linux a11y 本会话仍未做）。
4. **环境固化脚本**：把 212 `Xvfb+openbox+应用`、Windows `screen` 供给、Android 前置条件各收成一条 bootstrap。

## 环境与命令速查

- **本机**：`DISPLAY=:0`，`XAUTHORITY=/run/user/1000/gdm/Xauthority`；Xorg 在 vt2、`gnome-xorg`、GDM 自动登录 zhengyp。
  sudo：`cat ~/.secrets/centos.key | sudo -S -p '' <cmd>`（**绝不要把 `< file` 放在管道末尾**，见 `checkpoint-3.md` §七）。
- **212**：`ssh zhengyp@192.168.1.212` 免密；`xvfb99.service` + openbox；`DISPLAY=:99`；sudo 需密码。**本会话末已 `No route to host`，先确认开机。**
- **Windows `192.168.1.112`（Surface，Win11）**：
  - SSH：`ssh screen@192.168.1.112`（免密；非管理员账户 `screen`）。
  - daemon：`screen` 登录时由启动项拉起，`pythonw` 监听 `127.0.0.1:9911`，日志 `C:\Users\screen.TABLET-BBT8EQB4\screenlab\daemon.log`。
  - 本机隧道：`ssh -N -L 9911:127.0.0.1:9911 screen@192.168.1.112`；客户端 `--tcp 127.0.0.1:9911`。
  - 若 daemon 没起来：让 YZ 在该账户会话里跑 `C:\Users\screen.TABLET-BBT8EQB4\screenlab\restart_daemon.cmd`。
- **原型**：`work/A/checkpoint/screen-lab/`（README 有完整用法；Windows 启动器 `daemon.pyw`）。
- **无 `adb`/`scrcpy`**：本机与 212 都没有，Android 线第一步是装。

## 关键引用

- 设计稿：`spec-screen-1.md`（§5.7 = Windows 约束；§9 = 原型与验收）。
- 本会话实测与系统改动：`checkpoint-4.md`。
- 上游实测：`checkpoint-3.md`（X11 三段根因 / Wayland 两通路 / 安全事件 / 系统改动 / 命令备忘）。
- 讨论：`handoff-screen-01.md`（工具分域 / 协议 screen/1 / 客户端形态 / 行业现状 / 阶段划分）。
- 原型：`screen-lab/`（`backends.py` X11、`backends_win.py` Windows、`platform_backends.py`、`daemon.py`、`cli.py`）。
- 分册口径：`cogos/docs/design-agent-tools.md` §5.4 / §6 / §12；`cogos/docs/vision-system-design.md` §14 / §168–170。
- 代码面：`app.py:192` `_build_specs`；`tools.py:1131` `ToolRegistry`；`config.py:99` `render_system_prompt`；`consciousness.py:68` `schemas`；`image_ctx/tools.py:122` `see`。

## 纪律

- 跑测试用 `python3.11 -m pytest`（系统 `python` 是 3.9）。
- 结论先落 `checkpoint-4.md` / `spec-screen-1.md`，定案再更新权威分册 `design-agent-tools.md`。
- 不替 agent 决定用法；发现设计问题回 checkpoint 记，不悄悄改设计。
- 密码类只经文件与 `SSH_ASKPASS`，绝不落进命令行或工具输出（`act type` 已只回 `text_length`）。
