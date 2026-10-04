# 宽扫地形图 v1（2026-10-04）

> 长任务入口。目标：跳出 cogos 框架，先看 AI/神经侧**别人自己怎么设问题、怎么命名**，再看能否启发我们。
> 纪律：A/B 两节用**领域原生词**（不带 cogos 术语）；C 节才是我方对照，明标"我的读法"。
> 代理偶发断连，检索为单发+重试；此版为宽扫 v1，未穷尽。

## 阅读纪律（10-04 更新，YZ 定）
- 三件事分开：**做法 / 目的（理解用）/ 好处·优势（取舍依据）**。
- **取舍看好处，不看目的**；好处常超出作者自陈目的（附带/意外），要主动找最强好处。
- 卡片：`做法 ｜ 目的 ｜ 好处·优势 ｜ 我们缺不缺 ｜ 形式能否借`；**丢弃只在"这好处我们不要"时**。
- 反向用法：先列"我们想要的好处清单"，再去外部找"谁能给、怎么给"。

## A. AI 侧（LLM agent memory）

### A0. 领域自己设定的问题
- 主流形式化：memory = **write–manage–read loop**，嵌在 POMDP 式 agent 循环里（M_t≈belief state / 交互历史的 sufficient statistic）。（arXiv 2603.07670）
- 三条正交轴：**temporal scope / representational substrate / control policy**。

### A1. 时间/功能类型（他们分层的默认）
working memory / episodic / semantic / procedural。过渡（episodic→semantic 的 "transition policy"）被点名为**最欠发达**的一环。

### A2. 机制家族（6）
1. context-resident compression（滑动窗/滚动摘要/分层摘要/任务条件压缩）
2. retrieval-augmented stores（RAG、dense retrieval、多粒度索引、query reformulation）
3. reflective self-improvement（Reflexion、Generative Agents reflection、ExpeL）
4. hierarchical virtual context（MemGPT 三级：main/recall/archival）
5. policy-learned management（AgeMem：store/retrieve/update/summarize/discard 当工具，RL 训）
6. parametric memory（fine-tune/adapter）

### A3. 代表系统 / 数据
- 系统：Memory Networks/NTM/DNC（早期）、ReAct、Reflexion、**Generative Agents**（observation–reflection–planning；recency+relevance+importance 打分）、**Voyager**（skill library）、**MemGPT/Letta**、RET-LLM、Think-in-Memory、JARVIS-1、**H-MEM**（按语义抽象度分层）、Mem0、Zep、Cognee、Agentic Memory(AgeMem)、CLS-ER（continual learning，借 CLS）。
- 基准：**LoCoMo**、**MemBench**、**MemoryAgentBench**、**MemoryArena**。结论：long context ≠ memory；RAG 有用但瓶颈是 retrieval relevance；selective forgetting 无人做好；cross-session coherence 基本未解。

### A4. 他们公认的 open problems（原文）
continual consolidation · causally grounded retrieval · trustworthy reflection · learned forgetting · multimodal embodied memory。另：self-reinforcing error（错误反思固化）、schema drift（工具接口变）、parametric vs non-parametric 的失败画像不同。

### A5. 明确缺口（对我们重要）
- **consolidation 弱**：episodic→semantic 多靠人工规则/定期 LLM 摘要，"fragile & hard to validate"。
- **relevance ≠ similarity**：检索瓶颈从存储移到相关性。
- 表示基质多为**固定 schema / 向量索引**；"概念结构自己长出来"罕见。

### A6. 综述清单（备查）
- 2603.07670 Memory for Autonomous LLM Agents（write–manage–read，3 轴，最系统）
- 2404.13501 A Survey on the Memory Mechanism of LLM-based Agents（ACM TOIS，奠基）
- 2504.15965 From Human Memory to AI Memory（人→AI 映射）
- 2602.06052 A Survey of Agent Memory in the Second Half（self-evolving / long-horizon）
- 2602.19320 Anatomy of Agentic Memory（taxonomy + 实证）
- 2507.21046 A Survey of Self-Evolving Agents
- 202601.0618 From Storage to Experience（taxonomy by 轨迹利用度）
- 2603.0359 LLM Agent Memory: Unified Representation–Management
- Shichun-Liu/Agent-Memory-Paper-List（"Memory in the Age of AI Agents"）

