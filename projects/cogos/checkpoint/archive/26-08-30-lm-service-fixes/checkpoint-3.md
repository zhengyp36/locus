# checkpoint-3 — 轮 3：② tool_calls 归一输出

## 当前问题

契约 ② 输出侧：`message.tool_calls` 归一为 `[{id, name, args: dict}]`。`arguments`（JSON 字符串）parse 失败、或 `finish_reason == "tool_calls"` 但 tool_calls 空，均 → `ProviderError(semantic)`。`content` 与 `tool_calls` 并列可选。

## 已做修改

- `cogos/lm_service/providers/base.py:118-156`：`parse_response` 加 tool_calls 归一——`msg.get("tool_calls")` 为 list 时逐条提取 `{id, function:{name, arguments}}` → `{id, name, args}`；`arguments` 空串/None → `{}`，非空 `json.loads`，失败或结果非 dict → SEMANTIC；`finish_reason=="tool_calls"` 且 tool_calls 空 → SEMANTIC。
- `cogos/lm_service/providers/base.py:158-168`：返回 dict 加 `"tool_calls"` 键（无 tool call 时为 `None`，与 content 并列可选）。
- `cogos/lm_service/providers/base.py:78-88`：docstring 补 tool_calls 归一说明。
- `tests/lm_service/test_normalization.py:14`：`FIELD_SET` 加 `"tool_calls"`。
- `tests/lm_service/test_normalization.py:17-27`：`make_raw` 加 `tool_calls=None` 参数。
- `tests/lm_service/test_normalization.py:104-135`：新增 `test_tool_calls_normalized`（deepseek/openai 两 parametrize）+ `test_tool_calls_empty_arguments_is_empty_dict`。
- `tests/lm_service/test_errors.py:106-141`：新增 `test_tool_calls_arguments_parse_failure_is_semantic` / `test_tool_calls_finish_reason_empty_is_semantic` / `test_tool_calls_arguments_not_object_is_semantic`。

## 关键结论/决策

- 服务端 `parse_response` 抛 `ProviderError(ErrorCategory.SEMANTIC, ...)`，经 scheduler→handler→客户端统一成 `LmServiceError(semantic)`（任务文件「LmServiceError(semantic)」是客户端视角，服务端落地为 ProviderError 同 category）。
- `arguments` 空串/None 归一 `{}` 而非抛错：厂商可能返回空 arguments（无参工具），视为合法空参数；非空才走 json parse 校验。
- `id` 直接取厂商 `tc["id"]`（deepseek tool call 同构 openai，均带 `id`）；`type` 字段丢弃（内部规范不需要）。
- 无 tool call 时 `tool_calls` 为 `None`（非 `[]`），与 content 语义对称：`[]` 是「有归一结果但空」，`None` 是「本响应无此字段」。判续轮只看 `tool_calls` 是否非空（上层 cu 判）。

## 验证

- `python3.11 -m pytest tests/lm_service/` → 59 passed 绿（53→59，新增 6 例）。

## 遗留/坑

- recorder/scheduler 记录 tool_calls 字段留轮 5「调试记录字段补齐」（`_record`/`build_entry` 现不含 tool_calls，轮 3 scope 仅归一输出）。
- `tools` 输入组装（deepseek/openai `chat_completion` 拼厂商 `tools` 格式）+ `handler.py` 白名单加 `tools` 是轮 4。
- deepseek `strict` 字段支持与否待轮 4 实施时确认（任务②钉死细节：支持才补，不支持透传 schema 原样）。
