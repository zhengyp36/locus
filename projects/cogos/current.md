# cogos

多 agent 运行时，飞书作通信总线。通信层已收口，底层三件（lm-service + cog-runtime）完成。主线 = **自驱 agent**，agent 本体 = **动机为根**。术语权威 = `glossary.md`。本体 `../cogos/docs/design-selfdrive-agent.md` 已落后，不以其为准。

## 活跃 · 当前口径

### 元层 = 校准层；两层关系（10-25）

元层与意识层＝**同一 LLM 推理的两种职责**：意识层**前向推理**（怎么达成）、元层**对齐/校准**（偏没偏）。LLM 语义方向非唯一、有概率随机性、单层长程会漂，两层在介入点交替校准实现稳定。两层围绕**同一核心＝动机/方向/目标**（元层拿它判偏、意识层拿它推进）。→ `entries/2026-10-25-cogos-meta-layer-direction-alignment.md`

### 介入决策四元 Proceed/Relay/Switch/Stop（10-25）

元层介入点控制策略统一为四元，本质＝**下一轮输入从哪来**：**Proceed**（无助推继续，仅工具点，靠程序回灌）/ **Relay**（有助推继续，追加消息）/ **Switch**（重构上下文继续，替换内容）/ **Stop**（停止，去 unload→ASLEEP 或 idle）。换/不换＝内容「替换/追加」、非 cu；Sleep 降为 Stop 的去向、不再是决策。取代旧 `Resume`/`Switch`/`Sleep`。→ 同 entry

### 意识内容组织三动作（10-25）

**组装（从无到有：醒＝出生模板 / 记忆＋事件）→ 接续（从有到有：Proceed/Relay/Switch）→ 卸载（从无到有：整合进记忆/经历）**。**未点明核心＝动机/方向/目标**（引力）：内容组织＝**管道**、动机/方向/目标＝**引力**，两维正交。→ 同 entry

### 方向来源：持续存在（定）＋环境（长）（10-25）

动机/方向/目标两来源：**持续存在＝基础条件（定）**＝本性/法则＋种子（每天醒睡、能想能动）；**所处环境＝决定形状（长）**＝人生初课＋根/倾向（人类社会、工具互动）。**方向定、内容长**：定**方向/张力**（持续存在、与人打交道、思考价值），不定**内容/结论**（价值是什么——必须自己长）；不让方向自己长出。→ 同 entry

### 日界推进 = full 档整理专属（10-25）

wake_version 改锚**节律周期号（day）**：**只在时间界点（24:00）的睡眠整理（full 档）时推进**，不靠时钟独立递增，进程重启/归一化不推进；"今天→昨天"＝full 档整理时的时间投射推进。is_first_wake＝day==1 且日内首醒。→ 同 entry

### 主线 = 六步循环 loop（10-15）

机制驱动的**推理步循环**：**装配→推理一步→判走向→留痕(写回)→对齐→回装配**；事件（输入/动力）随时进循环。旧"事件→装载→思考⇄动手→留痕"线性管道作废。→ `entries/2026-10-15-cogos-main-loop-birth.md`

### 出生事件 = 循环冷启动（10-15）

出生＝**事件＋任务**（任务＝系统下达、持续张力：认识自己→试工具→与环境互动→形成初始记忆）；出生＝空记忆退化特例（统一装载）。→ 同 entry

### 动机 = 活＋张力（10-15）

活＝运行基底；张力＝带方向的拉力＝倾向本身；选择＝张力竞争；效价＝张力与结果的反馈。对齐两层（对齐目标用方向量 / 对齐动机用价值）；回音＝自我证实唯一来源＋检视修正。→ `entries/2026-10-15-cogos-motive-tension-echo.md`

### 意识层工具 body＋memory；元层工具 file（10-21 更新）

body（6 组 20 能力 file/vision/chat/terminal/web/time）＋ memory（fold/unfold/mark）＋ 元层 file（read/write/edit，root=agent_root）**均已落码**。→ `entries/2026-10-19-cogos-tool-design.md`、`entries/2026-10-20-cogos-memory-tool.md`、`entries/2026-10-21-cogos-memory-tool-impl.md`、`entries/2026-10-21-cogos-meta-file-tool.md`、`entries/2026-10-21-cogos-body-time-tool.md`

### 意识上下文 + 元层架子已落码（10-24，10-25 检视修复收口）

意识上下文（数据层+接口层，`consciousness.py`）＋ 元层架子 MetaLayer（Monitor+Control，`meta_layer.py`）已落码。**10-25 检视修复两轮已收口**（`b716a06`/`54b9a7f`，全量 1369 passed）：醒/睡 flow 内聚、`last_ts`、归一化=settle_to_asleep、start/stop 对称收口、`cons`→`consciousness`。→ `entries/2026-10-24-cogos-consciousness-context.md`、`entries/2026-10-24-cogos-meta-layer-scaffold.md`