### A7. 图谱/结构记忆（补漏）
- **Graph-based Agent Memory: Taxonomy**（arXiv 2602.05665）：把孤立轨迹连成 knowledge web；LLM 做 **latent link prediction** 连接时间上遥远的事件（"associative thinking, connect the dots"）。
- **GraphRAG / 社区摘要**（Microsoft）：把语料聚成 thematic communities、LLM 预生成社区摘要，查询走 map-reduce。
- **MRAgent / "Memory is Reconstructed, Not Retrieved"**（arXiv 2606.06036）：主张记忆是**重建**而非检索；**tags＝中间联想结构**，编码 cue↔content 的连接并引导重建；episodic/semantic 二分。
- **CoALA**（Sumers et al. 2309.02427）：认知架构 for language agents，把 substrate/retrieval/control 显式分层。
- 相关："On the structural memory of LLM agents"(2024)、"AI Meets Brain: Memory Systems from Cognitive Neuroscience to Autonomous Agents"(2025)。

## B. 神经/认知侧

### B1. 记忆系统划分
- episodic vs semantic（Tulving, 1972）；procedural；working。边界近年被质疑（episodic–semantic 非截然二分）。

### B2. Complementary Learning Systems（CLS）
- 海马＝**快、实例式/模式分离**；新皮层＝**慢、结构化/提取统计规律**。靠 **replay/interleaving** 巩固 → 习得结构（generalization）而非死记。
- 直系含义：**快慢两套 + 时间尺度分离**；离线重放把 fast 的个别经验变成 slow 的结构。（McClelland/McNaughton/O'Reilly 1995；Nature Neuro 2023 "Organizing memories for generalization in CLS"）

### B3. Hippocampal indexing theory
- 海马**不存内容本身**，生成 **index** 绑定当次分布式皮层活动 → 快速建**片段记忆**；回忆＝用 index 重激活皮层模式（context reinstatement）。（Teyler & DiScenna/Rudy；Nature Human Behaviour 2023 "Hippocampal neurons code individual episodic memories"；Neuron 2020 "An Integrated Index: Engrams, Place Cells, and Hippocampal Memory"）

### B4. Schema
- schema＝**superordinate knowledge structures：abstracted commonalities across experiences**（Tse 2007, Science；Gilboa & Marlatte 2017）。
- 有 schema 时，新信息**一 trial 同化**并快速脱离海马；vmPFC 临时绑定 schema、按情境门控相关联想。

### B5. Cognitive map / conceptual space（**和"维度"最相关**）
- 海马映射不限于空间：**social space** 由 power/affiliation 两维编码（Tavares 2015, Neuron）；"cognitive map reaches beyond navigation to social relationships, temporal order, abstract conceptual space"（Epstein/Spiers 2017）。
- **grid cells / place cells 用于抽象概念维度**；"Organizing Conceptual Knowledge in Humans with a Grid-like Code"（Constantinescu/Behrens 2016）。
- **Nature Comms 2019 "A non-spatial account of place and grid cells based on clustering models of concept learning"**：place/grid 与高维概念表示都能由一个**通用聚类算法**产生 → **维度/地图是从聚类学习涌现的**，非先验空间。

### B6. Reconsolidation & prediction error
- 记忆被**召回即变可塑**；**prediction error / incomplete reminder** 决定是否更新、如何更新（Nature Neuro/PNAS 多篇）。→ "更新（重写）在回忆时发生，且由预测误差门控"。

### B7. Value / motivation
- **motivational relevance prioritizes memory**（reward value 门控编码与巩固）；dopamine RPE；**value-based attentional orienting**（奖励线索自动夺注意）。→ "动机/价值=什么被注意、被记住、被优先取回"的偏置。

### B8. Conceptual spaces（Gärdenfors）——**维度的形式化**
- 概念空间＝几何结构：**点＝对象，区域＝概念**；由若干 **quality dimensions** 张成；**距离＝语义相似度**。
- 与 B5 的"聚类涌现"互为表里：空间本身可由相似度/混淆矩阵做**维度约减**构造。

### B9. Sleep / offline replay
- 睡眠期**神经元重激活**把新经历在 hippocampal-cortical 系统里**重组**；consolidation 不止"强化"，而是**定性重组**（可能产生 insight）。
- replay＝**context-driven 记忆重激活**（eLife 综述）。

