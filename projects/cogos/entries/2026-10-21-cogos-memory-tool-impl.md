# memory 工具落码（2026-10-21）

> 状态：**已落码**（`d062f2e`，已 push）。承 `2026-10-20-cogos-memory-tool.md`（设计定案）＋ `directory-roots`（落点，YZ 拍板）。本件记落码期暴露的结构决策 + 验证 + 残留，不重复设计正文。

## §1 落码结论

- 代码三层照 body：`impl/memory.py`（`MemoryStore`，**直写 agent_root/memory/，不走 FsChannel**——那是 machine_root + terminal 会话的通道，memory 是意识层的文件读写代理）+ `memory_catalog.py`（3 能力数据）+ `memory.py`（`make_memory_spec` meta-tool，无 session）+ `tools.py::make_memory_specs`（3 impl ToolDef：`memory_fold`/`memory_unfold`/`memory_mark`）。
- **落点（YZ 拍板）**：记忆内容 = `config.memory_dir`（agent_dir/memory，平铺 `INDEX.md` + `<slug>.md`）；状态文件（profile.md/timers.json/segments.jsonl）下沉 `memory/state/`，新增 `AgentConfig.state_dir`（＝ memory_dir/state，代码名，对应「state root」）。
- 装配：`app.py` 建 MemoryStore、注册 impl、`exposed["memory"]`；**未进 `toolset_names`**（同 body，不接 loop，模型尚不可见）。

## §2 落码期决策（why）

- `slug(name)` = trim + 折叠空白 + ASCII 小写 + 空白转 `-` + 去 `/` `\` 及 `.` 前缀 + 截断 100；中文保留；INDEX 只存 name+description，反查文件名靠同一 slug（不冗余存 slug）。
- frontmatter `---<yaml>---` 包裹；`_split_frontmatter` 用 `rest.find("\n---")` 找闭合 → 正文含 `---` 往返无损（检视专项验证）。
- overwrite 撞名：保留 created_at/type/marked_at，更新 accessed_at + description，同步 INDEX 该行（按 slug 匹配）。
- 无并发（意识层单写者）；fold 先写记忆文件再改索引。

## §3 验证

- 全量 `pytest tests/` **1307 passed / 6 skipped**（`/usr/bin/python3.11`；系统 python 3.9 缺 cryptography 收集不到）。
- 提交前检视：git diff 自查 + 3 个 edge case sanity（多行 content 往返 / 描述含 `:` + overwrite 索引同步 / 正文含 `---`）。

## §4 残留（非 bug，设计取舍，留元层整理轮）

- slug 截断 100 后，两个前 100 相同的长名撞名（设计只说「长度截断」、未定截断撞名）。
- 名字含 `: ` 会让 `_parse_index_line` 的 `partition(": ")` 误拆（名字截到第一个 `: `）。
- overwrite 时若该条索引行已丢失，不自动补回（`if changed and out` 才写）。

## §5 遗留（范围外）

- 索引进上下文＝**装配层**职责（memory-tool §裁定），未落。
- 元层 LLM 整理维度（type）延后，type 恒 `default`。
- memory 未进 `toolset_names`（不接 loop）。

## §被否

- 走 FsChannel（machine_root + session 通道；memory 须落本地 agent_root、不依赖 terminal 会话）→ 新写 MemoryStore 直写。
- 给 memory 接 session（无 `needs_session` 能力）→ `make_meta_tool` 的 session 传 None。
