# codebase 认知基线（验证专用，append 式）

> 入口与关键锚点。每步验证对代码的新认知 append 到文末「## 新认知」。

## 入口

- 本体 `~/codex/cogos`；入口 `python3.11 -m cogos.feishu.cli`
- 测试 `python3.11 -m pytest tests/ -q`
- 数据 `~/.cogos/feishu/default/run/sessions`
- 账号 `~/.cogos/feishu/accounts/bot-<provider>-<number>.json`（含 `pin` 字段）、`human-<provider>-<number>.json`

## 关键文件

- `cogos/feishu/telecom.py` — `FeishuTelecomClient(contact, pin)`：`startup`/`send`/`Chat.send`/`create_chat`/`add_members`/`get_members`/`remove_members`/`leave`/`listen`/`shutdown`；数据模型 `Contact`/`Chat`/`Message`/`ALL`
- `cogos/feishu/daemon.py` — `_handle_agent_*` 系列 handler + `get_chat_owner` 群主解析三分支
- `cogos/feishu/agent_conn.py` — 三缓存 `_id_cache`/`_open_id_index`/`_user_id_index` + `resolve_id`/`resolve_number` + `route_message` + `get_tracker`
- `cogos/feishu/tracker.py` — `GroupMemberTracker`：`members.json` + `build`/`add_event`/`rebuild`
- `cogos/feishu/group_event.py` — `/ENTER` `/LEAVE` `/REMOVE` + `_do_leave`
- `cogos/feishu/agent_cmd.py` — 命令注册表 + `is_command`/`dispatch_command`
- `cogos/feishu/bs_agent.py` — `add_agent`/`add_human`/`activate_agent`/`refresh_contact` + contact.json 缓存
- `cogos/feishu/bs_setup.py` — 消息命令 `/setup` `/add-agent` `/activate` 等
- `cogos/feishu/bs_provider.py` — `setup_provider`/`resume_provider`
- `cogos/feishu/provider.py` — `cmd_setup_bs`

## 新认知

