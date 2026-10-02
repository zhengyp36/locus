# cogos：P8 关联机械第一刀（10-03）

> 性质：**P8 首刀收口件**——把段上的跨事件「关联」从全占位推到**只机械打**（不做模型抽取）。承第二刀 `entries/2026-10-03-cogos-experience-axis-readback.md`（读回）＋ scratch `2026-10-03-experience-axis/`。
> 术语权威＝`glossary.md`。代码 cogos master **`9775293`（已 push）**。写法：结论 + why + 被否。

## 1. 落地

- **`experience.py`**：
  - `segment_from_flow(flow, *, people, thread, refs)`——三字段可由调用方传入续线信息；不传则退回退化映射（`人=[来源]` / `thread=id` / `refs=[]`）。
  - `open_thread_for(person)`：找该来源**最近的开放线**——按 `thread` 分组取每线**最新**落段，开放 iff 其 `结∈{未了,挂起}`（`了` 段关闭线）。
  - `continuation_for(person)`：有开放线→`{people=线人∪{来源}, thread=线根, refs=[continue_of→该线最新开放段]}`；无→`None`。
- **`consciousness.py::_land`**：落段前算续线并传给 `segment_from_flow`（写侧唯一落段点；读侧不动）。
- **测试**：`tests/agent/test_experience.py` ＋5（传入关联、选最近开放线、续线、人并集、跨事件同 thread、**关线后不再续**）。

## 2. 验收

- `tests/agent` **300 passed / 3 skipped**；`tests/agent tests/cog_runtime` **329 passed / 3 skipped**；全量 **1296 passed / 1 failed / 5 skipped**（唯一 fail＝`tests/image_ctx/test_p2.py` 硬编码素材缺失，无关）。

## 3. 目标内自决（why ＋ 被否）

- **机械，不模型抽取**：唯一可靠信号＝事件来源＋已有开放线；模型抽取需锚分类学（P8 本体）先长。被否：模型抽关联（无本体、易编）。
- **按「线」判开放（关键修正）**：`open_knots` 是**段级**，旧未了段被后续 `了` 段关闭后仍留在段级视图里；照段级续线会把**已关闭的线一直续下去**。改为「某 thread 开放 iff 其最新落段开放」。被否：段级直接续线。
- **选最近一条开放线**；`thread` 继承线根、`refs` 指向该线最新开放段；`人` 取线人并集。被否：一人多线全并（过并）、按主题匹配（需主题索引，本刀不建）。
- **只写不读**：本刀不改装载/生成提示（关联暂无读侧用法）。被否：本刀就改装载按 `thread` 取回。

## 4. 遗留 / 洞

- 关联**无读侧用法**（只写）——下一刀候选：装载按 `thread` 取回整线。
- 一人多开放线只取最近（未并/未选）。
- `open_knots()`（段级）与续线（线级）口径**暂不一致**。
- thread 关闭无「兑现/放弃」细分；`主题/预测/host` 仍占位。
- 模型抽取关联＋**P8 锚分类学**未启（等读侧用法暴露需求）。
