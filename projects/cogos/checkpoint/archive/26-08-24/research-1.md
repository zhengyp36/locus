# research-1 — 业界现状调研（2026-08）

## 调研背景

目标收敛后、动手前，先看业界现状。搜索引擎（google/ddg）被墙、代理不可用，改用 arxiv API 扫 2026-04~08 最新论文（cs.AI / cs.MA / cs.CL）。

## 关键发现：我们的设计已被业界密集研究

三篇高度吻合的论文（方向被验证，但"原创性"不是我们的价值点）：

1. **GWA**（2604.08206，Theater of Mind）：全局工作空间理论直接落成 LLM 架构——中心广播 hub + 功能受限 agent 群 + 熵驱动内源驱动力（破死锁）+ 双层记忆分叉（长期连续性）。≈ 我们的"全局工作空间 + 内源节律 + 记忆分层"。
2. **Structural Tension**（2607.06269）：结构张力（新信息与现有拓扑冲突的内源损失）+ Offline Recurrent Loop（无外部输入时维持静息电位、消化冲突）+ Inference-time Plasticity。≈ 我们的"张力 + 内源节律持续运转"。
3. **EMBER**（2604.12167）：SNN 在空闲期自发触发 LLM 行动，8 小时空闲后自发联系用户。≈ 我们的"自主性"。

## 主流趋势（2026）

- **self-evolving agent 是最热方向**：从轨迹提取技能/记忆，持续更新 harness，不改模型权重。
- 记忆管理已从 RAG 进化到"技能/经验/记忆分层"，Letta 为代表（FinEvo-Bench 中最高分）。
- 安全治理是主要关切：memory poisoning、sleeper agent、Chronos Vulnerability（时间持久性 + 记忆欺骗）。

## 关键教训（直接影响 D1）

- **能力污染**（2608.05810，When Self-Evolution Backfires）：技能池超过临界大小后，新增技能反而降性能，且结构性不可逆 → 记忆不是越多越好，需内置门槛/验证（VaG 三评论家过滤）。
- **harness scaling**（StateM 2608.15089）：不改权重，靠执行系统（durable states + runbook + 校验转换）大幅提升长期表现 → 支持 D1 最小闭环路线。

## 对我们的意义

1. 方向前沿但已被密集研究，差异需另找（见下一步讨论）。
2. D1"改 harness 不改模型"路线正确。
3. 记忆子系统必须内置门槛/验证，否则踩能力污染坑。

## 下一步调研方案（重定向，替代过时四方向）

- 精读 GWA、Structural Tension、EMBER 三篇：看做到什么程度、可借鉴点、我们的差异。
- 专题 A：self-evolving 技术栈（技能/记忆管理 + harness 设计）。
- 专题 B：记忆安全 / 能力污染（D1 必避的坑）。

## 论文索引（锚点，供后续精读）

- GWA: 2604.08206
- Structural Tension: 2607.06269
- EMBER: 2604.12167
- MELD（分布式记忆合并协议）: 2608.16357
- 能力污染 / VaG: 2608.05810
- StateM（harness scaling）: 2608.15089
- Self-Improving Agents Survey: 2607.13104
- Nurture-First（对话知识结晶）: 2603.10808
- OneDayAgent（长程 harness）: 2608.05013
- Memory Is Communication: 2608.17053
