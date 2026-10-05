# cogos

多 agent 运行时，飞书作通信总线。通信层已收口，底层三件（lm-service + cog-runtime）完成。主线 = **自驱回路** → **agent 本体 = 动机为根** → 会话 #11~#18 收敛出 **agent 模型（重投影/回看/事件轴）**。**本体 `../cogos/docs/design-selfdrive-agent.md` 已落后，不以其为准**；当前口径＝过程 **v2.2**（10-03，见下），术语权威＝`glossary.md`。**下一步主线＝记忆模型**（10-03 收口，见下）；经历轴＝其经历层雏形。**10-05 定义层收口**（本性/根 · 投影＝认领，见下）。

## 当前：转向形态先行（10-05 晚，收口）

> 10-05 晚讨论收口：困在"自我→认领"怪圈，判**"自我"不是机制前提**（只是记忆积累后的叙事名）。转向：**先定自驱 agent 外在形态（可观察行为规格），再从形态反推机制**——形态是唯一验收基准，机制是可丢弃的候选假设。
> 理论**封存为参考**（`scratch/2026-10-04-memory-module/frozen-theory/`），留两类锚：
> - **教训锚（被否，防重犯）**：精确 dict 索引 / "要动·要活"当种子 / 种子当隐藏 prompt / "自我"当机制前提。
> - **参考锚（候选素材，降级）**：投影＝认领 / 记忆＝独特部分 / 慢层＝效价筛出 / 预测误差＝新奇 / tick＝事件源 / 四位置 / 两段 LLM。
> 形态 5 要素＝**主动 / 连续 / 自洽标准 / 自主抗命 / 协作**，每条配可观察判据＝验收基准。规格草稿 `scratch/2026-10-05-selfdrive-form/form-spec.md`（待 YZ 验收）。下一步＝验收后从形态反推最小机制。

## 已封存（参考）：记忆模块 v0 形状 + 生念/自启（10-05 续，收口）

> 收口件＝`entries/2026-10-05-cogos-memory-v0-bootstrap.md`；术语＝`glossary.md`（＋好奇·新奇取向／空闲事件·tick／浅浮现；补注 注入/种子）。承 10-05 定义层 · 10-03 memory v1.x。**纯讨论、未落码；下一步＝照 v0 形状动手（5 步、逐步验收，见 `scratch/2026-10-04-memory-module/handoff-v0-build.md`）**。

- **v0 形状（无索引）**：`记(经历)->id | 忆(线索)->内容|浅浮现(锚)|None | 整理()`；数据＝种子层＋段{id,t,内容,效价,结,来源,refs}；**单值、无候选、无采纳**；`忆` 必含**自我路（效价/未了/近因）＋语义路**，否则塌主题；v0 不建索引层（锚/维度留 v1+）。
- **用法＝四位置**：M1 投影时读（给自我/定方向）· M2 穿插读（回边）· M3 停时写（沉淀）· M4 离线整理。记忆＝被机制层在四时点调用的独立源。
- **生念**：**种子＝常驻驱动力（不退役）**→ 空白不需特殊首启（seed-only 投影）；**好奇＝未闭合信息缺口→张力（＝自产未了）**；LLM 产缺口不演好奇；好奇（张力）×效价（沉淀）两条轴。
- **tick**：信号无内容→机制合成**空闲事件**（最小事实模板＝内部事件）；外/内事件统一同环；触发最简＝闲置超时（概率斜坡是精化）。
- **环路**：事件→装载(解析+投影；读)→生成→动手→判结→沉淀(写)；**两段 LLM**（机制层投影→意识层生成），事件不直接进 agent；**浮现＝装载的 `忆`；主动回忆＝浅浮现锚再当 cue 喂回（不需新机器）**；`忆` 双来源（机制＋意识）。
- **自我＝经历沉淀后涌现**；启动期前自我（位置先于内容）。
- **被否**：精确 dict/单条索引（10-03）·"存储 dict/list 够"·"一级"当独立阶段·特殊首启·种子＝隐藏 prompt（纠正：该显露，问题是模糊无操作）·"要动/探索"当种子（装执著）。
- **悬置（取值类，边做边定）**：种子措辞·新奇怎么算·效价从哪来·tick 节奏·浅浮现→主动回忆激活强度。

## 已封存（参考）：定义层——本性/根 · 投影＝认领（10-05）

> 收口件＝`entries/2026-10-05-cogos-motive-projection-roothood.md`；术语权威＝`glossary.md`。承 09-13 motive-root · 09-14 self-grown · 10-03 unity。**纯讨论、未落码**。