- `bs_provider.py:185` `_create_bitable_with_schema` — 建 bitable app + 7 表 + 写 COUNTER_RECORDS；`json_headers` 需本函数内定义（`_create_table` 只在自己作用域定义）
- `bs_provider.py:107` `_configure_admin_bot` — 加 scopes/设可见性/读飞书 app_name；返回 `bot_name` 是飞书应用名（带号码），非账号 name
- `bs_agent.py:265` `add_agent` — 分配号 → OAuth 建 app（on_url 提示命名「name(number)」）→ patch 权限 → 事件订阅 → 生成 pin → 写 agent_registry + contact bitable；账号 name 应为用户输入值，勿用 bot_name 覆盖
- `groupmgr.py:73` `Chat.add(humans, bots)` — 两个位置参数；拉 bot 用 `chat.add([], [peer_bot])`，勿只传一个（bs_agent.py:679 曾漏 bots）
- `bs_agent.py:592` `activate_agent` — 建 p2p 群（`_activate_agent_setup_p2p_group`，只对 lower-numbered peers）→ `/MEET` 收 open_id（`_collect_meet_openids`）→ `_activate_agent_finish` 写 contact bitable + agent_registry status=active + contact.json 缓存
- `bs_agent.py:855` `refresh_contact` — 手动刷新；从 max_idx+1 往上逐个拉 peer chat_id，遇未激活即停（连续区间）。无自动触发；新 bot 激活时天然收全 lower peers 无需刷新，仅先建 bot 需在新 bot 出现后刷新
- `daemon.py:284` agent startup 校验 `account.get("status")=="init"` → deny "account not active"；真机验证前须 `bs_agent.py:449 refresh_agent_account(provider, number)` 把本地账号同步成 active
- `accounts.py:388/415` `AccountRef._cache` 进程级内存缓存（`MEMORY_TTL=15*60`）；改本地账号文件后 daemon 未过期仍读旧值 → 需重启 daemon（`systemctl --user restart cogos-feishu-daemon`，DAEMON_MODE=systemd）
- `daemon.py:645 _handle_agent_get_members` — 只返回 human 成员（`_resolve_human`），bot 成员注释"block 6"未实现 → 纯 bot 群 `get_members()` 返回空；bot 成员观测点 = tracker 的 members.json
- `handler.py:41` — `MemberAdded`/`MemberRemoved` 走 `feed_member_event` → tracker.add_event，不走 route_message → agent on_msg **收不到**进群/退群 system 消息
- `daemon.py:209 _build_group_trackers` — agent startup 时 `list_chats` 遍历真实群（排除 contact.json 里的 group-p2p chat_id）逐个 build tracker → owner 重启后 members.json 才生成
- `groupmgr.py:44 create` register=True → `bs_agent.py:83 register_chat_info(chat_id, owner)` 写 chat_registry bitable（owner=provider:number）
- `accounts.py:418 ensure()` — 解析顺序 memory→local→cloud→hard fail；`available` 含 init（agent 专属，HumanRef 无 init）。本地 init 且未过期现会主动 `_refresh()` 云同步（他设备 activate 场景），失败 fail-open 退回 init；active 零额外开销
- `accounts.py:510 AgentRef._refresh()` — 查 agent_registry bitable merge 本地并 `_save_local` 写回 status/expires_at；cloud 无记录返回 {}，网络异常向上抛（调用方须 try）
- `daemon.py:652 _handle_agent_get_members` — human 走 API（`lib.list_members` user_id 类型 → `_resolve_human`）；bot 走 tracker `agent_numbers()` + `load_bot` 取 name；`get_tracker` try 包裹失败退回仅 human（fail-open）
- `tracker.py:286 GroupMemberTracker.agent_numbers()` — 公开访问器，返回 `sorted(_data["agent"].keys())`；`_data` 其余为私有，实时事件只改内存不落盘，唯一落盘点 `build()` 的 `_save()`
- `agent_conn.py:265 get_tracker` — LRU cache miss 才 new+build，命中直接返回；`_tracker_cache` 是 `AgentConn` 实例字段（:94），每次 startup 新建 conn 即重置（daemon.py:290），shutdown finally `manager.unregister` 丢弃对象 → 缓存随对象回收，无跨连接残留；close() 只关 sock 不清缓存
- `session_naming.py` — 物理布局 `SESSIONS_DIR/<app_id>/by_chat_id/<chat_id>/`；其上两个软链视图：`group/<name>`、`p2p/<Hxxxx>`（`ensure_chat_link`）+ `PROVIDERS_DIR/<provider>/<number> -> SESSIONS_DIR/<app_id>`（`ensure_provider_link`/`sync_provider_links`）；group-p2p 由 `fix_group_p2p` 提升进 p2p/
- `session.py:461 _sync_links` — `classify_chat` + `ensure_chat_link` + `ensure_provider_link`；只在 `_ensure_or_update_meta`（:384，处理 MessageReceived/MemberAdded/MemberRemoved/GroupDisbanded）时触发，建群流程不走 Session 故需在 `_handle_agent_create_chat` 补 `_link_group_chat`（daemon.py:417，构造 group meta → classify_chat → ensure_chat_link）
- `groupmgr.py:73 Chat.add(humans, bots)` — human 走 `_add_humans`（`lib.add_members` user_id + list_members 校验重试）；bot 走 `lib.join_chat`（me_join，用被拉 bot 自己的 app_id/app_secret），非 public 群先临时切 public 再切回 private
- `daemon.py:706 _handle_agent_get_members` — bot 段读 `conn.get_tracker(chat_id)` 前先 `await tracker.rebuild()`（否则读缓存滞后，add_members 后看不到新 bot）；`get_tracker`+`rebuild`+`agent_numbers` 整体 try 包裹 fail-open 空列表
- 关键机制：`im.chat.member.bot.added_v1` 事件只发给被拉 bot 自己的 app（me_join 的发起方）；`feed_member_event`（agent_conn.py:296）对 `is_bot` 只 `add_event(self.ref.number)` 更新该 bot 自己的 tracker，不更新群主/其它 bot 的 tracker。owner 的 members.json 收敛唯一靠 rebuild（`_replay_history` 解析 "{from_user} invited" 系统消息）；`/ENTER` 公告的发送端在代码中不存在（仅接收端 `_handle_enter`→`_rebuild`）

## 发送链路全貌

### P2P 发送
1. `Phone._send_p2p`（`cogos/phone/phone.py`）→ `client.send(TContact(number=...), msg)` 同步返回 `Message`。
2. `FeishuTelecomClient.send`（`cogos/feishu/telecom.py`）→ `_request(proto.agent.send(...))` 写 socket 帧并等 `send-ack`。
3. daemon `_handle_agent_send_p2p`（`cogos/feishu/daemon.py`）→ `session.send_text()` 同步 HTTP POST，拿到 `entry`（含 `message_id` + `time`=create_time）→ 回 `send-ack(ok, reason, request_id, message_id, time)` → `route_message(entry)` 异步回显。

### 群发送
同 p2p，走 `_send_chat` / `_handle_agent_send_chat`，`Chat.send` 委托 `client._send_chat`。

## 请求-响应机制（同步 RPC）

