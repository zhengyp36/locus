# handoff｜→ #77（审核 v2 链条落地与验证，再与 YZ 讨论）

> 规则 / 环境不在本文件——先读 `screenlab-rules.md`（含交接阈值 **150K**）。
> 本文件由 **#73**（v2 接口对齐会话）写给 **#77**；YZ 指派：新会话先**独立审核** #74–#76 的落地与验证，再**通知 YZ**，随后**在对话里与 YZ 一起讨论**。
> 链条：#73 对齐封板 → #74 落码 → #75 X11/Windows usage 验证 → #76 Android 补齐。

---

## 复制这段作为 #77 的第一句

```text
接 #77。上一链条已完成：v2 接口封板（../checkpoint/design-computer-v2-interface.md），#74 落码（8b4e685）、#75 X11/Windows usage 验证（6b78e58）、#76 Android 动作补齐+真机验证（837b51d），均已 commit+push 到 origin/feat/screenlab-p2（不 tag）。本会话任务：先【独立审核】这条链的落地与验证是否与封板接口/目标一致，再【飞书通知 YZ】，然后【停下，等 YZ 在对话里一起讨论】——不要重新设计接口、不要擅自推进下一步。

先按序读（纯文本）：
0. ../checkpoint/screenlab-rules.md（规则；交接阈值 150K）
1. ../checkpoint/design-computer-v2-interface.md（v2 封板接口 = 审核基准）
2. ../checkpoint/screenlab-work.md §状态（#74–#76 记录）
3. ../checkpoint/handoff-screen-74.md / -75.md / -76.md（链条各步自述）
4. ../checkpoint/handoff-screen-77.md（本文件）

审核（以代码/实测为准，不轻信 handoff 自述）：
① git：origin/feat/screenlab-p2 是否含 8b4e685 / 6b78e58 / 837b51d；工作树是否干净；有无 secrets 入库。
② 接口一致性：cogos/agent/impl/graphics.py + cogos/agent/tools.py 的 screen_fetch/screen_act/screen_save 与 make_vision_specs 是否真按封板稿形状（未擅自改形状）；坐标是否恒 @原图；on_change 是否在客户端判。
③ 测试：跑 tests/agent + tests/screenlab + tests/image_ctx，记 passed。
④ 验证真伪：#75/#76 的 usage 验收是否「模型面入口 + 独立真值」（非自证）；脚本锚 screenlab/tools/v2_usage_*.py；靶机环境在线则复跑一遍（X11 优先）。
⑤ 已知缺口核实：A 工具结果图路径未成模型附件；B screen_act 的 acted 多一层包壳；C Android app 端点 Java 已编译未真机验证。
⑥ 偏航检查：对照 spec-screen-1.md §0.0，链条有无偏离目标。

产出：一份审核结论（一致点 / 偏差 / 风险 / 缺口），飞书通知 YZ（写文件 + stdin，避免双引号），然后停下等 YZ。不改代码、不 commit。

约束：10min 闹钟；裁决由 §0.0 推、能推自决；不擅自推进下一步。
```

---

## 链条现状（审核起点 · 均来自 handoff 自述，需独立核实）

- **#73 封板**：图形面 = `screen_fetch` / `screen_act` / `screen_save`；看图拆到通用视觉面（`image_ctx`，坐标恒 @原图）；无窗口/帧号；`act` 绑 current frame + 回整屏+落点 + `on_change∈{act,skip}`（客户端判）；`launch` 进冻结枚举；`save` = 保留授权控制点。文档：`design-computer-v2-interface.md`。
- **#74 落码**（`8b4e685`）：v2 接口进产品（`graphics.py`/`tools.py`/`app.py`；`protocol.py` ACT_OPS 加 `launch`）。自述「只实现，未改接口形状」。
- **#75 验证**（`6b78e58`）：新增 `v2_usage_selftest.py`（X11）/`v2_usage_win_selftest.py`（Windows），走模型面入口 + 独立真值，自述 **ALL PASS**（X11 zenity 1→0、落点==真值、`on_change=skip` 生效；Windows Tk 靶 READY→HIT）。未改产品码。
- **#76 补 Android**（`837b51d`）：`ACT_OPS` 加 `drag`；daemon/三后端补 `launch`/`drag`；Android Java `AssistServer.act` 扩 `pointer/drag/key/launch`（`key`=back/home/recents）。新增 `v2_usage_android_selftest.py`，自述真机 **23/23 ALL PASS**；回归 `tests/agent+screenlab+image_ctx` **299 passed, 3 skipped**。
- **自述缺口**：
  - **A**（记录，未改）：模型面工具结果只带图片路径；LM 管线 `assemble_tool_messages` / `infer_modalities` 不把 tool result 的图变附件 → 「图不转文字」在产品 agent 内未接通。
  - **B**（记录，未改）：`screen_act` 成功返回的 `acted` 是协议 act 整包，落点像素在内层，多一层包壳。
  - **C**（#76 新记录）：Android **app 端点**（`tcp:…:8901`）的 Java `launch/drag/key` 已编译未真机验证（重装 APK 会丢 MediaProjection，需重新授权）。
- **仓库**：`cogos` @ `837b51d`（`feat/screenlab-p2`，工作树干净）。本会话（#73）**未动任何代码**。

## 审核口径提醒
- **不用 selftest 自证**：`*_selftest` 只是脚本；验收须「以 agent 身份、只用模型面公开入口真用 + 独立地面真值」。
- 封板接口是**基准**：任何形状改动都是偏差，需指出。
- 目标唯一约束：`spec-screen-1.md §0.0`。

## 锚
- 接口：`../checkpoint/design-computer-v2-interface.md`；目标：`../checkpoint/spec-screen-1.md §0.0`
- 代码：`cogos/agent/impl/graphics.py`、`cogos/agent/tools.py`、`cogos/agent/app.py`、`cogos/image_ctx/`、`cogos/screenlab/proto/protocol.py`、`cogos/screenlab/service/{daemon,backends,backends_android,backends_win,change}.py`、`cogos/screenlab/tools/v2_usage_*_selftest.py`
- 提交：`8b4e685` / `6b78e58` / `837b51d`（`origin/feat/screenlab-p2`，不 tag）