### B10. Emotion / mood（阴雨那条）
- **Mood-congruent memory**：当下情绪使**同调材料**更易被回忆，可发生于**内隐**（depressed 组优先内隐回忆负性信息）。
- Bower 联想网络：**情绪节点被 priming**，扩散到"generalized representation"（未必是具体自传事件）。→ "情境→情绪→泛化回忆"的联结链。

### B11. 待补（仍未扫）
development（维度如何随发育出现）；Gärdenfors 与 grid-cell 聚类的合流；embodiment。

## D. 发展脉络 / 时效（"这是最新吗"）
- **2014–2016**：Memory Networks / NTM / DNC（外部可微记忆，QA 用）。
- **2020–2022**：RAG、RETRO（检索进生成）；ReAct（推理↔行动，轨迹兼记忆）。
- **2023**：Reflexion（文字自我批判）、**Generative Agents**（observation–reflection–planning）、Voyager（skill library）。
- **2024**：**MemGPT**（OS 式虚拟内存）、CoALA、SQL/symbolic memory。
- **2025–2026（当下主战场）**：三件事——① **self-evolving agents**（综述 2507.21046）；② **learned memory control**（AgeMem 用 RL 训 store/retrieve/update/summarize/discard）；③ **agentic benchmarks**（MemoryArena 等，把记忆与行动耦合）。
- **演进主线**：storage（存）→ reflection（反思）→ **experience（经验/自演化）**（"From Storage to Experience" 2601.0618）；评价从 recall → **agentic utility**；架构从 RAG → 层级虚拟内存 → **图结构/重建** → RL 控制。
- **时效判断**：本版扫到的工作多为 2025–2026，含 2026-03/05/06 的综述与论文，**是当前最新**；该领域正处于快速爆发期（"hundreds of papers in 2025"）。

## C. 我的读法（对照 cogos，**非结论；刻意后置**）

| cogos | 领域对应物 |
|---|---|
| 索引/入口、不扫描 | hippocampal index |
| 经历层 / 经验层 | episodic / semantic |
| 时间尺度分离、倾向慢更新 | CLS 快慢 |
| 重投（不矛盾精化） | reconsolidation（但有预测误差门控） |
| 离线整理 / 点→轴升格 | consolidation + schema（superordinate = 共同要素） |
| 维度/轴 | cognitive/conceptual space；**可由聚类涌现**（B5） |
| 动机=坐标系权重/相关度 | value-based orienting、motivational relevance |

- **重叠**：我们独立收敛到的切分（索引、两系统、巩固、重投、维度空间、动机门控）在两侧都有对应物 → 至少不是臆造。
- **他们也没解决**：consolidation/schema 怎么**自动**发生（AI 侧靠 heuristic/prompt；认知侧有机制假设但不可直接搬）。
- **可能的空白/位置**：AI 侧基本停在**固定 schema + 向量索引 + 人工 memory 类型**；"维度自己长出来"只有认知侧的非空间聚类账户，AI 侧几乎没人做 → 与 cogos 的"派生轴/点→轴升格"方向重合，且是缺口。
- **可直接借的资产**：write–manage–read 循环措辞；representational substrate 分类；4 个 benchmark（可当可证伪判据灵感）；"relevance ≠ similarity"；"consolidation 是欠发达一环"作为外部背书。

## E. 好处导向回映射 v1（10-04，按阅读纪律重做）
> 卡片：做法 ｜ 目的（理解） ｜ **好处·优势（取舍）** ｜ 我们缺不缺 ｜ 形式能否借。
> 丢弃只在"这好处我们不要"时。

### 神经/认知侧

**E1. Sleep / offline replay**
- 做法：睡眠期重激活新经历、跨系统重组。
- 目的：巩固、防遗忘、系统转移。
- **好处**：**定性重组表征** → 提取规律、抽象细节、**泛化**、可能生成新组合（insight）。
- 我们缺否：**缺**（= 点→轴升格 / 新结构）。
- 借否：借"离线投影"，但关键在**产出结构这一好处**，不是"定期跑"这个形式。

**E2. Schema**
- 做法：由经历的共同要素抽象出 superordinate 结构；有它则新信息快速同化。
- 目的：高效吸收新信息、系统巩固。
- **好处**：**有结构后，新经验一次就位/同化**；**加速巩固**；泛化。
- 我们缺否：**缺**（= 派生轴 / 经验层）。
- 借否：借"共同要素固化成品"以及"有轴则新点一次归位"的好处。

