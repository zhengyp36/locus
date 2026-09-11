# task-5 — 自驱回路：验收遇错即止 + phase 计时

> 状态：待执行。工位 B 执行。自包含，干净会话读本文件 + 代码锚点即可开工，无需工位 A 讨论上下文。
> 背景：S3 真机跑一条回路 ≈ 2.5–3 min，其中每轮全量 pytest ~67s、模型一轮 ~90s。本任务只做两件**低耦合、已明确**的改动，为后续"按信息增量分配时间"提供数据与省时。

## 目标

1. **验收遇错即止**：`run_acceptance` 顺序执行验收步骤，第一个非零退出即停，不再跑后面的昂贵步骤（失败轮次不再白跑全量套件；通过那一刻才付一次全量）。
2. **phase 计时**：把 setup / model / acceptance / notify 的墙钟耗时写入 `runs.jsonl`，作为"时间花在哪"的事实基线。

两件都不改现有字段的形状（只加字段 / 改内部执行顺序），不引入新组件。

## 前置

- 本体：`work/B/cogos`（clone 自 `git@github.com:zhengyp36/cogos-dev.git`）
- 记忆：`work/B/locus`
- 本文件：`locus/projects/cogos/tasks/task-5-loop-verify-timing.md`
- **代码起点（已由工位 A 备好）**：目标代码在分支 `s2-selfdrive-loop`（origin `9eb76cf`）。工位 A 已在 `work/B/cogos-s2` 建好 worktree（与工位 A 同构），**直接在该目录开工**。已核验：`python3.11 -m pytest tests/agent/test_loop.py` → 10 passed，且 import 到的是 B 自己的 `cogos/agent/loop.py`。**不动 `work/B/cogos` 的 master**。
  - 若 worktree 丢失，重建：`cd work/B/cogos && git fetch origin && git worktree add ../cogos-s2 s2-selfdrive-loop`
- **环境坑（历史）**：`pip show cogos` 的 editable 指向工位 A `/home/zhengyp/work/A/cogos`。跑测试必须 `cd work/B/cogos-s2` + `python3.11 -m pytest`（cwd 进 sys.path），否则 import 到 A 的旧代码。

## 唯一改动面（文件归属冻结）

- 只改：`cogos/agent/loop.py`、`tests/agent/test_loop.py`。
- 不改：`agenda.yaml` schema、`run_item` 的既有字段与语义、其它模块、其它 loop 行为。
- **所有权冻结**：工位 A 在本任务期间不碰这两个文件。实施中若发现需改本文件以外的形状 / 需新增字段 → **停下，飞书通知 YZ，回工位 A**。

## 契约钉死（先读后写）

### ① 验收遇错即止

现 `run_acceptance`（`loop.py:102-130`）把每个 step 都跑完再取 `all(exit==0)`。改为**顺序执行、遇非零即停**，并钉死返回形状：

| 字段 | 语义 |
|---|---|
| `exit_codes` | **长度恒 = `len(steps)`，按 index 对齐**；未被执行的 step 记 `null` |
| `ran_steps` | 新增 int：实际执行的 step 数 |
| `passed` | `bool(steps) and ran_steps == len(steps) and all(c == 0 for c in exit_codes)` |
| `output` | 只拼接已执行 step 的 chunk；提前停止时末尾追加一行 `[short-circuit: steps after {i} not run]` |
| `has_steps` | 不变 |

- `_digest` 机制不变（仍 hash `output`）；失败轮 output 变短 → digest 随之变，属预期，不改 digest。
- 调用方 `run_item` 只读 `passed` / `exit_codes` / `output`，形状不变；`runs.jsonl` 的 `exit_codes` 数组现可能含 `null`。
- **步骤顺序即优先级**：贵的（全量套件）放后面，便宜的（目标测试）放前面，则短路即省时。

### ② phase 计时

用 `time.perf_counter()` 测墙钟，值 `round(x, 2)`（秒，float）。

- **每步 `runs.jsonl` 记录**（`loop.py:347-358` 的 `in_progress` 记录）新增：
  ```json
  "phase_seconds": {"model": <本轮模型耗时>, "acceptance": <本轮验收耗时>, "round": <model+acceptance>}
  ```
- **最终记录**（`loop.py:384-392`）新增：
  ```json
  "phase_seconds": {"setup": s, "model": M, "acceptance": A, "notify": N, "total": T}
  ```
  - `M` / `A` = 各步求和；`N` = 本次运行内 `notify` 调用耗时之和（含重试退避，起点通知 + 终点通知）；`T = s + M + A + N`。
- **setup**：在 `_main_async`（`loop.py:432-433`）`Agent(...)` 之前起 `perf_counter()`，`await agent.init()` 之后停；作为 `setup_seconds=` 传入 `run_item`。
- **签名**：`run_item(..., setup_seconds: float = 0.0)` —— **默认值关键字**，现有测试调用不变。
- `no_work` 路径（`loop.py:424-428`）不要求计时。
- 既有字段（`ts`/`item_id`/`step`/`verdict`/`reason`/`steps`/`notify_failed`/`question` 等）一律不动。

## 轮次清单（每轮：实现 → gate → 记 checkpoint → 通知）

| 轮 | 内容 | 验证 gate |
|---|---|---|
| 1 | ① 遇错即止 + `ran_steps`/`null` 对齐 + 短路尾注 | 新测试：`[false, 写 marker]` → marker 不存在、`exit_codes==[非零, null]`、`ran_steps==1`、`passed False`；全量绿 |
| 2 | ② 每步 `phase_seconds` + 最终 `phase_seconds` + `setup_seconds` 入参 | 新测试：dry 跑一条 → 每步记录含 `model`/`acceptance`/`round`，最终含 5 键且非负；全量绿 |
| 3 | 全量回归 + 文档（如需） | `python3.11 -m pytest -q`：`1018 passed, 1 skipped` 基线 + 新增测试全绿 |

**停下点（轮 3 之后）**：mock/本地测试全绿即停。真机耗时观测需要 lm-service + 真模型，非本任务必需；飞书通知 YZ，等工位 A 复核。

## 工程规范（防走偏）

- 不改 `run_acceptance` 的**返回字段名**、不改 `run_item` 既有字段名；只加字段。
- 计时用 `perf_counter`（单调钟），不用 `time.time()` 测间隔。
- 最小改动：不重构 loop、不动 dry/notify/outbox 逻辑、不动 S3 选条逻辑。
- 新增测试放 `tests/agent/test_loop.py`，沿用现有 `_LoopAgent`/`_FakeRuntime`/`_Registry` 夹具风格。

## checkpoint 工作法

- 每轮结束写 `work/B/checkpoint/`：`status.md` + 本轮 `checkpoint-N.md`（锚点 `文件:行` 优先、凝练可恢复）。
- 结构：当前问题 / 已做修改 / 关键结论 / 遗留坑；每轮 `status.md` 写"下一轮读什么锚点"。
- 轮结束飞书通知 YZ。
