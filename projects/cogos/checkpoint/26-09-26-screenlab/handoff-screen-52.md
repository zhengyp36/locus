# handoff｜交接给新会话 · 2026-09-25 #52

> 接 #50 / #51。本会话 = 开 **Windows 上的关系 3a**（Goal 3 扩展：在真人的 Windows 机上进行协助）。做到 W1 部署、卡住而停。
> **规则/环境不在本文件**——先读 `screenlab-rules.md`。
> **下一会话：修 W1 两个失败 → 跑通 Windows 机制链。**

---

## 复制这段作为新会话的第一句

```
先按序读，再动手：
0. ../checkpoint/tools/README.md（环境事实 + 固化脚本；`source tools/env.sh`，`tools/snapshot.sh` 一条命令拿状态）
1. ../checkpoint/screenlab-rules.md（规则，先读）
2. ../checkpoint/screen-assist-status.md —— §0 + §4（本会话新增 Windows 段落）+ §5
3. ../checkpoint/codebase.md（代码认知基线）
4. ../checkpoint/handoff-screen-52.md（本文件）

状态：#51 已闭合 Linux 关系 3a（tag `screenlab-goal2-3a-2026-09-25`）。本会话新开 **Windows 关系 3a**；
工作树 **DIRTY**（9 个改动未提交，见下）；**W1 未通**（install.ps1 两处失败）。
靶机新增：Windows 真机 `ssh assist@100.112.50.115` 免密可用。
```

---

## 本会话做了什么

把**关系 3a 从 Linux 扩到 Windows**（目标 §0.0 关系 3a：真人在自己 Windows 机上操作、agent 接入、人可随时拿回）。

- **W0 侦察**（Windows 真机 `tablet-bbt8eqb4` / `100.112.50.115`）：Windows 11 build 26200；Python 3.11.5（机器级，自带 PIL + cryptography）；**无 `socket.AF_UNIX`**；ssh 进的 Session 0（抓到的 1024×768 / DPI 96 不是交互会话真屏）。

## 从目标做的裁决（沿用，可推翻）

1. **账户 = 新建标准账户 `assist`**（隔离、可逆、与已定 Windows 形态"专用非管理员账户"一致；主账户只在反检"真实身份"层需要，本轮冻结）。
2. **传输 = loopback TCP + `ssh -L`**（免管理员）；tailnet 直连要防火墙规则，后置。
3. **不加新依赖**：presence/托盘用 `ctypes`，弹窗用 `MessageBoxW`。
4. **拿回走物理钩子**（`INJECTED` 标志分源），托盘点击只作 fallback。
5. **本轮只做 Windows / 关系 3a**；Wayland、macOS/Android、反检人类化 **不做**。

## 代码改动（cogos，**未提交**）

- `M screenlab/auth/consent.py` — consent 传输支持 `tcp:HOST:PORT`；`consent.addr` 发布/读取。
- `M screenlab/service/daemon.py` — `_start_presence` 按平台选；Windows 默认 consent `tcp:127.0.0.1:<port+1>`；写 `consent.addr`。
- `M screenlab/service/cli.py`、`M screenlab/service/consent_app.py` — 统一 `connect_socket` / `read_consent_addr`。
- `M screenlab/service/launch.py` — 透传 `auth/consent/consent_socket/presence`。
- `M screenlab/install/install.ps1` — 新增 `-BindHost/-Auth/-Consent/-ConsentSocket/-Presence`；venv 加 `cryptography`；改 `--system-site-packages`。
- `?? screenlab/service/presence_win.py` — 低层钩子 `WH_KEYBOARD_LL`/`WH_MOUSE_LL`，`INJECTED` 分源 + `Ctrl+Alt+Shift+Esc` 收回。
- `?? screenlab/service/consent_app_win.py` — 原生托盘（`Shell_NotifyIconW`）+ `MessageBoxW` 编号同意 + 单实例 mutex + 管理 daemon 起停。
- `?? tests/screenlab/test_consent_transport.py` — tcp / unix / addr 文件 3 例。
- **验证**：Linux `pytest tests/screenlab --ignore=tests/screenlab/e2e` = **21 passed**；Windows 模块 `py_compile` OK（**未在 Windows 运行过**）。
- 另有 `checkpoint/win-assist-setup.md`（建账户/免密 ssh 步骤）。

