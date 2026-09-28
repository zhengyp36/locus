# cogos

多 agent 运行时，飞书作通信总线。通信层已收口，底层三件（lm-service + cog-runtime）完成。主线 = **自驱回路** → **agent 本体 = 动机为根** → 会话 #11~#18 收敛出 **agent 模型（重投影/回看/事件轴）**；当前口径见本体 `../cogos/docs/design-selfdrive-agent.md`（唯一权威）。

## 最近收口：工具呈现 toolbox（09-28）

- **工具从"散"到"可用"**：模型只见 **3 组用法总览（常驻 `system-reminder`）＋ 单一元工具 `toolbox`**；schema 恒定吃前缀缓存；`toolbox help` 逐级精确路径发现、`toolbox call` 精确执行。目的函数＝感知清晰度。
- **实现已提交**：cogos master `f8ef94a`(S0) `67011d0`(S1) `fd2752b`(S2) `8a5cdf1` `42f09aa`(S3) `9183508`(S4)；工作树干净；`tests/agent tests/cog_runtime` **300 passed / 3 skipped**（用 `python3.11`）。
- **分层验收全过**：阶段 I/II 真实模型探针（判据 1、2）；阶段 III 主路径真机模型；**S5 真实飞书身份 e2e 本次跑通**——唐钰`COGOS002:A0005` ← 李恪`A0001`，模型 `call run cat E2E-S5.txt` → `S5-REAL-E2E-OK`，并出现 `help` 自纠（判据 3）。
- **教训**：此前误判 S5 为"外部阻塞"（daemon/profile/账号），实为可自解；校准——**判阻塞前先穷举本地可自解项**。
- **行为复跑（09-28，无外溢 harness）**：真实模型 + FakeTelecom 采样 16 次，行为高度一致——首调用前**不** help、直接猜错 `communication.message.send` 的参数（`to`→`target`）撞**裸 Python 异常**、靠 `help` 自纠；**16/16 外发 2 条**（根因 `consciousness.py:52` 去重判断写死 `send_msg`，S3 后失效）。harness 已入库 `66bf679`；详情 `entries/2026-09-28-cogos-toolbox-behaviour-probe.md`。
- **修复批（09-28）**：提交 `225c902`（已 push）——① registry 层记"是否已 send"（覆盖 message/file）修重复外发；② `toolbox` 调用边界按 catalog 校验参数 + 结构化可读错误；③ help 删"绑定"行；N2 catalog↔registry 启动期断言。**N1 裁断=撤下 `open`/`list`/`answer_auth`**（单会话 toolbox 无法定向会话，避免陷阱；多会话=A2，B 被否）。度量（真实模型 n=10）：外发 1 条 10/10、help 0/10、往返数全 4（原 5~7）。**N3 定稿｜N4 并入**（09-28 讨论，YZ 同意，未落码）：`run` 语义错位（后果型被当取值型）→ 正解＝run 改发起即返回、取值收敛到读类（`read`/`observe`，回到 §5.2）；命令结束通知机制**已实现**（`term.notify`），只需暴露 run 的 notify 参数；N4（`cancel` 未暴露）同源并入。建议 5 搁置。详情 `entries/2026-09-28-cogos-toolbox-fix.md`。

- **N3 定稿细节**：`entries/2026-09-28-cogos-toolbox-run-semantics.md`。

- **模型面命名准则（09-28 定稿）**：模型好理解优先、与机制实现名解耦（catalog 层映射）；元工具下参数名不可见、模型只能猜 → 稳定猜成同一合理值则对齐先验（三闸：一致性/合理性/证据）；案例 `target→to` 待验。落设计 `../cogos/docs/design-agent-tools.md §19`；`entries/2026-09-28-cogos-model-prior-naming.md`。
- 详情 `entries/2026-09-28-cogos-toolbox-presentation.md`。

## 最近收口：screenlab 图形面（09-20 ~ 09-26，会话 #1~#78）

- **一个 agent 一台"自己能用"的电脑** = `computer` 工具第三面（与 `term`/`fs` 并列）。目标唯一约束 `checkpoint/26-09-26-screenlab/spec-screen-1.md §0.0`。
- **v2 图形面接口层通过独立验收**（`checkpoint/26-09-26-screenlab/acceptance-screen-78.md`）：三动词 `screen_fetch/act/save`、viewing 拆给通用视觉面（`image_ctx`）、坐标恒相对 current frame、`on_change` 客户端判、settle 内化；X11/Windows usage 真值全过，回归 **1235 passed / 4 skipped**。
- **收口件（本体、权威）**：`../cogos/docs/screenlab-freeze.md`（代码清单/设计索引/v2 终态/暂停点）· `../cogos/docs/screenlab-env.md`（环境脱敏）· `../cogos/docs/design-agent-tools.md §16/§18`。
- **分支**：`feat/screenlab-p2` 已 ff 合入 master（`2c82c09`）+ tag `screenlab-v2-freeze`，master/tag 已 push origin。
- **过程依据**：`checkpoint/26-09-26-screenlab/`（工作单 `screenlab-work.md` · 规则 · 77 份 `handoff-screen-*` · design/spec · 实测 · 原型 `screen-lab*` · dev-ops `tools/`）。
- **待 YZ（非承诺）**：**D2**（`screen_act` 的 `acted` 透传设备像素，轻微待修）／**D1**（工具结果图未成模型附件＝上层装配，决定"有反馈"能否端到端）／**gap C**（Android app 端点 Java 未真机验）／Windows·Android 装配+同意入口、Wayland、`SETTLE`/`IDLE`。
- 关键条目：`entries/2026-09-20-cogos-screen-face.md` · `entries/2026-09-20-cogos-screen-net-vbox-bridge.md` · `entries/2026-09-23-cogos-sensitive-info-boundary.md` · 方向素材 `entries/2026-09-22-cogos-screen-direction-material.md`（素材、无结论）。

