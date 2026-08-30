# codebase — lm-service 代码认知快照

> 用途：工位 B 实施 task-3 前的代码认知基线，避免干净会话全量通读。锚点优先，细节靠锚点重 `read`；就地改，认知变就修正，不复述代码原文。
> 本体路径：`cogos/cogos/lm_service/`（在 work/B/cogos，非 locus）。

## 文件地图

| 文件 | 行 | 职责 |
|---|---|---|
| `client.py` | 91 | `LmClient`（async http 客户端，对外冻结契约入口）|
| `handler.py` | 89 | aiohttp 路由 + 请求字段白名单 + 错误响应 `{"error":{"category","message"}}` |
| `scheduler.py` | 182 | 并发池化：`AccountScheduler`(semaphore+RPM) + `Scheduler`((provider,account) 池) + 记录 |
| `router.py` | 66 | model 选择：`infer_modalities` + `select_model`（模态>tier>must）|
| `config.py` | 197 | 三文件 yaml(config/secrets/state) + `resolve_internal_key` |
| `admin.py` | 197 | CLI 管理命令（api-key / internal-key / calls）|
| `cli.py` | 127 | 命令入口（argparse 嵌套 subparsers）|
| `recorder.py` | 93 | calls.jsonl 落盘（`build_entry`）|
| `server.py` | 47 | aiohttp app 组装 |
| `providers/base.py` | 191 | `ErrorCategory`(六类) + `parse_response`(归一) + `assemble_tools` + `post_json`(防御性传输) |
| `providers/deepseek.py` | 38 | deepseek adapter（thinking/temperature 处理）|
| `providers/openai.py` | 36 | openai adapter（reasoning_effort 处理）|

## 三遗留改动点锚点

### ① internal_key 自带 base_url（YZ 拍板方案 A）✅ 轮1完成

- `client.py:30` `LmClient.__init__(internal_key)`：已删 `base_url` 参数，`_base_url` 恒 = `http://{DEFAULT_HOST}:{DEFAULT_PORT}`（`client.py:16-17` 从环境变量 `LM_SERVICE_HOST`/`LM_SERVICE_PORT` 读，模块导入时求值）。
- `cli.py:55/72/108`：`call` 命令同步删 `base_url` 链路与 `--host`/`--port` 参数（人工 CLI 也属上层，不感知地址）；`server` 命令 `--host`/`--port` 保留（服务端监听地址，非客户端）。
- `config.py:169-197` `resolve_internal_key`：返回厂商 `base_url`（`config.py:193`）且 `scheduler.py:55` 已用——服务端侧已实现，未动。
- LmClient 测试指 fake 服务：现有 `test_errors.py` 走 mock aiohttp（`LmClient("ik_x")` 无 base_url），不靠环境变量。

### ② tool call 内部化（输出侧 ✅ 轮3 / 输入侧 ✅ 轮4）

- `providers/base.py:141-179` `parse_response`：tool_calls 归一 ✅ 轮3——`{id, function:{name, arguments(str)}}` → `[{id, name, args: dict}]`；arguments 空→`{}`、非空 `json.loads` 失败或非 dict → SEMANTIC；`finish_reason=="tool_calls"` 但 tool_calls 空 → SEMANTIC；返回加 `"tool_calls"` 键（无则 `None`）。
- `providers/base.py:78-98` `assemble_tools` ✅ 轮4：内部 `[{name, description, parameters}]`（parameters=JSON Schema）→ 厂商 `[{type:"function", function:{...}}]`；空/None → None；不补 `strict`（deepseek 不支持 structured outputs，透传 schema 原样，真实验证阶段确认）。
- `client.py:34-60` `chat()`：加可选 `tools` 参数进 body ✅ 轮4。
- `handler.py:5-15` `ALLOWED_REQUEST_FIELDS`：加 `"tools"` ✅ 轮4。
- `providers/deepseek.py:28-30` / `providers/openai.py:25-27`：`body.get("tools")` 非空则 `req_body["tools"] = assemble_tools(tools)` ✅ 轮4。
- `recorder.py:19/45/64` + `scheduler.py:131` `_record`：记录 tool_calls ✅ 轮5——`_FIELD_ORDER`/`build_entry`/返回 dict 加 `"tool_calls"` 键，`_record` 传 `tool_calls=result.get("tool_calls")`；无 tool call 记 `None`，有记归一后 `[{id, name, args}]`。
- 内部规范见 `design-cog-runtime-min.md` 4.2（工具集输入 / tool_calls 输出 / 结果回填归 cu）。`tool_choice` 不传（厂商默认 auto）。
- 真实验证 ✅（deepseek-v4-flash，checkpoint-6）：tool call 同构 openai `{id, function:{name, arguments(str)}}`；`arguments` 真实 parse 成 dict；`strict` 厂商接受但忽略（不补正确）；tool call 轮 `content=""` → 归一 `[]`；调试记录 tool_calls 正确落盘。

### ③ content 归一 content[] ✅ 轮2完成

- `providers/base.py:128-133` `parse_response`：content 归一 list——`None or "" → []`，str → `[{"type":"text","text":x}]`，list 原样透传。
- `recorder.py:61` / `scheduler.py:130` `_record`：**透传不改代码**，`result["content"]` 归一后自动是 list（记录值随归一变）。
- `router.py:17-19` `infer_modalities` 是输入侧 messages content 推断，与输出归一无关，不动。
- `cli.py:81-82` `_cmd_call` 非 raw 模式 print content 会打 list repr（遗留，未动）。
- 契约见 `design-cog-runtime-min.md` 2.3（`CuResultOk.content: list`）/ 4.1。

## 测试

- `tests/lm_service/`：`test_errors.py`(194) / `test_normalization.py`(115) / `test_recording.py`(210) / `test_router.py`(171)。
- mock 手段：monkeypatch `scheduler.PROVIDER_REGISTRY`（或 `ProviderBase.chat_completion`）——服务端侧 mock，零网络零账号。

## 关键约定

- 命名三层：模块 `cogos.lm_service`（下划线）/ 命令 `cogos-lm-service`（连字符）/ 目录 `~/.cogos/lm-service/`（连字符）。
- 错误：`category` 字符串枚举六类（retryable/auth/quota/content/semantic/invalid_request）；错误响应 `{"error":{"category","message"}}`；客户端抛 `LmServiceError(category, message)`。
- 冻结契约：`LmClient.chat(messages, tier, must)` → 归一响应 + 失败抛 `LmServiceError(category)`（本次 task-3 在此契约上做三处扩展，见 task 文件）。
