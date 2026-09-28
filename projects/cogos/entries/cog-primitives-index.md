# 认知基元索引 · cog-unit / cog-func / cog-object

> 用途：跨文件的**主题锚点索引**（锚点 + 一句话），只做指路，**不含未定论讨论**。
> 本体正式文档在 `../cogos/docs/`；本仓只索引印象与归档。行号为落笔时位置，读时以 grep 为准。

## 正式定义（本体）

- `../cogos/docs/cogos-concept-system.md:19` — 正式术语：CogUnit / CogFunc / CogExecutor。
- `../cogos/docs/cogos-plan.md:28` — CogUnit = 一次语义运算。
- `../cogos/docs/cogos-design-theory-summary.md:25` — CogUnit = 推理请求的惰性描述。
- `../cogos/docs/design-selfdrive-agent.md` — 总纲（不变量 / 术语 / 落地路径）。

## 范式（cog-func）

- `entries/2026-09-03-cogos-cogfunc-paradigm.md` — 范式全文。要点：语义函数（输入=意图 / 输出=结果）、封装"理解"非"过程"（:9,:12）；机制层真隔离 / 语义层视角转换，"一个动词＝一次焦点转换触发"（:13）；原语层（封闭）→ 功能层（cog-func＝原语的命名组合，可生长）（:22-24）；三层命名 cog-actor / cog-func / cog-unit（:50-53）。
- `checkpoint/26-09-11-live-checkpoint/checkpoint-3.md` — 范式深化：cu／cog-func 同构（cu 原子、cog-func 分子）+ 业界定位 + 编程史类比（函数阶段 → 对象）。
- `checkpoint/26-09-11-live-checkpoint/checkpoint-2.md` — look_at 方法论 + cog-func 实现一般法（未完全收敛）。

## 三件定位 / 分层

- `checkpoint/26-09-11-live-checkpoint/impl.md:8` — 四层：lm-service → cog-unit → cog-func → cog-actor。
- `checkpoint/26-09-17-agent-theory/design-cogos-loop-invariants.md:119-177` — cu 实现（环＝机制三段夹一 cu）；**两轴表**：无状态/无模型＝cog-func、有状态/无模型＝cog-object、有模型＝cu（:161-177）；环＝object → func(装载) → cu → func(记录)。
- `checkpoint/26-09-26-theory-residual/design-cogos-loop-invariants.md:116-169` — 同上的归档副本（仍有效：cog-object／cog-func 并列表）。
- `checkpoint/26-09-17-agent-theory/handoff-cogos-loop.md:85` — 三件定位；**沉淀＝眼动的增量形，眼动＝沉淀的批形**。

## cog-unit / cu（设计与定位）

- `checkpoint/archive/26-08-29-impl-design/checkpoint-7.md` — cu 设计讨论：cu 必要性＝边界非代码量；资源级元控制（留 CogExecutor）vs 编排（在 cog-func / 业务）。
- `checkpoint/archive/26-08-29-impl-design/checkpoint-5.md` — cog-unit 调用契约（internal_key / tier，不指定模态）。
- `checkpoint/archive/26-08-29-impl-design/checkpoint-6.md:16` — LLM 输出＝语义/结构化意图，执行全走受控工具 / cog-func，无代码生成。
- `checkpoint/archive/26-08-30-cog-runtime-impl/design-cog-runtime-min.md:11` — runtime 不决策/不编排/不管语义；cog-func 是上层。
- `checkpoint/archive/26-08-30-cog-runtime-impl/checkpoint-1.md:14` — 术语澄清：正式为 CogUnit / CogFunc / CogExecutor；"cu" 系 checkpoint-7 讨论的简写。
- `checkpoint/archive/26-09-01-cog-graph-sealed/handoff.md:65` — cu ＝ 一次「启动→停」的完整闭合循环（执行壳），非一次 forward。

## cog-object / 对象化

- `checkpoint/26-09-11-live-checkpoint/checkpoint-13.md` — 命名层级修正：把"对象"升为与 cog-func 同层的封装范式（cog-object）。
- `checkpoint/26-09-11-live-checkpoint/checkpoint-14.md` — ImageObj 实现定稿：cog-object 方法集（含摘要内嵌修正）。
- `checkpoint/26-09-11-live-checkpoint/checkpoint-15.md` — ImageTool 看/记忆二分 + 意图＝任务（子任务划分）。
- `checkpoint/26-09-11-live-checkpoint/checkpoint-7.md` — 对象化认知 + 生命周期 / 记忆与遗忘（cog-func / cog-actor 落地铺垫）。

## 落地形态（视觉线，含"按需加载"）

- `checkpoint/26-09-11-live-checkpoint/checkpoint-18.md §6/§7` — 工具按需加载 + 痕迹擦除：加载器只 fetch 不翻译；两清理动作（擦除＝调用后即时 / 摘除＝闲置 N 轮，可重载）。
- `checkpoint/26-09-11-live-checkpoint/checkpoint-6.md` — 意图方案：意图＝cog-func 输入；对象（有状态可复用）vs 一次性值；错误诊断走 raw trace 旁路。
- `entries/2026-09-03-cogos-vision-scheme.md:39` — 视觉＝感知侧 io 层，独立 cog-func，不内置 CogUnit。
- `entries/2026-09-13-cogos-motive-root.md:14` — 视觉线可迁移通则摘录（含 cog-func 范式、经验绑定）。

## 相关（旧研究 hook）

- `checkpoint/archive/26-08-27-agent-study-review/hooks-draft.md:7-13` — agent-study 结论挂接 cog-unit / cog-executor 的 hook 草稿。
- `checkpoint/archive/26-08-24/checkpoint-5.md:11` — 架构形态（意识/意图/感知/记忆/LLM server/cog-unit/cog-func）是手段。
