# cogos

多 agent 运行时，飞书作通信总线。通信层已收口，底层三件（lm-service + cog-runtime）完成。主线 = **自驱 agent**，agent 本体 = **动机为根**。术语权威 = `glossary.md`。本体 `../cogos/docs/design-selfdrive-agent.md` 已落后，不以其为准。

## 活跃 · 当前口径

### 使用收口 CLI（10-31，已落码）

把「从零创建并运行一个自驱 agent」收口成一套 CLI，主线＝**程序/语义分离**（代码=程序架子、texts=通用文案库、实例内容=agent 目录文件）。顶层 `cogos` 编排入口（`up/down/status` + `agent create/template/run/stream/stop`），保留 5 个细粒度 console script；`create` 按 name 生成目录＋声明 `agent.yaml` 展开 `agent.json`+`profile.json`＋`birth.yaml` 声明=运行（占位符白名单 `{name}/{phone_number}/{contacts}`）；`up/down/status` 走服务清单（lm-service 编排层 PID 自管＋feishu 复用）；`run` 不携带属性参数（属性在 create 固定进 agent.json，run 派生）。三段落码 `31267e3`→`abeee16`→`48708e3`，全量 1445 passed，公开入口 `cogos agent run` 真跑 PASS。→ `entries/2026-10-31-cogos-usage-cli.md`

### 模型面向文本多语言资源库（10-30 选型·10-31 已落码收口，无尾巴）

所有模型面向语言剥离为语言资源库：`texts/{lang}/` 分目录，英文 canonical + 中文全量，`--lang` 切换（默认 en），配 hash manifest 同步检查（scan/check/view/commit，测试 import check，不变量=manifest==文件非"全同步"）。范围全搬不留尾巴（prompts/body/memory/toolbox + impl 工具描述）；结构留代码、字符串叶子进库；catalog 改工厂函数收 TextBundle；翻译目的驱动+审核非字面。**3 步已全部执行完毕**（Step 3 含 `texts/en/impl.json` 167 key + `texts/zh/*` 全量 402 key；全量 1377 passed, 6 skipped；commit `ac3d449`），待 YZ 核验。→ `entries/2026-10-30-cogos-model-text-i18n.md`

### 可视化调试工具（10-30，已落码）

调试自驱 agent 的**推理过程**（非程序 bug）＝**看**（模型视角＝流本身，无第二落点）＋**控制**（运行中暂停/恢复）。唯一新增数据＝**schema 落盘＋hash 版本引用**（`schema_ref` note，ID=sha256 前 8 位，跨代码版本回看旧流对得上）；`StreamReader` 把 stream 串成跨 Switch 连续序列、`python -m cogos.debug`（stream/events/cursor/pause/resume/shutdown）；控制＝`CogStream.pause()/resume()`（挂介入点 checkpoint 后）+`control.sock`。commit `bb7a489`＋`c97a468`（console script），全量 1363 passed。TUI／多流暂缓。→ `entries/2026-10-30-cogos-debug-visualization.md`

### body catalog 动态裁剪 + N2 启动校验 + 消息 ts（10-30，已落码）

真实 LLM 验证（`--no-phone`＋事件注入，判据全过）暴露**chat 组 no-phone 接线缺口**（catalog 暴露了未接线 impl）。修复三处：**动态裁剪** `Catalog.available`（模型只见已接线能力树，丢未接线 capability＋空组＋note）＋**N2 启动断言** `assert_bound`（catalog↔registry fail-fast，vision/web/time＋无 phone 时 chat 显式 `allow_missing` 放行）＋**消息 ts 补全**（birth context 与事件注入补 `meta.ts`，事件用 `signal.at`）。commit `0c3c148`，全量 1363 passed。→ `entries/2026-10-30-cogos-body-catalog-pruning.md`

### 目录结构规范化（10-30，已落码）

agent_dir 规范三层：**配置**（`agent.json` 总入口＋`profile.json` 纯人设 JSON，取代 `memory/state/profile.md`）／**运行事实**（`runtime.json`/`last_runtime.json`：boot 归档旧 runtime、birth_ts 继承→出生只一次、shutdown 只写 clean、crash 靠缺失推断；Decider 经 `on_state` 在介入点更新 last_state/last_intervene，状态变迁即写＋5s 节流）／**内容**（`stream/`＝意识流 store_dir 落点、`memory/`＝II型平铺、`events/`、`phone/`、`work/`、`machine/<name>/`、`secrets/`）。意识流与记忆平级。commit `ce7ac7a`，全量 1351 passed。→ `entries/2026-10-30-cogos-agent-dir-layout.md`

