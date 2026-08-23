# Checkpoint 28 — get_members 自阻塞修复（2A：reader 回调异步分发）

## 当前问题

phone 侧 telecom `_reader` 单协程内 `await` 回调，回调里发 get_members RPC 等 ack，而 ack 须同一 reader 读回 → 自阻塞 30s（checkpoint-27 定位）。本次只做 2A，不做 1（skip_pull），接受双拉 RPC。

## 已做修改

- `cogos/feishu/telecom.py:253-256` — `__init__` 增 `_callback_tasks: list[asyncio.Task]`。
- `telecom.py:427-439` — 新增 `_spawn_callback(coro)`（create_task + 进 `_callback_tasks` + done_callback）+ `_on_callback_done(task)`（移除跟踪、cancelled 跳过、异常 `logger.warning("agent callback failed: %s")`）。
- `telecom.py:456-464` — `_reader` 内 members_changed / message 回调由 `await` 改 `_spawn_callback(...)`；`_ACK_TYPES` 帧仍 `_handle_ack` 同步处理，reader 保持读 ack 能力。
- `telecom.py:536-546` — `shutdown` 增 cancel/await `_callback_tasks`（与 `_tasks` 合并）。
- `tests/feishu/test_telecom.py` — 新增 `_LoopbackSock`（get_members 请求回喂 ack）+ `TestReaderDispatch.test_members_changed_callback_does_not_block_ack`：回调内 `_get_members`，断言收到全量 members，证明 reader 不被回调阻塞。

## 已读代码要点

- `telecom.py:441-464 _reader`：ack 帧 → `_handle_ack`（:474 按 request_id set pending fut）；members_changed/message 帧 → 回调。改后回调脱离 reader 协程，reader 可继续 `_sock.read()` 读回 ack。
- `telecom.py:381-400 _request`：`await wait_for(fut, 30)`，fut 由 reader 内 `_handle_ack` set_result —— 自阻塞根源，2A 解除。
- `protocol.py:277-284 SockFile.write`：单次 `writer.write()` 无 await，事件循环内原子，多任务并发写不 interleave（写并发非新增风险）。
- `agent_conn.py:407-434 emit_members_changed`：daemon 对 phone 发 members_changed 帧，`added`/`removed` 是相对 daemon 内存快照的增量；首次发射全员塞 added。

## 关键结论 / 决策

- 2A 根治：回调脱离 reader 后，get_members 兜底正常返回，成员全量拉取语义保留（比 skip_pull 干净，避开"空基线 delta 套空集"的不全问题）。
- YZ 拍板：只做 2A，不做 1（skip_pull），接受 first-message 且 members 空时双拉 get_members RPC（幂等、仅浪费）。
- 消息顺序：reader 的 `read()` 是天然串行点，正常路径 append 顺序仍保持；仅"首消息 + members 空 + 两帧同批到达"时顺序可能乱——已接受。
- 写 socket 并发无虞（单次 write 无 await 原子）。

## 遗留 / 坑

- 测试 643 passed（+1 回归）；**真机验证未做**（待 /undo 后 YZ 跑真机：确认 30s 消失 + members 增减仍正确）。
- 真机验证点：真人进退群驱动 members_changed，观察 `request timed out: get_members` 不再出现；首条群消息 members 空时双拉是否正常。
- checkpoint-27 计时代码暂留（定位用），真机验证后考虑移除/降级。
- codebase.md（git）30s 段仍是 checkpoint-22「串行排队」旧结论，需 append 修正（见下）。
