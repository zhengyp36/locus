# 群聊块 4 实现（daemon handler + add_members 编排）

> 2026-08-21 会话。块 1-3（协议帧/数据模型/agent 侧）已在前会话落地；本会话先真机验证两行为点，再实现块 4。均未提交。

## 真机验证两行为点（先做，结论驱动实现）

脚本 `scripts/exp_group_verify.py`（`v1`/`v2` 两子命令，独立脚本，加载 accounts 目录 + `cogos.feishu.core.Lib` / `cogos.feishu.ws.WSManager`）：

1. **非 owner bot 拉真人**：A0001 建 private 群 → A0002（非 owner、未进群）`add_members`(YZ user_id) → `232011 Operator can NOT be out of the chat`，失败。
   → 结论：只能用群主 bot 拉真人（群主 = 建群的 agent 自己的 bot，即 `conn.ref.ensure()` 拿到的 account）。v1 方案维持。
2. **WS 群消息 sender**：A0001 建群 + 拉 YZ → WS 监听 A0001 → YZ 发消息 → raw `sender.sender_id` = `{open_id, union_id, user_id}` 三字段齐全，`user_id=125cf5a4` 直接可得。
   → 结论：块 5 真人 sender 无需 open_id→user_id 转换，`entry.sender.user_id` 直接用（与 p2p 一致）。

（临时验证群已 disband 清理。）

## 修改的文件与关键代码路径

### `cogos/feishu/core.py`
- 新增 `Lib.user_open_id(app_id, app_secret, user_id)`：`GET /contact/v3/users/{user_id}?user_id_type=user_id` → `data.user.open_id`。供 send_chat @真人用（human 本地账号只有 user_id 无 open_id）。复用已有 `url.user_info(user_id)`。

### `cogos/feishu/daemon.py`（块 4 主体）
- `_write_group_meta(app_id, chat_id, name)`：写 `SESSIONS_DIR/<app_id>/by_chat_id/<chat_id>/session.json` = `{"chat_type":"group","name":name,"members":[],"status":"active"}`。目的：create_chat 建群即标记 group，供 `route_message`（块 5 真群分支）和 `session_naming.classify_chat`（group/ 软链）识别；否则需等首条消息事件才由 `Session._init_meta_from_api` 补。
- `_handle_agent_create_chat(conn, msg)`：`conn.ref.ensure()` → `Lib.create_chat(app_id, app_secret, name)`（默认 private）→ `_write_group_meta` → `create_chat_ack(rid, ok, chat_id, name, reason)`。
- `_handle_agent_add_members(conn, msg)`：
  - 解析 `msg["numbers"]`（provider:number 全名）→ `AccountRef.from_number` 分 `HumanRef`/`AgentRef`；校验 provider 与 conn 一致、`ensure()` 可用、human 需 `user_id`、agent 需 `app_id`+`app_secret`；任一不满足即 fail-fast ack False（不落任何成员）。
  - **编排复用 `groupmgr.Chat.add(humans, bots)`**（`Chat(chat_id, owner, "private")`，owner=conn 自己 account）：已有 `_add_humans`（`list_members` 兜底校验 + 失败 sleep 5s 重试，`bfae959` 修过）+ 改 public → 逐个 bot `join_chat`(me_join) → 改回 private。**不重写编排**。
  - ack 语义：**同步实现**（await 编排完成后回 ack）。me_join 每次一个 API 调用，小群 <30s；`_request` 超时 30s，慢群再改异步。
- `_handle_agent_get_members(conn, msg)`：`Lib.list_members`（真人，member_id_type=user_id）→ 每个 `member_id` 经 `agent_conn._resolve_human(provider, user_id)` 转 H 号码 → `members=[{number: ref.key, name}]`（number 用 `ref.key` 全名，对齐 telecom `Contact.number`）。**bot 成员留空，待块 6 历史解析**。
- `_handle_agent_send_chat(conn, msg)`（替换原 `NotImplementedError`）：`Session(my_account, chat_id=chat_id).send_text(content, at_users=open_ids)` → `send_ack` → `conn.route_message(entry)` 回显。@ 解析：metions 逐条 `AccountRef.from_number` + `ensure()`，open_id 优先 `account.open_id`，human 缺则 `Lib.user_open_id`（user_id→open_id），bot 缺 open_id 则跳过（**bot @ 留块 5**，agent 账号不存 open_id）。
- 读帧循环 `_handle_agent_client`：`send_chat` 分支后加 `create_chat`/`add_members`/`get_members` 三分支（`await _handle_agent_xxx(conn, msg)`）。

### `tests/feishu/test_daemon.py`
- 新增 `TestAgentGroupHandlers`（10 测试）：create_chat 成功（校验 ack + 落盘 meta）/缺 name、add_members 成功（校验 humans/bots 分组 + `Chat.add` 调用）/缺 chat_id、get_members（list_members + `_resolve_human` 转号）、send_chat 成功/缺 content、`_write_group_meta`。
- mock 策略：`AgentRef.ensure` → account；`Lib.create_chat`/`Lib.list_members`、`groupmgr.Chat.add`、`Session.send_text`、`conn.route_message` 均 AsyncMock；`temp_config` fixture 隔离 SESSIONS_DIR。

## 测试

`test_daemon`+`test_client`+`test_entry`+`test_session`+`test_accounts`+`test_bs_agent`+`test_groupmgr`+`test_telecom`+`test_protocol`+`test_term`+`test_echo` = **305 passed**（含新增 10 个 handler 测试）。

## 遗留

- get_members 的 bot 成员 → 块 6 历史解析（`im/v1/messages` 增量 + system 进群/退群解析）。
- send_chat 的 bot @ → 块 5（open_id 来自 contact bitable，非 agent 本地账号）。
- add_members 同步 ack，慢群改异步（ack 通知，避免 `_request` 30s 超时）。
- 块 5：`route_message` 加真群 `group` 分支（真人 user_id→H 无需转换 / bot app_id→A / mentions）；`proto.agent.message` 帧需扩展 time/chat_id/chat_name/mentions 字段。
- 代码全部未提交。
