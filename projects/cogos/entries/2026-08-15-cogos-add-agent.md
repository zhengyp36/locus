# CogOS — /add-human /add-agent 实现（号码注册 + counter 接线 + PIN）

> 2026-08-15 会话。resume 收尾后实现数据管理两命令。截至会话结束代码未提交。

## 决策（与人确认）

- agent 账号 id = 号码（`accounts/bot-A0001.json`），不带 `agent-` 前缀。
- 事件订阅保留：全量 `BOT_EVENTS`（6 个，一个不漏）。
- scope 全量：复用 `_configure_admin_bot` 加 `BOT_SCOPES`（只能多不能少）。
- PIN：agent_registry 的 pin 列早已有；add-agent 生成 `secrets.token_hex(4)`，写账号 + agent_registry。
- 无 tenant 校验：agent 账号 tenant 直接从 admin 账号复制（走 bs-bot 通信，天然同租户）。

## 实现

- `bs_agent.py`（新）：`_load_admin`（provider.json → admin-bot 指针 → `load_bot` 读 app_id/app_secret/bitable_token）；`add_human`（校验 user_id → 写 human_registry）；`add_agent`（读 counter → OAuth → patch → scopes/可见性 → 事件订阅 → PIN → 写账号 + agent_registry + counter+1）；`AgentWorkspace`（`workspace/agent-{id}.json`）。
- `bs_agent_card.py`（新）：卡片 3 态（开始创建 / 已完成授权 / 已订阅事件），镜像 bs_card。
- `bs_setup.py`：新增 `/add-human` `/add-agent`（`@msg_command`）。
- `handler.py`：`agent_*` 卡片动作路由到 bs_agent_card（按 `action.startswith("agent_")` 分派）。
- 复用 setup 的 `_oauth_create_admin_bot`/`_configure_admin_bot`/`_save_admin_account`；OAuth 后立即落盘防泄漏，重试时复用已建账号跳过 OAuth（读 `bot-{number}.json` 判断）。

## 真机问题 → 修复

1. **命名提示缺失**：OAuth 链接未提示命名，真人把 app 命名成「陈奕迅」而非「陈奕迅(A0001)」→ 链接文案改为「将应用命名为「名字(Axxxx)」」。counter 在 OAuth 前已读、整流程成功后才 `increment_counter`（+1）。
2. **错误码后重试成功**：patch 权限传播延迟（`99991672`）→ `_configure_admin_bot` 特判，报错「patch 权限尚未生效 (code=99991672)，请稍候点击「重试」」。重试安全：失败时 counter 未 +1、账号已落盘、复用账号跳 OAuth。

## 测试

- `test_bs_agent.py`（新）24 个：AgentWorkspace / build_card / handle_card_action / add_human / add_agent（含复用、命名提示）。
- 全量 431 passed、1 failed（test_workdir_switch 残留 daemon 环境干扰，与改动无关）。

## 真机

- COGOS008 下 `/add-agent 陈奕迅` 跑通：`bot-A0001.json` 落盘（name=陈奕迅、patch_granted=true、pin=d6922ac7）。当时命名提示未生效，故 name 无号码后缀。

## 遗留

- agent-bot 尚未激活：EventHandler 只注册 test/bs，agent 未注册、WS 不监听（属 agent 运行时）。
- `startup/send/shutdown` + PIN 鉴权、双 bot 群 + @all、bot↔bot 私聊仍 ⏳。
