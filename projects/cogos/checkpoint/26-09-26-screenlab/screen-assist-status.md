# screen-assist-status.md · 3a 路线 + 进展（活文档）

> 唯一约束 = `spec-screen-1.md` §0.0（关系 3a）。本文件 = **路线 + 进展**，就地改，不追加成流水账。
> 新会话恢复：**读本文件 + `codebase.md`**，不必全量翻历史 / 重读代码。
> 相关：设计 `design-screen-assist.md`；实验 `screen-assist-exp-log.md`；规则 `screenlab-rules.md`。

## 0. 切会话须知（2026-09-25 11:55）

- **状态**：**E1–E4 ✅**（E4 于 #51 真机验收：真人真鼠标抢占 → `role=observer`；物理热键 → `REVOKED/channel_closed`；桌面双击「启动协助」无 untrusted、单实例一把锁）。**E5 已收尾**：#50 改动按关注点拆 4 个提交（`b853576` 信任 · `74aba3c` presence 抑制 · `b6e41e8` consent 单实例/编号 · `b3cc333` 分册回写），tag **`screenlab-goal2-3a-2026-09-25`**；3a 回写权威分册 `cogos/docs/design-agent-tools.md` §17。分支 `feat/screenlab-p2`。
- **当前焦点（#54）**：Windows 关系 3a——**W1 ✅ / W2 ✅ / W3 ✅ / W4 ✅**。W2 真机物理：鼠标/按键 → `PREEMPTED role=observer`；`Ctrl+Alt+Shift+Esc` → `REVOKED/channel_closed`。W4 产品入口：install.ps1 生成桌面+开始菜单快捷方式（`-Autostart` 另加登录自启），双击 = 托盘 `--manage-daemon` 拉起 daemon；真机 Session 6 验证 + agent capture 通（1920×1280），另远程操作 Chrome 访问 `cn.bing.com` 成功。工作树 **DIRTY**（新增 `install.ps1`/`consent_app_win.py` 改动）。详见 `handoff-screen-54.md`。
- **下一步（Windows 线）**：**W5 三判据验收 + 提交/tag/回写分册（待 YZ）**。
- **当前焦点（#55）**：**Android 远程控制线起步**——与 YZ 定了形态：**设备内 app**（采集 `MediaProjection`；注入 `AccessibilityService.dispatchGesture`，**只做手势不做语义树**）；传输 **tailscale**、开发期 **`adb forward`** 免网络；**复用 screen/1 + auth 核心一份**（agent 侧零改动）。M0 侦察过；**M1 构建链已就绪**（全用户态 `$HOME/Android`：JDK17 + cmdline-tools + build-tools34 + platforms;android-29），`cogos/screenlab/android/` 最小 app（无 Gradle 构建）已出 APK 并在旧机 **nova 4e / MAR-TL00（Android 10/EMUI 10/SDK29）** 装好、无障碍已开（YZ 完成安装）。**#56 已完成 Android M1/M2**：「串会话」复核**无真实跨会话**（terminal id 全局 + 闹钟续跑未进可见上下文，见 `handoff-screen-55.md` / `handoff-screen-56.md`）；**M1 ✅**（采集像素级对齐 screencap；无障碍注入命中按钮触发抓帧）、**M2 ✅**（app 内 `screen/1` 服务经 `adb forward` 跑通现有 `ScreenClient`）；**M3 ✅**（#57：通知「收回」+ 单控制者 + 服务单实例；物理触摸分源不可行→后置）。详见 §4。
- **当前焦点（#60）**：Android **M5 功能完成并真机验证**——`AgentRegistry` 读写（含 `alg`、base64 32B 校验、重复检测）、`AssistServer` alg 校验（`alg_mismatch`）+ `result`/`seat.identity` 带 alg、app 内「已登记 agent」列表（行=`别名 · alg:短码`，详情=全量 pubkey 可复制/删除，添加=粘贴 pubkey+别名），删除顺带断开该 pubkey 在线连接。**APK 0.2 已构建 + 部署**；真机用 UI 走通 add（落盘带 alg）/ 详情 / delete→在线连接 `channel_closed`，LAN 验 `alg_mismatch` + happy path，`pytest = 39 passed`。**剩余：M5 验收/提交/tag/回写分册（待 YZ）**。详见 §4。
- **当前焦点（#61）**：**Android 通用控制能力缺口**——真机演示（仅一次测试，非目标）暴露：坐标不准、`act` 只有 tap、无打字/导航/launch。清单 `screen-android-issues.md`（1 launch / 2a 坐标 / 2b 视觉 / 3 打字 / 4 导航 / 5 权限）。**待 YZ 讨论视觉**（适用于所有 GUI，架构级）。
- **交接（#61→#62）**：缺口已记录；`handoff-screen-61.md`。**新会话读完待命、不动手**；M5 验收/提交/tag/回写分册仍待 YZ（未提交、未 tag）。
- **当前焦点（#61）**：Android **真机演示 → 通用控制能力缺口**——LAN 单连接（一次同意）连上、info/open/capture 通；暴露**坐标映射不准**（tap 落点偏移：估微信开出支付宝、估 Chrome 两次无反应）、无导航/手势、无打字、无 Intent 启动。**澄清 consent = 每条 TCP 连接一次**（真实 agent 单连接 → 一次会话一次同意；多次弹窗系反复起连接）。缺口清单 = `screen-android-issues.md`。**#61 未改代码**。
- **交接（#61→#62）**：视觉定位讨论未开始；#62 首任务 = 讨论**视觉**（定位范式，适用所有 GUI）。见 `handoff-screen-61.md`。
- **#62 视觉工具脚本化**：工具实为 cogos 的 `cogos/image_ctx/`（see/mark/adjust_mark/unmark/coord；非 `research/vision/` 归档）。已定结论 + 待定 A 见 `design-vision-scripting.md`。核心信条：模型只看语义，几何全由工具做；裁剪/缩放唯一发生在 render。
- **#62 分支实验（62a/b/c）**：三平台屏变感知已做完 → `screen-change-detect.md`（X11 XDamage/SHM、Android 投影分块 diff、Windows DXGI；共性铁律"杀掉每帧 PNG"）。待定 F **已定**：传输/看屏分离 = **推变化事件（原生 damage + generation）+ 按需拉整帧 + 客户端按版本缓存**，不做帧流。产品码修正清单见 `design-vision-scripting.md`（待 YZ 定）。
- **#62 挂起 / 分支 #62a（2026-09-25 22:3x）**：#62 转入"传输与看屏分离"讨论（待定 F：服务端按变化推送/采样 + 客户端缓存 + 模型取图）。未决 = **服务端如何高效感知屏变** → 起子分支 **#62a**（`screenlab #62a`，见 `handoff-screen-62a.md`）做实验，产出平台×方法矩阵。**#62 本会话已挂起**（停干净：无 timer/terminal/后台）；父会话 session id `ses_f27b92b04ffeF5hz7zAFZPi026`（title `screenlab #62 - 电脑/视觉-讨论`），实验完 attach 回 #62 讨论。
- **#62→#63 交接（2026-09-26 00:5x）**：#62 已恢复并合并 62a/b/c 实验（`screen-change-detect.md`）；**F 已定**、待定 A 有推荐（帧内容寻址路径）。会话偏长，讨论转入 **#63**（见 `handoff-screen-62.md`）。**新会话读完待命、等 YZ 切会话**。已定 1–16 与传输修正清单见 `design-vision-scripting.md`。
- **#63（视觉 × 电脑工具 · usage-first，2026-09-26 02:3x）**：改从**目标 §0.0 推导**（不再堆机制/本体）。定：第一原则 = **工具保证"模型作用在它看到的那张图上"**（#61 打偏的根因）；模型面只要 5 个动作（看 / 指 / 放大 / 点 / 确认），**settle、帧库、传输、平台全内化**；settle = **事实层（revision+脏区）目标区域静默 T**（按区域判）；定位（窗口 / mark）**跨帧**、与内容分离；平台差异压成**一层后端**（`capture_raw` + `change_hint` + `bind`）、**Android 先行**逼出通用兜底。产出 `design-vision-computer-fusion.md`（取代 #63 中间机制版汇总）。**未改码。**
- **#63→#64 交接（2026-09-26 03:2x）**：#63 完成 usage-first 融合设计（`design-vision-computer-fusion.md`）；**平台顺序锁定 = X11 先行**（视觉/坐标闭环），Android 第二。开工工作单 = `screenlab-work.md`（**任务态落文件**，会话可弃）。转入 **#64** **直接开工 Slice 0**（视觉适配器 CLI 在静态 PNG 上验），见 `handoff-screen-63.md`。
- **#62a 结果（X11）/ 分支 #62b（2026-09-25 23:1x）**：#62a 出 **X11** 矩阵（并入 `screen-change-detect.md`）——`XDamage(root, NonEmpty)` 给真脏区矩形（~67 ev/4s，CPU 个位数%）；`MIT-SHM + 64 分块 diff` 无扩展依赖、~5–6ms/帧、CPU 2–3%；现状 `daemon.py:296` 全帧 PNG sha256 最贵（~29% CPU）。**Windows/Android 未做**（mutter/XWayland 未测；当前 VM 实为 Xorg/XFCE）。→ 起子分支 **#62b**（`screenlab #62b`，见 `handoff-screen-62b.md`）补 **Android**（无原生脏区、最难、当前焦点）；**新会话等 YZ 确认环境后动手**。做完回 #62。
- **分支 #62c（2026-09-25 23:3x，与 #62b 并行）**：补 **Windows**（DXGI Desktop Duplication / WGC / SetWinEventHook 候选），产出并入 `screen-change-detect.md`（三平台已汇总）。见 `handoff-screen-62c.md`；**新会话等 YZ 确认 Windows 环境后动手**。
- **#52 遗留（本会话已解）**：W1 两失败已修——坏 venv（干净重装 + `--system-site-packages`）、计划任务 `E_ACCESSDENIED`（改 `-Mode shared` 不建任务；测试期用管理员 COM 任务注入交互会话）。
- **其它候选**（Linux 3a 已闭合；待 YZ 议）：`SETTLE`/`IDLE`（进入静默门槛 / 空闲自动让出，体验升级）；**Wayland**（portal + 虚拟设备分源）；Windows/macOS/Android 的**装配 + 同意入口**；跨 provider。见 `design-screen-assist.md` §6、分册 §17。
- **分工**：段 A（功能打通）与段 B（体验验收）均已完成（段 B = YZ 在宿主 VBox 控制台用真键鼠验收）。

