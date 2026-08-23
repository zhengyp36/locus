# Checkpoint 工作方法

> 本文件是 locus 的 checkpoint 规则,与 README.md 同级。规则不进 AGENTS.md。

## 目的

会话过长时,YZ 用 /undo 回退多轮消息释放上下文,由 AI 把关键上下文蒸馏进 checkpoint,重读即可无痛恢复,不必重新全量加载。

## 核心原则:checkpoint 落在 /undo 覆盖之外

/undo 回退的是 locus 工作区的文件变更 + 会话消息。checkpoint 的价值就是"跨 /undo 存活",故:

- checkpoint 正文写 `../checkpoint/`(locus 之外,/undo 不回退)。
- locus 内只留锚点(`scratch/README.md`、`scratch/checkpoint-rule.md`)指向该路径与本文。
- 本文是长期规则,随 locus git 固化(写完需 commit,否则同样被 /undo 回退)。

## 路径

活文档 `../checkpoint/`:

- `status.md` — 当前状态入口,新会话只读它 + `codebase.md`
- `codebase.md` — 代码认知基线,append 式累积
- `checkpoint-<N>.md` — 每步过程记录,N 递增
- `archive/` — 归档历史

固化快照 `projects/<工程>/checkpoint/`(定期 commit 进 locus git)。

## 触发

- 仅 YZ 明确指示时写(如"记录 checkpoint""整理草稿")。不主动写。
- YZ 说"读 checkpoint/status.md"时,读之恢复上下文。

## 写作结构

缺哪块写哪块:

1. 当前问题 — 一句话
2. 已做修改 — `文件:行` + 改点(非 diff 原文)
3. 已读代码要点 — `文件:行` + 关键逻辑一句
4. 关键结论/决策 — 含 YZ 拍板
5. 遗留/坑 — 报错要点、未解决项

## 写作要求

- 凝练可恢复,锚点优先,细节靠锚点重 `read`/`grep` 找回,不搬运原文。
- 代码/路径/变量/文件名用英文;讨论结论可中文。
- `codebase.md` 只记"对代码的新认知",append 式,只增不改旧结论。

## 固化节奏

- checkpoint 常驻工位目录,不随重启丢失。每个里程碑收口后,可把关键结论固化进 `projects/<工程>/checkpoint/` 并 commit(可选,便于跨工位共享)。
- 活文档(`../checkpoint/`)是唯一权威;git 内固化快照只增不改,单向覆盖(codebase.md 以活文档版为准)。
