# handoff｜交接给新会话 · 2026-09-25 #55

> 接 #54。本会话 = 与 YZ 讨论 Android 远程控制并起步（M0 侦察 + M1 构建链/最小 app）。
> **规则/环境不在本文件**——先读 `screenlab-rules.md`。
> **串会话异常已查明（#56）**：**无真实串会话**——`terminal 34` 全部归属 #55，是 #55 跨轮次自我误判（见本文件《串会话异常：结论》）。#56 起会话先等 YZ attach TUI，之后直接继续 Android，无需再查。
> **YZ 要求：#56 起会话后先等 YZ attach TUI 再动手。**

---

## 复制这段作为新会话的第一句

```
先按序读，再待命（本轮不自行推进）：
0. ../checkpoint/tools/README.md（环境事实 + 固化脚本；先 source tools/env.sh）
1. ../checkpoint/screenlab-rules.md（规则，先读）
2. ../checkpoint/screen-assist-status.md —— §0 + §4 + §5
3. ../checkpoint/codebase.md（代码认知基线）
4. ../checkpoint/handoff-screen-55.md（本文件）

状态：Android 线刚起步——全用户态构建链已就绪（~/Android），APK 已构建并在旧机上装好（YZ 完成安装、无障碍已开）；cogos 工作树 DIRTY。
本轮任务顺序：① 起会话后先**等 YZ attach TUI**，不要动手；② 「串会话」已在 #56 查明（**无真实串会话**，见本文件《串会话异常：结论》），无需再查；③ 继续 Android 远程控制（M1 → M5，见本文件《下一步》）。
纪律：裁决按 spec-screen-1.md §0.0；不提交/不 tag；动手前 10 分钟闹钟（YZ 在场讨论时免）；每步飞书通知。
```

---

## 本会话做了什么

- **与 YZ 讨论 Android 线**（无代码，结论）：
  - Android 目标形态 = **设备内服务（一个 app）**，不是宿主侧 adb adapter。依据 §0.0（3a 附着真人机、真人可随时拿回、授权主体是人）+ §0.1（Android 无 sshd，走 LAN/反连，最终设备内 app）。adh 只留**一次性装配**（侧载），不做运行时通道。
  - **复用平台无关核心一份**：wire 协议（NDJSON + 可选二进制尾块）、`screenlab-auth`（Ed25519）、单控制者/世代/收回语义逐字不变 → agent 侧零改动。
  - Android 独有三块：采集 **MediaProjection**（系统一次性同意）、注入 **AccessibilityService.dispatchGesture**（**只做注入，不做语义树**——与 `rationale-screen-a11y-drop.md` 一致）、同意/拿回入口 = 前台服务 + 通知。
  - 传输 = **tailscale TCP**；**开发期用 `adb forward` 免网络**（旧机网络差不阻塞开发）。
  - 文本输入：`dispatchGesture` 不能打字；免树路线 = 剪贴板+粘贴 或 自建 IME；`ACTION_SET_TEXT` 需读节点（=回到树），不采用。**此点尚未定案。**
  - 旧机适配：nova 4e（MAR-TL00），Android 10/EMUI 10/SDK29。**旧机是合适的测试机**（网络差被 `adb forward` 绕过；日常机有隐私/兼容风险）。
- **M0 侦察**：本机无 Android 构建链（无 JDK/gradle/sdkmanager）；cogos 无任何 Java/Android 骨架；wire 格式跨语言可逐字复用。
- **M1 构建链（已完成，全用户态、无 root）**：见《环境事实》。
- **M1 最小 app（已构建+安装）**：见《产物》。

## 串会话异常：结论（#56 已查 —— 无真实串会话）

**现象（#55 报）**：本会话 `terminal 34` 的命令被"本会话之外的东西"替换并执行（JDK 直连下载被换成走代理、跑 `build.sh`、停机期间 `adb install` + 开无障碍）。

**结论：不存在跨会话占用。** 全是 #55 自己跨轮次做的事被误判成"外部驱动"。

