# handoff｜→ #77（#76 补齐 Android launch/drag/导航 并真机验证全过）

> 规则 / 环境不在本文件——先读 `screenlab-rules.md`（含交接阈值 **150K**）。
> 本文件由 **#76** 写给后继 **#77**；#76 完成「Android 动作按冻结动词集补齐 + 真机验证」，**未改已封板的 v2 模型面形状**（只扩了协议 act op 与后端）。
> 上游：#74 落 v2 接入（`8b4e685`）；#75 按 usage 角度真机复验 X11+Windows（`6b78e58`）；#76 补 Android（本文件）。

---

## 复制这段作为后继会话的第一句

```text
接 #77。上一会话 #76 已按封板稿 §3 冻结动词集补齐 Android 动作（launch/drag；导航 back/home/recents 走冻结的 key op），并以模型面入口（make_screen_specs 的 screen_fetch/screen_act）在真机验证 23/23 ALL PASS，代码已 commit+push `837b51d`（origin/feat/screenlab-p2，不 tag）。见 ../checkpoint/handoff-screen-76.md。剩：两处已知缺口（工具结果图路径未成模型附件；screen_act 的 acted 多一层整包包壳），以及 #76 新记录缺口——Android app 服务（Java）动作已编译未真机验证（重装 APK 会丢 MediaProjection，需重新授权）。不要重新设计已封板接口。

先按序读（纯文本）：
0. ../checkpoint/screenlab-rules.md（规则；交接阈值 150K）
1. ../checkpoint/design-computer-v2-interface.md（v2 封板接口 §3 冻结 op 枚举）
2. ../checkpoint/screenlab-work.md 状态节（#76 验证结论）
3. ../checkpoint/handoff-screen-76.md（本文件）

任务（待 YZ 在对话中定）：下一步方向由 YZ 提出后再去 ISSUES/ROADMAP 查候选；不擅自推进。
```

---

## #76 做了什么（结果）

**扩了协议与后端，未改 v2 模型面形状。** 目标 = 把 §3 冻结枚举 `{click,move,drag,scroll,type,key,launch}` 在 Android 侧真正可用。

- **协议**：`screenlab/proto/protocol.py::ACT_OPS` 加 `"drag"`（`launch` #74 已加）。
- **Python daemon 后端**（`screenlab/service/daemon.py::_dispatch_act`）：加 `launch`（`req["text"]`，无坐标）与 `drag`（`x,y` + `to`，归一化→设备像素）。
- **三个 act 后端补齐** `drag`/`launch`：
  - `backends_android.py::AdbAct`：`drag`=`input swipe x1 y1 x2 y2 300`；`launch`=URL→`am start -a VIEW -d`、包名→`monkey -p ... LAUNCHER 1`。
  - `backends.py::XdotoolAct`：`drag`=mousemove+mousedown+插值移动+mouseup；`launch`=`xdg-open`。
  - `backends_win.py::SendInputAct`：`drag`=SendInput mouse 序列；`launch`=`os.startfile`。
  - launch 回显统一 `{"target":..,"as":"url|package|open"}`。
- **模型面映射**：`cogos/agent/impl/graphics.py::ScreenChannel._inject` 把模型 `op=drag` 映射为协议 `kind=drag`（`x,y,to`）；缺 `to`/起点报错。`screenlab/service/cli.py act` 子命令补 `launch`/`drag`/`--to`。
- **Android app 服务（Java）**：`screenlab/android/src/com/screenlab/assist/AssistServer.java::act` 由只支持 `pointer` 扩到 `pointer/drag/key/launch`：`drag`→`InjectService.swipe`、`key`(back/home/recents)→`performGlobalAction`（`GLOBAL_ACTION_*`）、`launch`→`ctx.startActivity`（URL/包名）。`InjectService` 早已有 `swipe`/`global`，本次接上。**`screenlab/android/build.sh` 编译通过**（aapt2/javac/d8/apksigner）。
- **新增验证脚本** `screenlab/tools/v2_usage_android_selftest.py`（模型面入口 + 独立真值）。

