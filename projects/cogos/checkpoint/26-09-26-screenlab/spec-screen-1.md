# spec｜screen/1 图形面（看屏 / 操作）· 2026-09-20

> **范围**：图形化看电脑——协议 `screen/1`、图形服务形态、图形客户端动词、平台适配与验收。
> **依据**：`handoff-screen-01.md`（协议/客户端/行业现状）＋ `checkpoint-3.md` §五（两台真机实测约束）。
> **权威分册**：图形面并入「电脑」，最终进 `cogos/docs/design-agent-tools.md`（工具分册）；本稿是落码后的**工作稿**，未定案前以本稿为准、定案后回写分册。
> **状态**：**目标已于 2026-09-21 拉通（§0.0，唯一约束）**；Linux/X11、Windows、Android 实测均通（§7）；**协议 `screen/1` 已定稿（09-20，§1；09-23 删 `paste`）**；§10 未决已清账（09-23，逐条标注）。**图形服务持久形态已定**（账户级 socket 权限 + "开一个程序"生命周期，§7）。

## 0.0 目标（目标即约束 · 2026-09-21 拉通）

> **本稿只把下面这段当约束。** §0 及以后（定位 / 术语 / 形态 / 协议 / 平台适配 / 实现）都是**为目标服务的方案，可改**；实验结论与"已定案清单"同理——是**素材与方案**，不是约束。

**一句话**：让每个 agent 拥有一台"自己能用"的电脑（账户级），图形界面是这台电脑的一项能力——agent 能操作它、能得到反馈；这块界面平时不抢屏，需要时能和真人共屏。

**前提（已定）**
- 有若干 agent；**每个 agent 配一个电脑账户**，经 ssh 登录使用。**账户是归属单位，不是物理机**（一台机可以有多个 agent 账户）。
- 图形只是"用这台电脑"的能力之一，与 `term` / `fs` 并列。

**为什么必须走图形界面（动机 · 2026-09-21 YZ 补）**
- **文本方式上网易被屏蔽**：纯文本 / 无头 HTTP 通道容易被反自动化拦下。**图形界面 + 像真人的操作**正是绕开这类屏蔽的手段 → 所以 **"像真人、不被检测"属于目标**，不是可选优化。
- **很多应用只有图形界面可用**：没有文本 / API 通道，图形界面是唯一入口。

**核心能力**
- agent **能操作图形界面且有反馈**（发动作 → 读回结果，闭环）。
- **操作要像真人、不被检测**（理由见上"动机"）；这是图形路线**成立的前提**，不是可选项。
  - 它**牵动"不抢屏"的形态选择**：headless / 虚拟显示器 / surfaceless 渲染 / `webgl=null` 这类"自动化痕迹"本身就是指纹 → 与"默认不抢屏"存在**张力**，强度按"对谁隐蔽、隐蔽到什么程度"定。
- **占屏是独立的一件事**：反馈与操作**不依赖物理屏是否点亮**。默认**不抢屏**（不点亮、不独占物理输出）；**必要时与人共屏**。

**三种操作关系**
1. **自操作**：agent 操作自己账户对应的桌面。
2. **授权他 agent**：agent 授权**另一个 agent** 操作它那台电脑的图形界面。**授权 = 把账户给他**（用户名/密码或公钥）——软件不提供令牌/凭证层；承认这是**粗粒度、滞后、全量**的（改密码 / 删 key 才能收回）。判据只对**信任**场景负责（2026-09-23 裁决，`design-screen-system.md` D1/D2）。
3. **与真人之间**（两方向）：
   - **a. 真人机上**：真人在自己机器上操作、agent 接入协助。endpoint 在真人机，可能非 Linux；**真人可随时拿回**，授权主体是人。
   - **b. agent 机上**：真人查看 / 介入 agent 那台机的图形界面。endpoint 在 agent 机，授权主体是账户 / agent。