**E3. Cognitive map / conceptual space（含 grid cells、Gärdenfors）**
- 做法：把环境/关系编码成低维 quality 维度上的地图；维度可由聚类/相似度涌现。
- 目的：导航（空间 → 抽象）。
- **好处**：**低维、可比较、可泛化到未见点**（支持在新组合上仍能推断）；**异构信息同置一空间**。
- 我们缺否：**缺**（坐标系/维度）。
- 借否：借"维度化带来的可比较+可泛化+可重建"，以及"维度**从聚类涌现**"这条（对上点→轴升格）。

**E4. Motivational relevance / value-based orienting**
- 做法：reward value / dopamine 调制注意、编码、优先取回。
- 目的：为达成目标优先处理有用信息。
- **好处**：**自动门控**（不需显式检索）；**价值内化成注意偏置**（不依赖当下奖励）。
- 我们缺否：**缺**（动机=权重/相关度→冲击）。
- 借否：正对"倾向=坐标系权重场"；借其"内化偏置"这条。

**E5. Mood-congruent memory**
- 做法：当下情绪 priming 同调材料，可内隐。
- 目的：情绪一致性。
- **好处**：**用当前内部状态作检索线索**（无需外境线索）；内隐、非言语。
- 我们缺否：**部分缺**（"内部产生线索"我们有，"情绪态门控"没有）。
- 借否：给"主动回忆=内部产生线索"一个具体形态；但它是**联结通道**，非轴。

### AI 侧（用好处看，结论变了不少）

**E6. RAG / 向量库**：好处＝可扩展到海量 + 模糊命中；**我们只要"模糊命中"，不要"外包给几何空间"**。
**E7. MemGPT 层级虚拟内存**：好处＝无限长会话/预算可控（是**容量**好处，非结构好处）→ 参照换页，不作主轴。
**E8. AgeMem（RL 学记忆管理）**：好处＝**学出非显然策略**（未满先摘要）、策略自适应；但目的（任务效用）与我们（自驱/自我）不同 → 可参考"机制固定、策略可学"，不照搬 RL 端到端。
**E9. MRAgent《记忆是重建非检索》**：好处＝**重建带来泛化**（非原样取回）、tags 作联想中介 → 与我们"索引=投影/单值视图"很近，可借"重建"。
**E10. GraphRAG / graph memory**：好处＝**连接时间上遥远的事件**（connect the dots）、全局主题摘要 → 我们否的是"机械抽取关联"，但"连接遥远事件"这个好处要想办法拿到。

### E 的结论
- 用"好处"看，神经侧几条（E1–E4）**好处正是我们所缺**，且**不靠形式相似**成立 → 应重点吃。
- AI 侧多数**好处偏"容量/任务效用"**，与我们要的（结构自长、守得住）不同 → 作工程参照/反例即可，个别（E8/E9）取局部好处。

## 下一步（待 YZ 定）
- 调研已收口（本目录）；结论**未入记忆层**。
- 收口进记忆层（entries）：把关键结论+why+被否 蒸馏成 entry。
- 或按"好处清单"继续回映射。

## F. 来源总表（可重读）
> 全部 URL，供回看原文。精读件见 `paper-*.md`。

### AI 侧 · 综述
- Memory for Autonomous LLM Agents（write–manage–read，3 轴）— https://arxiv.org/html/2603.07670v1
- A Survey on the Memory Mechanism of LLM-based Agents（ACM TOIS）— https://arxiv.org/abs/2404.13501
- From Human Memory to AI Memory — https://arxiv.org/html/2504.15965v2
- A Survey of Agent Memory in the Second Half — https://arxiv.org/abs/2602.06052
- Anatomy of Agentic Memory — https://arxiv.org/html/2602.19320v1
- A Survey of Self-Evolving Agents — https://arxiv.org/html/2507.21046v4
- From Storage to Experience（preprints）— https://www.preprints.org/manuscript/202601.0618
- LLM Agent Memory: Unified Representation–Management — https://www.preprints.org/manuscript/202603.0359
- A Survey on the Evolution of LLM Agent Memory — https://arxiv.org/pdf/2605.06716
- Agent-Memory-Paper-List（GitHub）— https://github.com/Shichun-Liu/Agent-Memory-Paper-List