- `FeishuTelecomClient._request(payload)`：加 `request_id`（自增 `_request_seq`），写 socket，`create_future` 存 `self._pending[rid]`，`wait_for(REQUEST_TIMEOUT=30s)`。
- `_reader` 收帧：`mtype in _ACK_TYPES` → `_handle_ack(msg)` 按 `request_id` 匹配 future 并 `set_result`。
- `_ACK_TYPES = {create_chat_ack, add_members_ack, get_members_ack, remove_members_ack, leave_ack, send-ack}`（本次把 `send-ack` 收编进来）。
- 非 ack 的 `message` 帧 → `_to_message(msg)` → `on_msg`。

## 关键数据字段

- `Message`（telecom 数据模型）：`sender/content/time/chat/mentions/entry`；`time` 是 create_time 毫秒字符串。
- `session.send_text` 返回 `MessageSent` entry，`message_id` 来自飞书响应 `data.message_id`，`create_time` 来自 `data.create_time`（空时 fallback 本地时间）。
- `send-ack` 帧字段：`{ok, reason, request_id, message_id, time}`。

## Phone 落库与方向判定

- `Phone._append_msg(chat, direction, from_, to, content, time)`：消息内嵌 chat 文件，原子写。
- 发消息：`sent = await client.send(...)`，落 out 用 `sent.time or _now_ms()`。
- 收消息：`_make_on_msg` 里 `if message.sender.number == card_number: return` 跳过自己消息的回显；否则落 in 并 `_dispatch`。
- 会话产生惰性：`_ensure_p2p_session` / `_ensure_group_session`。

## 改动涉及文件（问题 1）

- `cogos/feishu/protocol.py` — `send_ack` 增字段。
- `cogos/feishu/daemon.py` — 两个 send handler 回带 message_id/time。
- `cogos/feishu/telecom.py` — `send`/`_send_chat` 同步化。
- `cogos/phone/fake.py` — 返回 Message（仍回显）。
- `cogos/phone/phone.py` — 落库用服务器时间。

## 测试

- `python3.11 -m pytest tests/`（默认 `python` 是 3.9，需用 `python3.11`）。
- `send-ack` 断言在 `tests/feishu/test_protocol.py`、`test_daemon.py`。

## 群成员变化链路（问题 2，已落地）

### 全貌
三个触发信号 → 统一入口 `AgentConn.emit_members_changed(chat_id)` → 重拉权威列表
diff → 推 `members_changed` 帧 → telecom `_reader` 识别 → `on_members_changed` 回调 →
Phone `_make_on_members_changed` 落库。

触发信号（都在 daemon 侧）：
1. 真人进退群：WS `user.added/deleted_v1` → `handler.handle_agent` →
   `conn.feed_member_event`（现在只调 `emit_members_changed`）。
2. 本 bot 进退群：WS `bot.added/deleted_v1` → 同上。
3. 其他 bot 进退群：/ENTER /LEAVE → `group_event._handle_enter/_leave` →
   `conn.emit_members_changed`。

### daemon 侧（关键）
- `AgentConn.resolve_group_members(chat_id) -> list[{number,name}]`：权威全量 =
  human（`list_members` + `_resolve_human`，仅已注册 human）+ bot（`tracker.rebuild()`
  + `agent_numbers()` + `load_bot` name）。`list_members` 失败 raise；tracker 失败降级。
- `AgentConn._members_snapshot: dict[chat_id, dict[number, name]]`，首次无快照推全量
  added，diff 出 added/removed，无变化不推。
- `AgentConn._read_group_name(chat_id)`：从 `session.json` 读 name（`Config.SESSIONS_DIR
  / app_id / BY_CHAT_ID / chat_id / session.json`），失败返回 ""。
- `_handle_agent_get_members`（`daemon.py:682`）复用 `resolve_group_members`，捕获
  list_members 异常回 `ack(False)`。

### telecom 侧
- `_ACK_TYPES` 不含 `members_changed`（非 ack、非 message）；`_reader` 单独分支识别，
  `_to_members_changed` 转 `(Chat, list[Contact], list[Contact])`。
- `OnMembersChanged = Callable[[Chat, list[Contact], list[Contact]], Awaitable[None]]`；
  `listen(on_members_changed=...)`。

### Phone 侧
- `Chat.members: list[str]`（`phone/model.py`），`chat_to_dict/from_dict` 序列化。
- `_make_on_members_changed(card_number)`：`_ensure_group_session` 后 `members =
  members - removed + added` 落库（`data["members"] = sorted(...)`）。
- Phone 无主动 `get_members`/`refresh_members`；初始成员靠 daemon 首次「全量 added」。

