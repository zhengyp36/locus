# locus-meta

人与 AI 协作的方法论工程。

## 锚点

- 定位：locus 自身设计与方法论的落点，讨论"人与 AI 协作方法论"。
- 本体路径：无（locus 自身即本体）；remote: https://github.com/zhengyp36/locus。

## 已定结论

- 记忆/管理协议：极简记忆契约（指令两条、更新=重写、摘要+索引、细节入 entries；projects 分工程 + active 指针 + timeline）+ 两层模型（管理层=确定锚、除 CHANGELOG 外可重写需慎重；记忆层=类人印象；大写=管理/小写=记忆）+ 目录整理（顶层 README 给 AI、docs/ 为本体）。→ projects/locus-meta/entries/2026-08-14-locus-meta-structure.md + projects/locus-meta/docs/minimal-memory.md + projects/locus-meta/docs/design-v2.md
- 外部工程身份：README 记 remote URL + 本地本体路径两条（URL=稳定身份，本地路径=操作位置）；remote 从 git remote -v 实取、SSH 转 HTTPS。
- 授权简化：权限白名单反转成黑名单（默认 allow + 枚举危险命令 deny/ask），匹配 last-match-wins。→ projects/locus-meta/entries/2026-08-14-permission-simplification.md
- token 消耗（样本 cogos 联调 101K）：四条根因 + 四方案 A–D + 方案 E（模型路由，减单价正交轴，推迟）；中文比英文贵约 1.4x。→ projects/locus-meta/docs/token-cost-analysis.md + projects/locus-meta/docs/language-token-cost.md + projects/locus-meta/docs/token-cost-implementation.md（实施计划：阶段1完成、阶段2定稿待执行）
- 路径锚点约定：locus 内部文件指针一律从 locus 根写完整相对路径（projects/<工程>/...）；新会话 cwd 是 locus 根，相对工程目录的短路径会解析错。→ projects/locus-meta/docs/path-anchor-convention.md + projects/locus-meta/entries/2026-08-14-path-anchor-convention.md

## 下一步

- 实施 token 消耗方案阶段2（新会话执行）：冷启动建代码认知地图（方案b），步骤见 projects/locus-meta/docs/token-cost-implementation.md "冷启动"节。
- 计划（ROADMAP）：核实对照前期原理探索，确认已实现/缺失，时间待定。
- 遗留：过度思考 / 重复性工作 / agent 模式 system-prompt（见 projects/locus-meta/ISSUES.md）；read .env 收紧待定；locus_original 目录去留待定。