## #76 验证结论（usage 角度，模型面入口，独立真值）

- **环境**：adb `192.168.1.175:5555` 在线；assist app `screen/1` on `8901` 在线、InjectService 已启用；设备 MAR-TL00 Android 10，1080×2312。
- **方法**：`ScreenChannel("unix:/tmp/kilo/screenlab-android.sock")`（host `screenlab daemon --backend android --adb-serial 192.168.1.175:5555`）+ `make_screen_specs` 的 `screen_fetch`/`screen_act`。真值 = `adb shell dumpsys activity ... mResumedActivity` / `dumpsys window ... mCurrentFocus`。
- **结果 23/23 ALL PASS**：
  - `screen_fetch` 返 `wm size` 1080×2312 原生 PNG。
  - `launch(app)`(com.android.chrome) 与 `launch(URL)`(https://example.com) → 真值前台 == Chrome；`acted` 回显 `target`/`as`。
  - `key(back)` / `key(home)` → 真值前台 == `com.huawei.android.launcher`；`acted` 回显 key。
  - `key(recents)` → 前台离开 Chrome。
  - `drag`（顶边 `(0.5,0.02)`→`(0.5,0.70)`）→ 真值 `mCurrentFocus=Window{... StatusBar}`（通知栏展开）；`acted` 回显起终点设备像素 (540,46)/(540,1618)。
- 回归：`tests/agent + tests/screenlab + tests/image_ctx` **299 passed, 3 skipped**；`test_impl_term_remote.py::test_write_secret_resolves_and_mutes_echo` 全量下偶发、单独跑过，与本改无关。

## 留给 #77 的关键点

1. **gap A（记录，未改）**：模型面工具结果只带图片**路径**；cogos LM 管线 `assemble_tool_messages`（`cogos/lm_service/providers/base.py`）把 tool content JSON 化、`router.infer_modalities` 只看 user content 的 `image_url` → tool result 的图路径**目前不会**变成模型可看的附件。"图不转文字"在产品 agent 内尚未接通；需另立小任务。
2. **gap B（记录，未改接口）**：`screen_act` 成功路径返回的 `acted` 是**协议 act 整包**（`{ok,op,acted:{...}}`），落点像素在**内层 `acted`**，多一层包壳（#74 落码形状）。是否收平留 YZ/后续定，**不要**在未对齐前擅改。
3. **gap C（#76 新增）**：Android **app 端点**（`tcp:192.168.1.175:8901`，auth+consent）的 `launch`/`drag`/`key` Java 实现**已编译、未真机验证**——`adb install -r` 会杀掉进程、丢 MediaProjection，需重新授权（`MainActivity` 的「启动协助」→ 系统录屏同意对话框，可能需人工点）。本次为避免破坏在用的投影，未重装；主验收走的是 host daemon `--backend android`（同一 `_dispatch_act`）。若要补验：重装后 `uiautomator dump` 找按钮坐标 + 点同意框，再以 `ScreenChannel(tcp:8901, key=keys/android_agent.key)` 跑同形状验收。
4. **验证脚本锚**：`screenlab/tools/v2_usage_android_selftest.py`（Android）、`v2_usage_selftest.py`（X11）、`v2_usage_win_selftest.py`（Windows）。产品面入口：`make_screen_specs`/`make_vision_specs`。
5. **环境提示**：host daemon 需 `/tmp/kilo/screenlab-android.sock`；`adb connect 192.168.1.175:5555` 在重启后可能需重连（Android 10 无无线调试 UI）。

## 锚
- 接口：`../checkpoint/design-computer-v2-interface.md`；目标：`../checkpoint/spec-screen-1.md §0.0`
- 代码：`screenlab/proto/protocol.py`、`screenlab/service/daemon.py`、`screenlab/service/backends{,_android,_win}.py`、`cogos/agent/impl/graphics.py`、`screenlab/android/src/com/screenlab/assist/AssistServer.java`
- 验证：`screenlab/tools/v2_usage_android_selftest.py`
- 提交：`837b51d`（#76，`origin/feat/screenlab-p2`，不 tag）
