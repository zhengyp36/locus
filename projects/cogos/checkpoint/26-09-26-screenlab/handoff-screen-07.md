# handoff｜P4 Windows 外壳：讨论怎么实现 · 2026-09-20 #7

> **新会话任务**：**讨论 Windows 上的"类似功能"怎么实现**——即 Phase 2 阶梯的 **P4「Windows 外壳」**：把 Windows 从"手工原型已通"推进到与 Linux P1 对等的**可安装、会话内自启、远程可连**的图形服务。**不是**继续写 Linux、**不是**做 Android。产出以**设计/决议**为主（Windows 装配与自启外壳怎么落），必要时少量落码验证。
> **交接语**：读本文件即可开会话；细节读 `checkpoint-4.md` §三（Windows 实测）、`spec-screen-1.md` §5.7、`handoff-screen-06.md`（P1 现状）。
> **前序**：`handoff-screen-05.md`（协议冻结 + P1 决议）→ `handoff-screen-06.md`（P1 落码 + 双机验收）→ 本文件。

## 本会话性质

**讨论**（承接 P1 完成）。目标：定 Windows 的实现形态与验收口径。

> P1 分支 `feat/screenlab-p1` **未合并 master、未建 PR**（见 `handoff-screen-06.md` §待裁决）。本会话要顺带定：Windows 工作基于 **合并后的 master** 还是 **同一条分支**。

## 已定（可当既定，不要重开）

**Windows 实测定案**（`checkpoint-4.md` §三 / `spec-screen-1.md` §5.7）

- **Session 0 无桌面**：`sshd` 在 Session 0，那里抓屏直接失败、`GetCursorPos`/`GetForegroundWindow` 为空 → 图形服务**必须由启动项在目标用户的交互会话里拉起**。
- **专用标准账户**（非管理员）占交互会话；**必须属于 `Users` 组**，否则登录界面不列该账户（SSH 不受影响，易误判为"账户不存在"）。
- **必须开 per-monitor DPI 感知**：不开时 `GetSystemMetrics`/`GetCursorPos` 给逻辑像素而 GDI `all_screens` 给物理像素（150% 下差 1.5×）。修法：进程启动即 `SetProcessDpiAwarenessContext(PER_MONITOR_AWARE_V2)`。
- **传输走 loopback TCP**：Windows OpenSSH **不支持 AF_UNIX 端口转发**，故服务监听 `127.0.0.1:<port>`，本机 `ssh -L` 转出。
- **注入 = `SendInput`（ctypes，无第三方依赖）**，`type` 走 `KEYEVENTF_UNICODE`（任意 Unicode）；抓屏 = Pillow `ImageGrab.grab(all_screens=True)`（GDI）。
- 已实测闭环（原型）：点开始按钮 → `Win+R` 起 notepad → 打字 75 字符成功。

**协议与客户端（已冻结/已落，Windows 直接复用）**

- `screen/1` 已定稿，**wire 不动**（`checkpoint-5.md` §九 / `spec-screen-1.md` §1）。
- `ScreenChannel` 已支持 `tcp:host:port` 端点 + **`ssh -L` TCP 隧道**（`cogos/agent/impl/graphics.py:172` `_open_tunnel_tcp`）；运输由 `agent.json` 的 `graphics.endpoint` 推。
- 工具 `screen_capture` / `screen_act` 与平台无关。
- 代码落点：`cogos/screenlab`（`proto` + `service`），**禁止 import cogos**；`cogos` 侧只 import `screenlab.proto`。

## 现状盘点（代码 + 机器）

**机器：Surface `192.168.1.112`**

