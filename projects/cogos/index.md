# 索引

> 分层：当前阶段（首页）→ 已收尾（归档入口）。细节按需去 entries/ 翻，不逐条占首页。
> **术语单一权威 → `glossary.md`**（09-30 立；新词/旧义/撞名当场钉，entry 与本表冲突以本表为准）。
> `checkpoint/26-09-26-*` = 2026-09-26 归档线；`checkpoint/26-09-17-agent-theory/` = cogos 理论归档。

## 最近收口 · 过程 v2.2 + 第一/二刀 + P8（10-03）

- **过程 v2.2（去投影·控制拍）**：环＝事件→装载→生成⇄动手→判结→沉淀；独立控制拍**降可插拔占位、第一刀不实现**（判停并入生成拍＋硬闸；整理/对齐/取回→装载/生成上下文或不做）；**投影只剩自指＝认领**。why：投影必要性未证（E1 天花板）。被否：控制拍必选、think 伪工具、彻底删投影 → `entries/2026-10-03-cogos-first-cut-flow-claim.md §1`、`glossary.md`
- **第一刀已落**：cogos master `91fd1de`（已 push）——`flow.py`＋`consciousness.py`/`app.py`：一事件开一流，装载产「定性＋采纳(理｜搁置｜不理)」，`理`跑生成⇄动手（思考＋工具事实入段`过程`）、其余不推进，**每流恰落一段**（`memory/segments.jsonl`）。承重重评：#1 否决、#3 消解、#2 存活；新焦点 **G1 认领/自指**
- **第二刀已落**：cogos master `7a67fc3`（已 push）——`experience.py`（段 schema＋读侧 `retrieve`/`open_knots`）＋ `consciousness.py` 回边（`recall` 开关）。**从"只写"到"能读回"**。收口件 `entries/2026-10-03-cogos-experience-axis-readback.md`
- **P8 关联机械第一刀已落**：cogos master `9775293`（已 push）——`open_thread_for`/`continuation_for`＋`_land` 续线；开放＝该线**最新**落段（修段级漏）。**只写不读**。收口件 `entries/2026-10-03-cogos-p8-association-mechanical.md`
- **验收**：机制—`tests/agent` 300、`tests/agent tests/cog_runtime` 329 passed；全量 1296 passed（1 无关 image_ctx 素材缺失 fail）。行为—探针固定事件×recall on/off **分叉=True**；**真身份 e2e 已跑**（真 daemon＋真 app `~/.cogos/agent/tangyu`，A0001→A0005 两事件，事件 2 装载读回事件 1 同来源近段）
- **遗留**：`主题/预测/host` 占位；**锚 P8 仍手写『我』占位**；关联**无读侧用法**；`open_knots`（段级）与续线（线级）口径暂不一致；权重=0。承重缺口 P7/P8 仍在；下一刀方向未定
- 实验：`entries/2026-10-03-cogos-projection-experiment-e1.md`（纯推理靠投影持续——天花板未证）；证据 `checkpoint/26-10-03-first-cut/`

## 最近收口 · 记忆模型 v1 / v1.1 / v1.2 ＋ 外部调研（10-03~04）

- **v1**：记忆＝**索引→内容 的有向图**（写建入口、检索走入口不扫描）；记忆＝经历＋经验＋动机倾向；无"世界原样"（逐字＝外部日志、非记忆）；两种投影（重投/蒸馏）；冲击＝入口初始激活；淘汰两步；支持度＋谱系晋升 → `entries/2026-10-03-cogos-memory-model.md`（**§4/§8 已由 v1.1 修订**）
- **v1.1**：**索引＝投影**（线索→锚空间匹配，多结果/语义，非精确 key；锚＝内容在某维度的投影）；**骨架(id/t/线)只作共指**；**单值视图**（agent 只见一份）；被动浮现↔主动回忆同源；**重投判据**（不矛盾=精化就地更新；**真矛盾→转变物化**：旧留"以前看法"＋转变链接、双值+定向）→ `entries/2026-10-03-cogos-memory-projection-unity.md`
- **v1.2**：**索引＝含义表达**（非词；标识型用词/id、语义型用描述；**句柄＋描述**；代号丢语义）→ `entries/2026-10-03-cogos-memory-index-consolidation.md`；检索**拒 RAG**（机制结构粗筛→模型语义判）；**离线整理**（睡眠＝蒸馏＋重整索引；per-agent 技能、差异选择）；**注入校准**（内容只能长、方法可注入可改写、机制固定）
- **设计方法**：重开设计、场景先行；现有 `experience.py` 降为**参考/反例**（dict 精确匹配≠索引，须重审）
- **承重缺口**：投影维度（锚空间）清单＝B 形状；描述长度（倾向）；矛盾判据机械代理；整理触发启发式；D/E/倾向算子。**未落码**
- **外部调研（10-04）**：AI/神经两侧宽扫＋3 精读 → **切分两侧皆有对应物（非臆造）**；**共同空白＝结构/维度自动长出**（对 B）；确立**好处导向**阅读纪律；神经侧 **E1–E4** 好处＝所缺，AI 侧降参照/反例；可借 benchmark、MRAgent"重建式检索" → `entries/2026-10-04-cogos-memory-external-survey.md`（细节 `checkpoint/26-10-04-memory-survey/`）

## 最近收口 · 工具呈现 toolbox（09-28）

