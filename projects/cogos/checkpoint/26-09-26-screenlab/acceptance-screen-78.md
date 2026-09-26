# acceptance｜screenlab v2 接口独立验收报告（#78 → YZ · 修订版）

> 验收方立场：**独立于 #74~76 的实现叙述，也非 #73 接口稿作者**；判据只有 `spec-screen-1.md §0.0` + 第一原则。
> 证据优先级：代码 + git（`d89abd7..HEAD`）+ 实测 > handoff 叙述；不采信仓库 selftest 自证。
> 本轮只审不改、不 commit。报告日期 2026-09-26。
> **修订说明（与 YZ 讨论后）**：把「模型能否看到图」划为**上层装配**（`assemble_tool_messages`/provider 消息组装），不属 v2 接口形状 → 原 D1 从"接口缺陷"移出，改列「上层依赖」。结论随之由"有条件通过"改为"**接口层通过**"。

---

## 一、结论

**v2 接口层：通过。** 封板稿的三动词、六条不变量、坐标模型、客户端 `on_change`、settle 内化、`save` 控制点，代码与真机实测一致；X11 + Windows usage 真值验收全过。
接口层仅剩一个**轻微偏差 D2**（`screen_act` 回吐设备像素）与一个**文档项 D4**（合理修正未回填）。
「模型看图」= 上层装配（agent 侧），**另立**，不阻塞 v2 接口验收。

| 项 | 结论 |
|---|---|
| A1 不变量 | ✅ 通过（11 条全中；#8 视觉面已暴露、#9 save 控制点在，授权/审计属 §6 目标级未闭合、设计已标） |
| A2 理由 | ✅ 无"为方便而偏"；第一原则未破（注入坐标取自 current frame） |
| A3 验收 | ✅ 工具层 usage + 独立真值，X11/Windows 我复跑全 PASS；回归 99 passed（层级说明见 §五） |
| A4 记录 | ⚠ 未收口：`on_change` 默认 / ε·指纹 / blob 根 未回填封板稿（D4） |
| D2 | ⚠ 轻微接口偏差，建议修 |

---

## 二、证据（代码 + git + 实测）

