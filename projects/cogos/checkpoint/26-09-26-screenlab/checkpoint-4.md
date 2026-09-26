# checkpoint-4｜图形面：Linux/X11 落码 + Windows 打通 + 最小原型（2026-09-20 #3）

> 性质：**讨论 + 实测 + 落码**。本会话新建了设计稿与原型，并**改了 Windows 机器的系统配置**（见 §五，可回退）。
> 入口：`handoff-screen-02.md` → 本会话 → 后续入口 `handoff-screen-03.md`。
> 上游实测：`checkpoint-3.md`（X11 三段根因 / Wayland 两通路 / 安全事件）。

## 一、本会话做了什么

一句话：把 `screen/1` 从"两台机上的手工闭包"变成**三平台、有设计稿、有最小 daemon+CLI 的原型**。

1. 回写设计：新建 `spec-screen-1.md`（协议 + 客户端 + 平台 + 验收 + 运行时约束）。
2. 落最小原型 `screen-lab/`（daemon + client + CLI，1082 行），三环境 LLM 在环验收。
3. 本机 `:0` 从锁屏解锁（YZ 授权）后跑通闭环。
4. Windows Surface `192.168.1.112` 打通（新线，见 §三）。
5. 途中修掉 Windows DPI 坐标错位（设计级）。

## 二、本机 `:0`（Linux/X11）

- 会话处 GNOME 锁屏 → 用 daemon 的 `act type` + `Return` 输入 `~/.secrets/centos.key` 解开（`type` 的响应只回 `text_length`，密码不进工具输出）。
- 闭环：`see` → `act pointer` 点顶栏时钟 → `see`（日历/通知面板）→ `act key Escape` → `see`（面板关，`frame_hash` 回到点击前值）。
- 随后 `act key super+l` 锁屏，`see` 的 `frame_hash` 与会话最初锁屏时**完全一致**（内容寻址可复现）。

## 三、Windows Surface `192.168.1.112`（新线，已通）

### 3.1 形态（YZ 选 A：专用标准账户占交互会话）

