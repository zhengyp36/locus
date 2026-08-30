# checkpoint-2 — cog-runtime 内部实现设计讨论

> 会话：`design-cog-runtime-min.md` 审核收口后，进入内部实现设计。4 问题逐一讨论，YZ 提意见，我主导方案。

## 当前问题

接口已定稿（审核 1~7），距开工还差「内部实现设计」：类结构 / 推进循环落地 / 父子通知 / 并发落地。

## 问题 1 结论：类结构与推进时序（已收敛）

- **CogUnit = 纯数据 + 句柄**，不含推进逻辑。字段 `material/tier/tools/callbacks/parent/children/state/result/interrupt_reason`；方法仅 `wait()/no_wait()/interrupt()/defer()`。
- **CogRuntime = 主动引擎**，推进集中 `_advance(cu)`；持 cu 队列 + `LmClient`。
- **入队** = 装配完、要调 lm-service 前（`queued`）；**出队** = 拿并发 slot（`running`）；**推进** = `_advance` 每步。
- **队列只装 `queued` 态**；`pending`/`running`/`tooling` 靠事件/await 挂起，`created`/`done` 不在队列。
- 五个推进触发源：`wait/no_wait`、子完成通知、队列 worker 出队、`LmClient` 返回、`on_tool_call` 返回。
- 稳定点四态：`pending`/`queued`/`running`/`tooling`。

## 问题 2 结论：状态机落地 + interrupt/defer（已收敛）

### on_ready = 幂等装配钩子

- 触发时机：查 ready 通过、要装配时调，每轮 ready 一次（多批子 = 多轮装配）。
- on_ready 里可改 material / 加子 / interrupt；加子导致退回 pending 是合法干预。
- 机制固定流程：查 ready → 通过 → 调 on_ready → 返回后重查一次依赖 → 有未完成子则 pending / 无则入队。
- 不死循环：加子有界，收敛靠上层自觉。
- **返回值协议（YZ 定）**：`async def on_ready(cu, material) -> None`。material 传引用原地改（上层保证增量装配不重复，自己知道哪些子新完成）；material 只经 on_ready 参数改（`cu.material` 其余时间只读，工具回填是 cu 内部 append，上层不碰）；加子走 `cu.add_child`、中断走 `cu.interrupt`。接口说明需写清这些约束。
- 关键：runtime 不自动汇总子结果进父 material——子 done 由上层 on_done 收结果存起，父 ready 时上层在 on_ready 里装配。on_ready 是上层「发起后改 material」的唯一合法入口。

### interrupt = 协作式取消

- 上层任何时候可调 `cu.interrupt(reason)`（设标志，同步非阻塞）；已 error 则 no-op。
- 检查点统一 `_advance` 入口一处（五个触发源都过这），置位即 `done(interrupted)` 跳过推进。
- running 期间 interrupt 不打断当前调用（协作式），结果回来在入口发现并丢弃。

### defer 后置（YZ 拍板）

- 目标态用途：资源控制/上层的协作式暂缓（错峰/退避/节律）。
- 最小版无真实场景（资源控制是阶段三），后置，同优先级待遇；状态机不加 `deferred` 态。

### cu 注册表（YZ 同意加）

- `_units: dict[id, CogUnit]`，创建登记、done 移除；用途 shutdown（遍历未 done 统一 `interrupt("shutdown")`）+ 调试。
- cu 给可读自增 id（`cu_1`/`cu_2`，YZ 同意），作 `_units` 的 key，调试日志好认。

## 问题 3 结论：父子通知机制（已收敛）

- 无计数器无 Event：子 `_advance` done 分支里，先调 `on_done`，再 `asyncio.create_task(_advance(parent))` 触发父。
- 父每次被喊就全量遍历 children 查 done，最后一个子 done 时一查全 done → ready（与「重查 ready」统一，天然支持动态加子）。
- 顺序：先 done 后父（checkpoint-11 暂定，沿用）。
- `parent` 指针冻结（发起后不可换父）；`children` 可增不可删。
- 增：`add_child()`；删：**显式提供 `remove_child()` 抛异常 + 注释**（YZ 拍板：显式禁止比不提供更钉死规则）；读：`children` property 返回不可变快照。
- **子不可删的理由**（写进 `remove_child` docstring，防后人误解放开约束）：子一旦发起即独立运行——running 中的子删不掉（停它走 `interrupt`），已结束的子其结果应保留供父装配；「从父身上摘掉子」既停不了在跑的子、又丢弃已完成的结果，无合法语义，故只能增不能删。

## 问题 4 结论：并发落地（已收敛）

- **短 task 粒度**：一次 `_advance(cu)` = 一个短 task（`asyncio.create_task`），推进到稳定点即结束；「短」= 不常驻（无 worker while 循环），非「不 await」（running 态 await LmClient 是挂起）。
- **cu 队列结构**：最小版 = `asyncio.Semaphore(N)`（内部 FIFO 即队列 + 计数即并发窗口）；queued = `await acquire()`，acquire 成功 = 出队进 running，done/再入队 release。未来优先级换优先队列，接口不变。
- **两层分界**：cu 队列（`Semaphore(N)`，agent 内逻辑限流，本次实现）→ lm-service（服务端 `AccountScheduler`，物理限流，已实现不动），叠加独立。
- **N 来源（YZ 拍板 A）**：`CogRuntime(internal_key, max_concurrent=N)` 构造参数 + 默认小值（如 4），与 lm-service `max_concurrent` 语义对齐。

## 内部实现设计 4 问题全部收敛

类结构+推进时序 / 状态机落地+interrupt（defer 后置）/ 父子通知 / 并发落地，见上文各节。下一步：把结论固化进 `design-cog-runtime-min.md`（补「内部实现」章节）或归档，待 YZ 提出。
