# 2026-08-17 — Telecom 通信接口实现（startup/send/listen/shutdown + term 迁移）

> 本体：`~/codex/cogos`（cogos 工程），提交 `88d34d4`
> 入口：`cogos-feishu <command>`（`python3.11 -m cogos.feishu.cli`）
> 测试：`python3.11 -m pytest tests/ -q`
> 工作方式：YZ 主导、逐接口派活，AI 实现。

## 一、本会话已确认的关键结论

- **号码 ↔ 飞书 id 对应**：
  - H 号（真人）↔ `user_id`
  - A 号（agent）↔ `app_id`（**不是 open_id**）
- **反查**：
  - `user_id → H 号`：没问题，属于已通的真人互通范围。
  - `app_id → A 号`：走 `AgentConnManager.get_by_app_id`（已存在）。
  - `open_id`：不用于反查，不碰。
- 入站消息 `event.sender.sender_id` 含三字段（`open_id`/`union_id`/`user_id`），真人消息能拿到 `user_id`；群里 bot 消息只有 `open_id`，其 A 号身份靠 `evt.app_id` 定位。
- **动手原则**：只有清楚讨论过的才动手，没方案的留空，与 YZ 讨论出方案后再动手。

## 二、接口定稿（TelecomClient ABC）

文件 `cogos/feishu/telecom.py`（ABC + 数据模型 + 异常；`FeishuTelecomClient` 已实现 startup/send/listen/shutdown）。

- `Contact`（frozen）：`number`（`COGOS001:H0002` / `COGOS001:A0001`，H=人 A=agent）+ `name`。
- `Chat`（frozen）：`id`（opaque，群 `oc_xxx` / P2P chat_id）+ `title`。
- `startup() -> Contact`：连 daemon、验证号码+pin，返回核实后身份，失败抛 `StartupError`。
- `send(target, msg, to_targets=None) -> None`：非阻塞 fire-and-forget；P2P target=Contact、群 target=Chat。
- `listen(on_msg, on_disconnect=None) -> None`：起 reader+heartbeat 后台 task 立即返回。
- `shutdown() -> None`：幂等。
- 回调 `on_msg(chat, contact_from, msg, contact_to)`；`on_disconnect()`。
- 异常：`TelecomError → StartupError / SendError(reason, code) / ConnectionLost`。

## 三、现状盘点（关键文件，反映当前代码状态）

- `cogos/feishu/telecom.py` — 接口层 ABC + `Contact`/`Chat` + 异常 + `FeishuTelecomClient`。**已实现** startup/send/listen/shutdown。`AGENT_HB_INTERVAL=15.0` 已迁入本文件。
- `cogos/feishu/term.py` — agent 交互终端，`main` 已改用 `FeishuTelecomClient`（startup/send/listen/shutdown），删手写 proto 与 reader/heartbeat task。
- `cogos/feishu/daemon.py` — `_handle_agent_client` 长连接（鉴权/踢旧/心跳超时/重校验），`startup_ack` 已带 `name`；`_handle_agent_send` **仍只收 H 号 p2p**（`AccountRef.from_number` 判 `HumanRef`），群聊发不出去。
- `cogos/feishu/protocol.py` — `proto.agent` 8 消息：`startup`/`startup_ack`/`hb_req`/`hb_ack`/`send`/`send_ack`/`message`/`shutdown`。`startup_ack(result, name)`、`message(frm, name, content, entry)` 已改多参。
- `cogos/feishu/agent_conn.py` — `AgentConn`（`bot_id = f"{provider}-{number}"`、`route_message` 已改 async：group 忽略 / p2p 取 user_id 反查）；module 级 `_human_cache[provider][user_id]=HumanRef`；`AgentConnManager`（`_by_key`/`_by_app_id`）。
- `cogos/feishu/handler.py` — `handle_agent` 用 `manager.get_by_app_id(evt.app_id)` 路由，`loop.create_task(异步 route + send)`。
- `cogos/feishu/entry.py` — `MessageReceived.sender` 是 `Person(open_id, union_id, user_id, type, name)`；`chat_type` 取值 `"p2p"`/`"group"`；`_parse_message_event` 里 `sender_id = event.sender.sender_id`。
- `cogos/feishu/session.py` — `Session(bot, chat_id=None, receive_id=None, receive_id_type=None)`；`send_text(content, at_users=None)`。
- `cogos/feishu/accounts.py` — `AccountRef`（三级缓存）+ `AgentRef`（`required_fields` 含 `app_id`）+ `HumanRef`（`required_fields = ("user_id", "status")`）；`agent_account_id(provider, number) = f"{provider}-{number}"`。易错：`AccountRef.key` = 全名 `"provider:number"`（如 `COGOS001:H0002`，`route_message` 用它作 `from`）；`HumanRef(f"{provider}:{number}")` 直接构造（不经 `from_number` 工厂）。

