# checkpoint-4 — 轮 4：② tools 输入组装厂商格式 + 白名单

## 当前问题

契约 ② 输入侧：`chat()` 增 `tools` 参数（内部结构化 schema），lm-service 组装厂商 `tools` 格式；`handler.py` 白名单放行 `tools`。`tool_choice` 不传；`strict` 待定。

## 已做修改

- `cogos/lm_service/providers/base.py:78-98`：新增 `assemble_tools(tools)`——内部 `[{name, description, parameters}]` → 厂商 `[{type:"function", function:{name, description, parameters}}]`；空/None → None。
- `cogos/lm_service/providers/deepseek.py:28-30`：`body.get("tools")` 非空则 `req_body["tools"] = assemble_tools(tools)`。
- `cogos/lm_service/providers/openai.py:25-27`：同上。
- `cogos/lm_service/client.py:34-60`：`chat()` 加可选 `tools=None` 参数，非 None 进 body。
- `cogos/lm_service/handler.py:5-15`：`ALLOWED_REQUEST_FIELDS` 加 `"tools"`。
- `tests/lm_service/test_normalization.py`：新增 `TestToolsAssemble`——`test_tools_assembled_to_vendor_format`（deepseek/openai）、`test_no_tools_when_absent`（deepseek/openai）、`test_no_tools_when_empty`。

## 关键结论/决策

- **内部 tools 形式钉死**（反推自任务②「组装厂商 tools 格式」）：`[{name, description, parameters}]`，parameters 是 JSON Schema；厂商格式 = 加 `type:"function"` + `function` 包装。与轮 3 输出 `[{id, name, args}]` 对称（输入无 id、输出有 id）。
- **`strict` 不补**（透传 schema 原样）：deepseek 无 OpenAI structured-outputs 的 `strict`，任务钉死「支持才补、不支持透传原样」→ 默认不补。mock 阶段无法真实验证，真实验证阶段（轮 5 后）确认 deepseek 是否支持。
- **`tool_choice` 不传**：厂商默认 auto，最小版不暴露。
- **空/None 不传 tools**：`if tools:` 同时覆盖未传（body 无键→None）与空列表（`[]`），语义一致（无工具 = 不带 tools 字段）。
- 组装复用 `assemble_tools` 放 base.py（deepseek/openai 同构 OpenAI 兼容格式，一处定义）。

## 验证

- `python3.11 -m pytest tests/lm_service/` → 64 passed 绿（59→64，新增 5 例）。

## 遗留/坑

- `recorder.py` / `scheduler.py _record` 记录 tool_calls 字段 → 轮 5「调试记录字段补齐」。
- `tools` 结构深度校验不做（白名单只放行字段，不校验 schema）；结构错由厂商 400/422 → invalid_request 上抛，最小版合理。
- deepseek `strict` 支持与否 + 真实 tool call 同构性 → 轮 5 后真实验证，AI 不擅自试账号。