## 1. 目标（3a 摘）

真人在**自己机器**上操作，agent 接入**协助**；真人有物理屏、常驻在场；**真人可随时拿回**；授权主体是**人**；授权 = **一条连接**（无会话凭证）；平台按"**实际会用的**"排。

## 2. 路线（从目标导出）

**打通判据（功能）**：agent 经 `computer` 工具（`screen_capture`/`screen_act`）、走 tailnet、在真人机的**现有会话**上完成 —— `发起 → 本地同意 → capture/act → 真人物理输入抢占 → 收回`，**全程公开入口 + 地面真值**（`import -window root` / `xdotool getmouselocation`），不用自写 e2e 自证。

- **段 A 功能打通（AI 主导，不需真人）**：接 agent 端（auth 握手）＋ 接真人端日常入口 ＋ 真机全链。
- **段 B 体验验收（YZ 下场）**：真鼠标物理事件（VBox 造不出，只有真鼠标能给）＋ 被打搅/拿回的体感 ＋ 入口顺不顺手。
- **明确不做**（§0.0 推不出 / 已定后置）：`SETTLE`/`IDLE`/物理热键（体验级"倾向"）；弹窗（v1 用 CLI/event 足够）；Wayland（暂缓）。

## 3. 阶段清单（status）

| # | 阶段 | 判据 | 状态 |
|---|---|---|---|
| E1 | **agent 侧接线**：`computer` 工具走 auth 握手 | 真 agent 经工具连上 3a 端点（非调试 CLI） | ✅ 本地过 + 真机活验（dirty @`0697c27`；pytest 33） |
| E2 | **真机全链**（surface `human@:0`） | 握手→同意→capture/act→**键盘物理**抢占→收回，公开入口 + 真值 | ✅ 真机过（`ScreenChannel(key_path)`；见 §4） |
| E3 | **真人端日常入口**（装配 + 常驻/一键） | 真人不手敲长命令即可起 3a | ✅ E3-a/E3-b/E3-c 已落（托盘入口 + 地址显示 + 物理热键收回），入口由 `install-machine` 生成 |
| E4 | **体验验收**（YZ 下场） | 真鼠标打断/拿回、体感、入口顺手 | ✅ 真机过（人优先/物理热键收回/入口信任+单实例） |
| E5 | 提交 / tag / 回写分册 | — | ✅ 4 提交 + tag `screenlab-goal2-3a-2026-09-25` + 分册 §17 |

