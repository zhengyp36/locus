# design｜screen 协助真人（Goal 2 / 关系 3a）工作稿 · 2026-09-24

> **状态**：工作稿（与 YZ 讨论已定方向；落码前以此为准）。2026-09-24 修订：流程改为"**先连接/握手、后同意**"；授权 = **一条连接**（连接 + nonce，**无会话凭证**）。2026-09-24 二次修订：身份改为 **公钥**（弃号码/通讯录，改真人机上一张"公钥登记表"）；认证做成**独立包 `screenlab/auth/`**，接口已冻结（§3.1）。**2026-09-25：E1–E5 完成（真机验收通过），结论已回写权威分册 `cogos/docs/design-agent-tools.md` §17；后置项见 §6。**
> **来源**：2026-09-24 与 YZ 的讨论（接 `handoff-screen-39.md`：Goal 1 收尾 → 下一线 Goal 2）。
> **目标（唯一约束）**：`spec-screen-1.md` §0.0。本稿只把目标当约束，其余都是方案，可改。
> **纪律**：本稿是**使用层**方案（怎么用合理/方便），不写内部实现；认证只记结论、**不再设计机制**。

## 0. 目标与边界

- **关系 3a**：真人在**自己机器**上操作，agent 接入**协助**。endpoint 在真人机，可能非 Linux；真人有物理屏、常驻在场；**真人可随时拿回**，授权主体是**人**。
- **与 Goal 1（关系 3b / agent 机）的根本差别**：
  | | Goal 1 | Goal 2（3a） |
  |---|---|---|
  | endpoint | agent 机 | **真人机** |
  | 屏/人 | 无人无屏（headless） | **有屏有人常驻** |
  | 授权性质 | 持久关系 = **给账户**（信任） | **一次事件 = 临时、可即时收回** |
  | 凭证 | 账户/密码/公钥 | **不交出账户、无会话凭证**：身份 = agent **公钥**（唯一），授权 = **真人本地确认这条连接** |
  | 收回 | 改密/删 key（滞后） | **一键、即时** |
  | 平台 | Linux/X11 先行 | 需覆盖 Linux/Windows/macOS/Android |
- **不在本线**：3b（Goal 1 已交付）；跨 provider（跨飞书租户）协助——那要回到"中心服务"档，另案；**Wayland 暂缓**（不追求覆盖所有情况）。
- **本线平台范围**：先 **Linux/X11 + Windows + macOS + Android** 中实际会用的；**Wayland 先不做**。

## 1. 使用层模型（agent 视角：同形）

- agent 看到的是一个**与"自己的电脑 / 别的 agent 的电脑"同形**的 `computer` 对象：同一 `screen_capture` / `screen_act`、同一 `ComputerSession`（graphics 面；term/fs 可选，默认只 graphics）。
- **agent 不需要为"协助真人"学任何新动词**——这是最值钱的一点。
- 与 Goal 1 的差异只有**四件事**（全是用法约定，不牵动动词）：
  1. **临时入场**：凭证不是长期账户，是**一条连接**的许可；
  2. **close = 松手/断开协助**，绝不关真人桌面/应用；
  3. **可被抢占**：真人有最高优先级，随时能接管；
  4. **收回显式可查**：授权一旦失效，agent 立刻能知道。

## 2. 流程（接入 → 会话 → 退场）

> 前提：真人要 agent 协助时，**双方一定已相互认识**（关系已建立）。故无需配对仪式，如人换存号码。

