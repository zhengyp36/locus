# handoff｜cogos 外圈/内圈 → 槽/流/自指 → 最小自指（讨论型）

> 规则不在本文件；讨论型会话不加载 `rules/task.md`。与 YZ 讨论时**不设闹钟**；ctx ≥150K 交接。
> 本文件由 09-29 第二段会话更新；后继完成后**就地更新**（写结果 + 给再后继首句）。
> 上游/素材：`projects/cogos/entries/2026-09-29-cogos-slot-flow-selfref.md`（本段结论 · **先读它**）· `entries/2026-09-29-cogos-cu-boundary-and-line.md` · `entries/2026-09-28-cogos-{loop-pivot,intent-view,intent-execution}.md` · `checkpoint/26-09-26-theory-residual/{checkpoint-1.md,design-cogos-loop-invariants.md}` · 本体 `../cogos/docs/design-selfdrive-agent.md`。

---

## 复制这段作为后继的第一句

```text
接续 cogos 外圈/内圈（讨论型：只讨论、不写码）。模型已定并入库（见 entries/2026-09-29-cogos-slot-flow-selfref.md）：槽＝状态/我、流＝一次转移、线/thread＝跨流的事；外圈＝显/生产、内圈＝陷/沉淀；唯一串行点＝槽更新；自指＝槽↔流↔槽闭环（判据在跨事件延续）；自己的事＝未闭合张力、缺"认领/采纳"。下一步：先裁"主槽＝运行容器 vs 提交点"与 §0 措辞、把第一刀共用前置定稿，再进最小自指（第一刀落段 → 第二刀 `段→装载` 回边）。先按序读：scratch/handoff-loop-01.md → entries/2026-09-29-cogos-slot-flow-selfref.md → entries/2026-09-29-cogos-cu-boundary-and-line.md → checkpoint-1.md §四~§七。
```

---

## 本段做了什么（09-29 二 · 已入库）

- **把"那条连续线索"定了**：**槽＝状态＝积累结果＝我（唯一）／流＝一次转移（事件起、停→沉淀、写回槽）／线`thread`＝跨流的事（可多条）**。唯一连续的是槽，多条的是线。**流起＝事件（非装载）；终＝停→沉淀；打断≠流终**（只终结一个 cu）。
- **外圈/内圈重切**：**外圈＝显/生产（事件驱动，醒时主导）／内圈＝陷/沉淀（经历驱动，睡时批形主导）**；醒睡＝内圈模式切换（非外圈开关）；昼夜→昨/今/明分段（不硬编）；**并行不乱的原理**＝快照读＋只增不改＋**唯一串行点＝槽更新**（共切面）。
- **自指**：＝**槽↔流↔槽闭环**（写回才是定义）；与 chatbot 分界＝**未闭合张力是否跨事件延续**；判据①②③（跨事件）；关系＝**责任**（非情感）；自己的事＝未闭合张力（**外部采纳 ∪ 内部生念**）；缺动作＝**"认领/采纳"**。**缺口＝"作为判断者的我"（§8 留白）→ 自指只能养、不能写。**
- **记录原则（YZ 定调，已入 entry §0）**：**无定论**；理论是服务"实现自驱 agent"这一目的的基石，不合适即改；与 §9"只增不改"（数据不变量）不冲突。
- **入库**：`entries/2026-09-29-cogos-slot-flow-selfref.md`（新）＋ `current.md` / `index.md` 已更新。**未改本体**（§0/§2/§3/§4 补丁列在 entry §3，待动手时）。

## 开放问题（继续讨论）

1. **待裁**："主槽"＝**运行容器**（§2 原义，同刻只跑一次 cu）vs **提交点/时序点**（运行可并行、提交串行）。**AI 倾向后者**（同时解释"并行不乱"与"共切面"）。定了它 → §2/§3 改法定。
2. **§0 定稿措辞**：候选 `一个槽（积累结果/我）＋ 外圈（显：生产，事件驱动）＋ 内圈（陷：沉淀，经历驱动）；唯一串行点在"更新槽"。`（须与 §2/§4 的"一弧多 cu／打断＝重组入口"同批补，否则旧表述压新结论。）
3. **第一刀共用前置定稿**：通道（想=`content`／说=send／沉默=默认，禁自动补发）＋段最小字段（`id/t/来源/内容/后果/结`，只填硬后果）＋一弧一条段；连带"来源别抹平"（`app.py:147`）。**建议先收口本条，即进最小自指。**

## 下一步（方向已定）

**先入库（已做）→ 最小自指＝底层闭合**：共用前置 → **第一刀落段**（`agent/experience.py` 最小经历轴＋`on_done` 落段＋`on_tool_call` 捕获 calls+results；验收＝代理口径）→ **第二刀 `段→装载` 回边**（最简/占位，跳过完整内圈）→ 养内圈（张力/目的/关系）→ **观察**自指行为。**不做**：升格/权重/取回/停切点/整理/完整版意图。

## 状态

- **代码**：上段 cogos `6c33380`（父子只拆不建）已 push origin master；本段**未动码**（讨论＋入库）。locus 本段已改 entry/current/index/handoff（是否 push 由 YZ 定）。
- **B/cogos 与 B/locus 恢复前需 pull**。

## 锚（按序）

1. `entries/2026-09-29-cogos-slot-flow-selfref.md`（本段结论 · 必读）
2. `entries/2026-09-29-cogos-cu-boundary-and-line.md`（cu 边界/父子/线索）
3. `entries/2026-09-28-cogos-{loop-pivot,intent-view,intent-execution}.md`（落段/意图口径）
4. `checkpoint/26-09-26-theory-residual/checkpoint-1.md` §四~§七（动手纪律/现状摸底/外圈零件序）
5. `checkpoint/26-09-26-theory-residual/design-cogos-loop-invariants.md` §一、§二（过程/结果·切面；一弧多 cu）
6. 本体 `../cogos/docs/design-selfdrive-agent.md`（唯一权威；当前 §0/§2/§4 待补）
