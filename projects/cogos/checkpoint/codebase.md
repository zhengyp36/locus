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
