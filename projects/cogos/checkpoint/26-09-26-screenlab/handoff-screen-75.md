# handoff｜→ #76（#75 v2 usage 真机验证全过；剩 Android 动作补齐）

> 规则 / 环境不在本文件——先读 `screenlab-rules.md`（含交接阈值 **150K**）。
> 本文件由 **#75** 写给后继 **#76**；#75 的 v2 usage 验证（X11 + Windows）已完成，**未改 v2 接口**。
> 上游：#74 落 v2 接入代码（commit `8b4e685`）；#75 按 usage 角度真机复验。

---

## 复制这段作为后继会话的第一句

```text
接 #76。上一会话 #75 已按 usage 角度真机验证 v2 接入（X11 + Windows 全 ALL PASS，见 ../checkpoint/handoff-screen-75.md），未动 v2 接口；cogos 提交见 handoff 锚。**剩：Android 动作按冻结动词集补齐（launch/nav/drag）排后**，以及两处已知缺口（工具结果图路径未成模型附件；screen_act 的 acted 多一层包壳）。不要重新设计已封板接口。

先按序读（纯文本）：
0. ../checkpoint/screenlab-rules.md（规则；交接阈值 150K）
1. ../checkpoint/design-computer-v2-interface.md（v2 封板接口 §3 冻结 op 枚举）
2. ../checkpoint/screenlab-work.md §状态（#75 验证结论）
3. ../checkpoint/handoff-screen-75.md（本文件）

任务：
① 先跑 `tools/snapshot.sh` 看靶机状态；确认 Android 环境（adb 192.168.1.175:5555 / assist 8901）是否在线，不在线按不阻塞原则先做能做的。
② 按冻结动词集补齐 Android 动作：`launch`（app/URL，无坐标）→ daemon `_dispatch_act` 加后端；`drag`（配 to）→ 触协议 ACT_OPS 加 drag + daemon 后端；导航动词（back/home/recents，按 key 或独立 op 与 YZ 已冻结枚举对齐后再定，先读 §3）。
③ 以模型面入口（`make_screen_specs` 的 screen_act / screen_fetch）在真机上验证，真值用 uiautomator / adb 前台 activity，不用自写 selftest 当验收。
④ 全过则更新 CHANGELOG（即 screenlab-work.md）/handoff，允许 commit/push（不 tag）。

约束：允许 commit/push（不 tag）；10min 闹钟；文档二手，动手前以代码/实测为准。
```

---

## #75 做了什么（结果）

**未改 v2 接口 / 产品码**；新增两个 usage 验收脚本 + `x11.sh` 三个真值 helper。

- **新增 `screenlab/tools/v2_usage_selftest.py`（X11）**：走**模型面入口**——`make_screen_specs(manager)` 的 `screen_fetch`/`screen_act`/`screen_save` + `make_vision_specs(root)` 的 `see`/`mark`/`coord`，底层 live `ScreenChannel`（`unix:/run/user/1000/screenlab.sock` over ssh StreamLocal）。地面真值独立取：`x11.sh target-geom`（zenity 窗 X/Y/WIDTH/HEIGHT）+ `xdotool getmouselocation`。**ALL PASS**。
- **新增 `screenlab/tools/v2_usage_win_selftest.py`（Windows）**：同形状，走 it-daemon（`tcp:127.0.0.1:19911`，consent-auto，ssh 隧道）+ Tk 靶（自报物理 rect/center）。**ALL PASS**。
- **`x11.sh` 增 `target-start` / `target-stop` / `target-geom`**：只重摆/移除/取 zenity 靶窗几何（`start` 复用同一 `target_start_body`），供真值对照。`target-geom` 输出 `WINDOW=.. X=.. Y=.. WIDTH=.. HEIGHT=..`。
- **`README.md`**：列新脚本 + x11.sh 新子命令。

## #75 验证结论（usage 角度，独立真值）

- **X11（surface 1280×800，zenity 窗 X=508 Y=360 266×120 → 中心真值 (641,420)）**
  - `screen_fetch` 返整屏原生 PNG 1280×800（size == geometry）。
  - 视觉面 `see(PATH)`→`mark`→`coord` 回读 px == 窗中心真值；`see(FIG)` 0.15 放大后 `mark 0.5,0.5`→`coord` 仍回同真值（@原图映射不丢）。
  - `screen_act(op="click", point=中心, on_change="act")`：`acted`(内层)+`xdotool pointer` == 真值 (641,420)；返回帧与 `screen_save()` 原始帧在中心邻域有差异像素 → **落点标记存在**；`region_changed`/`stable` 恒带。
  - **`on_change="skip"`**：fetch 当前帧后外部移除目标（`x11.sh target-stop`）→ 目标区已变 → **不注入**（pointer 前后不变）、`region_changed=true`、`skipped=true`、返回新帧（≠ fetch 帧）。
  - 效果确证：点由窗几何推得的真 OK 按钮 → zenity 1→0。
- **Windows（Tk 靶真值 center (900,550)，screen 1920×1280）**
  - `screen_fetch` 整屏；视觉面 `coord` == 真值（含 0.3 放大链）；`screen_act(click,中心)` → `acted` == 真值、靶 **READY→HIT**（`click=[900,550]`）、落点标记存在。

## 留给 #76 的关键点

1. **Android 动作补齐**：daemon `_dispatch_act` **无 `launch` 后端**（现调用回 `backend_error`，见 screenlab-work #74）；`drag` 未进 `screenlab/proto/protocol.py::ACT_OPS`。按封板稿 §3 冻结枚举 `{click,move,drag,scroll,type,key,launch}` 补；"nav"（back/home/recents）如何落进冻结枚举需先对照 §3（可能走 `key`，也可能要新 op）——**目标 §0.0 推不出就飞书升级后做不阻塞的**。
2. **已知缺口 A（记录）**：模型面工具结果只带图片**路径**；cogos LM 管线 `assemble_tool_messages`（`cogos/lm_service/providers/base.py`）把 tool content JSON 化、`router.infer_modalities` 只看 user content 的 `image_url` → tool result 的图路径**目前不会**变成模型可看的附件。"图不转文字"在产品 agent 内尚未接通；需另立小任务。
3. **已知缺口 B（观察，未改接口）**：`screen_act` 成功路径返回的 `acted` 是**协议 act 整包**（`{ok,op,acted:{x,y,button,clicks}}`），落点像素在**内层 `acted`**，多一层包壳。属 #74 落码形状；是否收平留 YZ / 后续定，**不要**在未对齐前擅自改（封板接口）。
4. **验证脚本锚**：`screenlab/tools/v2_usage_selftest.py` / `v2_usage_win_selftest.py`；产品面入口是 `make_screen_specs` / `make_vision_specs` 的 fn。

## 锚
- 接口：`../checkpoint/design-computer-v2-interface.md`；目标：`../checkpoint/spec-screen-1.md §0.0`
- 代码：`cogos/agent/impl/graphics.py`、`cogos/agent/tools.py`、`cogos/agent/app.py`、`screenlab/proto/protocol.py`、`cogos/image_ctx/`、`screenlab/service/change.py`
- 验证：`screenlab/tools/{v2_usage_selftest.py,v2_usage_win_selftest.py,x11.sh,windows.sh}`
- 提交：`8b4e685`（v2 接入）+ `6b78e58`（v2 usage 验收脚本，`origin/feat/screenlab-p2`，不 tag）
