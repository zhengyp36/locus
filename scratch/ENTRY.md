# ENTRY — meta-layer 代码检视与修复（2026-10-25）

一句话：第一轮（醒/睡内聚 + `last_ts` + 收口追认）已修完；第二轮 YZ 检视提 6 点 + revoke 深入讨论，已收敛出 5 项可动手、3 项待讨论。

## 读什么

- 代码：`/home/zhengyp/work/A/cogos/cogos/agent/meta_layer.py`、`consciousness.py`、`event_store.py`
- 测试：`tests/agent/test_meta_layer.py`、`tests/agent/test_consciousness.py`
- 记忆：`projects/cogos/entries/2026-10-24-cogos-meta-layer-scaffold.md`

## 第一轮修复（已完成）

- `meta_layer.py`：flow 方法内聚（`wake_up`/`fall_asleep` 同步切态 + spawn 内部流）、`last_ts` 重算、调用点收口、删 `spawn_*` 方法
- 测试：`test_wake_up_switches_state_synchronously` / `test_fall_asleep_switches_state_synchronously`
- 全量 1366 passed, 6 skipped
- entry + current.md 已修订

## 第二轮检视意见（YZ，10-25）

1. **period 显式化** — 用 dict 每状态列明，不用 if/else。**可动手**。
2. **取事件时机** — `take_all` 应在装载步取（消费），monitor 只 `has_events` 判信号；否则通知→装载间隙新事件漏/错位。**可动手**（只挪 drain 位置，G2 内容仍留白）。
3. **决策压栈** — 澄清：`_decisions` 是测试注入钩子，非生产设计；生产语义 `on_intervening` 本就该即时决策。真难点 = `on_intervening` 是同步回调（`consciousness.py:448`）而真 LLM 异步。**随 G7，不动手**。
4. **track cu 累积** — `_made_cus` 只增不减，泄漏。改活跃集合，cu settle 时移除。**可动手**。
5. **归一化不是 reset** — `reset` 是 unlink 删文件，`start()` 用它归一化会丢内容；应归档不删。**已收敛（10-25）**：归一化两种处理——`reset`=忽略上一次醒（丢、wake 不加）；走 sleep/走完=认可上一次醒（归档、wake 按规则续）。`start()` 归一化改**补走 sleep 收口**，按残留态分两路：**AWAKE/IDLE/WAKING_UP → `fall_asleep`**（完整 `start_unload`+`unload_done`）；**FALLING_ASLEEP → `resume_fall_asleep`**（只 `unload_done` 走完过程，不重复 `start_unload`）。无 wake 歧义。**已动手（`b716a06`）**：实现为 `Control.settle_to_asleep`（机械收口、无 G3）+ `Control.resume_fall_asleep`。
6. **start/stop 不对称** — **已收敛（10-25）**：收口职责不对称（start 补收口、stop 硬停不收口当前醒）。对称做法 = stop 也走 sleep 收口（当前醒归档 + wake+1），与 start 归位对称、可共用同一收口逻辑。**已动手（`b716a06`）**：`stop()` 末尾调 `settle_to_asleep`。

## revoke 深入讨论（10-25，已收敛）

- **revoke 只在 idle 调用**（当前仅 `monitor_on_idle`，`meta_layer.py:129`）。
- **revoke 与 do_switch 分离**：`do_switch` 保持通用（Switch 决策路径 `consciousness.py:452` 在 AWAKE 态用）；`revoke` = IDLE 前置的 do_switch（`if state is not IDLE: return`），state 本身当互斥锁，天然防「同 IDLE 内重复 revoke」，无需布尔锁；对称 `fall_asleep` 幂等 guard。
- **5s 频率闸**：Monitor 加 `last_revoke_ts`，`monitor_on_idle` 里 `now - last_revoke_ts < 5s` 跳过（事件留 pending 不丢）。有了 state guard，`last_revoke_ts >= entry_ts` 判定冗余，去掉；5s 只控频、不防重入（正常流程 revoke 切走 state → entry_ts 更新 → 不受限）。
- **事件消费归装载步**：`take_all` 挪进 `make_wake_context`，monitor（asleep/idle）只 `has_events`。不漏（take_all 取全部 pending）+ 不恒真（消费即 `has_events` false，ASLEEP 另有 state 切换兜底）。
- **恒真真正来源是 IDLE**（revoke 后 cu 跑完回 IDLE 又 revoke），不是 ASLEEP（wake_up 切 WAKING_UP 即防重复）。
- 分两区（pending/notified + 双口径判断）方案：能解但过重，磁盘第二区 + 孤儿恢复 + 批次区分无消费者，不采用。

## 可动手清单（5 项）

1. `meta_layer.py` `period` → 显式 dict（`WAKING_UP`/`FALLING_ASLEEP`=MINUTE_PERIOD，其余=tick）。
2. `consciousness.py` `revoke` 加 IDLE 前置（与 `do_switch` 分离）；`test_revoke_is_switch` 改为先入 IDLE 再 revoke + 补「非 IDLE 不动作」用例。
3. `meta_layer.py` Monitor 加 `last_revoke_ts` + `REVOKE_PERIOD=5.0`；`monitor_on_idle` 加频率闸、去 `take_all`。
4. `take_all` 从 `monitor_on_asleep`/`monitor_on_idle` 挪到 `make_wake_context`（Control 注入 events）；monitor 只 `has_events`。
5. `_made_cus` list → set，cu settle 时 discard；移除信号 = `on_cu_settled` 钩子（`Consciousness` 在 `_cu=None` 结算点回调）或 task done-callback（实现自决）。

## 待讨论（暂不动手）

- 决策压栈（第 3 条）：`on_intervening` 同步/异步，随 G7（并入 LLM 接线讨论）。

## 状态

- [x] 第一轮修复（内聚 + last_ts + 收口）+ 全量测试 + entry 修订
- [x] 第二轮可动手 5 项（已改 + 全量 1367 passed, 6 skipped）→ commit `c9b3acb`
- [x] 归一化语义收敛（第 5 条）：reset=忽略 / sleep·走完=认可；start() 归一化改走 sleep 收口 → `b716a06`
- [x] start/stop 对称收敛（第 6 条）：stop 也走 sleep 收口 → `b716a06`
- [x] 全量 1369 passed, 6 skipped（+2 新增：start 归一化 FALLING_ASLEEP、stop 收口）
- [ ] LLM 接线（G2/G3/G7/on_tool_call）另起讨论
- [ ] 删本草稿（LLM 接线讨论收口后）

## 下一步

本轮检视 6 点全部收敛且已动手（`b716a06`，全量 1369 passed）；下一步 = LLM 接线（G2/G3/G7/on_tool_call）讨论。
