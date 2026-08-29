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

## 当前：并行实施（08-29 起）

- 任务1（工位 B）：lm-service 实施 → `tasks/task-1-lm-service.md`，规格 `docs/design-lm-service-min.md`
- 任务2（工位 A）：cog-runtime 设计讨论 → 活文档 `../checkpoint/design-cog-runtime.md`

lm-service 最小版已收敛 v1（`docs/design-lm-service-min.md`）：LmClient 冻结契约（chat → 归一响应 + `LmServiceError(category)`）、category 六类字符串枚举（非错误码）、config/secrets/state 三文件分离、router 模态>tier、调试 jsonl + admin calls。过程归档 `checkpoint/archive/26-08-29-impl-design/`。

## 锚点

- 约定 / 关键文件 / 设计决策: README.md
- 阶段记录: CHANGELOG.md
- 遗留问题: ISSUES.md · 方向: ROADMAP.md
- 认知地图: entries/project-map.md
- 任务清单: tasks/
- agent-study 挂接: docs/agent-study-hooks.md
