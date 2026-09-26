# 进度｜Goal 1（agent 自活 + agent 间授权 + 人 viewer）· 滚动状态

> **就地更新，不追加成流水账。** 新会话只读本文件 + `handoff-screen-28.md`（环境细节）。
> 上次更新：2026-09-23 15:56 ｜ 当前上下文见 §6
> **Goal 1 收口（09-23 15:56）**：多账户缺口已补——每账户一块**自管 headless Xvfb**（`session-start.sh create`，systemd user unit 组）；形态裁决落定 **Xvfb**（GL/软件渲染不作为裁决项）。
> **Goal 1 收尾（09-24 #39）**：`#37` 起"按怎么使用重验"定位的 F1–F9 **全部处置并靶机验证**（详见 `issue-screen-surface-lifecycle.md`「执行中发现」、证据 `screen-verify-usage-1.md`）；跨机 `view` 3b 机械通路验证 ✅（真人浏览器侧由 YZ 天亮后自处理）。**已提交 3 commit + tag `screenlab-goal1-2026-09-24`（已 push 到 origin）。**

## 0 目标与形态
- **Goal 1** = agent 有自己的一块图形界面（自活）＋ agent 间可授权互操作 ＋ 人可 viewer 看（先只看）。
- **形态（推荐，待 YZ 正式确认）**：**VM 内普通 X11 桌面**（XFCE/Xorg）；人只用 viewer 看，不进 VBox 窗口。Wayland / Xwayland / headless 合成器 / Xvfb 全部降为**延后或备选**。
  - ✅ **2026-09-23 15:56 落定**：多账户各自独立面 **= 每账户一块自管 headless Xvfb**（`session-start.sh create`，systemd user unit 组）；Xephyr / VKMS 留作备选。GL/软件渲染不作为裁决项（见 §4）。

## 1 锚点（固定，别重新发现）
- 靶机 `surface-centos-9` / `100.100.137.78`（tailscale direct）；本机 `acer-centos-9` / `100.79.86.84`。
- surface 宿主：`ssh zhengyp@100.112.50.115`；VBoxManage 全路径 `"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"`（不在 PATH）。
- 靶机 agent 账户：**agent1**（uid 1001, video+render, 无 sudo）；`ssh agent1@100.100.137.78`。
- 靶机桌面：**`:0` = agent1 的 XFCE/X11**；auth = `/run/user/1001/gdm/Xauthority`。
- 以 agent1 身份跑 GUI/抓帧的模板：
  `runuser -u agent1 -- env DISPLAY=:0 XAUTHORITY=/run/user/1001/gdm/Xauthority XDG_RUNTIME_DIR=/run/user/1001 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus <cmd>`
