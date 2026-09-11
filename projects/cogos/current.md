# cogos

多 agent 运行时，飞书作通信总线。通信层已收口，智能系统设计已收敛。底层三件：lm-service + cog-runtime 已完成，第三件「认知图」设计探索已封存为预研（09-01），4K 聊天机器人 MVP 暂停。

## 通信（已收口）

后续通信用 `cogos/phone`，用法见 `docs/phone-usage.md` / `docs/comm-full-design.md`。细节不再记，用时看文档。

## 设计已收敛（08/24–08/26）

讨论收敛为概念体系 + 开发计划，固化到本体 docs：

- 概念体系：`docs/cogos-concept-system.md`
- 开发计划：`docs/cogos-plan.md`
- 理论摘要：`docs/cogos-design-theory-summary.md`
- 上网工具：`docs/webtool-design.md`（阶段二，工具子系统）

## agent-study 复习（08-26 晚 ~ 08-27，已收尾）

31 条已确认结论全过，保留项挂接进 cogos 模块，固化 `docs/agent-study-hooks.md`。关键新决策：元控制二分（资源级=机制层预装不可自长 / 认知级=策略层自长方法论）。两个设计缺口已归入 plan：过程元控制→阶段三整系统（认知级元认知）、诊断观察→每阶段都有诊断出口，完整事件流随阶段三。过程归档 `checkpoint/archive/26-08-27-agent-study-review/`。

## 当前：底层三件实施（08-29 起）

- 任务1（工位 B）：lm-service 实施 ✅ 完成（08-30）
- 任务3（工位 B）：lm-service 遗留三项 ✅ 完成（08-30）
- 任务2（工位 A）：cog-runtime 设计 ✅ 收敛（归档 `checkpoint/archive/26-08-30-cog-runtime-impl/design-cog-runtime-min.md`）
- 任务4（工位 A）：cog-runtime 实施 ✅ 完成（08-30）

lm-service 最小版（`docs/design-lm-service-min.md`）已实现并验证：mock 51 passed + 全量 pytest 719 passed 无回归 + 真实验证全绿（deepseek 文本/401/视觉 judge）。关键决策（YZ 拍板）：tier 改名 basic/advanced（视觉模型归 basic）；thinking 默认关闭（cogos 内部不用厂商 thinking，仅留参数对比）。冻结契约：LmClient.chat → 归一响应 + LmServiceError(category)。过程归档 `checkpoint/archive/26-08-30-lm-service-impl/`。

task-3 遗留三项（① LmClient 不暴露 base_url，走环境变量 ② tool call 内部化 ③ content 归一 content[]）完成：`chat` 加 `tools` 入参、响应加 `tool_calls` 出参（`[{id, name, args}]`）、content 变 list；mock 65 + 全量 733 passed 无回归 + deepseek 真实验证 tool call 全绿（同构 openai、arguments 真实 parse、strict 忽略不补）。契约形状不变，仅扩展字段。过程 `checkpoint/archive/26-08-30-lm-service-fixes/`。

task-4（cog-runtime 实施，工位 A）完成：类型 + CogUnit + CogRuntime/_advance 状态机 + 支路 A/B 闭环 + 并发 + 父子通知 + shutdown，测试 32 passed。真实测试暴露 lm-service 缺续轮消息归一→厂商转换，工位 A 直改补齐（`providers/base.py` `assemble_tool_messages`）；全量 777 passed 无回归 + 真实 deepseek 三路全绿（A 文本 / B 工具续轮 / E 401→auth）。遗留：告知值默认注入先不做。过程 `checkpoint/archive/26-08-30-cog-runtime-impl/`。

## CogUnit thinking 模式（09-02）

CogUnit 加 `thinking` 透传（dict，默认 None=厂商 disabled）+ 工具续轮回传 `reasoning` + `CuResultOk.reasoning` + `assemble_tool_messages` 转 `reasoning_content`，目的对比。真实验证：DeepSeek **不校验** reasoning_content 回传（漏传/截断均 200，flash/pro 一致），回传是质量导向非硬约束，官方「不传 400」是威慑性描述。遗留：plain assistant 的 reasoning 未映射（跨 cu 多轮才需要，暂不改）。细节 `entries/2026-09-02-cogos-cogunit-thinking.md`。

## 认知图设计探索 → 封存（08-30 晚 ~ 09-01 凌晨）

