# handoff｜cogos 外圈/内圈：线索命名与第一刀前置（讨论型）

> 规则不在本文件；讨论型会话不加载 `rules/task.md`。与 YZ 讨论时**不设闹钟**；ctx ≥150K 交接。
> 本文件由 09-29 会话写给后继；后继完成后**就地更新**（写结果 + 给再后继首句）。
> 上游/素材：`projects/cogos/entries/2026-09-29-cogos-cu-boundary-and-line.md`（本会话结论）· `projects/cogos/entries/2026-09-28-cogos-{intent-view,intent-execution,quota-pacing,loop-pivot}.md` · `projects/cogos/checkpoint/26-09-26-theory-residual/{checkpoint-1.md,design-cogos-loop-invariants.md}` · 本体 `../cogos/docs/design-selfdrive-agent.md`。

---

## 复制这段作为后继的第一句

```text
接续 cogos 外圈/内圈讨论（讨论型：只讨论、不写码）。任务 = 先与 YZ 定下"那条连续线索"的命名（主槽=唯一容器 vs thread/线=可多条）与总纲"两条链"是否改述为"一个主槽 + 两种驱动"，再定第一刀落段的共用前置。先按序读：scratch/handoff-loop-01.md（本交接：开放问题/状态/锚）→ projects/cogos/entries/2026-09-29-cogos-cu-boundary-and-line.md → projects/cogos/entries/2026-09-28-cogos-intent-view.md 与 -intent-execution.md → projects/cogos/checkpoint/26-09-26-theory-residual/checkpoint-1.md §四~§七。
```

---

## 本会话做了什么（09-29）

- **起点**：YZ 问"先实现意图还是先考虑外圈"。→ 结论：意图**横跨外圈中段（cu/装载/沉淀）＋内圈（程序式/权重）**，不是与外圈并列；**便宜版意图＝第一刀落段的同接缝**（回看只渲染头尾）。顺序＝**共用前置 → 第一刀落段 → 第二刀回边 → 完整版意图＋内圈**。否"先实现完整意图"（依赖倒置）。
- **cu 本体**：**cu ＝ 机制不介入的 append 自转区间**（实现单位，**非语义单位**）；稳定单位是**弧**；**一弧可多 cu**（打断点＝重组入口＝"存→取"的环内版）。打断源：回看（插入型）／上下文过长（压缩型）；叫停手段：预算／回看判停／误差切点。
- **父子 cu**：**拆**（判据＝**关系 ≠ 属性**，父子属**编排层**）。**已执行**：cogos `6c33380`（去 `unit.py`/`runtime.py` 的 `parent/children/add_child/_all_children_done`、删 `test_parent.py` 等；`tests/cog_runtime` **31 passed**、全量 **1276 passed/5 skipped**，仅 1 个已知无关 `image_ctx` 素材缺失 fail）。替代（回看＝`on_tool_call` 内 `await` 子 cu；fan-in＝`gather`）**未建，留编排层需要时**。
- **命名**：**开放**（见下）。

## 开放问题（继续讨论）

1. **那条连续线索的命名**。YZ 提：cu 被打断换新 cu，但仍是**一条连续线索**；外圈/内圈都靠它承载，它不是外圈/内圈，也可能其他。
   - AI 倾向：**主槽**＝唯一时序/决策中心（**唯一容器**）；**`thread`／线**＝槽上的一条事（**可多条**、跨 cu）；载体＝经历轴的段（`thread` 字段）＋ `refs` 链，**不是运行时对象**。
   - **待 YZ 裁**：名字定 `thread`／线 否？"主槽/流"保留为唯一容器否？
   - 注：**主槽**定义出自旧 design `checkpoint/26-09-17-agent-theory/design-cogos-agent-form.md:40`（唯一时序与决策中心；内容可装卸、有时间线、后台流不占槽）；总纲沿用（环＝主槽一次"机制三段夹一 cu"；流＝主槽流（唯一）/后台流）。
2. **总纲 §0 表述**：是否把"外圈/内圈＝两条链"改述为"**一个主槽 + 两种驱动（事件/经历）**，线可多条"。
3. **下一步落法**：共用前置（**通道想/说/沉默**、**段最小字段**、**一弧=一意图单位口径**）→ 第一刀落段（`on_done` 挂点、`on_tool_call` 捕获 calls+results、代理口径判据）→ 第二刀 `段→写回→装载` 回边。详见 `entries/2026-09-28-cogos-loop-pivot.md` 与 `checkpoint-1.md §七`。

## 状态

- **代码**：cogos **A 工位** master 与 origin 同步、工作树干净；locus 同步且已 push。**B/cogos 与 B/locus 恢复前需 pull**。
- **记忆层**已记：`current.md`、`index.md`、entry `2026-09-29-cogos-cu-boundary-and-line.md`（含"父子已执行"）。
- **约束**：讨论型——**不写码**；方向由讨论定、执行另启。

## 锚（必读，按序）

1. `projects/cogos/entries/2026-09-29-cogos-cu-boundary-and-line.md`（本会话结论）
2. `projects/cogos/entries/2026-09-28-cogos-intent-view.md` · `...-intent-execution.md`（意图口径；目的＝注意力减负）
3. `projects/cogos/checkpoint/26-09-26-theory-residual/checkpoint-1.md` §四~§七（动手纪律／现状摸底／外圈零件序）
4. `projects/cogos/checkpoint/26-09-26-theory-residual/design-cogos-loop-invariants.md` §二（环的形态：一弧多 cu）
5. 本体 `../cogos/docs/design-selfdrive-agent.md`（唯一权威）
