# handoff｜P4 Windows 外壳：讨论怎么实现 · 2026-09-20 #8

> **新会话任务**：**讨论 Windows 上的"类似功能"怎么实现**——即 Phase 2 阶梯的 **P4「Windows 外壳」**：把 Windows 从"手工原型已通"推进到与 Linux P1 对等的**可安装、会话内自启、远程可连**的图形服务。**不是**继续写 Linux、**不是**做 Android。产出以**设计/决议**为主（Windows 装配与自启外壳怎么落），必要时少量落码验证。
> **交接语**：读本文件即可开会话；细节读 `checkpoint-4.md` §三（Windows 实测）、`spec-screen-1.md` §5.7、`handoff-screen-07.md`（P4 原始议题清单）、`handoff-screen-06.md`（P1 现状）。
> **前序**：`handoff-screen-05.md`（协议冻结 + P1 决议）→ `handoff-screen-06.md`（P1 落码 + 双机验收）→ `handoff-screen-07.md`（P4 议题）→ 本文件。

## 本会话性质

**讨论 + 一次真机验证**（原计划只讨论 Windows，实际先被 Linux 的"给 agent 一个账户"这条追问带走）。Windows 侧只产出讨论结论，未落码。

## 已定（可当既定，不要重开）

### A. Windows 实现面（本会话讨论结论）

- **只需实现服务端**：协议 `screen/1`（wire 不动）、客户端 `ScreenChannel`、`ssh -L` TCP 隧道、`screen_capture`/`screen_act` 工具面**全部复用**。Windows 侧要补的只有两块：
  1. **服务端 backend**：`screenlab/service/backends_win.py` 已存在（Pillow 抓屏 + SendInput + DPI 感知），**未在真机复验**；
  2. **装配 / 自启外壳**：`screenlab/install/` **只有 Linux**，这正是 P4 要补的。
- 另有一项**客户端配置**（不是服务端能自决的）：装配期把 `agent.json` 的 `graphics.endpoint`（及 `authority`/`grant` 取值）配对。

### B. Windows「登录前 / 安全桌面」——能做，但建议不做

墙的位置：登录/锁屏界面 `LogonUI` 以 **SYSTEM 跑在 Winlogon 安全桌面**上，与用户默认桌面**不同桌面 + UIPI 隔离** → 普通进程既抓不到也注入不进。绕过只有三条路：

| 路 | 能力 | 代价 |
|---|---|---|
| **A. 自动登录**（现状思路） | 把问题变成"永不登出"；能覆盖"重启后远程可用" | 密码托管（注册表明文 → 用 LSA secret 或凭据提供程序收敛）；**锁屏/屏保会切回安全桌面，照样失联**，需禁锁屏策略 |
| **B. UIAccess**（签名 + 装 `Program Files`） | 进程可运行在安全桌面 → **能抓登录界面、能 `SendInput` 打字** | 需代码签名证书 + 受信任安装位置；仍是"装一个能看见/输入凭据的组件" |
| **C. Credential Provider / Winlogon notify** | 抓屏、注入、**填凭据**、远程解锁 | 管理员部署、签名、随 Windows 升级维护；**形态与远控/凭据窃取工具同构，AV/EDR 会盯** |
| 另一条思路：**RDP** | 不碰登录前，自己开一个会话，凭据由发起端给 | 运输从 `ssh -L` 换成 RDP；操作的是 RDP 会话桌面而非物理控制台 |

- **结论/建议**：这**超出 P4 口径**（P4 = 已登录的交互桌面）。按"借平台的门"的鉴权原则多半**不做**——A 已能用极低成本覆盖真实诉求；B/C 等于在目标机装 SYSTEM 级、能触登录凭据的组件，收益与风险不成比例。
- Linux 对标：**同样的墙**（greeter 是别的会话/用户，Wayland 下更够不着），解法也在显示管理器插件层。不是 Windows 特有。

### C. Linux「给 agent 一个账户」= 给它一个独立会话/桌面

