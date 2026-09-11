# handoff｜P3 已落码(FigContext+老化管理者)+P4 收尾+设计最终对齐 → 下一步 P3 目的层 vf6 探针（09-08 深夜收口）

> 2026-09-08 深夜。上游：`handoff-vision-image-fields-6.md`（P1+P2 落码 + 职责边界定案）。本会话完成：P3 上下文编译层落码（`cog_ctx/`）+ 老化管理者 + P4 验证收尾，并把**全部共识写回文档**。新会话只读本文件即可接手；接口/细节以本体 `design-vision-image-fields.md` 为准，验收以 `design-vision-image-fields-checklist.md` 为准，实现规格以 `design-vision-image-fields-p3-spec.md` 为准。

---

## 一句话状态

- **P1/P2/P3 全部落码并测试通过**：`image_ctx`（原始层+定位层）+ `cog_ctx`（上下文编译层+老化管理者）。全量 pytest **992 passed** 无回归（P3=22、image_ctx=33）。**P4 签证（验收）顺手收掉**——去重功能本就被 P1 实现，P4 只补了验证 + checklist。
- **下一步 = P3 目的层 vf6 探针**（验证「图被摘后，文字自含锚能否让模型重建窗口」）。⚠️ 这是唯一还悬着的东西，且现有 `vf6.py` 是**旧协议**（视野区/中央凹），要跑探针得先造 P3 消息 driver。

---

## 本会话产出（新会话必须知道）

### 1. P3 上下文编译层落码 `cogos/cogos/cog_ctx/`
- `context.py`：
  - `FigureAct`（`op/fig_id/note/status(ok|warn|error)/block/detail`）——一次图工具调用结果。
  - `FigMessage`（`text/image/image_size` + `to_message()` 映射 runtime dict）。
  - `compose_figure_text(fig_meta, note)`——固定格式图说明（`────────` 分段线 + `你的备注:`）。
  - `SYSTEM_HINT` + `FigContext.system_prompt()`——告知模型元信息行是程序参考、结论写进 `你的备注:`。
  - `FigContext`：`compile(act)`（error→纯文字；ok/warn→图说明+图块）、`strip(messages, msg_ref)`（只摘图、text 零改动、不替换）、`system_prompt()`。
- `manager.py`：`FigContextManager`（`next(act)`/`advance()`/`_age()`）——持有 `step/k/live deque`，老化调 `strip` + 出窗 `clear_fig_block`。纯文字轮用 `advance()`。
- 测试 `tests/cog_ctx/`：`test_p3.py`(18) + `test_manager.py`(4) = 22。

### 2. P4 去重验证收尾（无新功能；功能本就 P1 实现）
- `tests/image_ctx/test_p4.py`：跨时间同 `(path,window)` 同 FIG_ID（→ P3 重载锚稳定前置）、跨 path 不合并。
- **checklist P1~P4 共 57 项已勾**（`[x]`）：P3 mecanismos + P4 全部。通用不变式/待实测/残留待核仍 `[ ]`。

### 3. 设计文档全面对齐（**共识收口，勿再改**）
- `design-vision-image-fields-p3-spec.md`：重写为最终版——`FigContext(domain)` OO（`compile`+`strip`+`system_prompt`）、无 `agent/human` 参数、图说明固定格式、老化归 `FigContextManager`、**无独立薄状态行**。
- `design-vision-image-fields.md` §6/§7/§8/§10：删薄状态行、compile 改 OO 签名、边界句同步。
- `design-vision-image-fields-checklist.md`：P3/P4 按上述勾选。

---

## 关键决定（已定案，新会话别推翻）

1. **P3 = `FigContext`，只管 `compile`+`strip`+`system_prompt`**；**不感知 agent/人/轮次语义**（这两样归上层编排/管理者）。
2. **老化 = `FigContextManager`** 持有 `step`/`k`/`live deque`；每轮从队头摘 `step 差 > k` 的图块（`strip` 移图块、text 留底）；某 FIG **最后一块活图块**出窗才 `clear_fig_block` 清 annos。K 用连续 `step`，无"单指针"哲学。
3. **图说明固定格式**（这就是"状态"）：`F:id | 原尺寸 | @全图 c(..) s(..) shape → 位图 w×h`（自含重载锚）+ 标注行 + `> ⚠️`(仅异常) + `────────` + `你的备注:`。**无独立薄状态行**。
4. **文字永续、不做摘要**（只摘图、不摘文字）；`note` 瞬态、第二人称 `你的备注:`、不写回图/存储/缓存。
5. **单轮至多 1 图块、无 `load_many`**；`compile` 纯呈现、**不去重/防复读/「第 N 次」提示**。
6. **身份去重稳定（P4）是 P3 重载锚前提**：同 `(path,window)` 恒同 FIG_ID；**`Source.registry` 故意不回收**（锚要稳定）；**只有 `cache/` 可清**。`clear_cache` 目前**未实现**（design §8 有列出，实现里没有），Yz 说现在不做清理。
7. P1/P2 边界（勿踩）：`image_ctx` 只管图对象状态；`fig_meta`/`clear_fig_block` 是给上下文管理器的接口面。

