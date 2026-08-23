# 并行工作流（2026-08-23）

人与 AI 串行协作（讨论 → AI 执行 → 人等结果，全程排队）改为并行化。

## 问题

串行协作：讨论、执行、等待串成一条线，人等 AI 执行、AI 等人决策，效率低。

## 核心模型

并行化 = 多工位（自包含目录）+ 异步执行 + 记忆归并，工位间靠 git 合入。

## 布局与路径

- `~/work/<工位>/{locus, cogos, checkpoint}`；总工位 `main`，临时工位 `A`/`B`/任务名。
- 路径全部相对 locus 根：外部工程 `../<name>`，checkpoint `../checkpoint/`，clone 后路径自动自洽。
- 外部工程按需 clone：clone 工位只 clone locus；用到某外部工程才 `tools/external-clone.sh <name>`。

## checkpoint 移出 /tmp

放工位目录 `../checkpoint/`，常驻不丢；固化节奏从"必须"改"可选"。

## 记忆归并

人工在总工位完成，AI 平时无感知、只在合并时被一句话唤醒；规则放 locus-meta，不进 AGENTS.md。

## 代码合并

走标准 git：rebase → 解决本次冲突 → push；冲突大说明任务切分低估了耦合。

## 落地

三个 commit（github zhengyp36/locus）：`4c876f2`（active 切 locus-meta）、`7ecac70`（workspace 布局 + 路径相对化）、`1d63e45`（外部工程按需 clone）。产物在 `~/work/main/locus`。

## 遗留

- `~/work/A` 验证工位未删（`rm -rf` 被权限规则拦截），保留作样例，可自行删。
- 旧 `~/locus`、`~/codex/` 弃用待 YZ 定。
- `/undo` 边界未实测：新布局 checkpoint 在 `../checkpoint/`（locus 之外）是否跨 /undo 存活待验证。
