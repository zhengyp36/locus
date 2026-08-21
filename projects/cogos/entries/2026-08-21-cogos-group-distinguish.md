# group-p2p vs 真-group 区分（contact.json 本地缓存）

> 2026-08-21 会话。已实施，真机未验证。已提交 `835bc3e`。

## 目的

真群与 group-p2p 飞书 `chat_type` 都是 `"group"`。原靠 session.json meta `chat_type=="group-p2p"` 区分（activate/refresh 时 fix_group_p2p 写的一次性快照，会滞后）。改为以 contact bitable（权威源）的本地缓存判定。

## 核心：contact.json 本地缓存

- 路径：`SESSIONS_DIR/<app_id>/contact.json`（与 session.json 同级，按 `self.app_id` 定位不绕软链接）。
- 结构：`{"max_active_number": "A0004", "contacts": {"A0001": {"chat_id": "oc_xxx", "open_id": "ou_yyy"}}}`（per-bot 各 peer 的 dual-bot 群 chat_id/open_id，不含 self）。
- 本地缺 → 从云端 contact bitable 读全量新建（`_list_contact_rows` + `list_contact_open_ids`）。

## 判定

收 group 消息读本 bot contact.json：chat_id 命中 `contacts` → group-p2p（反查 number 得 peer_number）；未命中 → 真 group（sender 走 `resolve_number` 反查）。前提：contact bitable 只写 dual-bot 群（`_write_contact` 仅被 activate_finish / refresh_contact 调用），真群走 chat_registry 不污染。

滞后危害单向：只会把 group-p2p 漏判成真 group，不会反向。

## /clean-cache 失效广播

`cmd_clean_cache`：失效当前 provider 所有 agent 的 contact.json + 清进程内缓存 + 触发 refresh-contact。**失效 ≠ 刷新**（删 contact.json 只能重建云端已有数据，新号还没进 bitable 必须靠 refresh-contact 发现）。

- 轻量同步（失效）+ 重量异步（`_refresh_all_contacts` 后台逐个 agent 串行 refresh）。
- `AgentConnManager.all()` 遍历清 conn 三 id 缓存（`_target_cache`/`_human_cache` 不清）。
- provider 定位用 `list_bot_accounts()` 过滤（`bot_type=="agent"` + provider），不依赖软链接。

## 命令交互模式（通用）

耗时命令（/activate、/refresh-contact、/clean-cache）先回「处理中...」，异步完成后再回结果。`bs_cmd.py` `msg_command` 加 `long_running`。

## 实施

- `bs_agent.py`：contact.json 读写（`_contact_cache_path`/`_list_contact_full`/`save_contact_cache`/`load_contact_cache`/`invalidate_contact_cache`）+ `_max_active_number`；refresh_contact / activate_finish 末尾补写本地缓存。
- `agent_conn.py`：`route_message` else 分支走 `_resolve_group_sender`（contact.json 命中→group-p2p）；删 `_resolve_group_p2p_sender`/`_load_chat_meta`；`AgentConn` 加 `_contact_cache` 内存缓存 + `clear_id_cache`/`invalidate_contact_cache`。
- `bs_setup.py`：`cmd_clean_cache` 失效广播 + `_refresh_all_contacts` 后台刷新。
- `bs_cmd.py`：`long_running` + dispatch 先回「处理中」。

## 测试

全量 486 passed。

## 遗留

- 「滞后检测 + 自动 refresh」的 revalidate/hb 触发点未实现，当前仅靠 /clean-cache 兜底。
- 真群 sender/mentions 解析未真机验证。
- 已提交 `835bc3e`。