## 4. 进展（就地改）

- 2026-09-25 19:0x · **#61：Android 真机演示 → 能力缺口清单 + 视觉待议**（cogos **未改码/未提交**）：
  - **LAN 单连接**：`AuthClient.attach` + `ScreenClient` open/capture 通（seat `c1` controller）。**澄清** consent = **每条 TCP 连接一次**（`AssistServer.java:320`；`ConsentManager` 同刻一 pending、答完 `cancel()`）；真实 agent `ScreenChannel` 单长连接 → **一次会话一次同意**。本轮多次弹窗系反复起连接所致。
  - **坐标不准**：`tap(0.125,0.599)`（估微信）→ 实际开**支付宝**；`tap(0.26,0.77)`（Chrome）两次**无反应**；注入生效（App 被拉起），落点偏移。疑 `capture` 帧(1080×2312) 与 `dispatchGesture` 输入坐标空间不一致。
  - **缺口**：无 `global`(HOME/BACK)/滑动/长按、无打字、无 Intent 启动。清单入 `screen-android-issues.md`（1/2a/2b/3/4/5 + 建议顺序 2a→2b→4→3→1）。
  - **停点**：视觉定位待讨论（#62 首任务）；**未改代码、未提交**。手机前台被误点成支付宝；连接清场时已断。

- 2026-09-25 18:1x · **#60：Android M5 = registry/alg/agent 管理 UI 并真机验证**（cogos 未提交，`screenlab/android/`）：
  - **代码**：`AgentRegistry.java` 加 `alg`（缺省 ed25519）+ `add/remove/write`（规范化 base64 32B、重复检测、临时文件+rename）；`AssistServer.java` 读 `hello.alg` 与表比对（不符 `alg_mismatch`）、按表 alg 限 ed25519、`result`/`seat.identity` 带 alg、同意 label 用 `别名 (alg:短码)`、新增 `disconnectPubkey()`；`CaptureService` 暴露 `server()`；`MainActivity` 加「已登记的 agent」区（列表行/详情对话框/复制/删除/粘贴添加）+ strings。
  - **构建部署**：`build.sh` 出 APK 0.2（versionCode 2），wifi adb `install -r` 经 EMUI 提示后 `lastUpdateTime=17:59:58`。
  - **真机验收**（截图 `tools/blobs/m5_main_ui.png`）：主界面状态区 + 无障碍按钮「关闭无障碍」（随开态）+「停止协助」+ 协助地址 `192.168.1.175:8901`；常驻通知 `title=screenlab assist / text=协助地址 192.168.1.175:8901 / action=Take back / icon=ic_stat_assist`；列表 `kilocode · ed25519:Qvnb/X6m`；详情显示全量 pubkey + 复制/删除；**add** 成功落盘（`registry.json` 两条均带 `alg:ed25519`，log `registered ed25519:XxElaIFm`）；**delete** kilocode → `removed ed25519:Qvnb/X6m` + `disconnected 1 conn(s)`，在线 holder 下一次 `state` = `channel_closed`。
  - **LAN 负例/正例**：claim `alg=rsa` → `result alg_mismatch | registered as ed25519, client claims rsa`；`AuthClient.attach` happy path 的 `result`/`seat.identity` 带 `alg`。`pytest tests/screenlab tests/agent/test_screen.py` = **39 passed**。
  - **操作要点**：EMUI 上 uiautomator 在 MainActivity resumed（1s tick）时 `could not get idle state`→ 用截图定位；软键盘会移动对话框（`input text` 不弹键盘）→ 临时 `ime disable` 稳定布局，事后 `ime enable`。设备 registry 已还原为仅 kilocode（带 alg）。
  - **停点**：M5 功能闭环；**M5 验收/提交/tag/回写分册待 YZ**。