- **不是抢人的桌面**：agent 有自己的账户 → 有自己的桌面（自己的 X server/display、`XAUTHORITY`、session D-Bus、`systemd --user` 实例）。人的会话不受影响，输入注入走 XTest 只进它自己那个 X server。
- **隔离三层对齐**：**账户 = 会话 = 服务**（socket 归 uid）。实测：zhengyp 访问 tangyu 的 socket → `PermissionError`。
- **四种"多桌面"层次**（轻→重）：同机多用户会话（VT 切换，`chvt`/`loginctl list-sessions`）/ **无头 Xvfb**（212 形态，不占物理屏）/ 真多席（systemd-logind `seat`）/ 容器-VM。
- **对应 `authority` 模型**：agent 自己占的机器/会话 = **`owned`**（恒有 capture/input）；把人正在用的桌面让出去 = **`granted`**（要走 grant/consent）。
- **明确语义**：`给 agent 一个账户` = **把 agent 放进那个账户**（`agent 账户 = 服务账户 = 会话账户`），**不是**"给它一个它去连的账户"。这是目前唯一"零凭据直连"的形态。
- **缺口**：**免 root 的形态还没有**——用户态无头 Xvfb + `loginctl enable-linger`（一次性管理员动作）这条路未实现；当前无头只能走 root 装的 system unit。

### D. 本会话核心产出：发现并修复「无头 X 外壳缺 X 鉴权」

- **现象**：`xvfb-start.sh` 起的是 `Xvfb :99 ... -nolisten tcp`，**没有 `-auth`**；`/tmp/.X11-unix/X99` 是 `0777` → X server **不做访问控制**。
- **实测影响**：本机 zhengyp **能直接** `DISPLAY=:99` 读 tangyu 的**当前窗口标题**、`xdotool type` **注入成功**——完全不需要密码。
- **含义**：`账户即门` 当时**只守住了 screenlab socket，没守住它脚下的 X**；212 用同一份模板，同样敞开。
- **修法（3 文件，+18 −1）**：
  - `screenlab/install/xvfb-start.sh`：`Xvfb -auth "$AUTHFILE"` + `export XAUTHORITY`
  - `screenlab/install/install.sh`：system 模式生成随机 cookie → `$ETC/Xauthority`（`0600`、`chown $SERVICE_USER`），`sed` 渲染 `@XAUTHFILE@`
  - `screenlab/service/daemon.py::_make_daemon`：设 `os.environ["XAUTHORITY"]`——`PillowCapture` 用 `ImageGrab(xdisplay=...)`，认证**只认进程 env**；修前只把 xauth 给了子进程，开鉴权后抓屏会报 `X connection failed: error 1`
- **实测（本机 tangyu / 212 zhengyp 双机）**：无 cookie 直连被拒（`No protocol specified`）；有 cookie 与经 screenlab 均正常；`capture→act→capture` 闭环 OK；`pytest tests/ -q` → **1198 passed / 4 skipped**。
- **状态**：repo 改动**未提交**（分支 `feat/screenlab-p1`，工作树 3 个 modified）。

### E. 212 真 reboot 验证通过（回答"整机重启后 agent 能用吗"）

- `systemctl reboot` 后（boot_id 已变、uptime 0）：两个 unit **enabled + active、无人工、无登录会话**；`Xvfb :99 -auth …` 起来；daemon 带 `--xauth`；无 cookie 直连被拒；闭环 OK；`authority=owned`。
- **结论**：一次性装配（需 root）+ cookie 持久化在 `/etc` → **整机重启后 agent 零人工可用**。前提是 `agent 就以该账户运行`（同机直连）。

## 现状盘点（代码 + 机器）

**代码**

- `screenlab/`（cogos 仓库根）：`proto/`（framing + 协议 + 薄客户端）、`service/`（daemon + x11/win32/android 后端 + 调试 CLI）、`install/`（install/uninstall + units，**Linux only**）。
- 本会话未提交的 3 个 modified 见 §D。
- `screenlab/` **禁止 import cogos**；`cogos` 侧只 import `screenlab.proto`。

**本机 `10.0.2.15`（VirtualBox VM，CentOS Stream 9）**

- 新装系统包：`xorg-x11-server-Xvfb`、`openbox`（appstream）。
- screenlab 以 **system 模式**（无头）装给账户 **`tangyu`（uid 1001，无 sudo、不在 wheel）**：`authority=owned`、X auth 开、`/opt/screenlab` + `/etc/screenlab/Xauthority`、`/run/screen/screen.sock`（0700 tangyu）。
- 两 unit `enabled + active`；`/var/lib/screenlab`（`StateDirectory`，归 tangyu）。
- **实测闭环**：以 tangyu 起 Chrome → Bing 搜 `justmysocks` → 约 4,570 条结果 → 点第一条 `justmysocks.net`（`ERR_CONNECTION_REFUSED`，国内 DNS 污染）→ 点第二条 `jms-socks.com` 加载成功。截图 `/tmp/t.1.png`~`/tmp/t.7.png`。
- **跨账户实测**：zhengyp 连 tangyu 的 socket → `PermissionError`；zhengyp 直连 `:99`（修后）→ `No protocol specified`。
- zhengyp 的物理 `:0`（GDM 会话）**全程未受影响**；本机**没有**装 user 模式。
- `sudo` 用 `cat ~/.secrets/centos.key | sudo -S -p '' <cmd>`（**本机与 212 同一个 key**）。

