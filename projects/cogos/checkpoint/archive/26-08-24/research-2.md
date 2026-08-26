# research-2 — 业界实现层面现状（2026-08）

> 调研目标：回答"理论讨论之外，业界**实现层面**到底是什么情况"。
> 方法：arxiv API（https 直达，200）+ 本地代理 127.0.0.1:10809 抓 GitHub/搜索。
> 三篇核心论文读 HTML 全文，其余 7 篇读摘要。

## 一、三篇核心论文的实现现状（关键对照）

| 论文 | 实现程度 | 技术路线 | 开源 | 代码 |
|---|---|---|---|---|
| **GWA** 2604.08206 | **已实现、可跑** | 纯 LLM 多角色（无权重变化） | 是 | github.com/giansha/Global-Workspace-Agents（Python，18 stars） |
| **EMBER** 2604.12167 | 已实现、N=1 原型 | PyTorch SNN(220K 神经元)+STDP + 可替换 LLM | 否（发表时开） | 未公开 |
| **Structural Tension** 2607.06269 | **纯理论、零实现、零验证** | 理论框架（无代码） | 否 | 无 |

### GWA 实现细节（纯 LLM 角色分工）

- 不是"独立进程 actor"，是**同一个 LLM 多次调用扮演三个角色**：Generator（生成候选思想）→ Critic（评分+批评）→ Meta Agent（元仲裁，选唯一赢家，发 `[RESPONSE]`/`[THINK_MORE]` 标签决定继续想还是回复）。
- 广播机制 = 事件驱动：Global Workspace 状态更新时把信息张量广播给所有节点，每个 agent 持续评估全局状态，相关则处理并提交结构化 proposal。
- 打破初始休眠靠 **Genesis State**（预定义初始化向量，点亮初始 workspace 触发第一个 Perceive 阶段）。
- STM（短期记忆）承接获胜思想；Response Node 把内部表示翻译成自然语言发出。

### EMBER 实现细节（神经动力学路线）

- SNN 220K 神经元（LIF + STDP），四层：sensory(5K) → concept(150K, 可塑联想层) → category(25K) → meta-pattern(10K) + 抑制层(30K) E/I 平衡。
- 文本 → BGE-large(1024-dim) 嵌入 → z-score top-k 群体编码（dimension-independent）。
- **分工明确**：SNN 决定"何时动 + 表面什么关联"；LLM 决定"动什么类型 + 生成内容"。
- 混合记忆三件套：episodic（时间序列重放）+ perfect recall（精确事实不衰减）+ personal journal（自我反思）。
- 硬件：双消费级 GPU（SNN 在 RTX 5070 Ti 16GB，嵌入在 RTX 4060 Ti 8GB）。
- 结果：干净启动后 **7 次对话(14 消息) + 8h 空闲** → 首次 SNN 触发主动联系用户；3 天 52 消息触发 23 次行动(1 reach-out + 22 journal)。有 SNN-disabled 消融对照。
- 局限：**N=1 单用户**，代码未开源，跨模型验证未做。

### Structural Tension 实现现状（重点）

- 明写："**The framework as presented is a theoretical proposal without empirical validation.**" 张力公式未实现、未测试。
- 三机制：Structural Tension（内源损失，新信息 vs 现有 manifold 拓扑冲突）+ Offline Recurrent Loop（离线自处理循环，维持静息电位）+ Inference-time Plasticity（改上下文拓扑、不改权重）。
- 只给了 operational definitions + 算子(Expand/Fold/Trim) + 证伪标准 + worked example；cosine-distance 是几何代理，真正拓扑敏感需 persistent homology/TDA。
- 基于 Structural Intelligence (SI) protocol suite（Kanaria 2025），HuggingFace 有数据集。

## 二、内源驱动的两条实现路线（直接对应我们 cp6 内源节律）

1. **prompt/角色层（轻）**：GWA 熵驱动 + Genesis State。纯 LLM，无新计算层，靠"角色分工 + 广播 + 仲裁标签"造出持续运转。**与我们 cp7 多子系统形态同族，但 GWA 是单 LLM 角色扮演，非独立 actor 进程。**
2. **神经动力学层（重）**：EMBER 用 SNN 静息电位 + 侧向 STDP 传播做真内源动力（背景膜噪声是必要条件，无噪声则空闲期沉默）。重：220K 神经元 + 双 GPU。

→ 我们 cp6 的"内源节律（趋势+阻力）"想走 LLM 侧轻路线，落点接近 GWA 熵驱动，而非 EMBER 的 SNN。

## 三、self-evolving / 记忆分层实现（主流工程栈）

- **Letta**（MemGPT 改版）：stateful agents 平台，记忆 = memory blocks 分层、agent 自管理上下文窗口，**sleep-time compute 在空闲时整理/自改进记忆**。24.4k stars，活跃（源码已迁 letta-ai/letta-code）。是"记忆分层 + 内源整理"的实现代表。
- **StateM** 2608.15089（harness scaling 实证）：不改权重，靠执行系统（durable states + phase-local context + checked transitions + recoverable runbooks + versioned procedural practices）在 Terminal-Bench 2.1 拿到 95.3% raw accuracy / $15 frontier run。→ 支持我们"改 harness 不改模型"的 D1 路线。
- **能力污染 / VaG** 2608.05810：技能池超临界后新增技能反降性能，**结构性不可逆**（污染技能进入决策上下文 → 成为后续蒸馏的参照材料 → 形成跨轮污染链）。解法 = Pre-Commit Gating（提交前门控过滤）。
- **MELD** 2608.16357：分布式 agent 记忆合并协议，五结果判定（insert/merge/relate/conflict/reject），run-time model 是知识图谱本身。
- 其他：OneDayAgent 2608.05013（长程 harness）、Nurture-First 2603.10808（对话知识结晶）、Memory Is Communication 2608.17053（记忆 vs 通信信息预算前沿）。

## 四、对我们的意义

1. **GWA 可直接借力**：纯 LLM、开源、轻量，多角色广播仲裁 ≈ 我们 cp7 形态。但注意它是"单 LLM 角色扮演"，我们 cp7 是"独立 actor + mailbox"，两者形态不同，借的是"广播 + 竞争进入工作空间 + 元仲裁"机制而非其并发实现。
2. **EMBER 印证"内源动力"可实现**，但路线重（SNN+双GPU）且结论弱（N=1）。我们不走 SNN，走 LLM 侧（GWA 熵驱动 + 我们自己的张力/节律）。
3. **Structural Tension 是空壳规格**：业界"张力"论文没有实现、没有验证。我们 cp13 的张力讨论（价值认同 / 朝向未来的自我 / 世界指向）已远超它。这也意味着"张力落地"没有现成实现可抄——印证 cp11 判断"D2 是差异核心却最没把握"。
4. **能力污染是真实坑**：D1 记忆极小不会触发，但记忆子系统将来必须内置 Pre-Commit Gating 类门槛（对应 cp9 已确认 D1 不做门槛）。
5. **harness scaling（StateM）路线成立**：D1 最小闭环 + 不改权重正确。

## 五、索引

- GWA 代码: github.com/giansha/Global-Workspace-Agents
- Letta: github.com/letta-ai/letta（源码 letta-ai/letta-code）
- 论文全文已存: /tmp/kilo/{gwa,st,ember}.txt（临时，不跨会话）
