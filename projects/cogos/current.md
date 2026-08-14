# cogos

多 agent 运行时，飞书作通信总线，前身是 agent-study。通信层 Phase 0/1/A/C 已提交（`6e514fe`），Phase C 联调 3 bug 已修已提交（`54394c4`），待联调验证。

## 锚点

- 本体/约定/关键文件/设计决策/前身来源: projects/cogos/README.md
- 项目认知地图 · 建图（进行中；口述背景 + 偏差清单 + 工作约定）: projects/cogos/entries/2026-08-14-cogos-map.md
- 代码认知地图（旧方案 b 快照，将被取代）: projects/cogos/entries/code-map.md
- 阶段记录: projects/cogos/CHANGELOG.md
- 遗留问题: projects/cogos/ISSUES.md
- 下一阶段方向: projects/cogos/ROADMAP.md
- 历史细节: projects/cogos/index.md → projects/cogos/entries/

## 下一步

- 建项目认知地图（进行中）：口述背景 + 设计文档核对 + 偏差清单已完成，待人工审核 2 个偏差点，然后读代码分层 + 标状态轴 → 成图取代旧 code-map.md。过程草稿 scratch/cogos-map-2026-08-14.md（含 .orig 备份）。
- 联调验证 Phase C 全流程（3 bug 已提交 `54394c4`，待验证）。
- 遗留：speak 用 user_id 需额外权限。