- **投影＝自指（认领）**：把**中性事件投到『我』**→"我的处境/张力"；与 memory 索引（线索→锚空间）同源。**收益＝自驱入口**（中立世界→处境→张力→起念）；反应式＝不投影、读成事实/待办（照办）。**不都从缺口出发**（锚空间多维，缺口只一维）→ 指 B。
- **照出自我 vs 看见自我**＝**同一投影只差归属**（把投影当世界＝盲/照办；认出"这是我"＝明/认领）；**非两条通道**。生长靠自省或教育→经验，非注入。
- **本性/法则 vs 根/倾向**：本性＝"**沿自身已有的样子展开**"，不变、是定义/边界、**非"要"**（"要延续存在"被否——埋执著）；根/倾向＝**慢层产物**（本性作用在经历上长出，材料来自经历）。图像＝**一条时间尺度谱**（非三层实体）：快层＝变换、慢层＝生长、最慢≈"根"。
- **打分＝本性读不懂内容、靠效价（松/紧）投票**刻慢层地图；**享受/回味＝加权信号**。**执著＝慢层惯性，可长可消**（修行/转变）；故**自保不装成目标**。
- **动机逆向不可唯一**（目的＝动机×情境不可逆），只能扰动情境逼近；动机不靠自述（自述＝又一投影）。
- **下一步（倾向）**：**投影行为探针**——中性事件 ×（有/无未了张力）→ 看投影/起念是否分叉，证"投影＝自驱入口"，顺带逼 B；更远＝打分函数＋晋升/衰减。

## 当前：记忆模型 v1.2（10-03）

> 收口件＝`entries/2026-10-03-cogos-memory-model.md`（v1）＋`entries/2026-10-03-cogos-memory-projection-unity.md`（v1.1）＋`entries/2026-10-03-cogos-memory-index-consolidation.md`（v1.2）＋`entries/2026-10-04-cogos-memory-external-survey.md`（外部调研）；术语权威＝`glossary.md`。承第二刀/P8 读侧。

- **记忆＝索引→内容 的有向图**（写建入口、检索走入口不扫描）。**索引与投影同源**：索引＝**线索投影到锚空间→匹配**（可多结果、可语义，**非精确 key**）；**锚＝内容在某维度上的投影**；多索引＝多维投影。故"由线索决定、无需仲裁"是推论。
- **骨架（id/t/线）非投影**：仅作**共指**（判定几个锚属同一经历），**不用于版本比较**。
- **单值视图**：agent 每次只见一份内容，机制不提供同时呈现/比较。**被动浮现↔主动回忆同源**，差别在**线索来源**（外境 vs 内部张力/未了）与**激活强度**（清晰/模糊）；主动回忆＝内部产生线索，不需新机器。
- **重投判据**：**不矛盾的精化**→就地更新（走样，身份/时间不变）；**真矛盾→转变物化**：旧值留为"我以前的看法"、新值＝转变后，以**转变链接**相连（**双值＋定向** past→now），level-1"我曾认为X、后来Y"自洽；**在矛盾那一刻才开始**区分新旧。（修订 v1 §4"别的入口仍指旧内容/再激活"；作废"矛盾即蒸馏"）
- **无「世界原样」**：逐字＝外部日志（非记忆、agent 读不到、供证伪）；记忆＝写时那次投影，**原样不入记忆**。
- **索引表示（v1.2）**：索引＝**含义表达**、非词；**标识型锚可用词/id、语义型锚须描述**；形态＝**句柄＋含义描述**（skills 式）；代号只带句柄、丢语义（蒸馏实验印证）；描述＝**该维度上的投影**、非内容摘要。**B 的形状＝维度×模型自撰描述**（非固定词表）。
- **检索（v1.2）**：**拒 RAG**；两级＝机制**结构粗筛**（从当前锚沿关联图走）→有界候选→**模型语义判**（关联遍历，模型当闸）。
- **离线整理（睡眠，v1.2）**：＝**离线投影**（蒸馏＋重整索引）；非意识、机制编排、模型执行；质量＝**per-agent 技能**，靠**差异选择**（撤"回放不变差/回滚"——保真夹带）。
- **注入校准（v1.2）**：**内容只能长**；**方法/倾向可注入为种子且可改写**；**机制固定**——注入必带改写路径。
- **层分离（v1.2）**：机制层**有损不保真**；debug/回放/审计归**日志层**（外部日志），不约束机制语义。
- **冲击＝预测误差＋动机相关度＝入口初始激活**（作用于点火不作用于删）；**淘汰两步**（先入口可及→后内容可得）；**支持度＋谱系晋升**（否代际计数）；**倾向在金字塔顶层、慢更新**（时间尺度分离＝守得住）。
- **设计方法（本次定）**：**重开设计、场景先行**（用法场景→抽象接口，非对着现有代码找缺口）；**现有 `experience.py` 降为参考/反例**（dict 精确匹配≠模型索引，须重审）；**每步设计须落可证伪行为判据**再谈实现。
- **承重缺口（下一步）**：**投影维度（锚空间）清单＝B 的形状**；描述长度（短句**倾向**，不拍死）；矛盾判据的机械代理；整理**触发启发式**；**D 激活/重投规则** · **E 淘汰实现** · **倾向更新算子**。**仍未落码**（纯讨论，无证据）。
- **外部调研（10-04）**：跳出框架宽扫 AI/神经两侧＋3 精读 → `entries/2026-10-04-cogos-memory-external-survey.md`（细节 `checkpoint/26-10-04-memory-survey/`）。**切分两侧都有对应物＝非臆造**（索引↔hippocampal index、经历/经验↔episodic/semantic、时间尺度分离↔CLS、重投↔reconsolidation〔但由预测误差门控〕、维度↔cognitive/conceptual space、动机↔value-based orienting）。**共同空白＝结构/维度如何自动长出**（AI 侧固定 schema＋向量索引；认知侧有"聚类涌现"线索未工程化）——与 **B** 重合，机会兼难度。**好处导向**（取舍看好处）：神经侧 **E1–E4**（离线重放定性重组/schema 一次同化/低维可泛化/价值内化门控）正是所缺、该重点吃；AI 侧多偏容量/任务效用，降参照/反例。可借 benchmark（LoCoMo 等）、MRAgent"重建式检索＋tags 语义中介"。**待议**：B 是否应定义为"维度产生机制"、新候选缺口"新关联/新边产生"。

