# 自驱 agent 骨架轮廓 + 正式落架子（10-29 讨论，10-30 落码）

> 状态：轮廓已对齐（10-29），正式骨架已落码（10-30，cogos commit `699012e`）+ 第二刀删旧已完成（`3e05270` + tag `selfdrive-skeleton-freeze`）。
> 来路：实现 CogStream + 重构 MetaLayer/Consciousness 后，感觉重架子不对，想先搭轻聊天架子找起点；讨论中把「最终架子长什么样」想了出来（终态轮廓），再决定「轮廓不轻、实现可轻」。

## 核心结论

### 术语（钉进 glossary）

- **介入点**（intervene point）：TOOL / REASONING / STOPPED 三处回调，机制层，必然发生、必然输出一个 Action。
- **决策**（decision）：介入点输出的中性 Action（Proceed/Relay/Switch/Stop）。
- **干预**（intervene/correct）：决策的子类，特指「偏了要纠」（在 cu 中间插入纠正消息）。词源：本义是 cu 中间插消息纠偏，后 on_done/心跳也借用，一词混三义（时机/中性动作/纠偏），故拆三词。
- **事件 / 张力 / 张力源**：同一东西三阶段——事件进来（发生）；若需办则成张力源（待办）；未解决则持续有张力（拉力）；解决则张力消。张力源 = 外部消息 + 内部任务。
- **上电 / 出生 / 恢复**：上电 = 进程冷启动，一次性；首次上电走出生、非首次走恢复。

### 意识层 / 元层（概念非结构）

- **意识层有唯一载体 → 可命名**：`stream` 就是「意识」，连续 context 流 = 意识流（CogStream 承载）。
- **元层无唯一载体 → 不给对象名**：是「介入点登场的控制/校准功能」这个概念，落在三处——Decider（决策）+ State（记忆）+ 后台 LLM（判断）。锚点 = `on_intervene`。判据 = 完成功能，非「是否调 LLM」（元层可不含 LLM）。
- **旧重架子错在把概念物化成对象**（Consciousness/MetaLayer 类）。新轮廓里状态机/节律/整理降级为「状态字段 + 介入点决策」。
- 完整 agent = 6 机制部件：CogStream（意识流）、Decider（决策）、State（记忆）、事件源、工具层、持久化（+ 将来后台 LLM）。

### 介入点决策逻辑（程序档）

- **STOPPED**：未上电 → 走上电逻辑（出生或恢复）；已上电 → 有事件才介入，否则保持闲置。
- **TOOL**：有事件才介入，否则默认 Proceed（工具结果回灌继续）。
- **REASONING**：必须给决策；有事件 → 事件介入，无事件 → 看张力是否清除（未清除续推、已清除停回闲置）。
- 实现细节：TOOL 回灌用 Proceed（尾=tool 合法）；**REASONING 续推必须 Relay 不能 Proceed**（尾=assistant，Proceed 会 IllegalAction）。

### 程序架子（两个对象）

CogStream 之外只有**两个对象**（不是一不是三：状态/决定解耦）：

- **State（状态对象）**：元层记忆字段，分**不可编辑**（`boot_ts`/`birth_ts`/`powered_on` 系统事实，程序维护 LLM 不可改）+ **可编辑**（`tension_sources` 策略产物，元层程序或 LLM 可更新），可持久化。边界 = 事实 vs 策略。
- **Decider（决策器）**：`on_intervene` 宿主，固定 dispatch（TOOL/REASONING/STOPPED）+ 可替换决策函数；只读 State + `take_all()` 取事件 + 读 context 尾消息 → Action。不持有队列、不执行工具、不知道事件从哪来。

### 事件链两段（push / pull 不冲突）

- 源侧 **push**：impl 对象（ComputerManager/TimerService/WebService/PhoneCapability）`emit(Signal)` → `EventStore.emit` 落盘（`EventStore.emit` 实现 SignalSink 协议）。
- agent 侧 **pull**：Decider 在介入点 `take_all()`，有就 `render_signal` → `Relay` 注入。
- 注入动作 = `Signal → render_signal → Message(role="user")`（来源标注链，非裸文本）。

### 工具结果清理（填充侧剥离，延后实现）——解「元认知表达」+「展开」

- **口径**：不是「下轮清除/当轮可见」，也不是 agent 主动蒸馏；而是**填充侧剥离**——cu.material 完整保留工具结果，只在传给 lm-service 前按工具的剥离函数决定是否填充原始内容。剥的是原始结果本体，元信息（读了哪些行、成功与否）保留。
- **机制**：每工具自带剥离函数；可配置保留几轮（按消息 `meta.round` 比较）；默认剥原始、留元信息。
- **来路**：09-28「抹痕」（`entries/2026-09-28-cogos-loop-pivot.md` §5）→ 粒度从「抹调用痕迹」细到「剥结果内容」、时点从「append 时渲染」挪到「填充侧」→ **展开＝临时重新填充，不依赖 agent 预蒸馏留档**。
- **落点张力（下次实现第一个要钉）**：剥离在「cu 传 lm-service 前」（`runtime.py` `m.to_lm_dict()` 处，通用内核），但约束「归 agent 装配层、别塞 cog-runtime」——如何「每工具自带剥离函数却不污染 cog-runtime」待定。
- **「系统默认丢、agent 主动记」独立成立**：清理机制定了后，agent「记不记」（主动蒸馏/fold 进 memory）是另一条线。

