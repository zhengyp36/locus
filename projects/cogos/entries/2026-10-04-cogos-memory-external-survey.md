# cogos：记忆模型外部调研（10-04）

> 性质：**记忆模型的外部调研收口件**——为 v1.2 做的"跳出框架"宽扫（AI agent memory）＋神经/认知侧，含 3 篇精读。**不改变记忆模型结论**，提供**对应物 / 共同空白 / 好处地图**。
> 细节与来源：`checkpoint/26-10-04-memory-survey/`（`LANDSCAPE.md` ＋3 篇 `paper-*.md`＋来源总表）。
> 承：`2026-10-03-cogos-memory-{model,projection-unity,index-consolidation}.md`。术语权威＝`glossary.md`。写法：结论＋why＋被否。

## 0. 一句话

我方记忆模型的关键切分在 **AI 与神经/认知两侧都有对应物**（非臆造）；**双方都没解决"结构/维度怎么自动长出来"**——与我方承重缺口 **B** 重合，既是机会也是难度警告。本次确立**好处导向**的阅读纪律。

## 1. 对应关系（我方 ↔ 外部）

| 我方 | 外部对应物 |
|---|---|
| 索引/入口、不扫描 | hippocampal index（海马不存内容，生成 index 绑定皮层活动，回忆＝重激活） |
| 经历层 / 经验层 | episodic / semantic（Tulving；近年认为非截然二分） |
| 时间尺度分离、倾向慢更新 | CLS：海马快/皮层慢 ＋ replay |
| 重投（不矛盾精化） | reconsolidation（**但由 prediction error 门控**） |
| 离线整理 / 点→轴升格 | consolidation ＋ schema（schema＝superordinate 共同要素） |
| 维度 / 轴 | cognitive map / conceptual space（Gärdenfors quality dimensions；**可由聚类涌现**） |
| 动机＝坐标系权重/相关度 | value-based orienting、motivational relevance |
| 检索＝结构粗筛→模型语义判 | MRAgent"重建非检索"（active reconstruction；tags 作语义中介、选路在取内容前） |

## 2. 共同空白（最重要）

- **结构/维度如何自动长出来**（consolidation/schema 自动发生）：AI 侧停在**固定 schema ＋ 向量索引 ＋ 人工 memory 类型**；认知侧有机制线索（**聚类涌现**——无结构穷尽采样下 place/grid 是通用概念学习系统的极限特例，Nature Comms 2019）但未工程化。
- **relevance ≠ similarity**：AI 侧检索瓶颈从"存储"移到"相关性"。
- episodic→semantic 的 **transition policy** 被其综述点名为最欠发达一环。
- ⇒ 与我方 **B（维度/锚空间）** 及"维度应涌现、非先验"方向重合。

## 3. 好处导向回映射（阅读纪律 ＋ 结论）

- 纪律（YZ 定）：**做法 / 目的(理解) / 好处·优势(取舍依据)** 三件分开；**取舍看好处、不看目的**（好处常超出作者自陈目的）；丢弃只在"这好处我们不要"时；反向用法＝先列"我们想要的好处清单"再找。
- **神经侧 E1–E4＝正好是我们缺的好处**（不靠形式相似成立）：
  - **E1 sleep/offline replay**：**定性重组表征** → 规律/抽象/泛化/新组合(insight)。缺（＝离线投影的产出结构）。
  - **E2 schema**：**有结构则新经验一次同化**、加速巩固。缺（＝派生轴/经验层）。
  - **E3 cognitive/conceptual map**：**低维、可比较、可泛化到未见点**、异构同置一空间；**维度可由聚类涌现**。缺（坐标系）。
  - **E4 motivational relevance / value-based orienting**：**自动门控**（无需显式检索）、**价值内化成注意偏置**。缺（动机＝权重场→冲击）。
  - **E5 mood-congruent memory**：用**当前内部状态作检索线索**，内隐；给"主动回忆=内部产生线索"一个形态（是联结通道，非轴）。
- **AI 侧**：多数好处偏**容量/任务效用**（MemGPT 无限长会话、RAG 可扩展）——与我们（结构自长、守得住）不同 → 降**参照/反例**；个别取局部：MRAgent"重建→泛化"、AgeMem"机制固定/策略可学"。

## 4. 可直接借的资产

- 措辞：**write–manage–read** 循环；**representational substrate** 分类（context-resident compression / retrieval-augmented / reflective / hierarchical virtual context / policy-learned / parametric）。
- benchmark：**LoCoMo、MemBench、MemoryAgentBench、MemoryArena**（可作**可证伪判据**灵感）。
- "long context ≠ memory"、"consolidation is fragile & hard to validate"（**外部背书**：这块难）。

## 5. why（为什么这么调研）

- 跳出 cogos 框架、避免自嗨；目标不是"证明我们对"，而是**确认非臆造 ＋ 找缺口 ＋ 找可借好处**。
- 为何看好处不看目的：目的相同不代表能给我们要的好处；好处常是附带/意外的。

## 6. 被否 / 校准

- **按目的或形式相似选型** → 否（看好处）。
- 把 AI 侧当"能力基线/应对齐的对象" → 校准：其好处多为容量/任务效用，降参照/反例。
- （本次未否任何 cogos 既有结论；调研是**支持 ＋ 缺口**。）

## 7. 开放 / 下一步（待 YZ）

- 本次＝把调研**蒸馏进记忆层**（本 entry）。
- 或按"好处清单"继续回映射（E1–E4）。
- **B 的性质**：外部只给方向（聚类涌现 / schema＝共同要素），无工程解；提示 B 或应定义为**维度的产生机制**（离线整理论出的产物），而非先验清单——**kilo 倾向，待议**。
- **候选新缺口**：新关联/新边怎么产生（"连接时间上遥远的事件"，GraphRAG/E10）；我方结构粗筛只沿已有边、难跨远连接——**kilo 提出，待议**。

## 锚

- 细节/来源：`checkpoint/26-10-04-memory-survey/`（LANDSCAPE.md ＋ paper-grid-clustering / paper-memory-reconstructed / paper-human-to-ai-memory）
- 承：`2026-10-03-cogos-memory-{model,projection-unity,index-consolidation}.md`
- 术语：`glossary.md`（好处导向 / 维度涌现）
