# cogos

多 agent 运行时，飞书作通信总线，前身 agent-study。通信层（Phase 0/1/A/C + setup + provider.json 索引层 + resume cloud-first + 数据管理）已落地真机验证；agent-term 架子（`5094ba8`）+ 账号失效/刷新（`ae02c0b`）+ agent 账号 id 加 provider 前缀（`2381ffc`）已完成。下一步进 agent 运行时。

## 锚点

- 本体/约定/关键文件/设计决策/前身来源: projects/cogos/README.md
- 项目认知地图（目的轴 + 概念体系 + 状态轴 + 代码分层）: projects/cogos/entries/project-map.md
- 阶段记录: projects/cogos/CHANGELOG.md
- 遗留问题: projects/cogos/ISSUES.md
- 下一阶段方向: projects/cogos/ROADMAP.md
- 历史细节: projects/cogos/index.md → projects/cogos/entries/

## 下一步

- 补 revoke 命令（/revoke-agent <Axxxx>，云端 status 改 inactive）作失效机制真机验证入口。
- 后置项：agent-bot WS 激活 + EventHandler.register("agent") + agent:message 路由推送 + send 的 provider:Hxxxx 前缀解析。
- 之后按 ROADMAP：可靠性/可观测性 → 持久化 → 认知树 + InferNode → agent 运行时 → 权限。
