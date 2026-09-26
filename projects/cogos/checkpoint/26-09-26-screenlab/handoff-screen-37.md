# handoff｜交接给新会话 · 2026-09-24 #37

> 接 #36。本轮**按"怎么使用"重验图形面**（从目标推、对抗性找新问题），**未动码**；共定位 9 个问题（F1–F9 + O1–O5）。
> 上下文 ≈187k/1M（19%）→ 按纪律切会话。

## 给新会话的第一句话

> 先读 **`checkpoint/tmp-screen-usage-verify.md`**（本轮**全部**思路 / 证据 / 问题总表）＋ **`spec-screen-1.md` §0.0`**（**目标，唯一约束**）。
> **下一步顺序（YZ 定）**：①先修**"原因清楚且是纯 bug"**的一批 → ②其余**需决策的先讨论再修** → ③最后才是原因不清 / 非必现的复现分析。
> **判据**：一切从 **目标（§0.0）** 推；**不是 YZ 定、也不是 AI 定**——能推的自决并记录，推不出的才讨论。
> 靶机在跑：`surface-centos-9`（100.100.137.78），账户只剩 **`sva`（uid 1001，`:10` 1600x900）**（密码见 tmp 文件）。
> **临时文件 `tmp-screen-usage-verify.md` 在验证结束、与 YZ 讨论后再删**。

## 规则与纪律（YZ 定，务必沿用）

- **10 分钟闹钟**：动手前 `set_timer`；到点停下做两件事——① 对照 `spec-screen-1.md §0.0` 查是否**偏航**，偏了就拉回；② `python3 /home/zhengyp/work/A/locus/tools/ctx.py` 查上下文，**≥200K 或逼近就交接并通知 YZ**；查完再设下一个。
- **YZ 在场讨论时不用闹钟**（并取消已设的）。
- **每完成一步** → `tools/feishu_notify.py "…"` 通知 YZ，**不等回复，立即下一步**。
- **命令走 `terminal_exec`**（非阻塞，等唤醒），**不用 `sleep` 结束命令**；预计 >5s 的不阻塞等待。
- **遇问题** → 记录（先入 tmp 文件）；可找 YZ 讨论，或上网搜。
- **裁决按目标**：从 §0.0 + 易用性推，能推的**自决并记录**（先例：`--no-sandbox` 与"像真人、不被检测"冲突 → 默认**禁用**，已自决）。
- **不提交**：`../cogos` 含 #36 未提交改动 + 1 处 #35 遗留；tag / commit 由 YZ 定。

## 本轮思路（唯一方法论）

- #34 的"全绿"是**仓库自己的 harness 自证**（`roles_e2e` / `tool_loop_e2e` 都是我们写的）；#35 一"真用"就出问题。
- 故本轮**不用仓库 e2e 当验收**：从 §0.0 出发按"**怎么使用**"列清单，**以 agent 身份、只用文档公开入口**（`screenlab` / `surface` / `view`），对抗性找**新问题**；用 `import` 直抓 X 屏做**地面真值**对照，避免自证。
- 清单分组：A 装配 / B 自操作闭环 / C 生命周期 / D 状态延续 / E 观察面 / 隔离 / G 易用性 / H 痕迹。

## 进展（清单结果）

**通过**：A（从零 `install-machine`；`add-agent` 不预起面 inactive+disabled；目录归属 sva）·
B（`run` 起 chrome；`capture` 与 `import` 同尺寸同内容；`focus`/`close`；`act` ctrl+l→type→Return 后标题变；`clip` set/get 往返）·
C（`close` → target inactive、Xvfb/openbox/X10 全退；`open` 复用 `:10`+分辨率；`--destroy` 后 resolution 保留）·
D（`Default/History` 163840B，命中 `probe`/`example` → 状态真落盘）· E（`view` `/status` read_only / `POST /act` 405；`remove-agent` 清干净）·
隔离（`svb` `:11` 并存；双向 `/run/user/…` Permission denied；`surface windows`=[]）· H（痕迹量测，见下）。

**H 痕迹（1600x900 面上）**：`webgl/webgl2=false`、`dpr=1`、`screen 1600x900`、`webdriver=false`、
`cores=2,mem=2`、`vendor=Google Inc.`、`tz=Asia/Shanghai`、`langs=en-US,en`、窗口 `outer/inner=1050x880/1042x789`、
字体 `fc-list|wc -l = 135`、`Chrome 148.0.7778.96`。**与上一轮 1920x1080 结论一致**（只随分辨率变）。

## 问题清单与状态（详见 tmp 文件「问题总表」）

### 已定位根因（可直接修）
- **F1**：面未起时 `surface` **永久挂死**（无超时 / 无"面是否活着"预检）。根因：`:10` 的 **TCP 6010 被遗留 sshd X11 转发占用**，`/tmp/.X11-unix/X10` 不存在 → libX11 退回 TCP → 连上空壳永不握手。对照 `:99`（无监听）`rc=1` 快速失败。
- **F1b**：`session-start.sh` `alloc_display()` 只查 `/tmp/.X11-unix/XN` 与 `/tmp/.XN-lock`，**不查 TCP 6000+N** → 可能与 sshd X11 转发撞号（Xvfb 默认 `-nolisten tcp`，启动期无感）。
- **F2**：`surface clip` 空剪贴板吐裸 `xclip` 错、`rc=1`（把正常态当错误）。
- **F8**：`surface run` **无条件**报 `{"event":"started"}` 且 `>/dev/null 2>&1` 丢弃子进程输出（实测 `run /nonexistent-cmd-xyz` 照样 `started`）→ 失败零线索。
- **F5**（已自决）：默认**禁用** `--no-sandbox`（否则出现可见黄条 `unsupported command-line flag`）；实测不带也能起。待清仓库/文档残留推荐。
- **空格**：`session.env` 第 4 行前导空格（`session-start.sh` heredoc 缩进遗留，sourcing 可用，cosmetic）。

### 机制清楚、**修法待决策**
- **F6**：`close` 只停 systemd 面，`surface run`（`setsid -f`）起的 GUI 进程**不在 unit 里** → 成孤儿（数秒后随 X 消失自行退，但不保证）。
- **F9**：粗暴关闭（X 消失 / `pkill`）在 profile 留 `Chrome didn't shut down correctly` + `Restore pages?`（人可见 + 弱指纹）。
- **F6 / F7 / F9 同源**：GUI 进程生命周期**完全没被管理**。**F7（残留实例使后续 `run` 不可靠，窗口消失/黑屏/无错）先不单独复现**——很可能随"优雅收敛"一并消失；若修完仍复现再单查。（注：OOM 假设已基本排除：`dmesg`/`messages` 无 OOM，swap 仅用 4M。）

