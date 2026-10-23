# ENTRY — runtime 架子重设计 + 意识上下文（数据层 + 接口层）

一句话：重设计 agent runtime 架构，**逐个模块**实现；事件模块、cu material 改造、**① 依赖改造**均已收口；**意识上下文（数据层 + 接口层）讨论已收口（待议全过，commit `0da0243`）——下一步 = 编码：**② 数据层 → ③ 接口层**（积木，不含上层编排）**。

读什么：
1. `2026-10-22-runtime-redesign.md` — 讨论草稿（准则 + 事件模块方案 + 意识上下文/on_tool_done 讨论）。
2. `2026-10-22-task-event-store.md` — 事件编码任务单（已完成）。
3. `2026-10-23-cu-material-message.md` — cu material 改造任务单（已完成）。
4. `2026-10-23-cu-context-persistence.md` — 意识上下文**数据层**（已收口，待落 entries/glossary；**待同步**：§2/§6.1 加 idle、§11 活跃判定）。
5. `2026-10-23-cu-interface.md` — 意识上下文**接口 + 生命周期**（方案全貌 + 已定结论 + 待议清单，**已收口**，见该件 §9）。

状态：
- 事件模块已编码完成并推送（commit `edcfdab` + `d686683`）。
- **cu material 改造**（`list[dict]` → `list[Message]` + `Message`/`Meta` 类型）已完成（commit `2fcac25`）。
- **意识上下文接口+生命周期讨论已收口**（待议全过，commit `0da0243`）。
- **① 依赖改造已完成并推送**（commit `d6de28f`）：`cu.on_tool_done(ok)` 回调（成败两路：成功在 append 后·pending 前，失败在 on_tool_call 缺失/抛异常）；`cu.rounds` 每 chat +1、`cu.tokens` 累计 `completion_tokens`；最终 assistant 消息 append 进 material（方案 A，material=完整真相）；consciousness._handle_done / loop._run_one_round 的重复 append 已移除。全量 1359 passed 无回归。**决策：tokens 取 completion_tokens（= 纯 LLM 输出，天然不含工具结果）**。

已定（意识上下文）：
- 介入回调**返回决策** `Resume/Switch/Sleep` + 参数打包 `InterveneContext` + 介入决策同步·入睡记忆异步。
- **IDLE** = 对外新状态，逻辑 = AWAKE；盘上加 **idle**（瞬态，后必接 continuing/unloading）。
- **介入点 = 两层流程**：意识上下文通用流程（打包 ctx + 按决策做 cu/state 机械维护）＋元层流程（on_intervening 内做准入/判/算起点/定决策；介入点后编排睡眠三段式/唤醒/归一化）。睡眠编排归元层，不在 _on_intervening。
- **interrupt 两件事分离**：结束旧 cu（仅 tool 介入点，先记 cur_cu 再按策略 interrupt）+ 换新 cu/置 None（cu=None 两时机：→IDLE、→Sleep）。start_unload 纯落盘不 interrupt。sleep() 改名 request_sleep()，_wait_to_sleep 清在 unload_done（真睡）+ start_load（醒来兜底）；睡由元层决定无法强制。
- **revoke = 无 cu 的 Switch**：封装 do_switch 统一换 cu（Switch 决策 + revoke 共用）；do_switch = 关旧开新 + 起新 cu，不碰整理（起点 context 外部传入，整理是元层独立事可回读盘上）。

下一步 = 编码（意识上下文积木，不含上层编排）：

- **积木定位**：意识上下文 = 和 event store 同级的积木（被动持久化服务 + 介入点机械维护）；上层编排（归一化/醒/睡/IDLE 唤醒）属更上层系统、另行设计讨论，不在本模块范围。
- **编码顺序**：~~① 依赖改造~~（已完成）→ ② 数据层（文件格式 + 七态枚举含 idle + 版本号 + 归档；动手前先补 persistence 草稿"待同步"：§2/§6.1 加 idle、§11 活跃判定）→ ③ 接口层（原语 + 介入点包装 `_on_intervening` 判成败 + `_intervening_on_tool/_finish`）。
- **对齐设计文档（非结果验收）**：分层落地、逐层核对设计文档每条规格与**已指出的漏洞**是否在代码中执行（idle 态、成败语义、material 真相、cu 销毁自动、介入点两层流程、两件事分离）；不做"跑通"式验收（易把验收当目标、偏离忠实实现）。守边界不碰编排。
- **已定结论全集**：见 `2026-10-23-cu-interface.md` §9（已定 + 待议已全勾）。

更早的收口（已定，未改）：
- 数据层见 `2026-10-23-cu-context-persistence.md`（版本号 + 两套状态 + continuing/continued 续接 + archive 归档 + type 分派 + ISO 本地偏移 ts）。
- 事件模块、cu material 改造已完成。
