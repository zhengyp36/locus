# 索引

- 2026-08-15: agent 账号失效/刷新实现（refresh 无返回值 + load 判定，弃 ensure→verify；456 passed，`ae02c0b`）→ entries/2026-08-15-cogos-agent-refresh-impl.md
- 2026-08-15: agent-term 架子实现（6 步 subagent 工作流）+ 账号失效/刷新方案定稿（ensure→verify + 12h 失效，未实现）→ entries/2026-08-15-cogos-agent-term-impl.md
- 2026-08-15: agent-term 方案定稿（daemon=agent 通信代理 + channel 协议 + term 脚手架，产出 docs/agent-term-design.md，无代码）→ entries/2026-08-15-cogos-agent-term-design.md
- 2026-08-15: /help 调整（排首位 + bitable_url）+ /query-agent（云端查 agent_registry）真机验证通过（8b690be）→ entries/2026-08-15-cogos-help-query-agent.md
- 2026-08-15: /add-human /add-agent 实现（号码分配 + counter 接线 + PIN + agent-bot 卡片创建，已提交 c540d15）→ entries/2026-08-15-cogos-add-agent.md
- 2026-08-15: resume cloud-first 重写（drive API 列 bitable）+ 跨设备验证通过（`a0e1092`）→ entries/2026-08-15-cogos-resume-verify.md
- 2026-08-15: provider.json 3 字段索引层落地（`d84660d`）+ resume 验证 gap + test_workdir_switch 修复（`03854d0`）→ entries/2026-08-15-cogos-provider-resume.md
- 2026-08-15: setup 流程真机调通 + 3 项修复（done 去重 / finish 失效 / pin 列）→ entries/2026-08-15-cogos-setup-verify.md
- 2026-08-15: 项目认知地图成图（目的轴 + 概念体系 + 状态轴 + G1-G5 分层 + 映射）→ projects/cogos/entries/project-map.md；建图过程 → entries/2026-08-14-cogos-map.md
- 2026-08-14: Phase C 联调 3 bug 修复（patch 授权步 + 落盘提前/重试可续 + 卡片按钮）→ projects/cogos/entries/2026-08-14-cogos-bugfix.md
- 2026-08-12~13: Phase 0/1/A/C 实现 + provider 字段改造 + 联调 3 问题 → projects/cogos/entries/2026-08-12-cogos-setup.md
- 2026-08-12: 真实账号集成测试、invite-bot 修复、DESCRIPTION 补齐 → projects/cogos/entries/2026-08-12-cogos-comm-testing.md
- 2026-08-12: 交接确认、版本依赖、bot_type 补齐、测试范围 → projects/cogos/entries/2026-08-12-cogos.md