- **靶机无 sudo（需密码）→ 一律 `ssh agent1@100.100.137.78` 直连操作**（`--xauth` 显式传）。
- `act pointer --x/--y` 是**归一化坐标 0..1**（不是像素），daemon 内 `norm_point_to_px` 换算；`act type/text` 直接给字符串。
- 靶机部署（Step 4 起）：`rsync` 本仓 `screenlab/` → `~/cogos/screenlab`；服务包落在 `~/.local/share/screenlab`；Pillow 用 `pip3 install --user`（agent1 的 python3.9）。
- 起服务：`bash ~/cogos/screenlab/install/session-start.sh agent1 --display :0 --xauth /run/user/1001/gdm/Xauthority`；socket `/run/user/1001/screenlab.sock`。
- 靶机自活前置（已做）：屏保锁关（xfconf `xfce4-screensaver` 各 `/lock/*` = false + `xset s off -dpms`）；分辨率钉 1920x1080（`xrandr` + `~/.config/autostart/screenlab-resolution.desktop`）；keyring 已建空密码 `login.keyring`，不再弹框。
- 靶机第二账户 **agent2**（uid 1002, video+render，同密码）；`agent2 → agent1@localhost` 免密已配。
- 跨账户接入（Step 5 实测）：agent2 侧 `ssh -N -L $HOME/a1.sock:/run/user/1001/screenlab.sock agent1@localhost`，客户端 `--sock $HOME/a1.sock`。
- e2e harness 在靶机 `/tmp/slrun`（rsync 自本仓 `screenlab/` + `tests/screenlab/`，`chmod -R a+rX`）；客户侧用 `python3.11`（3.9 无 PyGObject 等）。
- **约束**：同一 VM 虚拟 GPU 只能有一个真 Xorg（DRM master 独占）→ "每账户一块独立 X11 桌面"需另定机制（Xephyr 嵌套 / 另开 VM / 虚拟显示），见 §4。
- **人侧 viewer 起法（Step 6 实测）**：本机 `ssh -N -L /tmp/kilo/a1.sock:/run/user/1001/screenlab.sock agent1@100.100.137.78`；`cli --sock /tmp/kilo/a1.sock grant --bits capture --subject YZ` 取只读凭证；`python3.11 -m screenlab.viewer.bridge --sock /tmp/kilo/a1.sock --credential <tok> --port 8800`；浏览器开 `http://127.0.0.1:8800/`。
- 起/停靶机：`ssh zhengyp@100.112.50.115 "\"C:\...\VBoxManage.exe\" startvm centos9 --type headless"`。
- 代码：`../cogos/screenlab` @ `c23dab3`（分支 `feat/screenlab-p2`，已推送）；旧 tag `screenlab-freeze-2026-09-22`。

## 2 步骤表

| # | 目标 | 状态 | 判据 / 证据 |
|---|---|---|---|
| 0 | 定靶 + 清场 | ✅ | 靶机=surface-centos-9；两机旧 screenlab 清空；靶机 machine-id `7db571b5…`、hostname `surface-centos`。见 `handoff-screen-28.md` |
| 1 | **闸门**：X11 能否看见 GTK/GL 窗 | ✅ | X11+合成 ON，root 抓与单窗抓都看清 `xfce4-terminal` 文字、`zenity` 文字、keyring 对话框 —— **B2 不重现**。证据 `/tmp/kilo/cap1-{root,term,zen,gst}.png` |
| 2 | 收敛取帧后端（`backends.py`） | ✅ | `pick_capture` 去掉探测链，默认唯一 = `PillowCapture`（合 spec：Pillow `ImageGrab(xdisplay)`）；`windows`/`x11-windows`/`gst`/`import` 降为 `SCREENLAB_CAPTURE` 显式 override。py_compile + 本地 dispatch 冒烟通过（默认→pillow，windows 别名→x11-windows） |
| 3 | X11 版会话脚本（`session-start.sh`） | ✅ | `session-start.sh` 改为定位账户既有 X11 桌面（默认 `:0` + `$RT/gdm/Xauthority`，`--display/--xauth` 覆盖，限时探测 `xdotool getdisplaygeometry`），不再起 headless 合成器 / 不探 mutter cookie；`session-stop.sh` 只停服务不碰桌面；删 `xvfb-start.sh` + `screenlab-xvfb.service`，`install.sh`/`screenlab.service`/`uninstall.sh` 同步去除 Xvfb 路线与 `--resolution`。校验：`bash -n` 全过；`pytest tests/screenlab`（python3.11）18 passed |
| 4 | agent 自活闭环 | ✅ | 靶机 `:0` 内 `capture → act → capture`：`act pointer(归一化) + type + key Return` 后第二帧 `changed=true`，终端回显 `screenlab-alive-42`。证据 `/tmp/kilo/screen-step4-*.png`。前置：分辨率 1920x1080、keyring 空密码、屏保锁关 |
| 5 | agent 间授权 | ✅ | 靶机建 **agent2**（uid 1002, video+render）；agent2→agent1 免密 ssh；agent2 经 **streamlocal 隧道** `ssh -N -L $HOME/a1.sock:/run/user/1001/screenlab.sock agent1@localhost` 接入 agent1 服务，`guest_intervention_e2e.py` **10/10**（凭证接入 / 看 / owner 把持时 guest 被拒 `input_taken` / yield 后 guest 可操作 / owner 自动取回 / revoke → `no_channel`） |
| 6 | 人侧 viewer（只看） | ✅ | `viewer/bridge.py` 默认 **read-only**（只 `GET /frame` + `/status`，`POST /act` → 403 `read_only`；`--allow-act` 才恢复操作），`page.html` 同步只读态；本机 acer 经 tailscale 隧道 `ssh -N -L /tmp/kilo/a1.sock:/run/user/1001/screenlab.sock agent1@…` 起桥 `:8800`，实测 `/frame` 1920×1080 PNG、`/status` read_only、`/act` 403。证据 `/tmp/kilo/frame.png` |
| 7 | 收尾 | 🟡 | 代码已检视 + 修 4 处小疵 + 提交推送（`d840ccd` X11 形态收敛 / `c23dab3` viewer 默认只读）→ `origin/feat/screenlab-p2`。**余**：spec 回写、清理、打 tag（09-24 收尾时统一处理） |
| 8 | **多账户 create 形态（Goal 1 收口）** | ✅ | `session-start.sh create` = 每账户自管 Xvfb + WM + 服务（systemd user unit 组，`session-create.md`）；靶机双账户 `run_goal1_xvfb.sh` 全绿 **RC=0**（create listening / 幂等 / 自闭环+隔离 / 跨账户 guest 10/10 / viewer 只读）；生命周期（stop 只停服务 / destroy 清净 / kill Xvfb 自愈 / linger=yes）全过。**余**：提交/tag（09-24 收尾时统一处理） |

