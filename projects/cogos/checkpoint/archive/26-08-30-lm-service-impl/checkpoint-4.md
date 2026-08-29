# checkpoint-4 — 轮 4：providers 归一 + 防御解析 + error category + finish_reason 特殊态

## 当前问题

补全 provider 适配层：deepseek/openai 响应归一（reasoning/视觉/content nullable）+ 防御性解析（空 body/非 JSON/choices 空不崩）+ 厂商错误码→category + finish_reason 特殊态，并 populate `PROVIDER_REGISTRY`。

## 已做修改

- `cogos/cogos/lm_service/providers/base.py`：新增共享函数 `status_to_category`（400/422→invalid_request，401/403→auth，402→quota，429→retryable，5xx→retryable，其他→semantic）、`post_json`（传输错误/空 body/非 JSON → retryable，不设 status_code）、`parse_response`（非200→category+status_code=原状态；200 但非 dict→retryable；choices 空→semantic；content_filter→content；insufficient_system_resource→retryable；content None→""；reasoning=msg.reasoning_content）。ProviderError(category, message, raw, status_code) 不变。
- `cogos/cogos/lm_service/providers/deepseek.py`：新建。蓝本逻辑原样（thinking enabled 发 `thinking.type`，disabled 发 temperature/top_p），响应归一走 `parse_response`（reasoning_content→reasoning）。
- `cogos/cogos/lm_service/providers/openai.py`：新建。蓝本逻辑原样（thinking enabled 发 `reasoning_effort=budget_tokens`），reasoning 恒 null。
- `cogos/cogos/lm_service/scheduler.py`：`PROVIDER_REGISTRY` 从 `{}` 改 populate `{"deepseek": DeepSeekProvider(), "openai": OpenAIProvider()}`。

## 已读代码要点

- 蓝本 `deepseek.py:42` `await resp.json()` 无 try → 非 JSON 会漏到 handler 变 500；`deepseek.py:48-51` 现丢弃 `reasoning_content`。
- 蓝本 `openai.py:25-27` `reasoning_effort` 是请求侧参数，响应无 reasoning。
- 本工程 `handler.py:81` `except ProviderError → _error_response(category, msg, status=e.status_code)`：status_code=None 时走 `_CATEGORY_STATUS` 映射。

## 关键结论/决策

- **错误分类收口在 base.py 共享函数**：两 adapter 只拼请求体，分类/防御解析/归一全走 `post_json`+`parse_response`，避免两处各写一套。
- **status_code 只给 HTTP 层错误**：非200 时 `status_code=status`（贴近原错误）；协议层异常（空 body/非 JSON/非 dict/choices 空/finish_reason 特殊态）不设 status_code——否则 handler 会以 200 状态码返回 error body，破坏「2xx vs 非2xx」区分。
- **finish_reason 特殊态**：content_filter→content、insufficient_system_resource→retryable；stop/length/tool_calls 透传。
- **视觉 content 归一最小版 = 原样透传**：deepseek/openai 均 openai 兼容 content[]，adapter 不做转换（deepseek-vl 是否同构待真实验证）。

## 遗留/坑

- **gate 通过**：round4_gate.py 全绿（status→category 9 项 + parse_response 归一/特殊态 12 项 + adapter 请求构造 4 项）+ round3_gate.py 回归绿。
- **正式 pytest 测试在轮 9**（mock 错误归类），本轮只做 /tmp 脚本 gate。
- **真实验证需 YZ 账号**（spec 6.2），mock 全绿后停。
