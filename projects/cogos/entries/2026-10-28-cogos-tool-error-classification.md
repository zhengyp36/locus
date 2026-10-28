# 工具错误分类（ToolResult）已落码

> 状态：已实现并推送，cogos commit `7ed3667`，全量 1408 passed, 6 skipped（+6 新增）。
> 来源：cu-prep 遗留问题（`scratch/2026-10-27-cogos-llm-wiring-cu-prep.md`）+ design §10 工具执行契约。

一句话：把 runtime 工具执行段的「异常整体挂 cu」修成「per-tool 结果分类回传」；错误分类落在 `ToolRegistry.execute`（executor 层），runtime 只透传 `ToolResult`。

## 结论

1. **分类放 `ToolRegistry.execute`（executor 层），不放 runtime**。design §10 文字写「runtime 在调用 executor 前校验」，与 §6「executor 含前置校验+分类」有张力；落实现按 §6，因 runtime 不持 registry/schema，校验+分类天然在 registry 内部。
2. **四类**：`unknown_tool`（name 不在 registry）/ `bad_args`（`validate_args` schema 校验失败）＝可恢复、模型的错，回传让模型改；`tool_bug`（校验通过后工具抛异常）＝不可恢复、系统的错，回传 + error 级日志 + 触发介入；normal＝正常结果。`ToolResult{ok, content, error_class, error_detail}`（`cog_runtime/types.py`）。
3. **`call` 委托 `execute`**（单一逻辑来源），`call` 保持 dict 契约 → `tests/agent` 零波及（只有 `test_time_wait_invalid_seconds` 一处断言更新，见「行为变化」）。
4. **runtime 归一化透传**：executor 返回元素若是 `ToolResult` 用之，否则兜底 `ToolResult(ok=True, content=x)`（向后兼容返回 dict/str 的旧 executor）。每个结果都回传成 tool message（错误回传 `error_detail` 文本）。整体 `ok` 仅在出现 `tool_bug` 时为 False；`error` 拼接 `"<tool>: <detail>"`。
5. **`on_tool_done(cu, ok, error)` 扩一参**（breaking，消费方少：stream/consciousness/StubCu + 测试）。error 经 stream → consciousness 进 `InterveneContext.error`。
6. **`_on_intervening` 的 `if not ok: raise` → `if not ok and error is None: raise`**：tool_bug（ok=False 且 error 非 None）走正常决策流（元层决定 halt/notify/exit），不再硬 raise；程序失败（ok=False 且 error=None，即 executor 整体崩溃 / LLM 失败）仍 raise。

## 被否方案

- **校验放 runtime**（design §10 字面）：否，runtime 不持 registry/schema，且 §6 已明确 executor = registry。
- **`call` 独立实现、不委托 `execute`**：否，unknown_tool/tool_bug 逻辑会重复、易漂；代价是 call 行为微变（见下），接受。
- **executor 必须返回 ToolResult、不做归一化**：否，归一化向后兼容，现有测试与冒烟脚本（echo_executor 返回 dict）零改动。

## 行为变化（需知悉）

`validate_args` 的 schema type 校验前置到 executor 层，取代部分工具内部的 `float()` 宽容转换：如 `time_wait` 传 `"abc"`（schema 声明 number）现被拦为 `bad_args`（`should be number`），不再落到工具内 `InvalidWait`。这是 design「bad_args = schema 校验失败」的直接结果，属预期收紧。

## 下一步

~~Consciousness 挂 CogStream~~（已落码 `e3f50b0`，10-28）：`_start_stream`/`_on_intervene`/`_checkpoint`，行为等价纯替换；**双持久化分叉已拍**（意识层挂 stream 不传 `store_dir`，store 是唯一持久化）。→ `entries/2026-10-27-cogos-cogstream.md`