**由目标导出的约束（不是方案）**
- **任一时刻至多一个"有效操作者"**：服务内一把输入锁，持有者显式交还（`yield`）他人才能接（关系 2 已无细粒度收回，约束落在单控制者上）。
- 高层协调（语言）只做"我要操作 / 你等下"，**不负责防冲突**。
- **输出 / 输入通路不得留下"一看就是自动化"的可见痕迹**（强度见下"仍未闭合"）。

**多账户形态（2026-09-23 定，落码 `screenlab/install/session-create.md`）**
- 前提「每 agent 一账户 / 操作**自己账户对应的桌面**」要求**每账户一块独立图形面**；同一 VM 单 GPU 只能有一个 rootful 真 Xorg（DRM master 独占），故每账户一块**自管的 headless Xvfb**（`session-start.sh create`，账户自己的 systemd user unit 组：Xvfb + WM + 服务）。
- **反检测口径修正**：软件渲染（llvmpipe）**不是 Xvfb 特有**——没开 3D 的真人 VBox 桌面同样是 llvmpipe，浏览器可见面几乎无差（`navigator.webdriver` 仍为 false：注入走 XTEST，不是 CDP）。故 GL **不再作为形态裁决项**；登录风险由 IP / 行为主导，要真 GPU 指纹需多 VM。
- 待办仍留：真 GPU（目标 3）、Wayland 真人桌面（Goal 2）、授权粒度。

**不属于目标（方案层，随时可换）**
后端选型（X11/Xwayland/XTEST…）、`screen/1` 的具体形态、桌面形态（headless + 虚拟显示器）、a11y 与像素如何分工、"模式 A/B"的分法、用不用 systemd、per-user 的具体落地方式。
> **由上导出的清账（2026-09-24）**：a11y 既属方案层，则 **Goal 1 只承诺像素 grounding**——`capture`/`act` 的 `tree`/`element` 是候选实现，未落**不算欠账**（F4）。

**仍未闭合（补齐才算定）**
- 关系 3 的 **a / b 都要，还是只要其一**？
- agent 的电脑上**有没有物理屏与常驻真人**？（决定"共屏"是常态还是例外）
- ~~ssh 断开后桌面状态是否保留~~ → **已定（09-21）**：图形界面按**"开一个程序"**模型按需开 / 关；**要延续的状态放磁盘**（浏览器 profile 按账户固定复用），**不靠会话常驻**。
- ~~同一桌面**允许多少操作者 / 观察者**？~~ → **已定（09-23）**：多观察者 + 单控制者（`design-screen-system.md` D3）。
- 授权的**粒度**：整台电脑 / 某个会话 / 某个窗口？
- **反检测强度**：对谁隐蔽（普通站点 / 风控 / 定向检测）、隐蔽到什么程度？（决定是否必须用**真 GPU / 真显示器**的机器——现有 `webgl=null` 是缺口）→ **分析已开**：`design-screen-antidetect.md`（2026-09-25 与 YZ 讨论：拆四层；同机 Xvfb≈attach；剩余欠账=输入人类化；威胁模型待裁）

**与旧表述的差别（防再串）**：上一轮把"agent 不需要用屏、默认不占屏"当成了目标属性，甚至推成"agent 没有用屏需求"——**错**。正确的是：**反馈必须有（目标）**；**占屏是可选的输出方式（方案）**。

## 0. 定位

- **图形面 = `computer` 工具的第三个能力面**（继 `term` / `fs` 之后），**不是图域的一部分**；图域是它的第一个消费者。
- 与 `ComputerSession` **同 account/target**：电脑对象的一种能力面，不是新对象。
- **a11y 与截图不是两条能力**：同一 `capture`/`act` 的两条 grounding（数据通道 / 宾语类型），**路由在服务端**。
- **服务端只做 mechanical**；理解 / 决断 / 记忆 / 装配留 agent 侧（唯一智能主体、图不转文字）。
- 客户端**薄 = 不含平台逻辑，但含 agent 语义**；分界线是 **mechanical vs semantic**，不是 client/server。
- 纪律：工具只保证**能力完整、可控、可观测**，不规定"它该怎么用"。