- 2026-09-25 17:5x · **#59：M5 起步 = 产品形态 + agent 身份登记/删除**（cogos 未提交）：
  - **产品形态（已定）**：主界面（状态区：无障碍/采集/服务/协助地址 + 无障碍按钮文字随状态变、深链设置 + 启动/停止协助）；**常驻通知**（VPN 式，正文含协助地址 + Take back，点回主界面）；图标 **方案 B**（两重叠圆角矩形，`#1A202C`/`#40D0D6`，adaptive icon + 通知小图标）；名字 `screenlab assist`；签名沿用 `debug.keystore`；版本 0.2。
  - **agent 身份（已定）**：`alg` 字段（缺省 ed25519，向后兼容）；`hello` 带 alg 但**以表里的 alg 为准**（不符 `alg_mismatch`）；展示短指纹 `alg:pubkey[:8]`，列表收起、**点开看全量 pubkey（可复制）**，同意文案 `别名 (ed25519:短码)`；登记=粘贴 pubkey+别名，删除=**顺带断开该 pubkey 在线连接**；存储暂留 external-files。
  - **Python 侧已实现并验**：`auth/protocol.py`（`ALGS/DEFAULT_ALG/fingerprint/alg_mismatch`）、`auth/registry.py`（`Record.alg`）、`auth/server.py`（alg 比对+按表验签）、`auth/client.py`（hello 带 alg）、`cli.py`（`register --alg` + 新增 **`unregister`**）、`consent_app.py`/`consent_app_win.py`/`daemon.py`（fingerprint）。`pytest tests/screenlab tests/agent/test_screen.py` = **39 passed** + registry/CLI 冒烟过。
  - **Android 侧半成品**：`Net.java`（新）、`CaptureService`（`isProjecting`+通知含地址）、`MainActivity`（重写入口）、manifest icon/版本、res（strings/colors/图标）已改；**APK 0.2 已构建未部署**。**未做**：`AgentRegistry` add/remove 写入、`AssistServer` alg 校验、app 内 agent 列表/添加/详情/删除。
  - **交接**：`handoff-screen-59.md`。

- 2026-09-25 17:3x · **#59：Android M4 收尾 = 部署 + LAN 端到端真机通过**（cogos 未提交，`screenlab/android/`）：
  - **部署新 APK**（17:20 构建，含 CmdReceiver gate 修复）：wifi adb `install -r` + EMUI「风险提示→继续安装」（adb dump 取 `android:id/button1` bounds → `input tap`），`lastUpdateTime=17:24:25`；起服务 `am broadcast … op serve` 日志证明修复生效——`screenlab.cmd: capture service start requested` → `screenlab.server: listening 0.0.0.0:8901`（a11y 分支不再吞服务）。
  - **LAN 直连**（不经 `adb forward`）：host `192.168.1.13` → phone `192.168.1.175:8901`；`AuthClient.attach` → `result ok`(alias=kilocode) → `ScreenClient.from_channel` 的 `info/open/state` 通，`seat.identity` 带验证过的 Record、role=controller。
  - **端到端**：YZ 手机点系统采集同意（`投射/录制时显示敏感信息`→`立即开始`，projection started `1080x2312@480`）→ `capture`（blob 65244B，`changed=true`）→ `act pointer` 归一 `(0.5,0.3088)`→像素 `(540,714)` **注入命中 app「grab a frame now」按钮**（地面真值 log `screenlab.inject: tap 540.0,714.0 -> true` 紧接 `captureOnce` 的 `no image`）→ 通知「Take back」→ log `revoke requested`/`revoked 1 client(s)`/`projection stopped`，agent 下一次 `state` = `channel_closed`。
  - 脚本 `/tmp/kilo/m4_auth_lan.py`、`m4_e2e.py`；consent `auto` 经 `op consent --es mode auto`（无人在场时免通知）。
  - **停点**：M4 完成；下一步 **M5**（装配/验收/提交/tag/回写分册）**待 YZ**。

- 2026-09-25 17:2x · **#58：Android M4 = auth/1 设备端实现并真机通过（传输/身份）**（cogos 未提交，`screenlab/android/`）：
  - **Ed25519 on API29**：JCA 无 Ed25519（API33 才有），Android 自带 BC 阉割也不含 → 用 SDK 自带的 `bcprov-jdk15on-1.67` **低层 `Ed25519Signer`**，按其常量池闭包取 **41 个类**打成 `libs/bc-ed25519.jar`（52KB；整包 6MB 用 d8/R8 >5min 卡死，闭包 d8 ~30s）。真机正/负向量验签过。
  - **代码**：新增 `Ed25519Verify.java`、`AgentRegistry.java`（设备侧允许 agent 公钥表 `<external-files>/registry.json`；语义 = 身份供给，授权仍是每次连接同意）、`ConsentManager.java`+`ConsentReceiver.java`（高优先级通知 Allow/Deny；后台活动受限故不用弹窗；超时/无答默认拒绝；`auto` 供无人在场测试）、`AssistServer` 接入 `screenlab-auth/1` 0 阶段（hello→challenge→verify→consent→result，过了同通道转 `screen/1`；`seat.identity`=验证过的 Record、`subject`=alias）、绑定地址可配 `bind_host.txt`（默认 127.0.0.1）。`build.sh` 接 `libs/bc-ed25519.jar`。
  - **真机验收（loopback + `adb forward`）**：happy path `AuthClient.attach`→`result ok`(pubkey/name/alias)→`ScreenClient.from_channel` 的 `info/open/state` 通；负路径 `unknown_key`/`bad_sign`/`expired`/`denied` 全对；同意通知出现且 Allow 放行。脚本 `/tmp/kilo/m4_auth_test.py`、`m4_auth_neg.py`、`m4_consent_ui.py`；agent key `/tmp/kilo/android_agent.key`，registry `/tmp/kilo/registry.json`。
  - **tailnet 判定不必要**：手机与本机同网段（phone `192.168.1.175`、host `192.168.1.13`；wifi adb `192.168.1.175:5555`）。spec §1.4 本就写 Android 传输为 LAN；直接 LAN + auth/1 即可。Tailscale APK 已下 `/tmp/kilo/tailscale.apk`（105MB universal）但**放弃安装**。
  - **坑**：① USB 透传（VBox ehci）大流量下会重新枚举掉线（内核描述符错误 -32/-71），改用 wifi adb；② `CmdReceiver` 原先在 a11y 未连接时 early-return，吞掉 `serve`/`consent` 广播——已修（移到 a11y 检查之前）；③ `am force-stop` 后 a11y 需重新绑定，InjectService 未 connected（**未解**）。
  - **本轮停点**：含 CmdReceiver 修复的新 APK 已于 17:20 构建，**未部署**；`bind_host.txt=0.0.0.0` 已推设备。下一步：装新 APK → 直连 `192.168.1.175:8901` 验 LAN 握手 → 端到端 capture/act/收回（YZ 点采集同意）→ M5。

