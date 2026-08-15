# 2026-08-15 cogos agent 账号 id 加 provider 前缀

## 问题

agent 账号文件名 `bot-A0001.json` 用裸号码，而号码 Axxxx 只在单 provider 内唯一（不变量 6），跨 provider 会冲突覆盖：`_save_admin_account` 是 merge 幂等，COGOS002 再 add-agent 得到 A0001 会直接覆盖 COGOS001 的账号。admin-bot（`admin-COGOS001`）/bs-bot（`COGOS001`）id 已含 provider，无此问题，只有 agent 裸号码中招。

## 方案（与用户讨论定稿）

- 接口层全名保持冒号 `COGOS001:A0001`（已定稿，`split_number` 按 `:` 拆，6 处文档不动）。
- 账号文件 id 用连字符 `provider-number`：`bot-COGOS008-A0001.json`（`:` 是 Windows 非法文件名字符）。
- 转换收敛到 `accounts.agent_account_id(provider, number)`，调用方不拼文件名。

## 实现（`2381ffc`）

- `accounts.py`：加 `agent_account_id(provider, number)` → `f"{provider}-{number}"`。
- `bs_agent.py`：`add_agent`/`refresh_agent_account` 里 `_save_admin_account(number, ...)` 与 `bot-{number}.json` 全改用 `agent_account_id(provider, number)`；JSON `id` 字段保持裸号码（无消费方用 id 字段定位文件）。
- `daemon.py`：`_load_local_agent(provider, number)` 重写；`_handle_agent_send(sock, provider, number, msg)` 补 provider；`_verify_pin`/心跳/`_handle_agent_client` 调用点透传 provider。
- 存量迁移：`bot-A0001~3.json`（provider=COGOS008）读 provider 字段幂等改名 `bot-COGOS008-A0001~3.json`。
- 全量 456 passed。

## 遗留

- `_agent_conns` key 保持冒号 `provider:number`（内存 key 无文件系统限制），与账号文件连字符是两套格式，靠 `agent_account_id` 收敛，外部不感知。