## 四、动手范围与留空

- **已通**：term↔daemon 真人互通 —— `FeishuTelecomClient` 四方法 + term.py 迁移 + daemon 发送路径（p2p human）均已落地。
- **留空 / 待讨论**：群聊 send（target=Chat）、`to_targets` @、群内收 bot 消息的 app_id 反查链路；`SendError` 的具体触发面。
- **既有行为（未讨论，非本次改动）**：`daemon._handle_agent_send` 发送失败时 `raise e` 会传播到 `_handle_agent_client` 的 finally 导致 agent 断连。

## 五、listen 接口修改点（已讨论定稿并实现）

**事实前提**：飞书 bot 自己的消息不会从 WS 回显，`lib.send` 直接返回发送结果；WS 收不到自己消息，故 route_message 无需过滤自己消息。`entry.chat_type` 取值 `"p2p"` / `"group"`。

**daemon 侧（反查在 daemon）**：
- 新增 `query_human_by_user_id(provider, user_id) -> fields | None`：参考 `bs_agent.query_agent_fields` 模式，`filter=CurrentValue.[user_id]="..."`，查 `human_registry`。
- 反查缓存：module 级 `cache[provider].human[user_id] = HumanRef`（只存 `HumanRef`，不存 ts）。命中则 `await ref.ensure()`，空 → 忽略消息（号码可能 inactive）；未命中 → `query_human_by_user_id` 得 `number` 构造 `HumanRef` 入缓存。过期/失效判断全部交给 `ensure()` 内部（三级缓存 + TTL），外层不重读 bitable。`provider` 取自 `self.ref.provider`。
- `AgentConn.route_message` 改 async（反查需 await bitable）：非 `MessageReceived` → None；`chat_type == "group"` → None；p2p 取 `sender.user_id` 反查 → `number` + `name`；查不到/失效 → None；返回 `proto.agent.message(number, content, asdict(entry), name)`。
- `handler.handle_agent` 改为 `loop.create_task(异步 route + send)`。

**protocol 侧**：`proto.agent.message` 增加 `from_name` 字段（from 填 `COGOS001:H0002` 全名，name 单独带回）。

**client 侧（telecom）**：
- `__init__` 设空 `_on_msg`/`_on_disconnect`；`startup` 成功时调 `_do_listen`；`listen(on_msg, on_disconnect)` 只重设回调。
- `_do_listen` 起 reader + heartbeat 两 task；reader 分发：`message` → `on_msg(Chat(id=entry.chat_id, title=""), Contact(number=from, name=from_name), content, [])`；`send-ack`/`hb-ack` 忽略；`sock.read()` 返回 None → `on_disconnect()` 并退出。

**未来扩展（留待群功能）**：缓存结构可能扩展为 `cache[provider].agent[open_id]`（群内 bot 消息的 A 号反查），当前只实现 `human[user_id]`。

## 六、实现进度

（逐个接口，每完成一个在此追加一行说明 + 状态）

