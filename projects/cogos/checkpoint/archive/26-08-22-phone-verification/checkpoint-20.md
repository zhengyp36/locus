# Checkpoint 20 — 会话4 异常边界已实施

> 按 checkpoint-19 设计实施:错误透传 → 自动延时重连 → 失败结果可观察。未 commit。

## 改动清单

### telecom.py(解 25 断连感知)
- `_reader` 断连分支:`msg is None` → `_handle_disconnect()` 同步清理 + `await _on_disconnect()` 通知。
- 新增 `_handle_disconnect()`:`_sock=None` + 未决 pending future 全部 `set_exception(ConnectionLost("connection lost"))` + `_pending.clear()` + `_tasks.clear()`。

### model.py(解 24 可观察)
- `Chat` 加 `members_error: str = ""`;`chat_to_dict`/`chat_from_dict` 序列化。

### phone.py
- `__init__` 加 `_reconnect_tasks`、`_on_disconnect`、`_on_error`。
- `listen(on_notify, on_msg, on_disconnect=None, on_error=None)`:逐卡透传 `_make_on_disconnect`/`_make_on_error`。
- `_make_on_disconnect(number)`:先通知使用者的 `on_disconnect(number)`,再 `create_task(_reconnect(number))` 存 `_reconnect_tasks`。
- `_make_on_error(number)`:通知使用者的 `on_error(number, err)`。
- `_reconnect(number, delay=1.0)`:sleep 后 `reconnect(number)`;CancelledError 上抛,其余 warning;finally 从 `_reconnect_tasks` 移除。
- `reconnect(number=None)`:复用旧 client 重 `startup()`(保留回调),失败标 `status="failed"` 并 `_save_cards`,成功标 `ok` + `sync_groups()`;无 number 时重连所有卡。
- `shutdown()`:先 cancel + await 所有 `_reconnect_tasks`,再逐 client shutdown。
- `sync_groups()` 返回 `{number: {ok, groups, error}}`(per-card fail-open,替代纯 warning)。
- `_ensure_group_session` 拉 members 失败:记 `data["members_error"]=str(e)` 持久化 + `chat.members_error`;成功时 `pop("members_error")`。
- `add_card` 去掉 `sync_groups` 的 try/except(sync_groups 不再抛)。

## 测试

- `tests/feishu/test_telecom.py`:新增 `TestDisconnect`(pending 请求收 ConnectionLost / 无 pending 清理)。
- `tests/phone/test_phone.py`:新增 `TestMembersPullError`、`TestSyncGroupsResult`、`TestDisconnect`(通知+调度重连 / 自动重连)、`TestReconnect`(失败标 failed / 恢复 ok)。
- 全量 **642 passed**(原 633,新增 9)。

## 关键决策落实(死锁规避)

- 断连清理在 `_reader` 内先 `_tasks.clear()` 再 `_on_disconnect()`,故 on_disconnect 里 create_task 的重连不会撞 `_do_listen` 的 `if self._tasks: return`。
- 重连走独立 task + `sleep(delay)`,天然等旧 reader 退场;shutdown 取消未完成重连 task。

## 遗留

- `_heartbeat` task 在断连后未被显式取消(design 用 `_tasks.clear()` 而非 cancel);旧 heartbeat 若在重连前醒来 `_sock=None` 会自行 return,若重连快会残留并发心跳(多写一次 hb,无功能影响)。未处理。
- on_error 仍是死通路(daemon 不发 error 帧),本次只接好 Phone 侧透传,未造 error 帧。
