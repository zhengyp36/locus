# handoff｜交接给新会话 · 2026-09-25 #56

> 接 #55。本会话 = Android 远程控制 **M1 + M2 真机通过**，M3 起步（未完成）。
> **规则/环境不在本文件**——先读 `screenlab-rules.md`。
> **本轮起交接阈值 = 150K**（YZ 2026-09-25 定；`screenlab-rules.md` 已改）。触发本次交接：本会话 ctx ≈153K。
> **#56 起会话不必再等 YZ attach**（YZ 已授权直接继续）；但重装 APK 后采集同意仍需 YZ 在真机点一下。

---

## 复制这段作为新会话的第一句

```
先按序读，再继续（接 #56，直接干活）：
0. ../checkpoint/tools/README.md（先 source tools/env.sh）
1. ../checkpoint/screenlab-rules.md（规则；**交接阈值已改为 150K**）
2. ../checkpoint/screen-assist-status.md —— §0 + §4 + §5
3. ../checkpoint/codebase.md（代码认知基线）
4. ../checkpoint/handoff-screen-56.md（本文件）

状态：Android 线 M1/M2 真机通过；M3 只改了 strings.xml（未完成）；cogos 工作树 DIRTY（未提交）。
本轮任务：继续 Android **M3 → M5**（见本文件《下一步》）；M3 只有前台通知「收回」+ 单实例 + 物理触摸抢占分源（若可分源）。
纪律：裁决按 spec-screen-1.md §0.0；不提交/不 tag；动手前 10 分钟闹钟（YZ 在场讨论时免）；每步飞书通知；上下文 ≥150K 即交接。
```

---

## 本会话做了什么

- **M1 ✅ 真机通过**：`MainActivity` → MediaProjection 同意（YZ 点）→ `CaptureService` 抓帧 1080×2312；与 `adb exec-out screencap` 地面真值**像素级一致**（去状态栏 0.00% 差）。无障碍 `dispatchGesture` 注入 `tap` 命中按钮并触发真响应。
- **M2 ✅ 真机通过**：app 内 `screen/1` 最小服务（`AssistServer.java`），loopback TCP `127.0.0.1:8901`（开发期 `adb forward`），与 `proto/framing.py` 同款 framing（一行 JSON header + 可选二进制尾块），`org.json` 编解码；实现 `info/open/capture/act/blob_get/state/displays/close/yield` 子集，`act` 暂只支持 `pointer`（tap）。用**现有 `ScreenClient`** 跑通：`capture` 与 `screencap` **0.000%** 差；`act pointer` → 无障碍注入命中按钮、屏幕真响应（帧 hash 变化）。
- **串会话复核（再次确认无跨会话）**：M2 期间出现的“非我所发”terminal 命令，查明是**本会话被 10 分钟闹钟唤醒后的续跑**（`bridge.log` 的事件 owner 全是本会话 `ses_f287ecf7…`；`kilo.db` 的 tool part 也归本会话）。原因是本会话按 `[2 条待处理事件]` 继续执行、但该轮续跑未进入当前可见上下文，造成“外部驱动”的错觉。**非第二个会话/进程**。YZ 据此判定：多次“串会话”疑似长会话幻觉，故把阈值降到 150K。

## 未完成（M3，下一步从这里接）

**M3 = 同意 + 拿回**。目标：真人可随时拿回；前台服务通知提供「收回」；单实例；物理触摸抢占分源（若可分源）。

**已做**：仅 `screenlab/android/res/values/strings.xml` 加了 `capture_active` / `revoke` 两条文案。

**待做（计划）**：
1. `CaptureService.java`：加 `ACTION_REVOKE`；`buildNotification()` 加「Take back」action（`PendingIntent`，`FLAG_IMMUTABLE`）→ `revoke()` = `server.revokeAll()`（关所有客户端 → agent 下次调用 `channel_closed`，对齐 G3）+ `stopProjection()` + `stopForeground(true)` + `stopSelf()`；`onStartCommand` 返回改 `START_NOT_STICKY`（收回后不自动重启）；单实例。
2. `AssistServer.java`：维护客户端 socket 集合 + 单控制者（`holder`）；`revokeAll()`（shutdown 所有连接）、`preempt()`（holder 降 observer + 滚代 → 下次 act `no_input_bit`）；`act` 前 `InjectService.noteInjection()` 自抑制。
3. `InjectService.java`：订阅 `typeTouchInteraction` 事件，`onAccessibilityEvent` 里在注入抑制窗口外收到触摸 → 回调 `onPhysicalTouch`（= `server.preempt()`）；`noteInjection()` 记时间戳。
4. `res/xml/accessibility_service_config.xml`：`accessibilityEventTypes` 加 `typeTouchInteraction`（**不**加 `canRetrieveWindowContent`，仍不读窗口内容/语义树）。
5. 验收：通知「收回」→ agent 连接 `channel_closed` 且服务停；单实例（重复启动不叠加）；物理触摸 → `PREEMPTED`/`no_input_bit`（若 TYPE_TOUCH 事件可区分注入与物理；不可分源就记录并后置）。