- [x] `FeishuTelecomClient.startup` — 完成。`__init__(self, contact, pin)`；startup 走 `client.agent_connect()` → `proto.agent.startup(ref, pin)` → 读 ack，非 ok 抛 `StartupError`；成功存 `self._sock` 并返回 `Contact(number=ref, name=ack["name"])`（name 权威）。daemon 侧 `startup_ack` 增加 `name` 字段（`account.get("name","")`），`proto.agent.startup_ack(result, name)` 改双参；同步更新 test_protocol/test_daemon。
- [x] `FeishuTelecomClient.send`（p2p human 路径）— 完成。前置校验：未 startup → `SendError("not started")`、空 msg → `SendError("empty message")`、`Chat` → `NotImplementedError`、A 号目标 → `NotImplementedError`；H 号走 `proto.agent.send(target.number, msg)` fire-and-forget，不读 send_ack。daemon 侧无需改。
- [x] `FeishuTelecomClient.listen` + daemon 反查 — 完成。`__init__` 设空回调；`startup` 成功调 `_do_listen`（起 reader + heartbeat，`AGENT_HB_INTERVAL=15`）；`listen` 只重设回调。reader：`message` → `on_msg(Chat(id=chat_id), Contact(number=from, name=from_name), content, [])`，send-ack/hb-ack 忽略，read None → on_disconnect。daemon 侧：`bs_agent.query_human_by_user_id`（filter user_id 查 human_registry）+ `agent_conn._human_cache[provider][user_id]=HumanRef`（无 ts，失效交给 ensure()）+ `route_message` 改 async（group 忽略、p2p 取 user_id 反查、ensure 空忽略、返回 `message(ref.key, name, ...)`）+ `handler.handle_agent` 改 `loop.create_task(异步 route+send)`。`proto.agent.message(frm, name, content, entry)` 加 `from_name`。同步更新 test_protocol。
- [x] `FeishuTelecomClient.shutdown` — 完成。幂等（`_sock is None` 短路）；顺序：置 `_sock=None` → 写 `proto.agent.shutdown()`（吞异常）→ cancel 并 await 回收 reader/heartbeat 两 task（吞 CancelledError/Exception）→ `sock.close()`。主动关闭不触发 `on_disconnect`。daemon/protocol 无需改（`proto.agent.shutdown()` 已有 + `test_shutdown_removes_from_registry` 已测）。
- [x] daemon 发送路径适配 — 完成。`startup_ack` 带身份（name）已随 startup 完成；send 语义无需改（`_handle_agent_send` 已支持 H 号 p2p）。
- [x] term.py 迁移 — 完成。`main` 改用 `FeishuTelecomClient`：连接段 `Contact(number=args.agent)` + `startup()`（catch `StartupError`）；`/send` 走 `client.send(Contact(number=parts[0]), content)`（catch `SendError`/`NotImplementedError`）；`/quit`/`/exit` 走 `client.shutdown()`；`listen(on_msg, on_disconnect)` 接管收发（on_msg 显示 `name or number`，on_disconnect 提示并 `term.exit()`）；`finally` 只 `await client.shutdown()`（幂等）。删 `asyncio`/`client`/`proto`/`AGENT_HB_INTERVAL` imports 及 tasks/add_task/cancel_tasks/reader/heartbeat。行为变化：send-ack 显示消失（fire-and-forget）。

## 七、本会话改动记录与验证

已改动文件（startup/send/listen/shutdown/term 迁移五步，均已测试通过）：

- `cogos/feishu/telecom.py` — `FeishuTelecomClient` 实现 startup/send/listen + 空回调 + `_do_listen`/`_reader`/`_heartbeat`
- `cogos/feishu/term.py` — `main` 迁移到 `FeishuTelecomClient`，删手写 proto/reader/heartbeat
- `cogos/feishu/protocol.py` — `startup_ack(result, name)`；`message(frm, name, content, entry)` 加 `from_name`
- `cogos/feishu/daemon.py` — `startup_ack("ok", account.get("name",""))`
- `cogos/feishu/bs_agent.py` — 新增 `query_human_by_user_id`
- `cogos/feishu/agent_conn.py` — `_human_cache` + `route_message` 改 async
- `cogos/feishu/handler.py` — `handle_agent` 改 `loop.create_task(异步 route+send)`
- `tests/feishu/test_protocol.py`、`tests/feishu/test_daemon.py` — 同步新签名

验证：term 迁移步 —— term/protocol/daemon 61 passed；全量 456 passed / 1 failed（唯一失败 `test_workdir_switch`，环境残留 daemon 进程 expected 1 got 2，与改动无关）。

下一步（待 YZ 派活）：群聊 send（target=Chat）+ `to_targets` @ + 群内 bot 消息 app_id 反查链路（见「四、留空」）。
