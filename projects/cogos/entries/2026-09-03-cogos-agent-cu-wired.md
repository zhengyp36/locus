# agent 接 cu 实施（09-03）

> 起因：terminal+timer e2e 暴露 agent 层 oneshot 无续轮，LLM 只调 terminal_open 就停。方案收敛见 `2026-09-03-cogos-agent-cu-wiring.md`，本条目记实施结果。

## 改动

- `cogos/cog_runtime/runtime.py`
  - `CogRuntime.__init__` 加 `client=None` 注入（`client or LmClient(internal_key)`），供 agent/demo/单测注入假 client。
  - `_advance` 的 `on_tool_call` 加 try/except：抛异常 → `CuResultError("tool_error")`（原会悬挂，`_done_event` 永不 set）。
- `cogos/agent/consciousness.py` 重构
  - `__init__(registry, runtime, profile, toolset_names=None, context=None)`：换 lm_client 为 CogRuntime，持 `self._context`（默认写入 system 身份）+ `asyncio.Lock`。
  - `on_message`：`async with self._lock` 串行 → append user → `runtime.cu(material=self._context, tier="basic", tools=schemas, callbacks={on_tool_call, on_done})` → `await cu.wait()`。
  - `on_tool_call`：闭包计数 rounds，超 `MAX_TOOL_ROUNDS=10` 则 `cu.interrupt("max_tool_rounds")` 返回 `[]`（interrupt 后 `_advance` 循环开头检查，不走 append，无孤儿 tool_calls）；否则逐个 `registry.call` 返回结果 list（dict 被 `_vendor_tool_message` 转 json）。同时记录是否调过 `send_msg`。
  - `on_done` → `_handle_done`：`CuResultOk` 补 assistant 到 context + 兜底 send_msg（text 非空 + source != system + 本轮未 send_msg）；`CuResultError` log + 非 system 告知；`CuResultInterrupted` log。
- `cogos/agent/app.py`
  - `Agent.__init__`：`lm_client=None` 时 `CogRuntime(os.environ["LM_INTERNAL_KEY"])`，否则 `CogRuntime("", client=lm_client)`；持 `self._context = [system]` 传 Consciousness。
  - `_DemoLmClient` 改有状态（首轮 tool_calls、次轮纯文本），避免无限循环。

## 关键决策

- context 是 agent 对象：Agent 持 `self._context`，Consciousness 收引用；cu 用完即丢，material 留 agent。
- 串行用 `asyncio.Lock` 而非单 consumer 队列：perception 直连 on_message 未改，p2p / event 两条路径靠锁串行（最小改动；entries 里的"单 consumer"是理想架构）。
- 事件用 user 角色 append（唤醒行动），内容层已标 `[来源: system]` 区分不回复。
- send_msg 语义：从"无 tool_calls 自动发"改为"LLM 用工具自主发 + on_done 兜底"。
- tier 显式 basic。

## 验证

- 全量 pytest 886 passed（+3：`test_tool_call_exception_finishes_error`、`test_on_message_multi_round_tools`、`test_on_message_system_event_no_reply`），无回归。
- 真实 deepseek e2e（fake phone + 真 lm-service）：deliver `sleep 3 && echo hello_done`，6.73s 返回，terminal_open→exec→observe→send_msg 完整闭环；terminal_done 事件回传成第二轮 user 消息，LLM observe 后汇报输出。context roles 呈 `system, user, [assistant,tool]×N, user(事件), assistant`。

## 遗留

- 上下文无限增长压缩/截断未做（MVP 暂缓，待 YZ 提方向）。
- 串行靠锁，未来若上多认知层再迁单 consumer 队列。
