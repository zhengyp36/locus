# Checkpoint 17 — 未决点讨论:主动 get_members + 群列表 sync

> 本体 `~/codex/cogos`。两个未决点(Phone 主动 get_members、diff 每次 tracker.rebuild)经讨论收敛为实施方案,待 /undo 后实施。

## 结论

### 未决点 1:Phone 主动 get_members(改为内部自动)
- 现状:telecom 层有公开 `Chat.get_members()`(`telecom.py:81`),Phone 侧零调用,`chat.members` 完全靠 `_make_on_members_changed` 被动填充。
- 方案:`_ensure_group_session`(`phone.py:187`)建会话后,若 `data.get("members")` 为空,自动 `client._get_members(tchat)` 拉一次做初始值。幂等(覆盖式 `sorted(members)`),与 daemon 首次全量 added 不冲突。
- 覆盖所有建会话路径(收群消息 / members_changed / sync),单点兜底,不依赖上层。

### 未决点 2:Phone 后接入「未知群」盲区 → sync_groups
- daemon 侧已有现成路径:`_build_group_trackers`(`daemon.py:209`)用 `lib.list_chats`(`core.py:482`,飞书 API,只返回当前所在群)拉所有群,再用 `_load_contact_cache` 的 chat_id 集合过滤 group-p2p(`daemon.py:230-235`)。
- 过滤必须用 contact cache(`_is_group_p2p`),不能信 session.json meta(group-p2p 标记只在 meta,从没进 entry)。
- 新加 `list_chats` RPC:抽公共 `conn.list_real_groups()`,tracker 构建与新 handler 共用,避免过滤逻辑漂移。
- Phone 侧 `sync_groups()`:拉群列表 → 每个群 `_ensure_group_session` + members 空则 get_members。title fallback chat_id(list_chats 群名可能空)。

### 触发点:startup 自动 + 显式接口兜底
- Phone 无 `startup()` 方法,生命周期 `add_card` → `listen`。
- 挂点 = `add_card` 里 `client.startup()` 成功分支(`telecom.py:284` `_do_listen()` 已启动 reader,`_request` 可用)。
- 逐卡 sync 正确粒度:list_chats 按 app_id,每卡拉自己群,无重复。
- sync 失败 fail-open:log + 卡仍标记 ok,不影响 add_card(对齐 `_build_group_trackers` 风格)。
- 显式 `sync_groups()` 保留作运行期兜底(运行中才被拉进的新群且错过成员事件)。

## 实施清单

1. telecom:协议层加 `list_chats` 帧 + `list_chats_ack`;`FeishuTelecomClient.list_chats()`;`Chat`/裸 dict 返回 `[{chat_id, name}]`。
2. daemon:`_handle_agent_list_chats`,复用抽出的 `list_real_groups()`,name 用 `_read_group_name` fallback ""。
3. Phone:`sync_groups()`;`_ensure_group_session` 补「members 空则拉」;`add_card` 成功分支自动 sync(fail-open)。
4. fake:`FakeTelecomClient.list_chats()` 返回空。
5. 测试:单测补 list_chats 协议/daemon/fake 断言。

## 未决点 3(diff 每次 tracker.rebuild)本轮未动

仍待优化(先正确后优化),不阻塞。
