# cogos

多 agent 运行时，飞书作通信总线。通信层已收口，智能系统设计已收敛。底层三件：lm-service + cog-runtime 已完成，第三件「认知图」设计探索已封存为预研（09-01），4K 聊天机器人 MVP 暂停。

## 通信（已收口）

后续通信用 `cogos/phone`，用法见 `docs/phone-usage.md` / `docs/comm-full-design.md`。细节不再记，用时看文档。

## 设计已收敛（08/24–08/26）

讨论收敛为概念体系 + 开发计划，固化到本体 docs：

- 概念体系：`docs/cogos-concept-system.md`
- 开发计划：`docs/cogos-plan.md`
- 理论摘要：`docs/cogos-design-theory-summary.md`
- 上网工具：`docs/webtool-design.md`（阶段二，工具子系统）

## agent-study 复习（08-26 晚 ~ 08-27，已收尾）

31 条已确认结论全过，保留项挂接进 cogos 模块，固化 `docs/agent-study-hooks.md`。关键新决策：元控制二分（资源级=机制层预装不可自长 / 认知级=策略层自长方法论）。两个设计缺口已归入 plan：过程元控制→阶段三整系统（认知级元认知）、诊断观察→每阶段都有诊断出口，完整事件流随阶段三。过程归档 `checkpoint/archive/26-08-27-agent-study-review/`。

## 当前：底层三件实施（08-29 起）

- 任务1（工位 B）：lm-service 实施 ✅ 完成（08-30）
- 任务3（工位 B）：lm-service 遗留三项 ✅ 完成（08-30）
- 任务2（工位 A）：cog-runtime 设计 ✅ 收敛（归档 `checkpoint/archive/26-08-30-cog-runtime-impl/design-cog-runtime-min.md`）
- 任务4（工位 A）：cog-runtime 实施 ✅ 完成（08-30）

lm-service 最小版（`docs/design-lm-service-min.md`）已实现并验证：mock 51 passed + 全量 pytest 719 passed 无回归 + 真实验证全绿（deepseek 文本/401/视觉 judge）。关键决策（YZ 拍板）：tier 改名 basic/advanced（视觉模型归 basic）；thinking 默认关闭（cogos 内部不用厂商 thinking，仅留参数对比）。冻结契约：LmClient.chat → 归一响应 + LmServiceError(category)。过程归档 `checkpoint/archive/26-08-30-lm-service-impl/`。

task-3 遗留三项（① LmClient 不暴露 base_url，走环境变量 ② tool call 内部化 ③ content 归一 content[]）完成：`chat` 加 `tools` 入参、响应加 `tool_calls` 出参（`[{id, name, args}]`）、content 变 list；mock 65 + 全量 733 passed 无回归 + deepseek 真实验证 tool call 全绿（同构 openai、arguments 真实 parse、strict 忽略不补）。契约形状不变，仅扩展字段。过程 `checkpoint/archive/26-08-30-lm-service-fixes/`。

task-4（cog-runtime 实施，工位 A）完成：类型 + CogUnit + CogRuntime/_advance 状态机 + 支路 A/B 闭环 + 并发 + 父子通知 + shutdown，测试 32 passed。真实测试暴露 lm-service 缺续轮消息归一→厂商转换，工位 A 直改补齐（`providers/base.py` `assemble_tool_messages`）；全量 777 passed 无回归 + 真实 deepseek 三路全绿（A 文本 / B 工具续轮 / E 401→auth）。遗留：告知值默认注入先不做。过程 `checkpoint/archive/26-08-30-cog-runtime-impl/`。

## CogUnit thinking 模式（09-02）

CogUnit 加 `thinking` 透传（dict，默认 None=厂商 disabled）+ 工具续轮回传 `reasoning` + `CuResultOk.reasoning` + `assemble_tool_messages` 转 `reasoning_content`，目的对比。真实验证：DeepSeek **不校验** reasoning_content 回传（漏传/截断均 200，flash/pro 一致），回传是质量导向非硬约束，官方「不传 400」是威慑性描述。遗留：plain assistant 的 reasoning 未映射（跨 cu 多轮才需要，暂不改）。细节 `entries/2026-09-02-cogos-cogunit-thinking.md`。

## 认知图设计探索 → 封存（08-30 晚 ~ 09-01 凌晨）

第三件从「认知树」转向「认知图」的设计探索（checkpoint-1~13），最终封存为预研，聊天机器人 MVP 暂停。关键结论：图必要性在上下文局限而非「抽象需要记忆」；图非预先设计、从 cu 痛点长出；MVP 记忆用文件组织（profile replace + events append）、预算外包取舍自学。归档 `checkpoint/archive/26-09-01-cog-graph-sealed/`，状态 ISSUES「封存/暂停」。

## agent 认知架构 + 实施（09-01 ~ 09-02，讨论收敛 + 概念澄清）

编程助手场景，从「记忆系统」转向「LLM 自管理上下文」。核心：cu 覆盖式回合、状态对象（context/intent/problem/gain）、意识=脉络（放下意识层/元层术语，改功能命名）、心智时间留元层不进对象层、来源标注分工、scratch 脚注引用与 cu 化展开、目录 ID 化、元层内省推/拉、张力驱动主题调度、模型分级。设计原文归档 `checkpoint/26-09-02-agent-cog-arch/`，凝练版 `entries/2026-09-02-cogos-agent-cog-arch.md`。

实施已推进 6 期（意识层第一期 + 工具层 read/write/edit/execute/search/fetch + scratch 草稿纸），read 已改行模式（offset/limit+行号），全量回归 856 passed 已推 master；当前 consciousness 仍是 oneshot 不续轮。代码认知 `entries/2026-09-02-cogos-agent-codebase.md`。

## terminal + timer 实施 + agent 接 cu 讨论（09-03）

terminal + timer 已实施（`../cogos/docs/design-terminal-timer.md` 落地）：terminal.py（busy/idle + buffer/cursor + killpg 中止 + terminal_done 事件）、timer.py（绝对时间戳 + 单调度循环 + timers.json 恢复 + timer_fired 事件）、events.py（AgentEvent/render_event）、app.py（事件队列 + consumer + stop）、tools.py 提取 drain_stream。全量 883 passed 无回归。

e2e（真实 deepseek）：exec 非阻塞验证通过（deliver 长命令 0.66s 未卡 4s）；但 LLM 只调 terminal_open 就停——暴露 agent 层 oneshot 无续轮，open 结果不回传。

→ 引出 agent 接 cu 讨论（收敛）→ 已实施（09-03 晚，见下）。

## agent 接 cu 实施（09-03，完成）

oneshot 改 cu 多轮续轮：Consciousness 持 context + `asyncio.Lock`，`on_message` append user → `runtime.cu(tier="basic")` → `await cu.wait()`；`on_tool_call` 计数超限 interrupt + 调 registry；`on_done` 补 assistant + 兜底 send_msg（非 system 且未 send_msg）。runtime 加 `client` 注入 + `on_tool_call` 异常保护（原会悬挂）。全量 886 passed 无回归。真实 deepseek e2e：`sleep 3 && echo` 6.73s 走通 open→exec→observe→send_msg 完整闭环，terminal_done 事件回传成第二轮 user 消息。细节 `entries/2026-09-03-cogos-agent-cu-wired.md`。

## 锚点

- 约定 / 关键文件 / 设计决策: README.md
- 阶段记录: CHANGELOG.md
- 遗留问题: ISSUES.md · 方向: ROADMAP.md
- 认知地图: entries/project-map.md
- 任务清单: tasks/
- agent-study 挂接: docs/agent-study-hooks.md