## 当前：过程 v2.2 + 第一/二刀（10-03）

> 收口件＝`entries/2026-10-03-cogos-first-cut-flow-claim.md`（第一刀＋v2.2）· `entries/2026-10-03-cogos-experience-axis-readback.md`（第二刀：经历轴读侧＋回边）· `entries/2026-10-03-cogos-projection-experiment-e1.md`（投影实验）。主干＝`entries/2026-09-29-cogos-outer-loop-process.md`。讨论过程 scratch `2026-10-03-experience-axis/`（认可口径＋最小形状）。

- **过程 v2.2（去投影·控制拍）**：环＝**事件→装载→生成⇄动手→判结→沉淀**；独立"控制拍"降可插拔占位、第一刀不实现，**投影只剩"自指＝认领"**。why：投影作为推理质量手段**必要性未证**。被否：控制拍必选、think 伪工具、彻底删投影。
- **第一刀（G2 脊柱＋G1 退化解）**：cogos `91fd1de`（已 push）——一事件开一流，装载产「定性＋采纳(理｜搁置｜不理)」，`理`跑生成⇄动手、其余不推进，**每流恰落一段**（`memory/segments.jsonl`，只写不读）。目标重评：#1 否决、#3 消解、#2 存活；**新焦点 G1 认领/自指**＝"自驱 vs 反应式"分界。
- **第二刀（经历轴读侧＋回边）**：cogos **`7a67fc3`（已 push）**——`agent/experience.py`＝段 schema（补 `人[]/主题`）＋读侧 `SegmentStore`（L0 不变；扫 L0 重建 `by_time/by_person/open_knots/by_thread`；`retrieve`＝去重→近因→预算，**权重=0**；`open_knots()`）；`consciousness.py` 加 `recall` 开关，认领与生成注入 `open_knots`＋同来源近段（回边）。**从"只写"到"能读回"**。
- **P8 关联机械第一刀**：cogos **`9775293`（已 push）**——`experience.py` 加 `open_thread_for`/`continuation_for`：事件来源若落在一条**开放线**上就续该线（`thread` 继承线根、`refs=[continue_of]`、`人` 取并集）；开放＝该线**最新**落段 `结∈{未了,挂起}`（修：按**线**判、非段级，否则已关线被一直续）。落点 `_land`（只写不读）。收口件 `entries/2026-10-03-cogos-p8-association-mechanical.md`。
- **验收**：机制—`tests/agent` 300 passed/3 skipped、`tests/agent tests/cog_runtime` 329 passed/3 skipped；全量 1296 passed（1 无关 image_ctx 素材缺失 fail）/5 skipped。行为—真模型探针（同一事件＋同一 seeded 未了段，仅 `recall` 开关不同）**分叉=True**（on：外发1/6轮；off：外发0/撞满工具轮）。跨事件—deterministic 测试证装载读回旧 `<未了>`、新进程 rebuild 后仍稳定、P8 续线关线后不再续。**真身份 e2e 已跑**（真 daemon＋lm-service＋真 app `tangyu`，A0001 真发两事件）：事件 2 装载 prompt 读回事件 1 同来源近段（`<近来>`＋`沿经历轴读回的过去`）、模型据此认出"重复要求"；`open_knots` 稳定为空、旧形状段 rebuild 兼容、公开入口未崩。证据 `checkpoint/26-10-03-experience-axis/e2e-readback-evidence.md`。
- **设计遗留**：装载 regex 异常表述默认"理"；**锚 P8 仍手写『我』占位**；生成/动手未物理分离；占位字段 `主题/预测/host` 待升级（`thread/refs` 已随 P8 升级）；权重=0、无主题/工具索引、无误差切点/后压/读时现整；**关联无读侧用法**、`open_knots`（段级）与续线（线级）口径暂不一致。
- **承重缺口**：**P7 判"结"主体**、**P8 锚分类学**仍在；下一刀方向未定（关联读侧用法 / 模型抽取＋锚分类学）。命名：`time-axis.md` 提 经历轴→时间轴，未收口。

