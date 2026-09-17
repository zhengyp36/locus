# dogfood 报告｜真靶：COGOS_HOME 切片（判据源外移首次上真活）

> 2026-09-11 晚。承接 `handoff-s4-next.md` 候选 1（真靶 dogfood），YZ 选定靶子=工位隔离缺口里的 `COGOS_HOME` 切片。
> 结论：**机制在真活上跑通**（真红→真绿 + 真增量），但首跑暴露两个 harness 缺陷，修复后才可信。

## 一、设置

- **靶子**：引入 `COGOS_HOME` 覆盖运行时状态目录（`~/.cogos` 四处硬编码：feishu config、lm-service config、phone term、loop agent 默认目录），默认不变。加能力类，`requires_criterion: true`。
- **壳**：`cogos/agent/loop.py`（S4 两相），worktree `/home/zhengyp/work/A/cogos-dogfood`，分支 `dogfood-cogos-home`。
- **环境**：真实 deepseek（lm-service `127.0.0.1:11434`）+ `--dry-notify`（不碰真飞书）。
- **验收**：`python3.11 -m pytest -q`（全量）。

## 二、运行 1（未改 harness）：verdict=done，但零改动 → **假 done**

- 壳报 `done`，`red_green` 证据齐全；实际 `git status` **完全干净**。
- **根因①（机制被不稳定验收欺骗）**：全量套件有 flaky —— `tests/agent/test_terminal.py::test_observe_while_busy`（全量负载下 `assert 'start' in ''`，复现约 1/6）。步骤 1–4 绿 → 步骤 5 偶发红，被壳当成"agent 写出的判据"记 `criterion_red` → 步骤 6 又绿 → 判 `done`。
  - 比 S3「验收空转」更隐蔽：S3 是假绿，这里是**假红→假绿 + 零改动**，红→绿门形同虚设。
- **根因②（模型从未写成功文件）**：全程多次 `cu error semantic`。定位=`cog_runtime._advance` 调 `LmClient.chat` 未传 `max_tokens`，用默认 1000；写测试文件的 tool_call `arguments` 被截断 → JSON 非法 → semantic。S3/S4 的小改动没触发。
- **harness 修复**（commit `30de9fd`）：
  1. `test_observe_while_busy` 改轮询等待 start（消 flaky）；
  2. `runtime._advance` 传 `max_tokens=8192`（够写文件）。

## 三、运行 2（修复后）：verdict=done，真增量

- **证据链**：baseline 绿 → step1 `criterion` 红（模型新建 `tests/test_cogos_home.py`）→ step2 `implement` 绿；`red_green` 全齐。
- **agent 产出**：
  - 新增 `cogos/home.py`：`cogos_home()` 解析 `COGOS_HOME`（支持 `~`，空值回落 `~/.cogos`）；
  - 改 `cogos/feishu/config.py`、`cogos/lm_service/config.py`、`cogos/phone/term.py`、`cogos/agent/loop.py`（新增 `_default_agent_dir()`）；
  - 新增 `tests/test_cogos_home.py`（13 用例：resolver 默认/覆盖/expanduser/空值 + 四处 call site 的 relocate/default）。
- **独立复核**：
  - stash 源码、保留测试 → 5 failed（判据**真实**，非无关红测试）；还原后全量 **1038 passed / 1 skipped**（连跑两次一致）。
  - 判据合理性（保留给人复核的认知贡献）：覆盖中心 resolver + 四处 call site，合理。

## 四、结论

1. 判据源外移机制在真活上**成立**：agent 自产判据 → 壳确认红 → 实现 → 红转绿 → done，且是真增量。
2. **红→绿门的前提是验收确定**：验收不稳定会伪造判据（本次靠人复核才发现假 done）。
3. `cu max_tokens=1000` 不足以写文件是 harness 缺陷，已修（8192）。

## 五、遗留 / 待 YZ

- **红→绿门是否加机制守卫**：如"done 必须有 git diff / `criterion_red` 必须伴随新文件"——否则不稳定验收 + 模型空转都能骗过（本次两坑叠加）。
- **验收确定性**：全量套件 flaky 是共性风险；是否要求验收确定/治理 flaky，或验收分"靶向（确定）+ 全量（信息）"。
- **runtime 是否重试 semantic**：模型偶发畸形响应，现在直接 `CuResultError`，未重试（暂未做）。
- agent 产出的 `COGOS_HOME` 改动**留在 worktree 未 commit**，待 review。

## 六、锚点

- 代码：`/home/zhengyp/work/A/cogos-dogfood`（worktree，`30de9fd` = harness 修复；其上为 agent 未提交改动）。
- 证据：`runs.jsonl`（运行 2，真 done）、`runs-run1-false-done.jsonl`（运行 1，假 done）。
- 靶子：`dogfood/agenda.yaml`。

## 七、最小修改 + 运行 3（YZ 批准"先简单修改"）

按"实验阶段、最小可回退"只做两项（落 `cogos-s2`，分支 `s2-selfdrive-loop`，commit `4cf0f31`）：

1. **变更绑定守卫**（治假 done 正主，`loop.py`）：新增 `_worktree_fingerprint`（`git status --porcelain` 摘要哈希，非 git 则返回 None=守卫关闭）；`start_fp` 在 baseline 后取；criterion 相"红但 worktree 无变化"→ 判为环境噪声、**不记 `criterion_red`**（记 `spurious_red`）；`done` 前要求 worktree 有变化，否则 `needs_human/no_change`（单相项同样受益，顺带堵住 S3 空转）。
2. **cu error 保留 message**（`types.py` + `runtime.py` + `loop.py`）：`CuResultError` 增可选 `message`；runtime 传 `message`；壳回喂 `[cu error] category: message`。纯观测，category 契约不变。

- 单测：`test_loop.py` 20 passed（新增 3：无变化 done→no_change / 无变化红被忽略→invalid_criterion / 有变化红→绿→done）；`test_contract.py` 增 `message` 断言。
- 全量：**1028 passed / 1 skipped**（cogos-s2）。
- **dogfood 运行 3（同步 `738fdfe` 到 worktree 后重跑）**：`verdict=done`，真增量；证据链 baseline 绿 → step1 criterion 红（worktree 有变化，守卫放行）→ step2 implement 绿。独立复核：stash 源码保留测试 → 5 failed（判据真实）；还原后全量 **1040 passed / 1 skipped**（两次一致）。
- 运行 3 同时验证守卫不误伤：真变化时正常 done。

**未做（押后）**：semantic 重试、红绿取两次一致、验收确定性治理、rubric/人裁决层。

## 八、遗留（更新）

- `cu max_tokens=8192` 修复目前**只在 dogfood 的 `30de9fd`**，尚未并入 `s2-selfdrive-loop`——收口时需 port。
- 红→绿门已加"变更绑定"，但"变化是否合理"仍留人复核；`no_change`/`spurious_red` 是新停/记状态，需观察。
- agent 运行 3 的产出留在 `cogos-dogfood` worktree 未 commit，待 review；运行 2 产出存档 `agent-run2-output.patch`。
- 证据：`runs.jsonl`（运行 3 真 done）、`runs-run2-real-done.jsonl`、`runs-run1-false-done.jsonl`。
