# cogos 真机验证步骤记录（YZ 主导）

> 验证过程与问题，逐步 append。问题与结论编号：问题 N。

## 问题 1（2026-08-22）

- 现象：主动建群（`create_chat`）后不初始化 session 目录、不生成 `members.json`。
- 现状：`_handle_agent_create_chat`（daemon.py:484）建群后只 `_write_group_meta`（写 session.json，`members:[]`），未建 tracker；tracker 只在 startup 的 `_build_group_trackers`（daemon.py:209）遍历 list_chats 时才 build。
- 方向：建群后复用 tracker 方式构建，触发一次 `get_tracker` + `build`。
- 实现思路（待 YZ 确认）：
  - 在 `_handle_agent_create_chat` 的 `_write_group_meta` 后、`ack` 前加 `await conn.get_tracker(chat_id)`。
  - `get_tracker`（agent_conn.py:265）new `GroupMemberTracker` + `build`（tracker.py:115），build 会设置 `_dir`/`_path`、mkdir session 目录、写 members.json 骨架（agent/human/last_updated/history_available）。
  - 新群无 enter 历史、无 human，members.json 初始为空骨架，后续靠 `/ENTER` 公告 + `add_event` 收敛（L4 话题）。

## 问题 2（2026-08-22）

- 现象：`get_members` 只返回真人成员，bot 成员缺失。
- 现状：`_handle_agent_get_members`（daemon.py:652）对 `lib.list_members` 每个成员只走 `_resolve_human`（user_id → H 号），bot 解析不到被 `continue` 跳过；注释「bot members come from group-history parsing (block 6)」未实现。
- 方向（YZ）：真人用 API，bot 用自身 tracker 机制——成员已写入 members.json，ws 在、事件处理通即可。
- 实现思路（待 YZ 确认）：
  - human 部分保留：`lib.list_members`（user_id 类型）→ `_resolve_human`。
  - bot 部分改从 tracker：`tracker = await conn.get_tracker(chat_id)`，取 `tracker._data["agent"]` 的 A 号集合。
  - 每个 bot 拼 `{"number": f"{provider}:{number}", "name": load_bot(f"{provider}-{number}")["name"]}`（load_bot 读法同 tracker.py:260-262）。
  - 建议给 `GroupMemberTracker` 加公开访问器 `agent_numbers()`（`_data` 私有），`get_tracker` 调用 try 包裹，失败退回仅 human。
- 缓存生命周期结论（确认后）：`_tracker_cache` 是 `AgentConn` 实例字段（agent_conn.py:94），每次 startup 新建 conn 即重置；shutdown/断开走 finally `manager.unregister` 丢弃对象，缓存随对象回收，无「缓存命中但无 ws」的跨连接残留。唯一窗口期：ws 断但 socket 未 break 时，返回最后同步态（事件链滞后，非缓存残留）。

### 实施（问题 2）

- `tracker.py`：新增公开访问器 `GroupMemberTracker.agent_numbers()`（:286）返回 `sorted(self._data["agent"].keys())`。
- `daemon.py` `_handle_agent_get_members`（:652）：human 段不变；新增 bot 段——`conn.get_tracker(chat_id)` 取 `agent_numbers()`，逐个 `load_bot(f"{provider}-{number}")["name"]` 拼 `{number: provider:number, name}`；`get_tracker` try 包裹，失败退回仅 human；删除旧注释「bot members come from group-history parsing (block 6)」。
- 验证：syntax OK；`test_tracker.py` + `test_daemon.py` 52 passed；`test_accounts.py` 45 passed。

## 问题 3（2026-08-22）

- 现象：新群会话物理文件已落 `by_chat_id/<chat_id>/`（session.json + members.json），但 `group/<name>` 软链视图缺失。
- 现状：`group/`、`p2p/` 是 session_naming.py 的软链视图；`Session._sync_links`（session.py:461）在收到 `MessageReceived/MemberAdded/MemberRemoved/GroupDisbanded` 事件时惰性调用 `classify_chat` + `ensure_chat_link` 建链；`ensure_provider_link` 建 provider 软链。建群走 `_handle_agent_create_chat` → `_write_group_meta` 只写 session.json，未建 group 软链。
- 方向（YZ）：建群后补一次 link 同步。

### 实施（问题 3）

- `daemon.py`：新增 `_link_group_chat(app_id, chat_id, name)`——构造 group meta → `classify_chat` 取 `(category, base_name)` → `ensure_chat_link` 建软链；在 `_handle_agent_create_chat` 的 `_write_group_meta` 后调用。
- 验证（重跑步骤 1-2）：syntax OK；`test_daemon.py` 37 passed；真机建群 `verify2` 后 `group/verify2 -> by_chat_id/oc_aaab70dbe6cc42759a1e2372ce06cd54` 软链生成，session.json + members.json（含 A0001）落盘，init 云刷新回 active 正常。

## 问题 4（2026-08-22）

- 现象：`add_members([A0002])` ack ok 且 A0002 确已进群（`list_chats` 证实），但再次 `get_members` 仍只返回 `[A0001]`，看不到新成员。
- 现状：`_handle_agent_get_members`（daemon.py:665）bot 段读 `conn.get_tracker(chat_id).agent_numbers()`，即 A0001 的 members.json `agent` 区。A0001 建群时 build 一次（只有 A0001）；`add_members` 拉 bot 走 `Chat.add` → `lib.join_chat`（me_join），`bot.added_v1` 事件只发给被拉 bot（A0002）自己的 app，`feed_member_event`（agent_conn.py:296）对 `is_bot` 只更新 A0002 自己的 tracker。A0001 的 tracker 无 rebuild 触发，members.json 停留在 `['A0001']`。
- 佐证：重新 startup A0001 触发 `_build_group_trackers` rebuild 后，`get_members` 才返回 A0001+A0002——是 tracker 滞后，非 add_members 未生效。
- 方向（YZ 此前对问题2 定调：bot 用自身 tracker 机制）：get_members 读 bot 段前强制刷新 tracker。

### 实施（问题 4）

- `daemon.py:706` `_handle_agent_get_members` bot 段：`get_tracker` 后加 `await tracker.rebuild()` 再读 `agent_numbers()`；rebuild 有 `_build_lock` 防并发，异常 fail-open 空列表。
- 验证：syntax OK；现有群 `get_members` → `[A0001, A0002]`；新建群完整链路 `get_members` → `[A0001]` → `add_members` → `get_members` → `[A0001, A0002]`；`test_daemon.py` 37 + `test_tracker.py` 15 passed，全量 548 passed 1 failed（`test_bs_agent.py::test_full_flow`，step-1 遗留）。

