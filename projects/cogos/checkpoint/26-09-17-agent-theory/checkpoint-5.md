# checkpoint-5｜S4 第一阶落地：判据源外移（红→绿两相）+ 极小靶实跑

> 2026-09-11 晚。承接 `checkpoint-4.md`（自驱最终态 + 源外移判据修正 + S4 起点）。
> 性质：**已落码 + 真机验证**。YZ 选定"造极小靶先验机制"；本会话实现并跑通。

## 一、做了什么

判据源外移的最小机制（S4 第一阶）：议程项只给标题/目标，**判据（红测试）由 agent 写**，壳只跑机制、判红绿。

- **两相**：`requires_criterion: true` 的项走
  1. `baseline`：先跑验收，必须绿（否则 `needs_human / baseline_not_green`，无法区分旧红与新红）；
  2. `criterion`：agent 只写会失败的红测试；验收转红 → 记 `criterion_red`；一直绿/打转 → `invalid_criterion`；
  3. `implement`：agent 实现到绿；红转绿 → `done`。
- **挪内容、留机制**：判据内容归 agent；跑命令/退出码/红绿判定/超时仍在壳。
- **证据**：`runs.jsonl` 每步记 `phase`；最终记 `red_green: {baseline_green, criterion_red, criterion_red_step, implemented_green}`。`done` 必 `criterion_red && implemented_green` → 治 S3 验收空转。
- **无 `requires_criterion` 的项行为不变**（S1 单相）。

## 二、改动面

- `cogos/agent/loop.py`：`task_system(item, phase)`；`run_item` 两相状态机 + baseline 守卫 + `red_green` 证据 + 每步 `phase` 字段。
- `tests/agent/test_loop.py`：+4 测试（红→绿 done / 从不红 invalid / 基线非绿 / 红后不绿 max_steps），沿用 `_Registry` 风格，新增 `_ScriptedRuntime`。
- `docs/design-selfdrive-loop-s4.md`：本阶 spec。

## 三、验证

- 单测：`tests/agent/test_loop.py` 14 passed；`tests/agent` 117 passed。
- 全量：**1022 passed, 1 skipped**（基线 1018 + 新增 4）。注意 `tests/agent/test_terminal.py::test_observe_while_busy` 在**全量负载下偶发**（0.2s 内 `python3 -c` 未及时打印 start），单独/子集跑通过，**与本次改动无关**（task-6 的测试提速区）。
- **真机（极小靶）**：`/home/zhengyp/work/A/checkpoint/s4-target`（`duration.py` 桩 + 一条 smoke 测试），验收 `python3.11 -m pytest -q`，真实 deepseek（lm-service，`LM_INTERNAL_KEY`）。结果 `verdict=done`，`runs.jsonl` 证据链：
  - baseline `passed=true` → step1 `phase=criterion passed=false`（红）→ step2 `phase=implement passed=true`（绿）；
  - `red_green={baseline_green:true, criterion_red:true, criterion_red_step:1, implemented_green:true}`。
  - agent 自写 `tests/test_duration.py`（有效样例 + 11 条 malformed 用例）、实现 `duration.py`（正则 + 单位降序校验）。判据看上去合理（合理性最终由人复核）。

## 三补、收尾（merge + push，09-11 晚）

- B 已 push task-5（`17ce1d5` 验收短路 + phase 计时）与 task-6（`be916d6` lark import/sleep mock）；本阶在其上 rebase，人工合并 `loop.py`（两相状态机 + 计时并存：`phase` 与 `phase_seconds` 同记录）。
- S4 commit `d417332`，已 push origin/`s2-selfdrive-loop`。
- 合并后全量 **1025 passed, 1 skipped in 39s**（task-6 提速生效：71s→39s）。
- **合并后再跑真机极小靶**：仍 `verdict=done`，证据链 + 计时齐（total 24.65s；step1 criterion 红、step2 implement 绿）。

## 四、遗留 / 坑

- **本机制只适用"加能力"类项**：基线须绿，故"修既有 bug"项（基线红）仍由人给判据。
- 判据"合理性"无法机械判定 → 留人复核（保留的认知贡献，防无关红测试钻空子）。
- `test_observe_while_busy` 全量负载偶发（独立缺陷，非本阶）。

## 五、下一步（待 YZ）

- 复核本阶改动 + 靶子判据合理性。
- 合 task-5/6 后收口 S4 第一阶。
- 后续阶（风险低→高）：议程内容（L3，须先有终结/丢弃权）→ 跨会话记忆。
