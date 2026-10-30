# CogStream 连续推理流机制（设计＋实现＋持久化＋挂接）

> 状态：已落码并推送。commit `ca597be`（机制，全量 1383 passed＋真 LLM 冒烟）→ `9996d19`（二次检视，1387）→ `456b231`（轮次累积下沉，1389）→ `333ce9f`（持久化，1401）→ `7ed3667`（工具错误分类，1408）→ `e3f50b0`（Consciousness/MetaLayer 挂接，1408）。
> 接口权威＝`scratch/2026-10-27-cogos-cogstream-design.md`（已随收口删除，本 entry 蒸馏其结论）。

一句话：把「连续推理＋介入决策」从 Consciousness 里剥出来，做成 cog_runtime 下纯内存单元 `CogStream`；裸 cu 改名 unit 留 CogRuntime 作引擎；Consciousness 退化为持久化＋生命周期＋元层决策，挂在一个 CogStream 上。

## 动机（why）

现状把持久化＋状态机＋生命周期与「连续推理＋介入」焊在一起、从没跑真 LLM；fall_asleep 的 distill 要用另一个 LLM 任务却只能拿裸 cu 组织流程，介入能力复用不了。→ 抽出通用连续推理流，distill 就是一个新 CogStream（换 context/tier/tools），复用同一套介入机制。

## 机制结论

1. **CogStream（纯内存）**：一份连续 context＋介入点 `tool_done`/`reasoning_done`＋决策 `Action` 四元 Proceed/Relay/Switch/Stop。由 unit 回调驱动、不自写循环。
2. **核心不变量**：advance（调 LLM）合法 ⟺ context 尾 role ∈ {user, tool}。构造尾=tool 也合法（接手中途上下文继续推）。
3. **软中断**＝`unit.interrupt`：不 cancel 在途 leg（LLM/工具未回不回填）、回滚到停点；产出 `UnitResultInterrupted`，stream 翻转 RUNNING→STOPPED。
4. **错误分两类**：同步 raise（构造尾非法/act 状态非法/墓碑 `wait_stopped`）vs 异步 `on_exception(stream, error)`（非法 Action/LLM 失败/未预期异常）。on_exception 不自动重试（策略留上层）。
5. **rounds＝模型调用次数**（跨 unit 连续）：CogUnit 加 `base_round`、runtime 写 assistant 填 `Meta.round`；`tokens`→`last_prompt_tokens`（当前上下文大小，不累积）。
6. **executor 归 runtime**（一个 agent 一个分发器＝`ToolRegistry`）；`.stream(tools=...)` 是 schema 子集，换工具只换 schema 不换 executor。
7. **Sleep 不进 Action**：sleep 是元层生命周期概念，落 stream＝Stop＋另行 distill stream。

## 持久化结论（`333ce9f`）

`store_dir` 可选：有→持久化（append-only jsonl、复用意识上下文的 `type=message/state` 分派），无→纯内存。抽通用 `ContextStore`，birth/FileState 醒睡七态/锚「上一份文件」恢复语义留意识层。meta.json=`{date,next_version}`（惰性日界，建新文件/切 Switch 时取）。七态 builtin（created/restored/continuing/continued/stopped/shutdown/failed）＋ user note（scope=user）。Switch 交叉链接（continuing+next / continued+prev）。restore＝空 context＋有旧文件自动重建，恢复后尾可能=assistant、只能 Relay/Switch 续。

## 挂接结论（`e3f50b0`）

Consciousness 持一个活跃 CogStream 替代 `_cu`/`make_cu`：`_start_cu`→`_start_stream`（`runtime.stream`＋`act(Proceed)`）；两个介入点合并 `_on_intervene`（五元决策翻译成 stream Action，Sleep→StreamStop）。**双持久化分叉拍掉**：意识层要持久化就给 stream 传 `store_dir`（stream store 是唯一落点、不另做意识层独立持久化），不传则纯内存。MetaLayer 注入 runtime、删 tracked_make_cu/_made_cus/StubCu。行为等价（纯替换）：全量 1408 passed 基线不回归＋真 LLM 冒烟跑通。

## 被否 / 未采用

- **先改架子（不碰真 LLM）再接线** → 否（10-27 晚）：架子把持久化＋状态机＋生命周期与连续推理焊死，直接接线 blast radius 太大，改为先实现 cog_stream 通用机制再回头接。
- **外置回调持久化** → 否：上下文变化点全在 stream 内部，外置回调让调用方重复枚举、易漂。
- **整搬 ConsciousnessStore** → 否：抽通用 store（append-only/序列化/archive/日界），birth/醒睡七态/恢复语义留意识层。
- **`wait_stopped()` awaitable** → 否（墓碑方法 `raise NotImplementedError`）：防后人实现会在介入点死锁的 awaitable。
- **`CuResult*`→`UnitResult*` 改名** → 暂缓（低优先级，避免 churn）。

## 下一步

草稿收口（本 entry）→ 通用机制接 LLM（开场＝小的可判定落地验证，非概念设计）。