1. **真人开口**：真人在飞书对 agent 说"来协助一下"，并给出**通道**（怎么连到真人机；发起方永远是真人）。飞书只做**发起 + 通道交换**。
2. **agent 连接 + 握手**：agent 经通道连过去，发**自己的公钥**；服务端拿它查**本地公钥登记表**——不在表里直接拒绝，在表里则发 **nonce**，agent 用私钥签回，服务端用**登记表里那条公钥**验签。**连接在同意之前已建立，但此刻只握手、不建会话**。
3. **真人机确认**：验签通过后，向真人提示**登记表里的 `alias+name`**（**不采信客户端自报**），请他确认（是谁 · 授什么能力 · 直到收回）。**v1 用 CLI/事件，后换弹窗**。
4. **人点同意**：本地确认（OS 层）+ 授权**本次连接** + 勾选能力。
5. **开通会话**：在同一连接上给 agent 开**同形 `ComputerSession`**（一次同意即带操作能力，**不再"默认只读起步"**；见 §3.2 权限档）。
6. **会话中**：单控制者；**真人一上手（本地键鼠）→ agent 自动转观察态 / 可被抢占**。
7. **退场**：agent `close` = **松手**（礼貌断开）；真人**收回** = 断**本次连接**（即时）/ 删通讯录条目（长期）。
8. **感知收回**：agent 下一次任何调用**立即返回 `revoked` / `channel_closed`**（绝不挂死）；`state` / `info` 可查是否仍有效。**不推事件**（沿用 §0.0 §3）。
9. **重连**：收回后再用，必须**重走第 2–4 步**（重新握手 + 真人再点一次）；**不存在可复用的离线授权**。

## 3. 分层与各层用什么

**认证到此为止，不再设计机制。** 身份 = **公钥**（唯一，配一把私钥）；**号码 / 名字只是展示用的别名**，退到**通讯层（飞书）**，不进认证。真人机上只有一张**本地公钥登记表**（`{pubkey → {name, alias}}`），公钥经飞书消息登记（与人存电话号码同构）。

| 层 | 用什么 | 状态 |
|---|---|---|
| 身份 | **公钥（唯一）**；name/alias 仅展示、可重 | **已定，不再设计** |
| 验证 | **Ed25519 数字签名**（服务端发 nonce，agent 私钥签，用登记表公钥验） | 已定（就是签名本身） |
| 授权 | **真人本地确认**（显示登记表里的 name/alias + 能力 + 直到收回） | 已定 |
| 本地确认入口 | CLI/事件先行，弹窗后置（同一 hook） | v1 |
| 传输 | **tailscale（已定）** | 见 §4.2 |
| 会话凭证 | **无**：一条连接 + nonce 定界；不做短票，无可吊销的离线凭证 | 已定 |
| 收回 | 即时 = 断连接；长期 = 删登记条目 | 已定 |

**唯一要守的一句**（不是新增设计，只是别写错）：**连接自报的公钥不当真，只认登记表里存的那条。**

**两侧存什么**（结论）：
- **服务端（真人机）**：长期只存**公钥登记表 `{pubkey → {name, alias}}`**；运行态存**连接** `{pubkey, 建时, 能力位, state: active|revoked}`；nonce 瞬时、验完即弃。**不存签名、不存会话票**。
- **客户端（agent）**：只存**自身私钥**（身份）；不存对方公钥（对方由真人 UI 确认，不走签名验证）。

### 3.1 认证接口（已冻结，落码用）

独立包 **`screenlab/auth/`**，**与 `screen/1` 不混**（自带协议常量/版本，只复用 transport 的 `Channel` framing）。认证是**同一 socket 的第 0 阶段**，过了才进 `screen/1`。

- **`Registry(directory)`**（纯逻辑、无网络、可单测）：
  - `add(pubkey, *, name="", alias="", overwrite=False) -> Record`：重复且 `overwrite=False` → `raise DuplicateKey(existing)`；`overwrite=True` → 替换。
  - `remove(pubkey) -> Record | None`（= 长期收回）、`get(pubkey)`、`list()`。
  - `Record = {pubkey, name, alias}`，主键 = 规范化 pubkey。
- **`AuthServer(registry, *, consent, timeout=60)`**：`serve(chan) -> Record | None`。
- **`consent: Callable[[ConsentRequest], bool]`**（`ConsentRequest = {request_id, record}`）；v1 = `auto_consent` / `stdin_consent`；**弹窗同一签名**。
- **客户端**：`AuthClient(key).attach(host, port) -> Channel`；`Key.generate(path)` / `Key.load(path)` / `key.pubkey` / `key.sign(data)`。
- **协议 `screenlab-auth/1`**，帧：
  `hello{pubkey}` → `challenge{request_id, nonce}` → `verify{request_id, sign}` → `result{ok, ...}`；
  错误码 `unknown_key / bad_sign / expired / denied / malformed`。
