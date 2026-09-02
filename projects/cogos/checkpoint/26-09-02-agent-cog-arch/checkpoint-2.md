# checkpoint-2 — agent 雏形架子实施完成（感知/意识/工具层，私聊假回复闭环）

> 实施 `agent-impl.md` 的架子。结果：一条 p2p 消息 → 意识层 echo 假回复 → 工具层 `phone.send` 发给来源。全量回归无回归。

## 当前问题

搭「感知层 → 意识层 → 工具层」最小架子，跑通「收到消息 → 回复一条」闭环。

## 已做修改

- `cogos/agent/__init__.py` — 空包。
- `cogos/agent/message.py` — `IncomingMessage` dataclass（chat_type/source/content/time/members/mentions）。
- `cogos/agent/perception.py` — `Perception(phone, on_message)`，`start()` 挂 `phone.listen`，`_handle` 只处理 p2p，群聊 return。
- `cogos/agent/consciousness.py` — `Consciousness(tools)`，`on_message` → `_reply`（`echo: {content}`）→ `tools.send_msg(msg.source, reply)`。
- `cogos/agent/tools.py` — `Tools(phone)`，`send_msg` 薄封装 `phone.send`。
- `cogos/agent/app.py` — `Agent(phone)` 组装；`__main__` fake 模式 deliver 一条消息打印闭环。
- `cogos/tests/agent/`（`__init__.py` + 5 个 test 文件）— 分层单测 + 集成闭环测试。

## 已读代码要点

- `phone.py:521-530` `_dispatch` — `on_msg(chat, from_number, content, to_number)`，**不含 time**；`content` 是字符串，`from_`/`to` 是 `Number`。
- `phone.py:438-473` `_make_on_msg` — p2p 走 `_ensure_p2p_session`；群聊 `message.chat is not None` 分支。
- `model.py:12-29` — `Number.from_str` 校验 `provider:number` 格式，`str(Number)` 还原字符串。
- `fake.py:110-111` `deliver(TMessage)` — 手动投递触发 on_msg；`fake.py:47-55` send echo 自己会被 phone 过滤，不会死循环。
- `tests/conftest.py` + `pyproject.toml:24-26` — `asyncio_mode="auto"`，async 测试无需 marker。

## 关键结论 / 决策

- 假回复用 `echo: {content}`，可断言回复内容正确，且是替换 LmClient 的洞。
- `IncomingMessage.time` 在感知层留空串（on_msg 回调不传 time），记录进 codebase.md，后续要真实时间从 `chat.history()[-1].time` 补。
- 三层 import 只依赖 `message.py`，无业务类交叉 import。

## 验证

- `python3.11 -m pytest tests/agent/ -q` → 9 passed。
- `python3.11 -m pytest tests/ -q` → 786 passed（无回归）。
- `python3.11 -m cogos.agent.app` → 打印 `received: hello -> replied: echo: hello`。

## 遗留 / 坑

- 意识层 `_reply` 是假回复，下一步接 `lm_service.LmClient` 替换。
- 群聊、元层时钟、场、折叠均未做（后续「细化意识层」阶段）。
- 感知层未做通讯录转名字（source 仍是 Number 字符串）。
