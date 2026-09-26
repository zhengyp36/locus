# handoff｜交接给新会话 · 2026-09-25 #57

> 接 #56。本会话 = Android **M3 完成并真机验收**（通知收回 + 单控制者 + 服务单实例）；物理触摸抢占分源判定**不可行→后置**。
> **规则/环境不在本文件**——先读 `screenlab-rules.md`（含交接阈值 **150K**）。
> YZ 出门中：**任何需要真机「立即开始」采集同意的地方都要等 YZ 回来**；不要用 adb 代点系统同意（授权主体是人）。M4 的代码/构建可先做。

---

## 复制这段作为新会话的第一句

```
先按序读，再继续（接 #57，直接干活）：
0. ../checkpoint/tools/README.md（先 source tools/env.sh）
1. ../checkpoint/screenlab-rules.md（规则；交接阈值 150K）
2. ../checkpoint/screen-assist-status.md —— §0 + §4 + §5
3. ../checkpoint/codebase.md（代码认知基线）
4. ../checkpoint/handoff-screen-57.md（本文件）

状态：Android M3 ✅ 真机过（通知「Take back」→ channel_closed + 服务停；单控制者 input_taken）；物理触摸抢占分源判定不可行（touch exploration 才投递）已后置。cogos 工作树 DIRTY（screenlab/android/ 未跟踪）。
本轮任务：Android **M4**（auth/1 握手 + 入 tailnet；API29 可能缺 JCA Ed25519 → BouncyCastle 或纯 Java），再 **M5** 装配/验收（M5 与提交待 YZ）。
约束：YZ 出门中，真机采集同意要等 YZ；不提交/不 tag；动手前 10 分钟闹钟（YZ 在场讨论时免）；每步飞书通知；上下文 ≥150K 即交接。
```

---

## 本会话做了什么（#57）

### M3 ✅ 真机验收（2026-09-25 16:17）
- **通知「Take back」**：前台通知 action（`PendingIntent`→`CaptureService.ACTION_REVOKE`）→ `revoke()`：`AssistServer.revokeAll()` 关所有客户端 → 在持连接下次 `state` = **`channel_closed`**；`stopProjection()` + `stopForeground(true)` + `stopSelf()`；服务停、投影停（log `revoke requested` / `revoked 1 client(s)` / `projection stopped`）。脚本 `/tmp/kilo/m3_revoke.py`。
- **单控制者**：c1 `act` 后 c2 `act` → **`input_taken`**（对齐 `service/channels.py`）。脚本 `/tmp/kilo/m3_test.py`。
- **物理触摸抢占：API29 不可行，后置**——`TYPE_TOUCH_INTERACTION_*` 只在 **touch exploration 模式**（`FLAG_REQUEST_TOUCH_EXPLORATION_MODE`）投递；开该模式会改掉真人单指触摸行为（不可接受）。`InjectService.onAccessibilityEvent` 保留为**休眠路径**（若 OEM/高版本直接投递则生效；自身注入由 `noteInjection()` 500ms 窗口遮挡）。

### 代码改动（cogos，**未提交**；`screenlab/android/` 为未跟踪目录）
- `CaptureService.java`：`ACTION_REVOKE`；通知加「Take back」action（`Icon`+`Notification.Action`，`FLAG_IMMUTABLE`）；`revoke()` / `stopProjection()` / `onPhysicalTouch()`；`onStartCommand` 改 **`START_NOT_STICKY`**；`onDestroy` 也 `stopProjection()`。
- `AssistServer.java`：补会话状态——`conns` 集合、单控制者 `holder`、session `generation` 滚动、`revokeAll()`、`preempt()`、`act` 前置「输入位→kind→a11y→世代/stale→input_taken」校验、`seat/screen/state` 对齐 daemon；`ServerSocket.setReuseAddress(true)`。
- `InjectService.java`：`noteInjection()`（注入自抑制窗口 500ms）、`onAccessibilityEvent` 处理 touch interaction（**休眠**，注释已写明原因）。
- `res/xml/accessibility_service_config.xml`：`accessibilityEventTypes` 加 `typeTouchInteractionStart|typeTouchInteractionEnd`（注意 XML 枚举名不是 `typeTouchInteraction`）。
- `res/values/strings.xml`：`capture_active` / `revoke`（#56 已加）。
- `build.sh` 无需改；APK 构建通过。

