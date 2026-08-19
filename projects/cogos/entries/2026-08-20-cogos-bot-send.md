# 2026-08-20 — bot 间消息发送落地（发送 + 接收）

与 YZ 讨论后实现 bot↔bot 消息发送，未提交前发现并修复 3 处问题。

## 发送侧

- `AgentConn.make_session(receive_id, receive_id_type)`：用 `self.account`（= `ref.ensure()` 结果，含 app_id/app_secret/open_id/bitable_token）作 bot dict，弃 `accounts.load_bot` 重复读文件。
- `AgentConn.resolve_target(to)`：号码 → 飞书 receive 地址。目标缓存放模块级（`_target_cache`，`OrderedDict`，上限 20 FIFO，key=`provider:number`），跨 agent 共享。
  - Hxxxx → `(user_id, "user_id")`（`account["user_id"]`）
  - Axxxx → `(chat_id, "chat_id")`（`bs_agent.query_contact_chat_id` 查自己 contact bitable）
- `bs_agent.query_contact_chat_id(self_bot, peer_number)`：查自己 contact 表 `number=peer_number` 的 chat_id。
- daemon `_handle_agent_send_p2p` 重写：走 `conn.resolve_target` + `conn.make_session`。

## 接收侧

- 按 YZ 思路（不用 open_id 反查 bitable，更快）：`session_naming.fix_group_p2p` 在 meta 写 `peer_number`（activate/refresh 收尾已落盘）。
- `AgentConn.route_message` 按 `chat_type` 分派：`p2p` → `_resolve_human_sender`（human）；其余 → `_resolve_group_p2p_sender`（读 meta `peer_number` 构造 AgentRef）。普通群 meta 不符返回 None 不路由。
- `_resolve_human` 改本地优先（`accounts.get_human_by_user_id` 读 human-*.json，`ensure` 已持久化 user_id↔number）云端兜底，不再每次都打 bitable。

## 修的 3 处 bug

1. `resolve_target` 原 `_resolve_agent_chat_id(self.account, to)` 传完整全名 `COGOS001:A0002`，而 contact 表存裸号 `A0002` → filter 查不到，agent→agent 发送必 fail。改传 `target.number`。
2. provider 校验原 `my_account["provider"] != account["provider"]`，human account 无 provider 字段 → 发 human 恒被拒。改 `target.provider != self.ref.provider`。
3. 发送失败原 `raise e` 会断开整个 agent 连接，改仅 `send_err`。

## 真机待验证

- 双 bot 群普通文本消息（非 `/MEET` @all）对方 bot 是否稳定收到 `im.message.receive_v1`。
- 飞书是否把 bot 自己发的消息回传（预期不回传）。

## 验证

全量 `python3.11 -m pytest tests/ -q` 459 passed。
