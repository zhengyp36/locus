# handoff｜交接给新会话 · 2026-09-25 #58

> 接 #57。本会话 = Android **M4**（auth/1 + 传输）：**设备端 `screenlab-auth/1` 已实现并真机通过**（loopback + `adb forward`）；**tailnet 判定不必要**（走 LAN）。
> **规则/环境不在本文件**——先读 `screenlab-rules.md`（含交接阈值 **150K**）。
> YZ 在场；未提交/未 tag。

---

## 复制这段作为新会话的第一句

```
先按序读，再继续（接 #58，直接干活）：
0. ../checkpoint/tools/README.md（先 source tools/env.sh）
1. ../checkpoint/screenlab-rules.md（规则；交接阈值 150K）
2. ../checkpoint/screen-assist-status.md —— §0 + §4 + §5
3. ../checkpoint/codebase.md（代码认知基线）
4. ../checkpoint/handoff-screen-58.md（本文件）

状态：Android M4 auth/1 设备端已实现并真机通过（loopback + adb forward）：happy path 握手→result ok→同通道 screen/1 info/open/state；负路径 unknown_key/bad_sign/expired/denied 全对；app 内通知同意 Allow/Deny 生效；Ed25519 用自带 BC 最小闭包(41类/52KB)。tailnet 判定不必要（手机与本机同网段，LAN+auth/1）。cogos 工作树 DIRTY（screenlab/android/ 未跟踪），未提交。
本轮任务：Android **M4 收尾** —— 部署含 CmdReceiver gate 修复的新 APK（17:20 已构建未部署）→ 直连 192.168.1.175:8901 验 LAN 传输握手 → 端到端 capture/act/收回（需 YZ 点采集同意）→ 然后 **M5** 装配/验收/提交（待 YZ）。
约束：不提交/不 tag；每步飞书通知；上下文 ≥150K 即交接。
```

---

## 本会话做了什么（#58）

### 结论：Ed25519 on API29（真机实测）
- **JCA 无 Ed25519**（`Signature.getInstance("Ed25519"/"EdDSA")` 抛 `NoSuchAlgorithmException`；API33 才有）。
- Android 自带 BC provider（`BC 1.61`，包名 `com.android.org.bouncycastle`）**阉割**：无 Ed25519 签名类、无 `java.security.spec.EdECPoint`。
- 方案：用 Android SDK 自带的 `bcprov-jdk15on-1.67.jar`（`$HOME/Android/Sdk/cmdline-tools/latest/lib/external/org/bouncycastle/...`）的**低层 `org.bouncycastle.crypto.signers.Ed25519Signer`**。整包 6MB 用 d8/R8 **>5min 卡死**；按常量池图取闭包 **41 个类** → `screenlab/android/libs/bc-ed25519.jar`（52KB），d8 ~30s。真机正/负向量验签过。

### 代码（cogos，**未提交**；`screenlab/android/` 未跟踪）
- 新增 `Ed25519Verify.java`（BC 低层验签封装）、`AgentRegistry.java`（设备侧 `<external-files>/registry.json` = 允许的 agent 公钥数组 `{pubkey,name,alias}`；**身份供给**，授权仍靠每次连接同意）、`ConsentManager.java` + `ConsentReceiver.java`（高优先级通知 Allow/Deny；后台活动受限不用弹窗；超时/无答默认拒绝；`auto` 供无人在场测试）、`ConsentReceiver` 注册进 manifest（`exported=false`）。
- `AssistServer.java`：新增 `screenlab-auth/1` 0 阶段（`authenticate()`：hello→challenge{request_id,nonce(32B)}→verify{sign(64B)}→BC 验签→consent→result{ok,pubkey,name,alias}），过了同通道转 `screen/1`；`seat.identity` = 验证过的 Record，`subject` = alias；绑定地址读 `<external-files>/bind_host.txt`（默认 `127.0.0.1`，tailnet/LAN 时写 `0.0.0.0`）。
- `CmdReceiver.java`：调试口 `op=serve`（起 CaptureService 无投影）/`op=consent mode=auto|allow|deny|interactive`；**修复**：这些分支原先在 `InjectService.instance==null` 的 early-return 之后，被吞——已移到之前（**此修复的新 APK 未部署**）。
- `build.sh`：javac classpath + d8 输入加 `libs/bc-ed25519.jar`。
- `strings.xml`/`AndroidManifest.xml`：同意通知文案 + ConsentReceiver。

