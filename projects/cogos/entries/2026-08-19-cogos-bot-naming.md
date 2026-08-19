# cogos bot 命名规范 + bs_registry 自检

commit `951c32a`（2026-08-19）。

## 命名规范（accounts 目录）

| 类型 | id（文件名 stem） | name（显示名） | 文件 |
|---|---|---|---|
| admin-bot | `{provider}-ADMIN` | provider_name | `bot-COGOS001-ADMIN.json` |
| bs-bot | `{provider}-BS` | `{provider}-BS-{device_name}` | `bot-COGOS001-BS.json` |
| agent-bot | `{provider}-Axxxx`（`agent_account_id`） | `{name}(Axxxx)` | `bot-COGOS001-A0003.json` |

- 原 admin-bot id `admin-{provider}` → `{provider}-ADMIN`（`bs_provider` 两处 bot_id 拼接改掉）。
- 原 bs-bot id = provider（`COGOS001`）→ `{provider}-BS`；name 加设备名后缀。
- `cmd_setup_bs` 读 `device.json` 取 `device_name`，前置校验 device 已 init；`--bot` 参数移除。
- `create_bot` 加可选 `device` 参数（bs-bot 落盘 device 字段）。

## 删 S 计数器

- `bs_provider.COUNTER_RECORDS` 只留 `A`，新 provider bitable 不再有 S counter。

## bs_registry 自检 + tenant 回填

- `bs_registry` 字段改 `device/app_id/app_secret/status`（原 number/name 删除）。
- `_ensure_bs_registry(session, http_session, admin_app_id, admin_app_secret, bitable_token)`：
  - 唯一判断标准 = bs-bot 的 `app_id`（`CurrentValue.[app_id]="{self_app_id}"` 查询）。
  - 有记录 → `update_record`，无 → `insert_records`；字段 device/app_id/app_secret/status=active。
  - 同时把 `session.tenant_key`（事件 header 带）回写 bs-bot account 的 `tenant` 字段。
  - best-effort：内部吞 RuntimeError 只 log warning，不影响 setup/resume 主流程。
- 调用点：`setup_provider` 和 `resume_provider` 末尾（均持有 admin bitable_token + app_id/app_secret）。

## 原因

- S 计数器原为"预留、永不分配"，且 bs-bot 创建早于 admin-bot/bitable，读不到 counter → 删掉，改用 device_name 区分 bs-bot。
- tenant 之前恒空：`accounts.create_bot` 写 `poll_data.get("tenant_key","")` 但 poll_data 无 tenant_key；真正来源是飞书事件 header，故在 setup/resume 时回填。

## 测试

全量 `python3.11 -m pytest tests/ -q` 459 passed（新增 `_ensure_bs_registry` 2 例：insert+回填 tenant / update）。
