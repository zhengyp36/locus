# dogfood 报告｜真靶：list-timers（加能力类，判据样本 #2）

> 2026-09-11 晚（承 `handoff-criterion-dogfood.md` 候选 1）。YZ 选定靶子 = 给 `cogos/agent/timer.py` 加 `list_timers`（枚举 pending 闹钟）。
> 结论：**机制再次在真活上干净跑通**（真红→真绿 + 真增量），无 `spurious_red` / `no_change` / `unstable_acceptance` / `repeated_cu_error`。判据质量高（含负例）。

## 一、设置

- **靶子**：`list_timers` 工具——`TimerScheduler` 能 set/cancel 并持久化 `timers.json`（重启加载 pending），但无法枚举；补 scheduler 方法 + 注册工具，返回 id/title/fire_at/remaining_seconds。
- **壳**：`cogos/agent/loop.py`（S4 两相 + 确定性/错误处理），worktree `/home/zhengyp/work/A/cogos-dogfood-timer`，分支 `dogfood-list-timers`，基线 `62c400f`（= `s2-selfdrive-loop`）。
- **环境**：真 deepseek（lm-service `127.0.0.1:11434`，`LM_INTERNAL_KEY`，tier=basic/flash）+ `--dry-notify`。
- **验收**：`python3.11 -m pytest -q`（全量）。

## 二、证据链（`runs.jsonl`）

```
baseline  : passed=true  (acceptance 132.99s，复跑两次)
step 1    : phase=criterion  passed=false  exit_codes=[1]  (model 110.3s / acceptance 127.74s，复跑确认红)
step 2    : phase=implement   passed=true   exit_codes=[0]  (model  58.66s / acceptance 132.81s，复跑确认绿)
final     : verdict=done  red_green={baseline_green:true, criterion_red:true, criterion_red_step:1, implemented_green:true}
```
- 总耗时 **562.53s**（setup 0.03 / model 168.96 / acceptance 393.54 / notify 0）。仍以全量验收为主导（约 66s/次，相变各复跑一次）。

## 三、agent 产出（真增量）

- `cogos/agent/timer.py`：`TimerScheduler.list_timers()`（按 fire_at 排序、只含 pending、含 remaining_seconds）+ `make_timer_specs` 注册 `list_timers` 工具。
- `cogos/agent/consciousness.py`：把 `list_timers` 加进 consciousness 的 toolset（否则不暴露给模型）。
- `cogos/agent/config.py`：`render_system_prompt` 工具清单补一行。
- `tests/agent/test_list_timers.py`：8 用例。

三处生产改动**逻辑一致且必要**：注册工具 → 进 consciousness toolset → 进系统提示，缺一模型就看不见。

## 四、独立复核（§8 三样证据）

1. **red_green**：齐；无异常状态。
2. **判据真实性**：`git stash` 掉三处生产改动、只留测试 → `tests/agent/test_list_timers.py` **8 failed**（`AttributeError` / `KeyError: 'list_timers'`）；恢复。
3. **实现最小性**：diff 仅 timer.py 新方法 + spec、consciousness/config 各一行同步；贴合目标，未弱化测试。
4. **全量**：**1040 passed / 1 skipped**（基线 1032 + 新增 8）。

## 五、结论 / 观察

1. 判据源外移机制**第二个真靶再次成立**，且比 COGOS_HOME 那次更干净（无 harness 缺陷干扰、无守卫触发）。
2. 本次判据含**负例**（排除 cancelled/fired）+ 排序 + 工具注册，合理性明显高于"仅覆盖 happy path"，可作正样本。
3. 目标文件外的"暴露路径"（registry→toolset→system prompt）由 agent 自行发现并改全——印证"最小改动"不等于"单文件改动"。
4. 成本结构不变：**验收（全量 ~66s/次 × 复跑）仍是主要时间项**，分层验收的价值进一步显现。

## 六、遗留 / 待 YZ

- 产出留在 worktree **未 commit**（`cogos-dogfood-timer`：3 改 + 1 新测试），待复核后决定是否入库/合并（可作独立小 PR）。
- `cogos-dogfood`（COGOS_HOME 靶）产出仍未 commit，同上。
- 机制侧本轮到目前**未暴露新缺陷**；分层验收设计、工位隔离、task-7 仍未动。

## 七、锚点

- 代码：`/home/zhengyp/work/A/cogos-dogfood-timer`（`62c400f` + 未提交产出）。
- 证据：`runs.jsonl`（本次）。
- 靶子：`agenda.yaml`。