### 真机环境（复用）
- 设备 `nova 4e / MAR-TL00`，serial `XMK4C19318000820`，SDK29，1080×2312@480。`adb` = `$HOME/Android/Sdk/platform-tools/adb`。
- 装 APK：`adb install -r screenlab-assist.apk`。**EMUI 会弹「未经华为应用市场检测」页**，用 adb 点「继续安装」：`uiautomator dump` 取 `android:id/button1` bounds `[270,1976][810,2084]` → `adb shell input tap 540 2030`（安装确认可用 adb，不需 YZ）。
- 重装 APK 清空无障碍 → adb 重开：`adb shell settings put secure enabled_accessibility_services com.screenlab.assist/com.screenlab.assist.InjectService` + `adb shell settings put secure accessibility_enabled 1`。已确认绑定：`eventTypes=[TYPE_WINDOW_STATE_CHANGED, TYPE_TOUCH_INTERACTION_START, TYPE_TOUCH_INTERACTION_END]`，`touchExplorationEnabled=false`。
- **采集同意**：`am start -n com.screenlab.assist/.MainActivity` → `adb shell input tap 540 426`（请求采集）→ 系统 `MediaProjectionPermissionActivity`，**必须 YZ 点「立即开始」**（每次投影会话一次；本次 YZ 已点，现服务已因收回而停）。
- `adb forward tcp:8901 tcp:8901`；host 侧 `sys.path.insert(0,"/home/zhengyp/work/A/cogos"); from screenlab.proto.client import ScreenClient`。
- 通知「Take back」按钮 UI 坐标（下拉通知）：bounds `[48,909][302,1053]` → 中心 `(175,981)`；下拉 `adb shell cmd statusbar expand-notifications`。
- `CaptureService` 是 `exported=false`，`am start-foreground-service` 会被拒（`Requires permission ... not exported`）——**只能靠真通知 action 或 App 内路径**触发 revoke。

## 未完成（M4，下一步从这里接）

**M4 = 传输 + 身份**：入 tailnet + `screenlab-auth/1` 握手；同意入口在 app UI。

- **现状**：agent 侧 auth 接线已具备（E1，`cogos/agent/impl/graphics.py` 的 `key_path`/`AuthClient.attach()`），**app 侧要把 `screenlab-auth/1` 服务端实现在设备内**（当前 `AssistServer` 无 auth，M2 直连 `screen/1`）。
- **握手（照 `screenlab/auth/server.py`）**：收 `hello{pubkey}` → 查登记表（设备侧允许的 agent 公钥表）→ 发 `challenge{request_id, nonce(32B b64)}` → 收 `verify{request_id, sign(64B b64)}` → **Ed25519 验签** → 同意（app UI）→ 发 `result{ok,pubkey,name,alias}`，然后同通道进 `screen/1`。帧名/编码见 `screenlab/auth/protocol.py`（`b64`，`PUBKEY_BYTES=32`/`SIGN_BYTES=64`/`NONCE_BYTES=32`）。
- **关键未知｜Ed25519 on API29**：JCA `Signature.getInstance("Ed25519")` 在 Android 13(API33) 之前大概率不可用（Conscrypt 较晚才加 EdDSA）。先**在真机实测**（可用 `adb logcat` 探针或临时 MainActivity 打日志）确认；不可用则选：① 打包 BouncyCastle（`bcprov` jar 进 `build.sh` 的 javac/d8 classpath，APK 体积 +~5MB）；② 纯 Java Ed25519 verify（可先用 host JDK17 的 Ed25519 做对照测试）；③ 与应用目标/风险权衡后延后（见下）。
- **传输**：可先继续 `adb forward` 验证 auth 握手（不阻塞），tailnet 作为独立子步（需 YZ 在手机装/登录 Tailscale）。spec §1.4 把 Android 传输记为「LAN + token，独立配对协议」；design M4 写「screenlab-auth 握手」——**若两者冲突，按 §0.0「复用 screen/1 + auth 核心一份，agent 侧零改动」优先复用 auth/1**；真有分歧再升级 YZ。
- **同意入口在 app UI**：把 `ConsentRequest`（alias/pubkey 前 16）弹给真人确认（对齐 Linux `consent_app` 的体验）；不要在 M4 引入弹窗之外的形态。
- **登记表（设备侧）**：一个允许的 agent 公钥列表（JSON 文件或编译内置），开发期可用 `/sdcard` 或 assets；来源与信任语义需自决并记录（目标：授权主体是真人，公钥只是身份）。

**M5** = 装配 + 验收 + 提交/tag/回写分册（**待 YZ**；Windows 线 W5 也未做）。**全程不提交/不 tag**。

## 锚
- 活文档：`screen-assist-status.md`（§0/§4/§5）
- 代码认知：`codebase.md`（版本戳 `b3cc333`；`screenlab/android/` DIRTY）
- 目标：`spec-screen-1.md` §0.0、§1.4；设计：`design-screen-assist.md`（§4.1/§4.6/§4.7）
- auth：`screenlab/auth/{protocol,server,client}.py`
- 上轮：`handoff-screen-56.md`；Android 构建链/环境同样继承之