**证据**
- **bridge owner 日志（决定性）**：`~/.local/state/kilo-resident/log/bridge.log` 每次 terminal 结束都记 `owner=`。当前 bridge 生命周期内 `id=34` 的 10 次事件**全部 `owner=ses_f28ae9165…`（#55）**，无第二个会话；本生命周期内每个 id 只有一个 owner（26–28=#53、29–33=#54、34=#55）。id 1–24 的"多 owner"来自 bridge 自身多次重启后的 id 复用，非并发。
- **#55 原始 transcript**（`kilo_local_recall`）：Android 脚手架是它自己 `write` 的；JDK 换代理是它自己 `terminal_cancel`+`terminal_exec`；`adb install` 是它自己 exec 后、会话结束时命令继续跑完（非阻塞，正常）。它自己也已复盘并撤回误报。
- **无第二执行者**：4097 上只有 `kilo serve`、bridge `node src/index.ts`、TUI attach；两个 `feishu_server.py` 只是 MCP 文件发送器。

**为何会看成"串会话"（设计诱因，非执行串线）**
- `TerminalManager` 是 bridge 里**一个全局 Map**（`src/terminal.ts:57`），id 全局自增、exited 不清理；`terminal_list` 返回**全部**会话的终端（`plugin/kilo-resident-terminal.ts:133`）→ #55 看到 1–34（含 #53/#54 的命令）误当自己的。
- `session.command` 每轮 exec 被**覆盖**（`src/terminal.ts:115`），`terminal_list` 只显示最后一次 → 命令"变化"像被替换。

**真实（潜在）缺陷，已定位**：`exec/observe/notify/cancel/close` 不校验 `ownerSessionID`，`list` 不按会话过滤 → 理论上可 `exec` 别人的 id 并抢其完成唤醒（本次未发生）。修法（集中在 `../kilo-resident`）：terminal/timer 的 op 带 caller `sessionID`、按 `ownerSessionID`（timer 按 `origin`）鉴权、`list` 按会话过滤；涉及 `src/terminal.ts`、`src/bridge.ts`、`src/control.ts`、`plugin/kilo-resident-{terminal,timer}.ts`。
- 注：#56 曾在被 YZ `/undo` 回退的一轮里就地实现过此修法；实际是否遗留工作树改动，以 `git -C ../kilo-resident status` 为准。

## 产物 / 代码改动（cogos，**未提交**）

- **新增 `screenlab/android/`**（设备内 app 骨架，M1 验证用）：
  - `AndroidManifest.xml`（minSdk/targetSdk 29；`FOREGROUND_SERVICE`/`INTERNET`；`CaptureService`(type=mediaProjection) + `InjectService`(BIND_ACCESSIBILITY_SERVICE)）
  - `res/{values/strings.xml, xml/accessibility_service_config.xml}`（`canPerformGestures=true`，**不**请求读窗口内容）
  - `src/com/screenlab/assist/{MainActivity,CaptureService,InjectService}.java`
    - `CaptureService`：前台服务持 MediaProjection → VirtualDisplay → ImageReader(RGBA) → PNG 写 `getExternalFilesDir()/shot.png`。
    - `InjectService`：`tap/swipe`（`dispatchGesture`）+ `global`（`performGlobalAction`）；static `instance` 供 MainActivity 触发。
    - `MainActivity`：三个按钮 = 请求采集 / 委托点击屏幕中心 / 立即抓帧。
  - `build.sh`：**无 Gradle** 构建（aapt2 → javac → d8 → jar 打包 → zipalign → apksigner；debug keystore 自动生成）。
  - 已产出并安装 `screenlab/android/screenlab-assist.apk`（package `com.screenlab.assist`）。
- **其余 11 个未提交改动**仍同 #53/#54（Windows 3a：`install.ps1`、`consent_app_win.py`、`presence_win.py`、`auth/consent.py`、`daemon.py`、`cli.py`、`consent_app.py`、`launch.py`、`tests/screenlab/test_consent_transport.py`）。