## 0.1 术语与形态（09-20 定）

**面向 agent 是"工具 → 能力面"，面向实现是"客户端 / 服务"。** 两条轴：

| 概念 | 术语 | 归属 | 对应 |
|---|---|---|---|
| 工具 | `computer`（另有 `phone` / `web`） | agent | `ComputerManager` / `ComputerSession` |
| 能力面 | `term` / `fs` / **`graphics`** | `computer` 工具 | `ComputerSession` 的三个面 |
| agent 侧实现 | **图形客户端** | `computer` 工具的一部分 | 原型 `client.py`（`cli.py` 是其调试前端） |
| 目标机侧实现 | **图形服务**（graphics） | 支撑 `computer` 工具 | 原型 `daemon.py` |

- **`graphics` 是 `computer` 工具的第三个能力面**（继 `term` / `fs`）；`screen/1` 是这一面的协议。
- **三面的目标侧支撑是异构的、一面一个，不合并**：
  - `term` → sshd（远端）/ 本机 `$SHELL`（既有，不重造）
  - `fs` → sftp（远端）/ 本机 FS（既有，不重造）
  - `graphics` → **图形服务（自建）**：目标上**没有既有的通用"看屏/操作"通道**，且必须活在交互会话内（sshd 做不到）
- **统一只在 agent 侧**（`ComputerSession` 把三面并成一个会话对象），**不在目标机 wire 上统一**——故**不存在"一个服务全包 `computer`"的形态**。
- **图形服务借 ssh 做装配/运输**（Linux/Windows）：scp 投递 → ssh 触发会话内自启 → `ssh -L` 隧道；**不重造认证/传输**。Android 无 sshd，改走 LAN 直连/反连（或 `adb forward`），且**只有 `graphics` 面**（无 `term`/`fs`）。
- 类比：`phone` 靠 feishu 服务（外部既有）；`computer.term/fs` 靠 sshd/sftp（既有）；`computer.graphics` 无既有通道 → **自建图形服务**。
- **术语纪律**：目标侧一律叫**服务**，**不叫 agent**（避免与自驱 agent 混）；`daemon` 只是服务的*进程形态*；`CLI` 是图形客户端的调试前端，不简称"客户端"。

## 1. 协议 screen/1（09-20 定稿）

> **状态：定稿**。动词改名与坐标口径是走向 1.0 的一次性改动（wire 未对 agent 开放过，仍记 `screen/1`）。
> **边界**：认证不在协议里——`screen/1` 假定一条**已认证的字节流**（见 §1.4）。协议只做 mechanical。

**wire 照 MCP 形状**（不自造标准），自己只加语义（世代 / 静默 / 去重）。

```
info()      -> {protocol:"screen/1", platforms, modes, authority, grant}

displays()  -> [{id, name, geometry:{w,h}, scale, rotation, primary}]

state(display?)
            -> {display, pointer:{x,y}|null, focus:{window_id,title}|null,
                frame_hash, snapshot_id, grant}

capture(display?, mode=auto|pixels|tree,  # tree/auto 未实现；Goal 1 只出 pixels
        center?, size?,          # 归一化窗口；缺省全屏
        max_dim?,                # 渲染上限，与坐标无关
        since_hash?, wait_stable?)
            -> {snapshot_id, frame_hash, changed,
                window:{center,size},
                image?:{blob_sha, w, h},                    # w,h 是渲染后图幅，不是坐标空间
                tree?:[{id, role, name, bounds, clickable}]} # 候选，未实现；bounds 归一化

act(display?, op, snapshot_id)
    op ∈ {pointer|element|key|type|scroll}   # element 候选，未实现
      pointer:{x,y}(归一化) · element:{id} · key:{keys} ·
      type:{text} · scroll:{at:{x,y}, dx, dy}
            -> {ok, hint?:{frame_hash}}      # 只是提示；判稳定须再 capture

blob_get(sha) -> <bytes>                     # client 内部取，不裸露给 agent
```

