# 260818 — agent-bot 创建流程两处修改

## 目标

修改 cogos 的 agent-bot 创建流程（`bs_agent.add_agent`），两件事：

1. 创建 agent-bot 过程中，号码记录的状态**不写 `active`，改写 `init`**（云端 agent_registry + 本地账号文件两处一致）。
2. 在创建 agent-bot 的最后步骤之后，**仿照 admin-bot 的建表方式**，用 agent-bot 自己的账号（app_id/app_secret）为它建一个 Contact bitable：
   - bitable 命名 `{number}-Contact`，例如号码 `A0012` → `A0012-Contact`
   - 内含一张 `contact` 表，字段：`number`、`chat_id`、`open_id`（均为文本）
   - 建表后把 `bitable_token`/`bitable_url` 落盘到本地账号文件

## 代码位置（本体 `~/codex/cogos`）

- 创建流程入口：`cogos/feishu/bs_agent.py` 的 `add_agent()`（第 106 行起）
- 关键步骤（现有顺序）：
  - `bs_agent.py:134` 读 counter 分配号码 `A{next_n:04d}`
  - `bs_agent.py:165-177` OAuth 建 agent-bot + 落盘
  - `bs_agent.py:210-216` `bh.insert_records` 写 `agent_registry`（**status 在此，第 215 行**）
  - `bs_agent.py:217-219` `bh.increment_counter` counter+1
  - `bs_agent.py:221-224` `_save_admin_account` 落盘本地 `status`/`expires_at`（**status 在此，第 222 行**）

## 修改点清单

### M1 — 状态改 init（两处字符串 + 一个 select 白名单）
- `bs_agent.py:215`：`"status": "active"` → `"status": "init"`
- `bs_agent.py:222`：`"status": "active"` → `"status": "init"`
- `bs_provider.py:13` `STATUS_OPTIONS`：加一项 `{"name": "init", "color": 2}`。
  原因：`agent_registry.status` 是 select 字段，选项白名单由 `STATUS_OPTIONS` 提供（`bs_provider.py:24-25` 的 `_select`），不加 `init` 则写入会被 bitable 拒绝。

### M2 — 建 Contact bitable
- 新增函数 `_create_contact_bitable(http_session, app_id, app_secret, tenant_key, number)`，放在 `bs_agent.py`，仿照 `bs_provider.py` 的 `_create_bitable_with_schema`（第 175 行），但精简为：建 app（name=`{number}-Contact`）→ 建一张 `contact` 表 → 加 3 个文本字段 → 删 Feishu 自动生成的默认表。**用 agent-bot 自己的 `app_id/app_secret`**（bitable 归 agent-bot 所有，非 admin）。
- 在 `add_agent` 里 `increment_counter` 之后调用它，并把返回值 `bitable_token`/`bitable_url` 合并进 `_save_admin_account` 落盘（`bs_agent.py:221-224` 那处）。

## 隐性依赖 / 风险（改后需留意）

1. **存量 provider 的 agent_registry 表**：旧 bitable 的 `status` select 字段没有 `init` 选项。代码改了之后，旧 provider 下 `/add-agent` 写 `init` 会失败。需手动给存量表的 status 字段补 `init` 选项，或后续补迁移逻辑。（新 provider 不受影响，建表时用新 `STATUS_OPTIONS`。）
2. **`refresh_agent_account`（`bs_agent.py:297`）**：第 326 行 `if status != "active":` 会把非 active（含 `init`）账号在下次心跳重校验时写成 `inactive`。当前 agent 尚未 startup/激活（WS 不监听），暂不触发；但"init → active"的激活流程后续要处理这里的判定，避免 init 被误判失效。
3. **expires_at**：init 状态本不该有 12h TTL 过期语义，但本次保持原有写入（`bs_agent.py:223` 不变），是否调整留待激活流程一起定。

## 执行状态

- [x] M1 状态改 init
- [x] M2 建 Contact bitable

（测试 `python3.11 -m pytest tests/ -q` → 457 passed；无 lint/typecheck 配置）