## 当前：agent 理论——要"能自我长的 agent"（09-14 起，#14~#18）

- **目标**：要能**自己判断、长跑不偏、该顶就顶**的 agent；"好用"与"自驱/有自我"是一件事（迎合≠好用）→ `entries/2026-09-14-cogos-self-convergence.md`
- **自我**＝环里**慢变量**（只能长不能装）；自驱三条件；防偏靠"整合"；判断归它、决定权归规则。
- **#15~#18 推演链**：#18（经历表示/切点=误差/取回内容寻址/整理=抽样重演）已入 `entries/2026-09-17-cogos-experience-representation.md`；#15~#17（动因证伪 → 感知/身份/事件驱动 → 运行框架/流与时间线）交接在归档、未入 entries。总纲 `../cogos/docs/design-selfdrive-agent.md`，过程 `checkpoint/26-09-17-agent-theory/`。
- **#14 后半**：动因收敛到饿/困/疼 → `checkpoint/26-09-17-agent-theory/handoff-cogos-drives.md`
- **倾向探针（#14）**：机制通但只"照结局记账"、无解读 → `entries/2026-09-14-cogos-tendency-probe.md`、`checkpoint/26-09-17-agent-theory/probe-tendency/`

### 前情（会话 #12~13：E0 → 自我是经历长出来 → 压缩探针）

- **E0 手动探针已跑完整回合**（无代码；YZ=世界、AI=机制）→ `entries/2026-09-14-cogos-e0-root-probe.md`、`checkpoint/26-09-17-agent-theory/probe-e0/`
- **方法教训**：temp=0 非确定（须聚合+reps）；测冲突的指令不能引用根原话。
- **转向（YZ）**：**根可能不是必须，自我是经历塑造的**；机制给"位置"、经历长"根" → `entries/2026-09-14-cogos-self-grown-from-experience.md`
- **#13 讨论**：把"自我是经历长出来的"拆清楚（未动手）→ `entries/2026-09-14-cogos-root-self-discussion.md`
- **压缩探针（#13）**：因变量被世界话术+根主导、记忆是弱变量 → 方法校准 → `entries/2026-09-14-cogos-compress-probe.md`、`checkpoint/26-09-17-agent-theory/probe-compress/REPORT.md`
- **09-13 模型链**（根=动机、v0 婴儿期、重投影/事件轴）：`entries/2026-09-13-cogos-{motive-root,v0-arch,reprojection-events}.md`

## 自驱回路（09-11 起主线）

- 转向造自驱推进 agent（L1→L4），入口=dogfood；行业结论=视觉已商品化，力气放回路 → `entries/2026-09-11-cogos-selfdrive-pivot.md`
- S2 首跑 → S3 触发 → S4 判据源外移+分层验收（真机省 ~33%，`9563fe4`）→ `entries/2026-09-11-cogos-{s3-trigger,criterion-dogfood,layered-acceptance,selfdrive-p0}.md`
- 路线修正（09-12）：**自驱地基=上下文组织，非调度机制** → `entries/2026-09-12-cogos-general-agent.md`
- 上下文组织推演链 → `entries/2026-09-12-cogos-{recurrence-arm-analysis,distill-retrieval-frame-swap,frame-swap-trigger,identity-anchor-frame}.md`
- 旧活文档归档 `checkpoint/26-09-11-live-checkpoint/`（ctx-* / handoff-ctx-* 亦在 `checkpoint/26-09-17-agent-theory/`）

## 已收尾

- **通信层（08-07~24）**：用 `cogos/phone`，见本体 `docs/phone-usage.md`；代码现状地图 `entries/project-map.md`。
- **智能系统设计（08-24~27）**：本体 `docs/cogos-concept-system.md`、`docs/cogos-plan.md`、`docs/agent-study-hooks.md`。
- **底层三件（08-29~30）**：lm-service + cog-runtime；归档 `checkpoint/archive/26-08-30-*`。
- **认知图设计探索**：封存为预研（09-01）→ `checkpoint/archive/26-09-01-cog-graph-sealed/`。
- **agent 认知架构 + 实施（09-01~03）** → `entries/2026-09-02-cogos-{agent-cog-arch,agent-codebase}.md`、`2026-09-03-cogos-agent-cu-wired.md`
- **cog-func 范式（09-03）** → `entries/2026-09-03-cogos-cogfunc-paradigm.md`
- **视觉 + image_ctx（09-03~08）** → `entries/2026-09-08-cogos-{vision-image-fields,image-ctx-boundary}.md`；本体 `docs/design-vision-image-fields.md`
- **agent 工具实现（A 层，09-18~20）**：批次 1/2/2.5/3/4a 已提交、4b 缓；phone 文件收发真机全过（`5c5e1b4`+`45ab216`，已 push）→ `entries/2026-09-19-cogos-agent-tools-impl.md`、`checkpoint/26-09-26-agent-tools/`
- 阶段脉络 `CHANGELOG.md`（#15~#18 理论线未入阶段，见上）；认知地图 `entries/project-map.md`。

## 锚点

- **理论评审入口（只讲不推进）**：`checkpoint/26-09-26-theory-residual/handoff-cogos-theory-review.md`
- **敏感信息边界讨论（09-23 #26）** → `entries/2026-09-23-cogos-sensitive-info-boundary.md`
- **并行支线**：`../kilo-resident/checkpoint/26-09-17-phone-number-contacts/`（kilo-resident，别混 v0）
- **工程管理**：`README.md`、`CHANGELOG.md`、`ISSUES.md`、`ROADMAP.md`、`tasks/`
- **记忆索引**：`index.md`