- **编码 / 文件**：pubkey=`base64(raw 32B)`、sign=`base64(64B)`、nonce=`base64(32B)`；登记表 `<dir>/registry.json`（数组）；agent 密钥 `<path>` JSON `{pubkey, privkey}`。
- **开关**：仅 `--tcp --auth <registry>` 启用；Goal 1 的 Unix socket 路径**不动**。

### 3.2 认证之后的连接管理（会话 / 席位 / 模式）· 已定（2026-09-24 落码）

> 认证只开"门"。"过门之后谁在驱动这块桌面"单列一层来管，与 `screen/1` 的传输/动词不混。**本轮已按目标落码**（见下"本轮已落"）；**自动抢占/分源**等按目标推为后置（见"后置"），不阻塞。

**三层（连接是管子，别把图形状态挂上去）**

| 层 | 持有 | 归谁 |
|---|---|---|
| 连接 | socket + auth 门 + framing + snapshot 世代 | `proto`（纯管道） |
| 会话 | 附着哪个真实 DISPLAY、屏幕、**单一控制者**、**物理输入抢占**、参与者集合 | `service/session`（每账户一实例） |
| 席位 | 一条连接 join 后的身份：`observer` / `controller` | 状态属会话，不属连接 |
| 分源 | 物理输入监视（平台件）→ 通知会话 `preempt` | `service/presence` |

- **身份/模式挂连接，但逻辑归 server**：连接只持句柄（auth 的 identity + server 发的 seat id），role/抢占/让出全在 `session` 走同一把锁；连接 handler 只转发帧。
- 代码现状：`service/channels.py` 即**会话**（未改名；`Channels` = 会话，channel 记录 = 席位）；已补 `generation`、席位 `identity`。daemon 侧：`ConnState` 持席位 id + 验证过的身份 + 本连接快照代；`op_open` 用 auth `Record` 定席位身份；`op_state` 暴露 `seat`；`revoke_all` 供本地 `cancel` 调用。

**控制权**
- **只有真人是绝对抢占**（真人不在锁内，靠物理输入检测直接夺权）。
- **agent 之间不互抢** —— §0.0 约束"持有者**显式交还（`yield`）**他人才能接"，属目标导出，不松。
- **空闲自动让出（防锁死）**：在"只能显式交还"下，闲置/挂掉的持有者会永久占锁；`capture` 不需要控制权，故"只看不做"时让出无损失。倾向空闲 N 秒自动让出。
- **取得控制权即作废 snapshot 世代** → agent 必须重新 `capture` 才能 `act`（"看清楚"由此结构性保证，不靠定时器）。

**进入门槛（只做 mechanical 的部分）**
- 倾向：agent 进入 `controller` 前要求**物理输入已静默 ≥ SETTLE**，防与真人抢及其余波竞态。**不**由服务端强制"取得后再等 T 秒"——"看清没看清"是 agent 侧决断（§0：服务端只做 mechanical）。

**不推事件**
- agent 靠每次调用返回（`not_operating` / `input_taken` / `stale_snapshot`）+ `state` 感知被降级；`state` 带 `session.controller` 与 `seat.role`。

**未定（续讨论）→ 已定（2026-09-24，按 §0.0 推出，已落码）**
- **generation 归属**：归 **Session**（会话级单调计数器）；`capture` 盖章、`act` 校验、**控制权释放即滚代**（`yield`/`close`/断连）。快照只在铸造它的那一代有效，跨代即 `stale_snapshot`。落 `service/channels.py` 的 `generation`。
- **取得控制权即作废**：不单列"take"事件。控制只在**释放**时滚代，故"上一控制者/旁观者的旧快照"在新控制者接手后一律作废 → 必须重新 `capture`；不由服务端强制造次 capture。
- **`input_taken`**：**拒绝**，不排队（服务端只做 mechanical，排队=替 agent 决策 + 延迟注入危险）。
- **动词**：**复用 `open(role)`**（observer/controller），**不新增 `mode`**；席位内不引入新动词族。
- **控制者数量**：**单控制者**（§0.0"任一时刻至多一个有效操作者"）；无多 controller 竞选。
- **seat 身份**：过 auth 后，席位身份取 **server 验证过的 `Record`**（`subject = alias|name|pubkey[:16]`），不采信客户端自报；`state` 暴露 `seat`（`role`/`subject`/`identity`）+ `screen.generation`。未启用 auth（Goal 1 unix 路径）时维持旧行为。
- **本地取消入口**：复用 slice 2 的 consent socket，新增 `cancel` → daemon `revoke_all`（清席位、滚代、关连接）；agent 下一次调用即 `channel_closed`。真人入口 = `consent --cancel`（弹窗同签名）。
- **consent 措辞**：改为"允许 **加入本次协助会话**（observe + operate，直到收回）"，不再说"授权此连接"。
- **权限档**：**取消**（不做"默认只读起步 → 抬升"）。一次同意即带操作能力；只读/让出是 **agent 侧礼节**，非协议态。§2 step5 与 §6 据此更新。

