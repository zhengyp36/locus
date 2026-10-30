# CogStream 心跳驱动改造（10-29）

结论：CogStream 从「`act()` 显式驱动」改为「构造即后台心跳 + `on_intervene` 单一回调驱动」，落码 commit `56bed02`。全量 1407 passed。

## 改了什么

- **去 `act`**：外部不再管何时启动/停止推理，全部收进 `on_intervene`。构造即 `asyncio.create_task(_idle_loop())`，空闲时周期回调 `on_intervene(STOPPED)`（默认 250ms，`idle_interval` 可配）。
- **介入点三种**：`TOOL` / `REASONING` / `STOPPED`（原 TOOL_DONE/REASONING_DONE 改名 + 新增 STOPPED）。
- **合法性判据统一为 context 尾消息**：介入点不再限制返回策略；继续类（Proceed/Relay/Switch）apply 后尾 ∈ {user, tool} 且非空才合法（Proceed 尾非法 → `IllegalAction`，Relay/Switch 尾非法 → `ValueError`）；Stop 总是合法。这与既有不变量「advance 合法 ⟺ 尾 role ∈ {user, tool}」同源。
- **`shutdown()`**：同步、幂等、不可重启（只能重构）。cancel 心跳 task + `_shutdown` 标志 + 活跃 cu `interrupt("shutdown")`（软中断）。
- 意识层挂接最小适配：`_start_stream` 去 act、`_on_intervene` 加 STOPPED 分支（尾 user/tool → Proceed 启动）、Stop/Sleep 决策后延迟 shutdown 回收 idle task。

## why（关键决策）

- **心跳驱动而非事件唤醒**：最轻架子、无状态、天然覆盖「无外部事件」场景；250ms 异步 sleep 不忙等，开销可忽略。
- **`_shutdown` 标志是必须兜底**：cancel 心跳 + interrupt cu 仍留「心跳正 await on_intervene(STOPPED)，shutdown 打断后返回 Relay 拉起新 unit」的顺序窗口（cancel 只在 await 点生效，on_intervene 返回→执行 Action 之间是同步原子块）。故 `_dispatch` 执行 Action 前检查 `_shutdown`。
- **`cu.interrupt` 是软中断**：不 cancel 飞行中的 chat，shutdown 返回后 cu 可能再完成一次网络往返才 settle；`_on_done` 收到 `CuResultInterrupted` 走既有分支、不回调 on_intervene，所以「shutdown 后不再回调」成立。
- **STOPPED 下允许 Proceed**：停在 TOOL 介入点（尾=tool）后，STOPPED 心跳 Proceed 续推是合法重启路径。

## 被否方案

- 保留 `act` 换个名字 → 与「去 act、驱动全收进 on_intervene」矛盾，否。
- shutdown 不等 + 不设 `_shutdown` 标志 → 有顺序窗口，否。
- 让 consciousness 深度适配（STOPPED 语义进状态机、shutdown 时机联动）→ 属阶段1 重写，本次仅最小适配保测试绿。
