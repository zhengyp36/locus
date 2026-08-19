# 2026-08-19 cogos p2p 激活流程落地

`/activate <Axxx>` 命令 + `bs_agent.activate_agent` 三步编排。本体 `~/codex/cogos`。

## 命令
- `bs_setup.cmd_activate`：admin_only，`/activate <Axxx>`，去 `provider:` 前缀，调 `activate_agent`，RuntimeError 转 str。
- usage 提示曾误写 `/query-agent`，已修正。

## activate_agent 编排
1. `query_agent_fields` 查自身状态：active→「agent Axxxx 已经激活」；init→激活；其他→「状态为 'xxx'，无法激活」。
2. `self_bot` = 云端 fields 的 app_id/app_secret + 本地账号的 `bitable_token`（`load_bot(agent_account_id(provider, number))`）。
3. `_activate_agent_setup_p2p_group` → `_activate_agent_setup_meet`。

## _activate_agent_setup_p2p_group
- `_list_agent_fields`（分页拉 agent_registry 全部 fields）筛出 number < self 的 A 号。
- 群主规则：同奇偶 → self 群主；异奇偶 → 对方群主（均匀分布）。`_same_parity`/`_number_index`/`_p2p_name`（P2P:小:大）。
- 每对：`Chat.create(owner_bot, name)` → 写 activate.json `{num: chat_id}`（TmpFilePair 原子）→ `chat.add([peer_bot])`（对方 me_join，type="bot"）。
- 返回 `peers = {num: {app_id, app_secret, chat_id}}`。

## _activate_agent_setup_meet
- `botmgr.get_ws_manager()`（新增 getter）→ `WSManager.add(self_bot_id, on_event=on_event_for_activate, persist=False)`（临时监听，结束 remove）。
- 用对方 app_id/app_secret 在群里发 `Lib.send(..., "chat_id", "text", {"text": f'<at user_id="all">@所有人</at> /MEET {num}'})`。
- `asyncio.wait_for(done_event.wait(), MEET_TIMEOUT=600)`。

### on_event_for_activate（同步回调）
- `entry_from_event(evt)` → MessageReceived；正则 `_MEET_RE = /MEET\s+(A\d+)` 匹配 content_text；`peers[num]["chat_id"] == entry.chat_id` 校验。
- 通过则写 `activate.meet.{num}.json`（`{"open_id": entry.sender.open_id}`，TmpFilePair 原子，并发安全）；全收齐 `done_event.set()`。
- open_id 取消息 sender.open_id（对方 bot 的 open_id）。

## _activate_agent_finish
- 汇总 activate.json 为 `{num: {chat_id, open_id}}`（读 meet 文件）。
- 写 A0015 自己的 Contact bitable（`contact` 表 number/chat_id/open_id，`bh.insert_records`，用 self 的 app_id/app_secret/bitable_token）。
- admin agent_registry 该 number 置 `status="active"`（`bh.update_record`）。
- 回「agent Axxxx 激活完成」。

## 关键结论 / 坑
- 飞书 owner_id 恒非空，无法判断群主 → 用奇偶规则均匀分布，不查群主。
- bot 收 bot 群消息需 @all 标记（`<at user_id="all">@所有人</at>`），否则收不到。
- 未更新本地账号 status（只改 admin bitable，下次 startup 由 `refresh_agent_account` 同步）。
- /MEET 无 message_id 去重，重投重复写同一文件（幂等覆盖，无副作用）。
- WS 临时监听 persist=False；`botmgr.get_ws_manager()` 为新增访问入口。
