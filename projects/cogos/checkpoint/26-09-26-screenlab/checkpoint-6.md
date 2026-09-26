# checkpoint-6｜P4 Windows 外壳：形态与持久化决议（2026-09-20）

> 性质：**讨论 + 只读真机探针**。P4 设计决议定案；未落 Windows 代码（仅提交 08 遗留的 X auth 修复）。
> 入口：`handoff-screen-08.md` → 本会话。上游：`checkpoint-5.md` §九/§十、`spec-screen-1.md`、`handoff-screen-07.md`。
> 承接：08 的待裁决 1–11 逐条裁决，本文件记定案。

## 一、本会话做了什么

1. 承接 **P4（Windows 外壳）**：把 Windows 从"手工原型已通"推到与 Linux P1 对等的可安装 / 会话内自启 / 远程可连。
2. 提交并推送 08 遗留的 **X auth 修复**（3 文件）。
3. 只读探针 Surface：auto-logon / 会话 / daemon / Python 运行时。
4. 逐条裁决 P4 所需设计项（本文核心）。

## 二、Surface 只读探针（`screen@192.168.1.112`）

- `HKLM\...\Winlogon`：`AutoAdminLogon=1`、`DefaultUserName=screen` → 自动登录已配。
- `explorer.exe` 在跑（PID 5516）→ **已自动进 screen 交互桌面，零人工**。
- `HKCU\Control Panel\Desktop`：`ScreenSaveActive=0`（屏保已关）。
- 无 python/pythonw 进程 → **daemon 未运行**（原型自启未兜住，与 08 盘点一致）。
- Python：`C:\Program Files\Python311\python.exe`（3.11.5）+ `py.exe`。
- 原型 `%USERPROFILE%\screenlab\`：`daemon.pyw`、`restart_daemon.cmd`、`blobs/`、`daemon.log`、`screenlab/`、`_selftest.py`；**无 venv**（裸用系统 Python）。

## 三、P4 决议

### 1. 分支 / 基线

- 新分支 **`feat/screenlab-p2`**（从 `feat/screenlab-p1` 拉出）。
- X auth 修复提交 `16b8b36`（`fix(screenlab): enforce X auth on the headless Xvfb display`），已推送 origin。
- P4 在本分支继续。

### 2. 形态模型：授权轴 × 持久轴（拆开，不塞一个枚举）

- **授权轴** `authority ∈ {owned, granted}`（已有；装配期注入）：谁拥有这台机 / 这个桌面。
- **持久轴（新）** 装配形态 `dedicated | shared`：重启是否自愈、是否 auto-logon、覆盖范围。
  - `dedicated`：agent 占整机；重启后无人工继续可用。
  - `shared`：借人当前会话；随会话起停。
- 二者相关但不等价（owned 可不覆盖登录前；不得因 owned 默认背 UIAccess）。

### 3. auto-logon 语义

- auto-logon 只在**开机 / 重启**生效 → 是**装配期持久状态**，不是运行开关。
- 不跨重启：不需要它（登录一次会话即常驻）。
- 长期无人值守（`dedicated`）：auto-logon **常开**，是机器形态。
- 一次性无人值守：走**临时装配 + 收尾卸载**生命周期，不手工开 / 关注册表（凭据落盘不可逆、可能来不及收尾）。
- Linux 对照：`dedicated` ≈ system 模式 + 专用账户 + 独立 Xvfb（已实现）；`shared` ≈ user 模式 + 借人的 `:0`（granted）。

### 4. 自启外壳

- `dedicated`：**计划任务 AtLogOn**（交互会话内起、可配失败重拉、可观测）。弃 Startup `.vbs`（无重拉、不可观测）；不用 SYSTEM 服务 + 会话代理（Session 0 无桌面、成本高）。
- `shared`：随会话，不需开机自启。

### 5. Python 运行时

- **venv**（基于系统 Python 3.11），建在用户目录 → 无需管理员；与 Linux `install.sh` 的 venv 对齐。
- 装配器前置检查系统 Python；缺失则提示 / 退回嵌入式 Python。
- 修点：原型裸用系统 Python，P4 须收进 venv（否则"干净卸载"不成立）。

### 6. 端点与运输

- 端口**装配期确定**（探测空闲 / 指定）→ **写服务端配置持久化**（重启 daemon 复用同端口，否则客户端 endpoint 失效）。
- 客户端 `agent.json`：`computer.graphics.endpoint = tcp:127.0.0.1:<port>`。
- 本地端口由客户端 `_open_tunnel_tcp` 自选（`graphics.py:173-179`），不配置、不冲突。
- 运输 `ssh -L local:127.0.0.1:port`（Windows OpenSSH 不支持 AF_UNIX 转发）；**客户端 / 协议零改动**。

### 7. loopback 认证

- **P4 先不加 token**。前提 = `dedicated` / 单用户 / 可信本机。
- 翻案条件：机器不再单用户，或要正式支持 `granted` 撤销 / `stop`（与 P3 同源）。
- 记 ISSUES。

### 8. 验收判据（Windows，对齐 P1 七条）

1. 一次装配（`install.ps1` 末行打印 `SCREENLAB_ENDPOINT=tcp:127.0.0.1:<port>`）。
2. 真 `reboot` 后自启、无人工、agent 自动连。
3. 真 `capture → act → capture` 见预期变化。
4. 过期帧被拒 + `since_hash` 命中回 `changed:false`。
5. 干净卸载（计划任务 / auto-logon / 目录 / venv 无残留）。
6. wire（`screen/1`）形状未变。
7. 等价判据：**锁屏后失联 = 已知边界、不算失败**（与 Linux Wayland greeter 对称）。

### 9. P4 范围外（明确不做）

- **档二**：UIAccess / SYSTEM 服务 / 登录前 / 锁屏后控制 → 未实现、默认关；未来做需代码签名 + 受信安装位置 + 明示同意。
- **RDP**：若要覆盖登录前，作为替代路线评估（注意开的是 RDP 会话、非物理控制台）。

## 四、开工待办（P4）

1. 诊断现有 Startup `.vbs` 为何没拉起 daemon（看 `daemon.log`）。
2. 真机复验 `backends_win.py`。
3. 写 Windows 装配器：venv + 端口配置持久化 + 计划任务 AtLogOn +（dedicated）auto-logon / 禁屏保锁屏。
4. Surface 真机跑七条验收。
5. 定案后回写权威分册 `cogos/docs/design-agent-tools.md`。

## 五、遗留

安全组 4 条已并入 `cogos` ISSUES（loopback 无认证 / autologon 凭据托管 / 档二未实现 / granted 撤销未实现），均带前提与翻案条件。

## 六、关键引用

- 实测：`checkpoint-5.md` §九/§十、`handoff-screen-08.md`（现状盘点）、`spec-screen-1.md` §5.7（Windows 约束）。
- 客户端：`cogos/agent/impl/graphics.py`（`tcp:` + `ssh -L`、`_open_tunnel_tcp`）、`cogos/agent/config.py:51/74`（token 预留）。
- 服务：`cogos/screenlab/service/backends_win.py`、`service/daemon.py:405`（`serve_tcp`）、`install/`（仅 Linux）。
- 权威分册：`cogos/docs/design-agent-tools.md`（待回写）。

## 七、P4 落地与真机验收（2026-09-20 补，本会话）

**新增/改动（`feat/screenlab-p2`，未提交）**

- `screenlab/install/install.ps1`：Windows 装配器（venv + Pillow、config.json、计划任务、末行 `SCREENLAB_ENDPOINT=`）。
- `screenlab/install/uninstall.ps1`：停任务/进程、删 Startup 项与安装目录。
- `screenlab/service/launch.py`：无窗口 headless 入口（pythonw 下重定向日志、崩溃重拉）。
- `screenlab/service/cli.py`：修正 `--tcp` 示例（顶层参数，须在子命令前）。

**关键实现决策 / 发现**

- **ssh（Session 0）下 `schtasks` 被拒、CIM/WMI 不可用** → 改用 **Task Scheduler COM API**（`Schedule.Service`）注册/启动任务。
- 任务 Action = `venv\Scripts\pythonw.exe -m screenlab.service.launch`：**无控制台窗口**，任务实例常驻 → `DeleteTask` 能回收进程树，卸载干净。
- 端口**装配期探测**写入 `config.json`；`launch.py` 读它。auto-logon 是 HKLM 前提，install 不碰（需管理员）。
- **Windows Startup 文件夹的 `.cmd` 未被登录执行**（原因未定）→ 弃用 Startup，改计划任务。

**真机验收（Surface `192.168.1.112`，dedicated，末次端口 `60776`）**

1. 一次装配 ✓（末行打印 endpoint）
2. 重启自启 ✓（用 `act` 注入 `Win+X → U → R` 触发重启；自动登录后任务无人工起 daemon）
3. agent 自动连 ✓（cogos `ScreenChannel` 自动 `ssh -L` + `capture`）
4. 过期帧拒 ✓（同连接二次 `act` → `stale_snapshot`）
5. 干净卸载 ✓（task / 进程 / 目录 / Startup 全清）
6. wire 不变 ✓
7. 闭环 ✓（Pillow 抓屏 + SendInput；`super` 键开出开始菜单）

**坑（新增）**

- `--tcp` 是 cli **顶层**参数，须在 `daemon` 子命令前。
- PowerShell `$Args` 是**自动变量**，作函数参数名会静默失败（Action.Arguments 为空 → pythonw 无参即退）。
- ssh 会话 `taskkill /im` 失效（走 WMI）；`Stop-Process -Id` 可用（跨会话可杀同用户进程）。
- **VM↔Surface 链路带宽低**：1.8MB `scp` 超时 60s；`capture` 需 `max_dim` 降采样或容忍长时延。
- Surface 上 `screenlab/`（旧原型）仍在 home；`screenlab-p4` 复验目录已清。

**下一步**：回写权威分册 `cogos/docs/design-agent-tools.md`；P4 代码待提交/推送。