第三件从「认知树」转向「认知图」的设计探索（checkpoint-1~13），最终封存为预研，聊天机器人 MVP 暂停。关键结论：图必要性在上下文局限而非「抽象需要记忆」；图非预先设计、从 cu 痛点长出；MVP 记忆用文件组织（profile replace + events append）、预算外包取舍自学。归档 `checkpoint/archive/26-09-01-cog-graph-sealed/`，状态 ISSUES「封存/暂停」。

## agent 认知架构 + 实施（09-01 ~ 09-02，讨论收敛 + 概念澄清）

编程助手场景，从「记忆系统」转向「LLM 自管理上下文」。核心：cu 覆盖式回合、状态对象（context/intent/problem/gain）、意识=脉络（放下意识层/元层术语，改功能命名）、心智时间留元层不进对象层、来源标注分工、scratch 脚注引用与 cu 化展开、目录 ID 化、元层内省推/拉、张力驱动主题调度、模型分级。设计原文归档 `checkpoint/26-09-02-agent-cog-arch/`，凝练版 `entries/2026-09-02-cogos-agent-cog-arch.md`。

实施已推进 6 期（意识层第一期 + 工具层 read/write/edit/execute/search/fetch + scratch 草稿纸），read 已改行模式（offset/limit+行号），全量回归 856 passed 已推 master；当前 consciousness 仍是 oneshot 不续轮。代码认知 `entries/2026-09-02-cogos-agent-codebase.md`。

## terminal + timer 实施 + agent 接 cu 讨论（09-03）

terminal + timer 已实施（`../cogos/docs/design-terminal-timer.md` 落地）：terminal.py（busy/idle + buffer/cursor + killpg 中止 + terminal_done 事件）、timer.py（绝对时间戳 + 单调度循环 + timers.json 恢复 + timer_fired 事件）、events.py（AgentEvent/render_event）、app.py（事件队列 + consumer + stop）、tools.py 提取 drain_stream。全量 883 passed 无回归。

e2e（真实 deepseek）：exec 非阻塞验证通过（deliver 长命令 0.66s 未卡 4s）；但 LLM 只调 terminal_open 就停——暴露 agent 层 oneshot 无续轮，open 结果不回传。

→ 引出 agent 接 cu 讨论（收敛）→ 已实施（09-03 晚，见下）。

## agent 接 cu 实施（09-03，完成）

oneshot 改 cu 多轮续轮：Consciousness 持 context + `asyncio.Lock`，`on_message` append user → `runtime.cu(tier="basic")` → `await cu.wait()`；`on_tool_call` 计数超限 interrupt + 调 registry；`on_done` 补 assistant + 兜底 send_msg（非 system 且未 send_msg）。runtime 加 `client` 注入 + `on_tool_call` 异常保护（原会悬挂）。全量 886 passed 无回归。真实 deepseek e2e：`sleep 3 && echo` 6.73s 走通 open→exec→observe→send_msg 完整闭环，terminal_done 事件回传成第二轮 user 消息。细节 `entries/2026-09-03-cogos-agent-cu-wired.md`。

## 视觉方案收敛（09-03）

视觉子系统方案讨论+实测收敛，目标=人眼看东西（全景背景 + 局部看清细节），省 token + 看清楚。否定预生成金字塔与放大，取图 = 原图 + range(crop 原生，凑近=缩 range) + scale(draft 降采样档，非放大倍数)。全细节不降采样，串行 + 能力探测超限即返回错误态由 LLM 第一人称转述，不降级。视觉子系统独立进程。实测：draft 70ms/22MB、crop 原生 285ms/67MB；**token 封顶 443（≥1000×750 不变）**，封顶原因=厂商内部 resize 到封顶尺寸切 patch，crop 局部=提高有效分辨率（印证永不放大）。已更新本体 `vision-system-design.md` §4/§6/§14。细节 `entries/2026-09-03-cogos-vision-scheme.md`。

img-tool 并发控制已收敛（09-03 四轮）：短命子进程 + flock 计数信号量（N slot 抢任意空闲 + jitter 防惊群），N 可配置、N=1 退化互斥；控制落在 img-tool 自身，不放上层（多进程管不住）。细节 entry 末尾「并发控制」节 + 本体 §14。

→ 分叉已化解（09-03 续）：视觉既非工具也非子系统，是 cog-func（img-tool 原语 + look_at 种子功能 + 生长功能）。见下节。

## cog-func 范式讨论（09-03 续）

