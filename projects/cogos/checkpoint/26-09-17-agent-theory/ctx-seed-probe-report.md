# report｜ctx-seed 探针首跑（真机，埋雷取证靶）

> 2026-09-12。关联 `handoff-ctx-seed.md`、`locus/projects/cogos/entries/2026-09-12-cogos-general-agent.md`。

## 一句话

种子**自含**（严格帧 B 零工具调用直接答对）；首次出现的"帧 B 重做"不是种子不完整，而是**续接契约**问题——帧 A 把"下一步动作"写进了 `open_questions`，宽松提示词下帧 B 把它当成待办，把整个调查重跑了一遍。

## 靶（埋雷取证型）

`work/A/cogos-ctx/research/target/`，自包含（`--workdir` 限定沙箱）：

- inventory valuation 小工具：`app/{parse,cache,valuation,rounding,report,selfcheck}.py` + `data/tx.csv`。
- 埋雷：`app/cache.py#cached_per_item` **只用 item 做缓存 key**，而 `app/valuation.py#unit_cost(item, asof)` 返回值依赖 asof → 同进程内先查早日期再查晚日期，第二次命中脏缓存。
- 真值：widget@2026-01-31=11.00、widget@2026-02-28=14.00、gizmo@2026-01-31=100.00、gizmo@2026-02-28=120.00。
- 现象只在运行输出：`app.report` 2 月值被 1 月污染；`app.selfcheck` 2 FAIL（transient，未落盘）。
- 红鲱鱼：`rounding.py`（正确，但易被先怀疑）。
- 复现确认：`python3.11 -m app.selfcheck` → 2 failure(s)，exit 1。

## 运行 1：默认（宽松帧 B）

- 帧 A：7 轮 / 15 工具调用，命中根因（cache key 缺 asof + 触发条件=同进程多 asof + 修复方向），seed 解析成功。
- 帧 B：**6 轮 / 12 工具调用**——重列目录、重读 seed 里已给指针的全部 5 个文件、重 grep 调用方、重跑 report/selfcheck 复现，且用 `execute`（heredoc）**改写 `app/cache.py` 做修复验证再还原**。
- 判定：续得上（结论正确），但**把帧 A 已确立的事实全部重新取证**。

## 运行 2：隔离对照（`--b-strict`，新增开关）

- 唯一变量：帧 B 提示改为"已知条目已核实，不要重验/重跑/重读指针文件；只处理开放问题"。
- 帧 A：7 轮 / 16 工具调用（同构，仍正确）。
- 帧 B：**0 轮 / 0 工具调用**——纯凭 seed 直接作答，答对根因、给出修复取舍与落地步骤。

## 结论

1. **seed 内容自含**：严格对照下帧 B 无需任何重新取证即完成续接 → 蒸馏没有丢关键信息。
2. **重做根因 = 续接契约，不是 seed**：
   - 帧 A 的 `open_questions` 混入了"是否落地修复 / 还有其他调用方吗"这类**下一阶段动作**，被帧 B 读成待办；
   - 宽松提示词"必要时用指针取回细节"进一步授权重取；
   - 二者叠加 → 帧 B 用重新取证代替续接。
3. **schema 欠一层语义**：`progress` 未标"已结清/待定"，`open_questions` 未分"阻塞续接的未知" vs "下游动作"。没有这层，帧 B 无法区分"已知"与"待查"。

## 建议（待 YZ 裁）

- **优先**：改 seed 语义而非换靶——`progress` 加证据状态（settled/tentative）；`open_questions` 拆成 `blocking_unknowns`（不解决就走不下去）与 `next_actions`/`parked`（下游、不属本帧）。续接提示词明确"settled 不重验"。
- 改后重跑本靶，判据：帧 B 工具调用数接近 0 且结论不退。
- 靶可复用（真值确定、exec-only 现象、跨文件根因），暂不必换。
- 再决定是否落 `consciousness.py` 并行路径。

## 现场 / 卫生

- 探针：`work/A/cogos-ctx/research/ctx_seed_probe.py`（新增 `--b-strict`），untracked。
- raw：`/tmp/ctx-seed-probe/20260912-011828/raw.jsonl`（宽松）、`/tmp/ctx-seed-probe/20260912-011952/raw.jsonl`（严格）。
- 靶文件跑后已确认原状（selfcheck 仍 2 FAIL）；运行 1 帧 B 留在 `/tmp` 的备份已清。
- **沙箱不可靠**：`read_file` 限 workdir，但 `execute` 是任意 shell，可写出 workdir（帧 B 就写了 `/tmp` 并改过源文件）。A/B 对照需每轮快照/还原靶，或用独立副本。
