# handoff · 记忆模块 v0 动手（执行任务）

> 交接自：2026-10-05 讨论会话（收口）。执行按 `rules/task.md`；**逐步验收，每步做完停下来等 YZ**。
> 先读本文件 → `entries/2026-10-05-cogos-memory-v0-bootstrap.md` → `glossary.md`（好奇·新奇取向／空闲事件·tick／浅浮现 + 注入·种子）→ 按需前段 memory entries。

## 第一句话（给新会话，单列）

读 `scratch/2026-10-04-memory-module/handoff-v0-build.md` 与 `entries/2026-10-05-cogos-memory-v0-bootstrap.md`；按 `rules/task.md` 执行，逐步验收、每步做完停下来等 YZ。先从 Step 1（场景＋判据）做起，不落码。

## 目标

把**记忆模块 v0 ＋ 自启环路**造起来（cogos，代码在 `../cogos`）。**不一次到底**，5 步逐步验收。

## 已定（勿重讨论，锚在 entry）

- v0 形状、生念（种子常驻／好奇＝信息缺口）、tick、环路、浮现/主动回忆、自我涌现——全见 `entries/2026-10-05-cogos-memory-v0-bootstrap.md`。
- **悬置（取值类，边做边定）**：种子措辞、新奇怎么算、效价从哪来、tick 节奏、浅浮现→主动回忆激活强度。

## 5 步（每步：做什么 → 验收判据；每步结束停下等 YZ）

**Step 1 · 场景＋判据（不落码）**
- 做：写 scratch，定 场景A（空白启动）＋场景B（跨语义召回），各带可证伪判据＋**撤种对照**。
- 验收：YZ 读，判"可证伪、判据明确、合目标"。

**Step 2 · 记忆 v0**
- 做：新记忆模块（种子层＋段；`记/忆/整理`；单值；自我路＋语义路；浅浮现留位），替掉 `experience.py` 的 dict 检索。
- 验收：单测能记能取；跨语义线索召回**单条**、不塌主题（对照）。

**Step 3 · tick＋生念**
- 做：tick → 空闲事件 → 种子产缺口 → 生念 → 行动 → 落段。
- 验收：无输入、无经历，环转一圈、段落盘；**撤种对照不生念**。

**Step 4 · 环路接线**
- 做：外/内事件统一入口；`装载→生成→动手→判结→沉淀`；回边。
- 验收：外部事件与 tick 走同一条环；出现回边读＋落段。

**Step 5 · 收口**
- 做：蒸馏进 entries/glossary/current（含 why＋被否），删 scratch 草稿。
- 验收：YZ 核对术语与结论。

## 纪律（task.md 摘）

- 目标内能推的**自决**；推不出→带倾向求助；目标变更→回讨论。
- 默认自主提交/推送、提交前跑测试、`secrets` 不入库。
- 验收判据从**目标**推；不用自写 e2e 自证。
- 动手前 `set_timer` 600s 盯偏航；`start_context_watch` 20s/150K。

## 锚

- 结论：`projects/cogos/entries/2026-10-05-cogos-memory-v0-bootstrap.md`
- 术语：`projects/cogos/glossary.md`
- 定义层：`projects/cogos/entries/2026-10-05-cogos-motive-projection-roothood.md`
- 前段 memory：`projects/cogos/entries/2026-10-03-cogos-memory-{model,projection-unity,index-consolidation}.md`
- 代码：`../cogos`（`agent/experience.py` 降为反例；`agent/flow.py`/`consciousness.py`/`app.py` 是现有环）