### 后台 LLM（解「调度优先级」）

- 优先级判断**交给模型，不写进程序**。程序偶尔启动**后台 LLM** 判断当前各张力源优先级，结论写入 State；介入点只读结论、做轻量快决策。判断与决策解耦：慢判断后台异步、快决策介入点轻量。
- 元层触发时机从「介入点」扩展为「介入点 + 后台」两种；后台 LLM 只判断不推进，打断/推进仍由介入点通过 Action 完成。

## why（为什么对）

- 主流 agent = 连续追加上下文 + 压缩；另一路 = 写盘再读恢复。两者本质都是蒸馏。本方案把**连续性提为本体**，而非「不得已的工程手段」。
- 连续性 = 上下文本体：经历是一条线，只记脉络、在脉络上长枝叶。人脑不装细节、只装方向目的——方向目的在，细节丢了可重来，这正是蒸馏可行的原因。
- 折叠/展开 = 元层的索引能力，是自驱 agent 与「很长聊天记录」的本质差别。
- 系统默认「丢」、agent 主动「记」：世界不替你存，记不记得住是 agent 自己的事。
- **轮廓不轻，但实现可保持轻**——每块都锚在已有机制（CogStream/介入点/工具），可分阶段长、每阶段只背一个假设。「轻」= 每步假设少，非组件少。

## 被否 / 纠错

- **旧重架子物化**（consciousness 五态状态机 + meta_layer Rhythm/Monitor/Control）→ 否，把状态机/节律/整理物化成对象；新轮廓降级为状态字段 + 介入点决策。
- **「工具结果清理」=「Switch 蒸馏」**（纠错 10-30）→ 否。前者＝填充侧剥离（`m.to_lm_dict` 处、material 完整保留、延后实现）；后者＝元层折叠（Switch 替换为蒸馏产物）。二者不在一层，四 Action 无需「剪枝」。
- **Driver 命名作废**：第一刀 `Driver` 是临时口袋（决策+事件队列+工具执行混装），正式拆成 Decider + 装配。
- **事件源用 asyncio.Queue + push**（第一刀模拟期）→ 正式换 `EventStore.take_all`；`_Sink` 空壳 → `EventStore.emit`。
- **「介入」一词退役或收窄回「干预」**：拆三词（介入点/决策/干预）后，「介入」收窄为泛指（介入点/介入决策语境保留），「干预」=纠偏子义。

## 落码结果

- **第一刀（10-30 `594a762`）**：`experiment/selfdrive/stream_loop.py`，出生→事件→推进→停回闲置闭环 PASS（出生 = system+user+assistant；事件 = chat.message → render_signal 来源标注注入 → terminal.run 副作用落盘）。验证脚本驱动、非 unittest。
- **正式骨架（10-30 `699012e`）**：`agent/state.py`（State 两层 facts/policy）+ `agent/decide.py`（Decider 程序档 on_intervene）+ `agent/assemble.py`（装配，sink=EventStore）。`skeleton_loop.py` 离线闭环 PASS、`feishu_loop.py` 飞书 Kilo→唐钰→Kilo 真实收发 PASS；`scripts/kilo_send.py` 调试入口。飞书前置：tangyu `profile.md` 从 `memory/` 迁到 `memory/state/`（对齐 config.py `state_dir`）。
- **run entry（`f924140`）**：`agent/run.py` 长驻自驱进程（`python3.11 -m cogos.agent.run`），idle 心跳驱动一切、无显式循环。
- **第二刀删旧（`3e05270` + tag `selfdrive-skeleton-freeze`）**：删 `app.py`/`consciousness.py`/`meta_layer.py`（+ 旧测试），保留四 Action + CogStream + 事件/工具层。
- **飞书接入（身份已就绪）**：Kilo phone 卡 `COGOS002:A0006` 在 `~/.cogos/kilo-phone/`；agent 唐钰 = `COGOS002:A0005`。agent 收 = Phone（唐钰卡）+ Perception.listen → message_to_signal → EventStore.emit → Decider take_all → render_signal → Relay；agent 回 = body `chat.speak` 走真实 PhoneCapability。

## 悬置（实现时再讨论）

- **质疑收敛**（四语义点唯一未讨论：意识层质疑 → 元层再整理 → 再质疑的循环收敛规则）。其余三个已解方向：元认知表达+展开（工具结果清理/填充侧剥离）、调度优先级（后台 LLM）。
- **「State 叫记忆」语义**：State 是程序记忆（元层记忆字段、可编辑/不可编辑、可持久化），但「记忆」也指 agent 自己的记忆（memory 工具 fold/unfold 内容、经历）。二者关系未定；落码时 State 用中性字段名、不绑「记忆」。
- 参数类：张力源更新具体时机、元层三档（程序→裸 cu→CogStream）选型判据、恢复「间隔多长算长」、后台 LLM 触发时机（倾向事件驱动+周期兜底）。

## 下一步

续推（REASONING 有张力 Relay，首刀后置未做）→ 张力源 → 蒸馏。待钉实现细节：assemble() 返回物＝薄生命周期壳 vs 纯 dataclass；State 持久化落盘格式（复用 persistence jsonl vs 独立文件）。
