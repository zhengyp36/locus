# 飞书群历史拉取实验（真机）

> 结论已入本体 `~/codex/cogos/docs/feishu-group-history.md` + 实验脚本 `~/codex/cogos/scripts/exp_group_history.py`。本条目存索引 + 群聊方案讨论要点（未成形，待新会话定）。

## 实验结论（真机验证）

- 鉴权：`POST /auth/v3/tenant_access_token/internal`（app_id/app_secret）→ tenant_access_token。
- 拉取：`GET /im/v1/messages`（`container_id_type=chat` + `container_id` + `page_size=50` + `sort_type=ByCreateTimeAsc`）分页拉全量。
- sender 表示：text 消息 bot=`app_id`(id_type=app_id) / 真人=`open_id`(id_type=open_id，**无 user_id**)；system 消息 sender 全空，操作者在 `body.content.from_user/to_chatters`（**展示名字符串**，无机器 id）。
- system 模板（前缀匹配）：`{from_user} started the group chat.` / `{from_user} invited {to_chatters} to the group.` / `{from_user} removed {to_chatters} from this chat.`；bot me_join 特征 `from_user == to_chatters`（自己邀请自己）。
- 群主多 1 条 position 0 `Welcome to {group_type}`；新成员能否看入群前历史取决于群设置「New members can view all chat history」。
- 群成员 API `GET /im/v1/chats/{chat_id}/members?member_id_type=open_id` **只返回真人，不含 bot**。
- open_id→user_id/union_id：`GET /contact/v3/users/{open_id}?user_id_type=open_id`（A0001 已有权限，真机通过）。
- 增量：`start_time` 秒级（10 位）含边界（`create_time/1000 >= start_time`）；余量前移 + `message_position`（群内连续递增序号）去重可行。

## 群聊方案讨论（未定）

- 真人身份：open_id→user_id→human_registry 确定身份。**open_id 是 per-app 的**，跨 bot 不稳定；本地 open_id 缓存仅 per-bot，最终身份键落 user_id（union_id 跨租户兜底）。
- bot 身份：text 消息 sender.app_id→agent_registry；system 消息只有展示名号码（`A0003`）→再查 agent_registry 补 app_id。
- 群成员获取：真人走 API；bot 靠解析历史进群/退群 system 消息，依赖命名 `名字(Axxxx)`，add-agent 结束时校验命名不合规告警。
- 增量拉取：记上次最新 create_time(ms)+position，本次 `start_time = create_time/1000 - margin`（几十秒），`position > 上次` 去重。
- 不在 provider 名录的真人和 bot 暂不考虑（解析时静默跳过）。
