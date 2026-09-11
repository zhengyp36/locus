# 分层验收：设计 + 落码（2026-09-11 晚，会话 #3）

承接 list-timers dogfood。把"每相全量 + 复跑"的验收降为"变更测试先行、全量按需"。

## 成本事实（实测）

- 全量 `python3.11 -m pytest -q` = **41s / 1052 passed**（task-6 已生效，旧报告的 66s 作废）。
- 现状一次 run：baseline/criterion/implement 三相各复跑确认 = 6 次全量 ≈ 246s，占 run 主导（model ~169s）。
- 分层预期：验收 ~246s → ~175s（省 ~30%）；套件增长时全量单价上升，收益放大。

## 设计（YZ 认可两裁决点）

spec：`cogos-s2/docs/design-selfdrive-loop-s4-layered-acceptance.md`。

- **步骤类型 `changed_tests`**：agenda 的 `acceptance` 加 `{changed_tests: true}`，机制运行前解析为"相对 run 起点的变更 `tests/**/*.py`"并生成 `python3.11 -m pytest -q <files>`。
- **裁决点 1**：target 由工作树 diff 推导（写前未知），agenda 显式 `cmd` 可覆盖。
- **裁决点 2**：全量恒在 acceptance 末步、遇错即止短路；baseline/终局付全量，判据相不付。
- **判据相 `only_target=True`**：只跑变更测试。空 target → `target_missing`（反馈写测试，不记红）；红 → 冻结 `target_files`、记 `criterion_red`、切实现相；绿 → 判据未成立、不跑全量（无信息）。
- **收紧**：判据相记红**只认 target 红**，不再看 `changed_now`（原"工作树有变化"信号）→ 堵"改坏源码伪造判据红"。
- **实现相**：沿用冻结 `target_files`（防换测试）；文件丢失 → `criterion_lost`；target 绿 → 跑全量；全量绿 + `changed_now` → done。
- **复跑触发**：判据相改用 `target_red`；实现相仍 `passed + changed_now`；baseline 不变。
- **opt-in + 兼容**：agenda 不含 `changed_tests` → 走 legacy 路径，旧行为零影响。

## 落码（cogos-s2）

- `cogos/agent/loop.py`：`is_changed_tests_step` / `_step_label` / `_changed_test_files` / `collect_changed_tests` / `_target_cmd`；`run_acceptance(**start_tests, target_files, only_target)` + 返回字段 `target_files/target_missing/target_red/failed_step`；`run_item` 相逻辑（`layered` / `start_tests` / `frozen_target`）。
- `tests/agent/test_loop.py`：+9（分层解析 6 + 两相端到端 3）。
- 常量：`CHANGED_TESTS_RUNNER = "python3.11 -m pytest -q"`、`MAX_TARGET_FILES = 20`（超限 target 视为不可用）。

## 验证

- `tests/agent/test_loop.py` 33 passed；全量 **1061 passed / 1 skipped**，无回归。
- **真机 dogfood（09-11 会话 #4）**：靶 `list-timers`，worktree `cogos-dogfood-layered`（基于 `136ff2e` + 分层 `loop.py`；agenda `[{changed_tests: true}, {cmd: python3.11 -m pytest -q}]`）。
  - `verdict=done`；baseline `[null,0]` 152.65s（2 全量）；criterion `[1,null]` **5.58s（0 全量）**；implement `[0,0]` 105.43s（target + 全量 ×2）。
  - 总验收 393.5s → 263.7s（省 ~33%）；单次 run 562.5s → 448.4s；全量 6 → 4 次（合 spec §4）。
  - `target_files=["tests/agent/test_list_timers.py"]` 落库且判据/实现两相一致；stash 生产改动 → 8 failed（判据真红）。

## 归属 / 提交

- `cogos-s2`：commit `9563fe4`，已 push `s2-selfdrive-loop`。
- dogfood 靶场产出（list_timers 的重复实现）属实验、**不入库**；list_timers 已在 `77dc547` 入库。
- 接口 spec 与实现已一致；spec 顶部标注"已落码"。