1. 建**非管理员**账户 `screen`；装 SSH 公钥；加 `Users` 组。
2. 代码放 `C:\Users\screen.TABLET-BBT8EQB4\screenlab\`（`daemon.pyw` + `screenlab\` 包）。
3. 挂启动项 `...\Startup\screenlab_daemon.vbs` → 该账户登录时在**交互会话**拉起 `pythonw`，监听 `127.0.0.1:9911`。
4. 本机 `ssh -N -L 9911:127.0.0.1:9911 screen@192.168.1.112` → 客户端 `--tcp 127.0.0.1:9911`。

### 3.2 实测约束（设计级，已进 `spec-screen-1.md` §5.7）

- **Session 0 无桌面**：`sshd` 在 Session 0，那里 `see` 直接 `screen grab failed`、`GetCursorPos`/`GetForegroundWindow` 为空 → daemon 必须由启动项在交互会话里拉起。
- **必须开 per-monitor DPI 感知**：不开时 `GetSystemMetrics`/`GetCursorPos` 给逻辑像素（1280×853），GDI `all_screens` 抓屏给物理像素（1920×1280），150% 下**图像坐标 ×1.5 ≠ 落点**。实测：要求移到 `(200,200)`，光标实际在物理 `(300,300)`。修法 `SetProcessDpiAwarenessContext(PER_MONITOR_AWARE_V2)`；修后 `displays` 报 1920×1280、点击精确命中。
- **传输走 loopback TCP**：Windows OpenSSH **不支持 AF_UNIX 端口转发**。
- **标准账户必须属于 `Users` 组**：`New-LocalUser` 不自动加组；不在 `Users` 就没有"允许本地登录"权 → **登录界面根本不列该账户**（SSH 不受影响，容易误判为"账户不存在"）。
- 注入 = `SendInput`（ctypes，无第三方依赖）；`type` 走 `KEYEVENTF_UNICODE`（任意 Unicode）；抓屏 = Pillow `ImageGrab.grab(all_screens=True)`。
- 闭环验证：点开始按钮（图像坐标 `618,1258`）弹菜单 → `Win+R` 起 notepad → 打字 75 字符成功。

### 3.3 其他观察

- `192.168.1.112` 是 **Microsoft Surface 平板**（进程表有 SurfaceService 等），**当时没有 VirtualBox 在跑**——早前"它=本 VM 宿主"的说法存疑（本会话据此解除"注销会杀本机 VM"的顾虑，但未求证）。
- daemon 重启是**借它自己**完成的：`act` 开 Win+R → 跑 `restart_daemon.cmd` → `taskkill pythonw` + 重新 `start`（同会话内），不需要注销。

## 四、原型（`work/A/checkpoint/screen-lab/`）

- `framing.py`（JSON 行 + 二进制尾）、`backends.py`（X11：Pillow/ImageMagick + xdotool）、`backends_win.py`（Windows：GDI Pillow + SendInput + DPI 感知）、`platform_backends.py`（按平台选）、`daemon.py`（Unix socket / **TCP**）、`client.py`、`cli.py`、`daemon.pyw`（Windows 启动器）。
- 行为：快照世代 `snapshot_id`（`act` 必须绑最新一代，过期拒）、`since_hash` 未变短路、内容寻址 blob 去重、`wait_stable` 静默等待、不推事件。
- **新观察**：`act` 完成时即时抓的帧**可能早于 UI 渲染**（`Escape` 后 `act` 回的帧哈希仍是面板打开态，`see --wait-stable` 才拿到关闭态）→ `act` 的返回世代只当提示。
- **安全**：`act type` 响应只回 `text_length`、不回文本。
- 未实现：`mode=tree` / `act element`（a11y），窗口级抓屏，多显示器枚举（`all_screens` 已覆盖抓取）。

## 五、系统改动清单（可回退）

**Windows `192.168.1.112`**
- 新建本地账户 `screen`（非管理员），加入 `Users`；SSH 公钥在 `C:\Users\screen.TABLET-BBT8EQB4\.ssh\authorized_keys`。
- 装 Pillow（user-scope，`python -m pip install --user pillow`）。
- `C:\Users\screen.TABLET-BBT8EQB4\screenlab\`（原型 + `daemon.pyw` + `restart_daemon.cmd` + `blobs\` + `daemon.log`）。
- 启动项 `…\Startup\screenlab_daemon.vbs`；`HKCU\Control Panel\Desktop` 屏保关。
- `net user screen /passwordreq:yes`（管理员，修 `New-LocalUser` 留下的 `PasswordRequired=False`）。
- 账户标志/组由 YZ 在管理员 PowerShell 执行；系统更新 + 重启后自动进入 `screen`。

**本机**
- 仅临时文件：`/tmp/kilo/screen-lab/`、`/tmp/kilo/win-deploy/`、`/tmp/kilo/screen.win.pw`（`screen` 账户密码，600）。无系统级改动。

## 六、遗留与风险

- **`screen` 账户密码** `Screen-Lab-1!` 明文写在 `/tmp/kilo/screen.win.pw`；自动登录（若启用）会把密码明文写进注册表。要不要收敛由 YZ 定。
- `screen` 账户目前可被局域网密码登录（`sshd` 默认 `PasswordAuthentication yes` + 防火墙放行）——安全暴露面见 `checkpoint-3.md` §七。
- 212 本会话末已 **`No route to host`**（可能关机/网络变化），Android 线要注意先确认机器状态。
- 本机与 212 均**无 `adb` / `scrcpy`**（未装）。
- 代码落点仍未定（裁决 7）；裁决 1–3、5、6、9、10 均未动。

> 纪律：跑测试用 `python3.11 -m pytest`；结论先落 checkpoint / spec，定案再更新权威分册 `cogos/docs/design-agent-tools.md`。
