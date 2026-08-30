# cogos

多 agent 运行时，飞书作通信总线。通信层已收口，智能系统设计已收敛，进入实施（底层三件）。

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

## 锚点

- 约定 / 关键文件 / 设计决策: README.md
- 阶段记录: CHANGELOG.md
- 遗留问题: ISSUES.md · 方向: ROADMAP.md
- 认知地图: entries/project-map.md
- 任务清单: tasks/
- agent-study 挂接: docs/agent-study-hooks.md