- 2026-09-25 16:2x · **#57：Android M3 通过（同意 + 拿回 / 单实例）**（cogos 未提交，`screenlab/android/`）：
  - 代码：`CaptureService` 加 `ACTION_REVOKE` + 前台通知「Take back」（`PendingIntent`，`FLAG_IMMUTABLE`）；`revoke()` = `AssistServer.revokeAll()`（关所有客户端 → agent 下次调用 `channel_closed`，对齐 G3）+ 停投影 + `stopForeground(true)` + `stopSelf()`；`onStartCommand` 改 `START_NOT_STICKY`。`AssistServer` 补会话状态（单控制者 `holder`、session `generation` 滚动、`revokeAll`/`preempt`、`act` 前先查输入位与世代），对齐 `service/channels.py`。`InjectService.noteInjection()` 注入自抑制窗口（500ms）。
  - **真机验收**（`adb forward` + 现有 `ScreenClient`，2026-09-25 16:17）：通知「Take back」→ 在持连接下次 `state` = `channel_closed`、服务停、投影停（log `revoke requested` / `revoked 1 client(s)` / `projection stopped`）；单控制者：c1 `act` 后 c2 `act` = `input_taken`。
  - **物理触摸抢占分源：API29 不可行，后置**——`TYPE_TOUCH_INTERACTION_*` 仅在 touch exploration 模式投递，而该模式会改变真人单指触摸行为（不可接受）→ 记入后置；`InjectService.onAccessibilityEvent` 保留为休眠路径（若 OEM/高版本直接投递则生效，自身注入由抑制窗口遮挡）。
  - 下一步 **M4**（入 tailnet + `screenlab-auth` 握手；API29 可能缺 JCA Ed25519 → BouncyCastle 或延后），随后 **M5** 装配/验收/提交（待 YZ）。

- 2026-09-25 16:0x · **#56：Android M2 通过**（cogos 未提交，`screenlab/android/`）：
  - **app 内 `screen/1` 最小服务** `AssistServer.java`：loopback TCP `127.0.0.1:8901`（开发期 `adb forward`），与 `proto/framing.py` 同款 framing（一行 JSON header + 可选二进制尾块），`org.json` 编解码；实现 `info/open/capture/act/blob_get/state/displays/close/yield` 子集，`act` 暂只支持 `pointer`。
  - `CaptureService` 新增 `grabPng()`（ImageReader→PNG，屏幕静态时回缓存）并起服务线程；`InjectService.instance` 供 `act` 注入。
  - **用现有 `ScreenClient` 跑通**：`info`（protocol/platforms/backends 对）、`open`（geometry 1080×2312）、`capture`（帧与 `adb screencap` 地面真值 **0.000%** 差）、`act pointer`（无障碍注入命中按钮 → 屏幕真响应，帧 hash 变化）、`blob_get`。
  - **串会话复核**：M2 期间出现的“非我所发”命令，查明是**本会话被 10 分钟闹钟唤醒后的续跑**（bridge owner 全是本会话），非跨会话。
  - 下一步 **M3**：同意/拿回（前台服务通知收回 + 单实例；物理触摸分源待验）。

- 2026-09-25 15:5x · **#56：Android M1 真机通过**（cogos 未提交，`screenlab/android/`）：
  - **采集**：`MainActivity` → MediaProjection 同意（YZ 点）→ `CaptureService` 1080×2312@480 抓帧写 `shot.png`；与 `adb exec-out screencap` **地面真值**同刻对比：去状态栏后 **0.00%** 像素差（>10 的仅 168 px，均为状态栏）。
  - **注入**：`InjectService.dispatchGesture` 注入 `tap(540,715)` → 命中「grab a frame」按钮 → 触发新抓帧（log `screenlab.inject tap 540.0,715.0 -> true` 紧接 `captured`）。
  - **新增 `CmdReceiver`**（`.CMD` action，`exported` 但 `Binder.getCallingUid()` 仅放行 root/shell）：adb 显式广播驱动 tap/swipe/global，供 M2 调试复用。**注意**：manifest 隐式广播会被 Android O+ 后台限制拦（须 `am broadcast -n` 显式组件）。
  - 旧机 `nova 4e / MAR-TL00` SDK29；重装 APK 后无障碍保持 `enabled_accessibility_services=….InjectService`。下一步 **M2**（app 内 TCP 服务 + `screen/1` 子集，`adb forward`）。

