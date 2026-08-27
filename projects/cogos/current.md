# cogos

多 agent 运行时，飞书作通信总线。通信层已收口，智能系统设计已收敛，进入实施（底层三件）；实施前已预研上网/视觉并归档。

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

## 预研归档（08-27~08-28，已收口）

底层三件实施前跑了两项分支预研，均已归档，回到底层三件：

- 上网 → docs/webtool-design.md（工具子系统，阶段二实施；阶段 1 只打地基）
- 视觉 → docs/vision-system-design.md（感知子系统，后置实施；阶段 1 只留 schema 钩子）
- 细节：entries/2026-08-28-cogos-vision-system.md（视觉）、locus checkpoint archive 26-08-27-web-search-fetch（上网过程）

## 下一步

按 `docs/cogos-plan.md` 实施阶段 1 底层三件：LLM-Service → CogUnit/CogExecutor（含资源级元控制）→ 认知树（带记忆/浮现远景定 schema）。

## 锚点

- 约定 / 关键文件 / 设计决策: README.md
- 阶段记录: CHANGELOG.md
- 遗留问题: ISSUES.md · 方向: ROADMAP.md
- 认知地图: entries/project-map.md
- agent-study 挂接: docs/agent-study-hooks.md
- 视觉系统预研: docs/vision-system-design.md
- 上网能力设计: docs/webtool-design.md
