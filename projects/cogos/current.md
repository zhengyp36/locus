# cogos

多 agent 运行时，飞书作通信总线，前身是 agent-study。通信层 Phase 0/1/A/C 已提交，setup 流程（卡片驱动 provider 创建）已真机调通；`/resume` 代码完整、待真机验证。调通中修 3 点已提交（`19cf32b`）。

## 锚点

- 本体/约定/关键文件/设计决策/前身来源: projects/cogos/README.md
- 项目认知地图（已成图；目的轴 + 概念体系 + 状态轴 + 代码分层）: projects/cogos/entries/project-map.md
- 阶段记录: projects/cogos/CHANGELOG.md
- 遗留问题: projects/cogos/ISSUES.md
- 下一阶段方向: projects/cogos/ROADMAP.md
- 历史细节: projects/cogos/index.md → projects/cogos/entries/

## 下一步

- `/resume` 真机验证。
- 之后按 ROADMAP：可靠性/可观测性 → 持久化 → 认知树 + InferNode → agent 运行时 → 权限。
- 地图维护：改动改变不变量/易错点/状态轴时，更新 project-map.md（AI 触发 + 人纠偏）。
- 遗留：speak 用 user_id 需额外权限。
