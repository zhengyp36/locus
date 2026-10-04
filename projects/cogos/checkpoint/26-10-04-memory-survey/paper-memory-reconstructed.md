# Memory is Reconstructed, Not Retrieved: Graph Memory for LLM Agents

- Authors: Yibo Li, Bryan Hooi (NUS)
- URL: https://arxiv.org/html/2606.06036v1
- Code: https://github.com/Ji-shuo/MRAgent

## 1. 一句话结论


MRAgent 把 LLM agent 的记忆访问从"对 query 做一次性 top-k 检索"改为在
**Cue–Tag–Content 异质图**上由 LLM 反复推理、扩张、剪枝的**主动多步"重建"**过程；
tags 是 cue 与 content 之间的关联中介（语义桥），让"选路"发生在"取昂贵内容"之前。

## 2. 做法 / 机制

### 记忆怎么建（LLM 蒸馏，Sec 3.3, Fig 4a）
- 输入流 T 先切成 episodic units `e_i`（一个具体事件）。
- 对每个 `e_i`：`g_i = F_LLM^tag(e_i)`（生成一个短的关联 tag），
  `C_i = F_LLM^cue(e_i)`（抽取细粒度 cues：实体、属性、显著描述符）。
- 每个 cue 通过 tag 连到 `e_i` → Cue–Tag–Episode 关系。Semantic units 同法抽取，
  锚到 entity-level cue，用 aspect-level tag（人格特质、长期偏好、事实属性）。
- Topic nodes：总结相关 episodes 的共同主题，连到其组成 episodes，支持粗粒度推理。
- **构建是"轻量"的**：只做抽取/总结，不做复杂的关系建模。

### 三层记忆（Sec 3.2）
- Episodic Layer (Cue–Tag–Episode)：事件级，沿统一 timeline 组织以支持时序约束。
- Semantic Layer (Cue–Tag–Semantic)：跨事件的稳定知识/事实/偏好。
- Abstraction Layer (Topics)：共享模式的 topic 摘要，支持 top-down `φ_{τ→e}`。

### tags 是什么
- 形式化：图 `M=(C,V,R)`，关系 `R ⊆ C×G×V`，每个 triple `(c,g,v)` 把 cue `c`
  经关系属性 `g`（即 Tag）连到 content `v`。
- Tag = "summarize associative relations between fine-grained cues and content units"。
  它是**关联的显式中间表示**，不是可学习参数，是 LLM 从 episode 摘要出的文本标签。
- 两阶段检索：先选一小批 tag，再在 tag 条件下取 content（decouple 关联推理与内容级取回）：
  - `φ_{c→g}(c) = { g | (c,g,·)∈R }`（cue 激活候选 tags）
  - `φ_{(c,g)→v}(c,g) = { v | (c,g,v)∈R }`（cue+tag 条件下取 content）

### 怎么"重建"而非检索（Sec 4, Fig 4b）
- 定义状态 `S^(t) = (Z^(t), H^(t))`：`Z`=active set（cue/tag/content 候选），
  `H`=已累积的证据上下文，用来 condition 下一步方向。
- 动作空间 A = 由算子诱导的遍历动作：
  - Forward：`Π_{c→g}` 激活 tags，`Π_{(c,g)→v}` 取 content。
  - Reverse：`Π_{v→(c,g)}` 从已取回的 content 反激活新的 cues/tags（重定向轨迹）。
- 迭代循环（Eq 10–12）：
  1. LLM reasoning + action selection：`A^(t)=f_select(x,H^(t),Z^(t))`，选有希望的扩张方向。
  2. Controlled traversal：对选定动作执行算子，得候选集 `Z̃^(t+1)`（非穷举扩张）。
  3. LLM routing + 状态更新：`Z^(t+1)=f_route(x,H^(t),Z̃^(t+1))`（选相关、剪枝），
     `H^(t+1)=H^(t)∪Z^(t+1)`；再由 `C_LLM` 判断证据是否足够，不足则继续。
- 对照定义：passive `π_p(x)` 是一次性函数；active `v^(t)=π_a^(t)(x,S^(t-1))` 是
  stateful、可基于中间证据改策略的序贯决策。

## 3. 目的（作者想解决什么）

长交互历史下 LLM agent 的长期记忆。现有记忆系统是 **passive retrieval policy**，
作者列三大弱点（Sec 2.2）：
1. 无法基于中间状态改策略（例：推理中出现"July"这一时间锚点却无法据此重定向）；
2. 固定聚合（top-k / 预定义 N-hop）累积噪声；
3. 依赖预构建结构，不灵活、难扩展。

由此提两个挑战：**Challenge 1 Active Reconstruction**（把一次性取回变成多步重建）、
**Challenge 2 Associative Memory Structure**（怎么组织记忆以支撑有引导的关联探索）。

## 4. 好处 / 优势（最重要）

- **性能**：LoCoMo J 分 68.31→84.21（Gemini，+23.3% relative），Claude 下 +12.4%；
  LongMemEval 相对最强 baseline +32%。
- **成本**：LongMemEval 每样本 prompt tokens 降到 118k（A-Mem 为 632k），runtime 也降。
  原因：轻量构建 + 把复杂关系建模**推迟到检索期、按 query 特定地做**；on-demand 访问。
