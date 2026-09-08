# CHANGELOG

> 只记阶段级里程碑（成果 + 时间 + 锚点）。每日变更流水、commit、测试数在 git log 与 entries/ 里。

## 阶段 1 · 通信层基建（08-07 ~ 08-14）

从零搭起飞书通信底座：环境/设备/账号、WS/Session、收发卡片、命令机制、provider 搭建与 setup 真机调通。

- 初始提交 + 环境管理 + secrets 类型系统（bot/human）+ core.Lib
- WS/Session 设计 + 卡片消息 + FileLock + history 落地
- 命令机制（`@msg_command`）+ provider 编排（OAuth → scope → Bitable 7 表 → 注册）
- 卡片驱动 provider setup 真机调通 + Phase C 联调修复

→ 细节：entries/（08-12 ~ 08-14 系列，含 setup / comm-testing / bugfix）
→ 设计：docs/comm-full-design.md

## 阶段 2 · agent 接入 + 群聊（08-15 ~ 08-21）

agent 长连接与账号体系落地，打通群聊：agent-term、账号失效/刷新、Telecom 接口抽象、群操作、bot 间 p2p。

- agent-term 长连接（鉴权/心跳）+ 账号失效/刷新 + resume cloud-first
- Telecom 接口抽象 + 真机通信接口实现
- 群操作（me_join 唯一路径）+ bot 间 p2p（双 bot 群 + @all）+ 群聊收发/命令/区分

→ 细节：entries/（08-15 ~ 08-21 系列）
→ 设计：docs/agent-account-refresh-design.md + docs/agent-term-design.md

## 阶段 3 · phone 收口（08-22 ~ 08-24）

Phone 抽象落地（agent 侧 API），真机验证全绿，通信层收口。

- Phone 四件（model/store/fake/phone）+ 接真机 + TUI 交互终端
- 真机验证全绿（668 passed）+ get_members 30s 自阻塞根治

→ 细节：entries/2026-08-22-cogos-phone-stage-a-done.md + checkpoint/archive/26-08-24/
→ 用法：docs/phone-usage.md

## 阶段 4 · 智能系统设计（08-24 ~ 08-26）

智能系统方向收敛为概念体系 + 开发计划，进入实施。无代码变更。

- 概念体系 → docs/cogos-concept-system.md
- 开发计划 → docs/cogos-plan.md（底层三件 → 子系统 → 整系统）
- 理论摘要 → docs/cogos-design-theory-summary.md
- agent-study 已确认结论复习 → 挂接点固化 docs/agent-study-hooks.md；元控制二分（资源级/认知级）；缺口进 ISSUES

→ 过程：checkpoint/archive/26-08-26/ + checkpoint/archive/26-08-27-agent-study-review/

## 阶段 5 · 底层三件设计收敛 + 进入并行实施（08-27 ~ 08-29）

lm-service 最小版设计收敛为 v1，cog-runtime 雏形已出，进入「工位 B 实施 lm-service / 工位 A 讨论 cog-runtime」并行。

- lm-service 设计 → docs/design-lm-service-min.md（LmClient 冻结契约 / category 六类 / 三文件分离 / router 模态>tier / 调试记录）
- cog-runtime 雏形 → 活文档 design-cog-runtime.md（继续讨论）
- 任务清单 → tasks/（task-1 lm-service 工位 B + task-2 cog-runtime 工位 A）

→ 过程：checkpoint/archive/26-08-29-impl-design/

## 阶段 6 · lm-service 实施完成（08-29 ~ 08-30）

task-1（工位 B）完成：lm-service 最小版全链路跑通，mock + 真实验证全绿。

- 包骨架 + yaml 三文件（config/secrets/state）+ admin CLI + router + handler + scheduler 主链路 + providers 归一 + 调试 jsonl + LmClient + lm_call CLI
- tier 改名 basic/advanced（视觉模型归 basic，YZ 拍板）
- thinking 默认关闭（cogos 内部不用厂商 thinking，仅保留参数对比，YZ 拍板）
- mock 51 passed + 全量 pytest 719 passed 无回归；真实验证全绿（deepseek 文本/401/视觉 judge）

→ 过程：checkpoint/archive/26-08-30-lm-service-impl/
→ 任务：tasks/task-1-lm-service.md

## 阶段 7 · lm-service 遗留三项完成（08-30）

task-3（工位 B）完成：lm-service 三项遗留补齐 + tool call 内部化真实验证全绿。

- ① `LmClient` 删 base_url 参数（internal_key 自带地址，走环境变量/默认，上层只持句柄）
- ② tool call 内部化：`chat` 加 `tools` 入参（组装厂商格式）+ 响应 `tool_calls` 归一 `[{id, name, args}]` + 调试记录落盘
- ③ 输出 content 归一 `content[]`（消息数组，对称输入 material）
- mock 65 passed + 全量 733 passed 无回归；deepseek 真实验证 tool call 全绿（同构 openai、arguments 真实 parse、strict 忽略不补）

