# 群聊（Telecom 真群）方案定稿 + 1-4 实施

> 2026-08-20~21 会话。方案已与 YZ 讨论定稿，块 1-3（协议帧 / 数据模型 / agent 侧）已落代码；块 4（daemon handler + add_members 编排）2026-08-21 会话已实施。均未提交。块 5-6 待接。真机验证两行为点已确认（见下）。本体方案文档：`~/codex/cogos/docs/group-chat-telecom.md`；块 4 实现细节 → entries/2026-08-21-cogos-group-chat-block4.md。

## 目标

Telecom 层真群（多成员）能力，agent 视角接口：

```python
chat = await client.create_chat(name)     # -> Chat
await chat.add_members([Contact])         # 透明编排，不感知中间过程
members = await chat.get_members()        # -> list[Contact]（真人+bot）
```

接收仍走 `client.listen(on_msg)`，on_msg 收 `Message` 对象。

## 已定方案（讨论结论）

- **Chat 从 frozen dataclass → 普通类**：字段 `id`/`name`/`client`（title→name，与飞书 create_chat 的 `name` 一致）；`client` 记录所属 TelecomClient；方法 `add_members`/`get_members` 委托 `client._add_members`/`_get_members`。
- **OnMsg 结构化**：`OnMsg = Callable[[Message], Awaitable[None]]`。`Message` = `sender: Contact` / `content: str` / `time: str`（毫秒串，透传 entry.time）/ `chat: Chat|None` / `mentions: list[Contact]` / `entry: dict`（兜底）。**显式字段由 daemon 填充，agent 不抠 entry**；entry 只作兜底。**p2p 与 group-p2p 的 chat/mentions 均为空**（group-p2p 对 agent 是 p2p，sender 即对端）。
- **add_members 透明编排**（daemon 内部，Chat 不感知）：真人用群主 bot 身份 `add_members`（user_id）拉；bot 成员用各自账号 `me_join`（需 public 群）→ 编排「拉真人 → 改 public → 逐个 bot me_join（等待）→ 改回 private」。**约束**：飞书 app 拉 app bot 被封（invite 230003），所以 agent 成员只能 me_join，不能 add_members 拉。
- **get_members**：真人走 `core.list_members`（只含真人）；bot 成员走**历史增量拉取 + 解析进群/退群 system 消息**（群成员 API 只返回真人，bot 成员无法实时）。**进群/退群实时公告协议（`/ENTER` `/REMOVE` `/EXIT`）不实现，写 ISSUES 作遗留**——因退群有缺口（bot 被移除后无法发公告）+ 依赖真人走命令（易碎），历史解析是观测事实更可靠。
- **进群/退群事件**（若后续暴露给 agent）：只报 who 不报 operator，简化。

## 1-3 已实施（未提交）

- `cogos/feishu/protocol.py`：`proto.agent` 新增 `create_chat`/`add_members`/`get_members` + `*_ack`（ack 带 `request_id`）；`send_chat` 帧 `title`→`name`；docstring 补协议说明。
- `cogos/feishu/telecom.py`：`Chat` 普通类；`Message` frozen dataclass；`OnMsg` 类型改 Message；`TelecomClient` ABC 加 `create_chat`/`_add_members`/`_get_members` 抽象；`FeishuTelecomClient` 加请求-响应机制（`_request` 注入 `request_id` + `_pending` Future + `_handle_ack`；`REQUEST_TIMEOUT=30`；`_ACK_TYPES`）、`create_chat`/`_add_members`/`_get_members` 实现、`_reader` 把 message 帧转 `Message`（`_to_message`：time 优先 `msg["time"]` 否则 `entry["time"]`；`chat_type=="group"` 才构造 Chat；mentions 从 `msg["mentions"]` 解析）。
- `cogos/feishu/term.py`：`on_msg` 适配 Message 对象（`msg.sender.number`/`msg.time`/`msg.content`）。
- `tests/feishu/test_protocol.py` 新帧测试 + `tests/feishu/test_telecom.py`（Chat 委托/Message/_to_message/_request/create_chat/get_members）。

**测试**：`test_protocol`+`test_term`+`test_telecom` = 51 passed；`test_daemon`+`test_client`+`test_entry`+`test_session` = 156 passed。全量 `pytest tests/` 会超时 120s（既有慢集成测试，与本次无关）。