- **抗噪 / 抗组合爆炸**：tags 让 agent 在访问昂贵 episodic content **之前**评估并剪掉
  无关分支；避免朴素 n-hop 邻域扩张的 combinatorial explosion 与碎片/无关记忆。
- **可解释 / 可控**：把关联显式暴露，LLM 在 content 级之前就能"选路"。
- **多步重建逐步找回缺失证据**：single-hop/temporal ~3 步近满 recall；
  multi-hop 累计 recall 每步 +30% 以上（Fig 6a）。
- **自主终止**：Max Valid Turns ≈ Average Turns，LLM 自行判断何时继续/停止，减少冗余探索；
  附录显示**加大并行检索预算不能替代重建深度**（Fig 9）。
- **ablation 结论**（Fig 5, multi-hop）：
  - reasoning 是主增益来源：各结构下"带推理"都优于"仅结构"；
  - tags 单调有用：no-reasoning 下 CE < CTE < CTC；
  - episodic 与 semantic 互补：去掉 semantic 明显掉分。
- **理论**：Theorem 4.1 —— 对任意预算 T≥2，passive 假设类严格包含于 active
  （`H_passive(T) ⊊ H_active(T)`）；即 active 检索策略严格更具表达力。
- **附带好处（未重点强调）**：记忆构建反而更简单——把关系依赖的建模负担从构建期
  挪到检索期；无需在构建时做复杂依赖分析/重复总结。

## 5. 关键概念 / 术语

- **Active memory reconstruction**：把 LLM 推理直接嵌入记忆访问，基于累积证据迭代
  探索并剪枝的重建式访问。
- **Passive / stateless retrieval**：仅由 query 决定一次性取回（top-k、预定义子图遍历）。
- **Cue–Tag–Content (CTC) graph**：cue 为细粒度关键词；content 为记忆项；
  tag 为二者间类型化关联的中介。
- **Tag**：summarize 关联关系的短标签，充当语义桥与剪枝依据。
- **Cue**：实体 / 属性 / 上下文的细粒度关键词。
- **Reconstruction state** `S=(Z,H)`：active set + reconstructed context。
- **Forward / Reverse traversal**：沿 Cue–Tag–Content 扩张；从 content 反激活 cue/tag。
- **f_select / f_route**：LLM 的动作选择函数 / 路由剪枝函数。
- **Two-stage retrieval**：先选 tag 再按 tag 取 content。
- **Engram**（引神经科学）：由过往经验形成的紧凑内部记忆状态，其激活会偏置并约束
  后续回忆，逐步"重建"连贯记忆。
- **Episodic / Semantic / Topic abstraction**：事件 / 稳定知识 / 跨事件模式三层。

## 6. 意外点 / 反直觉的地方

- 标题"reconstructed, not retrieved"很强，但系统本质仍是**结构化检索 + agentic 循环**；
  与 agentic RAG 的差别在于检索对象是"agent 自身持久交互历史"而非外部语料库。
- 作者反而强调**构建更简单**：把复杂度整体搬到检索期——这是双刃剑（见局限）。
- 神经科学动机（engram/reactivation/序贯回忆）是**功能对应**（Fig 3），不是机制还原；
  tags 是 LLM 生成的文本摘要，不是学出来的关联结构。
- Theorem 4.1 是假设类包含关系（表达力存在性），**不保证**当前 LLM 策略能达到该上界。
- 时序推理靠"episodic 沿统一 timeline 组织 + 中间推断时间锚点"，而非显式时间图。

## 7. 原文锚

- URL: https://arxiv.org/html/2606.06036v1
- Abstract；Sec 1（Fig 1 passive vs active；Fig 2 三个例子 a/b/c）
- Sec 2.1 形式化（Eq 1–2）；Sec 2.2 三大弱点；Sec 2.3 认知动机（Fig 3）
- Sec 3（Fig 4 框架）；Sec 3.1 定义（Eq 5 两算子）；Sec 3.2 三层；Sec 3.3 构建（Eq 6）
- Sec 4.1 状态与动作（Eq 7–9）；Sec 4.2 重建循环（Eq 10–12）；Sec 4.3 Thm 4.1
- Sec 5: Table 1（LoCoMo）、Table 2（LongMemEval）、Table 3（成本）、
  Fig 5（ablation）、Fig 6（multi-turn）、Fig 7（case study）
- Sec 6 Related Work；Sec 7 Conclusion & Discussion（局限）
- Appendix: A（passive 分析）、B.1/B.2（实现）、C（证明）、D（实验细节）、Fig 9（预算）

## 8. 局限 / 未解决

- **重建成本随探索深度增长**：需要很多遍历步的 query 延迟高于单次检索。
- **静态构建、无更新/遗忘/巩固**：图随交互单调增长，长期部署存储开销上升。
- 作者明确把以上两点列为 future work：adaptive construction、lightweight memory
  maintenance、更鲁棒的 traversal policy。
- 未深入讨论：tag/cue/topic 抽取质量对结果的敏感性；错误 tag 的传播。
- Topic 生成与连接的细节在附录，主文较略。
- 评测限于 LoCoMo / LongMemEval；未展示 long-lived 部署与持续更新场景。