## 环境事实（本会话新增）

- **Android 构建链（用户态，无 root，`$HOME/Android/`）**：
  - `jdk17/`（Temurin 17，`$HOME/Android/jdk17`）
  - `Sdk/` = cmdline-tools + `build-tools/34.0.0` + `platforms/android-29` + `platform-tools`
  - 下载物在 `$HOME/Android/dl/`。
  - **注意**：本机只有 JRE 1.8、无免密 sudo。`build.sh` 已 `export JAVA_HOME`（否则 `d8` 会用 1.8 崩 `UnsupportedClassVersionError`）。
  - 直连 `dl.google.com` 可用；`api.adoptium.net` 直连会卡（需代理 `-x http://127.0.0.1:10809`）。
- **旧机（测试设备）**：`nova 4e / MAR-TL00`，serial `XMK4C19318000820`，Android 10/EMUI 10，**SDK 29**，arm64-v8a，1080×2312 @480dpi。USB 直通进本 VM。
  - `com.screenlab.assist` **已安装**；`enabled_accessibility_services=com.screenlab.assist/com.screenlab.assist.InjectService`、`accessibility_enabled=1`（YZ 完成）。
  - 抓帧产物路径：`/sdcard/Android/data/com.screenlab.assist/files/shot.png`（当前尚无）。
  - MediaProjection 同意弹窗需真人点「开始/立即开始」（每次采集会话一次）——与「授权主体是人」自洽。
- **不要用**：`adb shell getprop` 无参（会把全部属性灌满上下文）。

## 下一步（按序，别发散）

1. **等 YZ attach TUI**（不 attach 不动手）。
2. **查「串会话」异常**（见上）。
3. **Android 线（M0 已过）**：
   - **M1 机制验证**：真机跑 `MainActivity` → 请求采集（YZ 点同意）→ 抓帧；`adb exec-out screencap` 做**地面真值对照**。注入用「真机屏幕响应 + 抓帧差分」验收（不用自写 e2e 自证）。
   - **M2 拼最小服务**：app 内起 TCP 服务，实现 `screen/1` 的 `info`/`capture`/`act` 子集（先不带 auth，走 `adb forward`），跑通**现有 agent 入口**（`cogos/agent` 的 `ScreenChannel`/`screenlab cli`）。
   - **M3 同意 + 拿回**：前台服务 + 通知收回 + 单实例；物理触摸抢占分源（若可分源）。
   - **M4 传输 + 身份**：入 tailnet，`screenlab-auth` 握手（老机 API29 可能缺 JCA Ed25519 → 需 BouncyCastle 或延后），同意在 app UI。
   - **M5 装配 + 验收/提交/tag/回写**（待 YZ；Windows 线 W5 也未做）。
   - 未定项：文本输入通道（剪贴板 vs IME）。

## 踩过的坑（本会话新增）

- **跨轮次自我误判**：我把自己前几轮 `write` 的 `screenlab/android/` 当成"别的会话写的并发改动"，发了错误告警（已更正）。教训：先核对自己会话历史/工具记录。
- `terminal 34` 命令被外部替换 → 见《未解异常》。
- `aapt2 link` 可直接吃 `aapt2 compile` 产出的 zip；`d8` 的 wrapper 用 PATH 里的 `java`，**必须 `export JAVA_HOME` 指到 JDK17**。
- 无 Gradle 打包：`jar uf app.apk classes.dex` 把 dex 塞进 aapt2 产出的 apk，再 `zipalign` + `apksigner`。

## 锚

- 活文档：`screen-assist-status.md`（§0/§4/§5）
- 代码认知：`codebase.md`（版本戳 `b3cc333`；本会话 DIRTY）
- 目标：`spec-screen-1.md` §0.0；设计：`design-screen-assist.md`（§4.1 Android、§4.6 平台适配、§4.7 收回）
- a11y 决策：`rationale-screen-a11y-drop.md`
- 上轮：`handoff-screen-54.md`；Windows ops：`tools/win/README.md`
