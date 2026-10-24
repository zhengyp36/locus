# cu.material 改造 list[dict] → list[Message]（2026-10-23）

## 结论（活跃）

`CogRuntime` 的 `cu.material` 从 `list[dict]`（internal-form 协议格式）改为 `list[Message]`（内部语义类型，带 `meta.ts`），出站转回 dict。已落码 `2fcac25`（16 files, +242/-123）。

- 载体：`cogos/cog_runtime/message.py`（`Message`/`Meta`）+ `runtime.py`/`unit.py` 适配 + 全部调用方与测试改 `Message`。

## 核心不变量

- `Message.to_lm_dict()` 输出与改造前 internal-form dict **完全等价**：provider 层 `assemble_tool_messages` 与 `FakeLmClient` 断言均不受影响（`fake_client.calls[i]["messages"]` 断言未改）。
- `meta` 不参与相等比较（`field(compare=False)`），测试断言忽略动态时间戳。

## 类型

- `Message(role, content, tool_calls, tool_call_id, reasoning, meta)`；`content` 按 role 分层：system/user/assistant = `str|list`（多模态 parts）、tool = `dict`（`{ok,result}` 包装），**不归一**、出站原样透传（tool 的 `json.dumps` 在 provider 层做）。
- `Meta.ts` = float epoch seconds，与 `Signal.at` 一致。

## 时间戳记录点（消息产生处记，append 复用，无差值）

| 消息 | 记录点 | ts 来源 |
|---|---|---|
| assistant | `await client.chat(...)` 返回后 | `cu._resp_ts = time.time()` |
| tool | `await on_tool_call(...)` 返回后 | `cu._tool_results_ts = time.time()` |

## 已定决策

- **彻底改、不做兼容层**：`cu(material=...)` 只接受 `list[Message]`。
- 类型名 `Message`（一条消息）/`Meta`（`meta.ts`），不用 `Context`/`ts`。
- `LmClient` 与 provider 层不动（frozen contract）。

## 边界（本次不做）

- 不落盘（版本号/`meta` 序列化到文件属后续意识上下文，见 `2026-10-24-cogos-consciousness-context.md`）。
- 不动 `LmClient` / provider / `cog_ctx`（`cog_ctx/context.py` 是另一套 `text` 字段消息）。