## 下一步（10-25 定）

方向已对齐（介入决策四元＋内容组织三动作＋方向来源）。下一步 = **LLM 接线**：G2 装载（组装原语）、G3 整理（分级，先只 full 档）、G7 介入形态（四元决策落地）、工具执行层 `on_tool_call`。**IDLE 整理（medium 档）后置**。

## 开放问题（悬置，待讨论）

- **自我**（YZ 自推中，未收口；回音＝自我证实唯一来源）
- 事件**源头链**记不记；**拆/外包判据**（什么算"不适合拆"）
- **锚展开共用机制**未设计（出生走查第一个硬实现点）
- 出生事件**措辞/第一份记忆形状**
- **P7 判"结"主体**、**P8 锚分类学**
- 工具**待定项**：terminal.notify、web.format、toolbox 全集团组织、phone 异步作业、limit 去留、body/toolbox 暴露关系、render_overview 中文、记号表不统一
- **生命周期机制层**：事件来源收窄**永久性**（暂定）；介入具体形态（审视措辞/清理时机/留痕形式，随 G7）；强制 sleep「极限」；SEQ 时间脉络；idle＋halt 张力机制

## 参考 · 历史结论（细节进 entries/，正文不铺）

- **记忆动力学重建（10-08）**：记忆＝思考的痕；取即写；三动作＝融合/转变/新建；维度＝用进废退长出的边。→ `entries/2026-10-08-cogos-memory-dynamics.md`
- **系统架构＋人生初课（10-08）**：事件→控制系统→全局工作空间＋记忆；七维度以"我"为中心；出生事件＝第一次认领。→ `entries/2026-10-08-cogos-arch-first-lessons.md`
- **记忆模型 v1/v1.1/v1.2＋外部调研（10-03~04）**：索引＝投影；单值视图；转变物化；索引＝含义表达；离线整理；注入校准。→ `entries/2026-10-03-cogos-memory-*.md`、`entries/2026-10-04-cogos-memory-external-survey.md`
- **形态先行＋定义层（10-05）**：形态 5 要素＝唯一验收基准；投影＝自指；本性 vs 根。→ `entries/2026-10-05-cogos-{selfdrive-form,motive-projection-roothood,memory-v0-bootstrap}.md`
- **过程 v2.2＋第一/二刀＋P8（10-03）**：落码部分有效；环被六步循环取代。→ `entries/2026-10-03-cogos-{first-cut-flow-claim,experience-axis-readback,p8-association-mechanical}.md`
- **外圈/内圈 × 工具面（09-29~10-01）**：被 v2.2/loop 覆盖；工具二分、槽＝分布式并集仍有效。→ `entries/2026-10-01-cogos-process-toolface-close.md`
- **总结可恢复性（10-02 方法论）**：递归蒸馏 A/B 两层。→ `entries/2026-10-02-cogos-summary-recoverability.md`
- **system prompt 调研（10-09）**：控制配方三构件。→ `entries/2026-10-09-cogos-system-prompt-study.md`
- **toolbox 呈现（09-28）**：落码有效，设计被新 body/toolbox 覆盖。→ `entries/2026-09-28-cogos-toolbox-*.md`
- **screenlab 图形面（09-20~26）**：已收尾，tag `screenlab-v2-freeze`。→ `entries/2026-09-20/22/23-cogos-screen-*.md`

## 废弃

- **介入决策 `Resume`/`Switch`/`Sleep`** → 10-25 被四元 `Proceed`/`Relay`/`Switch`/`Stop` 取代（Sleep 降为 Stop 去向）。
- **wake_version＝醒次数、随重启推进** → 10-25 改锚节律周期号（day）、full 档整理专属。
- **v2.2 flow 子系统**（`consciousness.py`/`flow.py`/`experience.py` + 脚本 + 3 测试）→ 已退役（10-24 `2f0c34c`）。
- **runtime 骨架七模块**（`6563b28`）→ freeze 删除（`23bff9f`）。
- **工作方法：YZ 自推、kilo 退回编程手（10-15）** → 10-19 废止，回到一起推进。
- **线性管道**「事件→装载→思考⇄动手→留痕」→ 被六步循环取代。
- **意识层工具名 intent（对外）** → body（10-19）。
- **用法缓存「条数上限，LRU」** → 当轮内修剪。
- **time/now/wait/remind 不进 body**（10-18 裁）→ 10-21 推翻，time 组进 body。

## 锚点

- 工程管理：`README.md`、`CHANGELOG.md`、`ISSUES.md`、`ROADMAP.md`、`tasks/`
- 记忆索引：`index.md`；术语：`glossary.md`