**git**：`cogos` @ `feat/screenlab-p2` `837b51d`，工作树干净（`snapshot.sh` 实测）。
`d89abd7..HEAD` = `8b4e685`(#74) / `6b78e58`(#75) / `837b51d`(#76)。新增文件仅 3 个 `v2_usage_*`；`screenlab/tools/keys/` 与 `blobs/` **未入库**，无 secrets。

**实测 1（X11，独立复跑）**：`/usr/bin/python3.11 screenlab/tools/v2_usage_selftest.py` → `RESULT: ALL PASS`
- `screen_fetch` size==1280×800、native PNG；
- 视觉面 `see→mark→coord` 回窗中心真值 (641,420)，0.15 放大链后仍回同真值；
- `screen_act(click,point=中心)` → `acted` 落点 (641,420)== `xdotool` pointer 真值；返回帧含落点标记；
- `on_change=skip`（外部 `x11.sh target-stop` 移除目标）→ 不注入（pointer 前后不变）、`region_changed/skipped=true`、返回新帧；
- 效果：点窗 OK 按钮 → `zenity 1→0`。

**实测 2（Windows，独立复跑）**：`v2_usage_win_selftest.py` → `RESULT: ALL PASS`
- Tk 靶自报真值 center (900,550)，screen 1920×1280；fetch size==1920×1280；coord/zoom→coord==真值；act 落点==真值、靶 `READY→HIT`；落点标记存在。

**实测 3（回归）**：`pytest tests/agent/test_screen.py tests/image_ctx tests/screenlab -q` → **99 passed**。

**实测 4（边界事实 · 非接口缺陷）**：`screen_fetch` 结果 `{"ok":true,"path":"...","size":[1280,800]}` 过真实 LM 管线——
```
assemble_tool_messages -> tool content = str（JSON 字符串，无 image part）
infer_modalities       -> set()
```
即上层当前不把工具给的图引用装配成模型附件。**这是上层封装缺失，不是 v2 接口形状问题**（接口给的是图引用 `path`，够装配用）；但它决定目标 §0.0「有反馈」能否端到端达成 → 另立小任务。代码：`base.py:166-174`、`router.py:9-22`；全仓 `image_url` 生产者只在 `research/vision/*` 原型。

---

## 三、A1 不变量逐条判定

| # | 条目 | 判定 | 证据 |
|---|---|---|---|
| 1 | 仅 `screen_fetch/act/save`，无 look/zoom/mark 残留 | ✅ | `tools.py:1221-1267`；`tests/agent/test_screen.py:337`；旧名只在 `screenlab/tools/*_selftest.py`、`imgctx.py` CLI |
| 2 | 模型不可见帧/图 id、snapshot、revision、区域链、窗口、时间戳 | ✅（⚠见注） | `_fetch` 只回 `{ok,path,size}`（`tools.py:1177`），无 header/snapshot/hash |
| 3 | act 绑 current frame；一次往返给整屏+落点 | ✅ | `graphics.py:337-361`；`_current` 即模型上帧；返回 marked path |
| 4 | 位置/区域相对 current frame；换算工具侧、模型零换算 | ✅ | `graphics.py:51-58,341,384-413`；全归一化 0~1 |
| 5 | settle 内化（fetch change-gated、act 有界，只回报不保证） | ✅ | fetch `wait_stable=settle`（`:317-318`）；act `_settle` 有界（`:427-446`）回 `stable` |
| 6 | 抓屏只在 fetch/act；无窗口、无观测编号 | ✅（⚠见注） | pre-grab/settle 都在其内部；无窗口/时间戳 |
| 7 | on_change 客户端判 diff；恒回报 region_changed | ✅ | `graphics.py:343-347,415-425` 本地 `change.diff_bbox`；两路恒带 |
| 8 | 视觉面坐标恒回 @原图；已作为模型面工具暴露 | ✅ | 已注册（`tools.py:1293-1394`；`app.py:248` 无条件）；@原图由 `image_ctx.anno_to_src` 保；X11/Windows 实测 zoom→coord 回真值 |
| 9 | `screen_save` = 唯一持久化动作 + 保留授权控制点 | ✅（授权部分见下） | save 在（`graphics.py:363-375`）；授权判定/审计属 §6「授权粒度未闭合」，设计已标"先保守+可审计"→ 目标级未闭合项 |
| 10 | `launch` 进 ACT_OPS；后端逐平台实现 | ✅ | `protocol.py:15`；`daemon.py:400-407`；`backends*.py` + Java。⚠ Java app 端点未真机验证（gap C） |
| 11 | 决策口② 持久连接代持 current frame；无"重抓近似" | ✅ | `_current` 单状态；act 预抓仅作变更判/settle 基准，注入坐标取 current frame 归一坐标 |

> 注（#2/#6）：返回的 `path` 形如 `frame-<pid>-<seq>.png`（`graphics.py:470-473`），序号对模型可见，是"观测编号"的弱形式。封板稿允许回"文件路径"，序号无语义，**不判缺陷**。
> 另：fetch/act 会把帧落 `/tmp/screenlab-frames/`（默认 `blob_root`，`:110`），非持久但落盘；封板稿 §10 已记"blob 根 /tmp→持久位置"为开 → 归 A4，不判缺陷。

## 四、A2 理由核对

- 未把 viewing 塞回图形面；未暴露 id/窗口；settle 未变"保证"。✅
- **第一原则未破**：`act` 的预抓新帧只用于目标区变更判与 settle 基准；真正注入的坐标来自模型上帧的归一坐标，非"另抓一帧的坐标"。✅
- 图形面隐藏状态仍只有 `_current` 一个（`_seq` 是文件名计数器，非语义状态）。✅

## 五、A3 验收核对

- **工具层 usage + 独立真值**：X11/Windows 我独立复跑全 PASS，真值独立（xdotool 窗几何/pointer；Tk 靶自报 rect/center）。✅ 机械层可信。
- **层级说明**：脚本以 `_Manager` stand-in 直调模型面 `fn`（`v2_usage_selftest.py:59-64,153-155`），未跑真 agent loop / LM 往返。对**接口验收**这是足够的层（验的是工具契约与真值落点）；若要验"agent 看到图并据图决策"，需上层装配接通后另做 —— 归 D1 上层项。
- 回归：`tests/screenlab + tests/image_ctx`（+ `tests/agent/test_screen.py`）99 passed。✅

## 六、A4 待记录项收口

| 项 | 状态 |
|---|---|
| `on_change` 默认值 | 实现取 `"act"`（`tools.py:1185`），**封板稿 §10 仍列开、未回填** |
| `launch` | 已收（协议 + 四后端） |
| 保留授权模型 | 未收口（目标级未闭合，设计已标） |
| blob 根 `/tmp`→持久位置 | 未收口（仍 `/tmp/screenlab-frames`） |
| ε / 指纹形式 | 代码已定（`change.py` SAMPLE=8 / BLOCK=32 / THRESH=12），**封板稿未回填** |

→ A4 结论：**未收口**；封板稿状态仍写"未落码"，也未回填任何"合理修正"。

---

## 七、缺陷清单（修订）

**D2（轻微 · 接口层，建议修）— `screen_act` 回吐设备像素**
- 现象：`screen_act` 把底层协议 act **整包**塞进 `acted`（`graphics.py:355,359` → `tools.py:1201-1202`），落点像素在**内层** `{ok,op,acted:{x,y,button,clicks}}`；实测即设备像素（X11 641,420；Windows 900,550）。
- 判据：不变量 2 / `spec-screen-1.md §1.1`「agent 可见的一切坐标 = 归一化 0~1」；封板稿 §3 该位应是"acted|skipped"状态，不是协议整包。
- 证据：`graphics.py:355,359`；`tools.py:1201-1202`；验收脚本自己都要挖两层（`v2_usage_selftest.py:123-131`）。
- 影响：露设备像素与协议内部形状，与"平台差异/换算全内化"不符。建议收平为归一化落点 + `acted|skipped`。
- **根因（边界）**：两条边界——A（模型面）= `ToolDef.fn` 的入参/返回，返回即 `tool_result`（`ToolRegistry.call` `tools.py:1422-1432` → `runtime.py:135-142` → `base.py:166-174`）；B（协议）= `screen/1` wire，模型不可见。`ScreenChannel` 是内部客户端层，持协议形状本无错；错在模型面 adapter `_act` **没做翻译**：`path` 收了名（`raw_path`→`path`），`acted` 却整包 copy（`tools.py:1201-1202`）→ B 的包被抬过 A。修法只在这一处：`_act` 只回契约字段（`acted` 收成状态、要落点就回归一化 `landing`，`graphics.py:361` 已有）。

**D4（文档 · P3）— 合理修正与已定实现未回填封板稿**
- 协议新增 `drag`、`on_change` 默认 `act`、ε/指纹取值，应写入 `design-computer-v2-interface.md`（§9/§10）。

## 八、合理修正（应回填，不算缺陷）

1. **协议 `ACT_OPS` 加 `drag`**（`protocol.py:15`）：封板稿 §9 只提"加 launch"，但 §3 冻结的模型 op 含 `drag`，协议原无 drag 载体，必须加 → 回填 §9。
2. **Android 导航走冻结的 `key` op**（back/home/recents → `performGlobalAction`）：§3 无独立 nav op，走 key 合理 → 回填说明。
3. `_settle` 以 bool `stable` 回报（而非只报"仍不稳"）：语义等价、更直白，可接受。

## 九、上层依赖 / 记录在案（不属 v2 接口缺陷）

- **D1（上层装配）**：工具返回的是**图引用**（`screen_fetch` 的 `path`、`see` 的 `image` 字段），接口层已给足；当前 LM 管线不把它装配成模型附件，模型看不到图、也不被路由到视觉模型（实测 4）。→ 属 agent 侧装配，**另立小任务**；它决定目标 §0.0「有反馈」能否端到端达成。
- **gap C**：Android **app 端点**（`tcp:…:8901`）Java `launch/drag/key` 已编译**未真机验证**（重装丢 MediaProjection，需重授权）；主验收走 host daemon（同一 `_dispatch_act`）。Android 本就排后。
- **保留授权 / 审计**：`screen_save` 无授权判定、无留痕；§6/§10 目标级未闭合。
- **blob 根 `/tmp`**：帧默认落 `/tmp/screenlab-frames`；持久位置未定。
- 本轮我复跑 X11/Windows；Android 未复跑（设备/环境未确认）。

---

## 十、建议（给 YZ 讨论）

1. **接口层修 D2**：`screen_act` 回归一化落点 + `acted|skipped`，别透传协议整包。
2. **回填 D4**：把 `drag` 协议项、`on_change` 默认、ε/指纹、blob 根写入封板稿，并更新状态（"已落码/已验收"）。
3. **另立上层图装配（D1）**：tool result 的图引用 → `image_url` 附件（`research/vision/image_field_chat.py` 已有原型可复用）；接通后再补一条 agent 级端到端验收。
4. Android app 端点（gap C）按排后补验。
