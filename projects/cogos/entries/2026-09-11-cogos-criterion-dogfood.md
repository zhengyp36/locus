# cogos 判据源外移：真靶 dogfood + 假 done 修复（09-11 晚）

> 承接 `2026-09-11-cogos-selfdrive-pivot.md`、`2026-09-11-cogos-s3-trigger.md`；
> 过程/证据在 `/home/zhengyp/work/A/checkpoint/`（`status.md` = 新会话入口，`dogfood/report.md` = 本轮报告，`handoff-criterion-dogfood.md` = 方向候选）。

## S4 第一阶（判据源外移）

- 议程项可标 `requires_criterion: true`：**判据内容（红测试）由 agent 写，机制（跑命令/退出码/红绿）留壳**。
- 两相：baseline 必绿 → criterion 相（agent 只写会失败的红测试，验收转红即确立判据）→ implement 相（改到绿）→ done。
- `done` 必过 `baseline_green → criterion_red → implemented_green`；证据落 `runs.jsonl`（`phase` / `red_green`）。
- 落 `cogos/agent/loop.py` + `tests/agent/test_loop.py` + `docs/design-selfdrive-loop-s4.md`，commit `d417332`（已 push `origin/s2-selfdrive-loop`）。

## 真靶 dogfood（候选 1，YZ 选 COGOS_HOME 切片）

- 靶子：给运行时状态目录引入 `COGOS_HOME`（`~/.cogos` 四处硬编码），加能力类，`requires_criterion`。
- worktree `/home/zhengyp/work/A/cogos-dogfood`（分支 `dogfood-cogos-home`），真机 deepseek + `--dry-notify`。

**运行 1（未修 harness）→ 零改动假 done**：壳报 `done`、`red_green` 齐全，但 worktree 零改动。两坑叠加：
- **验收 flaky**：`tests/agent/test_terminal.py::test_observe_while_busy`（全量负载下偶发，复现 ~1/6）→ step5 偶发红被当成"agent 写出的判据"，step6 又绿 → 假红→假绿。比 S3 空转更隐蔽。
- **cu error**：`runtime._advance` 调 `LmClient.chat` 未传 `max_tokens`（默认 1000）→ 写文件的 tool_call arguments 截断 → JSON 非法 → `semantic`，模型从未写成功。

**修复 + 运行 2**：先修 harness（`30de9fd`：flaky 测试改轮询、`max_tokens=8192`）→ `verdict=done` 真增量（新增 `cogos/home.py` + 改 4 处 call site + 13 测试）；独立复核 stash 源码→5 failed、全量 1038 passed。

## 最小修改（YZ 批"实验阶段先简单改"）

落 `cogos-s2`（`s2-selfdrive-loop`，commit `4cf0f31`，未 push）：
1. **变更绑定守卫**（`loop.py`）：`_worktree_fingerprint`（`git status --porcelain` 哈希，非 git 返回 None=守卫关闭）；baseline 后记 `start_fp`；criterion 相"红但无变化"→ `spurious_red` 不认判据；`done` 前要求有变化，否则 `needs_human/no_change`（单相项一并堵 S3 空转）。
2. **cu error 保留 message**（`types.py`/`runtime.py`/`loop.py`）：`CuResultError` 增可选 `message`，壳回喂 `category: message`。category 契约不变。

验证：`test_loop.py` 20 passed、cogos-s2 全量 1028 passed/1 skipped；同步 `738fdfe` 到 dogfood 重跑**运行 3** `verdict=done` 真增量、全量 1040 passed（两次一致）。

## 遗留

- `max_tokens=8192` 修复只在 dogfood `30de9fd`，**未并入 s2 分支**，收口需 port。
- semantic 自动重试、红绿取两次一致、验收确定性治理、rubric/人裁决层——均押后待 YZ 开题。
- 新状态 `no_change`/`spurious_red` 需观察；agent 运行 3 产出留在 dogfood worktree 未 commit（运行 2 存档 `dogfood/agent-run2-output.patch`）。
- 工位 B：task-6（pytest 提速）、task-7（Kilo 常驻多通道）结果本会话未碰。

## 锚点

- 代码：`/home/zhengyp/work/A/cogos-s2`（`4cf0f31`）、`/home/zhengyp/work/A/cogos-dogfood`（`738fdfe` + 未提交 agent 产出）。
- 过程：`/home/zhengyp/work/A/checkpoint/`（`dogfood/report.md`、`runs*.jsonl`、`handoff-criterion-dogfood.md`）。