### 1.1 坐标模型

- **agent 可见的一切坐标 = 归一化 0~1、相对整屏**；`act` 也收归一化坐标。
- **窗口 = `center` / `size`（归一化）**：放大局部看——同区域占更多像素，估坐标更准。
- **`max_dim` 只是渲染上限，与坐标无关**：图被缩放不影响归一化坐标；DPI / rotation / scale 由 client 换算成设备像素。
- **换窗口看图不改帧**：窗口只是同一帧的另一个视图；客户端用最近一次 `capture` 的世代即可（§2），agent 无需感知。
- `mode`：`pixels`（抓屏）/ `tree`（a11y 树）/ `auto`（服务端按次路由）。a11y 不是另一族工具，是同一 `capture`/`act` 的一条 grounding。**（`tree`/`auto` 未实现：Goal 1 只承诺像素 grounding；a11y 记候选，理由见 §0.0「不属于目标」。）**

### 1.2 状态：authority / grant

- `authority ∈ {owned, granted}`：**机器级**，装配注入，不协商。
- `grant = {capture: bool, input: bool}`：**运行时**，两个独立位（无障碍持久、MediaProjection 会话级）；仅 `granted` 机器会变，`owned` 恒真。

### 1.3 命名

- **`see` → `capture`**：避开与看图工具 `image_ctx.see` 同名。两者不同——`capture` 是**实时抓帧**（有世代、配 `act`），`see` 是**看图**（静态、可反复缩放注释）。
- **`caps` → `info`**：`caps`＝capabilities，与 `capture` 撞脸；`info` 是握手/自述（协议版本、后端、modes、authority/grant）。

### 1.4 传输绑定（非协议本体）与版本

| 平台 | 绑定 | 认证来源 |
|---|---|---|
| Linux / Windows | `ssh -L` 到目标 loopback | 机器账户（借 sshd） |
| Android · 装配期 | adb | USB + 设备授权 |
| Android · app | LAN + token | **独立配对协议**，不进 `screen/1` |

- **只做加法**，`protocol:"screen/1"` 不变；新字段可缺省，**缺省语义 = owned / 无限制**，老客户端不受影响。
- `capture` 无副作用（只读）；`act` 只接受当次帧的世代。

## 2. 快照世代 `snapshot_id`（实测依据）

- **实测**：加窗口装饰后输入框 y 从 158 → 185，按旧坐标点空。→ `act` **必须绑"当次看过的那一帧"**，不能拿旧坐标直接点。
- **P1 服务端校验＝token 身份**：`capture` 每次 mint 新 `snapshot_id`，`act` 必须携最新签发的那个；**act 后作废并签发新的 → 强制 act 后必须重看**。**不做逐像素比对**——屏幕一直在变（时钟/光标/动画/视频），逐像素相等会导致每次 act 都被拒。
- **agent 不接触 `snapshot_id` / `frame_hash`**：客户端按 display 自动绑最近一次 `capture` 的世代（**B 层代持；A 核心不代持**）。
- **去重**：客户端默认带最近 `frame_hash` 作 `since_hash`；命中 → `capture` 回 `changed:false`（省带宽、省 token），世代仍有效。
- **`act` 的返回只能当提示**：`act` 完成后即时抓帧可能早于 UI 渲染（原型实测），判定稳定态必须再 `capture --wait-stable`。
- **作用域＝连接内**，断连即作废；**同一 display 单活跃、串行**。
- **后置**：`frame_changed` 提示（不阻断）；`act element` 按 id **重新解析 bounds**（防布局漂移，随 a11y）；粗比对容差**不做**。

