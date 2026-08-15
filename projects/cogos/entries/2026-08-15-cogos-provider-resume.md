# CogOS — provider.json 落地 + resume 验证 gap

> 2026-08-15 会话。provider.json 改造已落地并提交（`d84660d`）；test_workdir_switch 修复已提交（`03854d0`）；resume gap 未解、待真机验证。

## provider.json = 3 字段索引层（已落地）

`providers/{name}/provider.json` 只存指针，不存凭据：

```json
{
  "provider": "COGOS007",
  "admin-bot": "admin-COGOS007",
  "bs-bot": "COGOS007"
}
```

- `admin-bot`/`bs-bot` 是 account-id（省略 `bot-` 前缀），= `load_bot()` 入参；凭据在 accounts/。
- `bitable_token`/`bitable_url` 不存 provider.json，消费端 `load_bot(admin-bot)` 读（bot-admin-*.json 里都有）。
- 落地改动：`_save_provider` 幂等 merge 写 provider/admin-bot + 删平级 `{name}.json`（参照 `_save_admin_account`）；`setup-bs` 的 `device-bot`→`bs-bot` 去前缀、merge 写；已迁移 COGOS001~007（002/003 无 admin，仅 bs-bot）。
- `bs-bot` 单值是多设备折中，未来变列表。

## resume 验证 gap（未解）

- 输入（保留）：`/resume <app_id> <app_secret>` 参数、`accounts/bot-admin-*.json`、云端 bitable admin_registry 表。
- 输出（删了模拟未恢复）：`providers/{name}/provider.json`、config.json 的 providers 条目 + default-provider。
- 做法：只删输出留输入，再 `/resume`。清理到「创建 admin-bot 之前」是错的（会把输入一起删光）。
- gap（实现缺陷）：`resume_provider` 的 bitable_token 从本地 `accounts/bot-admin-*.json` 读，非云端查。真换设备（空 accounts）→ `get_bot_by_app_id` KeyError → 失败分支。只能验「账号在本地、provider 配置丢」的半恢复，验不了跨设备。对应地图不变量 3 兑现缺陷。

## 附带：test_workdir_switch 泄漏修复（已提交）

- `tests/feishu/test_workdir_switch.py`：`work_dir` 记录提前到 `init` 成功后（原在 `assert count==1` 之后，失败时泄漏 `default-xxxx` 目录）；清理移入 `finally`（`ignore_errors=True`）。
- 根因：`Config._init_once` 在 global.json 缺失且 `default/` 已存在时随机后缀建新目录；test 失败时 finally 不 rmtree。