- 2026-09-25 14:0x · **#54：Windows W2 物理输入 + W4 装配通**：
  - 隧道沿用 #53 遗留的 `ssh -L`（9911/9912）；consent 走 Windows CLI 应答（`printf 'y\n' | … consent --once`），空 stdin 会默认 denied。
  - agent `hold`：YZ 动真鼠标 → `PREEMPTED role=observer after 27.2s`；YZ 按 `Ctrl+Alt+Shift+Esc` → `REVOKED after 62.6s: channel_closed`。**W2 ✅**。
  - **W4 ✅**：`install.ps1` 加桌面/开始菜单快捷方式 + `-Autostart`（Startup 快捷方式）；快捷方式 = `venv\pythonw -m screenlab.service.consent_app_win --manage-daemon --auth <reg>`。真机以交互任务 `start` 该 `.lnk` 模拟双击 → 托盘拉起 daemon（9911/9912 监听，Session 6），agent 经隧道 capture 1920×1280 通。
  - 代码：`install.ps1`（快捷方式 / `-Autostart` / serve.cmd 改 pythonw）；`consent_app_win.py` `_start_daemon` 用 `cmd /c` 包 `.cmd`（CreateProcess 不能直接跑 `.cmd`）。新增 harness `tools/win/run_shortcut.ps1`。Linux 21 passed。下一步 W5（待 YZ）。

- 2026-09-25 13:3x · **#53：Windows W1 + W3 通**：
  - **W1 ✅**：干净重装（`install.ps1 -Mode shared`，不建任务）；`registry.json` 写成 JSON 数组；daemon 在 assist **交互会话（Session 6 / Console）**；Linux 经 `ssh -L` 接入；Windows `screenlab consent` CLI 同意；`capture` 真桌面 1920×1280；`act` 三点归一坐标与 Session 6 `GetCursorPos` 精确吻合（seat 保持 controller）。
  - **W3 ✅**：`consent_app_win` 单实例（`Local\` mutex）+ 真桌面弹窗「#1 (UMRzsY)」。
  - **修 4 个真 bug**：`cli.py os.getuid()`（Windows 崩）、`Shell_NotifyIconW` 应属 shell32、托盘首用 `NIM_ADD`、mutex 命名空间。`daemon.py` 连接异常改打 traceback（诊断）。
  - **环境事实纠正**：机器**无** PIL/cryptography（#52 W0 说自带是错的）→ venv 联网 pip 装 Pillow 12.3/cryptography 50.0.1。`venv\pythonw` 一个逻辑进程=6MB launcher + ~25MB 真解释器，非重复。
  - **固化**：`tools/win/`（launch_daemon/launch_tray/setup_registry/status/shot + push_*.sh），用法见其 README。测试期用管理员 COM 计划任务注入交互会话（harness，产品路径留 W4）。Linux 测试 21 passed。详见 `handoff-screen-53.md`。

- 2026-09-25 13:0x · **#52：开 Windows 关系 3a**（Goal 3 扩展）：
  - **W0 侦察**（Windows 真机 `tablet-bbt8eqb4` / `100.112.50.115`）：Win11 build 26200；Python 3.11.5（机器级，带 PIL/cryptography）；**无 `socket.AF_UNIX`** → consent 端点改走 loopback TCP；ssh 是 Session 0（1024×768/DPI96 非真屏）。
  - **裁决**：新建标准账户 `assist`；传输 loopback TCP + `ssh -L`（免管理员）；不加新依赖（ctypes/MessageBoxW）；拿回走物理钩子（INJECTED 分源），托盘只 fallback；本轮只 Windows/3a，反检冻结。
  - **代码（未提交）**：consent 传输支持 `tcp:` + `consent.addr`（`auth/consent.py`）；`daemon.py` presence 按平台选 + Windows consent 默认端口；`cli.py`/`consent_app.py` 统一端点解析；`launch.py`/`install.ps1` 透传 auth/consent/presence（venv 加 cryptography、`--system-site-packages`）；新增 `presence_win.py`（低层钩子分源+热键）、`consent_app_win.py`（原生托盘）、`test_consent_transport.py`。Linux 测试 21 passed；win 模块仅 py_compile。
  - **靶机侧**：`assist` 标准账户可登录、免密 ssh 通；包投到 `C:\Users\assist\sl\screenlab`。**W1 未通**：坏 venv（`No pyvenv.cfg`）+ 计划任务 `E_ACCESSDENIED`；未起 daemon、registry 未写。详见 `handoff-screen-52.md`。

- 2026-09-25 11:5x · **#51：E4 真机验收 + E5 收尾**：
  - **E4 三判据真机过**（YZ 在宿主 VBox 控制台用**真键鼠**）：① agent 经 `ScreenChannel` 接管后，真鼠标接入 → `role=observer`（PREEMPTED，83s）；② 真键盘 `Ctrl+Alt+Shift+Escape` → 连接 `REVOKED/channel_closed`（80s）；③ 桌面双击「启动协助」无 untrusted（`attention=0`）、单实例只出一把托盘锁。地面真值：guest 指针随真鼠标移动、8911 连接数回 0、attach 仍 active。**上会话末"物理输入没进 guest"= VBox 控制台未取键鼠，非代码问题**。
  - **E5**：4 个提交 `b853576`（Xfce 信任）· `74aba3c`（presence 自抢占抑制 + `test_presence.py`）· `b6e41e8`（consent 单实例 + 请求编号）· `b3cc333`（分册回写）；tag `screenlab-goal2-3a-2026-09-25`；`codebase.md` 版本戳更至 `b3cc333`、清 DIRTY 标记。本会话另修 `tools/status.sh`/`desktop.sh` 的 `|| echo 0` 换行污染 JSON 的 bug。

- 2026-09-25 10:5x · **#50：untrusted / 单实例 / presence 自我抢占 / 同意编号**（改动**未提交**，详见 `handoff-screen-50.md`）：
  - **XFCE untrusted 修**：新增 `install/trust-launcher.sh`（`chmod +x` + 写 `metadata::xfce-exe-checksum`=sha256）；`install-machine --desktop-user` 装 helper 到 `/usr/local/bin/screenlab-trust-launcher` + `~/.config/autostart/screenlab-assist-trust.desktop`（登录自愈），并借会话总线装时立即打信任。真机 checksum = `86db8ace…`。
  - **consent_app 单实例**：`$XDG_RUNTIME_DIR/screenlab-assist.lock`（flock）；重复双击不再叠托盘锁（idle 灯 = `changes-prevent` 闭锁）。
  - **presence 自我抢占（VBox）**：XTEST 注入的指针事件被 VirtualBox mouse integration(id 9)/PS-2(id 12) 复读成"物理" → `channels.preempt()` 把 controller 降 observer，一条连接只能 act 一次。修：`PresenceMonitor.note_injection(window=0.5)` 抑制窗口，`daemon._dispatch_act()` 注入前调用。真机：同一连接 `act1`/`act2` 均 `ok`、seat 保持 `controller`；单测 `tests/screenlab/test_presence.py`。
  - **同意编号**：`consent_app` 弹窗显示 `#N (rid[:6])`，同 request_id 复号且不重弹、一次只弹一个。真机显示「协助请求 #1 (bVhcTn)」。
  - **E4 功能链路**：agent（`ScreenChannel` + `/tmp/kilo/agent.key`）连接 → YZ 同意 → 抓帧 1920×1093 → `act` 打开应用程序菜单，真机通。**未验**：真鼠标抢占 + 物理热键收回（末尾 YZ 物理输入未进 guest）。

