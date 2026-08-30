# checkpoint-6 — 真实 tool call 验证（deepseek，YZ 提供 key）

## 当前问题

task-3 停下点：真实 tool call 验证——deepseek 是否同构 openai tool call 格式、`arguments` 真实 parse、`strict` 是否支持、tools 输入组装是否被厂商接受。key `~/.secrets/deepseek-cogos.key`（= 已配置 `尾号b111`，internal_key `ik_c47WkfAw7E5v6Ck8idMHgg`）。

## 验证过程

1. **直连 deepseek API**（httpx，`api.deepseek.com`，model `deepseek-v4-flash`）：
   - 发带 `tools` 请求 → HTTP 200，响应 `tool_calls=[{index, id, type:"function", function:{name, arguments(str)}}]`，`arguments` 是 JSON 字符串 `"{\"city\": \"Beijing\"}"`，`finish_reason="tool_calls"`，`content=""`。
   - 发 `function.strict=true` → HTTP 200 不报错，正常返回（deepseek 接受但**不强制** structured outputs，忽略 strict）。
2. **走 lm-service 完整链路**（LmClient + server 11435）：
   - `LmClient(internal_key).chat(messages, tier="basic", tools=[...])` → 归一输出正确（见下）。
   - 调试记录 `calls.jsonl` 最后一行 `tool_calls` 字段正确落盘。

## 归一输出（验证通过）

```
content: []                       # tool call 轮 content 空 → 归一 []
finish_reason: "tool_calls"
tool_calls: [{id: "call_00_...", name: "get_weather", args: {city: "Beijing"}}]   # arguments JSON 字符串 → dict ✅
usage: {prompt_tokens: 288, completion_tokens: 44}
routed: {tier: "basic", degraded: false}
```

## 关键结论/决策

- **deepseek tool call 同构 openai** ✅：`{id, function:{name, arguments(str)}}`，与 `parse_response` 归一假设一致，零改动。
- **`arguments` 真实 parse** ✅：厂商返回 JSON 字符串，`json.loads` 成 dict 正确。
- **`strict` 不补** ✅ 决策正确：deepseek 接受 strict 字段但忽略（不强制），透传 schema 原样安全；若强行补也不会报错但无意义。当前代码不补，保持。
- **tools 输入组装** ✅：`{type:"function", function:{name, description, parameters}}` 被 deepseek 接受并正确触发 tool call。
- **content 空 → []** ✅ 与契约③一致（tool call 轮 content 为空串）。

## 验证结果

task-3 三项遗留（① base_url ② tool call 内部化 ③ content[]）+ 调试记录 tool_calls，mock 65 + 全量 733 全绿，真实验证也全绿。**task-3 完成。**

## 遗留/坑

- 环境坑：`pip show cogos` 的 editable 指向工位 A `/home/zhengyp/work/A/cogos`；跑脚本（非 pytest）需 `PYTHONPATH=/home/zhengyp/work/B/cogos` 或把脚本放 cogos 目录，否则 `import cogos.lm_service` 会拿到工位 A 旧代码（无 `tools` 参数）。pytest 不受影响（rootdir 处理）。
- server 端口仍用 11435（11434 被蓝本旧 server 占用）。
- 规格 `design-lm-service-min.md` 第五节字段清单未加 `tool_calls`、cli content 打印美化——两项待 YZ 裁决（延续轮 2/5）。
