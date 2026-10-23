# ENTRY — runtime 架子重设计 + 意识上下文（数据层 + 接口层）

一句话：重设计 agent runtime 架构，**逐个模块**实现；事件模块已收口，cu material 改造（Message 类型）已完成；**意识上下文（数据层 + 接口层）讨论中——接口/生命周期已重组，正在逐条过待议点**。

读什么：
1. `2026-10-22-runtime-redesign.md` — 讨论草稿（准则 + 事件模块方案 + 意识上下文/on_tool_done 讨论）。
2. `2026-10-22-task-event-store.md` — 事件编码任务单（已完成）。
3. `2026-10-23-cu-material-message.md` — cu material 改造任务单（已完成）。
4. `2026-10-23-cu-context-persistence.md` — 意识上下文**数据层**（已收口，待落 entries/glossary；**待同步**：§2/§6.1 加 idle、§11 活跃判定）。
5. `2026-10-23-cu-interface.md` — 意识上下文**接口 + 生命周期**（方案全貌 + 已定结论 + 待议清单，**当前讨论焦点**，见该件 §9）。

状态：
- 事件模块已编码完成并推送（commit `edcfdab` + `d686683`）。
- **cu material 改造**（`list[dict]` → `list[Message]` + `Message`/`Meta` 类型）已完成（commit `2fcac25`，未 push）。

已定（意识上下文）：
- 介入回调**返回决策** `Resume/Switch/Sleep` + 参数打包 `InterveneContext` + 介入决策同步·入睡记忆异步。
- **IDLE** = 对外新状态，逻辑 = AWAKE；盘上加 **idle**（瞬态，后必接 continuing/unloading）。
- **介入点 = 两层流程**：意识上下文通用流程（打包 ctx + 按决策做 cu/state 机械维护）＋元层流程（on_intervening 内做准入/判/算起点/定决策；介入点后编排睡眠三段式/唤醒/归一化）。睡眠编排归元层，不在 _on_intervening。
- **interrupt 两件事分离**：结束旧 cu（仅 tool 介入点，先记 cur_cu 再按策略 interrupt）+ 换新 cu/置 None（cu=None 两时机：→IDLE、→Sleep）。start_unload 纯落盘不 interrupt。sleep() 改名 request_sleep()，_wait_to_sleep 清在 unload_done（真睡）+ start_load（醒来兜底）；睡由元层决定无法强制。
- **revoke = 无 cu 的 Switch**：封装 do_switch 统一换 cu（Switch 决策 + revoke 共用）；do_switch = 关旧开新 + 起新 cu，不碰整理（起点 context 外部传入，整理是元层独立事可回读盘上）。

下一步（待议清单，逐条过，见 `2026-10-23-cu-interface.md` §9）：
1. ~~`started`~~ → `started_before_last_shutdown`：以盘上为唯一真相（loaded 后有无 message），不设运行期字段（已定，见 interface §1.3）。
2. ~~睡眠编排归属~~ → 已定：睡眠编排归元层，介入点=两层流程（意识上下文通用流程 + 元层流程），见 interface §2.6。
3. ~~`interrupt` 位置~~ → 已定：收进 `_intervening_on_tool`（两件事分离），start_unload 纯落盘不 interrupt。
4. ~~`revoke` = 无 cu 的 Switch~~ → 已定：封装 do_switch 统一换 cu。
5. ~~新实现点~~ → 已确认：on_tool_done 回调（插入工具结果 append 后）+ rounds 字段 + tokens（lm_client usage）+ 最终 assistant 消息 append 进 material；interrupt()/no_wait 已存在无需落地。
6. ~~双驱动~~ → 已定：介入点 = 有 cu 时的唯一决策点；心跳 = 无 cu（ASLEEP/IDLE）时的唯一驱动（见 interface §0）。
7. ~~归一化条件表达清晰化~~ → 已清晰，无需改（见 interface §3）。
8. ~~旧遗留：失败路径不进介入~~ → 方向已定（继续遗留、不落码）：工具业务失败转结果给模型（生命周期无岔路）；工具程序失败 / on_done 非 OK 非 interrupt 失败 = BUG → 介入点打日志退出留痕；interrupt 不算失败；不引入重试。

更早的收口（已定，未改）：
- 数据层见 `2026-10-23-cu-context-persistence.md`（版本号 + 两套状态 + continuing/continued 续接 + archive 归档 + type 分派 + ISO 本地偏移 ts）。
- 事件模块、cu material 改造已完成。