---

## 下一步（P3 目的层 vf6 探针——唯一悬着项）

**目的**：验证「图被摘后，文字自含锚能否让模型重建窗口」（checklist 残留探针 §139「K 轮滚动+重载锚长会话复核」）。

**⚠️ 关键前置**：现有 `/tmp/kilo/vision/vf6.py` 的 SYSTEM 协议是**旧「视野区/中央凹」**，**不是 P3 图说明锚格式**。要跑探针必须先造一个**产出 P3 消息的 driver**（复用 image_ctx + FigContextManager + LmClient 的小循环），否则 vf6 直接跑验不了 P3 自含锚。

**建议落地顺序**：
1. 先起后端：`cd /home/zhengyp/work/A/cogos && python3.11 -m cogos.lm_service.cli server --port 11434`（**会话级，每新会话重开**）。KEY `ik_REDACTED`。
2. 造 P3 消息 driver（薄）。
3. **先跑任务 A（便宜、最聚焦）**：给模型**只有图说明文字（无图）**，问"请重新定位到该窗口"，要求输出 `view` 的 `@窗口` center/size；判对 = 坐标 ≈ 锚真值。场景默认 `windows.png` + 目标 `工具(T) @ c(.188,.042)`；也可换 msg4/msg5 的"体温符号对照表"。
4. A 过了再上任务 B（多轮 + 人为让图块超龄，看能否靠锚重载继续）——字面 checklist 探针，成本高。

**vf6 用法**：`cd /tmp/kilo/vision && python3.11 vf6.py <msg.txt> --scene windows.png --out DIR [--no-thinking]`。

---

## 运行

- 后端：`cd /home/zhengyp/work/A/cogos && python3.11 -m cogos.lm_service.cli server --port 11434`（会话级，重开）。KEY `ik_REDACTED`。
- 测试：`cd /home/zhengyp/work/A/cogos && python3.11 -m pytest -q`（需 python3.11）。子集：`-m pytest tests/cog_ctx -q`（P3）、`tests/image_ctx -q`（P1/P2/P4）。
- vf6：`cd /tmp/kilo/vision && python3.11 vf6.py <msg.txt> --scene windows.png --out DIR [--no-thinking]`。
- 飞书：`cd /home/zhengyp/work/A/locus && python3.11 tools/feishu_notify.py "<文本>"`（默认 YZ）。

---

## 遗留 / 待办（非阻塞）

- **超龄回收**：`Source.registry`/`cache/` 长会话会积。registry **故意不回收**（锚稳定）；`cache/` 可清但 `clear_cache` 未实现。若要做清理，需先定"如何不坏锚"的降级方案——独立设计题，待议。
- `detail=original`（禁厂商二次 resize）归请求构造层（P2+/vision-func），未接；坐标安全靠主动控图到封顶已保住。
- 指纹 4 位小数是否误撞同构 window（必要时升 6 位）；`estimate_peak` 对"小口大图"是否误拒——待实测（checklist 残留 §8）。
- `desc/` canonical 层未落盘（P1/P2/P3 只留内存）。
- 视觉子系统（vision-system-design §14）与 image_ctx 融合，后续再议。

---

## 关键文件

- P3 实现：`cogos/cogos/cog_ctx/{context.py, manager.py}` + `__init__.py`；测试 `tests/cog_ctx/{test_p3,test_manager}.py`
- P4 验证：`tests/image_ctx/test_p4.py`
- 实现规格：`cogos/docs/design-vision-image-fields-p3-spec.md`（最终版，OO FigContext）
- 设计本体（最终定稿）：`cogos/docs/design-vision-image-fields.md`
- 验收清单：`cogos/docs/design-vision-image-fields-checklist.md`（P1-P4 勾完，P3/P4 已勾）
- P1 实现：`cogos/cogos/image_ctx/{view,domain,render,tools}.py`
- 小原型：`/tmp/kilo/vision/anno_proto.py`、`anno_draw.png`
- 上游设计：`cogos/docs/vision-system-design.md`（§4/§6/§14）
- 交接：`handoff-vision-image-fields-6.md`（P1+P2）、`-5.md`（P1 规格+两拍板）