## 3. 变化感知（不推事件）

- **不发屏幕变化事件**（合 `design-agent-tools.md` §5.4 不做通用事件）。
- 靠 **`frame_hash` ＋ `wait_stable(timeout)`**：等到连续两帧哈希相同（静默）返回。
- `state` 给 `frame_hash`，供 agent 自己决定要不要再看。

## 4. blob 内容寻址

- 图 / 大 payload 走 **`blob_get(sha)`**，内容寻址天然去重；协议本体**不回大字节**。
- 与 phone 文件同口径：**字节不进 socket**，disk→disk。
- blob 是**在途介质**还是**持久资产**取决于裁决 1（§10）：`image_ctx`（有根）还是 `img-tool`（无根），两条 lineage 未并。

## 5. 运行时约束（本会话实测 · 设计级，进 spec 即生效）

1. **图形服务必须在目标会话内部**：GNOME Shell 的 D-Bus 抓屏对外部登录会话 `AccessDenied`（`Screenshot is not allowed`）；rootless Xwayland 根窗口 `XGetImage` 直接 `BadMatch`。**外部进程抓不了 Wayland 会话**——图形服务要活在目标会话里（会话内自启 / systemd user unit / 登录时拉起）。
2. **`snapshot_id` 必需**：见 §2。
3. **WM 是 `act` 可靠性的前置**：Xvfb 无 WM 时 `_NET_ACTIVE_WINDOW` 缺失、`getactivewindow` 报错、键盘事件跑到别处（实测误触发浏览器新标签页）；起 openbox 后 `windowactivate --sync` 正常。无 WM 时须显式 `windowfocus`。→ 成熟形态由 create 模式提供：每账户 Xvfb + WM（openbox）+ 服务，做成 systemd user unit 组（`session-create.md`）。
4. **工具选型定案**：
   - 抓屏：**Pillow** `ImageGrab.grab(xdisplay=...)`（自带 `xcb`，无需外部工具）。
   - 注入：**`xdotool`**（XTEST）；手写 python-xlib **不可靠**（Xlib RandR 错误处理 bug：`BadRRModeError object has no attribute sequence_number`，连接初始化排队错误在 `flush()` 时炸）。
5. **窗口级抓屏可用**：X 下 `import -window <id>` 出窗口尺寸图；整屏 `-window root`。属后置项。
6. **a11y（AT-SPI）未实现，且 Goal 1 不作要求**：`tree`/`element` 通道未落（§0.0 把「a11y 与像素如何分工」列为方案层）→ **Goal 1 交付 = 仅像素 grounding**；a11y 记候选。

### 5.7 Windows 特有约束（09-20 实测，Surface `192.168.1.112`）

- **Session 0 无桌面**：`sshd` 跑在 Session 0，在那里抓屏直接 `screen grab failed`、`GetCursorPos`/`GetForegroundWindow` 为空 → 图形服务**必须由启动项在目标用户的交互会话里拉起**。
- **必须开 per-monitor DPI 感知**：不开时 `GetSystemMetrics`/`GetCursorPos` 给**逻辑**像素（如 1280×853），而 GDI `all_screens` 抓屏给**物理**像素（1920×1280），150% 缩放下**图像坐标 ×1.5 ≠ 落点**（实测：要求移到 200,200，光标实际在物理 300,300）。修法：进程启动即 `SetProcessDpiAwarenessContext(PER_MONITOR_AWARE_V2)`，此后抓屏/坐标/注入三者同一物理空间。
- **传输走 loopback TCP**：Windows OpenSSH 不支持 AF_UNIX 端口转发，故图形服务监听 `127.0.0.1:<port>`，本机 `ssh -L` 转出。
- **标准账户必须属于 `Users` 组**：`New-LocalUser` 不会自动加组；不在 `Users` 就没有"允许本地登录"权限 → **登录界面根本不列出该账户**（SSH 不受影响，所以容易误判）。
- **注入 = `SendInput`（ctypes，无第三方依赖）**；`type` 走 `KEYEVENTF_UNICODE`（任意 Unicode，无需键位映射）；抓屏 = Pillow `ImageGrab.grab(all_screens=True)`（GDI）。
- 中文字符串经 `ssh`（GBK 控制台）会乱码，属显示问题、不影响功能。