从"视觉看似收敛但仍有疑虑"出发，换角度从三件套（LLM/cog-unit/cog-func）审视，发现缺 cog-func。讨论从"cog-func 是什么"一路推到范式层，三层结论：

- **具体**：视觉非子系统 = img-tool 原语 + look_at 种子功能 + 生长功能；cog-func 分层 = 原语层（预枚举封闭）+ 功能层（组合开放，种子+生长）。
- **成长**：经验绑定 cog-func（程序性记忆，调用即生效）不进认知树（陈述性记忆）；成长 = raw trace 攒批 → 量变总结 → 保底滚动替换；记录规则自长（只给保守种子）。
- **范式**：函数封装"过程"→ cog-func 封装"理解"；正确性从精确过程→契约+约束+反馈；复用代码→复用理解；开发者从园丁→可调度协作资源+研究者。主线：主体性从"固定的我"→"流动的调度权"（人与机制等价）。
- **命名（YZ 拍板）**：cog-actor（谁）/ cog-func（什么能力）/ cog-unit（什么动作）三层；agent = 对外的 cog-actor 实例，总结模块 = 内部 cog-actor；本质层 actor、呈现层 agent，主体性 = actor 在呈现层的投影。

细节 `entries/2026-09-03-cogos-cogfunc-paradigm.md`。

## img-tool 实现（09-03 续，四层第一步落地）

img-tool 原语已实现（`../cogos/cogos/img_tool/` core/cli/stub + tests/img_tool 29 测试），全量 915 passed 无回归（基线 886），四项验收全过。关键：flock 计数信号量抢槽、能力探测（MemAvailable×0.6 每次读）、extract 写 `--out` 文件、stub tempfile 建/读/清。代码认知在 `/home/zhengyp/work/A/checkpoint/codebase.md`（已加 img_tool 段）。跑测试需 python3.11。

→ **下一步**：实现 cog-func（look_at）= 看图契约 prompt + 缓存句柄 + 复用主 cu 循环，接 img-tool 两个原语。交接 `checkpoint/26-09-03-imgtool-impl/handoff.md`。

## 聚焦-扫描 / foveation 预研（09-03 起，视觉方案之后的机制探索）

视觉"工具 vs 子系统"分叉化解（cog-func）后，进一步探索"模型到底怎么看"的机制层。主线几轮（principle-exp 目录，非 cogos 仓库本体）：

- 机制已收敛到**镜筒** `look(center, radius, focal)`（中心=注视/扫描、半径=视野可退可近、焦距=清晰度档）。网格/贴边/IoU/降采样档/判别锚决策层**全部作废**（是"把规划外包给程序 + 只用单方向凑近"产生的多余层）。
- 关键立场：**模型管"怎么看"（规划），我们只管"能看多清"（哑原语）**；不写状态机/策略循环。之前"模型自报不可靠"是"没镜筒只能单遍看"的后果，非能力缺陷；重构为"注视=检验"（看的结果=内生反馈），落 cogos 功能成长。
- 坚持每轮修正：网格≠隔离、蒸发≠挑错、凑近≠放大像素；**判据锚=目标可辨性，非像素档**（降采样划档方法论不成立）。
- 当前正做**镜筒快速验证**（首次把"看"自主权交给模型，判据=能否自主走到 A）。

最新交接：`/home/zhengyp/work/A/checkpoint/principle-exp/handoff-focus-scan-foveation-7.md`（第 8 轮：落地单一视野三层 + 图对象统一 + open 路径化 + view 参数化，整合一次性/REPL）。前置：`handoff-focus-scan-foveation-{2,3,4,5,6}.md`（6/7 轮逐步收敛 view 两参 + 全景常驻 + 轨迹累积）、`handoff-focus-scan.md` / `-foveation.md`、`result-downsample-tiers.md`。

第 7 轮（handoff-6）：极简对话式，tool 收敛 view 两参，全景常驻 + 轨迹累积，一次运行一步 view。第 8 轮（handoff-7）：YZ 把"单一视野/驻留/对照"谈成可实现模型并落地——视野三层(驻留≤2/全景/中央凹 view 参数轨迹)、图对象统一(路径+属性, view 参数化不存图)、open 只 open 原图(用户给绝对路径, 同路径去重, 拒 view 产物目录)、view 产物图入 views/ 不作可 open 原图、模型可循环 view + json 剥离只存纯文字、P2 改 JPEG 降 base64 字节。后端 server 需新会话重启。”

