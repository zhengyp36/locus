# 群成员 tracker（members.json 运行时机制）

> 2026-08-22 会话。已实施（545 passed），真机未验证。已提交 `835bc3e`。方案承接 260821-bot-group-event.md。

## 目的

维护真群成员列表（bot + 真人）：实时事件 + 历史重建，产出并持续更新 `members.json`。

## 数据结构

`members.json`（`SESSIONS_DIR/<app_id>/by_chat_id/<chat_id>/members.json`，与 session.json 并列）：

```json
{"agent": {"A0001": {"last_timestamp": "...", "last_event": "enter"}},
 "human": {"H0002": {"last_timestamp": "...", "last_event": "enter"}},
 "last_updated": "<ms>", "history_available": true}
```

成员只存 bare number + event kind + timestamp，number↔id 转换在 daemon 层做。

## 核心规则

- `add_event(number, kind, ts, is_human)`：同步。`_building` 时进 `_buffer`，否则 `_apply`；`_apply` 单调判断 `int(ts) <= last_timestamp` 忽略（乱序 + 历史/实时同消息幂等）。
- `build()`（async）：`ref.ensure()` → `_load` → `_building=True` → `_replay_history` → `_snapshot_humans` → 回放 buffer → `_gc` → `_save` → finally `_building=False`。加载即 build。
- `_replay_history`：`_start_time()` 从 last_updated 倒推 5min；`list_messages(on_each_msg=...)` 流式（page_size 50 不攒全量）；只处理 bot system 消息（`started the group chat`→from_user enter 含建群者 / `invited ...`→to_chatters enter / `removed ...`→to_chatters leave）；`_resolve_bot_number` 正则 `A\d+` + `load_bot` 校验 name，真人 display-name 无锚返回 None 忽略；历史拉取失败置 `history_available=False` 告警降级；最后 `last_updated = _last_create_time`（历史最后一条）。
- `_snapshot_humans`：`list_members`（user_id type）→ `get_human_by_user_id` → number；真人唯一全量源 = API 快照 + 实时事件，**不从历史重建**；新成员 `last_timestamp = last_updated`。
- `_gc`：`last_event=="leave"` 且 `last_timestamp` 比 `last_updated` 早超 24h 淘汰（仅 build 时做）。
- 写盘 `TmpFilePair` 原子写。

## 事件接入（两触发点）

1. 群消息路由：member_added/removed 事件也喂 tracker（`handler.py` `handle_agent` conn 判定后分流，`loop.create_task(conn.feed_member_event)`；无 conn 静默丢弃）。
2. 账号 startup：`_build_group_trackers(conn)` 后台 task，`list_chats` 遍历群，跳过 group-p2p（读 `_load_contact_cache` 的 chat_id 集合），逐个 `get_tracker`。

## 其他模块

- `entry.py`：`MemberChanged` 加 `is_bot: bool = False`；`_parse_member_event` 传 is_bot（bot 事件 affected_users 空 = 自己）。
- `core.py`：`Lib.list_messages(app_id, app_secret, chat_id, start_time=None, end_time=None, on_each_msg=None)`（`url.list_msgs`，分页 + async 流式回调）。
- `agent_conn.py`：`_tracker_cache`（OrderedDict，`TRACKER_CACHE_LIMIT=128` LRU）+ `get_tracker(chat_id)`（miss 新建 + 超限 popitem LRU + `await build()`）+ `feed_member_event(entry)`（is_bot→自己 add_event，否则遍历 affected_users 转 human number）。

## 测试

新增 `test_tracker.py`（add_event 单调 / human-agent 分区 / buffer / GC / _start_time / _resolve_bot_number / _on_history_msg）。全量 **545 passed**。

## 遗留

- 真人历史重建不做（display-name 无 id 锚）。
- `history_available=false` 降级：读不到历史成员从空开始。
- 真机未验证（build 回放 / startup 遍历 / member 事件喂入）。
- 已提交 `835bc3e`。
