# ENTRY — runtime 架子重设计 + 意识上下文（数据层 + 接口层）

一句话：重设计 agent runtime 架构，**逐个模块**实现；事件模块、cu material 改造、**① 依赖改造**、**② 数据层**、**③ 接口层**均已落码收口（退役 `2f0c34c` → 数据层 `3d20dce` → 接口层 `f76da56`）——**下一步 = 上层编排**（归一化/醒/睡/IDLE 唤醒，属更上层系统，另行设计讨论，不属意识上下文模块）。

读什么：
1. `2026-10-22-runtime-redesign.md` — 讨论草稿（准则 + 事件模块方案 + 意识上下文/on_tool_done 讨论）。
2. `2026-10-22-task-event-store.md` — 事件编码任务单（已完成）。
3. `2026-10-23-cu-material-message.md` — cu material 改造任务单（已完成）。
4. `2026-10-23-cu-context-persistence.md` — 意识上下文**数据层**（已收口 + 已落码；idle 三处已同步）。
5. `2026-10-23-cu-interface.md` — 意识上下文**接口 + 生命周期**（方案全貌 + 已定结论 + 待议清单，**已收口**；§3–§8 上层编排仍待下一步）。

状态：
- 事件模块已编码完成并推送（commit `edcfdab` + `d686683`）。
- **cu material 改造**（`list[dict]` → `list[Message]` + `Message`/`Meta` 类型）已完成（commit `2fcac25`）。
- **① 依赖改造已完成并推送**（commit `d6de28f`）。
- **退役 v2.2 flow 子系统已完成并推送**（commit `2f0c34c`）：删 `consciousness.py`/`flow.py`/`experience.py` + `scripts/exp_*.py` + 3 测试；app.py 解接线（感知改 inert `_on_message`）。
- **② 数据层已完成并推送**（commit `3d20dce`）：`FileState`（盘上七态含 idle）+ 序列化 + `ConsciousnessStore`。
- **③ 接口层已完成并推送**（commit `f76da56`）：`State`（对外五态含 IDLE）+ `Consciousness`（原语 + 介入点包装 + do_switch）。全量 1350 passed。

已定（意识上下文）：
- 介入回调**返回决策** `Resume/Switch/Sleep` + 参数打包 `InterveneContext` + 介入决策同步·入睡记忆异步。
- **IDLE** = 对外新状态，逻辑 = AWAKE；盘上加 **idle**（瞬态，后必接 continuing/unloading）。
- **介入点 = 两层流程**：意识上下文通用流程（打包 ctx + 按决策做 cu/state 机械维护）＋元层流程（on_intervening 内做准入/判/算起点/定决策；介入点后编排睡眠三段式/唤醒/归一化）。睡眠编排归元层，不在 _on_intervening。
- **interrupt 两件事分离**：结束旧 cu（仅 tool 介入点，先记 cur_cu 再按策略 interrupt）+ 换新 cu/置 None（cu=None 两时机：→IDLE、→Sleep）。start_unload 纯落盘不 interrupt。sleep() 改名 request_sleep()，_wait_to_sleep 清在 unload_done（真睡）+ start_load（醒来兜底）；睡由元层决定无法强制。
- **revoke = 无 cu 的 Switch**：封装 do_switch 统一换 cu（Switch 决策 + revoke 共用）；do_switch = 关旧开新 + 起新 cu，不碰整理（起点 context 外部传入，整理是元层独立事可回读盘上）。

下一步 = 上层编排（属更上层系统，另行设计讨论）：

- **已落码收口**：意识上下文积木（② 数据层 + ③ 接口层）已落码（`3d20dce` + `f76da56`），自决/遗留见 `entries/2026-10-24-cogos-consciousness-context.md`。
- **下一步范围（另行设计，不在本模块）**：① 归一化（启动读盘 → 收敛 ASLEEP）② 醒触发/装载（记忆 → 2 条起点）③ 睡眠三段式 ④ IDLE 唤醒（事件 + revoke）。另留装载机制、整理/重定向执行机制。
- **对齐设计文档（非结果验收）**已照做：分层落地、逐层核对 idle 态/成败语义/material 真相/介入点两层流程/两件事分离；守边界不碰编排。

更早的收口（已定，未改）：
- 数据层见 `2026-10-23-cu-context-persistence.md`（版本号 + 两套状态 + continuing/continued 续接 + archive 归档 + type 分派 + ISO 本地偏移 ts）。
- 事件模块、cu material 改造已完成。
