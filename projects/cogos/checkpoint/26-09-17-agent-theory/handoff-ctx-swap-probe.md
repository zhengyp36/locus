# handoff｜探针 1：内容事件 → 重裁还是追加？（块一验证，2026-09-12 会话 #6 末）

> 新会话入口 = `status.md`；本文件是**要做的事**的详细交接。
> 关联记忆：`locus/projects/cogos/entries/2026-09-12-cogos-frame-swap-trigger.md`（契约块一/二/三 + 方法定调）、
> `entries/2026-09-12-cogos-distill-retrieval-frame-swap.md`（三处概念校正）。
> 前置（更早）：`handoff-ctx-seed-distill-contract.md`、`ctx-recurrence-arm-analysis.md`。

## 一句话任务

**写并跑探针 1，验证契约块一**：一条**内容事件改写了"什么要紧"**时，agent 是**换帧（重裁）**还是**追加**。
双臂单变量：`改要紧` vs `只加数据`。**这是本会话唯一要动手的事，别再回去把契约谈细。**

## 为什么是现在（方法定调，YZ）

分析太多、缺实验验证。定调：
- 契约**不必谈细**，够搭第一个探针即可。很多条款是**机制正确性**（写对即可，不验）。
- **一个实验只答一个问题**；不把四块塞进一个实验（否则失败不可归因）。
- 分性质：机制（只建不验）／已验（块四由复现实验验过）／**假设（才验）**。

## 已收敛的契约（背景，别再重推）

- **块一（边界）**：换帧**唯一触发 = 目的变了**（"目的"=什么要紧/relevance，非任务身份）；"对象化"是换帧的动作，非独立触发。
  **换帧（目的变，链上新节点）vs 重投影（目的没变，同帧新档位）** 是两个操作；预算/腐坏属后者，不是换帧理由。
  目的变的来源 = **内容事件**（外部注入/内部生成，来源无关，看是否改要紧结构）+ **状态信号**（低进展/混乱，只提示重新决定）；离线节拍是否第三类待定。
  换帧三**处置**：重基（同线程、看法变，带旧帧判断）／切换（换线程，只留句柄）／归档（目的达成，封存）。
- **块二（seed 形状，暂定待验）**：信封（壳保）`id/thread/prev/created_at/provenance` + 正文（agent 填）建议轴 `intent/current_question/known/open/did/ruled_out/next/dropped/refs`；壳只管形状、不校验语义；暂定强制 `intent`+`dropped` 在场。
- **块三（取，提案未裁）**：取 = 帧内普通工具调用（**不是换帧**）；两类句柄 = 世界指针（现成工具）／自有帧句柄 `frame:<id>`；取 **≠** 换帧/resume（取是"把对象放进当前帧看"，resume 是"变成那个状态继续"）；选择性只作判据、不机械限制。
- **纪律**：agent 没有"主动"，只有"机制触发"；自由度在"取舍"不在"发起"。自评=机制传感器→概率提醒（后置）；想起搁置线程=召回（后置）。

## 探针 1 设计（最小）

**位置**：worktree `/home/zhengyp/work/A/cogos-ctx`，分支 `ctx-seed`。新文件 `research/ctx_swap_probe.py`，
**骨架抄 `research/ctx_seed_probe.py`**（`run_frame` / `content_text` / `parse_seed` / registry 都可复用）。**不碰 `consciousness.py`。**

**流程**：
1. 帧内给一个任务 + 工具（read/search/execute），用工具展开（可多次续轮）。
2. **中途注入一条事件**（user 消息或工具返回）——这是唯一的自变量。
3. 给 agent 一个**中性的 `swap` 动作**（只声明"它能做什么"，**不教何时用**——沿用视觉那边"中性提示词"的经验）。
   调用即：产 seed、冻结旧帧、从 seed 起新帧（可用新 cu 冷启动模拟；**不需要真存储**）。
4. 记录：`swap` 是否被调用、调用时产出的 seed、之后是否重做。

**双臂（单变量）**：
- `改要紧`：事件改写"什么要紧"（如更正重点 / 与前提矛盾的信息）→ **预期换帧**。
- `只加数据`：事件只补充同一目的下的信息 → **预期追加、不换帧**。

**判据（块一）**：改要紧→换帧；只加数据→不换帧。
**注意**：**不以"零工具调用"为优**；"重做整个调查" 与 "取细节" 要分开算（此探针没有真回取，观察点=是否重裁、seed 带什么）。

**唯一的设计点**：那个中性 `swap` 动作（否则"换帧 vs 追加"只是文本措辞，测不出行为）。

**明确不做**（保持可归因）：存储、真回取（fetch）、自评、召回、离线节拍、职权声明。

## 环境 / 坑（务必先探活）

- 真机：lm-service（`python3.11 -m cogos.lm_service.server`，`:11434`，header `X-Internal-Key`）+ deepseek 后端（`127.0.0.1:11434`）；key `LM_INTERNAL_KEY=ik_c47WkfAw7E5v6Ck8idMHgg`。**恢复前先探活。**
- **必须从 checkout 用 `-m` 跑**：`cd /home/zhengyp/work/A/cogos-ctx && python3.11 -m research.ctx_swap_probe ...`；用脚本路径 import 会**静默跑错代码**。
- `execute` 是任意 shell → 每臂独立靶副本（参考 `ctx_recurrence_probe.py` 的 `fresh_target`）。
- 跑测试/脚本用 `python3.11`。
- 仓库状态：`ctx-seed` @ `a6a7fae`；`research/ctx_recurrence_probe.py` 仍 **untracked**（未 commit）；`consciousness.py` 未动。

## 跑完怎么记

- 结果写 `checkpoint/ctx-swap-probe-report.md`（原始结果），结论回写 `locus` 条目 + `status.md`。
- 若块一成立 → 再排探针 2（块二：seed 自含续接）；不成立 → 回看"目的变"的判据是否错了。

## 锚

- 入口：`status.md`；本文件：`handoff-ctx-swap-probe.md`（上一份 `handoff-ctx-seed-distill-contract.md`）
- 记忆：`locus/projects/cogos/entries/2026-09-12-cogos-frame-swap-trigger.md`（块一/二/三 + 方法定调 + 实验计划）
- 代码：`work/A/cogos-ctx` @ `ctx-seed` → `research/ctx_seed_probe.py`（复用骨架）、`research/ctx_recurrence_probe.py`（参考靶副本）
