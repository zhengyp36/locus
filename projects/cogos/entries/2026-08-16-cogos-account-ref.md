# 2026-08-16 — AccountRef 号码解析 + agent send 修复（bug2）

提交 `f7cfd1a`（amend 合并了 term.py 的 CancelledError 修复）。

## AccountRef（account_ref.py 新模块）

号码 `provider:number` → 账号的解析，用面向对象替代过程式 load/refresh 三连。

- 三级缓存：内存 15min（`MEMORY_TTL`，class 级 dict）/ 本地 6h（`LOCAL_TTL`，靠 `expires_at`）/ 云端；`HARD_TTL=6h` 本地过期后超过此时长强制失效（返 `{}`，不续命）。
- 类结构：`AccountRef` 基类（`_parse` + `from_number` 工厂按 number 首字母分派 A/H + `ensure` 流程 + `_load_local`/`_load_remote`/`_save_local`/`_refresh`/`_validate`），`AgentRef`/`HumanRef` 子类只定义 `path`/`remote_table`/`required_fields`。
- 文件命名：A → `bot-{provider}-{number}.json`，H → `human-{provider}-{number}.json`（`Config.ACCOUNTS_DIR` 下）。
- 云端 `_load_remote`：复用 `bs_agent._load_admin(provider)` 拿 bitable，`bh.query_records` 查表（A→`agent_registry`，H→`human_registry`），filter `CurrentValue.[number]="{number}"`，`_cell_value` 把每个 cell 归一化为 str。
- `_refresh`：`local`+`remote` merge（`{**local, **remote}`，remote 覆盖同名、local 独有 `open_id`/`patch_granted` 保留），`remote` 空返 `{}`（云端无记录=失效），`expires_at = now + LOCAL_TTL`，`_validate` 通过才 `_save_local`。
- `_validate`：`required_fields` 缺失（falsy）抛 `ValueError`；agent=`(app_id, app_secret, pin, status)`，human=`(user_id, status)`。

## bug2 修复

`daemon._handle_agent_send`：删 `prefixed target not supported` 分支，改 `AccountRef.from_number(to)` 解析 → 仅 `isinstance(ref, HumanRef)` 通过（否则 send_ack 拒绝）→ `ref.ensure()` 拿 account → `Session(bot, receive_id=account["user_id"], receive_id_type="user_id")` 发送。A 目标（agent→agent，open_id）留后。

## 其他

- term.py finally：`await` 已 cancel 的任务会重抛 `CancelledError`，而它属 `BaseException` 非 `Exception`，`except Exception` 捕不到 → 泄漏到 `asyncio.run`。补 `except asyncio.CancelledError`。
- 删 ISSUES「speak 用 user_id 发消息需额外权限」（已解决，agent 发送真机验证通过）。
