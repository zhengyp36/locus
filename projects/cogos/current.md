# cogos

多 agent 运行时，飞书作通信总线，前身是 agent-study（先学 agent 后开发 agent）。通信层 Phase 0/1/A/C 已提交（HEAD `6e514fe`），Phase C 联调 3 bug 已修（未提交），待联调验证。

## 锚点

- 本体/约定/关键文件/设计决策/前身来源: projects/cogos/README.md
- 代码认知地图: projects/cogos/entries/code-map.md（写时同步重写，读代码先查它）
- 阶段记录: projects/cogos/CHANGELOG.md（G1~G3f + comm 全史）
- 遗留问题: projects/cogos/ISSUES.md（Phase C 3 bug 已修待验证 + speak 权限）
- 下一阶段方向: projects/cogos/ROADMAP.md
- 历史细节: projects/cogos/index.md → projects/cogos/entries/

## 下一步

- 联调验证 Phase C 全流程（3 bug 修复未提交，一起验证）→ 提交
- 遗留：speak 用 user_id 需额外权限（见 projects/cogos/ISSUES.md）
- 待验收：code-map.md 各模块条目（职责一句话 + ≥1 条不变量/易错点；红线=只有文件清单/只列函数名/有职责零不变量）
