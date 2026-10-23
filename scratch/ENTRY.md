# ENTRY — runtime 架子重设计 + 意识上下文（数据层 + 接口层）

一句话：重设计 agent runtime 架构，**逐个模块**实现；事件模块已收口，cu material 改造（Message 类型）已完成，**意识上下文（数据层 + 接口层）已收口**。

读什么：
1. `2026-10-22-runtime-redesign.md` — 讨论草稿（准则 + 事件模块方案 + 意识上下文/on_tool_done 讨论），随讨论增改。
2. `2026-10-22-task-event-store.md` — 事件编码任务单（已完成，见「完成情况」）。
3. `2026-10-23-cu-material-message.md` — cu material 改造任务单（已完成，见「完成情况」）。
4. `2026-10-23-cu-context-persistence.md` — 意识上下文**数据层**（持久化与版本化，讨论已收口，待落 entries/glossary）。
5. `2026-10-23-cu-interface.md` — 意识上下文**接口层**（构造/属性/操作 + 睡觉流程 + meta.json + is_first_wake，讨论已收口，待落 entries/glossary）。

状态：
- 事件模块已编码完成并推送（commit `edcfdab` + `d686683`）。
- **cu material 改造**（`list[dict]` → `list[Message]`，引入 `Message`/`Meta` 类型 + 消息产生处记 `meta.ts`）已完成（commit `2fcac25`，未 push）。

下一步：
- 继续讨论其他模块（状态机/心跳/介入/装载）。
- 意识上下文已收口（数据层 + 接口层）：数据层见 `2026-10-23-cu-context-persistence.md`（版本号 + 两套状态 + continuing/continued 续接 + archive 归档 + type 分派 + ISO 本地偏移 ts）；接口层见 `2026-10-23-cu-interface.md`（Consciousness 原语 + 睡觉流程 start_unload/元层/unload_done + meta.json 版本号来源 + is_first_wake）。待落 entries/glossary。
