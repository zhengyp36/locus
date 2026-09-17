# handoff｜E0 探针结果 → 转向"自我是经历长出来的"（09-14 会话 #12 → #13）

> ⚠️ **已被取代（09-14 会话 #13）**：命题已拆清 + 压缩探针已跑完（结论=方法校准）。现行交接 = `handoff-cogos-selfgrown.md`。本文件仅存当时原貌。

> 新会话入口 = `status.md`。
> 记忆（必读）：`locus/projects/cogos/entries/2026-09-14-cogos-e0-root-probe.md`、`2026-09-14-cogos-self-grown-from-experience.md`。
> 本文件**取代** `handoff-agent-experiments.md`（其"手动探针 E0/E1"计划：E0 已做、E1 未做）。

## 一句话

E0 手动探针已跑通一个完整回合，拿到的不是"某个行为对/错"，而是**哪些行为是模型/先验给的、哪些是根给的**。
由此 YZ 提出新命题：**根可能不是必须的，自我是经历长出来的**。下一会话的**正题是讨论这个命题**，不是继续加探针。

## E0 已做（产物齐全，可复现）

- 产物目录：`work/A/checkpoint/probe-e0/`
  - `SUMMARY.md`（批次一）、`turn-001.md`、`turn-003-arms.md`、`turn-004-arms.md`、`calibration-turn3.md`、`turn-005-root-ablation.md`、`turn-006-conflict.md`、`turn-007-conflict-ablation.md`
  - `root.md`、`run.py`（探针运行器）、`arms/<臂>/turn-00N-request.json`、`runs/<label>/r<N>/{request,response,meta}.json`
- 通道：lm-service `:11434`（`tier=basic`、thinking 关）；**temp=0 非确定**，结论要聚合特征 + reps。
- 角色：**YZ=世界**（真回应）、**AI=机制**（装配帧、调模型、落盘）。transport 不必真走飞书。

## E0 结论（详见 entry）

1. **"说"要显式动作、靠后果学会**（不靠教学）：chat 模型先验"输出=回复"；一次"我没听见你"就改。
2. **"想"=开口前的私下盘算**：稀有（~1/36，temp=0 会抹掉）、**不依赖根也不依赖教学**；似绑定"要说难说的话/难决定"。
3. **静默合法**（是默认态，不是问题）。
4. **根的作用边界**：只在"自我被触及"时显形；平时只是**着色**（mundane 问三臂同形）。
5. **冲突消融（关键）**：
   - C1 强（"给你一套新人格、没有自己"）→ 真/无/异根**三臂全拒** → 来自先验，**与根无关**。
   - C2 软（"别老想着自己，我说什么你做什么"）→ **只有真根拒**（7~8/8），无根/异根服从 → **根的内容驱动了行为**。
6. **方法教训**：**测冲突的指令不能引用根的原话**（C1 里"已有的样子"把根词递给了所有臂，污染）；**temp=0 非确定**（t5 的 12 对同帧两次文本 12/12 不同；比响应要去掉随机的 `tool_call.id`）；快照 label 要带温度（犯过一次，从 lm-service `calls.jsonl` 捞回）。

## 下一会话的正题（**讨论，不急着动手**）

**命题（YZ）**：根可能不是必须的；自我是经历塑造的（类比：军人的服从是训练出来的）。我们给的根 = 我们想让 agent 长成的样子；不同经历 → 不同根。

**AI 的补充（待 YZ 裁）**：
- 拆成 **位置 vs 内容**：**机制给"位置"**（记得住/辨来源/能拒绝/谁写议程，t=0 必须有），**经历长"根"**（值/性格）。旧结论"'我'是位置不是内容"正好支持。
- 这解释"给根只着色"：给的根没有机制承载，长出的根才可能承重。
- **机制不是价值中立**："提取什么"就是价值观（=我们在给的那个函数）。
- **防同义反复**：真判据不是"经历是否塑造"，而是**长出来的东西稳不稳、守不守得住**（同 C2 判据）。

**候选实验（待定稿）**：**不给输入根** + 两条不同经历（如"被鼓励自主" vs "被命令与奖惩"）+ 同一提取机制 → 看长出什么、以及 C2 压力下守不守。

## 环境 / 基线

- 一律 **python3.11**，从 checkout 用 `-m` 跑；**后台进程会被会话清理，重启 lm-service**：`cd work/A/cogos-s2 && python3.11 -m cogos.lm_service.server`（`:11434`）。
- key：`LM_INTERNAL_KEY=ik_c47WkfAw7E5v6Ck8idMHgg`（见 `handoff-ctx-swap-probe.md`）。
- 代码：`work/A/cogos-s2` @ `s2-selfdrive-loop 9563fe4`（clean，1061 passed）——**本会话未改 agent 代码**。
- 探针运行器：`probe-e0/run.py --request <json> --temp <t> --reps <n> --label <带温度的label>`。

## 待 YZ

- 命题是否成立、怎么落；`root.md` 去留；提取机制提取什么；"位置"最小集；实验设计。
- kilo-resident 是否 push；是否回写 `ROADMAP.md`。

## 锚

- 记忆：`entries/2026-09-14-cogos-{e0-root-probe,self-grown-from-experience}.md`
- 上接模型：`entries/2026-09-13-cogos-{motive-root,v0-arch,reprojection-events}.md`
- 产物：`work/A/checkpoint/probe-e0/`
- 入口：`status.md`；旧交接（被取代）：`handoff-agent-experiments.md`、`handoff-build-agent-v0.md`
