# ENTRY — meta-layer 代码检视与修复（2026-10-25）

一句话：检视发现元层实现与讨论结论漂移（醒/睡不对称 + `last_ts` 未重算 + 收口把实现追认成结论），本次修 `meta_layer.py` + 测试 + 修订 entry；LLM 接线留到修复完成后再议。

## 读什么

- 代码：`/home/zhengyp/work/A/cogos/cogos/agent/meta_layer.py`、`consciousness.py`
- 测试：`/home/zhengyp/work/A/cogos/tests/agent/test_meta_layer.py`
- 记忆：`projects/cogos/entries/2026-10-24-cogos-meta-layer-scaffold.md`

## 讨论结论（本次修复依据）

1. **wake_up / fall_asleep 内聚**：flow 方法 = 同步切态 + spawn 内部流；调用点只调一个方法，不拆开调。
2. **触发口径**：醒由 monitor 触发 / 睡由介入点触发 / idle 则由 monitor 触发，各自触发**完整动作**。entry 里「整理流启动统一归 Monitor」是收口记歪（追认了实现拆法），非原始结论。
3. **`last_ts` 重算**：`Monitor.run` 里 `_dispatch` 之后应重新 `time.monotonic()`，不复用 loop 开头 `now`（否则 dispatch 耗时被算进周期判断）。此结论收口时丢失。
4. **归一化不算睡触发点**：归一化 = `reset` 直接到 ASLEEP，不走入睡流。

## 修复清单

- `meta_layer.py`:
  - `Monitor.run`：`self.last_ts = time.monotonic()`（2 处，dispatch 后重算）
  - `monitor_on_asleep`：`spawn_wake_up` → `control.wake_up`
  - `monitor_on_idle`：`self._cons.start_unload()` → `self._control.fall_asleep()`
  - `monitor_on_falling_asleep`：去掉 `spawn_fall_asleep`，只留卡住检测 TODO
  - `Control`：删 `spawn_wake_up` / `spawn_fall_asleep` / `_fall_asleep_task`
  - `wake_up`：同步 `start_load` + spawn 内部装载流（append + load_done）
  - `fall_asleep`：state guard 幂等 + 同步 `start_unload` + spawn 内部整理流（unload_done）
  - `on_intervening`：`self.cons.start_unload()` → `self.fall_asleep()`
- `test_meta_layer.py`：补时序断言（`wake_up` 返回时 `state` 已是 `WAKING_UP`）
- `entries/2026-10-24-cogos-meta-layer-scaffold.md`：重写机制编排段（内聚 + 触发口径 + last_ts + 归一化）

## 状态

- [x] 修 `meta_layer.py`（wake_up/fall_asleep 内聚 + last_ts 重算 + 调用点收口 + 删 spawn_* 方法）
- [x] 补测试（`test_wake_up_switches_state_synchronously` / `test_fall_asleep_switches_state_synchronously`）
- [x] 跑全量测试（1366 passed, 6 skipped）
- [x] 修订 entry（机制编排段 + 被否段）+ current.md 摘要
- [ ] 删本草稿（留待 LLM 接线讨论后）

## 下一步

代码/测试/entry 已修完并验证。剩余：**LLM 接线**（G2 装载/G3 整理/G7 介入/`on_tool_call`）另起讨论；本草稿可作为该讨论入口，讨论收口后删。