→ 过程：checkpoint/archive/26-08-30-lm-service-fixes/
→ 任务：tasks/task-3-lm-service-fixes.md

## 阶段 8 · cog-runtime 实施完成（08-30）

task-2（工位 A 设计收敛）+ task-4（工位 A 实施）完成：cog-runtime 最小版闭环。

- CogRuntime/CogUnit/_advance 状态机 + 支路 A/B 闭环 + 并发 + 父子通知 + shutdown
- 真实测试暴露 lm-service 缺续轮消息归一→厂商转换，工位 A 直改补齐（assemble_tool_messages）
- 测试 32 passed（cog_runtime）+ 全量 777 passed 无回归 + 真实 deepseek 三路全绿

→ 过程：checkpoint/archive/26-08-30-cog-runtime-impl/
→ 任务：tasks/task-2-cog-runtime.md + tasks/task-4-cog-runtime-impl.md

## 阶段 9 · 认知图设计探索 + 封存（08-30 晚 ~ 09-01 凌晨）

底层第三件从「认知树」转向「认知图」的设计探索，最终封存为预研、聊天机器人 MVP 暂停。无代码变更。

- checkpoint-1~6：认知树结构/表达/环境同一性收敛
- checkpoint-7：认知树→认知图转向（节点+类型化关系，路 A 单一原语多视图）
- checkpoint-8~11：初态与好奇 / replace 纠错+场景+时间 / 接口方法论+四通道+情绪 / 图无决策
- checkpoint-12：必要性质疑（上下文窗口本身就是记忆，图必要性在上下文局限）
- checkpoint-13：图封存，转向 4K 聊天机器人 MVP（记忆文件组织 / 软预算+冗余 / 预算外包取舍自学）→ 暂停

→ 归档：checkpoint/archive/26-09-01-cog-graph-sealed/（封存，后续再看）
→ 状态：ISSUES「封存/暂停」

## 阶段 10 · CogUnit thinking 模式 + DeepSeek 行为验证（09-02）

CogUnit 支持 think 模式（对比用），真实验证 DeepSeek thinking 回传行为。

- `thinking` 参数透传（dict，默认 None=disabled）+ 工具续轮回传 reasoning + `CuResultOk.reasoning` + `assemble_tool_messages` 转 `reasoning_content`
- 真实验证：DeepSeek 不校验 reasoning_content 回传（漏传/截断均 200，flash/pro 一致）；回传是质量导向非硬约束，官方「不传 400」是威慑性描述
- 全量 862 passed 无回归；测试 +6（thinking 透传/默认、续轮 reasoning 回传、result 带 reasoning、转换层 2 例）

→ 细节：entries/2026-09-02-cogos-cogunit-thinking.md

## 阶段 11 · terminal + timer 工具实施（09-03）

模拟 kilo code「agent 被工具阻塞」，落地非阻塞工具 + 事件回执通路。

- terminal.py（busy/idle + buffer/cursor + killpg 中止 + terminal_done 事件）+ timer.py（绝对时间戳 + 单调度循环 + timers.json 恢复 + timer_fired 事件）+ events.py（AgentEvent/render_event）+ app.py（事件队列 + consumer + stop）+ tools.py 提取 drain_stream
- 全量 883 passed 无回归
- e2e（真实 deepseek）：exec 非阻塞验证通过（deliver 长命令 0.66s 未卡 4s）；但暴露 agent 层 oneshot 无续轮（LLM 只调 terminal_open 就停），引出 agent 接 cu 讨论

→ 设计：docs/design-terminal-timer.md
→ 讨论：entries/2026-09-03-cogos-agent-cu-wiring.md（agent 接 cu 收敛，见阶段 12）

## 阶段 12 · agent 接 cu 实施（09-03）

oneshot 改 cog-runtime cu 多轮续轮，打通 terminal/timer 工具闭环。

- Consciousness 持 context + asyncio.Lock，on_message append user → runtime.cu(tier="basic") → await cu.wait()；on_tool_call 计数超限 interrupt + 调 registry；on_done 补 assistant + 兜底 send_msg（非 system 且未 send_msg）
- runtime 加 client 注入 + on_tool_call 异常保护（原会悬挂）
- 全量 886 passed 无回归（+3 测试）
- 真实 deepseek e2e：sleep 3 && echo 6.73s 走通 open→exec→observe→send_msg 完整闭环，terminal_done 事件回传成第二轮 user 消息

→ 细节：entries/2026-09-03-cogos-agent-cu-wired.md

## 阶段 13 · 视觉图组织/引用规范定稿（09-06 ~ 09-08，principle-exp）

从 vf6 镜筒实测收敛到"图如何落到上下文"的设计定稿（独立于 img_tool，落 cogos `image_ctx`，后续再议融合）。

