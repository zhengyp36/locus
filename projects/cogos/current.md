# cogos

多 agent 运行时，飞书作通信总线。通信层已收口，智能系统设计已收敛，进入实施（底层三件）。

## 通信（已收口）

后续通信用 `cogos/phone`，用法见 `docs/phone-usage.md` / `docs/comm-full-design.md`。细节不再记，用时看文档。

## 设计已收敛（08/24–08/26）

讨论收敛为概念体系 + 开发计划，固化到本体 docs：

- 概念体系：`docs/cogos-concept-system.md`
- 开发计划：`docs/cogos-plan.md`
- 理论摘要：`docs/cogos-design-theory-summary.md`

## agent-study 复习（08-26 晚 ~ 08-27，已收尾）

31 条已确认结论全过，保留项挂接进 cogos 模块，固化 `docs/agent-study-hooks.md`。关键新决策：元控制二分（资源级=机制层预装不可自长 / 认知级=策略层自长方法论）。两个设计缺口进 ISSUES（缺过程元控制 / 缺诊断调试观察）。过程归档 `checkpoint/archive/26-08-27-agent-study-review/`。

## 下一步

按 `docs/cogos-plan.md` 实施阶段 1 底层三件：LLM-Service → CogUnit/CogExecutor（含资源级元控制）→ 认知树（带记忆/浮现远景定 schema）。

## 锚点

- 约定 / 关键文件 / 设计决策: README.md
- 阶段记录: CHANGELOG.md
- 遗留问题: ISSUES.md · 方向: ROADMAP.md
- 认知地图: entries/project-map.md
- agent-study 挂接: docs/agent-study-hooks.md
