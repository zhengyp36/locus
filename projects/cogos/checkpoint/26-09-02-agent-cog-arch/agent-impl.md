# agent 雏形架子 — 实施交接

> 目标：搭「感知层 → 意识层 → 工具层」最小架子，先做私聊，假回复，跑通「收到消息 → 回复一条」闭环。
> 设计主文档：`agent-prototype-design.md`。代码认知：`codebase.md`。

## 明确边界（不做的事）

- 不接 lm_service（意识层 `_reply` 用假回复，是换 LmClient 的洞）。
- 不碰 cog_runtime（状态机/场/元层是后续「细化意识层」阶段）。
- 不做群聊（只处理 p2p；`members`/`mentions` 字段留空当口子）。
- 不做元层时钟 / 场 / 折叠。

## 新包结构：`../cogos/cogos/agent/`

```
__init__.py
message.py        # IncomingMessage（统一消息对象）
perception.py     # 感知层：持 phone，listen on_msg → 产 IncomingMessage → 推意识层
consciousness.py  # 意识层：on_message(msg) → 生成回复 → 调工具
tools.py          # 工具层：send_msg(target, content)，薄封装 phone.send
app.py            # 组装：Phone(fake) + Tools + Consciousness + Perception + listen
```

依赖单向：`app` 组装一切；`perception` 回调推消息给 `consciousness`；`consciousness` 注入拿 `tools`；`tools` 持 phone。三层都 import `message`，彼此不 import 业务类。

## 接口契约

```python
# message.py
@dataclass
class IncomingMessage:
    chat_type: str        # "p2p"（先只处理这个）| "group"（口子）
    source: str           # 来源（Number 字符串；感知层查通讯录可转名字）
    content: str
    time: str
    members: list = None  # 口子，私聊恒空
    mentions: list = None # 口子，私聊恒空

# perception.py
class Perception:
    def __init__(self, phone, on_message): ...      # on_message 是意识层回调
    async def start(self): await self._phone.listen(on_msg=self._handle)
    # _handle(chat, from_, msg, to): 只处理 chat.type=="p2p"，产 IncomingMessage，调 on_message

# consciousness.py
class Consciousness:
    def __init__(self, tools): ...
    async def on_message(self, msg: IncomingMessage) -> None:
        reply = self._reply(msg)                     # 假回复：固定文本或 echo
        await self._tools.send_msg(msg.source, reply)

# tools.py
class Tools:
    def __init__(self, phone): ...
    async def send_msg(self, target, content) -> None:
        await self._phone.send(target, content)
```

## 关键实现细节（坑，务必照做）

1. `listen(on_msg)` 回调参数 `msg` 是**字符串 content**，不是 Msg 对象（`codebase.md` phone.py:521-530）。`from_`/`to` 是 `Number`。
2. 离线跑：`Phone(config_path, client_factory=FakeTelecomClient)`；config_path 用 tmp/临时目录，别污染真实 `phone.json`。
3. 装卡 pin 用任意非空字符串（如 `"pin"`）。
4. 测试「收到消息」用 `client.deliver(TMessage(sender=TContact(number="COGOS002:H0002"), content=..., time=...))`，**不要**靠 `send()` 的 echo（echo sender 是自己，被 phone 过滤）。
5. 感知层只处理 p2p：`chat.type == "p2p"`；来源取 `from_`（`Number`）。群聊分支先 return 或置空口子字段。
6. 意识层回复发给 `msg.source`（即 `from_` 的 Number 字符串），工具层 `phone.send(target, content)` 会按号码/名字发。

## 验证

1. pytest 单测（新文件 `cogos/tests/agent/test_*.py`，仿 `test_phone.py:13-17` 的 fake 注入）：注入 fake phone → deliver 一条 p2p 消息 → 断言 `Tools.send_msg` 被调、回复内容正确。
2. 全量回归：`python3.11 -m pytest tests/ -q`（无回归）。
3. （可选）`app.py` 提供 `__main__`：fake 模式下手动 deliver 一条消息，打印「收到 X → 回复 Y」。

## 完成标准

一条 p2p 消息进来 → 意识层生成假回复 → 工具层 `phone.send` 发给来源。pytest 通过 + 全量无回归。
