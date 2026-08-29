# Checkpoint 27 — get_members 30s 超时根因定位（reader 自阻塞）

## 当前问题

get_members RPC 真机稳定复现 30s 超时，30s 花在哪未坐实。加时延统计后定位。

## 已做修改

- `cogos/feishu/daemon.py` — 读循环每个 handler 计时（>1s 打 warning）；`_handle_agent_get_members` 加 total/ensure/resolve 计时。
- `cogos/feishu/agent_conn.py` — `resolve_group_members` 六段分步计时（ensure/list_members/resolve_human/tracker/load_bot）。
- `cogos/feishu/tracker.py` — `rebuild` 锁等待计时（>0.5s 打 log）+ `build` replay/snapshot 计时。
- 测试 642 passed。

## 已读代码要点

- `telecom.py:426 _reader` 单协程循环；`members_changed` 帧 `await self._on_members_changed(...)`（:443）、`message` 帧 `await self._on_msg(...)`（:447）。回调期间 reader 停读 socket。
- `telecom.py:381 _request` 写 socket 后 `await wait_for(fut, 30)`（:396）；fut 由 `_handle_ack`（:457，reader 内）set_result。
- `phone.py:378 _make_on_members_changed` 先 `_ensure_group_session`（:380）后才用 added/removed 写 members（:385-393）。
- `phone.py:202 _ensure_group_session` members 空时 `await tchat.get_members()`（:216-218）。
- `daemon.py:659 _handle_agent_get_members` → `resolve_group_members`（agent_conn.py:291）= list_members(HTTP) + tracker.rebuild + load_bot。

## 关键结论 / 决策

- 根因：phone 侧 telecom `_reader` 单协程，`await on_members_changed` 回调里同步发起 `get_members` RPC 等 ack，而 ack 必须由同一 reader 协程读回 → 自阻塞 30s。不是 daemon 慢/排队/HTTP 长尾。
- 证据（真机时间线）：daemon get_members handler 总 1.387s（resolve 1.386s），14:30:54 回 ack；phone 14:30:53 发请求，14:31:23 才超时（=发请求+30s），中间 28.6s ack 躺 socket 无人读；超时后积压帧 9ms 批量释放。
- YZ 拍板修复：**1（`_make_on_members_changed` 加 `skip_pull` 跳过 get_members 兜底）+ 2A（telecom `_reader` 回调改 `asyncio.create_task` 异步分发，reader 保持读 ack 能力）**；2B（`_request` 防重入快速失败）作可选护栏。

## 遗留 / 坑

- 修复未实施。下一步：先做 1，真机验证 30s 消失；再评估 2A 并发落库影响后实施。
- 计时代码暂留（定位用，修复验证后考虑移除或降级）。
- `_make_on_msg`（phone.py:353）同样在 reader 回调里走 get_members 兜底，同类隐患，由 2A 根治。
