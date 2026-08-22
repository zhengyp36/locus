# step-3 ensure init 主动云刷新

> 修复：本地 status=init 时 startup 拒绝且不自动云同步，导致"他设备 activate"后本地残留 init 卡死。

## 问题

- 现象：step-2 踩坑"本地账号 status=init 拒 startup"（`daemon.py:284`），须手动 `refresh_agent_account` 才能解开。
- 根因：`accounts.py ensure()` 的 `available` 判定把 init 算"可用"，本地 init 且 `expires_at` 未过期时直接返回，走不到 `_refresh()` 云端同步；主动刷新只在连接建立后的 `revalidate()`（`agent_conn.py:427`）里跑，而 startup 在连接建立前就被 deny 拦下。
- 触发场景：activate 在他设备/会话完成，云端 agent_registry 已 active，但本地 `bot-xxx.json` 残留 init（`_activate_agent_finish` 不回写本地 status）。

## 修改

- `cogos/feishu/accounts.py`：
  - `ensure()` 本地命中分支加 init 特判：`status=="init"` 时先 `await self._refresh()` 云同步，同步结果可用（active/init）则采用，失败（异常/空）fail-open 退回本地 init。
  - 新增 `import logging` + `logger = logging.getLogger("cogos.feishu.accounts")`，刷新异常打 warning。
  - active 态路径不变，零额外开销（非热点）。

## 验证

- 单元测试 `tests/feishu/test_accounts.py` 新增 `TestEnsureInitRefresh` 4 例：init→active 刷新、init→仍 init、init→异常 fail-open 返回 init、active 不触发刷新。全过（45 passed）。
- 真机手动验证：脚本把 `bot-COGOS002-A0005.json` 的 status 改 init，调 `AgentRef.ensure()` → 返回 active，本地文件同步回 active，恢复备份。通过。

## 遗留

- 全量测试 1 failed：`tests/feishu/test_bs_agent.py::TestAddAgent::test_full_flow` 断言 `name == "李四(A0001)"`（旧行为），与本次无关——step-1 bug#2 删除 bot_name 覆盖后该测试未同步更新。待后续修正。
