# 2026-08-15 cogos 账号失效/刷新 实现

## 会话内容

- 审视 `docs/agent-account-refresh.md`（ensure→verify + 12h 失效方案），提 3 关键疑问（refresh 返回值歧义 / startup 阶段过期+网络错误行为 / `_agent_conns` 跨 provider key 冲突）+ 2 小确认。
- 与用户定稿 7 条精确化规则，关键变化：**弃 ensure→verify，改 refresh 无返回值 + load 本地判定**。

## 定稿规则（写入详细设计 docs/agent-account-refresh-design.md）

- `refresh_agent_account` 无返回值，只写本地；失效判定统一 load 本地读 `status`/`expires_at`。
- 单一判定规则：`now > expires_at` → 向云端 refresh 重新确认；startup fail-closed、心跳 fail-open。
- startup 本地缺失 → 先 refresh 物化（换设备可恢复）；缺失/过期 + 网络错误 → 拒。
- `_agent_conns` key 改 `provider:number`（与 term 入口格式一致）。
- 无记录 = inactive，落 `status=inactive` + `expires_at = now + TTL`。
- 老账号自愈：无 `status`/`expires_at` 字段 → `expires_at` 缺省 0 判过期 → 首次 startup 自动 refresh 补齐，无迁移。
- 时间源：`expires_at`/`next_revalidate_at` 用 `time.time()`（墙钟），`last_hb` 用 `time.monotonic()`。

## 实现（已提交 `ae02c0b`）

- `bs_agent.py`：`AGENT_ACCOUNT_TTL = 12*3600`；`refresh_agent_account`（复用 `_load_admin`/`_cell_value`/`_save_admin_account`/`bh.query_records`；active 走 merge 保留 `open_id`/`patch_granted`/`tenant`/`id`/`type` + 重算 `expires_at`；非 active/无记录只写 `status`+`expires_at`）；`add_agent` 注册后补写 `status=active`+`expires_at`。
- `daemon.py`：`AGENT_REVALIDATE_COOLDOWN=300`；`_load_local_agent(number)`（load_bot 失败返 `{}`）；`_verify_pin` 重写（缺失/过期→refresh→status 判→pin 比对，fail-closed）；`_handle_agent_client` startup 按新 key 写 conn（`expires_at`/`next_revalidate_at=0`）；`hb-req` 分支心跳重校验（fail-open + 300s cooldown + inactive break 断连）；踢旧按 key。
- `protocol.py` 不改。测试：`TestAgentClient` 增 `_load_local_agent` mock；新增 `TestAgentVerifyPin`(6) / `TestAgentHeartbeatRevalidation`(5) / `TestRefreshAgentAccount`(5)。全量 456 passed。

## 遗留

- 无 revoke 命令（云端 status 改 inactive 无入口，失效真机端到端不可触发，只能 mock 单测）。
- 心跳 refresh 内联 await 最坏 30s 阻塞，先接受，真机见延迟再拆 task。
