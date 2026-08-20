# 2026-08-20 — account refactor 实施完成

按 account-refactor 篇实施，459 测试通过。

## 查证结论：列 bitable API

- 飞书无「列 app 名下 bitable」专用端点，用 `GET /drive/v1/files`（不带 folder_token，返回 app 云空间）过滤 `type=bitable`，鉴权 tenant_access_token（app_id/app_secret）。
- 已存在 `bh.list_apps`，`resume_provider` 已实测用。bitable 的 drive file `token` 即 app_token，`name` 字段可匹配 `{number}-Contact`。
- 故 token 重建可行，无需进 agent_registry 云端。

## 改动

- `bitable_helper.py`：新增 `find_contact_bitable(session, app_id, app_secret, number)` 列 app 名下 bitable 匹配 `{number}-Contact` 返回 app_token。
- `bs_agent.py`：
  - `add_agent` 删 open_id/patch_granted/bitable_url 三字段写入；resume 只读 app_id/app_secret；patch 授权改为总是提示（重复幂等）。
  - `refresh_agent_account` 删 open_id/patch_granted 的 local.get 保留行。
  - 新增 `_ensure_contact_token(provider, number, app_id, app_secret)`：本地 token 缺失→`find_contact_bitable` 重建→写回本地缓存。
  - `activate_agent`/`refresh_contact`/`query_contact_chat_id` 三处 token 读取改缺失即重建。
- `bs_provider.py`：`_configure_admin_bot` 的 open_id 可空（agent resume 时为空跳过 creator 查询；admin 流程不受影响）。
- `term.py`：`_load_pin` 改 async `await AgentRef(number).ensure()` 取 pin。
- `tests/feishu/test_bs_agent.py`：删/改 open_id、patch_granted、bitable_url 相关断言。

## 追加修复：ensure 补固有字段

term 改 ensure 后暴露：`AgentRef._refresh` 只 merge 云端 agent_registry 字段，缺 `bot_type`/`type`/`id`/`provider`/`tenant`，导致 daemon `ws.add` 读 `bot_type` 失败（`bot 'COGOS001-A0001' has no bot_type`），term 报 `daemon closed connection during startup`。

修 `accounts.AgentRef._refresh`：merge 后补 `id=number`/`type=bot`/`bot_type=agent`/`provider`，tenant 从 `_load_admin` 拿。删残缺缓存后 ensure 重建。真机验证：`ws added for COGOS001-A0001 (bot_type=agent)` + startup OK；token 重建 `find_contact_bitable` 命中 `A0001-Contact` 写回。

## 验证

- `python3.11 -m pytest tests/ -q`：459 passed。

## 遗留

- `_peer_chat_id` 读 peer 本地 token 仍用 `load_bot`（load-bot-vs-ensure 篇的「该改」项），未动，待 YZ 定方向。
- 存量 `bot-{provider}-{number}.json` 可能残留旧 open_id/patch_granted/bitable_url 字段（merge 不删），可 `invalidate_local_accounts` 或手动清理。
- 删三字段的新建路径（add_agent）仅单测覆盖，未走真机 add-agent 流程。
