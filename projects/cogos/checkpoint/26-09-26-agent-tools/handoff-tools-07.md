# handoff｜web 异步化：spec 已定，待编码 · 2026-09-19

> **新会话任务**：读 `checkpoint-2.md` §二十 ＋ `spec-tools-a.md` §6.1，**按 spec 实现 web 异步化**（四步见下）。spec 已按 YZ 逐轮裁决定稿，可直接开工；编码期小点见 spec §10.7。
> **交接语**：读 `work/A/checkpoint/handoff-tools-07.md`，先读 `spec-tools-a.md` §6.1，再动手。

## 入口

- 本会话讨论记录：**`work/A/checkpoint/checkpoint-2.md` §二十**（本会话新增；§一～§十九为前会话）。
- 本会话产物：**`work/A/checkpoint/spec-tools-a.md` v1.4 §6.1**（WebService A 层规格）＋ §9.4 变更 27–33。
- 上一批交接：`handoff-tools-06.md`（标注与模型可见面讨论）。
- 权威：`cogos/docs/design-agent-tools.md`（**本轮未改**，§4／§14 待定案后更新）；批次 `plan-tools-impl.md`。
- 代码：`cogos` @ **`4f3c017`** ＋ 未提交改动 `docs/design-agent-tools.md`（前会话所留）。
- 相关代码面：`cogos/agent/impl/*.py`（A）、`agent/tools.py`（B 契约表）、`agent/webtools.py`（待改造）、`agent/app.py`（装配）、`agent/events.py`／`agent/consciousness.py`（渲染现状）。

## 本会话做了什么

- **只讨论 + 落 spec，未动代码**。
- 主线：web 工具异步化 → 作业 id（每能力独立、不统一）→ cancel 语义与闸门 → 短/长结果与草稿 → **底层工具不与模型渲染耦合**（渲染缝）→ 独立服务与并发控制 → 淘汰不做保护 → 风险清单收束。

## 结论要点（详见 checkpoint-2.md §二十／spec §6.1）

- **类重划**：`search`／`fetch` 从 sync 移入 async（判据＝能否无界阻塞）。
- **作业 id 每能力独立**，不建全局层；A 作业记录只含机器事实（`state`／`result|handle`／`error`／`source`／`at`），**不含工具名**；工具名由 kind（`web.fetch_done`）承载。
- **渲染解耦**：B 只产机器事实；另立渲染缝（默认 `str`），§十五 文案后填不返工。
- **cancel**：同步、幂等、尽力而为；闸门在"算出 → 落载体＋发 Signal"之间；取消不发 Signal；已 emit 的完成事件不可撤回。
- **短/长**：阈值 `inline_max_bytes`＝2048（注入），超出 `DraftStore.put` 落草稿并附**来源头**（URL／"网页搜索"）。
- **淘汰不保护**：web 属"只读可重做"类；缺失草稿只回"不存在"，工具说明写明"需要时重抓"；§五 "结果可达不丢"修正为"不可重做者不丢、可重做者保证能重做"。
- **并发两道上限**：`max_inflight_jobs`（超限抛 `WebBusy`，不排队）＋ `max_concurrent_requests`（Semaphore）。
- **过渡件**：web 不进最终形态（长期＝电脑视觉上网），对象自洽可拔除、不得被其他契约依赖。
- **R15 硬要求**：作业记录带发起时 `source`，否则异步结果回不到原会话（`consciousness._handle_done` 只对非 `system` 自动回）。
- **已核实**：`checkpoint-2.md` §十二"lm-service 不透传 tool call"**可能过期**——`lm_service` 已支持 tools 组装与 `tool_calls` 解析（`providers/base.py:78-260`、`deepseek.py:34`）。

## 下一步（新会话任务 · 四步）

1. `cogos/agent/impl/web.py`（新）——`WebService`，按 spec §6.1；纯 HTTP 层可注入，便于假 transport 单测。
2. `cogos/agent/tools.py`——`search`／`fetch` 换 fn、`time_form` 转 `async`、注入 `source`；新增 `web_cancel`（同步）。
3. `cogos/agent/observation.py`（新，渲染缝）——`render_tool_result(name, result)`，默认 `str`；只有 web 走临时形状。
4. `cogos/agent/app.py`——装配层读 key/proxy；构造注入；`Agent.stop()` 调 `WebService.aclose()`。

测试（`tests/agent/`，假 transport）：成功／超时／取消（含取消后不发事件）／长结果落草稿＋来源头／并发上限／无 key。

**编码期小点**见 spec §10.7：`source` 注入方式（显式参数 vs contextvar）、search 内联形态、终态作业保留条数、`aclose` 形状、共享 session 重连。

## 本批明确不做（记债，勿混入）

模型可见文案定稿（§十五）、统一事件信封、`transfer` 对齐作业形状、作业可观测列表、上下文压缩／丢弃（§十八）、同 URL 去重、草稿淘汰保护。

## 待 YZ 裁决（开工前）

1. 是否**本批就做渲染缝** `observation.py`（不做则 web 的 B 返回即模型可见，耦合固化）。
2. 是否同步更新 `design-agent-tools.md`：§4 判据改写为"能否无界阻塞"、补"机制自持上界＝同步"（`fs.read` 留同步）、§14 解除 `search`／`fetch` freeze 并写明"过渡件／长期走电脑视觉"。
3. `send_msg` 是否本批一并真异步（现状标 async 却阻塞）。

## 遗留（不在本会话范围）

- **4b 装配**：`assemble`／分包／按需／`agent.json`「电脑」接线。
- **标注规范（§十五）／`tool` 命名／模型可见面最小词汇** 三项仍待裁（`handoff-tools-06.md`）。
- `transfer` 尚无 cancel；`term.*` 整族一刀切 async（`observe`/`list`/`cancel` 实为取值）。
- `experiment/selfdrive/loop.py:TASK_TOOLSET` 旧 `read_file` 语义。
- 批次 2.5 旧遗留：armed/一次性 token、槽位列举、密钥/`ControlMaster`。
- 通信工具**历史回读面**（§十八）；统一"在途调用"可观测面。
- 草稿 id 复用坑（淘汰最大号＋重启，`DraftStore._scan_next_id`）——归"草稿 id 语义"。

## 纪律（照 plan §0）

- 结论先落 `checkpoint-2.md`／`spec-tools-a.md`，定案再更新权威分册 `design-agent-tools.md`。
- 一批一会话；开工前重审 spec／权威分册。
- `time_form` 目前是**无人消费的死元数据**（已 grep 确认），"异步不阻塞"无机制保证——靠 B 自觉早返回 + 测试兜底。

## 收工

- 本批实现后 → 视裁决更新 `design-agent-tools.md`（§4／§14）并另起 handoff。