## 3 当前指针
- **🟢 09-24 收尾（#39）**：Goal 1 能力与生命周期已按目标验证到**无已知开放缺口**；F1–F9 全落定（见 `issue-screen-surface-lifecycle.md`「执行中发现」）。**唯一剩余 = 提交 / tag**（YZ 定；固化 = 把"本机现场可用"变成"可复现"）。观察/搁置见下 §4。下一线 = **Goal 2**（真人机上，关系 3a）。
- **09-23 17:3x 方向变更：Goal 1 收口之后进入"体系重建"**。Linux 形态裁决：**授权 = 给账户**（信任前提），删除令牌/凭证层；对外只留一个 `screenlab` 入口。
- **工作稿（唯一入口）**：`design-screen-system.md`（三面：装配/会话/观察；多观察者+单控制者；viewer 只读、默认绑 tailnet）。
- **代码**：`../cogos` @ `feat/screenlab-p2` —— 体系重建已提交推送 `14fca90`；本会话（Act 1 / 设计讨论）**未改代码**。
- **09-23 17:5x 进展**：第 3 步服务瘦身、第 4 步统一入口（+`remove-agent`）、第 5 步靶机从零验证 **✅ 全绿**；死值默认 / view 绑定 / 幂等 display / firewalld 放行 均已处理；`ledger.py` → `channels.py`。
- **下一步（#35，动手改）**：按 `issue-screen-surface-lifecycle.md` 落码（C1–C12 / B1–B2）＋量三项形态小项＋搁 L1；详见 `handoff-screen-35.md`。tag / §16 回写属流程。
- 旧 Goal 1 结论见 `handoff-screen-32.md`（多账户 Xvfb 全绿），形态仍沿用。

## 4 阻塞项 / 待 YZ
- **🟢 09-24 收尾盘点**：
  - **提交 / tag 已完成**：3 commit + tag `screenlab-goal1-2026-09-24`（`feat/screenlab-p2` 与 origin 同步，**已 push**）。Goal 1 事项均已落定。
  - **暂放（不阻塞收尾，候选）**：L1 行为保真（鼠标轨迹/打字节奏）· O1 窗口不铺满/整屏 bounds · O2 首跑气泡 · O3 tz/lang · `install-machine` 不放行宿主 firewalld（view 端口需手工放行）· **真人浏览器侧 3b**（**✅ 2026-09-24 #43 现场验收**）· 真重启确认（C4 静态已过）。
  - **归 Goal 2 / 更后**：观察者凭据（capability URL）· 真 GPU（口径已定=与真人 VBox 齐平）· Wayland 真人桌面 · 关系 3a（真人机上）。
