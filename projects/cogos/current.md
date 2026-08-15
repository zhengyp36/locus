# cogos

多 agent 运行时，飞书作通信总线，前身是 agent-study。通信层 Phase 0/1/A/C 已提交；setup 流程真机调通；provider.json = 3 字段索引层落地；/resume cloud-first 重写并跨设备验证通过（半恢复已裁决推迟）。数据管理已落地：/add-human /add-agent（号码分配 + counter 接线 + PIN 生成 + agent-bot 卡片创建）+ /query-agent（云端查 agent_registry 取 name/app_id/app_secret/pin/status）+ /help（排首位 + admin-bot 已建时打印 bitable_url）。agent 账号 id = 号码（bot-Axxxx.json）。

## 锚点

- 本体/约定/关键文件/设计决策/前身来源: projects/cogos/README.md
- 项目认知地图（目的轴 + 概念体系 + 状态轴 + 代码分层）: projects/cogos/entries/project-map.md
- 阶段记录: projects/cogos/CHANGELOG.md
- 遗留问题: projects/cogos/ISSUES.md
- 下一阶段方向: projects/cogos/ROADMAP.md
- 历史细节: projects/cogos/index.md → projects/cogos/entries/
- 本会话（/help 调整 + /query-agent）: projects/cogos/entries/2026-08-15-cogos-help-query-agent.md
- 上次会话（add-human/add-agent 实现）: projects/cogos/entries/2026-08-15-cogos-add-agent.md

## 下一步

- 半恢复（账号在、只删 provider.json）：已裁决推迟、标未验证。
- 待定：resume 重建账号 name 是否还原 app 真实名；可选抽 _get_app_name。
- 之后按 ROADMAP：可靠性/可观测性 → 持久化 → 认知树 + InferNode → agent 运行时（EventHandler 注册 agent、WS 激活 agent-bot、startup/send/shutdown + PIN 鉴权）→ 权限。
- 遗留：speak 用 user_id 需额外权限；agent-bot 已可创建但未激活（属 agent 运行时）。
