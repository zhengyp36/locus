# MIGRATION-MAP｜../checkpoint 归置（2026-09-17）

源：`/home/zhengyp/work/A/checkpoint`（不在 git 内，临时讨论目录）
目标 1：`/home/zhengyp/work/A/locus/projects/cogos/checkpoint/26-09-17-agent-theory/`（cogos 过程/依据）
目标 2：`/home/zhengyp/work/A/locus/projects/kilo-resident/checkpoint/26-09-17-phone-number-contacts/`（kilo 支线）
目标 3（Phase 2 新建，非拷贝）：`/home/zhengyp/work/A/cogos/docs/design-selfdrive-agent.md`

纪律：物理归位不改内容；先 copy 后验证；本表为覆盖核对基准。

## 1. 散装 .md（源根目录，按原名 → 目标 1 根）

| 组 | 文件 | 类型 |
|---|---|---|
| design（当前） | `design-cogos-agent-current.md` `design-cogos-open-items.md` | 权威（Phase 2 被本体整体取代，此处留档） |
| design（旧 6） | `design-cogos-agent-form.md` `design-cogos-flow-direction.md` `design-cogos-loop-invariants.md` `design-cogos-minimal-agent.md` `design-cogos-runtime-flows.md` `design-cogos-runtime-states.md` | 过程（状态见 ARCHIVE-INDEX） |
| handoff（cogos） | `handoff-cogos-drives.md` `handoff-cogos-experience.md` `handoff-cogos-loop.md` `handoff-cogos-perception-tick.md` `handoff-cogos-scaffold.md` `handoff-cogos-selfgrown.md` | 过程 |
| handoff（agent） | `handoff-agent-e0-to-selfgrown.md` `handoff-agent-experiments.md` `handoff-build-agent-v0.md` | 过程 |
| handoff（ctx） | `handoff-ctx-seed.md` `handoff-ctx-seed-distill-contract.md` `handoff-ctx-seed-recurrence.md` `handoff-ctx-swap-probe.md` | 过程 |
| handoff（其它） | `handoff-identity-anchor-frame.md` `handoff-criterion-dogfood.md` `handoff-layered-acceptance.md` `handoff-s4-next.md` | 过程 |
| ctx 报告 | `ctx-recurrence-arm-analysis.md` `ctx-seed-experiments-e1-e2.md` `ctx-seed-probe-report.md` `ctx-seed-recurrence-experiment.md` `ctx-seed-trace-dump.md` `ctx-swap-probe-report.md` | 旁证 |
| 自驱阶段 | `checkpoint-1.md`~`checkpoint-5.md` `plan.md` `state.md` `status.md` `next-experiments.md` `s2-report.md` `s3-report.md` | 过程 |
| 目录说明 | `README.md` | 过程 |

> 目标 1 根共 43 个 .md 中的 41 个；其余 2 个见 §4。

## 2. 子目录

| 源 | 处理 | 目标 |
|---|---|---|
| `probe-e0/`（10 md + 512 非 md） | md 拷为 `probe-e0/*.md`；整目录 tar 为证据 | 目标 1 / `runs/probe-e0.tar.gz` |
| `probe-tendency/`（2 md + 1570 非 md） | md 拷；整目录 tar | 目标 1 / `runs/probe-tendency.tar.gz` |
| `probe-compress/`（1 md + 2975 非 md） | md 拷；整目录 tar | 目标 1 / `runs/probe-compress.tar.gz` |
| `s4-target/`（19 文件，含 py 测试） | 去掉 `__pycache__/`(4) `.pytest_cache/`(5) 后整拷 10 | 目标 1 / `s4-target/` |
| `dogfood/`（6 文件） | 整拷 | 目标 1 / `dogfood/` |
| `dogfood-timer/`（3 文件） | 整拷 | 目标 1 / `dogfood-timer/` |

tar 含各自目录内脚本（`run.py` `build_arms.py` `analyze.py` `*.sh` 等），它们是实验代码，非本体代码。

## 3. 非 md 清点（源共 5100）

| 类型 | 数量 | 去向 |
|---|---|---|
| json（run 结果） | 5041 | 随 §2 tar |
| jsonl / yaml / sh / log / patch / bak / TAG / gitignore | 31 | 随 §2 tar |
| py（实验脚本/测试） | 16 | 随 §2 tar（s4-target 除外，直拷） |
| pyc（缓存） | 4 | **排除**（`__pycache__`） |
| `.pytest_cache/`（含 1 md） | 5 | **排除** |

## 4. kilo 支线（→ 目标 2）

| 文件 | 类型 |
|---|---|
| `handoff-kilo-phone.md` | 过程 |
| `handoff-kilo-number-contacts.md` | 过程（current.md 标并行支线） |

## 5. 排除项

- 源根 `__pycache__/`、`.pytest_cache/`：缓存，不迁。
- 无其它非 cogos/kilo 文件。

## 6. 覆盖核对

- 源文件总数：5143（`find -type f`）。
- 迁入：45 散装 md（43 cogos ＋ 2 kilo）＋ probe 13 md ＋ 6 子目录全部非缓存文件。
- 排除：9（s4-target 的 pyc 4 ＋ `.pytest_cache/` 5）。
- 核对式：`5143 = 5070(probe tar) + 10(s4-target) + 6 + 3 + 45 + 9`，实测见 `MIGRATION-COVERAGE.md`。