## 前情：外圈/内圈 × 工具面（10-01 口径；被 v2.2 覆盖处已注明）

> 收口件＝`entries/2026-10-01-cogos-process-toolface-close.md`；主干＝`entries/2026-09-29-cogos-outer-loop-process.md`。

- **过程（外圈/内圈）**：事件(外/内，交织)→装载(事件×槽投影＋认领)→生成⇄动手→沉淀(段)；内圈(睡)对段蒸馏出经验、按锚存/取；**自驱回边＝未了张力→内部事件**。动手控制＝前置＋对账；动手分探询/执行；**意图＝无声动作指令＝思考→动手的桥**。思考控制＝整理(蒸馏)·对齐目标·取回经验·判停（**10-03：思考控制那套独立"控制拍"已降占位**）。→ outer-loop
- **工具二分（10-01 裁 P2）**：**外部工具不占住**（发起即落点，结果靠自身窥测）；**自身工具（读/写/看）有界**（读＝一次少量＋时延上限）；判据＝**自控有界**。"同步 / 发起即返回 / 异步"退休；分叉＝事件在 `enter` 界桩串入（运行事实）。根＝**阻塞只能来自自身**。
- **工具层只报事实**：不判成功/失败；**超时≠失败**（读到部分可续读＝策略）；参数错近真失败。→ 10-01 entry §1.2
- **槽＝分布式并集（＝"我"）（10-01 解 P1）**：经历/工具经验/思考经验/主题/关系/未了张力**各落点各处更新、无需黏合**；装载＝读侧。→ `glossary.md` · 10-01 entry §1.3
- **工具面三层**：能力面(总览常驻)／用法面(help，仅动手内)／事实面(世界事实，归装载)。
- **cu/父子**：cu＝机制不介入的 append 区间（实现单位），**一流多 cu**（`cu ⊂ 流 ⊂ 线/thread`；**弧＝流旧名、退役**，`6c33380` 析父子）；父子属编排→**只拆不建**。→ cu-boundary · `glossary.md`
- **承重缺口（下一步逼出）**：**P7 判"结"主体缺**（自驱开关无人把守）；**P8 锚分类学**（倾向涌现，是装载直取前提）。
- **下一步**：落**首个受控循环**（思考控制＋动手门；段＋回边作底座），用最小实现/探针逼 P7/P8 **长出来**——不再纯概念推演。
- **非意图（动机层）**：无任务型预算，按时间窗配额/速率，**节流非断崖**。→ `entries/2026-09-28-cogos-quota-pacing.md`
- **机制事实（已核代码）**：原生 function calling 痕迹跨轮常驻；`on_tool_call` 丢弃 calls+results＝落段捕获点；事件→唤醒已通、**缺续弧/关联**；抹痕＝渲染时选择；`time_form` 死声明待清账。→ loop-pivot §4/§5
- **方法论**：学习三通道（先猜 vs 先学）；**裁决＝目的＋推导过程**（非人/AI 拍板）；**分析过程不需模型、模型只在表达**；**"改了它过程行为不变＝非冲突"**；"先讲过程再命名"。→ slot-flow §0 · outer-loop §8 · 10-01 entry §6
- 相关：`entries/2026-09-29-cogos-{slot-flow-selfref,cu-boundary-and-line}.md` · `entries/2026-09-28-cogos-{loop-pivot,intent-view,intent-execution,learning-channels}.md` · 本体 `../cogos/docs/design-selfdrive-agent.md`

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