- **【已解】多账户各自独立图形面**：→ **每账户一块自管 headless Xvfb**（`create` 模式）。"同 VM 单 GPU 只能一个 rootful 真 Xorg（DRM master 独占）"仍成立，故走虚拟 server；Xvfb 上 GTK/VTE/Chrome 取帧已实测通，B2（取帧盲）不重现（B2 是 mutter+Xwayland 特有）。
  - 候选顺序（YZ 已认可）：**Xvfb 单测 → Xephyr 嵌套**（叠在真 Xorg 上，取帧走已验证路径）**→ VKMS**（各一 DRM 设备，最重）。
  - **Xvfb 单测结果（14:56，✅ 通过）**：靶机 agent1 起 `Xvfb :7 -screen 0 1920x1080x24 -ac` + openbox + `xfce4-terminal`/`zenity`，用**真实 `PillowCapture`** 抓帧 → **GTK/VTE 文字全在**（`SCREENLAB-XVFB-GATE-2026`、`SCREENLAB-ZENITY-GATE 42`）。**B2 在 Xvfb 上不重现** → 「非真 Xorg ⇒ B2」外推被证伪，B2 是 mutter+Xwayland 特有。证据本机 `/tmp/kilo/gate-xvfb.png`（真桌面对照 `gate-real.png`）。
  - **daemon-on-Xvfb 闭环（14:58，✅ 通过）**：`session-start.sh agent1 --display :7` 起服务（pillow + xdotool），`capture→act type→act key Return→capture` 闭环，帧现 `echo SCREENLAB-ACT-OK` 回显。证据 `/tmp/kilo/gate2-after.png`。
  - **多账户各自独立面 + 隔离（15:01，✅ 通过）**：agent1 `:7` **1280x720**、agent2 `:8` **1024x768**，各起**独立 Xvfb（各自 0600 xauth）** + **各自 screenlab 服务**，两者并存；各自闭环 `changed=True`，帧内各自身份（`AGENT1/2-SURFACE`、各自 hostname 提示符）。**X 级隔离成立**：互访 `getdisplaygeometry` → `No protocol specified` DENIED；对方 `/run/user/*` 与 xauth 文件 `Permission denied`。证据 `/tmp/kilo/gate3-agent1.png`、`gate3-agent2.png`。
  - **GL/Chrome（15:02，✅ 功能可用）**：`:7` 上 Chrome 148 完整渲染，页面文字 + 浏览器 UI（tab/地址栏）全可抓。`glxinfo` = **llvmpipe 软件 GL**（`direct rendering: Yes`、`Accelerated: no`）。→ **取帧没问题**；但软件渲染本身是自动化指纹（spec §0.0「不被检测」），属形态权衡点。
  - **凭证层 e2e（15:03，✅）**：`guest_intervention_e2e.py` 在 agent1 `:7` 与 agent2 `:8` **各 10/10**。
  - **结论**：Goal 1 三关系（自操作 / 授权他 agent / 人 viewer）现已在**多账户各自的 Xvfb 面**上全部实测通过。
  - **✅ 形态裁决已落（15:56，YZ 认可思路）**：多账户 = **每账户自管 Xvfb**（`session-start.sh create`，systemd user unit 组）。**GL/软件渲染不作为裁决项**（真人未开 3D 的 VBox 桌面同样 llvmpipe；`navigator.webdriver=false`，注入走 XTEST 非 CDP）。Xephyr / VKMS / 多 VM 留作**真 GPU 需求**的备选（延后）。
  - **验证工具已收编（15:56，✅ 全绿）**：`../cogos/tests/screenlab/e2e/` 的 `run_goal1_xvfb.sh` 改为**驱动正式 `create`**（`session-start.sh create` / `session-stop.sh destroy`），删掉 `xvfb_account_prepare.sh` 原型；`xvfb_goal1_e2e.py`（账户内判据）、`xvfb_tunnel.sh`（隧道）沿用。一次跑完 **RC=0**。证据 `/tmp/kilo/goal1/{frame,agent1-after,agent2-after}.png`。
  - **踩到的坑（供 create 模式参考）**：① 换掉包目录后**必须 restart** 服务，否则旧 daemon 的 blobs 目录消失→`FileNotFoundError`；② 终端焦点会被残留浏览器抢占，`type` 进错窗 → prepare 每次都 `windowactivate`；③ ssh 命令行里 `pkill -f <同串>` 会自匹配杀掉自己（放进脚本文件才安全）。
  - 判据：GTK/VTE 窗（**不能用 Chrome**，B2 里它恰好正常）、Pillow 真实后端、账户间互不可见/不可操作、落像素级 PNG 证据。