## 5-6 待实施

### 块 4：daemon 侧命令处理（`daemon.py`）— 已实施（2026-08-21，未提交）

实现细节、修改思路、关键代码路径见 entries/2026-08-21-cogos-group-chat-block4.md。要点：

- 四 handler 均已实现并接线读帧循环（`create_chat`/`add_members`/`get_members`/`send_chat`），回对应 `*_ack`（带同一 `request_id`）。
- `_handle_agent_create_chat`：`Lib.create_chat`（群主 bot 建 private 群）→ `_write_group_meta` 写 session.json `chat_type:group` → ack。
- `_handle_agent_add_members`：解析 numbers 分真人/agent → **复用 `groupmgr.Chat.add`**（群主拉真人 → 改 public → 逐个 bot me_join → 改回 private）；**同步 ack**（先同步，慢群再改异步）。
- `_handle_agent_get_members`：真人 `list_members` + `_resolve_human`；bot 成员待块 6。
- `_handle_agent_send_chat`：发群消息 + @（真人 `user_open_id` 转换）；bot @ 待块 5。

### 块 5：真群 sender/mentions 解析（`agent_conn.route_message`）

`route_message` 现有分支：`MessageSent` 回显 / `MessageReceived` 按 `chat_type` 分派（`p2p`→`_resolve_human_sender`（entry.sender.user_id→H）、`group-p2p`→`_resolve_group_p2p_sender`（meta peer_number→A））。**缺真群 `group` 分支**：

- 真人 sender：群里 `entry.sender` 可能是 **open_id**（per-app，需 `GET /contact/v3/users/{open_id}?user_id_type=open_id` 转 user_id→H）；p2p 里是 user_id。**待真机确认** WS 群消息 `sender.sender_id` 到底带不带 user_id。
- bot sender：`entry.sender.sender_type=="app"` → app_id → agent_registry 查 A 号码。
- mentions 同链路（open_id→H / app_id→A）。
- 组装 `Message` 时 daemon 显式填 `time`/`chat_id`/`chat_name`/`mentions`（`proto.agent.message` 目前只有 `from`/`from_name`/`content`/`entry`，需扩展 message 帧或另加字段）。

### 块 6：历史解析模块（新文件，供 get_members 的 bot 成员）

把 `scripts/exp_group_history.py` 结论固化（见 entries/2026-08-20-cogos-group-history.md + `docs/feishu-group-history.md`）：

- tenant token：`POST /auth/v3/tenant_access_token/internal`（app_id/app_secret）。
- 增量拉取：`GET /im/v1/messages`（`container_id_type=chat` + `container_id` + `sort_type=ByCreateTimeAsc`），记上次 `create_time`(ms)+`message_position`，`start_time = create_time/1000 - margin`，`position > 上次` 去重。**冷启动无基线 → 全量拉**。
- 解析 system 消息：`{from_user} invited {to_chatters}` / `{from_user} removed {to_chatters}`；bot me_join 特征 `from_user == to_chatters`；bot 身份从展示名 `名字(Axxxx)` 反查 agent_registry 补 app_id。
- 只解析 provider 名录内的真人和 bot，其余静默跳过。

## 真机验证结论（2026-08-21 已确认）

1. 非 owner bot（未进群）`add_members` 拉真人 → `232011 Operator can NOT be out of the chat`，失败。只能用群主 bot 拉真人（v1 方案维持，群主=建群的 agent 自己 bot）。
2. 群消息 WS 事件 `sender.sender_id` **同时带 `open_id` + `union_id` + `user_id`**（真人 YZ 发消息，`user_id` 直接可得）。块 5 无需 open_id→user_id 转换。

## 新会话提示词

```
继续 cogos 群聊（Telecom）实现。先加载 locus 记忆 projects/cogos/current.md + entries/2026-08-20-cogos-group-chat-telecom.md + entries/2026-08-21-cogos-group-chat-block4.md + 本体 ~/codex/cogos/docs/group-chat-telecom.md。块 1-4 已完成（代码未提交）。从块 5 开始：route_message 真群 group 分支（真人 sender user_id→H 已确认无需转换 / bot app_id→A / mentions 解析）+ proto.agent.message 帧扩展 time/chat_id/chat_name/mentions。块 6 历史解析模块（get_members 的 bot 成员）。
```
