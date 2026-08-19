# 2026-08-19 cogos contact-refresh 落地

`/refresh-contact <Axxx>` 命令（`608ecef`）+ 工作区未提交改动。本体 `~/codex/cogos`。

## 命令
- `bs_setup.cmd_refresh_contact`：admin_only，`/refresh-contact <Axxxx>`，去 `provider:` 前缀，调 `bs_agent.refresh_contact`，RuntimeError 转 str。

## refresh_contact（bs_agent）
让已激活 agent 刷新通信录，补齐更高号码的新激活 agent：
1. `query_agent_fields` 查状态：`init`→「尚未激活，请先 /activate」；非 `active`→「账号已失效」。
2. `self_bot` = 云端 fields 的 app_id/app_secret + 本地账号 `bitable_token`。
3. `_list_contact_numbers` 拉自己 contact bitable 现有 A 号索引，取 `max_idx`。
4. `_list_agent_fields` 拉全部 agent；从 `max_idx+1` 到 counter `next_n` 逐个 peer：跳过自己；`_peer_chat_id` 从对方 contact bitable 查自己的 chat_id（无记录→对方未激活→stop，保证连续区间）；收进 `peers`。
5. 无 peers →「已是最新」或「已是最新，X 待激活」。
6. 有 peers → `_collect_meet_openids`（复用 activate 的 /MEET 收集，`prefix="refresh-contact"`）→ `_aggregate_openids` → 写 `refresh-contact.json` + `_write_contact` 写入自己 contact bitable。回「已刷新到 X」或「完成更新」。

## 重构（activate 与 refresh 共享）
- `_activate_agent_setup_meet` → `_collect_meet_openids`（`prefix`/`action` 参数化，写 `{prefix}.meet.{num}.json`）。
- `_activate_agent_finish` 拆出 `_aggregate_openids(peers, meet_dir, prefix)` + `_write_contact(http_session, self_bot, final)`。
- 新增 `_list_contact_numbers`、`_peer_chat_id`（对方 contact 用 `filter=CurrentValue.[number]="self_number"` 查自己 chat_id）。

## 工作区未提交改动（进行中）
- `accounts.py` `AccountRef`：`is_active` lambda 改名 `available`（`status in ("active","init")` 判定，语义化）。
- `bs_agent.py` `_list_contact_numbers`：`result["items"]` → `result["items"] or []`（空值保护）。
- `daemon.py`：
  - `_handle_agent_client` startup 时 `status=="init"` 拒绝（「account not active, activate it and try again」）。
  - `_handle_agent_send_p2p` 重构：`my_account = ref.ensure()` 校验（无→「Your number may be inactive」+ 返回 `"shutdown"` 断连）；provider 一致性校验（跨 provider 拒绝，兑现「不互通」折中）；`send_err`/`send_ok` 封装 send_ack；失败返回 `"shutdown"` 由外层 break。
