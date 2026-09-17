# handoff｜身份即锚：判据重述 + 探针 1 复盘（块一，2026-09-12 会话 #7 末）

> 新会话入口 = `status.md`；本文件是**要做的事 / 待裁的问题**的详细交接。
> 本轮记忆：`locus/projects/cogos/entries/2026-09-12-cogos-identity-anchor-frame.md`（并置讨论的主体）。
> 前置：`entries/2026-09-12-cogos-frame-swap-trigger.md`（块一，**§十 已标冲突**）、`entries/2026-09-12-cogos-distill-retrieval-frame-swap.md`、
> `entries/2026-09-12-cogos-ctx-seed-diagnosis.md`（§七 身份层）、`entries/2026-09-12-cogos-recurrence-arm-analysis.md`。
> 探针 1 报告：`ctx-swap-probe-report.md`；代码 `work/A/cogos-ctx/research/ctx_swap_probe.py`（untracked）。

## 一句话状态

探针 1 跑完（块一主判据**不成立**，且实验设计不可归因）；由此追问把"身份/复现"与"帧/注意力"两条线并置，得出**判据重述：身份优先于目的**。
**下一步不是再跑实验，而是先由 YZ 裁决这次重述**（改块一判据 + 定几个悬置前提），再谈落码/新实验。

## 本轮做了什么

1. **探针 1**（验证块一：内容事件改要紧 → 换帧？）：`research/ctx_swap_probe.py`，双臂 `recast`/`append` + 正对照 `recast_forced`；真 deepseek，n=3。
   - 结果：`recast` 3/3、`append` 3/3 **均未换帧**；`recast` 原帧内直接转向、零 `swap_frame`；正对照 1/1 换帧、帧 B 全量重做。
   - 判读：**不能判块一真假**——实验把"是否换帧"交给 agent 自愿，违背契约自定"无主动"纪律；"帧 B 重做"是块二现象被误当块一证据。**根因：块一"目的变"不可操作。**
2. **并置讨论**（核心，记入新 entry）：身份 = 锚/脊；"丢 vs 模糊"分界=有无身份脊；块二信封其实就是身份层；**块一与身份线冲突**；判据重述为三问。

## 本轮的关键结论（供 YZ 裁决）

- **换帧本体没定义**：契约只在目的层定义，机制层被默认实现"产 seed + 冷启动"占领；它只适配"换对象"，被错用到"同主题换视角"。
- **身份 = 锚/脊**，是三条线（帧/注意力、复现、块二信封）的合流点；"丢 vs 模糊"取决于有无身份脊。
- **块一冲突**：§一"目的≠任务身份" vs 身份线"是不是同一件事决定切不切材料"；任务 1→2 落在相反的一格，**实验支持身份线**。
- **判据重述三问**：①身份是否延续（材料切不切）②视角是否变（是否重裁）③新输入需要旧帧哪层（留下帧/seed/锚）。

## 待 YZ 裁决（优先，未裁不动手）

1. **是否把块一判据从"目的变"改为"身份（延续/切换）为第一判据"**（`frame-swap-trigger.md` §一/§十 需据此重写）。
2. **四个悬置前提**，任一都改变后续：
   - **底片是否常驻**（软预算 vs 硬窗口）——"丢/模糊/锚"结论都挂它；
   - **帧职权**：只陈述/思考 vs 含行动（`ctx-seed-diagnosis.md` §四先决①）；
   - **轨迹归帧还是归链**：归链（身份脊）则帧更轻（先决②）；
   - **召回最小版**形态（身份/`dropped` 形状，不做 embedding）。
3. **块二/块三是否按"身份层"重读**（信封=身份显式锚；取=按锚重新聚焦）。

## 候选下一步（待 YZ 选，不预造）

- A. **重写块一判据**（把身份/主题、视角、需要哪层三问写进契约），再据此**重设探针**（用"换材料 vs 同材料"、以及"只需结论 vs 需过程"分臂——现探针的任务 1→2 属于"同材料换视角"，该 append，测不出边界）。
- B. **先定"底片是否常驻"**（它决定换帧到底丢不丢、锚长什么样），再回头收判据。
- C. **补回取半边**（帧存储 + 自有帧句柄 + 选择性解引用），使"换帧后能否召回"（线 B）可测。
- D. 维持最小：只把本轮结论写入契约与当前 entry，暂不落码。

## 环境 / 坑

- 真机：lm-service（`python3.11 -m cogos.lm_service.server`，`:11434`，header `X-Internal-Key`）+ 真 deepseek；key `LM_INTERNAL_KEY=ik_c47WkfAw7E5v6Ck8idMHgg`。**恢复前先探活**（本轮由我重起，会话结束时可能已随会话停）。
- 探针用 `cd /home/zhengyp/work/A/cogos-ctx && python3.11 -m research.ctx_swap_probe --arm {recast,append,recast_forced} [--fake]`；用脚本路径 import 会**静默跑错代码**。
- `execute` 是任意 shell → 每次 run 独立靶副本（脚本已做 `fresh_target`）。
- 仓库：`ctx-seed` @ `a6a7fae`；`research/ctx_swap_probe.py`、`ctx_recurrence_probe.py` untracked；`consciousness.py` 未动。

## 跑完/定完后怎么记

- 判据若改 → 回写 `entries/2026-09-12-cogos-frame-swap-trigger.md`（重写 §一 / §十）+ `identity-anchor-frame.md` 标注已裁；新实验另起报告。
- 结论回写 `status.md`。

## 锚

- 入口：`status.md`；本文件：`handoff-identity-anchor-frame.md`（上一份 `handoff-ctx-swap-probe.md`，已完成）
- 记忆：`locus/projects/cogos/entries/2026-09-12-cogos-identity-anchor-frame.md`
- 代码：`work/A/cogos-ctx` @ `ctx-seed` → `research/ctx_swap_probe.py`、`research/ctx_seed_probe.py`、`research/ctx_recurrence_probe.py`
