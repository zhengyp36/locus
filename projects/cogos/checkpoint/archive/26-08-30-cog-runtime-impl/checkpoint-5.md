# checkpoint-5 — lm-service 续轮消息归一→厂商转换（工位 A 直改）

> 状态：完成。真实支路 B 闭环打通。
> 验证：`tests/lm_service/` 77 passed；全量 pytest 777 passed 无回归（765 → 777，净增 12）；真实 deepseek 三路全绿（A 文本 / B 工具续轮 / E 401→auth）。

## 当前问题

cog-runtime task-4 真实环境测试，支路 B（工具续轮）续轮那一次 LLM 请求被 deepseek 以 400 invalid_request 拒绝。`on_tool_call` 正确收到归一 `[{name,args}]`，但续轮发送失败。

## 根因

lm-service 只实现了 tool call 内部化的两个方向（输入 `tools` schema→厂商、输出厂商 tool_calls→归一），漏了**续轮回填方向**：cog-runtime 按内部规范拼的 `assistant(tool_calls)` + `role:tool` 消息，被 provider 层原样透传厂商。属设计 4.2「lm-service 只负责与厂商格式互转」已约定职责的实现遗漏（task-3 只验证了单轮输出，续轮当时未实现，故未暴露）。

三处格式差异：

| 位置 | 内部格式 | 厂商格式 |
|---|---|---|
| `assistant.tool_calls` | `{id, name, args: dict}` | `{id, type:"function", function:{name, arguments: str}}` |
| `role:tool.content` | dict/list | JSON 字符串 |
| `assistant.content` | list `[{type:text,...}]` | str / null |

## 已做修改

- `cogos/cogos/lm_service/providers/base.py` — 加 `assemble_tool_messages`(base.py:101) + `_vendor_assistant_tool_message`(base.py:134) + `_vendor_assistant_content`(base.py:152) + `_vendor_tool_message`(base.py:163)，与 `assemble_tools`(base.py:78) 并列，是 `parse_response`(base.py:174) tool_calls 归一的反向转换
- `cogos/cogos/lm_service/providers/deepseek.py` — import 加 `assemble_tool_messages`；`req_body["messages"] = assemble_tool_messages(body["messages"])`
- `cogos/cogos/lm_service/providers/openai.py` — 同上
- `cogos/tests/lm_service/test_tool_messages.py`（新建）— 12 用例（纯函数 8 + provider 接入 4）

## 关键结论

- **转换边界**：只碰 `role=="assistant"` 且含 `tool_calls` 的消息 + `role=="tool"` 消息；user/system/普通 assistant 原样透传。多模态 user content（image_url）不经过此转换。
- **assistant content**：list 提取 `{type:text}` 拼 str（`\n` join）；空 list → `None`（厂商 tool_calls 消息 content 标准形式）；非 list（str）透传。续轮场景 assistant 只可能有 text part（模型调工具时不会出图）。
- **role:tool content**：dict/list → `json.dumps(ensure_ascii=False)`；str 透传。
- **arguments**：`json.dumps(args or {}, ensure_ascii=False)`，args 缺失兜底 `"{}"`。
- **幂等/契约**：不做「已转厂商则跳过」判断——lm-service 对外契约恒为内部格式（cu 只拼内部格式），每次请求都从内部格式转，不存在重复转换。

## 遗留

- 无。真实闭环（A/B/E）已通，cog-runtime task-4 连同 lm-service 续轮转换整体验证完成。