## 聚焦-扫描落地推进（09-06 ~ 09-07 本会话，principle-exp，`/tmp/kilo/vision/vf6.py`）

镜筒从跑通到可对话式使用。核心：**定位=对话式观察**（人主导、agent 负责看说，不做自动化/收口）；**中性提示词**（只声明工具能做什么，不教策略，修正"全景唯一坐标基准"矛盾→默认坐标上下文）；本会话关键 = **image 坐标系**：`view{"image","center","radius"}`（坐标相对指定图、缺省=当前全景、可超[0,1]、出界停边界），**换算收归工具** `State.map_to_pano`，修掉模型手算子图→原图坐标的误差（手算偏(0.63,0.58)，工具算(0.593,0.515)≈GT A）。真实对话 2-3 步命中双矩形（≈GT A）。行为分化：空区"重复/微挪/收尾"各 1/3（偶发，根因=缺收口动作，与"过度收敛"同源，不无限重复）。机制层候选（同坐标重复 view≥N 次注入轻提示）与收口动作**观察阶段先不落**。细节 `entries/2026-09-07-cogos-vision-find.md`。

## 读图精度：思考/注意力/模型/像素（09-07 晚，principle-exp 对照）

`vf6.py` 读体温单 p062 做一组对照（无思考/有思考/提示词/不同模型/不同像素）测"读准靠什么"，收敛：**模型视觉能力 > 思考**（网页版强模型无思考近可用，deepseek 无思考乱读/打转——属谱系偏差，别当通则）；**思考=非单调增益器**（纠模糊也用错、会为自洽编造且不自知，提升幅度与模型强弱成反比）；**提示词**能逼诚实/不脑补，但不加推理深度、不补像素；**单次前向不可全信**，任何模型单点会错、需交叉验证兜底。deepseek thinking 无预算（思考链吃满 max_tokens→content 截断，`finish_reason=length` 可检测；"加大 token"是反方向）。vf6 已改造（删驻留、fovea 按源图分组、open 恢复上下文组图、修 P2 body 超限、`--no-thinking` 开关）。细节 `entries/2026-09-07-cogos-vision-thinking-attention.md`。**已交接新会话**：`checkpoint/principle-exp/handoff-read-precision-context.md`（含 vf6 上下文串行不分区→复读 bug、待办：上下文分区/动作状态区 + finish_reason 处理 + 交叉验证）。

## GUI 点击坐标 + 矩形/十字标记 + 上下文管理（09-08 早）

用 Xftp 截图 windows.png(1357×764) 测「agent 点击坐标精度」+ 给视觉工具加原语 + 深挖上下文管理。三次坐实「单次前向不可信」：工具(T) 真值≈[0.188,0.042]；模型给过 [0.188] 也 [0.55](错~490px)；thinking 反而把整图误读成"渐变背景"退回去猜(思考=非单调不可靠)；复读/parroting 连发 4 次相同 view+相同理由。

- 工具原语(**已落地+接入 vf6**)：矩形视野 fovea + 中心十字(aim marker) `Viewer.view_box(center,size,step,shape,mark,mark_pt)`（size 相对短边、归一化[0,1]、只缩不放）；SYSTEM/map_to_pano/exec_action/save_trail 均已接。矩形对表格/UI 净收益(rect 框整行、circle 读不了)。原型 `vf_box_proto.py`。交接 `checkpoint/principle-exp/handoff-vf6-rect-marker-context.md`。
- 上下文管理重设计(**定案未实现**)：图在上下文**出现一次**、LIVE 张常驻带图(全景1+最新视图1)、旧观察**降级文字**、contexts 只作动作轨迹+重看兜底。模型"知道图变了"靠 ① 当前新鲜图 ②文字状态 ③ 增量+十字(注视=检验)。复读根因=模型自己长文回喂 + 每轮同批静态图无增量 + 无收敛信号；根在上下文组织+反馈信号，非模型能力。
- 遗留：落地上下文重设计(A/B 测工具(T) 复读/命中)；交叉验证+不确定出口并入；finish_reason=length。细节 `entries/2026-09-08-cogos-vision-rect-marker-context.md`。

## 对话式图工具 + 点击『工具(T)』取证（09-09 晚，principle-exp，`/tmp/kilo/vision/image_field_chat.py`）

