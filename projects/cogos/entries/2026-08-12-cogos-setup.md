# CogOS — Phase 0/1 实现 + provider 字段改造 + A 阶段卡片模拟

> 2026-08-12。设计文档 `~/codex/cogos/docs/comm-full-design.md`，实施计划 `~/codex/cogos/docs/comm-impl-plan.md`。

## Phase 0：bs-bot 命令机制（提交 71abae9）

- `cogos/feishu/bs_cmd.py` — `@msg_command` 消息命令框架（注册 + dispatch + admin 校验）
- `cogos/feishu/bs_setup.py` — `/setup`、`/resume`、`/help` 消息命令
- `cogos/feishu/handler.py` — 注册 `bot_type="bs"` 的 EventHandler
- `cogos/feishu/daemon.py` — 启动时自动扫描 `bot_type="bs"` 的 bot 并激活 WS
- `cogos/feishu/accounts.py` — `create_bot()` 接受 `bot_type` 参数
- `cogos/feishu/provider.py` — `setup-bs` 增强：bot_type="bs"，IPC update-config + add-bot
- `cogos/feishu/env.py` — 新增 `update-config` daemon 命令
- 真实验证：`/help` 返回命令列表、非管理员 `/setup` permission denied ✓

## Phase 1：Provider 搭建（提交 7b67561）

- `cogos/feishu/bot_manifest.py` — BOT_SCOPES、BOT_PATCH_PERMISSIONS、BOT_EVENTS
- `cogos/feishu/bitable_helper.py` — Bitable CRUD 封装
- `cogos/feishu/bs_provider.py` — `setup_provider()` / `resume_provider()` 编排

`/setup` 流程：OAuth 授权 → 加 11 scope → 可见性 → 保存 admin-bot → 建 Bitable 7 表 → 写 counters + admin_registry → 保存 provider。
`/resume` 流程：验证凭据 → 查 admin_registry → 注册 provider → 写 devices/instances。

## provider 字段改造（提交 402ddf1）

- bot/human JSON 增加可选 `provider` 字段；bs-bot 必填（`create_bot` 校验，`bot_type="bs"` 无 provider 抛错）
- `/setup` 不再带参数，从 `session.bot["provider"]` 读取
- `create_bot()` 加 `provider` 参数、`cmd_create_bot` 加 `--provider`、`setup-bs` 传 provider

## A 阶段：卡片模拟（未提交）

目的：先验证卡片交互链路（发卡片 → 按钮回调 → 解析 value → patch 更新），不碰真实 API。

- `session.py` — `send_card()` 返回 message_id
- `cogos/feishu/bs_workspace.py` — 新建，setup 状态落盘 `sessions/{app_id}/workspace/setup-{id}.json`（step/status/message_id/steps）
- `cogos/feishu/bs_card.py` — 新建，`build_card()`（✅/⬜ 逐行打勾 + 确认/取消按钮，value 带 step 快照）+ `handle_card_action()`（confirm 递增 / cancel / 快照校验）
- `bs_setup.py` — `/setup` 发卡片 + 防重（done 拒绝、in_progress 提示、cancelled/failed 重开）
- `handler.py` — `handle_bs` 分发 `CardActionTriggered`：`loop.create_task` 异步处理 + 返回"处理中" toast

测试：`tests/feishu/test_bs_card.py` 新建，370 tests pass。
真实验证：用户确认通过（卡片原地更新、逐行打勾、防重、取消均正常）。

## 手动测试：创建后流程（2026-08-12 跑通）

OAuth 创建流程本身已验证过是通的，跳过创建，直接用已有 admin-bot 走创建后流程。

- admin-bot：app_id `cli_aaf63d948ab89d25`（凭据存 `accounts/bot-admin-COGOS001.json`，app_secret 不记录）
- 结果：凭据验证 ✓ → 查 scope 缺 9 个 → **添加 9 个 scope 成功（code 0）** → 建 Bitable 7 表 ✓ → 写 counters + admin_registry ✓ → 保存 provider ✓
- Bitable token：`F00mbGqlDanXnjs4qgTce4uUnac`，tenant_key：`1abed56748075c80`

关键结论：**add scope 在该账号上直接成功**，说明 patch 权限（application:application:patch + admin:app.visibility）已预授权，真实流程无需 `awaiting_scope_retry` 分支。

## Phase C：卡片 + 创建合一（2026-08-12，未提交）

把 A 阶段的模拟卡片换成真实创建流程。`/setup` 发卡片 → 点「开始创建」→ 真实走 OAuth→权限→Bitable→注册→保存，卡片逐行打勾；失败显示「失败：原因」+ 重试按钮。