### 电脑独立 = 一等机器（10-30，已落码）

电脑从"agent 进程内单台 ComputerManager"升为**按账户寻址、可命名、可切默认**的一等对象。隔离边界在**电脑账户身份**（不是 agent 进程降权）：agent 进程统一（管自己 agent_root），body 工具（terminal/fs）副作用发生在电脑账户下。`MachineSpec`+`MachineRegistry`（named machines + `current` 指针，add/remove 普通方法＝预埋 inbound 协助）；terminal/fs spec 接受 callable manager 走 `registry.current`；`DefaultSession` 按机器名切 session；`machine.list/switch` 进 body。本机账户＝`ssh tangyu@localhost`（专用 key，`SshTarget.identity_file`＋`SftpBackend.client_keys`），真机验隔离（tangyu 读不了 zhengyp 敏感目录）。commit `907fe23`，全量 1333+ passed。→ `entries/2026-10-30-cogos-computer-machines.md`

### 自驱 agent 骨架轮廓 + 正式落架子（10-30，已落码）

从「最轻可对话架子」讨论出**终态轮廓**：意识层＝连续 context 流（`stream` 承载、可命名）；元层＝介入点登场的控制/校准功能（**概念非结构**、无单一载体、落 Decider＋State＋后台 LLM 三处）；完整 agent＝6 机制部件（CogStream/Decider/State/事件源/工具层/持久化）。CogStream 之外只两个对象——**State**（不可编辑 facts＋可编辑 policy 两层）＋**Decider**（`on_intervene` 宿主、只读 State＋`take_all()`→Action）；事件链两段＝源 push `EventStore.emit`＋agent pull `Decider.take_all`。术语拆三词（介入点/决策/干预）＋事件/张力/张力源＋上电/出生/恢复。**已落码**：第一刀 `stream_loop.py`（`594a762`）→ 正式骨架 `agent/{state,decide,assemble}.py`（`699012e`，skeleton_loop 离线＋feishu_loop 飞书真实收发 PASS）→ run entry `agent/run.py`（`f924140`）→ **第二刀删旧完成**（`3e05270`＋tag `selfdrive-skeleton-freeze`，删 app/consciousness/meta_layer＋旧测试）。→ `entries/2026-10-30-cogos-selfdrive-skeleton.md`

### body 工具验证（阶段0 第二步，10-29，已落码）

裸 cu harness `cogos/experiment/body_verify.py` 证「LLM↔body/memory meta 工具↔实现工具」链路通：只暴露 body+memory 两 schema、实现工具靠 help 发现；任务只写目标、产出物在系统侧，判据=副作用落盘+on_tool_call 痕迹。**11/11 任务全过**，已验 12 能力（file.read/write/edit、terminal.run+observe、time.now/remind、memory.fold/unfold/mark、chat.speak 桩、web.search+browse 真跑）；跳过 vision.see/mark/coord + chat.browse（标注"未验证"）；未验 terminal.send/interrupt、time.wait、web.fetch/cancel/close。**英文化完成**（memory_catalog / memory._DESCRIPTION·_PROMPT / tools.make_memory_specs / config.render_system_prompt → 英文，人名唐钰保留）；内部全英文规范＝schema/说明/system 指令英文、仅对真人按真人语言。**接线缺口待补**（最轻对话驱动要补两处：app.py 传 tools + CogRuntime 接 tool_executor）。→ `entries/2026-10-29-cogos-body-tool-verification.md`

### CogStream 心跳驱动改造（10-29）

CogStream 从「`act()` 显式驱动」改为「构造即后台心跳 + `on_intervene` 单一回调驱动」：去 act、介入点 `TOOL/REASONING/STOPPED`、合法性判据统一为 context 尾消息（继续 ⟺ 尾 ∈ {user,tool} 非空）、`shutdown()` 同步停 task + 软中断且不可重启。意识层挂接最小适配（STOPPED 心跳 Proceed 启动 + Stop/Sleep 后延迟 shutdown 回收 idle task）。commit `56bed02`，全量 1407 passed。→ `entries/2026-10-29-cogos-cogstream-idle-heartbeat.md`

### 通用 vs 专用边界 + 方向流内涌现（10-28）