**后置（下一轮，收口 3a）**
- **分源**（物理 vs 注入）：**XI2 raw 为主**、轮询降级。**已落靶机（2026-09-24 #45）**：`xinput test-xi2 --root` 按 source device id 分（XTEST 设备 id = 我方注入，其余 = 物理），无需 evdev/root；见 `screen-assist-exp-log.md` §6。
- **真人自动抢占**：**已落（#45）** —— 物理输入 → 当前 controller 降 observer + 滚代（`Channels.preempt`），`service/presence.py`；靶机实测通过（exp-log §7）。
- **`SETTLE` / `IDLE`**：**未做**（参数待定）——进入 controller 前的静默门槛、空闲自动让出。
- **物理热键**取消入口：**未做**（§4.7）。
- 目标只要求"可随时拿回"，已由显式收回（断连 + `cancel`）满足；以上是体验/稳健升级。
- **弹窗（slice 3）** + **附着真人现有会话**（surface 生命周期线）：**attach 链路已落并 tailnet 端到端验证（#45）**；弹窗未做。

## 4. 其他环节（怎么做 · 思路）

### 4.1 附着真人现有会话（不新开面）
Goal 1 是"新开一块 Xvfb"；3a 必须**附着真人当前那一个会话**。各平台只在这两处不同（同意 + 采集/注入），上层统一：
- **Linux / Wayland**：`xdg-desktop-portal` 的 `RemoteDesktop` + `ScreenCast`/PipeWire；采集与注入都走 portal，需会话/应用同意。
- **Linux / X11**：沿用 Goal 1（Pillow `ImageGrab` + `xdotool`/XTEST），但目标是**已有 :0/:N**，不是 Xvfb。
- **Windows**：helper 必须活在**交互会话**里——Goal 1 已证 sshd 在 Session 0、抓不到屏；采集 Pillow/GDI，注入 `SendInput`。免端口：helper 出站长连。
- **macOS**：TCC（**屏幕录制 + 辅助功能**）由系统弹同意；采集 `ScreenCaptureKit`、注入 `CGEvent`；helper 走 launchd。
- **Android**：采集 `MediaProjection`（+ 同意），注入走 **Accessibility Service**；或 app 形态（Goal 1: Android 只挂 graphics 面）。
- **共性**：都是"**平台自己的同意 + 平台自己的采集/注入**"，我们只统一上层（身份/授权/动词/收回可见性）。

### 4.2 传输（已定：tailscale，先不引入别的方式）
- **直接用 tailscale**：它自带控制面 + DERP 中继 + WireGuard（自动打洞、打不通才中继）→ **免开端口、免 NAT、免自建服务器**；跨平台齐（Linux/Windows/macOS/Android）。Goal 1 跨机 `view` 已在用 tailnet，环境现成。
- **分工**：WireGuard 负责**管道**（已认证 + 加密，不用再派生会话密钥）；我们的**签名负责"是哪个面孔"**（号码是它的别名）；**授权仍在我们层**（通讯录 + 人点同意）。
- **粗边界对齐 Goal 1 §7**：tailnet 成员资格 = 粗粒度、设备级、不按人收回。
- **两件要记的**：① 真人机需入同一 tailnet（入场成本；将来跨人可用 tailscale **node sharing**，不必并入同一 tailnet）；② **防火墙/端口放行**仍是 Goal 1 的已知副发现（firewalld 默认只放 ssh）——绑 tailnet IP 或显式放行。
- **飞书只做三件事**：发起（真人开口）、**通道交换**（把连法给 agent）、**公钥登记**（一次性，人保存）。**握手与同意都不过飞书**（握手在连接上、同意在真人机本地）。另作 **out-of-band 兜底**（§4.7 的飞书远程停）。

