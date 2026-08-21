# 群聊收发打通（Telecom 发送拆分 + mentions 解析 + 接收三缓存）

> 2026-08-21 会话。块 5 主体：打通真群 send/recv 的号码↔id 双向转换。已提交 `835bc3e`。真机验证未做。

## 发送端：Telecom 发送接口拆分 + mentions open_id 解析

- `telecom.py`：`TelecomClient.send(target: Contact, msg)` 只收 Contact（p2p），不再收 Chat；群发走新 `Chat.send(msg, to_targets=None)` → `self.client._send_chat(self, msg, to_targets)`；新增抽象 `_send_chat(chat, msg, to_targets=None)` 及 `FeishuTelecomClient` 实现（拼 `proto.agent.send_chat(chat_id, name, msg, metions=[c.number for c in to_targets])`）；`ALL = Contact("@all")` 常量（显式 @all 语义）。
- `daemon.py` `_handle_agent_send_chat` 重写：`at_users` 恒以 `"all"` 开头（群发必须带 @all 否则群内其他 bot 收不到）；metions 里 `"@all"` 再 append 一个 `"all"`；其余走 `conn.resolve_open_id`。去掉 `account.get("open_id")`（agent 账号恒空）。
- `agent_conn.py`：`AgentConn` 加 `_open_id_cache`；`resolve_open_id(my_account, ref)` —— human 走 `user_open_id(user_id)`，agent 读自己 contact bitable 全表灌缓存，key=number（H/A 通吃）。
- `bs_agent.py`：`list_contact_open_ids(self_bot) -> {number: open_id}`（分页读 contact 表，含 `_ensure_contact_token`）。

## 接收端：三缓存取代 _open_id_cache

`agent_conn.py` 三结构单一写入口：

1. `_id_cache` 主表（OrderedDict，number → `{"user_id", "open_id"}`，human 两字段、agent user_id 恒空）
2. `_open_id_index`（open_id → number）
3. `_user_id_index`（user_id → number）

- 写入口 `_cache_id(number, id_dict)`：写主表 + 派生两反向索引（跳过空 id），FIFO 上限 50 淘汰。
- 查询：发送端 `resolve_id(number) -> dict`；接收端 `resolve_number(id, id_type)`（id_type ∈ open_id/user_id），反向 miss → 灌全表再查。
- `route_message` 加 mentions 转换（`_resolve_mentions`/`_mention_number`，number 拼 provider）+ 剩余 `@_all` → `{"number":"@all"}`；`_strip_at_all` 改返回 `(stripped, extra_all)`。
- `protocol.py` `agent.message` 帧加 `mentions`（默认 `[]`，number 形式）；`telecom._to_message` 已读 mentions 转 `Contact`，`@all` 命中 `ALL`。

## 结论

- open_id per-app：contact bitable 存「当前 bot 视角下另一 bot 的 open_id」；human open_id 走 `user_open_id` API。
- 转义：发送端默认 @all（通信层内部去掉），agent 可再加；`@_all` 不出现在 mentions 列表。

## 测试

全量 486 passed。

## 遗留

- 接收端「去掉第一个默认 @all」暂缓。
- 真机群发 @all + mentions 未验证（需 daemon running + 真群）。
- 已提交 `835bc3e`。
