# checkpoint-3 — cog-func 范式深化 + 业界定位（讨论）

## 当前问题

locate 方案讨论中引出两个更泛的问题：cog-func 的抽象层次本质（cu/cog-func 同构），以及业界对"组织 LLM 上下文"的现状与趋势定位。

## 关键结论 / 决策

### cu / cog-func 同构

- cu = 一次独立 LLM 推理（原子）；cog-func = 多个 cu 的组合（分子）。
- 删图审视应封装成 cog-func 而非"调一个 cu"：成本 = 多一次函数嵌套（可忽略），换逻辑清晰 + 可复用。

### 编程发展史类比（YZ 提出）

- 机器码 → 汇编 → 面向过程（函数）→ 面向对象（类）。
- LLM 编程对应：裸 prompt（机器码/汇编）→ cog-func 封装（函数阶段，当前所处）→ 未来对象（落点 cog-actor，但应是函数式轻对象——不可变状态 + 行为组合，非 OOP 重对象，因 cogos 哲学是"主体性流动"）。
- 感受：用 cu 封装 cog-func 后，正从 LLM 推理中解放——可确定的沉淀成函数外壳，只有内部不确定点留给 LLM；逻辑变清晰 = 责任边界变清晰（LLM 管理解、机制层管约束）。

### "上螺丝"吃力 → LLM 自组装愿景

- 现状痛点：开发者写死流程（循环/槽/阈值），LLM 只是每个环节的螺丝钉，写起来吃力。
- 愿景：提供适当原语 + 上下文操作能力，把"看图方法"（契约）告诉 LLM，它自己组织流程。
- 四件：原子原语（已有）/ 上下文操作能力（**缺口**，删图已是萌芽）/ 方法论契约（雏形）/ 反馈校准（成长机制）。
- 本质：流程控制权从机制层上移语义层 = 主体性流动。
- 路径：谱系（写死循环 → 给流程骨架 LLM 填策略 → 全交给 LLM），**数据驱动放开**——哪个环节 LLM 反复做错就留机制层兜底，不拍脑袋定。

### 业界调研

- **context engineering**（Anthropic，2024）：prompt engineering 的自然演进，核心 = "最小高信号 token 集"。五技巧：compaction（摘要压缩）/ tool result clearing（工具结果清除，最轻最安全）/ structured note-taking（结构化笔记到上下文外）/ sub-agent architecture（子 agent 独立上下文回摘要）/ just-in-time context（存轻量标识按需加载）。MemGPT/Letta = self-editing memory（LLM 用函数调用自管理内存）。
- **harness engineering**（2025→2026 转向）：Martin Fowler 撰文、arXiv《Code as Agent Harness: Executable, Verifiable, Stateful》、AGENTS.md 成跨工具开放标准、rules files 以 "error not warn" 硬门禁。harness = 包裹 LLM 的控制程序（循环/工具/约束/状态/权限），上下文只是子集。演化链：Prompt Engineering(23-24) → Context → Harness。
- **映射到本方案**：删图/槽改写 = tool result clearing；句柄 = note-taking；cog-func 嵌套 = sub-agent；句柄=path = just-in-time；LLM 决定删图 = MemGPT self-editing memory。
- **我们独特**：业界 harness 聚焦 coding agent 的"可靠性"，cogos 是"认知 harness + 成长维度"，且用"编程抽象层次"视角系统化组织（业界只是技巧清单，无人做此元视角统一）。

## 遗留 / 坑

- 均为方向性认知，无硬结论。LLM 自组装流程的可靠性未验证，需数据驱动渐进放开，勿一步到位。