### 4.3 会话与收回感知
- 一段协助 = **一条连接**：以"**连接 + nonce**"定界，**不做短票**——先握手验身份，真人同意即授权这条连接；**停连接即失效**，无离线凭证要吊销。
- 收回后再用须**重走握手 + 真人再点**（§2 step9）。
- **感知**：沿用"**不推事件**"——靠每次调用返回 `revoked` / `channel_closed` + `state`/`info` 可查；关键是**立即且明确**（Goal 1 的 F1 挂死是反面教材）。

### 4.4 close / 退场语义
- 协助模式 `close` = **断开协助**，不关真人桌面、不关应用、不动真人会话状态。文档要把"这里 close ≠ 关电脑"写白。
- 真人的"收回"是**单方面强制断开**；agent 的 `close` 只是礼貌退场，两者不对称。

### 4.5 单控制者与真人优先
- 单控制者不变；**真人本地一上手 → agent 自动转观察态 / 可被抢占**，避免与真人争输入。
- 礼节：察觉被收回或真人接管时，agent **立即停止注入**（等同 `yield` 后不能动手）。

### 4.6 平台适配的切法（平台相关三块 vs 平台无关一块）
- **分界线 = mechanical vs semantic**（`spec-screen-1.md` §0/§6）：平台差异属 mechanical，下沉服务端；客户端不含平台逻辑。
- **平台无关核心（一份）**：session/世代、单控制者+yield、nonce+签名校验、收回、连接生命周期。
- **平台相关（每平台一份）**：
  1. **采集 + 注入**（传统 adapter/backend）：X11=`ImageGrab`+XTEST；Wayland=portal `RemoteDesktop`+`ScreenCast`/PipeWire；Windows=GDI+`SendInput`；macOS=`ScreenCaptureKit`+`CGEvent`；Android=`screencap`+Accessibility。
  2. **装配**：怎么装、怎么进**交互会话**、怎么自启（Goal 1 只有 Linux 的 `install-machine`）。
  3. **同意入口**：portal / TCC / 托盘 / 调试授权。
  > 3a 比 Goal 1 多出来的平台面是 **装配 + 同意**，不只是 adapter。
- **纪律**：**不依赖平台**（mechanical 归一化）**＋ 最小描述平台**（behavioral 只给粗先验）。协议动词不因平台改变用法、无 `--portal`/`--uia` 开关。
  - **只给"身份 + 能力"，不给"行为手册"**：保留 `ostype`（粗先验，防低级错，如别在 Windows 按 Cmd）+ `info()` 的能力位（有哪些 `act`）+ 运行态（`displays()`/`state` 的 geometry、pointer，属实时状态非平台信息）；**不给**点击语义/修饰键/滚动方向/菜单约定。
  - **理由**：环境描述是对现实的**静态假设**，会过期/误导（自定义 DE、改键、RDP、VM、偏好）；**屏幕是地面真值且实时更新**，**真人是活的 oracle**。给多了既成为"按平台维护行为手册"的负担，又诱导 `if os==` 分支。
  - **获取途径优于元数据**：**看（capture）· 试（act→capture）· 问（真人）**。第三条是 3a 独有优势（Goal 1 无头无人）→ **3a 可比 Goal 1 给得还少**。
  - 边界：描述是**给 agent 用的数据**，非让**客户端**写 `if os==...` 分支；能力差异（Android 无 hover/右键、`input text` 不支持非 ASCII）走 `info()` **自述**；坐标一律归一化（Windows DPI、Wayland 局部坐标、Android 刘海/旋转各不相同）。
