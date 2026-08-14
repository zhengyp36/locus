# CogOS — Phase C 联调 3 bug 修复

> 2026-08-14。代码改动未提交，在 `~/codex/cogos`。三个问题是一条因果链，根子在问题 1。

## 根因

1. **缺 patch 授权步骤（根因）**：`setup_provider` 在 OAuth 建完 admin-bot 后直接进 `_configure_admin_bot` 去 PATCH scope，但 OAuth 设备流（`core.py` `archetype=PersonalAgent`）建的 bot 天生没有 `application:application:patch` 自管理权限 → PATCH 被拒（`99991672`）。该有的料其实都齐了但没接上：`bot_manifest.BOT_PATCH_PERMISSIONS` 已定义未使用，`core.url.auth(app_id, permissions)` 引导链接生成器已存在未调用，旧 spec `01b-request-patch-permission.md` 早已写明这步。
2. **重试不可续（连锁）**：`save_account` 落盘在 step 3，失败于 step 1 时 app_id/app_secret 丢失，重试从头 OAuth 又建新 bot 泄漏应用。
3. **重试后卡片无按钮（连锁）**：重试重新进 OAuth，`running=True` 时 `build_card` 隐藏全部按钮，卡死等 600s 超时。

## 修复（bs_provider.py + bs_card.py）

- **`_save_admin_account(bot_id, fields)`**（新）：幂等 merge 到 `bot-{bot_id}.json`，替代 `save_account` + 手工改文件。顺带修掉一个隐藏 bug：旧代码 `bot_file = ACCOUNTS / f"{bot_id}.json"` 漏了 `bot-` 前缀，导致 bitable_token/bitable_url 从来没真正落盘（`resume_provider` 读不到 bitable 的根因之一）。
- **`setup_provider`** 重排：
  - OAuth 后**立即** `_save_admin_account` 落盘；开头检测 `bot-admin-{provider}.json` 已存在则跳过 OAuth（重试不再泄漏）。
  - OAuth 与 `_configure_admin_bot` 之间插入 patch 授权步：`url.auth(app_id, BOT_PATCH_PERMISSIONS)` 发链接 + 等用户确认。
  - `_configure_admin_bot` 成功后写 `patch_granted=True`；Bitable 后写 bitable 字段。重试时 `patch_granted` 为真则跳过再次要授权。
  - 新增 `on_patch_permission(app_id, url)` 回调参数，由卡片层提供（阻塞等确认）。
- **`bs_card.py`**：
  - `build_card` 新增 `awaiting_patch` 态 → 渲染「已完成授权」+「取消」按钮。
  - `handle_card_action` 处理 `confirm_patch`；`cancel` 时也唤醒等待中的 event。
  - `_run_setup` 提供 `on_patch_permission`（`asyncio.Event` 阻塞，`wait_for` 600s 超时）；异常处理加 guard，用户主动取消时不用 FAILED 覆盖 CANCELLED。

## 测试

- 新增 `tests/feishu/test_bs_provider.py`（`_save_admin_account` 幂等 merge / 新文件）。
- `test_bs_card.py` 加 3 用例（awaiting_patch 按钮、confirm 清标志、cancel 清标志）。
- 全量 `pytest tests/ -q`：377 passed，1 failed（`test_workdir_switch` 因残留 daemon 进程 14244 计数干扰，与改动无关，孤立重跑仍失败）。

## 下一步

- 联调验证 Phase C 全流程（3 bug 修复未提交，与 Phase C 一起验证）→ 提交。
- 待办仍在 ISSUES.md：speak 用 `user_id` 需 `contact:user.employee_id:readonly` 权限，建议 bs-bot 与管理员通信统一 `bot["open_id"]` + `receive_id_type="open_id"`。
