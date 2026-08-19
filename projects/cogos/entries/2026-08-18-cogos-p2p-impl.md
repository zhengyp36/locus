# 2026-08-18 cogos p2p 消息实现 checkpoint

bot↔bot p2p 消息收发检视与修正，本体 `~/codex/cogos`。落地 commit `1624136`（feat: Implement p2p chat between bots）。p2p 群建立后续由 /activate 承接（`74d74bc`，见 entries/2026-08-19-cogos-p2p-activate.md）。

## 状态
- 已落地（1624136）：bot↔bot p2p 消息收发；commands/core/daemon/groupmgr/protocol/purge/telecom 七文件改动提交。
- p2p 群建立：由 /activate 三步编排承接（74d74bc），不再单列。
- 仍待办：agent 目标 account 使用（走 user_id 应为 open_id）、OnMsg 返回格式（应为 Chat）、send_chat 未实现。

## 本会话已做的修正
- `cogos/feishu/core.py:37,41,45` — `url.join_chat`/`chat_members`/`disband_chat` 重复拼 `{chat_id}` → 改为单次。
- `cogos/feishu/groupmgr.py:98` — `cmd_list_group` 循环 `idx` 不递增 → 用 `enumerate(chats, 1)`。
- `cogos/feishu/purge.py:104` — `_do_cleanup` 去掉 `if _is_owner(chat)` gate（群主判断无效），改为无条件先解散失败再离群；并修 `disband_or_leave` 标志：离群成功分支未置 True 会导致退群成功后仍误报"解散及离群失败"。

## 用户已改（本会话检视过，逻辑正确）
- `cogos/feishu/core.py:33,365` — `url.leave_chat` + `Lib.leave_chat` 由 `me_leave` 改为 `DELETE /im/v1/chats/{chat_id}/members` + `member_id_type=app_id` + `json={"id_list":[app_id]}`（me_leave 无法离群，与 `purge._leave_chat` 一致）。
- `cogos/feishu/groupmgr.py:27` — `Chat.list` 不填 owner（`{}`）/ chat_type（`''`）（群主判断无效，刻意留 TODO）。
- `cogos/feishu/purge.py:104` — `_do_cleanup` 先尝试解散、失败再离群。

## 待办（未完成）
- `daemon.py:293` `_handle_agent_send_p2p`：`isinstance(target, HumanRef)` 检查已删，但 agent 目标仍走 `account["user_id"]` + `receive_id_type="user_id"`（agent 应为 open_id）。
- `daemon.py:331` `_handle_agent_send_chat`：仍 `raise NotImplementedError`。
- `telecom.py` OnMsg 返回格式仍 `Callable[[dict], Awaitable[None]]`（应为 Chat，否则无法回群消息）。

## 已读代码要点（锚点）
- `daemon.py:293` `_handle_agent_send_p2p`：`AccountRef.from_number(to)` → `target.ensure()` → `load_bot(agent_account_id(provider, number))` → `Session(bot, receive_id=account["user_id"], ...)` 发文本 → `route_message`。
- `telecom.py:46` `Chat` dataclass（`id`/`title`）；`telecom.py:189` send 用 `isinstance` 分 Contact/Chat。
- `protocol.py:122` `send_chat` lambda 字段：`to`/`title`/`content`/`metions`（type=`send_chat`）；`send` 即 p2p。
- `core.py:379` `Lib.list_chats` 分页拉群列表；`core.py:332` `Lib.join_chat`（me_join，public 群）。

## 关键结论
- 飞书 list chats 的 `owner_id` 几乎恒非空 → 无法判断 bot 是否群主，放弃判断（改"先解散失败再离群"）。
- 离群 = `DELETE .../members` 用 app_id 移除自己；拉 bot 进群 = `me_join`（需 public 群）。

## 遗留 / 坑
- `purge.py:70` `_is_owner` 现无调用（死代码），可删或待判断修好再启用。
- `protocol.py:122` 字段 `metions` 拼写应为 `mentions`（protocol/telecom 两处一致，不影响运行）。
- `url.leave_chat` 与 `url.chat_members` 返回相同 URL（DELETE/POST 复用同端点）。