- **难点排序**：不是"多平台"，而是"**附着现有会话 + 平台同意**"，复杂度比 Goal 1 的"自建面"高一档。**Wayland 先不做**（Goal 1 空白、E5 证 XTEST 对原生 Wayland 无效、且需 portal + 虚拟设备分源，成本高）——本线从 X11 起，其余平台按"实际会用的"排。另注意 **macOS**（本轮问题未列，但若在用的机器是 Mac，它可能第一优先）。
- **验证组织**：按 **平台 × (采集/注入/同意/收回)** 矩阵，各平台用**自己的地面真值**（X11 `import -window root`、Windows 截图、Android `screencap`）；沿用"只用公开入口真用 + 真值对照"。
- **实施序**：**以真人机现实为纲**——先打通实际会用的平台（附着 + 收回），再扩。

### 4.7 真人侧的收回/取消入口（分源原则）
- **核心难点不是"悬浮窗 vs 热键"，而是"取消入口不能被执行 agent 合成输入的那条流碰到"**：悬浮窗会被注入点击误命中，全局热键会被注入按键误触发——agent 的注入走同一条输入流。
- **注入方自己最清楚**：我们是注入者，能识别自己的事件 → **取消热键只对"非我注入"的事件生效**，位置无关、无需真人移动窗口。
  - Windows：low-level hook 的 `LLMHF_INJECTED`/`LLKHF_INJECTED`；Linux/X11：XTEST 由我们发出（物理键走 evdev，XTEST 不经 evdev）；macOS：`CGEventTap` 按 event source / 源进程 pid 过滤。
  - **Wayland 例外**：注入经 compositor，未必我们发；但 compositor 视 portal 注入为**虚拟设备**，仍可区分——又一 Wayland 难点。
- **入口分层**：① 主 = **物理热键**取消/收回（即时、无位置）；② 辅 = **小悬浮指示器只做状态灯**（`click-through`、不接点击，避免误点 + 提供"协助中"可见性）；③ 兜底 = **系统自带共享指示器**（macOS 菜单栏 / GNOME ScreenCast 指示 / Android MediaProjection 通知）+ **飞书远程停**（out-of-band）。**不把"点悬浮窗"当唯一取消手段**；真人"别乱动窗口"不是可靠约束。
- **同一"分源"逻辑兼作抢占判定**：检测到非注入的**物理输入活动** → agent 自动转观察；agent 每次动手前须确认仍持控制（比"求真人别动窗口"可靠）。
- **注意**：`snapshot_id` 世代**不会**自动发现"人移了窗、agent 还没 act"之间的漂移（§2 明确不做逐像素比对）→ 防误点靠**单控制者 + 物理输入抢占**，不能只靠世代。

## 5. 与 Goal 1 的关系 / 可复用

- **同**：协议 `screen/1`、客户端动词、daemon 主体（角色 `observer`/`controller`）、`ComputerSession` 形态。
- **可直接搬**：单控制者 + `yield`；存活预检（F1）；ScreenCast 流单消费者但**服务内可 fan-out**（P1 分发 ✅）；**像素先行**（a11y 在 Wayland 真人桌面坐标不可用，A1 已证伪 → 不作要求）。
- **反面教训（3a 约束更硬）**：
  - A1：关 ScreenCast session 会**崩掉整个 headless shell** → 在真人机上绝不拆真人会话，只读/受控附着。
  - portal 授权"每次弹框" = 打扰真人 + 可见痕迹 → 收回机制不能靠反复弹框。
  - F6/F8/F9 同源是"进程生命周期没人管"；3a 里真人的会话生命周期**完全不由我们管**，只能寄生。

## 6. 未决 / 待讨论