- 核心跃迁：**FIG ≜ (path, view)**，主图/子图边界对模型不存在（所有图都是"子图"，自足带全局尺寸/窗口）；引用 = tagged token `FIG:`/`PATH:`/`(FIG,ANNO)`（模型只抄不造、系统解引用；PATH 为必需输入通道）。
- 新增 **Source(图根)** 身份层（单源 + 其 FIG 注册表），去重仅身份层（`FIG=(path,window)` 纯函数：同 path 幂等/同窗口同 FIG_ID）；**compile 无去重**（模型可反复看图，图管理层不干预）。
- **ANNO 图内作用域定稿**：draw 创建→move/adjust→delete_anno；生命周期=所属 FIG 在窗口内(淘汰失效)；移出边界 clamp 到边界 + markdown 高亮提示、不报错；不入 desc。
- 图说明 = 元注解(meta_annotation)+模型批注(compose_figure_text，note 瞬态)；批注回显**你的备注:**(第二人称)；元信息**短+固定序+分隔符统一、不做视觉对齐**；**文字必须自含**（工具痕迹可能被抹）。
- 待实现：落后 cogos `image_ctx`（原始层 add_src/load_view_field/view/render 先做，用 windows.png 验证）；元信息 A/B 验证待测。

→ 细节：entries/2026-09-07-cogos-vision-find.md / -vision-thinking-attention.md / 2026-09-08-cogos-vision-rect-marker-context.md / -vision-image-fields.md
→ 本体：cogos/docs/design-vision-image-fields.md
- 修订（09-08 同日续，YZ 拍板）：**取消「场」（观察场/比较场/展示集上限）** → 图的组织=**图块散落历史 + 活 K 轮（默认4、可配，`earliest_fig_turn` 单指针；K 改大不回生/改小即生效；compile 只编当前轮、历史固定只删超龄图块）**；接口 **`load`** 取代 `load_view_field`/`load_compare_field`（**无单轮多张**，原供一次多图的 `load_many` 也删；单轮至多 1 图块：load/view 各产一新 FIG 图块，draw/move/delete 改其所属 FIG 标注并重渲染产出最新图块——同 FIG_ID、模型可见变化）；**删 `View.parent`**（`FIG` 纯函数，各 FIG 只靠 path 归属自己 Source）。本体与 locus 记忆已同步。

## 阶段 14 · image_ctx 原始/定位/上下文/去重（P1~P4）落地 + 探针收口（09-08 晚 ~ 深夜）

从「视觉图组织/引用规范」定稿到 P1~P4 全落码 + LLM/几何探针双收口，图管理工具链完成并与 img-tool 衔接。

- **P1 原始层**：`cogos/image_ctx/{view,domain,render,tools}.py` + `tests/image_ctx/test_p1.py`（坐标换算/clamp/render 指纹/元注解）；全量 955 passed。
- **P2 定位层**：anno 像素叠加小原型先行（程序+视觉双确认），render 自绘 annos + 原语 `draw/move/delete_anno/clear_annos` + `clear_fig_block/fig_meta`；全量 967 passed。
- **职责边界定案（YZ）**：`image_ctx` 只管图对象状态，K 轮/compile/摘图块全归上下文管理器；设计 §10 原 window.py/compile.py 塞进 image_ctx 作废。
- **P3 上下文**：`cogos/cog_ctx/`（`FigContext` compile/strip 纯原语 + `FigContextManager` step/k/live deque `next/advance` 老化）+ `tests/cog_ctx`。
- **P4 去重**：Source 身份层（同 path 幂等/同窗口同 FIG_ID/跨 path 不合并）+ `test_p4.py`；全量 **992 passed**。
- **坐标基准统一**：size 分母从短边改**各自维度（宽对宽、高对高）**，全图窗口 `s(1.000,1.000)`、`@窗口≡@全图` 逐位一致（旧÷短边在横向图宽稀释 56%）。
- **探针收口**：P3 目的层 `taskA`（纯锚重建）/`taskB`（真实老化→图超龄被摘→纯锚无规则重定位）双过 delta 0；§138 换算精度 `probe138` 过（亚像素 0.56px、目标覆盖）。checklist 回勾 §0 行为 6 + 禁区 3 + 残留§138/§139。
- **遗留**：坐标规则动态注入暂缓（静态前置）；`desc/` canonical 未落盘；超龄回收（Source.registry/cache 积压）未做；待实测 3 项未测。

→ 细节：entries/2026-09-08-cogos-image-ctx-boundary.md（含 P1/P2/P3/P4 + 坐标统一 + 探针）
→ 设计本体：cogos/docs/design-vision-image-fields.md + -p1-spec.md + -p3-spec.md + -checklist.md
→ 最新交接：checkpoint/principle-exp/handoff-vision-image-fields-8.md（下一步=衍生推理档）
