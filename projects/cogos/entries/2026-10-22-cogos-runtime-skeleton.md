# agent runtime 骨架落码（2026-10-22）

> 状态：**第一步已落码**（`6563b28`，已 push）。承主线六步循环 loop ＋ 工具先行完成（body/memory/元层 file 均已落码）。本件记「搭架子」第一步的设计结论＋落码＋遗留；机制层设计（状态机/心跳/介入/装载）与三步路线原为 `scratch/2026-10-21-agent-lifecycle-design.md`、`scratch/2026-10-22-agent-build-roadmap.md`，收口后术语进 glossary、本件记已验证的落码结论。

## §1 结论

- 自驱 agent 大量停留概念，先搭**能跑的框架**：新建 `cogos/agent/runtime/` 独立模块，一条 stub 事件走通 `ASLEEP→WAKING_UP→AWAKE→FALLING_ASLEEP→ASLEEP` 完整生命周期。
- **架子的唯一验收意义 = 两个钩子接口形状定对**：`Context.append/entries`（append 上下文入口）＋ `Distiller.distill`（蒸馏挂载点）。内容 stub、接口形状不能错——价值本体＝append＋蒸馏，架子只是载体。
- **三步走**：① 搭架子（机制层、内容 stub，**本步完成**）→ ② append＋真 LLM＋工具接线验证 → ③ SEQ/蒸馏/对齐动机（前奏＝出生事件）。

## §2 关键选型（why）

- **并行新建独立模块** `runtime/`，不动 v2.2 过渡桩（`app.py`/`consciousness.py`/`flow.py`）：demo/测试仍用旧桩，原地改破坏可运行状态；跑通后再切换删除。
- **复用现有 CogRuntime ＋ `cu.no_wait()` ＋ `on_done` 回调**，stub 只换 lm_client：on_done/介入机制是真的，第二步接真 LLM 只换 client，不造假接线。
- **on_done 回调必须自包 try/except**：`runtime._finish` 里 `await on_done(...)` 裸奔，异常冒进无人 await 的 `_advance` task → 状态机卡 AWAKE 且无日志（runtime 改 on_except 留后）。
- **「无 while 循环」验收改「无忙等」**：grep 断言误伤 heartbeat 的 `while True + await sleep`；真该防的是 busy-wait（无 await 空转）＋ per-event flow 消费循环，走 review 不走 grep。

## §3 落码

- `cogos/agent/runtime/`：`state.py`（四态枚举＋StateMachine＋转移历史 observer）、`agent.py`（Agent＋start_agent/main＋心跳/介入/落盘归一）、`events.py`（EventQueue＋SignalQueue）、`context.py`（Context＋Distiller 协议＋StubDistiller）、`stream.py`（Stream 持 Context＋current_cu）、`stub.py`（StubLmClient）。
- 验收 5 条（4 pytest＋1 review）：四态走通、触发者可断言（`heartbeat/meta/on_done/meta`）、两态两法（AWAKE 注入立即走介入点、ASLEEP 注入只入队）、启动归一（非 ASLEEP 一律归 ASLEEP）、无忙等。
- 测试 `tests/agent/runtime/test_runtime.py` 4 passed；全量 agent 323 passed 3 skipped 无回归。

## §4 遗留（留第二步）

- `on_tool_call` 介入点（第一步 stub 不调工具不触发）
- runtime 改造（`on_ready`/`on_done` 走 on_except 兜底）
- 两套分层状态（意识盘上标签 `empty/loading/loaded/unloading`，第二步落盘切意识标签）
- Context 内容落盘、SEQ/记忆/蒸馏、sleep 工具真实现、昼夜节律/推理监控

## §被否

- 原地改 v2.2 过渡桩（破坏现有可运行状态）。
- 自写 stub cu（造假接线，第二步重接）。
- 「无 while 循环」grep 静态断言（误伤 heartbeat，改「无忙等」review）。
- 状态落盘落意识标签（第一步只落 agent 四态单字段临时方案）。
- 两钩子掺二三步概念（Context 只给 append/entries，主题检测/长度管理/折叠不进 Context）。
