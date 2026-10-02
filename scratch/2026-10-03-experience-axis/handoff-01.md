# handoff-01 · 经历轴骨架 + 第二刀回边（交接待续）

> 交接自：10-03 讨论会话（"从使用角度"收敛时间维 / 经历轴）。
> 本文件 = **任务入口**。上游：`README.md`（含「认可口径」）· `experience-py-shape.md`（最小形状）。

## 一句话

骨架先行：落 `cogos/agent/experience.py`（段 schema ＋ 读侧索引 ＋ `retrieve`/`open_knots`），再接**第二刀回边**（段→装载），让"经历影响行为"闭环、可验收。

## 第一句话（给新会话，单列）

读 `scratch/2026-10-03-experience-axis/handoff-01.md` 并照它开工；先落 `cogos/agent/experience.py` 骨架。

## 读什么

1. 本文件。
2. `README.md` →「认可口径」节（段 schema / 首版索引 / 搁置表 / 层级(RAPTOR) / 淘汰语义）。
3. `experience-py-shape.md`（最小形状：数据/索引/接口/挂点/验收）。
4. `projects/cogos/entries/2026-10-03-cogos-first-cut-flow-claim.md`（v2.2 ＋ 第一刀现状）。
5. 代码：`../cogos/cogos/agent/flow.py`（`SegmentStore`/`segment_from_flow`）· `consciousness.py`（`_load`/`_build_material`/`_land`）。

## 目标 / 计划

**A. 骨架** `cogos/agent/experience.py`（升级 `SegmentStore`，不重写）：
- `segment_from_flow` 补齐字段：`人[]`(机械取 `msg.source`，P8 退化解)、`主题:null`、`预测:null`、`refs:[]`、`thread=id`。
- 读侧内存索引 `by_time`/`by_person`/`open_knots`/`by_thread`（启动扫 L0 重建）；`retrieve(keys,budget)`（近因排序、权重=0）；`open_knots()`。
- 测试 `tests/agent/test_experience.py`（append/reload 一致、rebuild==增量、open_knots 跨 append 稳定）。

**B. 回边** `consciousness.py`：`_load`/`_build_material` 注入「过去」（`open_knots()` ＋ 同来源近段），加**可掐断开关**供对照验收。

**C. 验收**：
- 机制：`python3.11 -m pytest tests/agent tests/cog_runtime -q` ＋ 全量。
- 行为探针（真模型＋FakeTelecom）：同事件 ×｛注入历史／不注入｝→ 行为分叉。
- 真身份 e2e：真 daemon＋真 app，跨事件 `open_knots` 稳定。

## 不做（占位搁置）

权重 · 主题/工具索引 · 误差切点（首版用事件界/切细）· 后压/蒸馏 · 读时现整 · 控制拍。

## 纪律（各会话通用 · YZ 10-03 指示）

- **目标导向自决**：能推的不问，**决策当场记录**（写进本任务 scratch），**结束时汇总一次**。
- `start_context_watch`：间隔 **20s**、阈值 **120K**，超限即交接；`set_timer(600s)` 只盯偏航。
- 命令用 **terminal 工具**，不用 bash。
- 提交默认自主（提交前跑测试）；红线＝secrets / 不可逆 / 外溢。
- **链式交接**：本任务可连续交接（`handoff-02`、`03`…），**上限 5 跳**；顺序＝写 `handoff-NN` → 更新 `README.md` 状态 → **清异步源**（timer / terminal / background_process / 飞书 pin 与 inbox）→ `handoff` 工具 → 通知 YZ。
- bridge 侧：该会话若被飞书 pin 指到，入站会唤醒旧会话 → `/pin` 改指后继、清 `inbox`；兜底＝被误唤醒时先判"本会话已交接"、立即停并转给后继。

## 遗留 / 洞（别丢）

- `关联` 怎么打（P8 唯一入口）· 权重构造式 · 未来/计划形态（段/预测/挂起）· P7 判结主体 · 读时现整产物落不落轴。
- 第一刀字段占位待升级（`thread=id`、`refs=[]`、`结`）。
