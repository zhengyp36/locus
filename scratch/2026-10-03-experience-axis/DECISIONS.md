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

- **代码**：cogos master `7a67fc3`（7 files changed，未 push）。`experience.py`(新)·`flow.py`·`consciousness.py`·`app.py`·`tests/agent/test_experience.py`(新)·`test_flow.py`·`scripts/exp_experience_recall.py`(新)。
- **机制**：`tests/agent tests/cog_runtime` = **324 passed / 3 skipped**；全量 = **1290 passed / 1 failed / 5 skipped**（唯一 fail `tests/image_ctx/test_p2.py` 硬编码临时素材缺失，与本刀无关）。
- **行为探针**（真 deepseek-v4-flash ＋ FakeTelecom；同事件＋同 seeded `未了` 段，仅 recall 开关）：**分叉=True**。
  - `recall_on`：采纳=理，6 轮，`toolbox`×4，外发 1。
  - `recall_off`：采纳=理，12 轮（撞满工具轮），`toolbox`×13，外发 0。
  - 结果文件 `/tmp/kilo/experience_recall_probe/result.json`。
- **跨事件稳定**：新增 `test_open_knot_stable_across_events`——第二事件装载读回第一事件 `<未了>`；新 `SegmentStore` rebuild 后 `open_knots` 仍稳定。
- **未跑**：真身份 e2e（真 daemon＋真 app，真发飞书＝外溢＋第二账号编排）→ 留 YZ。
- **收口**：entry `projects/cogos/entries/2026-10-03-cogos-experience-axis-readback.md`；glossary 更新 `段`/`经历轴`＋新增 `回边`；`current.md` 更新。