### 不是 bug，是**清账**
- **F4**：`capture` 不返回 `tree`、`act element` 未实现（全仓无 a11y 实现）→ **spec §1 宣称与实现不符**。按 §0.0（a11y 非约束）建议**改 spec 承认"Goal 1 只有像素"**，a11y 记候选，而不是现在补实现。

### 观察（不改码）
O1 窗口不铺满面 且 `capture` 只给整屏 bounds（与 F4 同源）· O2 全新 profile 首次运行气泡遮挡 ·
O3 `tz=Asia/Shanghai` 与 `langs=en-US` 不一致（按"与真人 VBox 齐平"口径**不判偏离**）·
`/status` 的 `focus.window_id` 在窗口关闭后陈旧（`backends.py:356` 调 `xdotool getactivewindow`，是 **openbox 未重置死窗口焦点**，非缓存）。

## 下一步（顺序，YZ 已定）

0. **先补记忆**：更新 locus 的 `projects/cogos/current.md`（本轮印象 = "按'怎么使用'重验，定位 F1–F9"），指向本 handoff 与 tmp 文件。
1. **修"原因清楚且纯 bug"批**：`alloc_display` 避 TCP 号 / `surface` 加超时+存活预检 / `clip` 空剪贴板 / `session.env` 缩进 / grep 清 `--no-sandbox` 残留。修完**靶机重跑相关用例**。
2. **需决策的先讨论再修**：**F8** `run` 可观测性（detach 是否报 pid/退出码）；**F6+F9** `close` 是否**优雅收敛** GUI 进程（先 WM_DELETE / SIGTERM 再退 X）。
3. 之后：**F4** 改 spec 口径；**F7** 只在仍复现时单查。
4. **补验证尾巴**：跨机 `view`（便宜，本轮只测 loopback）；C4「重启不自启」= 静态判断通过（`is-enabled=disabled` + 无 autostart），**不跑重启**（靶机有 dracut 前科）。
5. **收尾**：问题并入 `issue-screen-surface-lifecycle.md`「执行中发现」；写新 handoff；**代码改动不提交**，等 YZ。

## 环境与操作（重要）

- 靶机 `surface-centos-9`（100.100.137.78）；宿主 VBox：`ssh zhengyp@100.112.50.115`（救机：`VBoxManage controlvm centos9 reset`）。
- 靶机 `/opt/screenlab` 已装（**无 `uninstall-machine`**）；账户只剩 `sva`（1001，`:10` 1600x900）；`/tmp/cogos-src` 是源码副本。
- **sudo**：`cat ~/.secrets/centos.key | ssh zhengyp@100.100.137.78 'sudo -S -p "" bash -c "…"'`；
  **多个 root 命令包在一个 `bash -c`**；账户侧 `runuser -u sva -- env HOME=/home/sva …`。
- **部署**：先 `rsync -a --exclude __pycache__ ../cogos/ zhengyp@100.100.137.78:/tmp/cogos-src/`，
  再 `sudo bash /tmp/cogos-src/screenlab/install/screenlab install-machine --prefix /opt/screenlab`。
- **取帧 / act**：`runuser -u sva -- env HOME=/home/sva PYTHONPATH=/opt/screenlab python3 -m screenlab.service.cli --socket /run/user/1001/screenlab.sock capture --out … | act key --keys … --snapshot auto`。
- 本机 `python3` = 3.9（`cogos/feishu/config.py` 用 `X | None` 跑不了），一律用 `/usr/bin/python3.11`。
- **证据**：`/tmp/kilo/verify/{cap,direct,cap2,search,search2,direct2,task,vframe}.png`。
- 已知噪声：sshd X11 转发占 TCP 6010/6011（`zhengyp@pts/0/1`，**别杀**——是交互会话）；`vboxclient.service` 无限重启（与 screenlab 无关）。

## 入口

- **本轮全部（先读）**：`checkpoint/tmp-screen-usage-verify.md`
- 目标（唯一约束）：`spec-screen-1.md` §0.0
- 结论/依据：`issue-screen-surface-lifecycle.md`（C1–C12 + B1–B2；本轮发现待并入「执行中发现」）
- 体系：`design-screen-system.md`；契约：`../cogos/screenlab/install/session-create.md`
- 代码：`../cogos` @ `feat/screenlab-p2`（含 #36 未提交改动 + 1 处 #35 遗留）
- 上一轮：#36 `handoff-screen-36.md`