**212（无头验证场）**

- 重装为**补丁版**（`/tmp/patched/`），`authority` 由 `granted` 改为 **`owned`**，X auth 开；真 reboot 验证通过（§E）。
- 只有一个普通账户 `zhengyp` → **跨账户拒绝在 212 是用"无 cookie 拒绝"代理验证的**；真跨账户靠本机那组。
- 遗留：`/tmp/patched/`、`/tmp/verify212.sh` 未清。

**Windows：Surface `192.168.1.112`（本会话未碰）**

- 账户 `screen`（非管理员、`Users` 组）；`ssh screen@192.168.1.112` key 免密；自动登录已配。
- 原型在 `C:\Users\screen.TABLET-BBT8EQB4\screenlab\`（`daemon.pyw` / `restart_daemon.cmd` / `blobs\` / `daemon.log`）；启动项 `…\Startup\screenlab_daemon.vbs`。
- **上次盘点时 daemon 未运行**（9911 无监听）——下会话第一件事先诊断是否已自动登录、启动项是否失败。
- 传输：Windows OpenSSH **不支持 AF_UNIX 转发** → 监听 `127.0.0.1:<port>`，本机 `ssh -L` 转出；客户端 `tcp:` + `ssh -L` 已支持。

## 待讨论/裁决（承接 07，本会话已消化其中几条）

1. **账户/会话模型**：继续"专用标准账户 + 自动登录"？还是占当前用户会话？自动登录密码怎么写才不落明文（LSA secret / 凭据提供程序）。
2. **自启外壳形态**：Startup 文件夹 `.vbs`（现用） vs **计划任务**（AtLogOn/AtStartup） vs Windows 服务 + 会话代理；谁负责重启后恢复、进程掉了重拉。
3. **装配器**：`install.ps1` / `.cmd` / python——与 Linux `install.sh` **对齐**：一次执行、末行打印 `SCREENLAB_ENDPOINT=...`；`uninstall` 对等。
4. **打包**：venv（Linux 走 `--system-site-packages`） vs Windows 嵌入式 Python vs PyInstaller；Pillow 依赖、GBK 控制台/路径编码。
5. **端点与运输**：`tcp:127.0.0.1:<port>` 固定 vs 动态；`ssh -L`；`agent.json` 里 `graphics.endpoint` 与 `authority`/`grant` 取值。
6. **认证**：Windows loopback TCP **任何本地进程都能连** → 是否加本地 token；与 P3（granted 的 `stop`）的关系；装配期认证来源（借 sshd）。（Linux 侧对应缺口＝X auth，**已修**；Windows 侧对应的是 NTFS ACL + token。）
7. **多显示器 / DPI 上报**：`all_screens` 多屏原点（`SM_*VIRTUALSCREEN`）、`scale`/`rotation` 是否补齐到 `displays`。
8. **验收判据**：对齐 P1 的 1–7（一次装配 / 重启自启 / agent 自动连 / 真 `capture→act→capture` 见变化 / 过期拒 + `since_hash` 去重 / 干净卸载 / wire 不变），在 Surface 真机跑；并给 P1 未做的"人工登出"在 Windows 上定等价判据（锁屏 / Winlogon / UAC）。
9. **顺序**：先做 P4，还是先补 P2（断连即终态）/ P3（grant 的 `stop`）？（阶梯见 `checkpoint-5.md` §九）

**另需裁决（本会话新增）**

10. **分支**：`feat/screenlab-p1` **未合并 master、未建 PR**，且现在多了一层未提交的 X auth 修复 → Windows 工作基于**合并后的 master** 还是**同一条分支**？这 3 个文件的修复是**单独提交/PR**还是并进 P1？
11. **文档回写**：本会话的 X auth 发现与修法要不要回写 `checkpoint-5.md` §十 / 权威分册 `cogos/docs/design-agent-tools.md`？

## 已知坑（照抄，别重踩）

**Windows**

- Session 0 无桌面 → 服务必须在交互会话内。
- 标准账户不自动进 `Users` 组 → 登录界面不列该账户。
- 不开 DPI 感知 → 逻辑/物理像素差（150% = 1.5×）。
- Windows OpenSSH **不支持 AF_UNIX 转发** → 必须 TCP。
- 中文字符串经 ssh（GBK 控制台）乱码（显示问题、不影响功能）。
- **UAC / Secure Desktop**：`SendInput` 受 UIPI 限制，提权窗口、登录/锁屏界面够不着（**待验证并记录**）——对应 Linux 的"登出后 Wayland greeter 够不着"。

**Linux / screenlab**

- 无头 X *必须* 有 X 鉴权（本会话修的），否则同机任意账户可抓屏/注入。
- system unit 必须 `User=<SERVICE_USER>`，否则 `/run/screen` 归 root 0700，`ssh -L` 进不来。
- **WM 是前置**：无 openbox 时 `_NET_ACTIVE_WINDOW` 缺失、键盘事件乱跑。
- **system 模式是单实例**：`/run/screen/screen.sock`、`/var/lib/screenlab`、unit 名都是固定路径；`--user` 模式才按 uid 隔离。
- 非前台 X11 会话能否稳定抓屏属实现细节、待验证；要稳就用独立 Xvfb。
- 服务**不绑登录会话**（headless 走 `multi-user.target`）；登出后 Wayland greeter 够不着（P1 已实测；P1 口径把"会话登录本身"排除在失败判据外）。

## 环境与命令速查

- **Surface（Windows）**：`ssh screen@192.168.1.112`（key 免密）；原型目录 `C:\Users\screen.TABLET-BBT8EQB4\screenlab\`；启动项 `…\Startup\screenlab_daemon.vbs`；诊断（第一步）：`netstat -an | findstr 9911`、看 `daemon.log`。
- **本机（Linux, tangyu）**：`sudo -u tangyu /opt/screenlab/venv/bin/python -m screenlab.service.cli --socket /run/screen/screen.sock {info|displays|capture|act}`；unit `screenlab.service` / `screenlab-xvfb.service`（system）；cookie `/etc/screenlab/Xauthority`。
- **212**：`ssh zhengyp@192.168.1.212`（key 免密）；`cat ~/.secrets/centos.key | sudo -S -p '' <cmd>`；同上的 CLI 路径；unit 同本机（system 模式，`authority=owned`）。
- **cogos**：`/home/zhengyp/work/A/cogos`；分支 `feat/screenlab-p1`（3 个未提交 modified）；测试 `python3.11 -m pytest tests/ -q`（**1198 passed / 4 skipped**）。
- 本机装包命令备忘：`cat ~/.secrets/centos.key | sudo -S -p '' dnf install -y xorg-x11-server-Xvfb openbox`。

## 关键引用

- 实测：`checkpoint-4.md` §三（Windows 打通）、§五（系统改动清单）、`spec-screen-1.md` §5.7（Windows 特有约束）。
- 阶梯/形态：`checkpoint-5.md` §九（P4 Windows 外壳）、§八（图形服务借 ssh 装配/运输）、§十（P1 决议 + 验收判据）。
- 前序：`handoff-screen-06.md`（P1 落码 + 双机验收）、`handoff-screen-07.md`（P4 原始议题）。
- 客户端：`cogos/agent/impl/graphics.py`（`tcp:` + `ssh -L`、`_open_tunnel_tcp`）、`cogos/agent/tools.py::make_screen_specs`。
- 服务：`cogos/screenlab/service/backends_win.py`、`platform_backends.py`（`backend="win32"`）、`screenlab/install/`（**仅 Linux**）。
- 本会话改动：`cogos/screenlab/install/install.sh`、`install/xvfb-start.sh`、`service/daemon.py`（未提交）。
- 旧原型：`work/A/checkpoint/screen-lab/`（`daemon.pyw` / `restart_daemon.cmd` / `README.md`）。
- 凭证/配置：`design-secrets.md` §5（`computer` 块）。

## 纪律

- 跑测试用 `python3.11 -m pytest`；结论先落 checkpoint/spec，定案再回写权威分册 `cogos/docs/design-agent-tools.md`。
- 目标侧叫"**服务**"不叫 agent；**认证不在协议里**；`screenlab/` **禁止 import cogos**；`screen_capture`/`screen_act` 是 agent 面。
- 密码类只经文件与 `SSH_ASKPASS`，绝不落进命令行或工具输出。
- **验证重启别用本机**（会断当前会话）——用 212。