- 2026-09-25 00:3x · **E3-b + 入口收进仓库 done**：
  - **E3-b（地址显示 / 默认端口）**：`consent_app.py` 托盘菜单显示协助地址（读 `session.env` 的 `SCREENLAB_TCP`）；缺省时按 **tailscale IP + 默认端口 8911**（`SCREENLAB_ASSIST_HOST/PORT` 可覆盖）推导；首次 `open` 也据此自动带 `--attach --tcp --auth --consent event`，真人无需再手敲长命令。真机验证：菜单显示 `100.100.137.78:8911`；`_assist_host/_assist_port` = `100.100.137.78 8911`。
  - **收进仓库**：新增 `screenlab/install/screenlab-assist.desktop`（`Exec=/usr/local/bin/screenlab assist`）；`screenlab` 加 `assist` 子命令（= `consent_app --manage-daemon`，统一入口、不用 wrapper）；`install-machine [--desktop-user ACCT]` 装桌面项到 `/usr/share/applications`，并可选复制到该账户 `~/Desktop`。真机：`install-machine --prefix /opt/screenlab --desktop-user human` → 两个 .desktop 就位、旧 ad-hoc wrapper 已删；`gio launch <desktop>` 起 tray + daemon 通过。
  - **更正（#50 结案）**：当时判为"靶机/合成输入的 xfdesktop 抖动"是**错的**——真因是 **XFCE 4.18 untrusted 弹窗**（缺 `metadata::xfce-exe-checksum`）。#50 已修信任，并实测 xdotool 双击 desktop 项**可用**（图标在 col0,row3 ≈ (70,405)；当时点 y=338 落在空隙）。