### 关键注意
- bot 与 human 在 Telecom 端无区别，diff 统一从权威列表得出，不信任事件
  `affected_users` 直接映射。
- tracker `_data["human"]` 快照只增不删，故 human 权威来源用 `list_members` API
  而非 tracker 的 human dict。

### tracker 历史回放的 system 消息模板（真机确认）
- `list_members` API 只返回真人、不含 bot → bot 成员权威来源完全依赖
  `tracker._on_history_msg` 对历史 system 消息的解析。
- 已识别模板（`startswith` 前缀匹配）：
  - `{from_user} started the group chat` → `from_user` 建群者 `enter`
  - `{from_user} invited` → `to_chatters` 被邀请者 `enter`
  - `{from_user} removed` → `to_chatters` 被移除者 `leave`
  - `{from_user} left the group` → `from_user` 主动退群者 `leave`（本次修复补上）
- bot 被 add_members 拉入群时，走 invited 分支按 `to_chatters` 识别。真机实测
  （checkpoint-15）：A0002 建群 add A0001 后，A0001 的 members 正确 =
  `{A0001, A0002}`，被拉入 bot 能按 `to_chatters` 识别。
- 号码解析：`_resolve_bot_number` 从展示名 `"名字(Axxxx)"` 抠号码，再 `load_bot`
  核对 name 一致才认。

## Phone 接入现状（集成前置认知）

- `Phone.__init__` 硬编码 `self._factory = FakeTelecomClient`（`phone/phone.py:46`），
  `add_card` 用 `self._factory(TContact(number=str(num)), pin)` 造 client → 全部走 fake，
  从未连真实 daemon。
- 真实 `FeishuTelecomClient` 目前只在 `feishu/term.py:98` 用过（`Contact(number=...)`
  + `_load_pin(number)` → `client.startup()`）。
- `FeishuTelecomClient.startup` → `client.agent_connect()` 连 `Config.SOCKET_PATH`
  unix socket → `proto.agent.startup(ref, pin)` → daemon `_handle_agent_client`
  （`daemon.py:250`）`verify_pin` + `ref.ensure()` + 查 `status=="init"` 拒绝未激活。
- fake 与真实的差异：fake `send` 立即 `_on_msg(echo)` 回显；真实 `send` 同步等
  `send-ack`，回显靠 daemon 异步 `route_message`。接通后 phone 的"自己消息按
  sender 跳过"（`phone.py:262`）才首次被真实数据验证。
- pin 来源参考：`term._load_pin(number)` 用 `AgentRef(number).ensure()` 拿 `account["pin"]`。

## 收消息链路：route_message 与 group-p2p 识别（checkpoint-10 新增）

### 收消息全貌
- 飞书 WS 事件 → `handler.handle_agent` → `conn.route_message(entry)` → 构造
  `proto.agent.message(from, name, content, asdict(entry), mentions)` 帧 →
  telecom `_reader` → `_to_message` → phone `_make_on_msg` 落库。
- `_to_message`（`telecom.py:438`）只看 `entry["chat_type"] == "group"` 才造
  `Chat`；否则 `message.chat = None`，phone 走 p2p 分支（`phone.py:279`），
  用 `message.sender.number` 做 p2p 会话 id。

### group-p2p（dual-bot group）识别
- 概念：bot↔bot 的 p2p 底层是飞书 dual-bot group（激活时 `bs_agent` 建的
  双人群）。飞书事件的 `chat_type` 对它仍是 `"group"`（不是 `"group-p2p"`）。
- `"group-p2p"` 标记只写在 `session.json` meta（`session_naming.py:247`
  `fix_group_p2p` 写 `meta["chat_type"] = GROUP_P2P`），用于文件系统 p2p/ 软链
  组织，**从没进过 entry**。
- 权威判断依据：`_load_contact_cache()` 返回的 `contacts[number].chat_id`
  （`bs_agent.load_contact_cache`），即每个 peer bot 的 dual-bot group chat_id。
  `_is_group_p2p(chat_id)`、`_resolve_group_sender`、`daemon.py:231` 三处都用它。
- `_resolve_group_sender`（`agent_conn.py:481`）：先用 chat_id 反查 contact cache
  命中即返回 peer 的 AgentRef；否则 fallback 到 `entry.sender` 的 open_id/user_id。

### route_message 的 chat_type 三分支（checkpoint-10 修复后）
- `chat_type == "p2p"`：真人 sender，`strip_at_all=False`，mentions 正常解析。
- `_is_group_p2p(chat_id)`：bot↔bot，`strip_at_all=True`（bot 在 dual-bot group
  靠 @all 通信，收消息剥 @all 前缀），`mentions=[]`，且把透传 entry 的
  `chat_type` 改成 `"p2p"` → 下游 telecom/phone 按 p2p 处理。
