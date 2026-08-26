# checkpoint-8 — 动手前调研：业界现状 + 重定向调研方案

## 当前问题

定 D1 前，YZ 提出先看业界现状（AI 训练记忆不能反映 2026 最新情况），不要马上动手。

## 已做

- 网络：google/ddg 被墙、代理不可用，arxiv 可达，改用 arxiv API 扫 2026-04~08 论文。
- 产出 `research-1.md`（业界现状 + 映射 + 教训 + 重定向方案）。

## 关键结论

1. 我们的设计已被业界密集研究，三篇高度吻合：GWA（全局工作空间+熵驱动内源节律+双层记忆）、Structural Tension（结构张力+Offline Recurrent Loop）、EMBER（SNN 自发触发行动）。
2. 方向前沿但"原创性"不是价值点，差异需另找。
3. 主流：self-evolving agent（改 harness 不改权重）+ 记忆分层（Letta 领先）+ 安全治理（记忆中毒最大风险）。
4. 关键教训：能力污染（技能池超临界后降性能、不可逆）→ 记忆需门槛/验证；harness scaling（不改权重靠执行系统）→ 支持 D1 最小闭环路线。

## 重定向调研方案（替代 AI 之前过时四方向）

1. 精读 GWA / Structural Tension / EMBER。
2. 专题 A：self-evolving 技术栈（技能/记忆 + harness）。
3. 专题 B：记忆安全 / 能力污染。

## 下一步

整理完 /undo 释放上下文，基于 research-1.md 继续讨论（重点：我们的差异在哪 + D1 边界）。
