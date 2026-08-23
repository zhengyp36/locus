# locus-meta

人与 AI 协作的方法论工程。

## 锚点

- 定位：locus 自身设计与方法论的落点，讨论"人与 AI 协作方法论"。
- 本体路径：无（locus 自身即本体）；remote: https://github.com/zhengyp36/locus。

## 已定结论

- 记忆/管理协议：极简记忆契约（指令两条、更新=重写、摘要+索引、细节入 entries；projects 分工程 + active 指针 + timeline）+ 两层模型（管理层=确定锚、除 CHANGELOG 外可重写需慎重；记忆层=类人印象；大写=管理/小写=记忆）+ 目录整理（顶层 README 给 AI、docs/ 为本体）。→ projects/locus-meta/entries/2026-08-14-locus-meta-structure.md + projects/locus-meta/docs/minimal-memory.md + projects/locus-meta/docs/design-v2.md
- 路径锚点约定：locus 内部文件指针一律从 locus 根写完整相对路径（projects/<工程>/...）；新会话 cwd 是 locus 根，相对工程目录的短路径会解析错。→ projects/locus-meta/docs/path-anchor-convention.md + projects/locus-meta/entries/2026-08-14-path-anchor-convention.md
- 认知地图方法论：目的优先 + 状态轴，代码是已实现子集；维护=AI 触发+人纠偏；验收=AI 验形式+人验实质；八节骨架 + 建图过程（口述→文档核对→偏差清单→人工裁决→代码核验→成图）。→ projects/locus-meta/entries/2026-08-14-code-map-revision.md + projects/locus-meta/docs/project-map-method.md
- 并行工作流：多工位（`~/work/<工位>/{locus,<外部工程>,checkpoint}`，总工位 main + 临时工位）+ 异步执行 + 记忆归并（人工在总工位归并，AI 合并时被一句话唤醒），工位间 git 合入；路径相对 locus 根（外部 `../<name>`、checkpoint `../checkpoint/`）；外部工程按需 clone；checkpoint 移出 /tmp 常驻。→ projects/locus-meta/entries/2026-08-23-parallel-workspace.md

## 下一步

- 通用方法论已定稿（projects/locus-meta/docs/project-map-method.md）；新工程建图按此法（AI 触发 + 人纠偏）。
- 并行工作流已落地（产物 `~/work/main/locus`）；下一步：弃用旧 `~/locus` 与 `~/codex/`、实测 `/undo` 边界（checkpoint 在 locus 外是否跨 /undo 存活）。
- 计划（ROADMAP）：核实对照前期原理探索，确认已实现/缺失，时间待定。
- 遗留：过度思考 / 重复性工作 / agent 模式 system-prompt（见 projects/locus-meta/ISSUES.md）；read .env 收紧待定；locus_original 目录去留待定。
