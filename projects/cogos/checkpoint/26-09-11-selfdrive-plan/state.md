# S0｜组件状态面（cogos 自驱回路）

> 2026-09-11。计划见 `plan.md`。用途：把"有什么、什么状态、在回路里扮演哪一环"收成一张表，一眼看出回路缺哪一格。
> 依据：`locus/projects/cogos/current.md` + cogos 代码/测试清点。状态含推断处标 `需核`。

## 一、回路角色对照

`议程 → 触发 → 执行 → 验证 → 写回(记忆) → 停/问`；感知/通信/模型是支撑件。

| 组件 | 位置 | 状态 | 回路角色 |
|---|---|---|---|
| lm_service | `cogos/lm_service/` | ✅ 完成（client/router/providers/admin/recorder/scheduler；6 测试目录） | 执行（模型底座） |
| cog_runtime | `cogos/cog_runtime/` | ✅ 完成（types/unit/runtime；cu 多轮续轮/并发/父子通知/shutdown） | 执行（动作循环） |
| agent.consciousness | `cogos/agent/consciousness.py` | 🟡 半成（cu 多轮已接；工具集齐全；**无持久记忆、无自验证**；context 仅进程内） | 执行 + 记忆（弱） |
| agent.tools | `cogos/agent/tools.py` | ✅ 完成（read/write/edit/execute/search/fetch/scratch） | 执行 |
| agent.terminal | `cogos/agent/terminal.py` | ✅ 完成（busy/idle、buffer、killpg 中止、terminal_done 事件） | 执行 |
| agent.timer | `cogos/agent/timer.py` | ✅ 完成（绝对时间戳、`timers.json` 恢复、timer_fired 事件） | **触发**（原语） |
| agent.events / app | `cogos/agent/{events,app}.py` | ✅ 完成（AgentEvent/render_event、事件队列 + consumer） | 触发（通道） |
| agent.perception | `cogos/agent/perception.py` | ✅ 完成，但**仅 p2p 文本** | 触发（外部消息） |
| agent.webtools | `cogos/agent/webtools.py` | ✅ 完成（search/fetch） | 执行 |
| feishu（通信总线） | `cogos/feishu/` | ✅ 收口（28 测试目录） | 触发 + 写回（人机界面） |
| phone | `cogos/phone/` | ✅ 完成（store/model/phone/term/fake） | 触发 + 通信 |
| img_tool | `cogos/img_tool/` | ✅ 完成（core/cli/stub/resource） | 感知（原语） |
| image_ctx | `cogos/image_ctx/` | ✅ 完成 P1/P2（view/domain/render/tools/schemas） | 感知（图对象状态） |
| cog_ctx | `cogos/cog_ctx/` | ✅ 完成 P3（FigContext/Manager，老化/strip） | 感知（上下文管理） |
| cog-func `look_at` 种子 | — | ❌ 未实现（handoff 下一步） | 感知（功能层） |
| 议程源（机器可读） | — | ❌ 无（现仅人写的 `ISSUES.md`/`tasks/`/`ROADMAP.md`） | 议程 |
| agent 内自验证 | — | ❌ 无（draft 缺口 = 触发 + 通道） | 验证 |
| 跨会话持久 agent 记忆 | — | ❌ 无（locus 是 dev 侧外部记忆，非运行时） | 记忆 |

## 二、缺口（一眼看）

回路 `议程 → 触发 → 执行 → 验证 → 写回`：

- **执行**：✅ 齐（模型 + 动作循环 + 工具 + 终端）。
- **触发**：🟡 有外部触发（消息/timer 原语），**缺"从议程自启动/续跑"**。
- **验证**：❌ 缺（agent 内不会自查；能力已验证存在，缺触发+通道）。
- **议程**：❌ 缺（无可被 agent 读取的"下一步从哪来"）。
- **记忆**：🟡 有进程内 context + scratch + timer 持久；**缺跨会话持久**。
- **感知/视觉**：🟡 库完成，**未接入 consciousness 工具集**（vision not wired）。

**结论**：回路最缺三格——**机器可读议程、自触发、agent 内自验证**。三者正是 L1→L2 的门槛。

## 三、开放议程候选（供 S2 选一条）

来自 `locus/projects/cogos/ISSUES.md`（按"自包含 + 可验证"排序）：

1. `load_bot` 与 `AccountRef.ensure` 分层错位 —— 边界清楚、有测试可验（**首选**）。
2. sessions 软链接：群改名同步未实现。
3. resume 重建账号与 setup 的字段差异。
4. 账号失效机制两处遗留（fail-open 续命 / 无 revoke）。
5. 坐标规则注入：静态前置 → 随图动态注入（已定方向，暂缓）。

## 四、待 YZ 验收

- 这张表是否认可（尤其"回路角色"的归位）？
- S1 是否就按"议程 → 触发 → 执行 → 验证 → 写回 → 停/问"，用**已有件**填？
- S2 首条议程是否取候选 1（`load_bot` 分层错位）？
