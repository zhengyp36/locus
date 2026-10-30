# body 工具验证（阶段0 第二步，已落码）

> 状态：已落码。YZ 定位：**阶段0 第二步 = body 工具验证**，是「设计对话架子（最轻对话驱动）」的前置条件。
> 目标：先独立证明「LLM ↔ body/memory meta 工具 ↔ 实现工具」链路真的通，再接 CogStream 搭对话驱动。

## 工具清单（已确认）

- **body**：单个 meta 工具（模型调 `body(command, name, args)`，机制路由到实现层），**6 组 20 能力**、全部复用实现工具、无新底层：file(read/write/edit)、vision(see/mark/coord)、chat(speak/browse)、terminal(run/observe/send/interrupt)、web(search/fetch/browse/cancel/close)、time(now/wait/remind)。
- **memory**：独立 meta 工具，3 能力 fold/unfold/mark。
- **toolbox**：大而全 catalog（3 组 computer/communication/vision）。
- 暴露层 registry（app.py）＝实现工具全量 + 三个 meta；但**「模型看到什么」由传给 cu/stream 的 `tools` schema 决定**，非 registry 本身。

## 结论（方案已定）

1. **裸 cu harness，不套 Agent/CogStream**：`CogRuntime` + `CogUnit` + 手写 `on_tool_call`（或 runtime 级 `tool_executor`），一个 cu 内部自动跑完「chat→工具→回灌→再 chat」直到模型不再调工具。裸的是**驱动层**，不是工具本体——工具本体（ComputerManager/Clock/WebService/TimerService/MemoryStore/stub capability）仍要用工厂函数装配，且装配量随增量叠加、不加不装。
2. **只暴露 body+memory 两个 meta 工具 schema**（实现工具不直接暴露、只能 help 发现）。这是验证核心：模型必须走 `body(help)` → `body(help, name="file")` → `body(call, name="file.read", args)` 的闭环。
3. **增量叠加落在任务清单，不在工具暴露**：body 是整体 meta 工具，schema 只有 command/name/args 三字段、无法逐能力暴露；增量＝一个连续 material 逐项追加任务（file 三项先验，通过再加 terminal/time/memory/chat/web）。工具全暴露，模型可能提前用未轮到工具，不禁止，判据只认「能力被成功调用 + 副作用对」。
4. **任务只写目标、产出物在系统侧**（模型裸答不了）：如「写文件再读回」「echo 再读回」「记住概念再展开」。判据 = 副作用落盘 + `on_tool_call` 痕迹，不解析 material、不信模型自称。
5. **副作用策略**：chat.speak 用桩（StubPhone 记 (target,content)）；web 有 brave/jina key 真跑一次（标"条件验证"）；time.remind 真 TimerService 只验"已创建/可 list"、不真等唤醒；vision/screen/chat.browse 跳过并显式标注"未验证"。

## 接线缺口（事实，最轻对话驱动要补两处）

- app.py:213 构造 `MetaLayer` 没传 `tools` → `Consciousness._tools=None` → `stream(tools=None)`，模型拿不到工具。
- `CogRuntime` 没接 `tool_executor`；`runtime.py:149` 无 `on_tool_call` 时直接 `invalid_request`。
- 参照：`experiment/selfdrive/loop.py:332-347` 的 `on_tool_call`（`agent.registry.execute(name, args)` 路由）；`experiment/cogstream_smoke.py:71-74` 已验证 `CogRuntime(tool_executor=...)` + 真 LLM 工具回灌。

## 语言规范（内部全英文，已拍）

- **内部默认全英文**：工具 schema/说明、system 指令、内部事件，一律英文；**只有对真人输出时按真人语言**。人名（唐钰）保留，名字非语言。
- 现状不统一，需英文化：`memory_catalog.py`、`memory.py`（_DESCRIPTION/_PROMPT）、`tools.py:788-888`（make_memory_specs 的 schema + 返回 message"已新建/撞名/已标"）、`config.py:125-136`（render_system_prompt persona）均为中文。
- 后置（不在本次主线）：`impl/memory.py` 异常消息、`impl/web.py` header"来源:网页搜索"、vision "@原图"、`events.py` 内部事件渲染。

## 被否方案

- **全量 20 能力一次验** → 否，改代表性 8-12 个（必测 + 条件跳过），未验证显式标注。
- **走完整 Agent / CogStream 驱动** → 否，Agent 连 phone/飞书/timer 太重有副作用；CogStream 把「工具验证」和「stream 心跳」两问题耦合。工具通了再接 stream。
- **直接暴露实现工具（read_file 等）** → 否，那样证明不了 meta 工具 help 发现闭环（旧 verify_tools.py 正是此形式，只冒烟过 3 个实现工具）。

## 下一步

1. 英文化：memory（catalog/meta 描述/impl 返回 message）+ persona → 英文。
2. 写 harness（裸 cu + 只暴露 body/memory）+ file 三项任务清单，跑通。
3. 增量加 terminal/time/memory/chat(stub)/web(条件)，输出"已验/未验"清单。

## 落码结果（10-29）

- **harness** `cogos/experiment/body_verify.py`：裸 cu（`CogRuntime` + `CogUnit` + 手写 `on_tool_call` 路由 `exposed.execute`），只暴露 body+memory 两 schema、实现工具靠 help 发现；每任务一 cu 自动跑完 chat→工具→回灌→再 chat；判据＝副作用落盘＋on_tool_call 痕迹。装配参照 `verify_tools.py`（ComputerManager+make_fs_specs+桩 send_msg）、executor 参照 `loop.py:332-347`。
- **英文化**：`memory_catalog.py`、`memory.py`（_DESCRIPTION/_PROMPT）、`tools.py` make_memory_specs（schema + 返回 message "created/name collision/updated/marked/already marked"）、`config.py` render_system_prompt persona → 英文；人名唐钰保留。后置清单（`impl/memory.py` 异常、`impl/web.py` header、vision `@原图`、`events.py` 事件渲染）未动。
- **验证结果 11/11 全过**：file.write/read/edit、terminal.run+observe、time.now、time.remind（只验创建）、memory.fold/unfold/mark、chat.speak（StubPhone 桩）、web.search+browse（brave 真跑、经 KILO_PROXY 代理）。
- **已验/未验清单**：已验 12 能力；跳过 vision.see/mark/coord + chat.browse（标注未验证）；未验 terminal.send/interrupt、time.wait、web.fetch/cancel/close。
- **harness 里发现的两个 false-negative 已修**（验证逻辑，非能力缺陷）：mark 的 help 结果与 call 结果同 path 需按 `command=="call"` 过滤；web 结果文件被模型主动 `web.close` 删掉，判据改读 browse 痕迹的 `state==done` 非查 cache 文件。
- **遗留**：接线缺口待补（app.py 传 tools + CogRuntime 接 tool_executor）＝最轻对话驱动的两处。
