# status｜cogos 自驱回路（2026-09-11 交接）

> 本文件是**新会话入口**。恢复顺序：`locus/active.md` → `locus/projects/cogos/current.md` → 本文件 → `plan.md` + `state.md`。
> 旧活文档已归档：`locus/projects/cogos/checkpoint/26-09-11-live-checkpoint/`（详见本目录 `README.md`）。

## 当前问题（一句话）

方向已从"视觉/机制细节"转回主线——造**能自驱推进**的 cogos agent；计划已定（`plan.md`）、状态面已收（`state.md`），**停在 S0 待 YZ 验收**。

## 本会话做了什么

1. **方向讨论收敛**：目标 = 自主度阶梯 L1→L4；入口 = dogfood（让 agent 维护 cogos 自身）；不押 L4，押"把回路建起来并逐阶抬升"。
2. **行业调研**（结论见 entries）：定位已商品化；未解在长程；验证是活跃区但差异化在 harness 层。
3. **保命收编**：`/tmp/kilo` → `cogos/research/`（push `c3ad76f`）；`../checkpoint` 87 文件 → locus 快照（push `ace9c95`）；旧活文档清理。
4. **产出**：`plan.md`（计划）+ `state.md`（S0 状态面）。

## 关键结论

- 回路 `议程 → 触发 → 执行 → 验证 → 写回` 最缺**三格**：**机器可读议程 / 自触发 / agent 内自验证** → 是 L1→L2 门槛。
- 执行层齐（模型 + 动作循环 + 工具 + 终端）；感知视觉库完成但**未接入 consciousness 工具集**；记忆缺跨会话持久。
- 纪律：模型驱动、环境哑；过程式只做机制、不设计策略；每阶配安全件；验收换任务轴。
- 落点：计划→`plan.md`；状态面→`state.md`（收口进 locus current/entries）；设计→`cogos/docs/`；过程→本目录。

## 下一步（新会话）

1. YZ 验收 `state.md` 的三问（表是否认可 / S1 用已有件填 / S2 取候选 1）。
2. **S1**：写最小回路 spec（`议程项 → 推进一小步 → 验证 → 写回 → 通知 → 停/问`，每格用已有件填）。
3. **S2**：取 `ISSUES.md` 候选 1（`load_bot` 与 `AccountRef.ensure` 分层错位）手工跑一遍（"YZ 不在"约束）。

## 状态/坑

- `../checkpoint` 已清空重启，编号从新开始，**不续接旧 `checkpoint-N`**。
- 内网 LM key 已在新提交中替换为 `ik_REDACTED`；原 key 仍在 locus 历史（YZ 已知，内部 key 外部不可用）。
- `/tmp/kilo` 的 ~133MB 渲染图片未进 git（可复现，未收）。
