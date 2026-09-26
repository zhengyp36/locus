# handoff｜P4 Windows 外壳：落码 + 真机打通 · 2026-09-20 #9

> **新会话任务**：P4 Windows 外壳**已落码并真机打通**（install/uninstall + 计划任务自启 + reboot 验收通过）。可接着做的：① 提交未跟踪的 `screenlab/service/launch.py`（本会话最终采用的 pythonw 入口；`4f33ead` 的 install.ps1 已引用它但漏加）；② 定端口策略（现为动态探测）与大图传输带宽问题；③ Windows 验收结论回写权威分册；④ 继续 P2/P3 或 cogos agent 全链路。
> **交接语**：读本文件即可开会话；细节读 `checkpoint-6.md`（P4 决议）、`handoff-screen-08.md`（P4 议题与现状盘点）、`checkpoint-5.md` §九/§十（协议 + P1 决议）。
> **前序**：`handoff-screen-08.md`（P4 讨论）→ 本文件。

## 本会话性质

讨论 + 落码 + 真机验证。产出 Windows 装配器并完成 P4 真机验收（含 reboot 自启、干净卸载）。**Surface 现处于"已 uninstall"状态**（无 daemon、无任务、无目录）。

## 已提交（分支 `feat/screenlab-p2`）

- `16b8b36` `fix(screenlab): enforce X auth on the headless Xvfb display`（08 遗留的 3 文件，本会话提交）
- `4f33ead` `feat(screenlab): add Windows installer and uninstaller`（本会话产出）
- **未跟踪**：`screenlab/service/launch.py` —— **本会话产出**，撰写时被误判为"并发会话产物"而漏提交，见 §遗留。

## 本会话产出

### Windows 装配器（`screenlab/install/`）