- **工具从"散"到"可用"**：3 组常驻总览（`system-reminder`）＋ 单一 `toolbox`；schema 恒定吃前缀缓存；`help` 逐级发现 / `call` 精确执行
- **代码**：cogos master `f8ef94a`(S0) `67011d0`(S1) `fd2752b`(S2) `8a5cdf1` `42f09aa`(S3) `9183508`(S4)；工作树干净；`tests/agent tests/cog_runtime` 300 passed / 3 skipped（用 `python3.11`）
- **验收全过**：阶段 I/II 真实模型探针；阶段 III 主路径真机；**S5 真实飞书身份 e2e**——唐钰`COGOS002:A0005` ← 李恪`A0001`，`call run cat E2E-S5.txt` → `S5-REAL-E2E-OK`（判据 3）
- **行为复跑（无外溢 harness，16 次）**：行为高度一致（先猜错参数撞裸异常→help 自纠；每次都外发 2 条）
- **修复批（09-28，`225c902` 已 push）**：registry 层记"已 send"（修重复外发）＋ 调用边界按 catalog 校验 + 可读错误 ＋ help 删"绑定"行 ＋ N2 启动期断言；**N1 裁断=撤下 `open`/`list`/`answer_auth`**（多会话=A2，B 否）。度量 n=10：外发 1、help 0/10、往返 4（原 5~7）。**N3 定稿｜N4 并入**（YZ 同意）：`run` 语义错位→改发起即返回、取值收敛读类；命令结束通知机制已实现（`term.notify`），只需暴露；建议 5 搁置
- **模型面修订已落码验证（09-28，`ab46a5b`＋`ea2812c`）**：`run` 发起即返回不取值（去 session、面级 help 给读法、暴露 notify）＋ `web.cancel`/`file.cancel` 暴露 ＋ `target→to`（arg_map）；n=10 复跑成功 10/10、help 0、工具错 0、往返 5。证据 `checkpoint/26-09-28-toolbox-model-face/`
- 条目：`entries/2026-09-28-cogos-toolbox-presentation.md` · `entries/2026-09-28-cogos-toolbox-behaviour-probe.md` · `entries/2026-09-28-cogos-toolbox-fix.md` · `entries/2026-09-28-cogos-toolbox-run-semantics.md` · `entries/2026-09-28-cogos-model-prior-naming.md`

## 当前 · 转外圈/内圈（09-28，工具呈现收口后）

- **呈现层可停手 + 转向外圈/内圈**（依据/做法/前置语义/代码事实/抹痕归属）→ `entries/2026-09-28-cogos-loop-pivot.md`
- **学习通道**（先猜 vs 先学 → 选通道）+ 用法知识归记忆 → `entries/2026-09-28-cogos-learning-channels.md`
- **意图（完整口径）**：意图＝意识角色的作用域（就地执行＋渲染隐藏；程序式记忆；渲染三律/吸收-上浮；回看只留结果）→ `entries/2026-09-28-cogos-intent-view.md`｜**目的＝注意力减负、非保密**
- **意图执行模型**：**模式决定允许集**（意图态=视角全集 / 非意图态=缓存集）；`toolbox(intent, enter|exit, content|result)`；入口加载经验/粗 help（只为会用法、不解锁）；出口缓存真实调用过的用法（机制固定格式，驻留≠经验）；append 原地＋短 TTL；尾注提示自判收尾；结果当场＋方法睡中蒸馏；上限=有界失败＋升级梯 执行→诊断→求助 → `entries/2026-09-28-cogos-intent-execution.md`
- **非意图 · 配额/节奏（动机层）**：无任务型预算，按时间窗配额/速率，节流非断崖，余量足也要缓 → `entries/2026-09-28-cogos-quota-pacing.md`
- **cu 边界／父子拆分／连续线索（09-29）**：意图横跨外圈中段（cu/装载/沉淀）＋内圈，便宜版＝第一刀同接缝；cu＝机制不介入的 append 区间（实现单位非语义单位）、一弧多 cu（打断=重组入口）；父子属编排（关系≠属性）**只拆不建**（已执行 `6c33380`）；连续线索＝运行时流／持久层 `thread`+`refs` 链 → `entries/2026-09-29-cogos-cu-boundary-and-line.md`
- **槽/流/自指（09-29 二）**：槽＝状态(我)、流＝转移、线＝事；外圈=显/生产、内圈=陷/沉淀；唯一串行点=槽更新；自指=槽↔流↔槽闭环（判据跨事件延续）；自己的事=未闭合张力、缺"认领/采纳"；**无定论、目的为锚** → `entries/2026-09-29-cogos-slot-flow-selfref.md`（**10-01 更正：槽＝分布式并集、各处更新；见下条**）
- **外圈/内圈的过程与命名（09-29 三）**：外圈主干=思考⇄动手（两端装载/沉淀），**每步带控制**——思考的控制=整理(蒸馏)·对齐目标·取回经验·判停；动手的控制=前置(为什么/在哪/预期)＋后置对账；动手分探询/执行；**意图=无声动作指令=思考→动手的桥**。内圈=睡/批形对段蒸馏出经验（按锚分区存、按锚取回）。自驱回边=未了张力→内部事件。上下文靠压缩+外部存储+按锚取回，不靠长上下文/缓存 → `entries/2026-09-29-cogos-outer-loop-process.md`
- **过程 × 工具面（10-01 收口）**：**工具二分**（外部不占住／自身有界，裁 P2）；**工具层只报事实**（超时≠失败）；**槽＝分布式并集**（解 P1）；工具面三层（能力/用法/事实）；P3 降为命名。承重缺口＝**P7 判"结"主体**、**P8 锚分类学**；下一步＝落**首个受控循环**逼出 → `entries/2026-10-01-cogos-process-toolface-close.md`
- 依据 `checkpoint/26-09-26-theory-residual/checkpoint-1.md` §四~§七（动手纪律/现状摸底/外圈零件序）；本体 `../cogos/docs/design-selfdrive-agent.md`

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

## 参考 · 认知基元索引

- cog-unit / cog-func / cog-object 理论锚点 → entries/cog-primitives-index.md
