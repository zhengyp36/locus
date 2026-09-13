# cogos

多 agent 运行时，飞书作通信总线。通信层已收口，底层三件（lm-service + cog-runtime）完成。主线已从视觉/机制转到**自驱回路**，最近定到 **agent 本体 = 动机为根**，下一步搭 **v0 婴儿期**。

## 当前：搭 agent v0（09-13，会话 #8/#9）

- **根 = 动机**，目的从动机长、任务从目的长；"给不了动机"与"不能自驱"是同一件事的两面。动作：给值→给函数；连续是纵向的、"我"是位置不是内容。→ `entries/2026-09-13-cogos-motive-root.md`
- **v0 架构**：system prompt = 每回合从文档装配的位（根 `root.md` + 账号 `profile.md` + 能力）；记忆/整理/议程全归机制层，它只思考行动、只看投影；输入以「经历」进入（≠待办）。v0 = 婴儿期：环境驱动、根在场、**不设 tick、不期待生念**。→ `entries/2026-09-13-cogos-v0-arch.md`
- **下一步（动手）**：落盘记忆（`log.jsonl` + `root.md` + `profile.md` + 土选取）+ 每回合装配 system prompt + 帧 dump。交接 `work/A/checkpoint/handoff-build-agent-v0.md`，入口 `work/A/checkpoint/status.md`；代码基线 `work/A/cogos-s2 @ 9563fe4`（1061 passed）。
- 待 YZ：根措辞（`root.md` 种子）；L2 最小自触发（醒来再跑一条 + 预算/暂停安全件）；工位隔离（代码身份）。

## 自驱回路（09-11 起主线）

- 转向：造能自驱推进的 agent（L1→L4 阶梯），入口 = dogfood；行业评估结论 = 视觉已商品化，力气放回路。→ `entries/2026-09-11-cogos-selfdrive-pivot.md`
- S2 首跑 → S3 触发（壳自动选条）→ S4 判据源外移（agent 写红测试）+ 分层验收（真机省 ~33%，`9563fe4`）。→ `entries/2026-09-11-cogos-s3-trigger.md`、`cogos-criterion-dogfood.md`、`cogos-layered-acceptance.md`、`cogos-selfdrive-p0.md`
- 路线修正（09-12）：**自驱地基 = 上下文组织，不是调度机制**。→ `entries/2026-09-12-cogos-general-agent.md`
- 上下文组织推演链：复现实验 → 蒸馏再校正（投影≠替换、回取≠立即取、换帧要质变）→ 换帧边界（唯一触发=目的变了）→ **身份即锚/脊** → 动机为根。→ `entries/2026-09-12-cogos-{recurrence-arm-analysis,distill-retrieval-frame-swap,frame-swap-trigger,identity-anchor-frame}.md`
- 活文档：`work/A/checkpoint/ctx-*.md`、`handoff-ctx-*.md`、`ctx-swap-probe-report.md`。

## 已收尾

- **通信层（08-07~24）**：用 `cogos/phone`，见本体 `docs/phone-usage.md`；代码现状地图 `entries/project-map.md`。
- **智能系统设计（08-24~27）**：本体 `docs/cogos-concept-system.md`、`docs/cogos-plan.md`、`docs/agent-study-hooks.md`。
- **底层三件（08-29~30）**：lm-service（tier basic/advanced、thinking 默认关、契约 `LmClient.chat`）+ cog-runtime 完成；归档 `checkpoint/archive/26-08-30-*`。
- **认知图设计探索**：封存为预研（09-01），聊天 MVP 暂停。归档 `checkpoint/archive/26-09-01-cog-graph-sealed/`。
- **agent 认知架构 + 实施（09-01~03）**：覆盖式回合 / 状态对象；read 行模式；terminal + timer；agent 接 cu 多轮续轮。→ `entries/2026-09-02-cogos-{agent-cog-arch,agent-codebase}.md`、`2026-09-03-cogos-agent-cu-wired.md`
- **cog-func 范式（09-03）**：cog-actor / cog-func / cog-unit 三层；img-tool 已实现。→ `entries/2026-09-03-cogos-cogfunc-paradigm.md`
- **视觉 + image_ctx（09-03~08）**：镜筒 / 视野三层、FIG/域、坐标三套化；设计定稿、P1~P4 落码。→ `entries/2026-09-08-cogos-{vision-image-fields,image-ctx-boundary}.md`；本体 `docs/design-vision-image-fields.md`
- 完整阶段脉络 `CHANGELOG.md`；认知地图 `entries/project-map.md`。

## 锚点

- 当前交接: `work/A/checkpoint/handoff-build-agent-v0.md`
- 并行支线: `work/A/checkpoint/handoff-kilo-number-contacts.md`（kilo-resident，别混 v0）
- 工程管理: `README.md`（remote/本体/关键文件）、`CHANGELOG.md`、`ISSUES.md`、`ROADMAP.md`、`tasks/`
- 旧活文档归档: `checkpoint/26-09-11-live-checkpoint/`