- 其余（真群）：`strip_at_all=True`，mentions 正常解析（`extra_all` 追加 `@all`）。
- 关键：`asdict(entry)` 透传前对 group-p2p 改 `entry_dict["chat_type"]="p2p"`，
  是让 telecom/phone 无需改动即正确落 p2p 会话的唯一转换点。

## 主动发送/建群/多卡与 dual-bot 方向约束（checkpoint-14 新增）

### Phone 发送 API 语义
- `Phone.create_group(title)`（`phone.py:335`）：default 卡 `client.create_chat(title)`，
  落库 `Chat(type="group", bound_card=default卡, title=tchat.name or title)`。
- `Phone.send(target, msg, from_number=None)`：`_send_p2p` 用
  `_resolve_send_card(from_number)` 选卡，落库 `from_=card.number`（=指定卡，非 default）；
  `_send_to_chat` 群发时 `bound = from_number or chat.bound_card`，落 out `from_=bound`。

### dual-bot p2p group 只对更低编号 agent 建立（重要约束）
- `_activate_agent_setup_p2p_group`（`bs_agent.py:622`）遍历所有 agent，仅
  `idx < self_idx`（编号更低）才 `Chat.create` 建双人群并写入自己 contact。
- 推论：A0002 的 contact 只有 A0001（更低），没有 A0003~A0005；高编号 bot 向更高
  编号 bot 发 p2p 会 `resolve_target` 抛 "target has no reachable address"。
- 故多卡/群发验证里，发送卡只能向"编号更低的 agent"发 p2p（或用真人 user_id）。

## 收消息链路：真群里 bot 发言被丢弃（checkpoint-11 新增）

### 现象（场景 7）
- A0002（bot）在真群 recv-group 里 `@_all` 发言，A0001 的 stream 已持久化
  `message_received`，但 phone 侧 on_msg 不触发、不落 in。

### 根因
- 飞书 `im.message.receive_v1` 对 bot 发送者返回 `sender.sender_type="bot"`。
- `entry._parse_message_event`（entry.py:216）只写
  `"app" if sender_type == "app" else "user"`，把 `"bot"` 误归 `"user"`，
  且 `user_id=""`（bot 无 user_id），open_id 被丢弃。
- `route_message` 的 group 分支走 `_resolve_group_sender`（agent_conn.py:489）：
  真群 chat_id 不在 contact cache（cache 只存 dual-bot group）→ `sender.type`
  非 "app" → `_resolve_human(provider, user_id="")` → None → `route_message`
  返回 None，消息静默丢弃。
- 关键点：`_resolve_group_sender` 对非 dual-bot 真群的 bot sender，只有
  `sender.type=="app"` 才会用 open_id `resolve_number`（触发 `_warm_agent_ids`
  加载 bot open_id→number 映射）；"user" 分支只走 user_id，bot 无 user_id 必失败。

### 与 group-p2p 的区别
- checkpoint-10 修 dual-bot group 的 chat_type 透传；本问题是真群 bot 发言的
  sender 解析失败，两条路径不同。

### 修复（checkpoint-11）
- `entry.py:216` sender_type 映射改为 `"app" if sender_type in ("app", "bot") else "user"`，
  把 receive_v1 的 `"bot"` 归入机器人（与 mentions 的 `mentioned_type=="bot"`→"app" 一致）。
- 下游约定：`Person.type=="app"`=机器人（open_id 解析）、`"user"`=真人（user_id 解析），
  `_resolve_group_sender`/`_mention_number` 据此分支，无需改。

## /LEAVE 事件即事实 + group-p2p 转义不对称（checkpoint-15 新增）

### 退群公告竞态与修复
- `_do_leave`（`group_event.py:30`）顺序 = 先 `send_text("/LEAVE X")` 公告、后
  `leave_chat` API。群内其他 bot 收到公告即 `emit_members_changed` 重拉，但此刻 X
  还没退，diff 空 no-op；X 真退后飞书只给 X 自己推 `bot.deleted_v1`，群内其他 bot
  无二次触发 → members 永远不减（真机复现）。
- 修复（事件即事实）：`_handle_leave`（`group_event.py`）判断
  `sender.type=="app"`（bot）才处理、真人忽略；用 `_resolve_group_sender` 拿发送者
  号码，调 `conn.emit_member_leave(number, chat_id)` 直接标记退群，不再重拉。
