# Checkpoint 工作流规则

采用 `locus/scratch/checkpoint-rule.md` 规则（凝练可恢复、锚点优先），但 checkpoint 落本目录（`../checkpoint/`），避免 `/undo` 回退草稿文档。

## 文件职责

- `cogos-live-verification-plan.md` — 验证计划（目标/阶段/分层/分工/必测点/工作流），相对稳定，只改计划本身
- `codebase.md` — 代码认知基线 + 每步对代码的新认知，append 式跨步骤累积
- `step-N-<主题>.md` — 每步过程记录（当前问题/已做修改/已读代码要点/关键结论/遗留坑）

## codebase.md 要求

- append 式，跨步骤持续累积，只增不改旧结论（新认知推翻旧的可就地标注）
- 只记"对代码的新认知"：`文件:行` + 关键逻辑一句话，够重读时定位即可
- 凝练可恢复，锚点优先，不搬运原文
- 代码/路径/变量/文件名用英文，讨论结论可用中文

## 会话节奏

1. 新会话加载 `cogos-live-verification-plan.md` + `codebase.md` 恢复上下文
2. 按阶段执行；重要信息记 `step-N-<主题>.md`；新代码认知 append 到 `codebase.md`
3. 一步完成后停下，提示 YZ `/undo` 回退清理讨论干扰
4. 下一步：加载 `codebase.md`（+ plan）恢复，继续

## 命名

- `step-1-setup-COGOS002.md`（建 provider + agent）
- 后续按实际拆：`step-2-...`、`step-3-...`