- 2026-09-25 00:2x · **E3-c（物理热键收回）done**：`presence.py` 在 `xinput test-xi2` 流里解析物理按键（`EVENT type` + `detail`=keycode），维护按下集合；命中约定组合即回调。daemon 接 `on_takeback → revoke_all()`（与 `consent --cancel` 同效）。默认键 = `Ctrl+Alt+Shift+Escape`（keysym，经 `xmodmap -pke` 解析；可用 `SCREENLAB_TAKEBACK_KEYS` 覆盖）。**分源**：只认非 XTEST 源，agent 注入不会触发。真机验证：agent 连接中，宿主 `VBoxManage keyboardputscancode 1d 38 2a 01 81 2a b8 9d` → agent 立即 `channel_closed`（REVOKED）。
- 2026-09-25 00:1x · **E3-a（入口装配）**：单一桌面入口「启动协助」→ `/usr/local/bin/screenlab-assist-app` = `consent_app --manage-daemon`（启动时 `screenlab open`(裸调复用 session.env)、退出时 `screenlab close`）。helper：无窗口托盘状态灯 + 弹窗同意 + 右键"收回/退出"；`SIGTERM`/菜单退出都会停守护。真机验证：启动 → `screenlab-assist`+`screenlab-attach` 均 active、托盘灯在、旧的两个 .desktop 已删；退出 → attach 转 inactive。**待补**：把「启动协助」.desktop/wrapper 收进 `install-machine`（现为靶机 ad-hoc 脚本）。
- 2026-09-25 00:0x · **E3-a 起步**：新增 `screenlab/service/consent_app.py`——无窗口 Gtk 托盘入口：状态灯（灰/问号/绿）+ 弹窗同意 + 右键"收回协助/退出"，订阅 `consent.sock`（与 CLI 同 hook，协议未改）。真机验证：**图标随进程出现/消失**（面板托盘区 on/off 差分命中 `(1494,0,1707,26)`），无窗口。
- 2026-09-24 23:1x · **E1 done**：`graphics.py` 加 `key_path` → `AuthClient.attach()` 握手 + `ScreenClient.from_channel()`；经 `config.py:49/72` → `app.py:167` → `terminal.py:339/358/486` 透传。缺省 = 旧路（Goal 1 零变化）。`pytest tests/agent/test_screen.py tests/screenlab` = 33 passed。
- 2026-09-24 23:2x · **E2 done**（agent 侧实现 `ScreenChannel`，即 `computer` 工具所用）：
  - 握手：`tcp:100.100.137.78:8911` + `/tmp/kilo/agent.key`（pubkey `TsrT…` 与登记表一致）→ 通过。
  - 同意：以 `human` 跑 `screenlab consent --once`（真实 v1 入口），显示登记表里的 alias `kilocode`。
  - `info/state`：seat `subject=kilocode`、`identity`=server 验过的 Record（非客户端自报）；`capture` 1920x1093。
  - `act pointer` → 地面真值 `xdotool getmouselocation` = `x:960 y:546` 命中；`import -window root` = 1920x1093 一致。
  - 抢占：宿主 `VBoxManage keyboardputscancode 1e 9e`（guest 内=物理）→ `seat.role=observer`、`gen 1→2`，下一次 `act` = **`no_input_bit`**。
  - 收回：以 `human` 跑 `consent --cancel` → `revoked=1`；连接下一次 `state` = **`channel_closed`**。
  - 脚本 `/tmp/kilo/e2_agent.py`、`/tmp/kilo/e2b_agent.py`。**注**：走的是 `computer` 工具同一实现，但未过完整 agent 工具壳（那属 E3/E4）。下一步 **E3**（真人端日常入口）。
- 2026-09-24 23:19 · **E2 独立复核（新会话亲手控）**：`/tmp/kilo/e2b_agent.py` 同链再跑一遍，`E2B_EXIT=0`；`capture` 1920×1093 → `act pointer` 落 `960,546` → 物理键(宿主 `keyboardputscancode 1e 9e`) → `role=observer gen 2→3` → `act no_input_bit` → `consent --cancel`(revoked=1) → `REVOKED channel_closed`。结论不变：**3a 机制链真机端到端通**。

## 5. 环境 / 入口（当前）

- **靶机** surface `100.100.137.78`：`human@:0` attached；daemon 带 `--presence --tcp 100.100.137.78:8911 --auth /home/human/.config/screenlab/registry --consent event`；注册表含 pubkey `TsrTNVQgfSeKuFDFxp07O06ji5NKH+Cmc2qwLqOj4cE=`（alias `kilocode`）；`tailscale0` 在 `firewall --zone=trusted`。
- **agent 侧 key**（测试用，可弃）：开发机 `/tmp/kilo/agent.key`。
- **真人入口（现）**：桌面是 **XFCE 4.18**（非 GNOME）。「启动协助」桌面项（`screenlab-assist.desktop`，由 `install-machine` 装）→ `/usr/local/bin/screenlab assist` = 无窗口托盘 helper（`consent_app --manage-daemon`）：状态灯 + 弹窗同意（**带请求编号 `#N (rid)`**）+ 右键显示**协助地址**/收回/退出；退出即 `screenlab close`。**单实例**（`$XDG_RUNTIME_DIR/screenlab-assist.lock`）。桌面项信任由 `install-machine` 写 `metadata::xfce-exe-checksum` + 登录自愈（`screenlab-trust-launcher`）。地址缺省 = tailscale IP + 8911（`SCREENLAB_ASSIST_HOST/PORT` 可覆盖）。物理热键收回 = `Ctrl+Alt+Shift+Escape`（分源；抑制窗口内仍有效）。CLI 兜底：`screenlab consent --auth <regdir> [--once|--cancel]`（`cli.py:240`）。
- **宿主 VBox**：`ssh zhengyp@100.112.50.115`，`VBoxManage.exe` 全路径；输入模拟**只有键盘**（`keyboardputscancode`，guest 内=物理），**无鼠标**。
- **Android 设备**（`nova 4e / MAR-TL00`，Android 10/EMUI 10/SDK29）：wifi adb `192.168.1.175:5555`（**别用 USB**，VBox ehci 大流量重枚举掉线）；app = `com.screenlab.assist`；服务监听 `0.0.0.0:8901`（`bind_host.txt`）；agent key `/tmp/kilo/android_agent.key`（pubkey `Qvnb/…`，registry `<ext-files>/registry.json`）；起服务 `am broadcast -n com.screenlab.assist/.CmdReceiver -a com.screenlab.assist.CMD --es op serve`；同意 `… --es op consent --es mode auto|allow|deny|interactive`；build `bash screenlab/android/build.sh`（~1.5min）。

## 6. 锚

- 代码：`codebase.md`（唯一代码认知基线）
- **反检测分析（横跨 Goal1/3a）**：`design-screen-antidetect.md`（2026-09-25 与 YZ 讨论）
- 设计：`design-screen-assist.md`（§3.2 已定 + 后置状态）
- 实验：`screen-assist-exp-log.md`（§5 e2e / §6 分源 / §7 抢占）
- 目标：`spec-screen-1.md` §0.0
- 前情：`handoff-screen-46.md`、`handoff-screen-45.md`
