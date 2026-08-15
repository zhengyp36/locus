# CogOS — resume cloud-first 重写 + 跨设备验证

> 2026-08-15 会话。resume 从「本地 accounts 读 bitable_token」重写为「云端 drive API 查」，无账号跨设备恢复真机验证通过。提交 `a0e1092`。

## 关键发现：飞书无「列多维表格」接口

- 之前假设的 `GET /open-apis/bitable/v1/apps`（list apps）**不存在**，返回 404 + text/plain。
- 正确做法：`GET /open-apis/drive/v1/files`（不带 folder_token = 列 app 云空间），筛 `type=bitable`；file 的 `token` 就是 app_token，`modified_time` 是编辑时间戳。
- 需 `drive:drive` scope（BOT_SCOPES 已含）。

## resume_provider 新流程（cloud-first）

验 token → drive 列 bitable → 逐个查 admin_registry（filter `CurrentValue.[app_id]="{app_id}"`）→ 取 `modified_time` 最新 → `_save_admin_account`（幂等 merge）+ `_save_provider` → 写 devices/instances 表。

- 错误区分：query_records 抛 RuntimeError 时，仅 `"not found"`（表缺失 = 非 CogOS bitable）跳过，其余 `raise`（不掩盖真实失败）。
- 消息收敛：`cmd_resume` 开始一条 + 结果一条（`resume_provider` 统一返回字符串）。

## 验证1：无账号跨设备恢复（通过）

操作：删 provider.json 的 admin-bot 字段 + 移走 admin account（备份 `/tmp/kilo/bot-admin-COGOS008.json.bak`），凭 app_id/app_secret 发 `/resume`，bitable_token 正确取回、账号 + provider 索引重建。

3 处预期差异（resume 重建 vs setup 原账号）：
1. `name`：provider_name（`COGOS008`）vs app 真实名（`COGOS008-ADMIN`）
2. `patch_granted`：缺失（registry 未存，resume 无从恢复；无功能风险）
3. `bitable_url` 域名：drive 返回 `wcnqq2zpu3zn.feishu.cn` vs setup 拼 `{tenant_key}.feishu.cn`（token 一致，指向同一 bitable）

## 遗留

- 半恢复场景（账号在、只删 provider 配置）：**已裁决推迟、标未验证**。理由：触发罕见（账号在但 provider.json 单独丢）；与全恢复共用 `resume_provider`，无隐藏失败模式；唯一差异是 `name` 被 `provider_name` 覆盖（admin 的 name 是装饰字段，admin 不监听 WS、不发消息、只读写 bitable，无功能影响）。真名问题已独立记入下一条，不因推迟漏掉。
- `name` 是否还原 app 真实名待定（可选：抽 `_get_app_name`，resume 也调 app info API，一次解决全/半恢复共同待定项）。
