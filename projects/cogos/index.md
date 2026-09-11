# 索引

> 分层：当前阶段（首页）→ 已收尾（归档入口）。细节按需去 entries/ 翻，不逐条占首页。

## 当前 · 自驱回路（09-11 起，主线）

- 转向 + 行业评估 + 保命收编 → entries/2026-09-11-cogos-selfdrive-pivot.md
- 计划 + S0 状态面 + 停点 → `../checkpoint/plan.md` / `state.md` / `status.md` / `checkpoint-3.md`（活文档）
- 旧活文档归档 → checkpoint/26-09-11-live-checkpoint/
- task-5 复核通过（验收遇错即止 + phase 计时）→ tasks/task-5-loop-verify-timing.md
- task-6（测试提速）+ task-7（Kilo 常驻多通道 spike）已交工位 B → tasks/
- S4 判据源外移 + 分层验收（真机 dogfood 验证省 ~33%）→ entries/2026-09-11-cogos-layered-acceptance.md；停点 `../checkpoint/status.md`
- 工位隔离更正：服务是设备级单例共用、无 owner；`COGOS_HOME` 仅 dev 用 → entries/2026-09-11-cogos-workstation-isolation.md
- 下一步（待 YZ）：L2 最小自触发（自己醒来再跑一条 + 预算/暂停安全件）

## 当前 · agent 认知架构（09-01 起）

- 设计凝练 → entries/2026-09-02-cogos-agent-cog-arch.md
- 设计原文归档 → checkpoint/26-09-02-agent-cog-arch/agent-prototype-design-v2.md
- 代码认知 + 实施状态 → entries/2026-09-02-cogos-agent-codebase.md
- 视觉图组织/引用规范（域·FIG + 图块K轮寿命；FIG:/PATH:/ANNO:，定稿待实现）→ entries/2026-09-08-cogos-vision-image-fields.md；本体 `cogos/docs/design-vision-image-fields.md`
- image_ctx P1~P4 落码 + 职责边界定案（图模块不管 K 轮/compile，归上下文管理器）+ 坐标基准统一 + 探针收口（§138/§139）→ entries/2026-09-08-cogos-image-ctx-boundary.md
- 探针：`/tmp/kilo/vision/p3probe/{taskA,taskB,probe138}.py`（P3 目的层 A/B + §138 换算精度，非仓库）
- 下一步：衍生推理档（用锚做新相对窗口，检验坐标教学必要性）——待 YZ 开题

## 已收尾 · 底层三件实施（08-29 ~ 08-30）

- 任务清单 → tasks/task-1-lm-service.md（✅ 完成）+ task-3-lm-service-fixes.md（✅ 完成）+ task-2-cog-runtime.md（✅ 设计收敛）+ task-4-cog-runtime-impl.md（✅ 完成）
- lm-service 规格 → docs/design-lm-service-min.md
- lm-service 实施过程归档 → checkpoint/archive/26-08-30-lm-service-impl/（task-1）+ checkpoint/archive/26-08-30-lm-service-fixes/（task-3）
- cog-runtime 设计/实施过程归档 → checkpoint/archive/26-08-30-cog-runtime-impl/（task-2 设计 + task-4 实施）
- lm-service 设计过程归档 → checkpoint/archive/26-08-29-impl-design/
- 开发计划 → docs/cogos-plan.md

## 已收尾 · 智能系统设计（08-24 ~ 08-27）

- 概念体系 → docs/cogos-concept-system.md
- 设计理论摘要 → docs/cogos-design-theory-summary.md
- agent-study 挂接点 → docs/agent-study-hooks.md
- 复习过程与阶段预估 → checkpoint/archive/26-08-27-agent-study-review/

## 已收尾 · 通信层（08-07 ~ 08-24）

- 代码现状地图 → entries/project-map.md
- 阶段脉络 → CHANGELOG.md（阶段 1 ~ 3）
- 细节条目 → entries/（08-12 ~ 08-24 系列，按日期命名，含 phone / 群聊 / 账号）
