# cogos

多 agent 运行时，飞书作通信总线，前身 agent-study。通信层已真机调通；agent-term、账号失效/刷新、AccountRef 号码解析、Telecom 通信接口（FeishuTelecomClient 四方法）均已完成；Phone 抽象（卡/联系人/会话/消息状态 + 本地目录）已定稿待编码。群操作落地（`eb68ceb`）：飞书封死 app 拉 app bot（invite 报 230003），自动化拉 bot 唯一路径 me_join（需 public 群），路径=建群 private→拉真人 user_id→改 public→各 bot me_join→改回 private。agent-bot 创建流程（`8ab7420`）：status 写 init + 每 agent 建 Contact bitable。群内 bot↔bot 消息、to_targets @ 留空待讨论。细节见锚点与 entries。

## 锚点

- 本体/约定/关键文件/设计决策/前身来源: projects/cogos/README.md
- 项目认知地图（目的轴 + 概念体系 + 状态轴 + 代码分层）: projects/cogos/entries/project-map.md
- 阶段记录: projects/cogos/CHANGELOG.md
- 遗留问题: projects/cogos/ISSUES.md
- 下一阶段方向: projects/cogos/ROADMAP.md
- 历史细节: projects/cogos/index.md → projects/cogos/entries/