- **`install.ps1`**：探测 Python(≥3.11) → 复制包到 `%LOCALAPPDATA%\screenlab\` → 建 venv + `pip install Pillow` → 写 `config.json`（host/port/blob_dir/authority/grant）→ 渲染 `serve.cmd`（shared 模式的手动入口）→ **用 Task Scheduler COM API 注册 AtLogOn 计划任务**（Action = `venv\Scripts\pythonw.exe -m screenlab.service.launch`）→ Start → 末行打印 `SCREENLAB_ENDPOINT=tcp:127.0.0.1:<port>`。参数：`-Mode dedicated|shared`、`-Authority`、`-Port`、`-Python`、`-Prefix`、`-TaskName`。
- **`uninstall.ps1`**：停/删计划任务 → `Stop-Process`（按 Prefix 匹配 venv python）→ 删 Startup 残留 → 删安装目录 → 打印 `SCREENLAB_UNINSTALLED=1`。
- **`cli.py`**：修正 usage 示例——`--tcp` 是**顶层**参数，必须在 `daemon` 子命令**之前**（原示例写反，实测报 `unrecognized arguments`）。

### 设计要点

- **自启载体 = 计划任务 AtLogOn**（interactive token）→ Action = `venv\Scripts\pythonw.exe -m screenlab.service.launch` → `launch.py` 无控制台窗口，重定向 `daemon.log`、loop 重拉 daemon，**任务实例常驻**（进程树可随任务回收）。重拉由 `launch.py` 的 loop 提供。（中途曾试 wscript+`launch.vbs`，因孤儿进程问题弃用，见 §已知坑。）
- **必须先 `Stop(0)` 再 `Run`**：注册后直接 Run 会因僵死实例（state=running）不生效。
- **端口**：装配期探测空闲端口（本次 61886），写入 `config.json`；重装复用（`-Port 0` 时读 config）。`launch.py` 启动时读它。
- **机器级项不在范围内**（auto-logon / 禁锁屏，需管理员）：install.ps1 不碰，只假设已配。

## 真机验证结果（Surface `192.168.1.112`，账户 `screen`）

- **backends_win 复验**：capture（Pillow GDI）1920×1280 ✓；act（SendInput）`key super` 打开开始菜单、截图确认画面变化 ✓。
- **agent 自动连**：cogos `ScreenChannel(endpoint="tcp:127.0.0.1:61886", ssh=...)` 自动建 `ssh -L` 隧道完成 info+capture ✓。
- **协议语义**：同连接内 capture→act 成功；重复用旧 `snapshot_id` → `stale_snapshot` 正确拒绝 ✓。
- **一次装配**：`install.ps1 -Mode dedicated` 输出 `SCREENLAB_ENDPOINT=tcp:127.0.0.1:61886` ✓。
- **重启自启**：用**注入 UI**（`Win+X` → `u` → `r`）触发重启 → auto-logon 进桌面 → 计划任务无人工拉起 daemon（log 新增 `listening pid=12700, tcp 61886`）✓；**无控制台黑窗**（`pythonw` 无窗口）✓。
- **干净卸载**：`uninstall.ps1` → `task removed` / `stopped processes: 1` / `removed` → 复查：目录不存在、无 python 进程、`TASK_GONE`、Startup 空 ✓。
- **未精确复测**：`since_hash` 的 `changed:false`（动态桌面难造静态帧；协议同 Linux 代码，P1 已在 212 验过）。

## 已知坑（本会话新踩，别重踩）

- **ssh 会话下 CIM/WMI 不可用**：`schtasks /create` 报"拒绝访问"，`New-ScheduledTaskAction`/`Get-NetTCPConnection` 报 CIM 断。**但 Task Scheduler 的 COM API（`New-Object -ComObject Schedule.Service`）可用** —— 这是本方案成立的关键。同理 `taskkill /im`（走 WMI）失败，**`Stop-Process -Id` 可用**（可跨会话杀同用户进程）。
- **`screen` 无重启权限**：`shutdown /r`、`Restart-Computer` 均"拒绝访问"。**改用注入 UI**（`Win+X`→`u`→`r`）可重启；注意 act 需先 capture，而大图 capture 受带宽限制（见下），故用 `max_dim` 小图取 `snapshot_id`。
- **链路带宽低**：VM(`10.0.2.15`) ↔ Surface 之间传 1.8MB 会超时（`scp` 同样 >60s），~279KB(640px) 秒回。**capture 大图会"卡"是带宽，不是协议 bug**；必要时降采样或增大 timeout。
- **Startup 文件夹项未被执行**：`%APPDATA%\...\Startup\` 里的 `.vbs`/`.cmd` 在 auto-logon 后**未运行**（无禁用记录，原因未查明）。→ 弃 Startup，改计划任务。
- **计划任务 Run 僵死**：直接 `Run` 不生效（旧实例 state=running），需 `Stop(0)` + sleep + `Run`。
- **wscript 包装留孤儿进程**：中途试过任务 Action = `wscript.exe launch.vbs` → vbs `start` 起 `serve.cmd`；wscript 起完即退，任务实例不留、进程树无人回收，卸载难清。→ 弃用，改 `pythonw -m screenlab.service.launch`（任务实例常驻、可随任务回收）。
- **`--tcp` 顺序**：顶层参数，须在子命令前。
- Windows OpenSSH 不支持 AF_UNIX 转发 → 只能 loopback TCP（沿用 08 结论）。

## 遗留 / 待裁决

1. **`screenlab/service/launch.py`（未跟踪）**：本会话最终采用的 pythonw 入口（读 `config.json`、重定向 `daemon.log`、loop 重拉、**保持任务实例存活**以便干净停止进程树），替代被淘汰的 wscript+`launch.vbs` 方案（后者有孤儿进程问题）。`4f33ead` 的 `install.ps1` 已引用它但当时漏加该文件 → 后续已补提交 `56f186c`。
   > 更正：撰写本文件时误判 `launch.py` 为"另一并发会话产物"（实为同一会话 17:58 写下，见 git log / session 记录）。不存在并发会话。
2. **端口策略（已定，YZ）**：默认固定 `9911`、占用再向上探测。`install.ps1` 优先级 = 显式 `-Port N` > 复用 `config.json` 中仍空闲的端口（重装稳定）> 从 `9911` 起 `Test-PortFree` 递增（至 9911+100）。客户端 endpoint 因此基本恒为 `tcp:127.0.0.1:9911`，可预写 `agent.json`。
3. **大图传输**：capture 全分辨率 1.8MB 在低带宽链路超时；是否在服务/客户端默认降采样、分块传输或压缩，待定。
4. **机器级项**：auto-logon（已外部配好）、禁屏保/锁屏/睡眠 —— install.ps1 不碰（需管理员），dedicated 完整形态需另行处理。
5. **回写权威分册**：Windows 装配细节 + 上述坑 → `cogos/docs/design-agent-tools.md`（定案后）。
6. **Surface 残留**：`~\screenlab-p4\`（投递的测试包 + diag/run/query 等脚本）未清；旧原型 `~\screenlab\` 与 `Startup\screenlab_daemon.vbs.bak` 仍在。
7. **P2/P3**：断连即终态（P2）、granted 的 `stop`（P3）仍未做。

## 环境与命令速查

- **Surface（Windows）**：`ssh screen@192.168.1.112`（key 免密）；系统 Python `C:\Program Files\Python311`；安装点 `%LOCALAPPDATA%\screenlab`；任务名 `screenlab`。
- **装配**：`powershell -ExecutionPolicy Bypass -File <pkg>\install\install.ps1 -Mode dedicated`；卸载 `uninstall.ps1`。
- **隧道**：`ssh -N -L <local>:127.0.0.1:<port> screen@192.168.1.112`。
- **cogos**：`/home/zhengyp/work/A/cogos`，分支 `feat/screenlab-p2`；测试 `python3.11 -m pytest tests/ -q`。
- **本会话临时脚本**：`/tmp/kilo/win-p4/`（launch.cmd / build-task.ps1 / install 测试 / reboot.py / check*.ps1 等）。

## 纪律

- 跑测试用 `python3.11 -m pytest`；结论先落 checkpoint/spec，定案再回写 `cogos/docs/design-agent-tools.md`。
- 目标侧叫"**服务**"不叫 agent；**认证不在协议里**；`screenlab/` 禁止 import cogos。
- 密码类只经文件与 `SSH_ASKPASS`，绝不落进命令行或工具输出。
- **验证重启**：本机（会断会话）不用；Surface 用注入 UI 或人工。