- 账户 `screen`（非管理员、`Users` 组）；`ssh screen@192.168.1.112` **key 免密可用**（本机 `~/.ssh/id_ed25519`）。
- 自动登录已配：`HKLM\...\Winlogon` `AutoAdminLogon=1`、`DefaultUserName=screen`。
- 原型装在 `C:\Users\screen.TABLET-BBT8EQB4\screenlab\`（`daemon.pyw` / `restart_daemon.cmd` / `blobs\` / `daemon.log`）；启动项 `…\Startup\screenlab_daemon.vbs` → `C:\Program Files\Python311\pythonw.exe daemon.pyw`。
- **当前 daemon 未运行**：`netstat -an | findstr 9911` 无监听（`daemon.log` 最后一条 listening 停在 11:40）。`quser`/`qwinsta` 在该 ssh 会话里不可用，**是否已自动登录、启动项是否失败未确认**——下会话第一件事先诊断。

**cogos 侧（P1 带入的 Windows 资产）**

- `screenlab/service/backends_win.py` 已存在（Pillow 抓屏 + SendInput + DPI 感知 + `active_window`/`pointer_pos`/`list_displays`），**未在 Windows 真机复验**（原型期验的是旧扁平版 `screenlab/`）。
- `screenlab/service/platform_backends.py` 已支持 `backend="win32"`。
- **`screenlab/install/` 只有 Linux**（systemd units + `install.sh`/`uninstall.sh`），**无 Windows 外壳**——这正是 P4 要补的。

**旧原型（临时件，非 cogos 形态）**：`work/A/checkpoint/screen-lab/`（`daemon.pyw` / `restart_daemon.cmd`）。

## 待讨论/裁决（本会话要定的）

1. **账户/会话模型**：继续"专用标准账户 + 自动登录"？还是占当前用户会话？自动登录把密码明文写进注册表的风险怎么收敛。
2. **自启外壳形态**：Startup 文件夹 `.vbs`（现用） vs **计划任务**（AtLogOn/AtStartup） vs Windows 服务 + 会话代理；谁负责重启后恢复、进程掉了重拉。
3. **装配器**：`install.ps1` / `.cmd` / python——与 Linux `install.sh` **对齐**：一次执行、末行打印 `SCREENLAB_ENDPOINT=...`；`uninstall` 对等。
4. **打包**：venv（Linux 走 `--system-site-packages`） vs Windows 嵌入式 Python vs PyInstaller；Pillow 依赖、GBK 控制台/路径编码。
5. **端点与运输**：`tcp:127.0.0.1:<port>` 固定 vs 动态；`ssh -L`（客户端已支持 tcp 隧道）；`agent.json` 里 `graphics.endpoint` 与 `authority`/`grant` 取值。
6. **认证**：Windows loopback TCP **任何本地进程都能连** → 是否加本地 token；与 P3（granted 的 `stop`）的关系；装配期认证来源（借 sshd）。
7. **多显示器 / DPI 上报**：`all_screens` 多屏原点（`SM_*VIRTUALSCREEN`）、`scale`/`rotation` 是否要补齐到 `displays`。
8. **验收判据**：对齐 P1 的 **1–7**（一次装配 / 重启自启 / agent 自动连 / 真 `capture→act→capture` 见变化 / 过期拒 + `since_hash` 去重 / 干净卸载 / wire 不变），在 Surface 真机跑；并给 P1 未做的"人工登出"在 Windows 上定等价判据（锁屏 / Winlogon / UAC）。
9. **顺序**：先做 P4，还是先补 P2（断连即终态）/ P3（grant 的 `stop`）？（阶梯见 `checkpoint-5.md` §九）

## 已知坑（照抄，别重踩）

- Session 0 无桌面 → 服务必须在交互会话内。
- 标准账户不自动进 `Users` 组 → 登录界面不列该账户。
- 不开 DPI 感知 → 逻辑/物理像素差（150% = 1.5×）。
- Windows OpenSSH **不支持 AF_UNIX 转发** → 必须 TCP。
- 中文字符串经 ssh（GBK 控制台）乱码（显示问题、不影响功能）。
- **UAC / Secure Desktop**：`SendInput` 受 UIPI 限制，提权窗口、登录/锁屏界面够不着（**待验证并记录**）——对应 Linux 的"登出后 Wayland greeter 够不着"。

## 环境与命令速查

- **Surface**：`ssh screen@192.168.1.112`（key 免密）；密码在 `/tmp/kilo/screen.win.pw`（**临时文件，重启可能已丢**）；原型目录 `C:\Users\screen.TABLET-BBT8EQB4\screenlab\`；启动项 `…\Startup\screenlab_daemon.vbs`。
- **本机隧道**：`ssh -N -L <local>:127.0.0.1:9911 screen@192.168.1.112`；客户端端点 `tcp:127.0.0.1:9911`。
- **诊断（下会话第一步）**：`netstat -an | findstr 9911`；看 `...\screenlab\daemon.log`；确认是否已自动登录（需可用的 `quser`/`qwinsta`）。
- **cogos**：`/home/zhengyp/work/A/cogos`；分支 `feat/screenlab-p1`；测试 `python3.11 -m pytest tests/ -q`。
- **212**：`ssh zhengyp@192.168.1.212`（当前可达）；本会话与 Windows 无关，仅备忘。

## 关键引用

- 实测：`checkpoint-4.md` §三（Windows 打通）、§五（系统改动清单）、`spec-screen-1.md` §5.7（Windows 特有约束）。
- 阶梯/形态：`checkpoint-5.md` §九（P4 Windows 外壳）、§八（图形服务借 ssh 装配/运输）。
- P1 现状：`handoff-screen-06.md`（落码 + 双机验收 + 待裁决）。
- 客户端：`cogos/agent/impl/graphics.py`（`tcp:` + `ssh -L`）、`cogos/agent/tools.py::make_screen_specs`。
- 服务：`cogos/screenlab/service/backends_win.py`、`platform_backends.py`（`backend="win32"`）、`screenlab/install/`（**仅 Linux**）。
- 旧原型：`work/A/checkpoint/screen-lab/`（`daemon.pyw` / `restart_daemon.cmd` / `README.md`）。
- 凭证/配置：`design-secrets.md` §5（`computer` 块）。

## 纪律

- 跑测试用 `python3.11 -m pytest`；结论先落 checkpoint/spec，定案再回写权威分册 `cogos/docs/design-agent-tools.md`。
- 目标侧叫"**服务**"不叫 agent；**认证不在协议里**；`screenlab/` **禁止 import cogos**；`screen_capture`/`screen_act` 是 agent 面。
- 密码类只经文件与 `SSH_ASKPASS`，绝不落进命令行或工具输出。