### AI 侧 · 图谱/重建/架构
- Graph-based Agent Memory: Taxonomy — https://arxiv.org/html/2602.05665v1
- Memory is Reconstructed, Not Retrieved（MRAgent）— https://arxiv.org/html/2606.06036v1（code https://github.com/Ji-shuo/MRAgent）
- CoALA — https://arxiv.org/abs/2309.02427
- Anthropic context engineering — https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Weaviate context engineering — https://weaviate.io/blog/context-engineering
- LangChain context engineering — https://www.langchain.com/blog/context-engineering-for-agents
- Zylos：AI Agent Memory Architectures — https://zylos.ai/research/2026-04-05-ai-agent-memory-architectures-persistent-knowledge/

### 神经/认知侧
- Hippocampal indexing theory（Teyler & Rudy）— http://people.whitman.edu/~herbrawt/hippocampus.pdf · https://pubmed.ncbi.nlm.nih.gov/17696170/
- Hippocampal neurons code individual episodic memories（Nat Hum Behav 2023）— https://www.nature.com/articles/s41562-023-01706-6
- An Integrated Index: Engrams, Place Cells（Neuron 2020）— https://www.sciencedirect.com/science/article/pii/S0896627320305286
- CLS（McClelland/McNaughton/O'Reilly 1995）— https://stanford.edu/~jlmcc/papers/McCMcNaughtonOReilly95.pdf
- Organizing memories for generalization in CLS（Nat Neuro 2023）— https://www.nature.com/articles/s41593-023-01382-9
- Schemas and memory consolidation（Tse 2007, Science）— https://www.science.org/doi/10.1126/science.1135935 · https://pubmed.ncbi.nlm.nih.gov/17412951/
- Neurobiology of Schemas（Gilboa & Marlatte 2017）— https://people.sissa.it/~ale/EvolNeurComp/2022/assessment2022/C_GilboaMarlatte-2017-NeurobiologyofSchemasandSchema-MediatedMemory.pdf
- Hippocampus as cognitive map of social space（Tavares 2015）— https://www.sciencedirect.com/science/article/pii/S0896627315005267
- The cognitive map in humans（Epstein/Spiers 2017）— https://www.psych.upenn.edu/epsteinlab/pdfs/EpsteinPataiJulianSpiersNN2017.pdf
- Grid Cells for Conceptual Spaces? — https://www.sciencedirect.com/science/article/pii/S0896627316307073
- Organizing Conceptual Knowledge with a Grid-like Code（2016）— https://pmc.ncbi.nlm.nih.gov/articles/PMC5248972/
- A non-spatial account of place and grid cells（Nat Comms 2019）— https://www.nature.com/articles/s41467-019-13760-8
- Conceptual Spaces（Gärdenfors）— https://mitpress.mit.edu/9780262572194/conceptual-spaces/ · https://en.wikipedia.org/wiki/Conceptual_space
- Sleep—A brain-state serving systems memory consolidation（Neuron 2023）— https://www.cell.com/neuron/fulltext/S0896-6273(23)00201-5
- To Replay, Perchance to Consolidate（PLOS Biol）— https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.1002285
- Prediction Error and Memory Reactivation（reconsolidation）— https://pubmed.ncbi.nlm.nih.gov/31506189/
- Prediction errors disrupt hippocampal representations（PNAS）— https://www.pnas.org/doi/10.1073/pnas.2117625118
- Mood-Congruent Memory Revisited — https://pmc.ncbi.nlm.nih.gov/articles/PMC10076454/
- Mood-congruent implicit memory（meta-analysis）— https://pubmed.ncbi.nlm.nih.gov/24980699/
- Value-based attentional orienting（dopamine）— https://pmc.ncbi.nlm.nih.gov/articles/PMC4767677/
- Influence of reward motivation on human declarative memory — https://www.sciencedirect.com/science/article/abs/pii/S0149763415003024
- Dopamine does double duty in motivating cognitive effort — https://pmc.ncbi.nlm.nih.gov/articles/PMC4759499/
- Interdependence of episodic and semantic memory — https://pmc.ncbi.nlm.nih.gov/articles/PMC2952732/
- Rethinking the episodic/semantic distinction — https://link.springer.com/article/10.3758/s13421-022-01299-x
