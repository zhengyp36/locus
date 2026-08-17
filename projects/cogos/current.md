# cogos

多 agent 运行时，飞书作通信总线，前身 agent-study。通信层已真机调通；agent-term 架子、账号失效/刷新、agent 账号 id 加 provider 前缀、AccountRef 号码解析（三级缓存）+ agent send 发 human 均已完成。Telecom 通信接口（agent↔daemon 面向对象重构）已实现并提交（`88d34d4`）：FeishuTelecomClient 四方法 + daemon user_id→H 号反查 + term 迁移。群聊 send（target=Chat）、to_targets @、群内 bot 消息 app_id 反查留空待讨论。`a7dabac` 补 agent startup deny reason + 账号过期 60s 缓冲 + term 改名。Phone 抽象（TelecomClient 之上领域层：卡/联系人/会话/消息状态 + 本地目录）已定稿待编码。细节见锚点与 entries。

## 锚点

- 本体/约定/关键文件/设计决策/前身来源: projects/cogos/README.md
- 项目认知地图（目的轴 + 概念体系 + 状态轴 + 代码分层）: projects/cogos/entries/project-map.md
- 阶段记录: projects/cogos/CHANGELOG.md
- 遗留问题: projects/cogos/ISSUES.md
- 下一阶段方向: projects/cogos/ROADMAP.md
- 历史细节: projects/cogos/index.md → projects/cogos/entries/