- `emit_member_leave`（`agent_conn.py` 新增）：
  1. `tracker.add_event(short_number, "leave", now_ms, is_human=False)`——用本地
     `now_ms` 做时间戳，靠 `_apply` 的单调性（`int(ts) <= cur.last_timestamp` 忽略）
     让后续历史回放的旧事件（含重复 leave、或误发公告后的 enter）不覆盖。
  2. 快照 `_members_snapshot[chat_id]` 剔除该 number，push
     `members_changed(added=[], removed=[该bot])`。
  3. 快照里无该 number 时只记 tracker、不 push（边界：快照未建）。
- 已知风险（接受）：公告后进程挂→退群失败→误判 leave；本地/服务器时钟倒挂时
  误判态无法被历史回放纠正。均不记 ISSUE。

### group-p2p 发送侧转义不对称（本次顺手修）
- 真群：发送 `_handle_agent_send_chat`（`daemon.py:488`）`escape_outgoing`（`/`→`//`），
  接收 `route_message` 群分支 `unescape_incoming`（`//`→`/`）——对称。
- group-p2p：发送走 `_handle_agent_send_p2p`（phone 把 group-p2p 当 p2p 发），
  **原本无 escape**；接收却走 `strip_at_all=True` 分支 unescape——不对称，导致
  group-p2p 里 agent 发 `/` 开头消息会被 `is_command`（`chat_type=="group"` 成立）
  误判成命令。
- 修复：`_handle_agent_send_p2p` 对 `isinstance(target, AgentRef)`（即 bot↔bot /
  group-p2p）分支补 `escape_outgoing`；真人 target 不转义（真人 p2p 接收也不
  unescape，保持对称）。

### 飞书行为备忘（真机）
- **owner bot `leave_chat` = 解散整个群**，不是成员减一（cleanup 报
  `232011 Operator can NOT be out of the chat`）。故「bot 退群 members 减」的验证
  必须用非 owner bot 退群。

## 群列表 sync 与主动 get_members（checkpoint-17 待实施）

### daemon 侧「找所有群」已有现成路径
- `_build_group_trackers`（`daemon.py:209`）：`lib.list_chats(app_id, app_secret)`
  （`core.py:482`，飞书 API，只返回当前所在群）拉 bot 所在所有群；再 `_load_contact_cache`
  拿 chat_id 集合过滤 group-p2p（`daemon.py:230-235`）。目前只用于建 tracker，未暴露给 agent 通道。
- 过滤 group-p2p 的权威判断 = contact cache 的 chat_id（`_is_group_p2p`，`agent_conn.py:548`），
  **不能信 session.json meta**（group-p2p 标记只写在 meta，从没进 entry）。

### Telecom 生命周期关键点
- `FeishuTelecomClient.startup()`（`telecom.py:262`）：`agent_connect` → 写 startup 帧等 ack →
  成功则 `self._sock = sock` + `_do_listen()`（`telecom.py:284`）。
- `_do_listen()`（`telecom.py:405`）：启动 `_reader` + `_heartbeat` task，**只在 startup 里调**。
- `listen()`（`telecom.py:387`）只设回调（on_msg/on_members_changed 等），不启动 reader。
- 故 startup 成功后 client 即可 `_request`（写 socket 等 reader 收 ack），`get_members`/未来 `list_chats` 可用。

### Phone 生命周期
- Phone 无 `startup()` 方法，只有 `add_card`（`phone.py:82`）→ `listen`（`phone.py:256`）。
- `add_card`：`client.startup()` 成功 → 存卡、记 `_clients`、自动 `await self.sync_groups()`
  （fail-open）；失败 → 卡标 `status="failed"`。
- `_ensure_group_session`（`phone.py`，async）：惰性建群会话，members 空则
  `await tchat.get_members()` 拉初始成员（fail-open 忽略异常）。members 平时由
  `_make_on_members_changed` 写入，此处是兜底单点。
- `sync_groups()`（`phone.py`）：逐卡 `client.list_chats()` → 每群 `_ensure_group_session`，
  title fallback chat_id；逐卡 list_chats 失败 fail-open。
- `Chat.get_members()`（`telecom.py`）是公开 API，Phone 经 `tchat.get_members()` 调用。

## list_chats RPC + 群列表 sync（checkpoint-18 已落地）

### 全貌
Phone `sync_groups()` → `client.list_chats()` → `_request(proto.agent.list_chats())`
→ daemon `_handle_agent_list_chats` → `conn.list_real_groups()` → 回 `list_chats_ack`
`{ok, chats:[{chat_id,name}]}`。

### daemon 侧 `AgentConn.list_real_groups()`（agent_conn.py）
- `Lib.list_chats(app_id, app_secret)`（core.py:482，飞书 API）拉 bot 所在全部群（含 group-p2p）。
- 过滤 group-p2p = `_load_contact_cache` 的 chat_id 集合（`_is_group_p2p` 同源），
  **不信 session.json meta**。
