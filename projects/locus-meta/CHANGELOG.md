# CHANGELOG

- 2026-08-15 — 项目认知地图方法论：以 cogos 建图过程为样本，把方案 A 的「代码认知地图」升级为「项目认知地图」（目的优先 + 状态轴 + 维护循环 + 验收分工，八节骨架 + 建图过程），落 projects/locus-meta/docs/project-map-method.md。
- 2026-08-14 — 路径锚点约定：修复记忆层路径指针不自包含问题（相对工程目录短路径 → 从 locus 根写完整相对路径），覆盖 locus-meta/cogos 两工程 current/index/README + entries 跨引用；详见 projects/locus-meta/docs/path-anchor-convention.md。
- 2026-08-14 — 权限简化定稿：人机配合授权问题解法（权限白名单反转成黑名单，默认 allow + 枚举危险命令 deny/ask），落 `~/.config/kilo/kilo.jsonc`。
- 2026-08-14 — 目录/工程管理定稿：顶层补 README；locus-meta 引入 docs/；引入 CHANGELOG/ROADMAP/ISSUES，确立"管理/记忆"两层模型。
- 2026-08-13 — 重新整理：极简记忆方案落地（docs/minimal-memory.md）+ 工程化印象层结构（docs/design-v2.md），active.md 指针，git tag locus-v1。
- 2026-08-13 — 使用一天后复盘：条件式规则失效、思考过长根因，git tag locus-original。
- 2026-08-12 — 搭建 locus 协作框架：初始提交 + 机制迭代（话题切换、旁注、timeline）。
- 2026-08-11 — 原理探索（在 ~/codex/agent-study 讨论实验）：multi-session-workflow 9 构想 + 5 实验，collaboration-framework-design 7 项决策。
