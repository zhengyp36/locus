# 建群 chat_registry + 群主解析

> 2026-08-21 会话。已实现 + 真机验证。已提交 `835bc3e`。

## 问题

bot 建群后 API 拿不到群主（真人建群 `GET /im/v1/chats/{chat_id}` 返回 owner_id/owner_id_type，bot 建群拿不到）。加人路径依赖群主身份，需把 `chat_id`/`owner` 落 admin bitable 供查询。

## chat_registry

- `bs_provider.py`：`TABLES` 加 `("chat_registry", [_text("chat_id"), _text("owner")])`；抽 `_create_table`；`ensure_chat_registry_table`（幂等补建）。
- `bs_agent.py`：`register_chat_info(chat_id, owner)`（解析 provider → `_load_admin` → 插记录）；`cleanup_chat_registry(provider)`（分页查记录，owner bot 查群信息，失败或 `chat_status=="dissolved"` 删记录）。
- `groupmgr.py`：`Chat.create(..., register=False)`，`register=True` 时校验 provider/id，建群后写 registry；`daemon._handle_agent_create_chat` 改 `register=True`。
- `scripts/fix_admin_bitable.py`（ensure + cleanup）、`scripts/exp_create_chat.py`（Telecom create_chat 验证）。
- owner 拼法 `f"{bot['provider']}:{bot['id']}"`（id=number）。

## 群主解析 `daemon.get_chat_owner(chat_id, ref)`

返回 `provider:number`，失败 `""`。顺序：

1. 真人建群：`Lib.get_chat_info` 加 `user_id_type` 参数，传 `"user_id"` 让 owner_id 直接返回 user_id（`core.py`，默认不传保持 open_id）；owner_id_type=="user_id" → `get_human_by_user_id` → `provider:number`（H）。
2. bot 建群：API 拿不到 → 查 chat_registry bitable 的 owner 字段（A）。
3. 都没有 → `""`。

`_handle_agent_add_members` 三分支：`""` → ack「group owner unknown」；human（H 开头）→ ack「only owner X can add members」；agent（A 开头）→ `AccountRef.from_number(owner_key).ensure()` 拿群主身份走 `Chat.add`。

## 关键坑

- 群解散后 `get_chat_info` 仍 code=0，需靠 `data.chat_status=="dissolved"` 判定（否则 registry 清不掉）。
- p2p 群不写 registry（register 默认 False），只有 Telecom.create_chat（daemon 建群）写。

## 验证

- 建群 `oc_df2a...` registry 写入 `owner=COGOS001:A0001`；解散后 cleanup 输出 `cleaned 1 stale row(s)`。
- 真机 add_members：真人群（owner H0002）add A0002/A0003 → 拒绝「only owner COGOS001:H0002」；A0001 建群 add A0002/A0003/A0004/H0002 成功。
- 全量 486 passed。

## 遗留

- 真人建群加人仍走「通知真人」路径（仅返回失败提示，未实现通知）。
- 已提交 `835bc3e`。