## 靶机侧现状（Windows `100.112.50.115`）

- 账户 `assist`：**标准（Users 组）、启用、已登录过**。
- **免密 ssh 通**：已写 `C:\Users\assist\.ssh\authorized_keys`（含 `id_ed25519` + `id_rsa` 两把公钥）。
- 包已投：`C:\Users\assist\sl\screenlab`（暂存）。
- `%LOCALAPPDATA%\screenlab` 含 `blobs/ screenlab/ venv/`（**venv 坏**）。
- **未起 daemon、未建任务、`registry.json` 未写**。

## W1 未通的两个失败

1. **venv 报 `No pyvenv.cfg file`**：残留坏 venv（`Scripts\python.exe` 在）→ `Test-Path` 判为已存在 → 跳过创建 → pip 失败。
   修法：删整个 `%LOCALAPPDATA%\screenlab` 再装；或将 venv 改为 `--system-site-packages` 重建（已改脚本，利用机器自带 PIL/cryptography，免联网）。
2. **注册计划任务 `E_ACCESSDENIED`**：非管理员从 ssh Session 0 建计划任务被拒。
   修法（从目标）：3a 是"开一个程序"模型 → **不建任务**，daemon 由托盘入口拉起（`consent_app_win --manage-daemon`），或先由人在 assist 交互会话手动起一次做 W1。

## 下一步（按此，别发散）

- **W1 机制在 Windows 活**：干净重装（删 `%LOCALAPPDATA%\screenlab` → 跑 `install.ps1`，**不建任务**）→ 写 `registry.json`（agent 公钥 `TsrTNVQgfSeKuFDFxp07O06ji5NKH+Cmc2qwLqOj4cE=`，alias `kilocode`）→ 在 assist **交互会话**里起 daemon（`--auth <regdir> --consent event --presence`，绑 `127.0.0.1:9911`）→ Linux 经 `ssh -L 9911:127.0.0.1:9911` 接入 → 用 `screenlab consent` CLI 应答 → `capture`/`act`，地面真值对照。
- **W2**：`presence_win` 真机验（act 后真鼠标 → `observer`；热键 → `REVOKED/channel_closed`）。
- **W3**：`consent_app_win` 托盘验（无重复实例、弹窗带 `#N (rid)`）。
- **W4**：`install.ps1` 加桌面/开始菜单快捷方式 + 可选自启。
- **W5**：三判据验收 + 提交/tag/回写（待 YZ）。

## 环境与操作（本会话新增）

- **Windows 目标**：`ssh assist@100.112.50.115`（免密，日常操作账户）；`ssh zhengyp@100.112.50.115`（管理员，用于建账户等）。
- assist 前缀 `C:\Users\assist\AppData\Local\screenlab`；registry `C:\Users\assist\.config\screenlab\registry`；端口 9911（screen）/ 9912（consent）。
- Windows 默认 shell = **cmd**；输出 GBK（读时 `tr -d '\r'`，中文可能乱码）；跑脚本用 `powershell -NoProfile -ExecutionPolicy Bypass -File <path>`。
- 建账户/免密步骤见 `checkpoint/win-assist-setup.md`。

## 疑似并发（待核，不据此行动）

本会话 `terminal_list` 里出现过非我创建/非我发出的命令（终端 24/25）。当时判为"并发会话"并飞书告知 YZ；**YZ 说不应有并发会话，可能是终端跨会话复用或长会话错觉**。事实留此供核对，本会话未据此做任何写操作。

## 锚

- 活文档：`screen-assist-status.md`（§0/§4/§5）
- 代码认知：`codebase.md`（版本戳仍 `b3cc333`；本会话 DIRTY）
- 设计：`design-screen-assist.md`；实验：`screen-assist-exp-log.md`
- 目标：`spec-screen-1.md` §0.0
- 上轮：`handoff-screen-50.md`（#51 无文件）
