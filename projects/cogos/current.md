# cogos

多 agent 运行时，飞书作通信总线。通信层已收口，底层三件（lm-service + cog-runtime）完成。主线 = **自驱回路** → **agent 本体 = 动机为根** → 会话 #11~#18 收敛出 **agent 模型（重投影/回看/事件轴）**；当前口径见本体 `../cogos/docs/design-selfdrive-agent.md`（唯一权威）；09-28 起主线转**外圈/内圈**（见下）。

## 当前：转外圈/内圈（09-28 起；09-30 整理）

> 术语单一权威＝`glossary.md`（09-30 立）：**意图现义＝无声动作指令**；09-28"作用域/意图态"口径已收回，旧义 entry 文头有指针。

- **呈现层可停手**：形态/落码/验证齐、A 工位无漂移、残留无一阻塞；`term.notify` 无消费者＝**外圈接线**非呈现尾巴；记忆更正两条（`image_ctx` 有引用／D1 未闭合）。→ `entries/2026-09-28-cogos-loop-pivot.md` §1/§2
- **推进方式**：现状＝**最简形态**（非退化），逐个换零件；只确认**第一刀＋直接上下游**（循环依赖不排全序）：前置（通道想=`content`/说=send/沉默=默认＋段最小字段）→ 第一刀落段（**代理口径**，不得声称"外圈稳"）→ 第二刀 `段→写回→装载` 回边 → 完整版意图；后果读者取 A。→ loop-pivot §3 · `entries/2026-09-29-cogos-cu-boundary-and-line.md` §0
- **意图落位**：横跨外圈中段＋内圈（非并列线）；否"先做完整意图"（依赖倒置）。09-28 旧口径（作用域/意图态）已收回；机制素材（允许集/缓存短 TTL/升级梯/enter-exit 界桩）仍有效。→ `entries/2026-09-28-cogos-intent-view.md` · `entries/2026-09-28-cogos-intent-execution.md` · `glossary.md`
- **cu/父子**：cu＝机制不介入的 append 区间（实现单位非语义单位），一弧多 cu（打断=重组入口）；父子属编排（关系≠属性）→ **只拆不建**（已执行 `6c33380`）。→ `entries/2026-09-29-cogos-cu-boundary-and-line.md`
- **槽/流/线＋自指**：槽＝状态(我)、流＝一次转移、线＝跨流的事；经历轴＝**图**（装载＝图上按相关性取）；唯一串行点＝槽更新；自指＝槽↔流↔槽闭环（判据跨事件延续），缺"认领/采纳"；**无定论、目的为锚**。→ `entries/2026-09-29-cogos-slot-flow-selfref.md`
- **外圈过程与命名**：主干＝思考⇄动手（两端装载/沉淀），每步带控制（整理=蒸馏·对齐·取回·判停／前置＋对账）；动手分探询/执行；**意图＝无声动作指令＝思考→动手的桥**；内圈＝对段蒸馏出经验（按锚存取）；自驱回边＝未了张力→内部事件；"没动作就结束"完整论证、经验两副面孔、缓存结论见补遗。→ `entries/2026-09-29-cogos-outer-loop-process.md`（§8）
- **非意图（动机层）**：无任务型预算，按时间窗配额/速率，**节流非断崖**，余量足也要缓。→ `entries/2026-09-28-cogos-quota-pacing.md`
- **机制事实（已核代码）**：原生 function calling 痕迹跨轮常驻；`on_tool_call` 丢弃 calls+results＝落段捕获点；事件→唤醒已通、**缺续弧/关联**；抹痕＝渲染时选择（P1 append 即渲染＝默认，先捕获后抹）；`time_form` 死声明待清账。→ loop-pivot §4/§5
- **方法论**：学习三通道（"先猜 vs 先学"＝选通道）、用法知识归记忆；讨论模式（YZ 拍板、按目的→效果展开）、"先讲过程再命名"。→ `entries/2026-09-28-cogos-learning-channels.md` · slot-flow §0 · outer-loop §8

## 最近收口：工具呈现 toolbox（09-28）