## 产物 / 代码改动（cogos，**未提交**）

- **`screenlab/android/`**（设备内 app，M1/M2 验证 + M3 起步）：
  - `AndroidManifest.xml`（minSdk/targetSdk 29；`FOREGROUND_SERVICE`/`INTERNET`；`MainActivity` + `CaptureService`(mediaProjection) + `InjectService`(BIND_ACCESSIBILITY_SERVICE) + `CmdReceiver`(exported, `android.permission.DUMP`)）
  - `res/values/strings.xml`（含 M3 新增 `capture_active`/`revoke`）、`res/xml/accessibility_service_config.xml`（`canPerformGestures=true`，不读窗口内容）
  - `src/com/screenlab/assist/`：`MainActivity.java`、`CaptureService.java`（前台服务 + MediaProjection→PNG + `grabPng()` 缓存 + 起 `AssistServer`）、`InjectService.java`（`tap/swipe/global`）、`AssistServer.java`（screen/1 子集）、`CmdReceiver.java`（adb 调试注入）
  - `build.sh`（无 Gradle：aapt2 → javac → d8 → jar → zipalign → apksigner；debug keystore 自动生成）
  - 已产出并安装 `screenlab-assist.apk`
- **其余 Windows 3a 未提交改动**仍同 #53/#54（`install.ps1`、`consent_app_win.py`、`presence_win.py`、`auth/consent.py`、`daemon.py`、`cli.py`、`consent_app.py`、`launch.py`、`tests/screenlab/test_consent_transport.py`）。

## 环境事实（Android）

- **构建链**（用户态，`$HOME/Android/`）：`jdk17/`（Temurin 17）、`Sdk/`（build-tools/34.0.0 + platforms/android-29 + platform-tools）。`screenlab/android/build.sh` 已 `export JAVA_HOME`；本机只有 JRE 1.8，无免密 sudo。
- **旧机**：`nova 4e / MAR-TL00`，serial `XMK4C19318000820`，Android 10/EMUI 10/SDK29，1080×2312@480。USB 直通进本 VM。`adb` = `$HOME/Android/Sdk/platform-tools/adb`。
- **开发传输**：`adb forward tcp:8901 tcp:8901`；app 内 server 绑 `127.0.0.1:8901`。host 侧用 `sys.path.insert(0,"/home/zhengyp/work/A/cogos"); from screenlab.proto.client import ScreenClient`。
- **抓帧产物（app 自写）**：`/sdcard/Android/data/com.screenlab.assist/files/shot.png`。
- **重装 APK 会清空无障碍设置** → 用 adb 重开：
  `adb shell settings put secure enabled_accessibility_services com.screenlab.assist/com.screenlab.assist.InjectService` + `adb shell settings put secure accessibility_enabled 1`。
- **EMUI 安装确认**：重装会弹华为「风险提示」/「未经华为应用市场检测」两页；注入触摸点不动它，用**键盘导航**：`input keyevent KEYCODE_DPAD_DOWN`（+ `KEYCODE_DPAD_DOWN`）再 `KEYCODE_ENTER`；同版本 `-r` 重装通常免弹。装完 `adb shell dumpsys package com.screenlab.assist | grep lastUpdateTime` 核对。
- **MediaProjection 同意**：系统弹窗（`投射/录制时显示敏感信息` … `立即开始`）须**真人**点（YZ）；每次采集会话一次。
- **CmdReceiver（adb 调试注入）**：须**显式组件**广播（隐式会被 Android O+ 后台限制拦）：
  `adb shell am broadcast -n com.screenlab.assist/.CmdReceiver -a com.screenlab.assist.CMD --es op tap --ef x 540 --ef y 715`。
- **MainActivity 三个按钮坐标**（1080×2312）：`request capture (540,426)`、`delegate tap (540,594)`、`grab a frame (540,715)`。
- **不要用**：`adb shell getprop` 无参（灌满上下文）。

## 锚

- 活文档：`screen-assist-status.md`（§0/§4/§5）
- 代码认知：`codebase.md`（版本戳 `b3cc333`；Android 改动 DIRTY）
- 目标：`spec-screen-1.md` §0.0；设计：`design-screen-assist.md`（§4.1 Android、§4.6 平台适配、§4.7 收回）
- a11y 决策：`rationale-screen-a11y-drop.md`
- 上轮：`handoff-screen-55.md`；Windows ops：`tools/win/README.md`
