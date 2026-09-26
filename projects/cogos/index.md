# 索引

> 分层：当前阶段（首页）→ 已收尾（归档入口）。细节按需去 entries/ 翻，不逐条占首页。
> `checkpoint/26-09-26-*` = 2026-09-26 归档线；`checkpoint/26-09-17-agent-theory/` = cogos 理论归档。

## 最近收口 · screenlab 图形面（09-20~26，#1~#78）

- **接口层通过独立验收**：三动词 `screen_fetch/act/save`、viewing 拆给 image_ctx、坐标恒相对 current frame、`on_change` 客户端判；X11/Windows usage 真值全过 → `checkpoint/26-09-26-screenlab/acceptance-screen-78.md`
- **收口件（本体）**：`../cogos/docs/screenlab-freeze.md`（代码清单/设计索引/v2 终态/暂停点）· `../cogos/docs/screenlab-env.md` · `../cogos/docs/design-agent-tools.md §16/§18`
- **工作单/规则**：`checkpoint/26-09-26-screenlab/screenlab-work.md` · `screenlab-tools-review.md`（原 `screenlab-rules.md` 已拆出——通用纪律 → locus `rules/task.md`，环境值 → `../cogos/screenlab/tools/README.md`）
- **目标唯一约束**：`checkpoint/26-09-26-screenlab/spec-screen-1.md §0.0`；封板 `design-computer-v2-interface.md`
- **分支**：`feat/screenlab-p2` 已 ff 合入 master（`2c82c09`）+ tag `screenlab-v2-freeze`，master/tag 已 push origin
- **待 YZ**：D2（acted 透传设备像素）／D1（工具结果图未装配成模型附件）／gap C（Android app 端点未真机验）／装配+同意入口、Wayland、SETTLE/IDLE
- 条目：`entries/2026-09-20-cogos-screen-face.md` · `entries/2026-09-20-cogos-screen-net-vbox-bridge.md` · `entries/2026-09-23-cogos-sensitive-info-boundary.md` · 方向素材 `entries/2026-09-22-cogos-screen-direction-material.md`

## 当前 · agent 理论（09-14 起，#14~#18）

- **自我收敛（09-14 #14）**：要"能自我长的 agent"；"好用"＝"自驱/有自我"；自我＝环里**慢变量**（只能长不能装）→ entries/2026-09-14-cogos-self-convergence.md
- **倾向探针（#14）**：机制通但只"照结局记账"、无解读 → entries/2026-09-14-cogos-tendency-probe.md；产物 `checkpoint/26-09-17-agent-theory/probe-tendency/`
- **#14 后半~#18**：#18（经历表示/切点=误差/取回内容寻址/整理=抽样重演）已入 `entries/2026-09-17-cogos-experience-representation.md`；#15~#17（动因证伪 → 感知/身份/事件驱动 → 运行框架/流与时间线）交接、未入 entries。总纲 `../cogos/docs/design-selfdrive-agent.md`；过程 `checkpoint/26-09-17-agent-theory/`（handoff-cogos-{drives,scaffold,perception-tick,loop,experience}）
- **理论评审入口（只讲不推进）**：`checkpoint/26-09-26-theory-residual/handoff-cogos-theory-review.md`

## 当前 · 自驱回路（09-11 起主线）

- 转向造自驱推进 agent（L1→L4）+ 行业评估 → entries/2026-09-11-cogos-selfdrive-pivot.md
- S2/S3/S4：判据源外移 + 分层验收（真机省 ~33%）→ entries/2026-09-11-cogos-{s3-trigger,criterion-dogfood,layered-acceptance,selfdrive-p0}.md
- 路线修正（09-12）：自驱地基=上下文组织 → entries/2026-09-12-cogos-general-agent.md
- 上下文组织推演链 → entries/2026-09-12-cogos-{recurrence-arm-analysis,distill-retrieval-frame-swap,frame-swap-trigger,identity-anchor-frame}.md；报告 `checkpoint/26-09-17-agent-theory/ctx-swap-probe-report.md`
- 动机为根（09-13 #8）→ entries/2026-09-13-cogos-motive-root.md
- v0 架构（09-13 #9）→ entries/2026-09-13-cogos-v0-arch.md；交接 `checkpoint/26-09-17-agent-theory/handoff-build-agent-v0.md`
- E0 探针（#12）→ entries/2026-09-14-cogos-e0-root-probe.md；产物 `checkpoint/26-09-17-agent-theory/probe-e0/`
- 自我是经历长出来的（#13）→ entries/2026-09-14-cogos-self-grown-from-experience.md；#13 讨论拆解 → entries/2026-09-14-cogos-root-self-discussion.md；压缩探针 → entries/2026-09-14-cogos-compress-probe.md、`checkpoint/26-09-17-agent-theory/probe-compress/REPORT.md`
- 旧活文档归档 → checkpoint/26-09-11-live-checkpoint/

## 当前 · agent 工具实现（09-18 起）

- A 层分批（1/2/2.5/3/4a 已提交，4b 缓）→ `checkpoint/26-09-26-agent-tools/`（spec-tools-a / spec-tools-web / spec-phone-files / plan-tools-impl / handoff-tools-01..09 / handoff-phone-files-01/02）；进度 entries/2026-09-19-cogos-agent-tools-impl.md
- 图形面（看屏/操作，09-20）→ entries/2026-09-20-cogos-screen-face.md；设计/实测见上"最近收口"

## 当前 · agent 认知架构（09-01 起）

- 设计凝练 → entries/2026-09-02-cogos-agent-cog-arch.md；归档 → checkpoint/26-09-02-agent-cog-arch/
- 代码认知 + 实施状态 → entries/2026-09-02-cogos-agent-codebase.md
- 视觉图组织/引用规范 → entries/2026-09-08-cogos-vision-image-fields.md；本体 `cogos/docs/design-vision-image-fields.md`
- image_ctx P1~P4 + 职责边界 → entries/2026-09-08-cogos-image-ctx-boundary.md

## 已收尾 · 底层三件实施（08-29 ~ 08-30）

- 任务清单 → tasks/task-1-lm-service.md + task-3-lm-service-fixes.md + task-2-cog-runtime.md + task-4-cog-runtime-impl.md
- 归档 → checkpoint/archive/26-08-30-* / 26-08-29-impl-design/
- 开发计划 → docs/cogos-plan.md

## 已收尾 · 智能系统设计（08-24 ~ 08-27）

- 概念体系 → docs/cogos-concept-system.md；设计理论摘要 → docs/cogos-design-theory-summary.md；agent-study 挂接点 → docs/agent-study-hooks.md
- 复习过程 → checkpoint/archive/26-08-27-agent-study-review/

## 已收尾 · 通信层（08-07 ~ 08-24）

- 代码现状地图 → entries/project-map.md；阶段脉络 → CHANGELOG.md（阶段 1 ~ 3）；细节条目 → entries/（08-12 ~ 08-24 系列）