### 真机验收（loopback + `adb forward`，2026-09-25 ~16:5x）
- happy path：`AuthClient.attach('127.0.0.1',8901)` → `result ok`(pubkey/name/alias=`kilocode`) → `ScreenClient.from_channel` 的 `info/open/state` 通；`seat.identity` 带 Record。
- 负路径：`unknown_key` / `bad_sign`（签错字节）/ `expired`（错 request_id）/ `denied`（CmdReceiver 发 deny）全对。
- 同意 UI：`dumpsys notification` 见 `screenlab-consent` 通知；Allow 后放行。
- 脚本：`/tmp/kilo/m4_auth_test.py`、`/tmp/kilo/m4_auth_neg.py`、`/tmp/kilo/m4_consent_ui.py`；agent key `/tmp/kilo/android_agent.key`；registry `/tmp/kilo/registry.json`。

### tailnet
- **不必要**：手机 `192.168.1.175`、本机 `192.168.1.13`（同 /24）。spec §1.4 本就写 Android 传输为 LAN；直接 LAN + auth/1 即可。Tailscale APK 已下 `/tmp/kilo/tailscale.apk`（105MB universal，官方 GitHub release，签名 AOSP 风格）但**放弃安装**（手机 2.4G WiFi + USB 不稳）。

## 未完成（下一步从这里接）

1. **部署新 APK**（含 CmdReceiver 修复）：`adb -s 192.168.1.175:5555 install -r screenlab/android/screenlab-assist.apk`（wifi adb，EMUI 弹确认页用 uiautomator dump 取 `android:id/button1` bounds → `input tap` 中心）。
2. **验 LAN 传输**：设备上 `bind_host.txt=0.0.0.0` 已推；装完后起服务并让 agent 直连 `192.168.1.175:8901`（改 `m4_auth_test.py` 的 HOST），验 auth 握手 + `screen/1`（**不经 adb forward**）。
3. **端到端**：YZ 点一次系统 `MediaProjectionPermissionActivity` 采集同意（`am start -n com.screenlab.assist/.MainActivity` → tap 「request screen capture」按钮 `(540,426)` → 系统弹窗 YZ 点「立即开始」）→ 验 `capture`/`act`/通知「Take back」收回。
4. **M5**（待 YZ）：装配（app 入口/地址展示/安装流程）+ 验收（agent 公开入口真用 + 地面真值）+ 提交/tag + `docs/design-agent-tools.md` §17 回写。

## 环境事实（本会话新增/变更）
- **设备走 wifi adb**：`adb devices` 默认即 `192.168.1.175:5555`（命令加 `-s 192.168.1.175:5555` 更稳）。**USB（VBox ehci 透传）大流量会重新枚举掉线**（内核 `error -32/-71` + disconnect），尽量别用 USB 传大文件。
- adb 路径 `$HOME/Android/Sdk/platform-tools/adb`；build `bash /home/zhengyp/work/A/cogos/screenlab/android/build.sh`（~1.5min）。
- 设备侧文件目录：`/sdcard/Android/data/com.screenlab.assist/files/`（`registry.json`、`bind_host.txt`）。
- 设备侧启动服务（无投影）：`am broadcast -n com.screenlab.assist/.CmdReceiver -a com.screenlab.assist.CMD --es op serve`；同意：`--es op consent --es mode auto|allow|deny|interactive`。
- **已知未解**：`am force-stop` 后无障碍需重绑，`enabled_accessibility_services`/`accessibility_enabled=1` 已置但 `InjectService` 仍 `Binding` 未 `connected`（logcat 无 `screenlab.inject: connected`）。端到端 `act` 前必须解决（可试：在设置里手动关开无障碍，或避免 force-stop）。改 `bind_host.txt` 后需让服务重启（force-stop 是其一，但会触发该问题，权衡）。

## 锚
- 活文档：`screen-assist-status.md`（§0/§4/§5）
- 代码认知：`codebase.md`（版本戳 `b3cc333`；`screenlab/android/` DIRTY）
- 目标/设计：`spec-screen-1.md` §0.0、§1.4；`design-screen-assist.md`
- auth：`screenlab/auth/{protocol,server,client,registry}.py`
- 上轮：`handoff-screen-57.md`