### 5.8 Android 特有约束（09-20 实测，EMUI 10 / Android 10 旧机）

- **与前三平台相反：服务不驻留目标会话内**（Android 走 adb，服务在宿主）。设备侧只有 `adbd`，图形服务跑在宿主、经 `adb` 驱动；**没有"服务必须活在会话里"的坑**（这正是 Android 作为最便宜 adapter 验证场的原因）。这是**装配期形态**；最终形态是设备内 app 服务（见 §0.1 与 `checkpoint-5.md` §八）。
- **坐标三方同空间**：`screencap` 输出 = `input tap/swipe` 坐标 = `uiautomator bounds`，**无 Windows 式 DPI 偏移**。实测 a11y 中心点 (540,2012) 直接命中秒表按钮。
- **刘海/挖孔造成尺寸口径差但不影响注入**：`wm size` 物理 1080×2312，a11y 根节点 1080×2231（差 81px = 顶部 cutout），但**坐标原点一致**、点按不受影响；顶边探针（y=2060、2200）均命中。
- **`input text` 受限**：空格须转义为 `%s`，且**不能输非 ASCII**（中文/特殊字符无效）——中文输入需另找通道。
- **旋转会翻转坐标空间**：旋转后 `screencap` 尺寸与 `input` 空间随之翻转，须按 `list_displays.rotation` 修正。
- **a11y 树可用且顺手**：`uiautomator dump` 直接给元素树（text/resource-id/class/bounds/clickable），坐标与像素同空间；比 Linux AT-SPI 省事。
- **无 WM 概念**：`focus` 取 `dumpsys window` 的 `mCurrentFocus`，`pointer` 恒为 `null`；无 `windowactivate`。
- **息屏**：`KEYCODE_WAKEUP` 唤醒；长实验用 `svc power stayon true` 保持常亮。
- **授权/权限**：宿主需 `android-tools`（EPEL `33.0.3p1`）+ udev 规则；设备侧开 USB 调试并授权（华为 EMUI 可能需先切"传输文件"才弹授权框）。无线调试（Android 11+）在本机不可用。

## 6. 图形客户端形态

- 一套动词：`connect / info / displays / state / capture / act`（`blob_get` 由图形客户端内部取，不裸露给 agent）。`capture` 抓到帧后落成图，可直接喂给看图工具 `see` 细看/注释。
- **薄语义层**：图形客户端把 `capture` 的结果组装成 agent 可读的 `Block{text,image}`，把 `act` 的 `element|pointer|key|type` 归一成一次调用；**不做平台分支**（平台差异下沉 adapter）。
- **agent 不接触世代**：`snapshot_id` / `frame_hash` 由客户端按 display 自动绑（§2）。**客户端挂 `ComputerManager`**（每台电脑一个、单连接），`ComputerSession` 只当寻址句柄；agent 侧动词定名 **`screen_capture` / `screen_act`**。
- a11y 不是另一族工具，是 `capture` 的一条数据通道（`mode`）和 `act` 的一种宾语（`element`）。

## 7. 平台适配

| 平台 | 状态 | 通道 |
|---|---|---|
| Linux / X11 | **已通**（真机 + 每账户自管 Xvfb） | Pillow `ImageGrab` + `xdotool`；多账户 = 每账户一块自管 Xvfb（§0.0，`session-create.md`） |
| Linux / Wayland | **阻断 / 暂缓** | `org.gnome.Mutter.RemoteDesktop`（可达）+ `ScreenCast`/PipeWire（重） |
| Windows | **已通**（09-20，Surface `192.168.1.112`） | Pillow（GDI，`all_screens`）抓屏 + `SendInput`(ctypes) 注入；loopback TCP + SSH 隧道 |
| Android | **已通**（09-20，EMUI 10 / Android 10 旧机，USB） | `adb exec-out screencap -p` 抓屏 + `adb shell input tap/swipe/text/keyevent` 注入；服务跑宿主、走 adb |

