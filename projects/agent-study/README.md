# agent-study

agent 设计的学习/理论工程。locus 存其索引与工程印象，本体不物理移动。

- remote: https://github.com/zhengyp36/agent-study
- 本体路径: `../agent-study`
- 性质: 知识库工程（本体即内容），非代码工程——locus 对它是「索引指针」而非「复制内容」，防双写。

## 本体结构锚点（`../agent-study/agent-study/`）

- `AGENTS.md` — 工作区规则 + 学习方式（区分智能决策层 / 执行运行层 / 产品系统层）
- `index.md` — 防丢记录索引（含协作方法论讨论的单元文件与问题清单）
- `00-meta/` — 学习方法、分类规则、样本研究方法、locus 迁移记录
- `01-recovery/` — 当前焦点 + 会话恢复点（`current-focus.md` / `current-session-recovery.md`）
- `02-concepts/` — 跨框架通用 agent 设计概念（约 50 个文件：认知树、决策层、语义视界、意识流等）
- `03-maps/` — 结构/模式图（`agent-architecture-layers.md` / `decision-layer-learning-path.md`）
- `04-samples/` — 具体框架样本研究（codex / langgraph / smolagents / openhands / autogen / openclaw / cc-connect / pi）
- `05-experiments/` — 最小实验（minimal-react-loop / planner-executor-replanner / multi-agent-supervisor / tool-runtime-sandbox / toy-self-learning-agent / external-distributed-agent-state）
- `06-comparisons/` — 样本对照（`runtime-vs-decision-layer.md` / `cogos-vs-industry.md` / `agent-landscape-2026-06.md` 等）
- `07-detailed-notes/` — 历史归档，默认不优先读
- `agi-core/` — 旧 agent 内核实现（agi_body / feishu / lm_call / comm 等）
- `cogos/` — cogos 前身工程（含旧设计文档 `comm/`）

## 关键入口

- 学习工作流: `00-meta/learning-workflow.md`
- 当前焦点: `01-recovery/current-focus.md`
- 会话恢复: `01-recovery/current-session-recovery.md`

## 历史

- 前身是「先学 agent 后开发 agent」，cogos 是其中「开发 agent」的落点（已独立为外部工程）。
- 08-13 曾声明「locus 自身机制待修，暂不记入 locus」，08-24 起转向纳入 locus 索引。
