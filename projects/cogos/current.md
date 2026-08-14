# cogos

多 agent 运行时，飞书作通信总线，前身是 agent-study（先学 agent 后开发 agent）。通信层 Phase 0/1/A/C 已提交，Phase C 联调 3 bug 已修并已提交（`54394c4`），待联调验证。

## 锚点

- 本体/约定/关键文件/设计决策/前身来源: projects/cogos/README.md
- 代码认知地图: projects/cogos/entries/code-map.md（写时同步重写，读代码先查它）
- 阶段记录: projects/cogos/CHANGELOG.md（G1~G3f + comm 全史）
- 遗留问题: projects/cogos/ISSUES.md（Phase C 3 bug 已修待验证 + speak 权限）
- 下一阶段方向: projects/cogos/ROADMAP.md
- 历史细节: projects/cogos/index.md → projects/cogos/entries/

## 下一步

- 用新方法建项目认知地图（目的优先，代码是已实现子集）：先读 ~/codex/cogos/docs/ 设计文档，建「项目目的→分层→代码子集」的地图；旧 code-map.md 是方案 b 冷启动快照，将被取代。思路见 projects/locus-meta/entries/2026-08-14-code-map-revision.md。
- 联调验证 Phase C 全流程（3 bug 已提交 `54394c4`，待验证）。
- 遗留：speak 用 user_id 需额外权限（见 projects/cogos/ISSUES.md）
