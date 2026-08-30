# checkpoint-4 — cog-runtime 实施 · 段 2/2（轮 4-6）

> 状态：task-4 完成，两条支路闭环 + 并发 + 父子 + shutdown 全绿。
> 验证：`tests/cog_runtime/` 32 passed；全量 pytest 765 passed 无回归（751 → 765，净增 14）。

## 已做修改

- `cogos/cogos/cog_runtime/unit.py` — 加 `_tool_calls`/`_tool_results`/`_tool_called` 三字段（unit.py:25-27，工具轮次状态）
- `cogos/cogos/cog_runtime/runtime.py` — `shutdown()` 方法（runtime.py:46-52，遍历 `_units` 统一 `interrupt` 后逐 `await wait()` 收尾）
- `cogos/cogos/cog_runtime/runtime.py` — running 分支检测 tool_calls 转 tooling（runtime.py:89-94）+ tooling 分支实现工具续轮（runtime.py:97-133）
- `cogos/tests/cog_runtime/test_tool_loop.py`（新建）— 支路 B 闭环 6 用例
- `cogos/tests/cog_runtime/test_concurrency.py`（新建）— 并发上限 + `_units` 注册表 2 用例
- `cogos/tests/cog_runtime/test_parent.py`（新建）— 父子通知 2 + 父 on_ready 装配示例 1 用例
- `cogos/tests/cog_runtime/test_lifecycle.py`（新建）— shutdown 收尾 3 用例

## 关键结论（本段钉死）

- **工具续轮（tooling 态两阶段）**：running 检测到 `resp["tool_calls"]` → 存 `_tool_calls`（含 id）+ 转 tooling。tooling 第一阶段（`_tool_called` 为 False）：剥 id 传 `[{name, args}]` 给 `on_tool_call`，await 返回结果存 `_tool_results`，`continue` 回入口检查 interrupt。第二阶段：append `assistant(tool_calls)`（含 id，content 有值才带）+ `role:tool` 消息（`tool_call_id` 按位置配回）→ 清理字段 + `_resp=None` → release sem → `state="pending"` 重查 ready 再入队。
- **工具续轮 sem 策略**：工具执行期间 release sem（让出并发窗口），append 后走 pending 分支重新 acquire（真「再入队」到队尾，非持有不放）。
- **on_tool_call 缺失**：有 tool_calls 但无回调 → `CuResultError("invalid_request")`（无法续轮，显式失败归因）。
- **结果等长等序**：用 `zip` 按位置配回，不校验长度/顺序（设计「乱了不报错」，最小版信任上层）。
- **shutdown 收尾**：快照 `_units` 后逐个 `interrupt("shutdown")`，再逐个 `await cu.wait()`（依赖 done_event，running 态等 chat 返回后在入口发现 interrupt；queued 态等 acquire 返回后入口发现）。父子场景 parent 由 child 的 `_finish` 通知唤醒后同样在入口发现 interrupt。
- **父 on_ready 装配模式（细节②示例）**：子 `on_done` 把 `result` 收起存外部，父 `on_ready` 里幂等装配（外部标志位防重复 append）进 material——runtime 不自动汇总，装配由上层做。

## 遗留

- **细节① 告知值默认注入（设计 2.5）**：YZ 拍板**先遗留**。原因：告知值本质是进 prompt 的预算文本，属后续语义层 prompt 设计；当前机制层不给默认注入。后续要加时注入点简单：`CogRuntime` 构造参数 + `cu()` 处 material 头部插一条 system 消息。默认文本数值（工作预算 16K/输出 4K 量级）本身在 checkpoint-7/8 已标注「待调参数，未定」。
- 工具轮次上限归上层（`on_tool_call` 里统计 + `cu.interrupt()`），未在 runtime 内置——设计如此，非遗漏。
