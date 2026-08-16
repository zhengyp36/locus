# cogos

多 agent 运行时，飞书作通信总线，前身 agent-study。通信层（Phase 0/1/A/C + setup + provider.json 索引层 + resume cloud-first + 数据管理）已落地真机验证；agent-term 架子（`5094ba8`）+ 账号失效/刷新（`ae02c0b`）+ agent 账号 id 加 provider 前缀（`2381ffc`）+ AccountRef 号码解析/三级缓存 + agent send 支持 provider:number 发 human（`f7cfd1a`）已完成。下一步进 agent 运行时。

## 锚点

- 本体/约定/关键文件/设计决策/前身来源: projects/cogos/README.md
- 项目认知地图（目的轴 + 概念体系 + 状态轴 + 代码分层）: projects/cogos/entries/project-map.md
- 阶段记录: projects/cogos/CHANGELOG.md
- 遗留问题: projects/cogos/ISSUES.md
- 下一阶段方向: projects/cogos/ROADMAP.md
- 历史细节: projects/cogos/index.md → projects/cogos/entries/

## 下一步

- revoke 命令（/revoke-agent <Axxxx>）暂不实现：短期内无失效必要。
- 后置项：agent-bot WS 激活 + EventHandler.register("agent") + agent:message 路由推送 + agent send 的 A 目标（open_id）支持。
- 之后按 ROADMAP：可靠性/可观测性 → 持久化 → 认知树 + InferNode → agent 运行时 → 权限。