- **工具从"散"到"可用"**：模型只见 **3 组用法总览（常驻 `system-reminder`）＋ 单一元工具 `toolbox`**；schema 恒定吃前缀缓存；`toolbox help` 逐级精确路径发现、`toolbox call` 精确执行。目的函数＝感知清晰度。
- **实现已提交**：cogos master `f8ef94a`(S0) `67011d0`(S1) `fd2752b`(S2) `8a5cdf1` `42f09aa`(S3) `9183508`(S4)；工作树干净；`tests/agent tests/cog_runtime` **300 passed / 3 skipped**（用 `python3.11`）。
- **分层验收全过**：阶段 I/II 真实模型探针（判据 1、2）；阶段 III 主路径真机模型；**S5 真实飞书身份 e2e 本次跑通**——唐钰`COGOS002:A0005` ← 李恪`A0001`，模型 `call run cat E2E-S5.txt` → `S5-REAL-E2E-OK`，并出现 `help` 自纠（判据 3）。
- **教训**：此前误判 S5 为"外部阻塞"（daemon/profile/账号），实为可自解；校准——**判阻塞前先穷举本地可自解项**。
- **行为复跑（09-28，无外溢 harness）**：真实模型 + FakeTelecom 采样 16 次，行为高度一致——首调用前**不** help、直接猜错 `communication.message.send` 的参数（`to`→`target`）撞**裸 Python 异常**、靠 `help` 自纠；**16/16 外发 2 条**（根因 `consciousness.py:52` 去重判断写死 `send_msg`，S3 后失效）。harness 已入库 `66bf679`；详情 `entries/2026-09-28-cogos-toolbox-behaviour-probe.md`。
- **修复批（09-28）**：提交 `225c902`（已 push）——① registry 层记"是否已 send"（覆盖 message/file）修重复外发；② `toolbox` 调用边界按 catalog 校验参数 + 结构化可读错误；③ help 删"绑定"行；N2 catalog↔registry 启动期断言。**N1 裁断=撤下 `open`/`list`/`answer_auth`**（单会话 toolbox 无法定向会话，避免陷阱；多会话=A2，B 被否）。度量（真实模型 n=10）：外发 1 条 10/10、help 0/10、往返数全 4（原 5~7）。**N3 定稿｜N4 并入**（09-28 讨论，YZ 同意）：`run` 语义错位（后果型被当取值型）→ 正解＝run 改发起即返回、取值收敛到读类（`read`/`observe`，回到 §5.2）；命令结束通知机制**已实现**（`term.notify`），只需暴露 run 的 notify 参数；N4（`cancel` 未暴露）同源并入。建议 5 搁置。详情 `entries/2026-09-28-cogos-toolbox-fix.md`。

- **N3 定稿细节**：`entries/2026-09-28-cogos-toolbox-run-semantics.md`。

- **模型面命名准则（09-28 定稿）**：模型好理解优先、与机制实现名解耦（catalog 层映射）；元工具下参数名不可见、模型只能猜 → 稳定猜成同一合理值则对齐先验（三闸：一致性/合理性/证据）；案例 `target→to` 已落码验证（n=10 首猜 10/10）。落设计 `../cogos/docs/design-agent-tools.md §19`；`entries/2026-09-28-cogos-model-prior-naming.md`。

- **模型面修订已落码并验证（09-28）**：`run` 发起即返回、不取值（删 `_run_composed`/`_observe_settled`＋`steps` 机制；回执去 `session`、带读法 note；`computer.command` 面级 help 给配方；暴露 `notify`）＋ `computer.web.cancel`/`communication.file.cancel` 暴露 ＋ `communication.*.send` 参数 `target→to`（catalog `arg_map` 映射，impl 不动）。cogos `ab46a5b` ＋ doc `ea2812c` 已 push；测试 `tests/agent` 277 passed、全量 1281 passed（1 个无关 image_ctx 素材缺失 fail）。
- **批 0 闸复评（n=10）**：成功 10/10、help 0/10、工具错 0/10、往返 5（基线 4）；取值全走重定向＋`file.read`。首轮"不达"＝不公平基准＋`to`/`session`/help 三摩擦，消除后达标；否 `settled` 过渡、否原样接受。证据 `checkpoint/26-09-28-toolbox-model-face/`。
- **执行口径**：本改由 **A 工位**执行（原指派 B 未执行）；**B/cogos 与 B/locus 恢复前需 pull**（A 已 push 到 origin master）。
- 详情 `entries/2026-09-28-cogos-toolbox-presentation.md` · `entries/2026-09-28-cogos-toolbox-run-semantics.md` · `entries/2026-09-28-cogos-model-prior-naming.md`。

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