- name 用 `_read_group_name(chat_id)` 兜底，失败返回 ""。
- list_chats 失败 fail-open 返回 `[]`（对齐 tracker 构建风格）。
- `_build_group_trackers` 复用 `list_real_groups()`，不再内联过滤逻辑。

### telecom 侧
- `_ACK_TYPES` 含 `list_chats_ack`；`list_chats()` 失败 `SendError`，成功返回 `ack["chats"]`。

### Phone 侧关键点
- `_ensure_group_session` 变 async，members 空则拉用 `tchat.get_members()`（= `client._get_members`）。
   - 拉取在「群消息到达且 members 空」时触发一次 RPC；正常路径已被 daemon 首次全量 added 填充，
     仅兜底命中（先正确后优化）。

## 异常感知现状（会话4 前置，checkpoint-19）

### Phone 使用者的异常感知三层
- 能感知：`send`/`create_group` 同步失败 → `SendError` 冒泡；`add_card` 失败 → 返回
  `Card(status="failed", status_reason=...)`；卡不存在/未激活 → `ValueError`
  （`_resolve_send_card` phone.py:170 / `_client_for` phone.py:243）。
- 静默吞：场景24 `list_members` 失败 → `_ensure_group_session`（phone.py:214）只
  `logger.warning`，members 空；`sync_groups`（phone.py:301）`list_chats` 失败只 warning。
- 通路断：断连完全无感。

### 关键事实（改异常感知前必须知道）
- `ConnectionLost` 定义于 telecom.py:136 但从未被抛。
- `_reader`（telecom.py:426）断连：`msg is None` → `await self._on_disconnect()` → return；
  不清理 `_sock`/`_tasks`/`_pending`。
- `Phone.listen`（phone.py:283）只接 `on_msg`/`on_members_changed`，不接 `on_disconnect`/
  `on_error`；telecom `listen`（telecom.py:402）缺省落 `_noop_on_disconnect`/`_noop_on_error`。
- `on_error` 是死通路：daemon 从不发 error 帧，`_reader` 对非 ack/members_changed/message
  帧 `continue` 丢弃（telecom.py:444），故 term.py:151 的 `on_error` 从未触发。
- `_do_listen`（telecom.py:420）`if self._tasks: return` 防重入；`_tasks` 只在 `shutdown`
  （telecom.py:510）清空，断连不清 → 重连前必须 `_tasks.clear()`，否则新 reader 不启动。
- on_disconnect 内不能同步重连（会死锁在 `_do_listen` 防重入），必须
  `asyncio.create_task` + `asyncio.sleep(delay)` 异步延时重连。

## 异常感知已实施（会话4，checkpoint-20）

### 断连清理与透传（telecom）
- `_reader`（telecom.py:426）断连：`msg is None` → `_handle_disconnect()` → `await
  self._on_disconnect()` → return。
- `_handle_disconnect()`（telecom.py 新增，_reader 之后）：`_sock=None`；未决 pending
  future 逐个 `set_exception(ConnectionLost("connection lost"))`（`if not fut.done()`
  防御）；`_pending.clear()`；`_tasks.clear()`。
- 顺序保证死锁规避：先 `_tasks.clear()` 再 `_on_disconnect()`，故 on_disconnect 里
  触发的重连不会撞 `_do_listen` 的 `if self._tasks: return`。

### Phone 断连/重连（phone.py）
- `Phone.listen` 新增 `on_disconnect=None, on_error=None` 参数，逐卡透传
  `_make_on_disconnect(number)` / `_make_on_error(number)`。
- `_make_on_disconnect(number)`：先通知使用者的 `on_disconnect(number)`，再
  `asyncio.create_task(self._reconnect(number))` 存 `_reconnect_tasks[number]`。
- `_reconnect(number, delay=1.0)`：`sleep(delay)` → `reconnect(number)`；CancelledError
  上抛、其余 warning；finally 从 `_reconnect_tasks` 移除。
- `reconnect(number=None)`：复用旧 client 重 `startup()`（回调保留，无需重新 listen），
  失败标 `status="failed"` + `_save_cards`，成功标 `ok` + `sync_groups()`；无 number 时
  遍历所有卡。
- `shutdown()`：先 cancel+await 所有 `_reconnect_tasks`，再逐 client shutdown。

### 失败结果可观察
- `sync_groups()`（phone.py）返回 `{number: {"ok", "groups", "error"}}`，per-card
  fail-open 替代纯 warning；`add_card` 内 `await self.sync_groups()` 不再 try/except。
