# cogos

多 agent 运行时，飞书作通信总线。通信层已收口，底层三件（lm-service + cog-runtime）完成。主线 = **自驱 agent**，agent 本体 = **动机为根**。术语权威 = `glossary.md`。本体 `../cogos/docs/design-selfdrive-agent.md` 已落后，不以其为准。

## 活跃 · 当前口径

### 主线 = 六步循环 loop（10-15）

机制驱动的**推理步循环**（取代线性管道）：**装配→推理一步→判走向→留痕(写回)→对齐→回装配**；事件（输入/动力）随时进循环（相关并入、无关转向/挂起）。旧"事件→装载→思考⇄动手→留痕"作废，三环节重定位（装载→装配、思考⇄动手→推理＋判走向、留痕→写回贯穿每步）。→ `entries/2026-10-15-cogos-main-loop-birth.md`

### 出生事件 = 循环冷启动（10-15）

初始配置→装配进工作记忆→循环跑→第一份记忆在留痕步落成→七维度被踩出。出生＝**事件＋任务**（任务＝系统下达、持续张力：认识自己→试工具→与环境互动→形成初始记忆）；身份「给/踩」边界（给＝是什么、踩＝怎么用）；教育不引入新机制。**10-19 起工具先行，出生走查顺延到工具落码后**（出生要"试工具"）。→ 同 entry

### 动机 = 活＋张力（10-15）

活＝运行基底（只给"能动的能力"）；**张力＝带方向的拉力＝倾向本身**；选择＝张力竞争；效价＝张力与结果的反馈；好奇＝动机的一种。对齐两层（对齐目标用方向量 / 对齐动机用价值）；回音＝自我证实的唯一来源＋检视修正。→ `entries/2026-10-15-cogos-motive-tension-echo.md`

### 意识层工具 = body＋memory；元层工具 = file（10-21 更新）