落地 handoff-12 遗留（schema 接入并暴露给模型）：`image_field_chat.py` 用 `figure_tool_schemas()` 把 `see/mark/adjust_mark/unmark` 暴露给模型（结构化 tool_calls），K=4 图上下文(`FigContextManager`)、raw.jsonl 持久化、`--resume` 重放、每次十字落 `crosses.jsonl`。真实模型点击『工具(T)』：命中样本(<10px)+非命中样本(test_2 偏右 78px)并存。**根因=模型子图目测偏 ~11%子图宽(77px)+未换算+标完未自证**（非基准乱：ref=全图与值自洽，但值从子图目测未经换算且估读本身偏）。关键修复：多 tool_calls 时 tool 必须连续(中间不可插观察图 user，否则 invalid_request)、重放协议安全重排、打印不截断。**本会话未上评审**，停点=模型视觉自证收口，正确性靠自证+事后 crosses.jsonl 评分。交接 `checkpoint/principle-exp/handoff-vision-image-fields-13.md`。

## coord 求解原图坐标 + ANNO 寿命=FIG（09-10，principle-exp）

把图工具用途讲透并落码：`see`=看清、`mark`/`adjust_mark`=点出并校准候选、`coord`=**把候选换回原图坐标值**（纯读）。关键：**坐标值必须工具给**——mark 存的是 `@窗口` 相对坐标，模型要的是 `@原图`，换算（`win_c−win_s/2+u×win_s`）工具做、模型不算（此前模型自己手算既多余又是错误来源）。新增 `coord(fig_ref, anno_id)`（返回原图路径+形状+cross→[x,y]/rect→[cx,cy,w,h] 归一化+像素）+ `anno_to_src` 单点换算（coord 与评分共用）；schema **契约自明**承载方法（see→mark→adjust→coord）。

**ANNO 寿命 = FIG**（YZ 拍板）：去掉"摘超龄图块即清 annos"（`clear_fig_block` 废除），anno 随 `View` 在 registry 存续；重载 `(path,window)` 带回 anno。文档同步 + **工具命名统一**（旧设计名 `load/view/draw/move/delete_anno` → 代码名 `see/mark/adjust_mark/unmark`）。

e2e 两轮均命中：coord_1 px(250.3,28.9)、coord_2 px(251.1,33.1) vs 真值 (255,32)；**隔离验证**（删 SYSTEM 一切 coord 提示）仍走对 → schema 契约自足、不依赖 SYSTEM。提交 `1b5153c`/`4555050`/`f12d1f0`。细节 `entries/2026-09-10-cogos-coord-anno-lifetime.md`，交接 `handoff-vision-image-fields-15.md`。

## 域 / 图(FIG) / 场设计 + 引用规范（09-08，下午轮定稿，待实现）

