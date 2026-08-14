# ISSUES

## Phase C 联调遗留（2026-08-13，均待修）

### 1. 缺 patch+visibility 授权步骤（关键）

- OAuth registration 创建的 admin-bot 无 `application:application:patch` 权限。
- `_configure_admin_bot` 的 `add_scopes` PATCH 失败：`code=99991672, Access denied ... required: [application:application:patch]`。
- `BOT_PATCH_PERMISSIONS = ["application:application:patch", "admin:app.visibility"]` 已定义但从未被使用。
- 旧 spec `01b-request-patch-permission.md` 已写明：创建 bot 后先引导人工加 patch 权限（`https://open.feishu.cn/app/{app_id}/auth?q=application:application:patch` + 等用户确认），再加 scope。Phase C 漏掉这一步。
- 修复方向：`setup_provider` 在 OAuth 后加一步——发 `url.auth(app_id, BOT_PATCH_PERMISSIONS)` 链接，等用户确认后再 `_configure_admin_bot`。

### 2. 重试不可续

- admin-bot 落盘在 step 3（`_configure_admin_bot` 之后），失败于 step 1 时未落盘。
- 重试从头走 OAuth → 又建新 bot → 泄漏应用（COGOS002 已泄漏 `cli_aaf627bb80f89d14`）。
- 修复方向：OAuth 创建 admin-bot 后立即 `save_account`；重试时若 admin-bot 已存在则跳过 OAuth。

### 3. 重试后卡片无按钮

- 重试 `set running=True` → `build_card` 隐藏按钮 → 卡在「OAuth 授权并创建 admin-bot」无按钮，等 600s 超时。
- 是问题 2 的连锁：重试又进 OAuth 等待，用户不会再次授权。

## 其他

### speak 用 user_id 发消息需额外权限

- `speak` 命令用 `user_id` 发消息需 `contact:user.employee_id:readonly` 权限；bs-bot 与管理员通信应统一用 `bot["open_id"]` + `receive_id_type="open_id"`。