- ~~**默认只读起步 & 权限抬升**~~ → **已定（2026-09-24，§3.2）**：**取消权限档**。一次同意即带操作能力，避免二次弹框=打扰；只读/让出作为 **agent 侧礼节**，非协议态。
- **"真人优先/抢占"如何判定** → **已定思路（§4.7）**：靠**物理/注入分源**（检测非注入的物理输入活动 → agent 自动转观察）。遗留：**Wayland** 下注入经 compositor，分源需靠"虚拟设备"标识，待验。
- **画面范围**：整屏 vs 单应用窗口。整屏最简但隐私（真人桌面全暴露）；窗口级需窗口跟踪，难度高一档。（倾向：整屏先行 + 人在场。）
- **attended 边界**：3a 是否只做"人在场"？无人值守（帮家人/远程）与"真人可随时拿回"冲突 → 倾向不算 3a。
- **helper 常驻 vs 按需 + 同意入口形态**：真人机上的 helper 需在交互会话内、能随时响应同意 → 倾向常驻托盘 + 按需开流。
- **agent 的跨会话学习留存**：真人机的桌面约定/偏好属"效率知识"，是否落盘复用（Goal 1 原则：延续状态放磁盘）。
- **跨 provider（跨租户）** 是否列入 Goal 2 范围（倾向：不列，留"中心服务"档）。
- ~~**传输选型**~~ → **已定：tailscale**（见 §4.2）；唯一遗留是"真人机入 tailnet"的入场成本与 port 放行。

## 7. 靶场（3a 闸门）

- **用靶机 `surface-centos-9` 的"真实桌面"当 X11 闸门**：新建账户 + 登录（`VBoxManage controlvm centos9 keyboardputscancode` 注入密码，或配 **GDM autologin** 更稳；**别 reboot**，靶机有 dracut 前科）→ 得到**真实 XFCE/X11 会话**，验"**附着现有真实会话**（非新建 Xvfb）"这一半。
- **意外好条件**：**VBox 键盘注入在 guest 里=物理设备（evdev）**，我们 `xdotool`=XTEST（注入）→ 可在 VM 上**真测"物理/注入分源"**（§4.7：取消热键只认真人、抢占判定）。
- **Wayland 先不做**（本线暂缓；不追求覆盖所有情况）：portal 附着 + 虚拟设备分源成本高，留待需要时另起。
- **偏差**：真人"在场"是**模拟**的（主机侧看 VBox 窗口或不看）→ 验机制够用，验体验不够。
- **倾向**：先打通 **X11 全链**（附着 + 同意/收回 + 分源 + 抢占）——这也是本线起点。

## 8. 规则与纪律（沿用 `screenlab-rules.md`，本线特别强调）

- **一切从目标出发**：判据 = `spec-screen-1.md` §0.0 + 通用规则（易用性）；**不从代码、不从"谁定的"推**。只有 §0.0 未闭合项才值得讨论；能推的**自决并记录**，推不出的**通知 YZ 后停下等**。
- **10 分钟闹钟**：动手前 `set_timer(600s)`；到点 ① 对照 §0.0 查偏航，② `ctx.py` 查上下文（≥150K / 逼近 → 交接 + 通知）；再设下一个。**YZ 在场讨论时不用闹钟**（并取消已设的）。
- **实验有记录**：3a 实验另开日志（拟 `screen-assist-exp-log.md`），逐条「判据 / 方法 / 结果 / 结论」；结论定案回写本稿 / `cogos/docs/design-agent-tools.md`。
- **每完成一步** → `tools/feishu_notify.py` 通知 YZ，**不等回复、立即下一步**（含双引号时用写文件 + stdin）。
- **命令走 `terminal_exec`**（非阻塞，等唤醒事件）；不用 `sleep` 结束命令；管道被后台进程持有 stdout 会永久 busy。
- **不提交**：改动一律不 `commit` / 不 `tag`，等 YZ 定。
- **验收不用自写 e2e**：以 agent 身份、只用文档公开入口真用 + **地面真值**（`import -window root`）对照。
- 交接阈值：上下文 ≥150K 或路径偏 → 就地更新进度 + 写 handoff + 通知。

## 锚

- 目标：`spec-screen-1.md` §0.0
- 体系：`design-screen-system.md`；生命周期/命令层：`issue-screen-surface-lifecycle.md`
- 号码体系：`../cogos/cogos/phone/`（`Number(provider, number)`）、`../cogos/cogos/feishu/telecom.py`
- 平台实测：`screen-exp-log.md`（E5/A1/A2/P1 等）
- 上一轮：`handoff-screen-39.md`；Goal 1 状态：`screen-goal1-progress.md`
