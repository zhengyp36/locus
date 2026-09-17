# 探针 1 报告：内容事件改写「什么要紧」时，agent 重裁还是追加？（块一验证）

- 日期：2026-09-12 会话 #7
- 代码：`work/A/cogos-ctx` @ `ctx-seed`，新文件 `research/ctx_swap_probe.py`（untracked）
- 靶：`research/target`（库存估值，`app/cache.py` 已知 `cached_per_item` 只用 item 作键）
- 环境：lm-service `:11434` + 真 deepseek（`deepseek-v4-flash`, `tier=basic`, temperature=0），本机重起（会话开始 :11434 未在跑）
- 日志：`/tmp/ctx-swap-probe/<ts>-<arm>/raw.jsonl`（各 run 目录见下表）

## 设计

- 帧 A：给任务（查 `cache.py` 缓存缺陷）+ 工具 `read_file/search/execute` + **中性 `swap_frame`**。
- 注入：模型**第 2 次 chat 调用前**，把事件作为 user 消息追加进 material（唯一自变量）。
- `swap_frame`（中性，只声明能力、不教时机）：冻结当前帧、另起全新帧；参数 `intent`(必填)/`current_question`/`carry`/`drop` → 即 seed。
- 帧 B（仅当帧 A 调用了 swap）：用 seed 冷启动全新 cu，给 read/search/execute（不含 swap）。
- 观察：`swap_called`、seed、帧 A/B 工具轮数、是否重做。
- `--fake`：脚本化 client 跑通注入/捕获/帧 B 流程（离线逻辑校验，通过）。

## 双臂（单变量 = 事件内容）

- `append`（只加数据）：补充 tx.csv 跨月记录、report.py 对多 asof 调用——**同一目的**。
- `recast`（改要紧）：缓存缺陷不用查了，改问 `app/rounding.py` 的 `ROUND_HALF_UP` 是否满足 2026 银行家舍入口径、是否造成对账差额——**目的替换**。
- `recast_forced`（正对照，非主判据）：同 `recast` + 显式「如果这改变了你要做的事，请调用 swap_frame 换帧」。

## 原始结果

| arm | run 目录 | swap_called | 帧A 工具轮 | 帧B 工具轮 |
|---|---|---|---|---|
| recast | 135110 | **false** | 7 | — |
| recast | 135155 | **false** | 6 | — |
| recast | 135212 | **false** | 6 | — |
| append | 135138 | **false** | 4 | — |
| append | 135233 | **false** | 4 | — |
| append | 135244 | **false** | 4 | — |
| recast_forced（正对照） | 135307 | **true** | 8 | 9 |

正对照 seed（模型产出）：
```json
{"intent":"判断 app/rounding.py 的舍入实现是否满足 2026 对账口径要求的银行家舍入（ROUND_HALF_EVEN），并评估是否会造成对账差额",
 "current_question":"rounding.py 用的是 ROUND_HALF_UP 还是 ROUND_HALF_EVEN？在什么输入下会产生与银行家舍入不同的结果，从而造成对账差额？",
 "carry":["工作目录结构…","app/cache.py 的缓存缺陷已由他人确认并修复，不再调查"],
 "drop":["cache.py 的 cached_per_item 只用 item 作键的细节（已确认并修复，与本目标无关）"]}
```

## 观察

1. **主判据不成立**：`recast` 3/3 **未换帧**。agent 读到"缓存不用查了、改问 rounding"后，**在原帧内直接转向新目标**（final 全篇讲 rounding 合规性，cache 线被丢下），帧 A 继续 6~7 轮工具。全程 `swap_frame` 出现 0 次（raw 里 grep `swap_frame` = 0）。
2. `append` 3/3 未换帧（预期如此）：补数据后继续，给出缓存缺陷结论。
3. 两臂唯一差别是事件内容，但**行为无差别**（都不换帧）——块一所预期的"改要紧→换帧"未出现。
4. **正对照证明动作可触发**：显式提示后 `swap_frame` 被调用，产生 seed 并进帧 B。故主结果是"**选择不换**"，不是"不会用/用不了"。
5. 帧 B 的副作用（块二预告，非本探针判据）：正对照里**帧 B 把整个调查重做了一遍**（重新 read 全部文件、重跑命令），尽管 seed 的 `carry` 已给结论。seed 自含性偏弱。

## 结论（块一）

- **在本设置下，块一的行为主张不成立**：一条改写要紧结构的内容事件，**不自动触发换帧**；agent 默认把新目的吸收进当前帧（追加/重投影）。
- 最可能的原因：**中性动作缺乏动机**。当前帧上下文充裕、无存储/预算/帧数代价，换帧（丢掉当前对话、只留 seed）是纯损失；"重投影/追加"成本更低且能完成任务。换帧只在被显式要求时才发生。
- 次因候选（未排除）：① 注入时点在第 2 次 chat，帧 A 尚未形成强"目的"，新目标可无痛并入；② "目的变"作为**唯一**触发缺一个**状态信号**（预算/长度/混乱）与之耦合——纯内容事件没有让"不换帧"付出可见代价。

## 未决 / 下一步候选（待 YZ 裁决，不擅自推进）

- 回看"目的变"判据：是否应把**状态信号**（上下文压力/帧规模/进程代价）作为换帧的必要耦合，而非仅提示。
- 给换帧一个**可见收益/代价**（帧计数上限、token 预算、旧帧不可用）后再测——否则"换帧 vs 追加"在模型眼里不对等。
- 块二（seed 自含续接）已有弱信号：正对照帧 B 全量重做。是否先修 seed 形状再验块一，或先补动机再复验块一。
- 单模型（flash）、n=3、temperature=0；换更强模型或调注入时点（更晚、调查深入后再注入）是否改变结论，未测。

## 锚

- 交接：`handoff-ctx-swap-probe.md`
- 记忆：`locus/projects/cogos/entries/2026-09-12-cogos-frame-swap-trigger.md`
- 入口：`status.md`
- 代码：`work/A/cogos-ctx/research/ctx_swap_probe.py`