推进＋控制是**通用结构**（cog_stream 已抽出）；**方向在流内涌现、连续 stream 聚合稳定**；**元层＝维护流内长出的方向不漂**（识别→钉住→回灌），维护回路才是「自驱 agent」与「很长聊天记录」的差别；**醒/睡降为长 stream 整理节律**（方向性、未落码）。改 10-25「方向定/内容长/不让方向自己长出」→「**初始设定＋流内聚合稳定**」；废「目标/方向＝外部锚」。通用层留的洞＝「方向被维护/回灌」动作的挂点。→ `entries/2026-10-28-cogos-generic-specialized-boundary.md`

### LLM 接线：CogStream 机制 + 工具错误分类 + 挂接已落码（10-27~28）

抽出通用连续推理流 **`CogStream`**（纯内存，unit 回调驱动、不变量＝advance 合法 ⟺ context 尾 role∈{user,tool}、软中断回滚、错误分同步 raise/异步 on_exception）；**持久化**（可选 `store_dir`、七态 builtin＋user note、restore、Switch 交叉链接）；**工具错误分类** `ToolResult` 四类（unknown_tool/bad_args/tool_bug/normal，落 executor 层，runtime 只透传）；**Consciousness/MetaLayer 挂接**（`_start_stream`/`_on_intervene`/`_checkpoint`，行为等价纯替换）。**双持久化分叉已拍**：意识层要持久化就给 stream 传 `store_dir`（stream store 是唯一落点），不另做意识层独立持久化；不传则纯内存。commit `ca597be`→`e3f50b0`，全量 1408 passed＋真 LLM 冒烟跑通。→ `entries/2026-10-27-cogos-cogstream.md`、`entries/2026-10-28-cogos-tool-error-classification.md`

### 意识文件版本方案 + 五元决策已落码（10-26，**已退役 10-30 第二刀删旧**）

弃 `wake_version`，意识文件改 `<YYYYMMDD>.TZ<offset>.V<version>.jsonl`；`meta.json` 始终存在、只存 birth/current_day/next_version；上电恢复 = meta 定位上一份文件（存在→读末态、不存在→已归档→ASLEEP）；废 `settle_to_asleep`（`stop` 停当前状态不进 ASLEEP）；新增 `heartbeat.json`（进程生命周期观测，只埋不消费）。介入决策四元扩五元（Stop→IDLE / Sleep→入睡拆开），介入点改名 `tool_done`/`reasoning_done`。commit `2ae2e9d`/`9056050`。→ `entries/2026-10-26-cogos-context-versioning.md`

### 元层 = 校准层；两层关系（10-25）

元层与意识层＝**同一 LLM 推理的两种职责**：意识层**前向推理**（怎么达成）、元层**对齐/校准**（偏没偏）。LLM 语义方向非唯一、有概率随机性、单层长程会漂，两层在介入点交替校准实现稳定。两层围绕**同一核心＝动机/方向/目标**（元层拿它判偏、意识层拿它推进）。→ `entries/2026-10-25-cogos-meta-layer-direction-alignment.md`

### 介入决策五元 Proceed/Relay/Switch/Stop/Sleep（10-25，10-26 扩）

元层介入点控制策略统一，本质＝**下一轮输入从哪来**：**Proceed**（无助推继续，仅工具点，靠程序回灌）/ **Relay**（有助推继续，追加消息）/ **Switch**（重构上下文继续，替换内容）/ **Stop**（停止本轮：settle cu + 转 IDLE）/ **Sleep**（入睡：settle cu + 元层走卸载）。换/不换＝内容「替换/追加」、非 cu。10-26 由四元扩五元（Sleep 从 Stop 去向回升为决策，Stop/Sleep 拆开去向歧义）；介入点 `tool`/`finish`→`tool_done`/`reasoning_done`。取代旧 `Resume`/`Switch`/`Sleep`。10-28 落码：五元翻译成 stream Action 四元（Sleep 不进 Action）。→ 同上两个 entry

### 意识内容组织三动作（10-25）

**组装（从无到有：醒＝出生模板 / 记忆＋事件）→ 接续（从有到有：Proceed/Relay/Switch）→ 卸载（从无到有：整合进记忆/经历）**。**未点明核心＝动机/方向/目标**（引力）：内容组织＝**管道**、动机/方向/目标＝**引力**，两维正交。→ 同 10-25 entry

