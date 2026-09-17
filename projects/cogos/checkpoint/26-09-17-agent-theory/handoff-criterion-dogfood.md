# handoff｜判据源外移：真靶 dogfood + 假 done 修复（新会话入口）

> 2026-09-11 晚。承接 `handoff-s4-next.md`（S4 方向选择）；本轮已完成"候选 1 真靶 dogfood"并按 YZ 指示做最小修改。
> 恢复顺序：`locus/active.md` → `locus/projects/cogos/current.md` → `../checkpoint/status.md` → 本文件 → `plan.md` + `state.md` → `checkpoint-3/4/5.md` → `dogfood/report.md`。
> 记忆细节：`locus/projects/cogos/entries/2026-09-11-cogos-criterion-dogfood.md`。

## 一、当前状态（一句话）

**S4 第一阶"判据源外移（红→绿两相）"已在真活 dogfood 上跑通（真增量），并针对首跑暴露的"零改动假 done"做了最小修复（变更绑定守卫 + cu error 留 message）；改动已 commit、未 push，下一步是 review/收口 + 选方向。**

### 本轮做了什么

1. **真靶 dogfood**（候选 1，YZ 选 COGOS_HOME 切片）：worktree `cogos-dogfood`（分支 `dogfood-cogos-home`），真机 deepseek + `--dry-notify`。
   - 运行 1（未修 harness）：**零改动假 done**。两坑叠加：① 全量 flaky（`tests/agent/test_terminal.py::test_observe_while_busy`，复现 ~1/6）伪造 `criterion_red`；② `cu max_tokens=1000` 截断写文件 tool_call → `semantic`，模型从未写成功。
   - 修 harness（`30de9fd`：flaky 测试改轮询 + `max_tokens=8192`）→ 运行 2 `verdict=done` 真增量。
2. **最小修改**（YZ 批"实验阶段先简单改"，落 `cogos-s2`，commit `4cf0f31`，未 push）：
   - **变更绑定守卫**（`loop.py`）：无变化的红记 `spurious_red` 不认判据；无变化不判 `done`（→`needs_human/no_change`）；单相项一并堵 S3 空转。
   - **`CuResultError` 保留 `message`**（`types.py`/`runtime.py`/`loop.py`）：观测改进，category 契约不变。
3. **同步 dogfood 重跑运行 3**：`verdict=done` 真增量，守卫不误伤；独立复核全量 **1040 passed / 1 skipped**（两次一致）。

### 验证

- `test_loop.py` 20 passed；`cogos-s2` 全量 **1028 passed / 1 skipped**。
- 运行 3：baseline 绿 → step1 criterion 红（worktree 有变化，守卫放行）→ step2 implement 绿；stash 源码→5 failed（判据真实）。

## 二、方向候选（供 YZ 选）

按"先收口、再外移"排序。

### 候选 0｜先收口本轮（低风险，建议先做）
- 复核 `4cf0f31`（守卫 + message）与 dogfood 运行 3 的 agent 产出。
- **把 `max_tokens=8192` 修复 port 到 `s2-selfdrive-loop`**（目前只在 dogfood `30de9fd`）；决定 `4cf0f31` / agent 产出是否 push、合并。
- 说明：不先定这个，机制分支与真跑环境会分叉。

### 候选 1｜继续真靶 dogfood（已验证机制，扩大样本）
- 换一个"加能力"类真靶（基线须绿）再跑，观察 agent 自产判据的合理性分布、`no_change`/`spurious_red` 是否误报。
- 注意：本机制不适用"修既有 bug"（基线红）项。

### 候选 2｜验证确定性 / 错误处理（补机制件）
- 验收 flaky 是共性风险：验收拆"靶向（确定）+ 全量（信息）"，或红绿取两次一致，或 flaky 治理。
- `semantic` 自动重试（模型偶发畸形响应，现直接 `CuResultError`）；连续 cu error 应触发停/问而非烧 max_steps。
- 属"机制性依赖"，是壳该补的件（非外移到 agent）。

### 候选 3｜议程源外移（L3，分水岭）
- 议程空时 agent 自生议题。**前提：先设计生成/终结/丢弃权安全件**，否则议程爆炸/自我扩权。
- 形态建议：先设计安全件，再谈外移。

### 候选 4｜触发进阶（L2 完整）
- agent 自己醒来（常驻/定时）。依赖工位 B 的 task-7（Kilo 常驻 + 事件唤醒 + 多通道）；工位隔离缺口仍是阻塞项。

### 候选 5｜跨会话记忆（支线）
- 运行时记忆跨会话持久。非人卡点，随需接。

### 候选 6｜不可执行判据的分化（rubric/人裁决层）
- verifier 不可能全程序化。方向：模糊目标→rubric/契约（agent 产、人复核）；真主观留人。别为可测而降目标轴。

## 三、YZ 要做的

- 复核 `4cf0f31` + dogfood agent 产出；决定是否 push/合并、是否 port max_tokens。
- 选下一步方向；若选候选 3 先谈安全件形态，若选候选 1 给靶子。

## 四、锚点

- 代码：`/home/zhengyp/work/A/cogos-s2`（`4cf0f31`，未 push）、`/home/zhengyp/work/A/cogos-dogfood`（`738fdfe` + 未提交 agent 产出）。
- 报告/证据：`dogfood/report.md`、`dogfood/runs.jsonl`（运行 3）、`runs-run2-real-done.jsonl`、`runs-run1-false-done.jsonl`、`dogfood/agent-run2-output.patch`。
- 靶子：`dogfood/agenda.yaml`；spec：`cogos/docs/design-selfdrive-loop-s1/-s3/-s4.md`。
- 状态面/计划：`state.md` / `plan.md`。
- 工位 B（未回）：`locus/projects/cogos/tasks/task-6-pytest-speedup.md`、`task-7-kilo-resident-multichannel.md`。
