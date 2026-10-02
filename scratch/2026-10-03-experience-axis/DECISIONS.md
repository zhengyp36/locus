# decisions · handoff-01 执行（骨架 + 回边）

> 目标导向自决，当场记录；结束汇总一次。写法：决定 + why + 被否/替代。

## 骨架

- **D1 模块切分**：新建 `cogos/agent/experience.py` 装段 schema（`segment_from_flow`）+ 读侧索引 `SegmentStore`；`flow.py` 保留 `Flow`/`parse_verdict`，从 experience **re-export** `SegmentStore`/`segment_from_flow`。
  - why：handoff A「升级 SegmentStore，不重写」+「落 experience.py（段 schema + 读侧索引）」；re-export 保住 `consciousness.py`/既有测试的 import。
  - 被否：类名改 `Experience`（徒增 churn，handoff 明说升级 SegmentStore）；只搬 store、schema 留 flow.py（不符「段 schema 落 experience.py」）。
- **D2 `by_time` 语义**：＝自然 append 序（id list），不是独立倒排索引。
  - why：`experience-py-shape` 明写「天然顺序（list，按 id/t）」；`time-axis.md §5`「时间不建倒排索引」与 README 列 `by_time` 由此调和。
  - 被否：为 by_time 单建 `dict`（与 time-axis 冲突、且无用法支撑）。
- **D3 `host` 字段**：**不加**。认可 schema 有 `t,host 坐标`，但 handoff A 的补齐清单只列 `人/主题/预测/refs/thread`，且 host 无生产者。
  - 被否：加 `host: None` 占位（无意义 + 顺手动 schema，违「不许顺手扩」）。→ 留作 open item（P8 坐标工作时定）。
- **D4 旧段兼容**：L0 里没有 `人` 的旧段，`by_person` 回退用 `来源.source`。
  - why：真身份 `~/.cogos/.../segments.jsonl` 已有旧形状段；rebuild 不能静默丢。

## 回边

- **D5 开关**：`Consciousness(recall=True)` / `Agent(..., recall=True)`，默认开；探针 A/B 传 `False`。
  - why：handoff B「加可掐断开关供对照验收」。
- **D6 注入内容**：`open_knots()` 全量（未了+挂起）+ 同来源近段 `budget=RECENT_SEGMENTS=3`；注入点＝`_load`（认领）与 `_build_material`（生成）。
  - why：认领是「我」投影事件处；生成也需材料。权重=0，排序纯近因。
  - 被否：只注 `_load`（生成拿不到）；只注生成（认领分叉不受历史影响）。

## 结果（10-03 执行）

- **代码**：cogos master `7a67fc3`（7 files changed，**已 push**）。`experience.py`(新)·`flow.py`·`consciousness.py`·`app.py`·`tests/agent/test_experience.py`(新)·`test_flow.py`·`scripts/exp_experience_recall.py`(新)。
- **机制**：`tests/agent tests/cog_runtime` = **324 passed / 3 skipped**；全量 = **1290 passed / 1 failed / 5 skipped**（唯一 fail `tests/image_ctx/test_p2.py` 硬编码临时素材缺失，与本刀无关）。
- **行为探针**（真 deepseek-v4-flash ＋ FakeTelecom；同事件＋同 seeded `未了` 段，仅 recall 开关）：**分叉=True**。
  - `recall_on`：采纳=理，6 轮，`toolbox`×4，外发 1。
  - `recall_off`：采纳=理，12 轮（撞满工具轮），`toolbox`×13，外发 0。
  - 结果文件 `/tmp/kilo/experience_recall_probe/result.json`。
- **跨事件稳定**：新增 `test_open_knot_stable_across_events`——第二事件装载读回第一事件 `<未了>`；新 `SegmentStore` rebuild 后 `open_knots` 仍稳定。
- **真身份 e2e（YZ 授权后补跑，10-03）通过**：真 daemon＋lm-service＋app，A0001 真发两事件；事件 2 装载读回事件 1 同来源近段、`open_knots` 稳定空、旧段 rebuild 兼容、公开入口未崩。证据已转存 `projects/cogos/checkpoint/26-10-03-experience-axis/e2e-readback-evidence.md`。
- **收口**：entry `projects/cogos/entries/2026-10-03-cogos-experience-axis-readback.md`；glossary 更新 `段`/`经历轴`＋新增 `回边`；`current.md` 更新。

## P8 关联第一刀（机械打关联，10-03 续）

> 承 `handoff-02 #3`。目标＝装载直取的关联入口，**先只机械打**（不做模型抽取）。

- **D7 首刀＝机械打关联，不做模型抽取**。why：当前唯一可靠信号＝事件来源＋已有开放线；模型抽取需要锚分类学（P8 本体）先长出来；认可口径明写「首版 P8＝只机械打(来源→人/thread/结)」。**被否**：让装载/判结模型抽关联（无本体、易编、不可重建）。
- **D8 续线判据＝按「线」而非「段」判开放**：某 `thread` 开放 iff 其**最新**落段 `结∈{未了,挂起}`；`了` 段关闭该线。why：`open_knots` 是段级，旧未了段被后续 `了` 段关闭后仍留在段级视图里，照段级续线会把**已关闭的线一直续下去**（工作树原实现即此漏）。**被否**：段级 `open_knots` 直接续线。
- **D9 选线**：来源 `person` 在开放线中取**最近**一条。**被否**：一人多开放线全并（过并）；按主题/时间窗匹配（需主题索引，本刀不建）。
- **D10 thread 继承线根**（`prior.thread or prior.id`）；`refs=[{kind:continue_of,id:prior.id}]` 指向**该线最新开放段**（非线根，保留链）。
- **D11 人并集**：`人 = 该线人 ∪ {来源}`，顺序去重，喂 `by_person`。
- **D12 落点＝`_land`（写侧唯一落段点）**；读侧不改（`_past_context` 仍只用 `open_knots`＋同来源近段）。**被否**：新增独立「关联拍」；本刀就改装载按 thread 取回（留待读侧真需要时）。
- **实现**：`experience.py` 加 `open_thread_for`/`continuation_for`，`segment_from_flow` 收 `people/thread/refs`；`consciousness.py::_land` 传续线。cogos **`9775293`（已 push）**。
- **验收**：`tests/agent` 300 passed/3 skipped；`tests/agent tests/cog_runtime` 329 passed/3 skipped；全量 1296 passed/1 fail（唯一 fail＝`tests/image_ctx/test_p2.py` 素材缺失，无关）/5 skipped。
- **洞**：一人多开放线只取最近（未并/未选）· `open_knots()`（段级）与续线（线级）口径暂不一致 · 关联仍**无读侧用法**（本刀只写）· thread 关闭无「兑现/放弃」细分。
