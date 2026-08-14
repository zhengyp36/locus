# locus-meta

人与 AI 协作的方法论工程。

## 锚点

- 定位：locus 自身设计与方法论的落点，讨论"人与 AI 协作方法论"。
- 本体路径：无（locus 自身即本体）。

## 已定结论

- 记忆契约：极简记忆方案（docs/minimal-memory.md）+ 工程化印象层结构（docs/design-v2.md）——指令两条、更新=重写、摘要+索引、细节入 entries；projects 分工程 + active 指针 + timeline。
- 两层模型（管理 vs 记忆）：工程管理层（README/CHANGELOG/ROADMAP/ISSUES，大写、确定、追加、不重写）vs 记忆层（current/index/entries，小写、重写、可乱）；CHANGELOG 人显式指出、阶段完成时更新；命名约定子工程内大写=管理/小写=记忆。→ entries/2026-08-14-locus-meta-structure.md
- 目录整理：顶层补 README（给人看，AGENTS 给 AI 看）；docs/ 定位为本体（可选）；目录结构按需生长，不预先设计。→ entries/2026-08-14-locus-meta-structure.md

## 下一步

- 计划（ROADMAP）：核实对照前期原理探索，确认已实现/缺失，时间待定。
- 遗留：过度思考 / 重复性工作 / agent 模式 system-prompt（见 ISSUES.md）；locus_original 目录去留、git remote 去留待定。
