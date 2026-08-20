# 2026-08-20 cogos bot p2p 真机调通 + group-p2p 迁移修复

与 YZ 一起调试 bot↔bot p2p 通信，最终真机调通。两个代码修复（cogos 本体）。

## 调试起点（YZ 指定）

1. 把真人 `COGOS001:H0002` 拉进 A0001↔A0002 群，让 YZ 在飞书客户端肉眼确认群里两个 bot 都在。
   - 群 chat_id `oc_e2abc2eddea3d6200aa0698e2ed1d88b`（群名 `P2P:A0001:A0002`），群主 = A0001（异奇偶规则）。
   - `invite-members --bot COGOS001-A0001 --chat-id ... --members human-COGOS001-H0002` 拉人成功。

## 现象（YZ 观察）

- A0001 发 `/send COGOS001:A0002 hi`，真人看到 `@所有人 hi`，但 A0002 收不到。
- 消息实际落盘了：A0002 的 `providers/COGOS001/A0002/by_chat_id/oc_e2abc.../stream/xxx_message_received.json` 存在 → 说明 A0002 收到了消息，只是没传到 term 端。
- 该群出现在 `group/P2P.A0001.A0002` 而非 `p2p/` → 群分类也错了。

## 根因：老群缺 group-p2p 元数据（迁移缺口，非收发 bug）

- 消息路由链：WS 事件 → `EventHandler.on_event` 落盘 stream → `handle_agent` → `route_message` → 决定是否传 term。
- `route_message` 对群消息走 `_resolve_group_p2p_sender`，要求 `session.json` meta `chat_type == "group-p2p"` 且带 `peer_number`，否则返回 None 不路由。
- `fix_group_p2p`（写 group-p2p + peer_number + 转 p2p 链）是 **08-20 bot-send 改动才加的**，只在 `/activate`、`/refresh-contact` 收尾调用。
- A0001↔A0002 群是 **08-19 激活**时建的，当时无这步 → session.json 一直是 `chat_type:"group"`、无 `peer_number`；08-20 后未再 activate/refresh，故永远不 fix。
- 群分类错同理：`classify_chat` 对 `group` 归 group/，只有 group-p2p 才转 p2p/。
- 佐证：两边 session.json 均 `chat_type:"group"` 无 peer_number；`SESSIONS_DIR/<app_id>/activate.json` 均不存在（激活记录早于目录整改，已丢）。

## 修复 1：sync-group-p2p 命令补数据（commit `32a2940`）

- `bs_agent._list_contact_rows(http_session, app_id, app_secret, token)`：读 contact 表全部分页记录，返回 `{number: chat_id}`。
- `bs_agent.sync_group_p2p_links()`：遍历本地 agent 账号（bot_type=agent 且 active），`_ensure_contact_token` 补 token，读 contact rows，对每条调 `session_naming.fix_group_p2p(app_id, chat_id, peer_number)`。
- `session_links.py` 新增 `sync-group-p2p` CLI 命令（MODE_CLI）。
- `commands.py` DESCRIPTION 补一行。
- 真机：`sync-group-p2p` 修复 6 条（A0001↔A0002/A0003/A0004、A0002↔A0001/A0003/A0004）；session.json 变 group-p2p + peer_number，p2p/ 链就位，group/ 清空。
- 持久性：`_ensure_or_update_meta` 对已存在 meta 不会因后续 MessageReceived 覆盖 chat_type，故修复持久。

## 修复 2：bot p2p 去 @_all 前缀（commit `665ddda`）

- `agent_conn._strip_at_all(text)`：去前导 `@_all`（`text.strip()` 后 `startswith("@_all")` 则 `strip` 掉该前缀）。
- `route_message` 对 group-p2p（非 p2p）分支才去，human p2p 不去。

## 验证

- 真机：bot↔bot 互相收到消息。
- 全量 `python3.11 -m pytest tests/ -q` 459 passed。

## 顺带发现（本次未处理）

- contact bitable 里有 A0003、A0004（云端 agent_registry 存在，但本地 accounts 目录无对应账号文件）——可能是他机激活或本地被清理，待 YZ 知悉。
