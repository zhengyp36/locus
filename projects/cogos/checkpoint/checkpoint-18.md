# Checkpoint 18 — 实施 list_chats RPC + Phone sync_groups + members 空则拉

> 本体 `~/codex/cogos`。checkpoint-17 的未决点 1、2 落地实施，全绿。

## 做了什么

### 1. 协议层（protocol.py）
- `agent` channel 新增 `list_chats`（term→daemon，无参）与 `list_chats_ack`（`{request_id, ok, chats, reason}`，`chats=[{chat_id, name}]`）。
- docstring 补两行帧说明。

### 2. telecom 层（telecom.py）
- `_ACK_TYPES` 增 `list_chats_ack`。
- `TelecomClient` 抽象接口新增 `list_chats() -> list[dict]`（返回 `[{chat_id, name}]`）。
- `FeishuTelecomClient.list_chats()` 走 `_request(proto.agent.list_chats())`，失败 `SendError`，成功返回 `ack["chats"]`。

### 3. daemon/agent_conn 层
- `AgentConn.list_real_groups()`（agent_conn.py 新增）：抽公共逻辑——`Lib.list_chats` 拉 bot 所在全部群，用 `_load_contact_cache` 的 chat_id 集合过滤 group-p2p，`_read_group_name` 兜底 name。list_chats 失败 fail-open 返回 `[]`。
- `_build_group_trackers`（daemon.py）改为调用 `conn.list_real_groups()`，不再内联 aiohttp/list_chats/过滤逻辑。
- 新增 `_handle_agent_list_chats`（daemon.py）：调 `conn.list_real_groups()`，异常回 `ack(False, [], str(e))`。
- `_handle_agent_client` 分发新增 `list_chats` 分支。

### 4. phone 层（phone.py）
- 加 `logging` + `logger`。
- `_ensure_group_session` 改 async：建会话后若 `data.get("members")` 空，自动 `await tchat.get_members()` 拉初始成员（fail-open，异常 log 后忽略），覆盖式 `sorted(c.number)` 落库。
- 新增 `sync_groups()`：逐卡 `client.list_chats()` → 每个群 `_ensure_group_session(tchat, number)`，title fallback chat_id；逐卡 list_chats 失败 fail-open（log + skip）。
- `add_card` 成功分支自动 `await self.sync_groups()`（fail-open）。
- `_make_on_msg` / `_make_on_members_changed` 的 `_ensure_group_session` 调用改 `await`。

### 5. fake 层（fake.py）
- `FakeTelecomClient.list_chats()` 返回 `[]`。

## 测试

- 新增 18 个单测：协议 2、telecom 2、agent_conn 2（`list_real_groups` 过滤+失败）、daemon 2、fake 1、phone 5（sync_groups / 失败 fail-open / add_card 自动 sync / members 空则拉）+ 原 checkpoint-15/16 已改的 group_event/daemon 测试。
- 全量 **633 passed**（`python3.11 -m pytest tests/`）。

## 关键决策/注意

- `_ensure_group_session` members 空则拉用公开 `tchat.get_members()`（等价 `client._get_members`），不新引入私有调用。
- 该拉取在「群消息到达且 members 空」时会触发一次 RPC；正常路径 members 已被 daemon 首次全量 added 填充，仅兜底时命中（先正确后优化，未优化）。
- `list_real_groups` 过滤 group-p2p 仍用 contact cache chat_id（`_is_group_p2p` 同源），不信 session.json meta。

## 未决点 3 仍未动

- `diff 每次 tracker.rebuild()`（HTTP 历史回放开销）未优化，不阻塞。

## 提交状态

- 尚未 commit（checkpoint-15/16 的 `emit_member_leave` + group-p2p 转义不对称修复也仍在工作区未提交）。
