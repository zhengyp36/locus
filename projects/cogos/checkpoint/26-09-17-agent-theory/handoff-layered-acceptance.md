# handoff｜分层验收：设计 + 落码（2026-09-11 晚，会话 #3）

> 承接 `status.md`（list-timers 会话）。本会话把分层验收从讨论推到设计 + 落码。
> 恢复顺序：`locus/active.md` → `locus/projects/cogos/current.md` → `locus/projects/cogos/ROADMAP.md` → 本文件（经 `status.md`）。
> 记忆细节：`locus/projects/cogos/entries/2026-09-11-cogos-layered-acceptance.md`。

## 一、当前状态（一句话）

**分层验收已设计、落码、真机 dogfood 验证省时**（`cogos/agent/loop.py` + `tests/agent/test_loop.py`），全量 **1061 passed / 1 skipped** 无回归；commit `9563fe4` 已 push。P0/L1 收口。下一步 = L2 最小自触发（见 `status.md`）。

## 二、本会话做了什么

1. **成本重算**：实测当前全量 `pytest -q` = **41s**（1052 passed；task-6 已生效，不再是旧报告的 ~66s）。现状一次 run 三相各复跑 = 6 次全量 ≈ 246s，验收占主导。
2. **设计 spec**（YZ 认可两个裁决点）：`cogos-s2/docs/design-selfdrive-loop-s4-layered-acceptance.md`。
   - 裁决点 1：target 由 **diff 推导 + agenda 可覆盖**。
   - 裁决点 2：**全量恒在 acceptance 末步按需短路**；baseline/终局付全量，判据相不付。
   - 预期：验收 ~246s → ~175s（省 ~30%）；套件增长时收益放大。
3. **落码**（cogos-s2 工作树，未 commit）：
   - `loop.py`：`acceptance` 支持 `{changed_tests: true}` 步骤；`collect_changed_tests` / `_changed_test_files` / `_target_cmd` / `_step_label`；`run_acceptance` 加 `start_tests` / `target_files` / `only_target` 与返回字段 `target_files` / `target_missing` / `target_red` / `failed_step`；判据相 `only_target=True` 只跑变更测试；实现相沿用**冻结 target**；新增 `criterion_lost` / `target_missing` 守卫；复跑触发改按 target；`changed_now` 信号在判据相被 target 取代（旧路径保留）。
   - `tests/agent/test_loop.py`：+9 测试（分层解析 6 + 两相端到端 3）。
   - spec 标注已落码；s4 spec §5 引用同步。
4. **飞书通知** YZ 两次（spec 完成、落码完成）。

## 三、关键结论 / 决策

- **验收分层的本质是改"步骤解析与排序"，不碰相状态机**：`changed_tests` 由机制解析成命令，全量恒在末步、遇错即止短路。
- **判据相收紧**：记红只认 target 红（不再看"工作树有无变化"），堵住"改坏源码伪造判据红"；`target_missing` 独立计数。
- **实现相防换测试**：冻结判据相首次记红的 `target_files`，实现相沿用；文件丢失 → `criterion_lost`。
- **旧行为零影响**：agenda 不含 `changed_tests` 时走 legacy 路径，全量旧测试不变（这是兼容关键）。
- **opt-in**：agenda 需显式加 `changed_tests` 步骤才启用。

## 四、验证

- `pytest tests/agent/test_loop.py -q` → 33 passed。
- 全量 `python3.11 -m pytest -q` → **1061 passed / 1 skipped**（基线 1052 + 9），无回归。
- 未做：真机 dogfood、commit。

## 五、下一步（待 YZ，已更新）

- **首推：L2 最小自触发**（自己醒来再跑一条 + 预算/暂停安全件）；判据 = 无人触发下推进一条且不自毁。服务 owner 不再是阻塞（已废）。
- 暂缓：P2 议程源外移安全件（不预造）。
- 可选：再跑 1 个真靶 dogfood 扩样本；task-7（工位 B）回后定常驻宿主。
- 本交接的 dogfood/commit 动作已于会话 #4 完成，最新入口见 `status.md`。

## 六、锚点 / 坑

- 代码：`/home/zhengyp/work/A/cogos-s2`（`77dc547` + 未 commit 改动：`loop.py` / `tests/agent/test_loop.py` / 两个 spec）。
- 设计 spec：`cogos-s2/docs/design-selfdrive-loop-s4-layered-acceptance.md`。
- 接口实现：`loop.py` 的 `is_changed_tests_step` / `collect_changed_tests` / `run_acceptance`；相逻辑在 `run_item`（`layered` / `start_tests` / `frozen_target`）。
- 靶场 worktree：`cogos-dogfood-timer` / `cogos-dogfood`（分支保留）。
- 坑：真机 target 命令硬编码 `CHANGED_TESTS_RUNNER = "python3.11 -m pytest -q"`（换项目需调）；target 上限 `MAX_TARGET_FILES=20`，超限视为不可用。
