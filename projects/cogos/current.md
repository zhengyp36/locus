# cogos

多 agent 运行时，飞书作通信总线，前身是 agent-study。通信层 Phase 0/1/A/C 已提交；setup 真机调通；provider.json 3 字段索引层落地；/resume cloud-first 跨设备验证；数据管理（/add-human /add-agent /query-agent /help）已落地。agent-term 架子已实现（channel 协议 + daemon 长连接 + term 交互终端 + startup PIN 鉴权，`5094ba8`）；账号失效/刷新已实现（refresh 无返回值 + load 判定，弃 ensure→verify，`docs/agent-account-refresh-design.md`，456 passed，`ae02c0b`）。agent 账号 id = provider-number（bot-COGOS008-A0001.json，跨 provider 不冲突）。

## 锚点

- 本体/约定/关键文件/设计决策/前身来源: projects/cogos/README.md
- 项目认知地图（目的轴 + 概念体系 + 状态轴 + 代码分层）: projects/cogos/entries/project-map.md
- 阶段记录: projects/cogos/CHANGELOG.md
- 遗留问题: projects/cogos/ISSUES.md
- 下一阶段方向: projects/cogos/ROADMAP.md
- 历史细节: projects/cogos/index.md → projects/cogos/entries/
- 失效/刷新实现细节（本次会话）: projects/cogos/entries/2026-08-15-cogos-agent-refresh-impl.md
- 失效/刷新详细设计（本体）: ~/codex/cogos/docs/agent-account-refresh-design.md

## 下一步

- 补 revoke 命令（/revoke-agent <Axxxx>，云端 status 改 inactive）作失效机制真机验证入口（现只能 mock 单测）。
- 后置项：agent-bot WS 激活 + EventHandler.register("agent") + agent:message 路由推送 + send 的 provider:Hxxxx 前缀解析。
- 之后按 ROADMAP：可靠性/可观测性 → 持久化 → 认知树 + InferNode → agent 运行时 → 权限。
- 遗留：speak 用 user_id 需额外权限；注销最终一致非强保证（fail-open 可无限续命）；resume 重建账号 name/patch_granted 与 setup 有差异。