### 方向来源：持续存在（定）＋环境（长）（10-25，10-28 修订）

动机/方向/目标两来源：**持续存在＝基础条件（定）**＝本性/法则＋种子（每天醒睡、能想能动）；**所处环境＝决定形状（长）**＝人生初课＋根/倾向（人类社会、工具互动）。**10-28 修订**：方向内容在上下文里、流内涌现＋连续 stream 聚合稳定；「持续活着、要想怎么活」只是**初始设定（种子）**，非「禁止方向长出」；元层＝维护方向不漂。→ `entries/2026-10-28-cogos-generic-specialized-boundary.md`

### 主线 = 六步循环 loop（10-15）

机制驱动的**推理步循环**：**装配→推理一步→判走向→留痕(写回)→对齐→回装配**；事件（输入/动力）随时进循环。旧"事件→装载→思考⇄动手→留痕"线性管道作废。→ `entries/2026-10-15-cogos-main-loop-birth.md`

### 出生事件 = 循环冷启动（10-15）

出生＝**事件＋任务**（任务＝系统下达、持续张力：认识自己→试工具→与环境互动→形成初始记忆）；出生＝空记忆退化特例（统一装载）。→ 同 entry

### 动机 = 活＋张力（10-15）

活＝运行基底；张力＝带方向的拉力＝倾向本身；选择＝张力竞争；效价＝张力与结果的反馈。对齐两层（对齐目标用方向量 / 对齐动机用价值）；回音＝自我证实唯一来源＋检视修正。→ `entries/2026-10-15-cogos-motive-tension-echo.md`

### 意识层工具 body＋memory；元层工具 file（10-21 更新）

body（6 组 20 能力 file/vision/chat/terminal/web/time）＋ memory（fold/unfold/mark）＋ 元层 file（read/write/edit，root=agent_root）**均已落码**。→ `entries/2026-10-19-cogos-tool-design.md`、`entries/2026-10-20-cogos-memory-tool.md`、`entries/2026-10-21-cogos-memory-tool-impl.md`、`entries/2026-10-21-cogos-meta-file-tool.md`、`entries/2026-10-21-cogos-body-time-tool.md`

### 意识上下文 + 元层架子已落码（10-24，10-26 版本方案收口，**已退役 10-30 第二刀删旧**）

意识上下文（数据层+接口层，`consciousness.py`）＋ 元层架子 MetaLayer（Monitor+Control，`meta_layer.py`）已落码。10-25 检视修复两轮（`b716a06`/`54b9a7f`）、10-26 版本方案＋五元决策（`2ae2e9d`/`9056050`）已收口，全量 1369 passed。→ `entries/2026-10-24-cogos-consciousness-context.md`、`entries/2026-10-24-cogos-meta-layer-scaffold.md`、`entries/2026-10-26-cogos-context-versioning.md`

## 下一步（10-31 更新）

正式骨架已落（`699012e`）、run entry 已加（`f924140`）、**第二刀删旧已完成**（`3e05270`＋tag `selfdrive-skeleton-freeze`）、**电脑独立已落**（`907fe23`）、**目录规范化已落**（`ce7ac7a`）、**可视化调试已落**（`bb7a489`＋`c97a468`）、**body catalog 裁剪＋N2＋ts 已落**（`0c3c148`）、**使用收口 CLI 已落码（10-31 `31267e3`→`abeee16`→`48708e3`，待 YZ 核验）**。**下一步 = 续推（REASONING 有张力 Relay，首刀后置未做）→ 张力源 → 蒸馏**。**并行支线 = 模型文本 i18n 已收口并 commit（`ac3d449`，3 步 + 尾巴补齐，1377 passed，en/zh 全量，mechanism 23 key，zh 冒烟纯中文）；遗留 2 条注册表级错误串（tool_base.py:113/:133，见 entry）待收**。待钉实现细节：assemble() 返回物（薄生命周期壳 vs 纯 dataclass）、State.policy 持久化落盘格式（runtime.json 只落了 facts，tension_sources 未落）。电脑面遗留：vision/screen resolver 化、body vision/web/time 接线（N2 已显式 `allow_missing` 放行，仍待接）、inbound 协助 transport（只预埋 registry add/remove）。恢复消费：读 last_runtime 判上次退出方式/状态的恢复流程未实现（本次只做记录）。调试面遗留：TUI 界面、多流/后台流/元层流。

## 开放问题（悬置，待讨论）

