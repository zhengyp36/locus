# ISSUES

遗留问题（未解决/未闭合的欠账）。

## 过度思考（思考过长 / token）

- 现象：思考只展开不压缩、反复自我怀疑多路推演、工具选错、事实/推断混层、任务当开放调查。
- 根因：缺收敛机制（风格层 + 机制层：自回归无"简洁"代价函数、无"已结论即停止"信号）；深层=缺"执行/调节层"。
- 修法方向：硬约束治本（决策模板、subagent 隔离、grep 缩小生成空间）。
- 状态：有结论，未完全闭合——"收敛的本质（什么时候该停）"未拆到底。
- 来源：git tag locus-original `entries/2026-08-13-methodology-thinking-length.md`；agent-study A1。

## 重复性工作（无法复用）

- 现象：无法复用已做过的事，每次像第一次。
- 状态：仅一句话，未展开"复用什么、怎么复用"。
- 来源：git tag locus-original `entries/2026-08-13-methodology-conditional-rules.md`（关联）；agent-study B1。

## 不同 agent 模式的 system-prompt 实现

- 内容：模式=偏置档位；五档（发散/收敛/质疑/执行/转述）；与 Kilo 内置 agent 正交；agent.md=注入偏置的 system prompt，AGENTS.md=底座。
- 结论：塑形被高估——结构（文件契约/权限）保留极简，话术（人格/偏置档位）砍掉；五档/agent 降级为未检验假设，暂不实现。
- 来源：projects/locus-meta/entries/history-260813-2014.discussion.md（单元 2–4）；agent-study collaboration-rules-draft.md。

## 探索丢 subagent 的操作细则（token 方案阶段 2）

- 内容：方案 B 的"读丢写留"——何时丢 subagent、怎么丢、摘要格式、触发阈值，操作动作尚未定。
- 状态：留到 cogos 下次联调前定；骨架见 projects/locus-meta/docs/token-cost-analysis.md 方案 B。
- 来源：scratch/token-cost-implementation-plan.md 阶段 2 讨论。