- **打 tag 的时机/名**：Goal 1 收口前**挂起**；收口后由 YZ 定。
- spec 回写（`cogos/docs/design-agent-tools.md`）：照旧可做。
- 其余开放问题（未被 YZ 裁，仍留）：同一桌面允多少操作者/观察者、授权粒度、反检测强度。

## 5 工作纪律（会话连续性）
- **阈值（09-25 起 150k）**：上下文 **≥150k（≈15%）** 或路径偏 → 就地更新本文件 + 写 handoff + `tools/feishu_notify.py` 通知 YZ 切会话。
- **当前阶段（screen 改体系）**：人工在旁，**不起 timer**；每完成一步 `tools/feishu_notify.py` 通知 YZ 一次。
- **每完成一步**：更新本文件（就地改），并在 §6 记一行；随后 `tools/feishu_notify.py` 通知 YZ，**若无须 YZ 介入（判据失败/需裁决/动本机或提交）则直接继续下一步**，不空等。
- **自检命令**：`python3 tools/ctx.py`（读 `~/.local/share/kilo/kilo.db` 的 token 字段，单行输出，极省）。

## 6 更新记录（每次只记一行：时间 · 指针 · token）
- 2026-09-23 13:45 · 建文档；Step 0/1 完成 · 168k/1M
- 2026-09-23 13:46 · 交接到新会话（`handoff-screen-29.md`）；指针仍停在"待 YZ 确认 X11 单形态，然后 Step 2" · 172k/1M
- 2026-09-23 13:52 · YZ 确认 X11 单形态；Step 2 完成（`backends.py` pick_capture 收敛，未提交）；指针 → Step 3
- 2026-09-23 14:07 · Step 3 完成（X11 版 session-start/stop + 删 Xvfb 路线，未提交）；指针 → Step 4
- 2026-09-23 14:10 · Step 4 完成（靶机 `:0` 自活闭环跑通，第二帧 changed；前置分辨率/keyring/屏保已处理）；指针 → Step 5（待 YZ 定 agent2）
- 2026-09-23 14:20 · Step 5 完成（靶机建 agent2 + streamlocal 隧道跨账户接入，guest_intervention_e2e 10/10）；指针 → Step 6
- 2026-09-23 14:26 · Step 6 完成（viewer 默认只读 + 跨 tailscale 实测 /frame & /status，/act 403；pytest screenlab 20 passed）；指针 → Step 7（提交/推送待 YZ）
- 2026-09-23 14:35 · 代码自检 + 修 4 处小疵；提交推送 `d840ccd` + `c23dab3` → `origin/feat/screenlab-p2`；Step 7 余 spec/清理/tag（tag 待 YZ）
- 2026-09-23 14:55 · **判断修正（YZ 同意）**：Goal 1 未完成，缺口=多账户各自独立图形面；tag 挂起；指针 → 闸门实验（Xvfb → Xephyr → VKMS）
- 2026-09-23 14:58 · **闸门①Xvfb 单测 ✅**：靶机 `Xvfb :7` + 真实 `PillowCapture` 抓到 GTK/VTE 文字，**B2 不重现**（B2 是 mutter+Xwayland 特有）；指针 → 闸门②daemon-on-Xvfb 闭环 + act 注入
- 2026-09-23 15:02 · **闸门②③ ✅**：daemon-on-Xvfb 闭环（type/key 生效）；agent1 `:7` 1280x720 + agent2 `:8` 1024x768 **各自独立 Xvfb + 各自服务并存**，X 级隔离成立（互访 DENIED）。**Goal 1 的多账户缺口在 Xvfb 形态下已打通**；余：GL/Chrome、会话脚本形态、凭证 e2e 复跑
- 2026-09-23 15:04 · **闸门④GL/Chrome ✅ + 凭证 e2e ✅（两账户各 10/10）**：Goal 1 三关系已在多账户 Xvfb 面全通。**停在 YZ 形态裁决**：Xvfb（软件渲染，指纹风险） vs 真 Xorg+Xephyr 嵌套（未验）。未定前不写会话脚本、不 tag
- 2026-09-23 15:24 · **Goal 1 验证工具落地并全绿（RC=0）**：`../cogos/tests/screenlab/e2e/run_goal1_xvfb.sh` 一条命令跑完「部署/双账户 Xvfb+服务/幂等/账户内闭环+隔离/跨账户隧道 guest/viewer 只读」；证据 `/tmp/kilo/goal1/*.png`。工具**未提交**（YZ 定）
- 2026-09-23 15:56 · **Goal 1 收口**：create 形态落地（`session-start.sh create` / `session-stop.sh destroy` + systemd user unit 组 + `session-create.md`）；靶机双账户 `run_goal1_xvfb.sh` RC=0；生命周期全过；spec 回写（spec-screen-1 §0.0/§5.3/§7、ledger §0、design-agent-tools §16）。**余**：提交/tag（YZ 定）
- 2026-09-23 17:3x · **方向变更（体系重建）**：Linux 授权裁决 = **给账户**，删令牌/凭证层；工作稿 `design-screen-system.md`；`1a818f1` 提交 create 存档；第 3 步服务瘦身 + 第 4 步统一入口 `screenlab`（install-machine/add-agent/open/close/view）落地，**未提交**；阈值 150K→200K。指针见 §3
- 2026-09-23 18:0x · **体系重建收口 + 第 5 步靶机验证 ✅**：清债（死值默认去 uid/路径常量化、view 默认绑 tailnet、install-machine 自检 python3/PIL/openbox、幂等 open 报真 display、新增 `remove-agent`、`ledger.py`→`channels.py`）；靶机清场后从零走通 install-machine→add-agent→open→自用闭环→roles(7/7)→view 只读（异机 tailnet 取帧）。坑：firewalld 默认拒非 ssh 端口。证据 `/tmp/kilo/sys/*.png`。**余**：提交/tag（YZ 定）、§16 回写
- 2026-09-23 22:5x · **诊断 VM 崩溃（非 screenlab）+ Act 1 演示 + 设计结论**：崩溃根因=宿主 AHCI 端口复位 / VM 时钟停摆（`controlvm reset` 修复）；Act 1 全绿（幂等 open / 闭环 / 三层隔离 / 三账户并存 / close·destroy 生命周期 / kill Xvfb 自愈 / 真工具层 `tool_loop_e2e`）；从目标推出 C1–C12 + L1，记入 `issue-screen-surface-lifecycle.md`，**未落码**。交接 `handoff-screen-35.md`
- 2026-09-24 17:3x · **#43 真人验收轮（Goal 1 三关系）✅**：YZ 在旁。① 自活闭环（`sva :10`，真值 `import -window root` 一致）② 关系 3b 人 viewer（YZ 浏览器见 live + 实时变化，只读 405）③ 关系 2 现场（`svb` 建号/隔离/写入公钥操作 sva 面/单控制者 `input_taken`+`yield`/删 key 收回）。**新发现 F11**：viewer 首屏破图（bridge 空 `since` 回退 + `parse_qs` 丢空值）→ 已修；另复现 F9 `Restore pages` 气泡。详情 `screen-verify-usage-1.md`「真人验收轮」。余：提交（bridge F11 + surface `--onlyvisible`）