- `_ensure_group_session` 拉 members 失败：`data["members_error"]=str(e)` 持久化 +
  `chat.members_error`；成功时 `data.pop("members_error")`。
- `Chat.members_error: str = ""`（model.py），`chat_to_dict/from_dict` 序列化。

### 已知遗留
- `_heartbeat` 断连后未显式 cancel（design 用 `_tasks.clear()` 而非 cancel）：旧 heartbeat
  重连前醒来见 `_sock=None` 自行 return；重连快则残留并发心跳（多写一次 hb，无功能影响）。
- `on_error` 仍死通路（daemon 不发 error 帧），Phone 侧透传已接好，未造 error 帧。

## 真人进退群真机验证 + get_members 兜底超时（checkpoint-21 新增）

### 真人进退群（场景17 全绿）
- 观察者 A0001（Phone 装卡），bot A0002 建群拉 A0001 + 真人 H0001/H0002。
- 进群：bot `add_members` 拉真人 → 飞书 `user.added_v1` → `feed_member_event` →
  `emit_members_changed` → members 增 [A0001,A0002,H0001,H0002]。
- 退群：YZ 用 H0002 真人号飞书 App 主动退 → `user.deleted_v1` → members 减 H0002。
- 真人路径与 bot 路径同源（`feed_member_event` 对 user/bot 同一 `emit_members_changed`），
  真机首次坐实。
- 飞书私群真人无法主动加入（无二维码/邀请 API），「进」用 bot 拉、「退」用真人主动，
  两者都覆盖 user 事件路径。

### get_members 兜底 RPC 真机超时（30s）
- 现象：日志出现 `request timed out: get_members`，members 更新被拖慢 ~30s，
  正确性无碍（members_changed 帧 added 兜底写入）。
- **归因修正（checkpoint-22 实测）**：原「tracker.rebuild 历史回放 >30s」是错的。
  真机实测 `get_members` RPC 2.73s、`list_messages` 全量 0.51s/2 条、`list_members`
  0.36s、`fetch_token` 0.23s（连打 10 次 1.61s，无限流）。HTTP 快、历史少。
- 真正根源（推测）：**串行排队**，非单次回放慢——daemon agent socket 读循环单协程
  逐个 `await`（daemon.py:286-311），`resolve_group_members` → `tracker.rebuild()`
  内 `_build_lock` 串行（tracker.py:139）；真人进退群连发 user.added/deleted_v1，
  每个都触发 `emit_members_changed` → `resolve_group_members` → `rebuild()`，叠加
  phone 侧 `_ensure_group_session` 又发 get_members，多 rebuild 锁上排队才累积到 30s。
- 优化方向（未实施）：`_make_on_members_changed` 已有 added/removed，可跳过
  `_ensure_group_session` 的 get_members 兜底（加 `skip_pull` 参数）；仅收群消息路径
  （`_make_on_msg`）保留兜底。

## 30s 根因修正 + 2A 异步分发（checkpoint-28 新增）

### 30s 真根因（修正 checkpoint-22 的「串行排队」）
- 真机时间线坐实：phone 侧 telecom `_reader` 单协程（telecom.py:441），`await
  on_members_changed` 回调里同步 `get_members` → `_request` → `await wait_for(fut, 30)`
  （telecom.py:396），而 ack 必须由同一 reader 协程 `_handle_ack` 读回（:474）→
  **自阻塞**，ack 躺 socket 无人读直到 30s 超时。非 daemon 慢/排队/HTTP 长尾。
- 证据：daemon get_members handler 1.387s 即回 ack，phone 发请求后 30s 才超时，中间
  28.6s ack 无人读，超时后积压帧批量释放。

### 2A 修复（reader 回调异步分发）
- `FeishuTelecomClient.__init__` 增 `_callback_tasks`（telecom.py:254）。
- `_spawn_callback`（telecom.py:427）：`create_task` + 进 `_callback_tasks` + done_callback；
  `_on_callback_done`（:432）：移除跟踪、cancelled 跳过、异常 warning。
- `_reader`（:456-464）：members_changed / message 回调由 `await` 改 `_spawn_callback`；
  ack 帧仍同步 `_handle_ack`，reader 保持读 ack 能力 → 自阻塞解除，get_members 兜底恢复。
- `shutdown`（:536-546）：cancel/await `_callback_tasks`（与 `_tasks` 合并）。
- 决策：只做 2A、不做 skip_pull（1），接受 first-message+members 空时双拉 RPC。
- 写并发无虞：`SockFile.write` 单次 `writer.write()` 无 await（protocol.py:278），事件循环
  内原子，多任务并发写不 interleave。