- Wayland 原生通道 `org.gnome.Mutter.RemoteDesktop` 可 `CreateSession`（`SupportedDeviceTypes=7`、`Version=1`），但看屏要再叠 ScreenCast + PipeWire，暂缓。
- **Windows 形态（实测定案）**：专用**标准账户**（非管理员）占交互会话 → 图形服务挂该账户启动项、监听 `127.0.0.1:<port>` → 本机 `ssh -L` 隧道转出（Windows OpenSSH **不支持 AF_UNIX 转发**，故用 loopback TCP）。
- Windows 线不阻塞 Linux 线，挂起。
- **Android 形态（实测定案）**：宿主装 `android-tools`，服务跑宿主（`--backend android`），`screencap`/`input` 全走 `adb`；**唯一不需要"服务在目标会话内"的平台**。传输沿用宿主 Unix socket（本机）或 TCP（Windows 宿主）。Android **只挂 `graphics` 面**（无 `term`/`fs`）。
- **持久形态（Phase 2）——2026-09-23 更新**：`install-machine` / `add-agent` + 账户内 socket 已实现；鉴权问题**已由账户级 socket 权限解决**（socket 在 `$XDG_RUNTIME_DIR` 0700，同 uid 才能连；**无令牌/凭证层**，授权=给账户）。生命周期定为**"开一个程序"模型**（`screenlab open` 拉起 / `close` 停整套面，不随开机常驻；状态落盘）。见 `issue-screen-surface-lifecycle.md` C1–C12。

## 8. 验收环境（实测可用）

- **本机（主验证场）**：`DISPLAY=:0`，`XAUTHORITY=/run/user/1000/gdm/Xauthority`；Xorg 在 vt2、`gnome-xorg`、GDM 自动登录 zhengyp。
- **`192.168.1.212`（弱机 / 无头场）**：1 vCPU / 1.7G，`Xvfb :99` + openbox + chrome，内存余 ~1.2G。`ssh zhengyp@192.168.1.212` 免密；sudo 需密码。
- **Android 设备（09-20 新增）**：华为 `MAR-TL00`（`12d1:107e`），Android 10 / EMUI 10，1080×2312 @480dpi，顶部刘海。宿主直通 USB 进本机 VM；`adb` 1.0.41（EPEL `android-tools`）。

## 9. 实施路线（Phase 1 自洽工具）

- **最小图形服务 + 图形客户端 + CLI**：mechanical 子集 `info / displays / state / capture / act / blob_get`（原型期旧名 `see`），Unix socket，Pillow 抓屏 + xdotool 注入 + 内容寻址 blob + 快照世代。
- **验收 = LLM 在环**：用 CLI + 读图跑"看 → 点 → 再看"，在 `:0` 与 `:99` 两环境各跑一遍；**不必等运行时改造**。
- **图进 context 属接入阶段**，不是 Phase 1 拦路虎。
- 一切后置：事件推送、window 级抓屏、多显示器、云桌面、term/fs 收编。