- **自我**（YZ 自推中，未收口；回音＝自我证实唯一来源）
- 事件**源头链**记不记；**拆/外包判据**（什么算"不适合拆"）
- **锚展开共用机制**未设计（出生走查第一个硬实现点）
- 出生事件**措辞/第一份记忆形状**
- **P7 判"结"主体**、**P8 锚分类学**
- 工具**待定项**：terminal.notify、web.format、toolbox 全集团组织、phone 异步作业、limit 去留、body/toolbox 暴露关系、render_overview 中文、记号表不统一
- **生命周期机制层**：事件来源收窄**永久性**（暂定）；介入具体形态（审视措辞/清理时机/留痕形式，随 G7）；强制 sleep「极限」；SEQ 时间脉络；idle＋halt 张力机制
- **质疑收敛**（10-30，四语义点唯一未讨论）：意识层质疑 → 元层再整理 → 再质疑的循环收敛规则；另三个已解方向＝元认知表达＋展开（工具结果清理/填充侧剥离）、调度优先级（后台 LLM）
- **「State 叫记忆」语义**（10-30 悬置）：State 是程序记忆（元层字段、可持久化）vs agent 自己的记忆（memory 工具 fold/unfold 内容、经历），关系未定；落码用中性字段名、不绑「记忆」
- **参数类悬置**（10-30）：张力源更新具体时机、元层三档（程序→裸 cu→CogStream）选型判据、恢复「间隔多长算长」、后台 LLM 触发时机（倾事件驱动＋周期兜底）；工具结果清理落点张力（`m.to_lm_dict` 处 vs 归 agent 层）
- **目录整理遗留**（10-30）：签名身份（预留 `secrets/` 空位、用途未定）；I型/II型 附着关系（fold 平铺 vs 按主题分组降条数，先平铺）；恢复消费（读 last_runtime 判上次退出，未实现）；`machine/` 与 `work/` 并存未合并

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

- **「方向定/内容长/不让方向自己长出」（10-25）** → 10-28 改「初始设定＋流内聚合稳定」（方向流内涌现＋元层维护）。
- **「目标/方向＝外部锚」（10-28 临时说法）** → 否，方向内容在流内不在外部。
- **介入决策 `Resume`/`Switch`/`Sleep`** → 10-25 被 `Proceed`/`Relay`/`Switch`/`Stop` 取代（Sleep 降为 Stop 去向）；10-26 又扩为五元（Sleep 回升为决策，Stop/Sleep 拆开去向歧义）。
- **wake_version＝醒次数、随重启推进** → 10-25 改锚 day；10-26 连同「日界推进＝full 档整理专属」一并废，由版本方案（birth/current_day/next_version）取代。
- **settle_to_asleep（归一化：start 启动归一化 + stop 收口）** → 10-26 废，`stop` 停当前状态不进 ASLEEP，上电恢复 = meta 定位上一份文件。
- **ACTIVE_STATES（状态过滤选文件）** → 10-26 删，改 meta 定位 + 存在性判据。
- **v2.2 flow 子系统**（`consciousness.py`/`flow.py`/`experience.py` + 脚本 + 3 测试）→ 已退役（10-24 `2f0c34c`）。
- **runtime 骨架七模块**（`6563b28`）→ freeze 删除（`23bff9f`）。
- **工作方法：YZ 自推、kilo 退回编程手（10-15）** → 10-19 废止，回到一起推进。
- **线性管道**「事件→装载→思考⇄动手→留痕」→ 被六步循环取代。
- **意识层工具名 intent（对外）** → body（10-19）。
- **用法缓存「条数上限，LRU」** → 当轮内修剪。
- **time/now/wait/remind 不进 body**（10-18 裁）→ 10-21 推翻，time 组进 body。
- **旧重架子物化**（consciousness 五态状态机＋meta_layer Monitor/Control＋五元决策翻译层＋意识文件版本方案）→ 10-30 第二刀删旧（`3e05270`＋tag `selfdrive-skeleton-freeze`）一并删；元层改口径「概念非结构」（见 glossary「意识层/元层」），五元收为 Action 四元（Sleep 不进 Action）。概念结论仍留 entries 供参考。

## 锚点

- 工程管理：`README.md`、`CHANGELOG.md`、`ISSUES.md`、`ROADMAP.md`、`tasks/`
- 记忆索引：`index.md`；术语：`glossary.md`
