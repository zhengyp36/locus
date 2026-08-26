# Checkpoint 19 — 会话4异常边界的感知缺口与修改思路

> 讨论结论:会话4异常边界(21-25)缺「phone 使用者感知」的方式。产出修改设计,待 /undo 后实施。

## 现状:异常感知三层

- **能感知**
  - `send` / `create_group` 同步失败 → `SendError` 从 telecom 冒泡(phone 不捕获)。
  - `add_card` 失败 → 返回 `Card(status="failed", status_reason=...)`(场景21/22 落这里)。
  - 卡不存在/未激活 → `ValueError`(`_resolve_send_card` / `_client_for`)。
- **静默吞(缺口)**
  - 场景24 `list_members` 失败 → `_ensure_group_session` 只 warning,members 空。
  - `sync_groups` 的 `list_chats` 失败 → 只 warning,无「哪卡失败」结果。
- **通路断(场景25 最严重)**
  - `ConnectionLost` 定义了(telecom.py:136)但从未被抛。
  - `_reader` 断连只 `_on_disconnect()` 就 return;`_sock` 不清理。
  - `Phone.listen` 不接 `on_disconnect`/`on_error` → 落默认 noop。
  - `on_error` 死通路:daemon 不发 error 帧,`_reader` 对未知帧 `continue` 丢弃(term.py 的 `on_error` 从未触发)。

## 修改思路(优先级 1→2→3)

1. **后台异步错误透传(解 25 感知)**
   - telecom `_reader` 断连:置 `_sock=None`、pending future 全部 `set_exception(ConnectionLost)`、清 `_tasks`,再 `_on_disconnect()`。
   - `Phone.listen` 加 `on_error`/`on_disconnect` 参数,逐卡透传给 `client.listen`。
2. **重连语义(解 25 恢复)**
   - Phone 存每卡 pin,新增 `reconnect(number=None)`:重 `startup()` + 恢复 `_clients`。
   - 不自动重连,由使用者在 `on_disconnect` 回调里决定。
3. **失败结果可观察(解 24 / sync_groups)**
   - `sync_groups()` 返回 `{number: {ok, groups, error}}`,替代纯 warning。
   - `_ensure_group_session` 拉 members 失败:记 `chat.members_error`(或走 on_error 回调)。

## 关键决策:on_disconnect 异步延时重连

- **同步重连会死锁**:`_reader` 断连时 `await _on_disconnect()`,此刻旧 reader task 仍在
  `_tasks` 列表;`reconnect → startup → _do_listen` 见 `if self._tasks: return` → 新 reader 永不启动。
- 且 `_tasks` 只在 `shutdown` 清空(telecom.py:510),断连路径不清,残留列表会挡重连。
- 修正三点:
  1. 断连清理放 `_reader` 内:`_sock=None` + pending `set_exception` + `_tasks.clear()` + `_on_disconnect()`。
  2. `on_disconnect` 只发通知 + `asyncio.create_task(reconnect_task)`,自身立即返回。
  3. 重连独立 task + 先 `asyncio.sleep(delay)` 再 `startup()`,天然等旧 task 退场;`shutdown` 取消未完成重连 task。
