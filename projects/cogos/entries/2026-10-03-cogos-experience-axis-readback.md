# cogos：经历轴读侧落地（骨架 ＋ 回边）（10-03）

> 性质：**第二刀收口件**——把经历轴从"只写"推到"能读回"。承第一刀 `entries/2026-10-03-cogos-first-cut-flow-claim.md`（段/流脊柱）＋ scratch `2026-10-03-experience-axis/`（已随收口删除）。
> 术语权威＝`glossary.md`。代码 cogos master **`7a67fc3`（已 push）**。写法：结论 + why + 被否。

## 1. 落地

- **`cogos/agent/experience.py`（新）**＝段 schema ＋ 读侧：
  - `segment_from_flow` 补 `人[]`（机械取事件来源＝P8 退化解）、`主题:null`（只存不索引）；`预测/refs/thread` 仍占位。
  - `SegmentStore` 升级：L0 `segments.jsonl` append-only 不变；构造/`rebuild()` 扫 L0 重建内存索引 `by_time`(自然 append 序) / `by_person` / `open_knots`(未了＋挂起) / `by_thread`；`retrieve(keys{person,thread,knot,since}, budget)`＝各索引取→去重→**近因**排序→预算截断（**权重=0**）；`open_knots()`。
- **`flow.py`**：`Flow`/`parse_verdict` 保留，`SegmentStore`/`segment_from_flow` 改为 re-export。
- **回边 `consciousness.py`**：`recall` 开关（默认开，`Agent(..., recall=)` 透传）；`_load`（认领）与 `_build_material`（生成）注入 `_past_context` ＝ 全量 `open_knots()` ＋ 同来源近段（`budget=3`）。
- **测试/探针**：`tests/agent/test_experience.py`、`test_flow.py` 跨事件稳定；`scripts/exp_experience_recall.py`。

## 2. 验收

- **机制**：`tests/agent tests/cog_runtime` **324 passed / 3 skipped**；全量 **1290 passed / 1 failed / 5 skipped**（唯一 fail＝`tests/image_ctx/test_p2.py` 硬编码临时素材缺失，与本刀无关）。
- **行为**（真 `deepseek-v4-flash`＋FakeTelecom；同一事件＋同一 seeded `未了` 段，仅 `recall` 开关不同）：**分叉=True**。
  - `recall_on`：6 轮、`toolbox`×4、外发 1 → 认领并收束。
  - `recall_off`：12 轮（撞满工具轮）、`toolbox`×13、外发 0 → 空转。
  - 证据 `/tmp/kilo/experience_recall_probe/result.json`。
- **自指/跨事件**：deterministic 测试证明第二事件的装载读回第一事件的 `<未了>`，且新进程 `rebuild()` 后 `open_knots()` 仍稳定。
- **真身份 e2e（已跑，10-03 补）**：真 feishu daemon＋lm-service＋真 app `python -m cogos.agent.app --agent ~/.cogos/agent/tangyu`（YZ 授权外溢）；`COGOS002:A0001`（李恪）真发两条飞书至 `COGOS002:A0005`（唐钰），两条均落段（新 schema、`人=["COGOS002:A0001"]`、判**不理**、`结=了`）。**跨事件读回证实**：事件 2 装载 prompt 含「沿经历轴读回的过去 / `<近来>`」，列回事件 1 同来源近段（＋旧段），模型据此认出"重复要求"→ 仍判不理。新进程 `SegmentStore.rebuild` 后 `open_knots()` 稳定为空、旧形状段（无 `人`）经 D4 回退纳入 `retrieve`、公开入口全程未崩。证据 `checkpoint/26-10-03-experience-axis/e2e-readback-evidence.md`。

## 3. 目标内自决（why ＋ 被否）

- **D1 模块切分**：experience.py 装 schema+读侧，flow.py re-export。why：handoff「升级 SegmentStore，不重写」＋保住既有 import。**被否**：类名改 `Experience`（churn）；schema 留 flow.py（不符「段 schema 落 experience.py」）。
- **D2 `by_time` ＝自然 append 序**，非独立倒排。why：最小形状明写「天然顺序（list）」；调和 `time-axis.md §5`「时间不建倒排」与认可口径列 `by_time`。
- **D3 `host` 不加**。why：handoff 补齐清单只列 `人/主题/预测/refs/thread`，且无生产者。**被否**：加 `host:None` 占位（无意义＋扩 schema）。
- **D4 旧段兼容**：无 `人` 的旧段，`by_person` 回退 `来源.source`。why：真身份 `~/.cogos/agent/tangyu/memory/segments.jsonl` 已有旧形状段，rebuild 不能静默丢。
- **D5 开关**：`recall` 默认开；A/B 传 `False`。
- **D6 注入内容**：`open_knots` 全量＋同来源近段(=3)，**认领与生成都注**。**被否**：只注一处。

## 4. 遗留 / 洞（别丢）

- 第一刀占位待升级：`thread=id`（"起始段 id"语义未实现）· `refs=[]` · `主题` 只存不索引 · `预测` 空。
- `host` 字段（认可 schema 有，无生产者）。
- 首版不做（占位搁置）：权重（=0）· 主题/工具索引 · 误差切点 · 后压/蒸馏 · 读时现整 · 控制拍。
- 老洞：`关联` 怎么打（P8 唯一入口）· **P7 判结主体**。
- 命名：`time-axis.md` 提 **经历轴→时间轴**，未收口；glossary 仍 `经历轴`。
