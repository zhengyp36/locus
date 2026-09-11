# cogos 自驱回路 P0 收尾 + 路线图（2026-09-11 晚）

承接 S4 第一阶（判据源外移）+ 真靶 dogfood。本会话按"先收口、再机制硬化"把当前阶收尾，并把路线画进 ROADMAP。

## 1. 收口（push `57c8aa9`）

把 dogfood `30de9fd` 的两项修复 port 到 `s2-selfdrive-loop`：
- `cogos/cog_runtime/runtime.py`：cu chat 传 `max_tokens=8192`（默认 1000 会截断写文件的 tool_call → `semantic`）。
- `tests/agent/test_terminal.py::test_observe_while_busy`：改轮询等 `start`（消 flaky）。

连同未 push 的 `4cf0f31`（变更绑定守卫 + CuResultError 留 message）一起 push。

## 2. 机制硬化（push `b8a92d5`，候选 2）

### 2.1 确定性：相变验收复现
单次验收不可信（flaky 会翻转 verdict，伪造判据红/假绿）。凡驱动相变的验收结论都复现：
- 基线：连跑两次同 verdict 才可信；不一致 → `needs_human / unstable_acceptance`（不唤醒模型）。
- 判据相转红：先过变更信号，再复跑确认；两次都红才记 `criterion_red`。
- 实现相转绿 / 单相 done：复跑确认两次都绿才 done。
- 非相变中间轮不复现（省验收开销）。

### 2.2 cu 错误：瞬时重试 + 连续停问
- `retryable`/`semantic` 在**同一轮内**原地重试至多 2 次（不耗 step、不跑验收、不回喂错误文本）。
- 任何 category 连续 2 轮错误 → `needs_human / repeated_cu_error`，不烧满 `max_steps`；成功一轮清零。
- 每次落 `event:"cu_error"`（category/message/streak）。

### 2.3 flaky 测试治理
`tests/agent/test_tools.py::test_execute_timeout_partial_output`：原 `python3 -c` 启动 + 0.2s 有竞态（无输出），改 shell 内建 `printf started; sleep 5` + 超时 0.5s。修前 2/20 失败，修后 15/15 稳定。

## 3. 路线图（`ROADMAP.md` 重写）

- 目标：自驱 L1→L4，最终态 = 双自驱共驱（认知层人机对等、机制层 agent 不可自改）。
- 核心表：回路 6 格（议程/触发/执行/验证·机制/验证·判据/写回/停问）× 现在的源 / 目标源 / 状态。
- 阶段：P0 收尾当前阶 → P1 自触发（常驻/事件唤醒 + 工位隔离，结构性大跳）→ P2 议程源外移（L3，先设计生成/终结/丢弃权安全件）→ P3 L4 协作协议；支线=跨会话记忆。
- 两个事实：L1→L3 只有两个结构跳（都是机制缺失）；"源外移"是持续轴，无 100% 终点。

## 4. 真机验证（`checkpoint/s4-target`）

重置最小靶（`duration.py` 桩 + smoke，无 agent 判据），用新 loop（cogos-s2 @ 新代码）+ 真 deepseek 跑：

- `verdict=done`；`red_green={baseline_green, criterion_red(step1), implemented_green}` 全齐。
- 相变处各跑两次：baseline/criterion/implement 验收 9.12/10.9/9.36s（合计 29.37s vs 旧 8.65s）；pytest 启动占大头。
- 判据真实性：stub `duration.py` → agent 测试 16 failed，恢复实现 → 17 passed。
- 旧态存档 `s4-target/_prev/`。

## 5. 判据复核点定型（`design-selfdrive-loop-s4.md` §8，push `62c400f`）

人只在 `done` / 停点复核，看三样证据：`runs.jsonl` 的 `red_green`、agent 产出的判据（stub 复跑确认真红）、实现 diff。不通过 = 改标题目标 / 换靶，不替 agent 写测试。

## 6. 结论 / 遗留

- 复现机制让相变验收翻倍；当前判定可接受，暂不做分层验收。
- **分层验收未做，需先定设计**：agenda 如何声明 target-gate vs full-info；两相项的 target 在判据写出前未知。
- 新状态 `unstable_acceptance` / `repeated_cu_error` / `no_change` / `spurious_red` 待更多真活观察。
- 下一步候选：新真活靶子（加能力、基线绿）/ 分层验收设计 / P1 工位隔离 / task-7（YZ 讨论中）。