对外 **body**（**6 组 20 能力** file/vision/chat/terminal/web/**time**）＋对内 **memory**（fold/unfold/mark 三操作 + overwrite 布尔），**均已落码**（body 10-20、memory 10-21 `d062f2e`、time 组 10-21 `e44fd0c`）。time 组＝now（补暴露已有 time_now）/ wait（新增阻塞 sleep，cap 60s）/ remind（镜像 set_timer）；**wait＝同轮阻塞暂停、remind＝跨轮唤醒**，定位分道。**元层 file**（read/write/edit，root=agent_root 硬约束、根内路径转换）**已落码**（10-21 `bf216c0`：FsChannel 加 `root` 参数 + `make_meta_fs_specs`；装配未接，元层 LLM 未实现）。10-15 的「intent（对外）」改名为 body；「意图＝无声动作指令」概念仍活。→ `entries/2026-10-19-cogos-tool-design.md`、`entries/2026-10-20-cogos-memory-tool.md`、`entries/2026-10-21-cogos-memory-tool-impl.md`、`entries/2026-10-21-cogos-meta-file-tool.md`、`entries/2026-10-21-cogos-body-time-tool.md`

### 主线 = 自驱 agent；runtime 骨架第一步已落码（10-22）

自驱 agent 大量停留概念，先搭**能跑的框架**，三步走：① 搭架子（机制层、内容 stub）→ ② append＋真 LLM＋工具接线验证 → ③ SEQ/蒸馏/对齐动机（前奏＝出生事件）。**第一步已落码**（`6563b28`）：`cogos/agent/runtime/` 七模块（state/agent/heartbeat/events/context/stream/stub），一条 stub 事件走通 `ASLEEP→WAKING_UP→AWAKE→FALLING_ASLEEP→ASLEEP`。**该骨架已 freeze 删除**（`23bff9f`，tag `runtime-skeleton-freeze`），仅作历史参考；架子的验收意义＝两钩子接口形状（`Context.append/entries`＋`Distiller.distill`）已吸收进后续设计。→ `entries/2026-10-22-cogos-runtime-skeleton.md`、`entries/2026-10-22-cogos-agent-lifecycle.md`

### runtime 重设计前置（事件模块 + cu material 改造 + ① 依赖）已落码（10-22~23）

事件模块 `EventStore`（`emit`/`take_all`/`has_events`，全同步 threading.Lock，append-only pending，渲染每 kind 一个转换函数，写好自验不接线）+ cu material 改造（`list[dict]`→`list[Message]`，`to_lm_dict` 等价不变量）+ ① 依赖（`on_tool_done` 回调 + `rounds`/`tokens` + 最终 assistant append）均已落码（`edcfdab`+`d686683`、`2fcac25`、`d6de28f`），为意识上下文落盘做前置。→ `entries/2026-10-22-cogos-event-store.md`、`entries/2026-10-23-cogos-cu-material-message.md`

### 意识上下文（数据层 + 接口层）已落码（10-24）

意识上下文 = **被动持久化服务（积木）**，与 event store 同级，已落码 **② 数据层 + ③ 接口层**，**不含上层编排**。三 commit：退役 v2.2 flow 子系统（`2f0c34c`）→ 数据层（`3d20dce`）→ 接口层（`f76da56`）。载体 `cogos/agent/consciousness.py`：`FileState`（盘上七态含 idle）+ `State`（对外五态含 IDLE）+ `ConsciousnessStore`（数据层）+ `Consciousness`（接口层）。全量 1350 passed。**遗留自决**（构造补 `make_cu`、`continued`→AWAKE、interrupt 顺序、介入点重入 guard、is_first_wake=wake==1）见 entry。→ `entries/2026-10-24-cogos-consciousness-context.md`

## 下一步（10-24 定）

**意识上下文积木已落码（数据层 + 接口层）**。**下一步 = 讨论心跳/元控制层**（＝意识上下文之后的**上层编排**，属更上层系统，另行设计讨论）：① 归一化（启动读盘 → 收敛 ASLEEP）② 醒触发/装载（记忆 → 2 条 `(system,user)` 起点）③ 睡眠三段式（`request_sleep`→介入点判睡→`start_unload`→元层整理记忆→`unload_done`）④ IDLE 唤醒（事件 + `revoke`）。另留：**装载机制**（记忆→起点接口）、**整理/重定向执行机制**（cu done 蒸馏+重定向由谁执行，元层 LLM 还是意识层判走向）。介入「具体形态」（审视措辞/清理时机/留痕形式）仍待实验。

## 开放问题（悬置，待讨论）

- **自我**（YZ 自推中，未收口；回音＝自我证实唯一来源是最近线索）
- 事件**源头链**记不记；**拆/外包判据**（什么算"不适合拆"）
- **锚展开共用机制**未设计（出生走查第一个硬实现点）
- 出生事件**措辞/第一份记忆形状**
- **P7 判"结"主体**、**P8 锚分类学**（承前承重缺口）
- 工具**待定项**：terminal.notify、web.format、toolbox 全集团组织、phone 异步作业、limit 去留、body/toolbox 暴露关系、render_overview 中文、记号表不统一
- **意识过程→记忆沉淀构想**（YZ 10-19）→ 已部分收口：**助推/SEQ** 已进 lifecycle 设计并钉 glossary；**元层 file 已落码**（`bf216c0`）；**「弧」未采用**（维持退役，收口时未重新定义）。→ `entries/2026-10-22-cogos-agent-lifecycle.md`
- **生命周期机制层**（10-21 设计，第一步骨架已落码、其余待实现）：事件来源收窄**永久性**（当前阶段只有 body 工具产生事件、无内部事件/生念，永久还是暂定）；介入**具体形态**（审视措辞/清理时机/留痕形式，待实验）；强制 sleep「极限」定义；SEQ 时间脉络缺口；idle＋halt 张力机制（`stand_down` 候选，后置）

## 参考 · 历史结论（细节进 entries/，正文不铺）

- **记忆动力学重建（10-08）**：记忆＝思考的痕；取即写；三动作＝融合/转变/新建；维度＝用进废退长出的边。→ `entries/2026-10-08-cogos-memory-dynamics.md`
- **系统架构＋人生初课（10-08）**：事件→控制系统→全局工作空间（树生长式）＋记忆；七维度以"我"为中心；出生事件＝第一次认领。→ `entries/2026-10-08-cogos-arch-first-lessons.md`
- **记忆模型 v1/v1.1/v1.2＋外部调研（10-03~04）**：索引＝投影；单值视图；转变物化；索引＝含义表达（句柄＋描述）；离线整理；注入校准；调研＝切分两侧有对应物、共同空白＝结构/维度自动长出。→ `entries/2026-10-03-cogos-memory-*.md`、`entries/2026-10-04-cogos-memory-external-survey.md`
- **形态先行＋定义层（10-05）**：形态 5 要素＝唯一验收基准；投影＝自指（认领）；本性 vs 根；执著可长可消。→ `entries/2026-10-05-cogos-{selfdrive-form,motive-projection-roothood,memory-v0-bootstrap}.md`
- **过程 v2.2＋第一/二刀＋P8（10-03）**：**落码部分有效**（`91fd1de`/`7a67fc3`/`9775293`）；环被六步循环取代。→ `entries/2026-10-03-cogos-{first-cut-flow-claim,experience-axis-readback,p8-association-mechanical}.md`
- **外圈/内圈 × 工具面（09-29~10-01）**：被 v2.2/loop 覆盖；工具二分（外部不占住/自身有界）、槽＝分布式并集仍有效。→ `entries/2026-10-01-cogos-process-toolface-close.md`
- **总结可恢复性（10-02 方法论）**：递归蒸馏 A/B 两层。→ `entries/2026-10-02-cogos-summary-recoverability.md`
- **system prompt 调研（10-09）**：控制配方三构件（few-shot 锚/边界＋例外/注入防护）。→ `entries/2026-10-09-cogos-system-prompt-study.md`
- **toolbox 呈现（09-28）**：落码有效（`f8ef94a`…`ab46a5b`），设计被新 body/toolbox 覆盖。→ `entries/2026-09-28-cogos-toolbox-*.md`
- **screenlab 图形面（09-20~26）**：已收尾，tag `screenlab-v2-freeze`。→ `entries/2026-09-20/22/23-cogos-screen-*.md`

## 废弃

- **v2.2 flow 子系统**（`consciousness.py`/`flow.py`/`experience.py` + `scripts/exp_*.py` + 3 测试）→ 已退役（10-24 `2f0c34c`）；agent 暂时 inert（收事件不推理），待上层编排/六步循环落地后重新接线。
- **runtime 骨架七模块**（`6563b28`）→ freeze 删除（`23bff9f`）。
- **工作方法：YZ 自推、kilo 退回编程手（10-15）** → 10-19 废止，回到一起推进（见 `worklog/README.md`）。
- **线性管道**「事件→装载→思考⇄动手→留痕」→ 被六步循环取代。
- **意识层工具名 intent（对外）** → body（10-19）。
- **用法缓存「条数上限，LRU」** → 当轮内修剪（tool-body-impl §4）。
- **time/now/wait/remind 不进 body**（10-18 裁）→ 10-21 推翻，time 组进 body（now/wait/remind）。

## 锚点

- 工程管理：`README.md`、`CHANGELOG.md`、`ISSUES.md`、`ROADMAP.md`、`tasks/`
- 记忆索引：`index.md`；术语：`glossary.md`