「图如何落到上下文」定稿：**FIG ≜ (path, view)**，全图=窗口覆盖整体、主/子图边界对模型不存在；引用=tagged token `FIG:`/`PATH:`/`(FIG,ANNO)`，模型只抄不造、系统解引用（**PATH 为必需输入通道**，人让"打开某路径图"；FIG 兜住任意图含无路径子视图）。**源/域**：Source(图根)=域与图之间的身份层（单源+其 FIG 注册表 `window→FIG_ID`，去重/枚举挂靠点；`FIG=(path,window)` 纯函数：同 path 幂等（同 Source+同 src_fig）/同窗口同 FIG_ID）；域=图资源容器。**无场**（废弃观察场/比较场，YZ 拍板）：图的组织=**图块散落历史、活 K 轮**（默认4、可配），超龄仅摘图块、文字永续；`earliest_fig_turn` 单指针比较即可清；K 改大不回生、改小立即生效；**compile 只编当前轮**、历史固定只删超龄图块；**load 打开进历史（只开一张）**；**无 load_many**（单轮至多 1 图块：load/view 各产一新 FIG 图块，draw/move/delete 改所属 FIG 标注并重渲染产其最新图块（同 FIG_ID、模型可见变化）；K 轮窗口总量≈K 张，容量由 K 完全控制）。坐标系=**三套化**（动作`@窗口`相对参考FIG窗口/地图`@全图`信息性/像素内部+尺寸；模型只在`@窗口`动作不做换算，看全图=load/view全图⇒`@窗口`≡`@全图`），**越界 clamp=只取有效区**（方案1：clamp 到边界、不补边/平移，标注「原坐标→实际生效坐标（含实际窗口）」）。**像素一致性（已定）**：下发=**render 出的窗口位图**（img-tool extract 语义 crop+本机按封顶 max_dim 主动降采样），**非原图**；请求 **`detail=original`** 禁厂商二次 resize（防坐标偏/元注解 w×h 失真）；**元注解 w×h=实际下发位图**。承接 vision-system-design.md §14「精确给」+ 官方 detail=original。上下文=**文字永续(重载锚)+图块K轮寿命**（砍降级文字），**文字必须自含**（工具调用痕迹可能被抹→重载锚/窗口/坐标必须写进文字）；**compile 无去重**（模型可反复看图，图管理层不干预、不提示；去重仅身份层）。图说明=**元注解**(`meta_annotation` 从管理数据渲染)+模型批注(`compose_figure_text` 拼；note 瞬态、不进图/存储/desc)，批注回显用**你的备注:**(第二人称)；元信息**短+固定序+分隔符统一、不做视觉对齐**（机制=低可预测/短token，非视觉显著性；A/B 可测）。**ANNO 图内作用域定稿**：draw 创建(初始定位)→move/adjust(改位置+尺寸)→delete_anno；生命周期=所属 FIG 的图块在 K 轮窗口内(超龄失效清空、重载不带回)；move 移出所属 FIG 边界→clamp 到边界+markdown 高亮(`> ⚠️ **…**`)、不报错；不入 desc。**parent 已删**：FIG 纯函数下无需 `View.parent`（YZ 拍板），各 FIG 只靠 path 归属自己的 Source。接口：`load`/`view`/`draw`/`move`/`delete_anno`（无 load_many）。本体 `cogos/docs/design-vision-image-fields.md`（已含全部结论），细节 `entries/2026-09-08-cogos-vision-image-fields.md`。

### 09-08 晚：坐标改三套化 + 建验收清单（设计定稿协调一致，尚未实现）
- **最大变更=坐标体系**从「相对全图全局系」重做→**三套化**（动作`@窗口`/地图`@全图`/像素内部+尺寸），§5/§9-3 重写；其余设计不变。
- **新建验收清单**：`cogos/docs/design-vision-image-fields-checklist.md`（分 P1~P4，行为 MUST HAVE + 禁区 MUST NOT，回指设计 §条款 + 可验证手段；自检=功能完整/是否偏离设计，禁区最易被顺手改回）。
- 交接 `checkpoint/principle-exp/handoff-vision-image-fields-4.md`：设计定稿协调一致、未实现；下一步落 `cogos/image_ctx` 原始层（P1 add_src/load/view/render，用 windows.png 验证）。
- **P1 实现规格 + 两项拍板（同晚续）**：规格 `cogos/docs/design-vision-image-fields-p1-spec.md`（坐标换算`@窗口`→`@全图`/越界clamp/render指纹`(path,window,annos)`/add_src·load·view·render 签名输出形状；只写规格未落码。subagent 检视过，修掉指纹对 list[list]/clamp退化0宽两个高危）。YZ 拍板：① `load` 产新 FIG=全图普通 FIG、按 `(path,全图窗)` 去重首次建再次复用；② `@窗口` size 基准=**方案 A**（center+size 均分轴 over 参考框、`1,1`=整盒、不取短边倍数，单基准）。
- **P1 落码完成（09-08 晚）**：`cogos/image_ctx/{view,domain,render,tools}.py` 落地 + `tests/image_ctx`（18 test 全过），P1 checklist 逐条勾（detail=original 按 §7-3 归 P2+），全量 pytest 955 过、无禁区 API。windows.png 探针（1357×764）：`@窗口≡@全图` center 精确、全图主动降到 800×450、越界只取有效区不补边。细节 `entries/2026-09-08-cogos-image-ctx-boundary.md`。
- **职责边界定案（YZ，勿越界）**：`image_ctx` **只管图对象状态**，**不管上下文/K 轮/compile**（earliest_fig_turn/图块散落/K 轮/薄状态行/摘超龄图块全归**上下文管理器**）；`image_ctx` 只暴露 `load/view/draw/move/delete_anno`(产 Block)、`fig_meta(fig_id)`、`clear_fig_block(fig_id)`（上下文管理器摘图块时调用，触发清 annos）。设计 §10 原把 `window.py`/`compile.py` 塞进 image_ctx 的建议**作废**，归上下文管理器。
- **P2 定位层落码完成（09-08 续，小原型先行）**：先 `anno_proto.py` 验证 anno 像素叠加正确性（程序断言+视觉双确认，十字压中 windows.png「工具(T)」无问题）；随后 render 改自绘 annos、新原语 `draw/move/delete_anno/clear_annos`+越界 clamp+markdown 高亮+`clear_fig_block/fig_meta`。测试 `tests/image_ctx/test_p2.py`（12 项）+ 全量 pytest **967 passed**，P2 checklist 全勾。细节 `entries/2026-09-08-cogos-image-ctx-boundary.md`。**已交接** `checkpoint/principle-exp/handoff-vision-image-fields-6.md`（P1+P2 落码 + 职责边界定案，下一步 P3 上下文编译层归上下文管理器）。
- **P3 上下文 + P4 去重落码（09-08 深夜，handoff-7）**：`cogos/cog_ctx/`（`FigContext`=compile/strip 纯原语、`FigContextManager`=step/k/live deque 老化 `next/advance`）+ `tests/cog_ctx`；P4 Source 去重 `test_p4.py`。全量 pytest **992 passed**。
- **坐标基准统一 + P3 目的层探针（09-08 深夜收口，handoff-8）**：① 坐标 size 分母从短边改**各自维度（宽对宽、高对高）**，全图窗口 `s(1.000,1.000)`、`@窗口≡@全图` 逐位一致（旧÷短边横向图宽稀释 56%）；② P3 探针双过：`taskA.py`（纯文字锚重建窗口）+ `taskB.py`（真实老化→图超龄被摘→纯锚无规则重定位）回放 delta 全 0——锚**自含**；③ §138 换算精度 `probe138.py` 过（亚像素 0.56px、目标覆盖）。checklist 回勾 §0 行为 6 项 + 禁区 3 项 + §138/§139。**下一步=衍生推理档**（用锚做新相对窗口，检验坐标教学必要性），待 YZ 开题。

