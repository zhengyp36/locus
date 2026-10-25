# 元层架子落码（2026-10-24）

## 结论（活跃）

元层 MetaLayer = **Monitor（监控）＋ Control（控制）** 上层编排，已落码 `b739378`。内容生产（LLM 上下文）全部留白 stub，全程不调 LLM。

- 载体 `cogos/agent/meta_layer.py`（单文件）：`Rhythm` / `WakeReason` / `Monitor` / `Control` / `MetaLayer` / `StubCu`；改造 `app.py` 4 处；测试 `tests/agent/test_meta_layer.py`（两剧本全链）。
- 验收：stub cu 两剧本走通全链（出生→介入→IDLE→事件唤醒→入睡）+ 全量 **1364 passed**（基线 1359，+5）。
- 不动积木：`consciousness.py` / `event_store.py` / `events.py` / `cog_runtime` 全部。

## 机制编排（钉死）

- **元层不持有状态**：状态＝意识上下文五态，元层只读 `cons.state`；意识层对象进元层属性。
- **醒/睡对称（flow 方法内聚）**：`wake_up`/`fall_asleep` 各是一个同步方法——方法内**同步切状态原语**（`start_load`/`start_unload`），再把走流包成内部协程 `spawn` 出去；调用点只调一个方法、不拆开调。醒＝`wake_up`(start_load + spawn 装载流[append+load_done])；睡＝`fall_asleep`(start_unload + spawn 整理流[unload_done])。
- **触发口径**：醒由 Monitor 触发（`monitor_on_asleep`→`wake_up`）；睡由介入点触发（`on_intervening` 返回 `Sleep` 前 `fall_asleep`）；IDLE 转黑由 Monitor 触发（`monitor_on_idle`→`fall_asleep`）。各自触发**完整动作**，无「走流统一归 Monitor」。归一化＝`reset` 直接到 ASLEEP，不算睡触发点。
- **`fall_asleep` 幂等**：state 已是 `FALLING_ASLEEP` 即 return（防重复切态/spawn）。
- **规则① 监控分离**：Monitor 不亲自跑长任务，只调用 flow 方法（方法内 `Control.spawn` create_task）+ 周期查卡住（卡住判断用 `entry_ts`，空函数+TODO）。
- **归一化**：`MetaLayer.start()` 里 `state != ASLEEP → reset()`。
- **醒因两分**：`WakeReason` = RHYTHM / EVENT（闹钟 remind 并入事件——工具产生事件，节律＝元层非事件）。
- **时钟双口径**：`Rhythm.is_daytime` 吃 **epoch 秒**（`time.time()`）；Monitor 的 tick / `entry_ts` / `now` 全用 **`time.monotonic()`**。`monitor_on_asleep` 判白天调 `is_daytime(time.time())`，不得喂 monotonic。
- **`last_ts` 重算**：`Monitor.run` 里 `_dispatch` 之后 `last_ts = time.monotonic()` 重新取值，不复用 loop 开头 `now`（否则 dispatch 耗时会被算进周期判断）。

## 关键决策

- **`on_intervening` 同步**（`consciousness.py:448` 同步调用）：返回 `Sleep` 前同步 `self.fall_asleep()`（`fall_asleep` 内同步 `start_unload` + spawn 整理流）。`Control.on_intervening` 用决策队列（测试可 push）+ 默认 `Resume`。
- **Control 构造环回填**：`Control.__init__(rhythm)` 不接 cons；顺序＝Rhythm → Control → Consciousness(`on_intervening=control.on_intervening`, `make_cu`) → `control.cons = cons` 回填 → Monitor。`on_intervening` 里引用 `self.cons` 只在回填后才被调，安全。
- **事件 drain**：Monitor 检测到事件即 `take_all()`（丢弃、G2 留白不渲染），防 IDLE 事件唤醒后 `has_events` 恒真 → 无限 revoke。
- **StubCu**：两剧本 `finish-only` / `tool-then-finish`，`no_wait` create_task 后台流程按剧本触发 `on_tool_done`/`on_done`（result 用 `CuResultOk`）；`interrupt` 记 reason + cancel 自身任务。`_start_cu` 只挂 `on_tool_done`/`on_done`、没挂 `on_tool_call`，故选 stub cu 而非 mock chat。

## 扩展（spec 未列，实现时补）

- `MetaLayer.__init__` 增 `make_start_context=None` 关键字：装载内容 persona+overview「程序化渲染可真实组装」需注入（Control 只接 rhythm，无处拿 profile/overview）。app.py 传 `self._make_start_context`（render_system_prompt + render_overview）；默认 stub 两条 `(system,user)` 占位。G2「从 memory 目录加载」仍留白。
- `Monitor.stop()` 是 `async def`（置 exit_flag）；`StubCu.running()` 供 stop 判断是否在跑。

## 留白（架子期不实现，之后回讨论）

- G2 装载内容（从 memory 目录加载）/ G3 整理内容（cu done 蒸馏+重定向）/ G7 介入形态（审视措辞/清理时机/留痕形式，判走向用 stub）。
- 工具执行层 `on_tool_call` 接线；接真 runtime + mock chat（`_DemoLmClient` 现成雏形）。
- 卡住后处理（空函数+TODO：上报飞书 fail-stop / 换 LLM / LLM 分析）；重判（IDLE 20~30min 元层 LLM 判有无可装载）触发钩子可钉。
- 装载机制、整理/重定向执行机制（cu done 蒸馏+重定向由谁执行）。

## 被否 / 未采用

- start_load 放 Monitor 内（scaffold 初版「Monitor 内 start_load 切态防重触发」）→ **否**，最终放 `Control.wake_up` 内**同步切态**；「wake_up 为 async、切态延迟到 task 内」是首版实现偏差（10-25 修正为 flow 方法内聚 + 同步切态）。
- 整理流启动统一归 Monitor 在 FALLING_ASLEEP 态触发（首版实现/收口口径，`spawn_fall_asleep`）→ **否**（10-25），走流在 `fall_asleep` 内 spawn；`monitor_on_falling_asleep` 只留卡住检测。
- 事件唤醒不 drain → **否**，会无限 revoke（has_events 恒真）。
- 长任务跟踪单独建结构 → **否**，卡住判断用 `entry_ts` 已够。