改动：
- `bs_card.py` — `build_card` 重写（start/cancel/retry 按钮，note 行显示进度/错误）；`handle_card_action` 的 start 分支调 `_run_setup`（后台 task 里 `await setup_provider`，WS 层已 `loop.create_task` + 返回"处理中" toast，所以长轮询不阻塞）
- `bs_provider.py` — `setup_provider(session, name, on_progress=None)` 加回调；拆 `_oauth_create_admin_bot`（纯 OAuth）+ `_configure_admin_bot`（scopes+visibility+info）；失败改 raise RuntimeError
- `session.py` — `Session` 加 `tenant_key` 属性，`EventHandler.get().on_event` 从 `evt.header["tenant_key"]` 注入
- `bitable_helper.py` — 新增 `list_tables` / `delete_table`，创建 Bitable 后删系统默认表
- `bs_workspace.py` — `SETUP_STEPS` 改为真实 5 步；`new_state` 加 `running`/`note`

测试：`test_bs_card` 19 通过；全量 372 通过，仅 `test_workdir_switch` 因旧 daemon 进程（44546/44547，23:12 起）干扰进程计数失败（与改动无关）。

## 发现的问题（下次修正）

1. ~~tenant_key 来源~~ ✅ Phase C 已改为从 WS header 取
2. ~~Bitable 默认表~~ ✅ Phase C 已删默认表
3. `speak` 命令用 `user_id` 发消息需 `contact:user.employee_id:readonly` 权限；bs-bot 与管理员通信应统一用 `bot["open_id"]` + `receive_id_type="open_id"`。（仍待处理）

## 下次起点

- 联调真实验证 Phase C：重启 daemon（旧进程 44546 在跑）→ bs-bot 发 `/setup` → 点开始创建 → OAuth 授权 → 逐行打勾 → 验证落盘
- 联调通过后 A 阶段 + Phase C 一起提交

---

## 联调发现（2026-08-13）

### 缓存失效 bug（已修，随 Phase C 一起提交）

`accounts.py` `_bot_by_app_id_cache` 模块级缓存只建一次、从不失效。运行期 `setup-bs` 新建的 bs-bot（COGOS002）事件进来解析不到 bot → `/help` 无反应，日志 `bot not found for app_id`。修复：`get_bot_by_app_id` miss 时重建缓存重试一次（自愈）。注意不能只在 `save_account` 里失效——`setup-bs` 落盘发生在 CLI 子进程，daemon 进程缓存碰不到。

### COGOS001 /setup 提示"已创建完成"

stale workspace `run/sessions/cli_aaf6d61e9d78dd18/workspace/setup-COGOS001.json` status=done（A 阶段产物）。防重设计如此，删文件即可重跑。

### Phase C 流程 3 个问题（已修 2026-08-14，见 projects/cogos/entries/2026-08-14-cogos-bugfix.md）

1. **缺 patch+visibility 授权步骤（关键）**
   - OAuth registration 创建的 admin-bot 无 `application:application:patch` 权限。
   - `_configure_admin_bot` 的 add_scopes PATCH 直接失败：`code=99991672, Access denied ... required: [application:application:patch]`。
   - 旧 spec `01b-request-patch-permission.md` 早已写明：创建 bot 后先引导人工加 patch 权限（`https://open.feishu.cn/app/{app_id}/auth?q=application:application:patch` + 等用户确认），再加 scope。Phase C 漏掉这一步。
   - `BOT_PATCH_PERMISSIONS = ["application:application:patch", "admin:app.visibility"]` 已定义但 grep 证实**从未被使用**。
   - 修复方向：`setup_provider` 在 OAuth 后加一步——发 `url.auth(app_id, BOT_PATCH_PERMISSIONS)` 链接，等用户确认后再 `_configure_admin_bot`。
2. **重试不可续**
   - admin-bot 落盘在 step 3（`_configure_admin_bot` 之后），失败于 step 1 时未落盘。
   - 重试从头走 OAuth → 又建一个新 bot → 泄漏应用（COGOS002 已泄漏 `cli_aaf627bb80f89d14`）。
   - 修复方向：OAuth 创建 admin-bot 后立即 `save_account`；重试时若 admin-bot 已存在则跳过 OAuth。
3. **重试后卡片无按钮**
   - 重试 `set running=True` → `build_card` 隐藏按钮 → 卡在「OAuth 授权并创建 admin-bot」无按钮，等 600s 超时。
   - 是问题 2 的连锁：重试又进 OAuth 等待，用户不会再次授权。