## 转向自驱回路（09-11）

从视觉/机制细节回到主线：造**能自驱推进**的 cogos agent（人不在场时自己思考推进，人在场一起裁决）。定为 L1→L4 自主度阶梯，入口 = dogfood（agent 维护 cogos 自身）；不押实现 L4，押"把回路建起来、逐阶抬升"。

- **行业评估**：定位已商品化（ScreenSpot-Pro ~88%、OSWorld-Verified 86%、人类基线 72%），未解在长程（OSWorld 2.0 20.6%），归因 planning+memory；验证是活跃区（VeriGUI/VSA/reward model），差异化在 harness 层。→ 视觉不追加投入，力气放回路。
- **保命收编**：`/tmp/kilo` → `cogos/research/`（push `c3ad76f`）；旧活文档 87 文件归档 → `checkpoint/26-09-11-live-checkpoint/`（push `ace9c95`）；`../checkpoint` 清空重启（编号不续）。
- **S0 状态面**：回路缺三格——机器可读议程 / 自触发 / agent 内自验证（L1→L2 门槛）；执行层齐，视觉库未接入 consciousness，记忆缺跨会话持久。
- **S2 首跑完成（09-11）**：靶子=给 `AccountRef.ensure` 本地缺失→云端兜底补测（最小可验，不取候选 1）。壳 `cogos/agent/loop.py`（薄壳+一个洞：壳跑判据、模型不自证）在 `cogos-s2` 分支跑出 **verdict=done**（agent 真加了 `TestEnsureCloudFallback`，全量绿）。报告 `../checkpoint/s2-report.md`：产出 7 条"人在哪被需要" + 3 个真实缺陷（① 全量 pytest 的 `test_workdir_switch` 未隔离，会改真实 `~/.cogos/feishu` 配置并停 daemon；② phone 连接失败会清 `is_default` 持久化→静默失联；③ 壳 notify 失败被吞）。
- **代码已提交（未 push）**：分支 `s2-selfdrive-loop`（`91ff8dc` 壳 + `c74f47e` 测试增量），spec 随分支入库。
- **停点**：`../checkpoint/status.md`（新会话入口）+ `plan.md` + `state.md` + `checkpoint-2.md`。S2 暴露的 3 缺陷已在 S3 前置修复（见下）。
- 细节：entries/2026-09-11-cogos-selfdrive-pivot.md

### S3 触发完成（09-11 续）