**原型已落（09-20）**：`work/A/checkpoint/screen-lab/`（图形服务 + 图形客户端 + CLI，含 Windows/Android adapter，暂存——代码放哪见裁决 7）。四环境 LLM 在环验收通过：212 `:99`、本机 `:0`（解锁后）、Windows Surface（`screen` 标准账户交互会话 + loopback TCP + `ssh -L`）、Android `MAR-TL00`（`--backend android`，宿主服务 + adb）均完成 `capture → act → capture`（原型期旧名 `see`）；Windows 另验 Win+R 起 notepad 并打字，Android 另验秒表启动/暂停（`00:00.00 → 00:01.24 → 00:02.55`）。用法与验收细节见该目录 `README.md`。
**Android 观察**：`act` 的 `frame_hash` 逐次变化、过期 `snapshot_id` 被拒（`stale_snapshot`）、`since_hash` 回 `unchanged`、blob 内容寻址 `sha==frame_hash`——与前三平台行为一致，**adapter 接口零改动即可接入**（只加 `backends_android.py` + `--backend` 选择）。
**原型新增观察**：`act` 完成时即时抓的那帧**可能早于 UI 渲染**（实测 `key Escape` 后 `act` 回的帧哈希仍是面板打开态，`capture --wait-stable` 才拿到关闭态）→ **`act` 的返回帧只能当提示，判稳定态须再 `capture --wait-stable`**；`act` 的返回世代不足以替代一次显式 `capture`。

## 10. 未决（继承裁决，未定前 spec 相关处留口）

> **2026-09-23 清账**（`issue-screen-surface-lifecycle.md` §五）：逐条标注，非本轮讨论项。

1. 图 = 持久资产（`image_ctx` 有根）还是临时介质（`img-tool` 无根）——**仍开**（属图域，与本线无关）。
2. 自建电脑 vs E2B 类云桌面——**已定：自建电脑**（每 agent 一账户，已落码 `screenlab/`）。
3. 客户端薄到哪（纯管道 vs 含 agent 语义）——**已定：带薄语义层**（薄=不含平台逻辑、含 agent 语义）。
4. 先做哪个平台——**已定：Linux/X11 先行**（Goal 1）。
5. 是否给 212 sudo——**作废**（212 已不在当前环境）。
6. 旧遗留 4b 装配 / 按需加载与本线的关系——**仍开**（属 tools 线）。
7. **代码放哪**——**已定：cogos 子包 `screenlab/`**（非新仓）。
8. **是否做 Wayland 适配**——**已定：Goal 1 不做**，真人 Wayland 桌面归 **Goal 2**。
9. Xfce 会话 XSMP 残留——**作废**（现形态为每账户 Xvfb + openbox，不用 Xfce）。
10. 密码轮换 / 关 SSH 密码登录 / 收紧 firewalld——**已定：收回靠惯例、不写代码**（C11）；firewalld 放行 tailnet 已在装配期处理（§7）。
11. Windows 线何时重启——**仍开**（挂起）。


## 11. 依据与引用

- 讨论：`handoff-screen-01.md`（工具分域 / 协议 screen/1 / 客户端形态 / 行业现状 / 阶段划分）。
- 实测：`checkpoint-3.md` §三（X11 三段根因）、§四（Wayland 两通路）、§五（设计级结论）、§七（安全）、§八（系统改动）、§九（命令备忘）。
- 交接：`handoff-screen-02.md`、`handoff-screen-03.md`。
- 本会话实测与术语定案：`checkpoint-5.md`（Android 打通 + §八 术语/形态 + §九 协议 `screen/1` 定稿）。
- 工具口径：`spec-tools-a.md` §5（`ComputerSession`；`graphics` 为其第三个能力面）。
- 分册口径：`cogos/docs/design-agent-tools.md` §5.4 / §6 / §12；`cogos/docs/vision-system-design.md` §14 / §168–170。
- 代码面：`app.py:192` `_build_specs`；`tools.py:1131` `ToolRegistry`；`config.py:99` `render_system_prompt`；`consciousness.py:65-70`、`:68` `schemas`；`image_ctx/domain.py:36-56`、`image_ctx/tools.py:122` `see`。

> 纪律：结论先落本稿 / checkpoint，定案再更新权威分册 `design-agent-tools.md`；不替 agent 决定用法，发现设计问题回 checkpoint 记、不悄悄改设计。
