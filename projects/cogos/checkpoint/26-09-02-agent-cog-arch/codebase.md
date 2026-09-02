# codebase.md — 对 cogos 代码的当前认知

> 活文档，就地改。记「对代码的当前认知」：`文件:行` + 关键逻辑一句，供新会话快速定位。代码/路径/变量英文，讨论结论可中文。

## 工程入口

- 本体：`../cogos`。语言 Python 3.11。测试：`python3.11 -m pytest tests/ -q`。
- 包结构：`cogos/feishu/`（通信层）、`cogos/phone/`（agent 通信抽象）、`cogos/lm_service/`（LLM 服务）、`cogos/cog_runtime/`（cu 状态机）、`cogos/agent/`（agent 认知：config/perception/consciousness/tools/app）。

## phone（agent 通信抽象，本次架子主要用这个）

- `cogos/phone/phone.py:52-56` — `Phone(config_path, client_factory=...)`，`client_factory` 可注入 `FakeTelecomClient` 实现离线跑。
- `cogos/phone/phone.py:115-127` — `add_card(number, pin)` 第一张卡自动 default；pin 非空（fake 下空串 → `status=failed`）。
- `cogos/phone/phone.py:129-144` — `_connect_card`：startup 失败则标记 `failed` 并 return（client 不进 `_clients`）；成功则注册进 `_clients` 并 `_register_listeners` 补回调。
- `cogos/phone/phone.py:165-190` — 通讯录：`add_contact(name, [numbers])` / `get_contact(name)` / `contacts()`。
- `cogos/phone/phone.py:192-215` — `send(target, content)`，target 可名字/号码/Chat。
- `cogos/phone/phone.py:396-405` — `listen(on_msg=...)`，回调签名 `on_msg(chat, from_, msg, to)`；遍历 `_clients` 调 `_register_listeners`。
- `cogos/phone/phone.py:406-414` — `_register_listeners(number, client)`：给单个 client 挂 `_make_on_msg`/disconnect/error/members_changed 回调。
- `cogos/phone/phone.py:442-478` — `_make_on_msg`：`message.chat is not None` 判定群聊；`message.sender.number == card_number` 过滤自己发的；群聊会 `_substitute_mentions` 把 @ 替换进文本（丢原始 mentions 结构）。
- `cogos/phone/phone.py:525-534` — `_dispatch` 调 `on_msg(chat, from_number, content, to_number)`：**`msg` 是字符串 content，不是 Msg 对象**；`from_`/`to` 是 `Number`。
- `cogos/phone/phone.py:536-550` — `sessions(type=)`；`Chat.history()` / `Chat.incoming()` 读消息（`model.py:60-80`）。
- `cogos/phone/phone.py:647-671` — `reconnect`：`num not in self._clients` 走 `_connect_card` 新建 client（已自动补 listener）；已有 client 直接 `startup()`。

## fake client（离线测试）

- `cogos/phone/fake.py:14-45` — `FakeTelecomClient(contact, pin)`，`startup()` 要求 pin 非空。
- `cogos/phone/fake.py:47-55` — `send()` echo 回 `_on_msg(echo)`，echo sender = 自己（会被 phone 的 `_make_on_msg` 过滤掉）。
- `cogos/phone/fake.py:110-111` — `deliver(TMessage)` 手动投递消息触发 on_msg——**离线模拟「收到消息」的标准方式**。
- `cogos/phone/fake.py:92-108` — `listen()` 只设置回调，不阻塞。

## phone 测试范式（新会话照抄）

- `cogos/tests/phone/test_phone.py:13-17` — `Phone(config_path=str(tmp_path/"phone.json"), client_factory=FakeTelecomClient)`。（实际测试根目录是 `tests/`，非 `cogos/tests/`。）
- `cogos/tests/phone/test_phone.py:162-180` — `listen(on_msg)` + `client.deliver(TMessage(sender=TContact(number="..."), content=..., time=...))` 触发收消息，断言 on_msg 收到 `(chat, from_, msg, to)`。

## lm_service（意识层已接 LmClient）

- `cogos/lm_service/client.py:34-46` — `LmClient(internal_key).chat(messages, *, temperature, max_tokens, thinking, tier, tools)`，返回归一响应（content 是 list、可选 tool_calls、reasoning）。internal_key 真实模式从环境变量 `LM_INTERNAL_KEY` 读。
- `cogos/lm_service/providers/deepseek.py:23-29` — thinking 传 `{"enabled": bool}`。

## cog_runtime（架子阶段不碰）

- `cogos/cog_runtime/runtime.py:54-133` — CogUnit 状态机 + 工具循环；无 tool_calls 就 finish。本次架子不套它。

## agent（意识层第一期 + 工具层两期已实施：身份认知 + 真实 LLM 回复 + 读写执行 + 上网）