前置三修复（S2 缺陷）已实施：`test_workdir_switch` 加 `COGOS_SERVICE_TESTS` 默认跳过；phone 失败不再清 `is_default` + `init_phone` 补默认卡；`_notify` 重试 + 本地 outbox + 标 `notify_failed`。**S3 触发**改为"壳自动选条（`pick_next`，跳 done/needs_human/high-risk），无候选走 `no_work`"（spec `cogos/docs/design-selfdrive-loop-s3.md`）。真机三次跑同一项 `create_group-clear-error`（先放红测试）：① 验收空转也 done（教训）；② `model_asked`，查出 **work_dir 未透传给模型工具**（已修 `Agent(work_dir=)`+loop 透传）；③ 自动把 `create_group` 改用 `_client_for`，红转绿、done。全量 1018 passed；分支 `s2-selfdrive-loop` 已 push。新发现待讨论：**验收空转**（验收太弱→不改代码也 done）、`send_msg` 问/报不分。报告 `../checkpoint/s3-report.md`。细节 `entries/2026-09-11-cogos-s3-trigger.md`。

→ **task-5（工位 B，已交接）**：回路省时两件——验收遇错即止 + phase 计时，`tasks/task-5-loop-verify-timing.md`；B 在 `work/B/cogos-s2`（s2 分支 worktree，A 已建好）开工。讨论中明确的其余时间项（分层验收、红→绿证据、候选项）留工位 A。
→ **task-5 复核通过（09-11，A）**：验收遇错即止 + phase 计时落地，全量 1021 passed；B 未 commit，等 A 收尾。**task-5 的"计时"证明浪费主要在：pytest 每轮全量（~60s）+ 3 条慢测试**（lark 首次 import ~13–18s、monitor 两处漏 mock 各 5s）。
→ **task-6（工位 B，已交接）**：测试套件提速——消除 lark 首次 import（mock `_build_handler`）+ 补 monitor 两处 sleep mock，A 实测约 28s 纯浪费；`tasks/task-6-pytest-speedup.md`；B 在 `work/B/cogos-s2` 同一 worktree 叠加开工（不 commit）。
→ **task-7（工位 B，已交接，Kilo harness 支线）**：Kilo 常驻 + 事件唤醒 + 飞书/窗口双通道 spike。关键事实：Kilo 有 `@kilocode/sdk` server/client（`createKiloServer`/`session.prompt`）、插件 `event` 钩子收全部总线事件（含 `session.idle`/`pty.exited`）、`PluginInput.client` 可注入、飞书出站已有 MCP（`tool/feishu_server.py`）、入站复用 cogos feishu。B owner（设计+实现同一人），A 仅末端复核。`tasks/task-7-kilo-resident-multichannel.md`。**分工模型调整：探索型任务一个 owner 设计+实现，避免 A 想一遍 B 再想一遍。**

→ **新遗留：工位隔离缺口**（editable 钉 A + `~/.cogos` 硬编码/服务单例）→ `ISSUES.md` + `entries/2026-09-11-cogos-workstation-isolation.md`；不阻塞 task-5，阻塞"同时真机跑/常驻"。

→ **本轮讨论（自驱语义 + 时间分配）**：`../checkpoint/checkpoint-2.md`（自驱 = 议程更新函数 f / ΔA、三源外移 & S0–S4 意义、分水岭=议程空时能否自生；时间按信息增量分配、等待=阻塞问题、通知保人低频）。

→ **回主线建议（09-11 晚）**：效率线收尾后回归 S4，建议第一阶 = **判据源→agent 最小 demo**，拿**红→绿**当硬门（同时治 S3 验收空转）。形态：只有标题的 issue → agent 先写会失败的红测试（停）→ 壳确认初始红 → 实现 → 红转绿 → 人只复核判据合理性；验收=①自产判据②判据合理。最小机制=验收分两相（判据相要求初始红/实现相红转绿）+ 初始非红→needs_human。先别做 L3/常驻/大重构。分工适合 A（B 忙 task-6/7）。待 YZ 开题/选靶。细节 `../checkpoint/checkpoint-3.md`。**分工模型调整**：探索型任务一个 owner 设计+实现同一人，另一工位末端复核，避免重复思考。

## 锚点

- 约定 / 关键文件 / 设计决策: README.md
- 阶段记录: CHANGELOG.md
- 遗留问题: ISSUES.md · 方向: ROADMAP.md
- 认知地图: entries/project-map.md
- 任务清单: tasks/
- agent-study 挂接: docs/agent-study-hooks.md
