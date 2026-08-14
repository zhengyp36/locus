# 路径锚点约定（2026-08-14）

记忆层路径指针不自包含导致的解析 bug。

## 根因

- 记忆层指针写"相对工程目录的短路径"（`docs/xxx.md`），但新会话 cwd 是 locus 根，短路径解析落空（拼成 `/home/zhengyp/locus/docs/xxx.md`）。
- 以前没暴露：AI 读指针不当真、没去 open；这次要实施 token 方案、必须真 open docs 读细节，才触发路径解析。

## 结论

- 约定：locus 内部指针一律从根写完整相对路径 `projects/<工程>/...`；外部本体路径以各 README 顶部"本体路径"字段为基准；历史 tag 引用（`git tag X` 限定）与文档正文的概念提及不改。
- 判定口诀：AI 会不会去 open 拿内容？会 → 完整相对路径；不会 → 保持原样。
- 规范：projects/locus-meta/docs/path-anchor-convention.md

## 本次修复清单

- locus-meta：current.md / index.md / README.md 指针；ISSUES.md 一处来源引用。
- cogos：current.md / index.md 指针；entries 一处跨引用（`2026-08-12-cogos-setup.md` → bugfix）。
- 落位：CHANGELOG 追加一条；docs 新增 path-anchor-convention.md。