- `cogos/agent/message.py` — `IncomingMessage(chat_type, source, content, time="", members=[], mentions=[])`，统一消息对象。
- `cogos/agent/config.py` — `ContactInfo(name, number)` / `Profile(name, phone_number, contacts, pin="")`（`name_for(number)` 号码→名字，未知回号码本身）/ `AgentConfig(memory_dir, phone_dir, work_dir)`。`load_agent_config(agent_dir)` 读 `agent.json`（`memory_dir`/`phone_dir`/`work_dir` 相对路径基于 agent_dir，`work_dir` 默认 `"work"`）；`load_profile(memory_dir)` 读 `<memory_dir>/profile.md`（YAML，含可选 `pin`）。`init_phone(phone, profile)` **幂等**装卡+建联系人：`any(str(c.number)==profile.phone_number for c in phone.cards())` 为 False 才 `add_card`（pin 用 `profile.pin or "pin"`，真实 pin 从 accounts `bot-<num>.json` 取）；`get_contact(name)` 空才 `add_contact`。`render_system_prompt(profile)` 产身份+当前时间+通讯录+六工具清单。
- `cogos/agent/tools.py` — `ToolSpec(schema, fn)` + `ToolRegistry`；`make_send_msg_spec(phone)` 造 send_msg 工具（`parameters` 含 target/content required）。`registry.schemas(names)` 动态组合工具集；`registry.call(name, args)` 执行并捕获异常 → `{"ok":True}` / `{"ok":False,"reason":...}`，未知工具也回 `ok:False`。`make_read_file_spec(work_dir)` / `make_write_file_spec(work_dir)` / `make_execute_spec(work_dir, timeout=30.0)` 三个外设工具；`_resolve(work_dir, rel)` 用 `Path.is_relative_to` 拒绝绝对路径/`..` 逃逸；read 二进制检测+8000 截断、write 自动建父目录、execute shell+超时 kill+stdout/stderr 各 4000 截断。`make_search_spec()` / `make_fetch_spec()` 上网工具，fn 调 `webtools.search_web`/`fetch_url` 并原样透传结果。
- `cogos/agent/webtools.py` — `search_web(query, count=10, *, proxy=None)` 走 Brave Search API（`X-Subscription-Token` 头，web.results 空回退 discussions.results，count clamp 1..20，`_clean_html` 去标签+`html.unescape`）；`fetch_url(url, fmt="markdown", *, proxy=None)` 走 Jina Reader（`Authorization: Bearer`，fmt 非三值回退 markdown，401/402/429 特判，50000 截断+truncated）。key 从 `~/.secrets/{brave,jina}.key` 读，环境变量 `BRAVE_API_KEY`/`JINA_API_KEY` 覆盖；proxy 从 `KILO_PROXY` 读、兜底 `http://127.0.0.1:10809`。**aiohttp 默认 trust_env=False，必须显式传 `proxy=`**。
- `cogos/agent/consciousness.py` — `Consciousness(registry, lm_client, profile, toolset_names=六工具默认)`；`on_message(msg)` 组 `[system(render_system_prompt), user(_render_user)]` 调 `chat(messages=, tools=schemas)`；有 `tool_calls` 逐个 `registry.call(tc["name"], tc["args"])` 结果仅日志；无 tool_calls 但有 content 兜底 `registry.call("send_msg", {"target": msg.source, "content": text})`。`_render_user` 落 `[来源: 名字 (号码)] [时间: t]`（time 空→「未知时间」）。工具集口子：构造时注入名字列表。
- `cogos/agent/perception.py` — `Perception(phone, on_message)`；`_handle(chat, from_, msg, to)` 只处理 `chat.type=="p2p"`，用 `chat.history()[-1].time` 补消息时间（空则 `""`），产 `IncomingMessage` 推 `on_message`，群聊 return。
- `cogos/agent/app.py` — `Agent(agent_dir, client_factory=None, *, lm_client=None)`：读 config+profile → `config.work_dir.mkdir()` → `Phone(config.phone_dir/"phone.json")` → `ToolRegistry({send_msg/read_file/write_file/execute/search/fetch})` → `Consciousness`（lm_client 缺省 `LmClient(os.environ["LM_INTERNAL_KEY"])`）→ `Perception`。`init()` 调 `init_phone` + `phone.startup()`；`start()` 调 `perception.start()`。`__main__`：`--agent <dir>` 真实模式；无参 fake demo（临时 agent_dir + FakeTelecomClient + `_DemoLmClient`）。
- 依赖单向：app 组装；perception 回调推 consciousness；consciousness 持 registry + lm_client + profile；tools 持 phone；config 被 app 引用。各层只 import `message`/`config`。

## 边界说明

- telecom（`cogos/feishu/telecom.py`）是 phone 的底层，架子阶段只碰 phone 接口，不碰 telecom。
- **phone 的 `on_msg` 回调签名是 `(chat, from_number, content, to_number)`，不含 time**（`phone.py:521-530` `_dispatch`）。感知层已从 `chat.history()[-1].time` 补真实时间；仍可能空（`message.time` 空串），意识层 `_render_user` 兜底「未知时间」。

## 真实部署（真实验证用）

- agent 目录：`~/.cogos/agent/tangyu/`（`agent.json` + `memory/profile.md`），phone.json/phone-data 在 `~/.cogos/agent/tangyu/phone/`（由 `init_phone` 装卡自动生成）。
- 启动顺序：`cogos-feishu init`（daemon+monitor，systemd 模式）→ 后台 `python3.11 -m cogos.lm_service.cli server`（127.0.0.1:11434）→ `LM_INTERNAL_KEY=ik_... python3.11 -m cogos.agent.app --agent ~/.cogos/agent/tangyu`。
- internal_key `ik_c47WkfAw7E5v6Ck8idMHgg`（deepseek/尾号b111）；唐钰 pin `967b6fa7`。
- 验证产物：`~/.cogos/agent/tangyu/phone/phone-data/chats/<num>.json` 存 in/out 历史；`~/.cogos/lm-service/calls.jsonl` 存每次 chat 请求与 tool_calls。
- 工具层验证可走「不启动 agent」路径：起 lm-service server + `LmClient(ik)` + `ToolRegistry({send_msg(stub)/read_file/write_file/execute})` + 临时 work_dir，直接 `chat(messages, tools=schemas)` 拿 tool_calls 再 `registry.call` 执行。真实 LLM 已驱动三工具 PASS（`/tmp/kilo/verify_tools.py`，2026-09-01）。上网工具同理已 PASS：LLM 调 search（Brave 返回 asyncio 结果）+ fetch（Jina 抓 example.com）（`/tmp/kilo/verify_webtools.py`，2026-09-01，需代理可用）。
