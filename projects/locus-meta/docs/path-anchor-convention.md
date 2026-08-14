# 路径锚点约定

> 2026-08-14 定稿。修一个真 bug：记忆层指针在新会话里解析错。

## 问题

新会话默认工作目录是 locus 根（`/home/zhengyp/locus`）。而记忆层文件的指针写的是**相对工程目录的短路径**：

- `current.md` 写 `docs/token-cost-analysis.md`
- 实际文件在 `projects/locus-meta/docs/token-cost-analysis.md`

AI 按 cwd（locus 根）解析，拼成 `/home/zhengyp/locus/docs/token-cost-analysis.md` —— 该文件不存在。

## 根因

指针的"基准目录"没有约定清楚，依赖"读的人知道当前工程目录"这一隐式前提。但新会话从 locus 根启动：读 `active.md` → 进工程 `current.md`，cwd 仍是 locus 根，短路径全部落空。

以前没暴露，是因为 AI 读记忆时只把指针当文字、没真正去 open 文件；这次要"实施 token 方案"必须打开 docs 读细节，才第一次触发路径解析。

## 影响面

- 系统性：locus-meta 和 cogos 两个工程的 current.md / index.md / README.md 都有此问题。
- 本质：任何"AI 需要 open 才能拿到内容"的指针，都必须自包含（不依赖隐式基准）。

## 约定

1. **locus 内部文件指针**：一律从 locus 根写完整相对路径 `projects/<工程>/...`。
   - 例：`projects/locus-meta/docs/token-cost-analysis.md`、`projects/cogos/entries/2026-08-14-cogos-bugfix.md`。
2. **外部本体路径**：以"本体路径"为基准的相对路径，由各工程 README 顶部的"本体路径"字段声明基准（如 cogos 的 `~/codex/cogos`）。不属于本约定，不改。
3. **历史 tag 引用**：用 `git tag X \`path\`` 形式，path 相对该 tag 的仓库根（如 locus-original 的 `entries/...`）。不是当前树指针，不改。
4. **文档正文里的概念提及**（讲机制时提到 `entries/`、`current.md` 作为目录/概念）：不是活跃指针，不改。

## 判定口诀

"这个路径 AI 会不会去 open 拿内容？" —— 会 → 写完整相对路径；不会（概念 / 历史 / 外部基准）→ 保持原样。

## 本次修复范围

- 改：locus-meta + cogos 的 current.md / index.md / README.md 指针；cogos entries 内一处跨引用（`2026-08-12-cogos-setup.md` → bugfix）；locus-meta ISSUES.md 一处来源引用。
- 不改：CHANGELOG / ISSUES / ROADMAP 的历史条目（追加不重写）；docs 正文的概念提及；外部本体路径；历史 tag 引用。
