# memory 工具设计收口（2026-10-20）

> 状态：**已定案、待落码**（含 §实现方案，10-20 补充定案）。承 `scratch/2026-10-20-memory-tool.md`（/undo 后草稿）＋本日讨论。术语权威＝`glossary.md`（fold/unfold、mark、overwrite、type、keep/forget〔废弃〕）。
> 落码前置（已定，见 `directory-roots`）：存 `agent_root/memory/`（归元层 LLM）；意识层不可见物理路径，只经 memory 工具间接访问。

## §1 意识层 API（三操作 + 一个布尔）

```
memory.fold(name, description, content, overwrite=false)
memory.unfold(name)
memory.mark(name)
```

- 意识层只这三个操作；排序/两段/抽样/挤出/淘汰在机制层，意识不感知。
- 命名保留 fold/unfold（承载"概念组织"语义），**不改成 create/access/update**（CRUD 名把记忆降格为 KV 存取，且让模型承担"名字存不存在"的判断——那是机制细节）。

## §2 操作语义

- **fold**＝意识命名＋机制收拢两面：写 `<name>.md`（name＋description＋content，时间戳落 frontmatter）＋索引区加一行（name＋description）。去重＝索引区查 name（归一化 trim＋lowercase 防假撞名）。
- **unfold**＝读 `<name>.md` 全文展开进上下文＝"取即写"最小落地（记 `accessed_at`）。
- **mark**＝标重要，幂等升格（已标不再作用），只改 `marked_at`；语义＝**提示非保证**（标了更容易被想起/保留、不承诺永久）。

## §3 撞名（核心机制）

- fold 撞名（名字已存在）：
  - `overwrite=false`（默认）→ 提示撞名，**回显该条索引（name＋description）**，不覆盖。撞名＝索引重新进上下文（模型可见旧锚，可 unfold 看全文再决定）。
  - `overwrite=true` → 覆盖写同一文件。
- **不加独立 update 操作、不加 force 参数**：一个 fold 动作覆盖"新建"和"更新"两种结果，机制分流（撞没撞名），模型不用声明 create/update。
- 回显只给一行 description，**不给全量旧内容**——避免"撞名→看全量→重新整理→再 fold 同名→又撞名又回显"的冗余循环。

## §4 时间戳三字段（frontmatter，将来机制原料）

| 字段 | 写时机 | 将来用途 |
|---|---|---|
| `created_at` | fold 时写一次 | 条目身份 |
| `accessed_at` | 每次 unfold 更新 | recency / 淡出 / 抽样权重 |
| `marked_at` | mark 时写，可空 | 重要性 / 两段 / 挤出 |

三字段＝"位置即强度"的最小原料，排序纯派生、可重建。

## §5 索引区长驻

- 索引区＝一行一条 name＋description，长驻上下文（模型由此知道所有名字）。
- fold 不即时改当前上下文的索引区（模型能看到自己刚 fold 的）；重载上下文时加载最新索引。
- 撞名只发生在索引区超 K 没全量加载时，且撞名本身把该条索引重新带进上下文。

## §6 给模型的规则（写进 fold schema description）

1. 发现记忆错 → 用 `fold(overwrite=true)` 改写为正确，改写时**保留"以前错＋现在对"**（转变落地，不物理删）。
2. `[[name]]` 是 content 内**纯文本标记**（提醒模型相关记忆/值得记的点），**机制不解析、不检查存在性**——claude code 亦未解析链；链可留、不必解析。

## §7 维度（type 字段，延后到 N>K）

- 采用**方式 B**：意识层不长维度、fold 无 type 参数；机制层/元层 LLM 整理时分析近期访问记忆（内容关系＋访问共现）长出维度，意识完全不感知。
- type 是**机制层字段**：fold 时写 `default`，元层 LLM 整理时可给维度、也可不给。
- why 方式 B 而非"意识标 type"：① memory-dynamics 原始口径＝"意识无意踩路、机制记路"；② 形状自证＞标签声明（意识标 type 是声明、可能是噪音，维度应从访问行为涌现）；③ 元层 LLM 已有"整理记忆"职责，正好复用。
- 规模演化（scratch §5，候选、不实现）：单维位置 → 经历挂钩 → 主题簇（簇＝主题＝维度，从相关性涌现）。

## §被否

- **forget 操作**：模型无主动降权动机，淡出/挤出交机制自动。
- **keep → mark**：记忆轴收为单向 mark（命名）。
- **四操作正交 → 三操作**（fold/unfold/mark）。
- **delete 操作**：物理删除与"记忆＝思考的痕、转变物化、淡出非删除"冲突；纠错精神由 overwrite＋记旧错新对承载，非删除形式。
- **create/access/update 命名**：CRUD 名降格为 KV 存取、让模型承担存在性判断；access 撞"内容访问统一"语境。
- **fold(mode="create|update|delete")**：mode 三值冗余（create/update 差异＝名字存不存在，机制分流即可；delete 语义怪）。
- **意识层标 type 枚举**（含照搬 claude code 的 user/feedback/project/reference）：预置固定清单 vs 维度用进废退；description 已承担 recall 相关性职责。
- **撞名自动覆盖＋回显全量旧内容**：盲目覆盖丢内容 + 回显循环冗余 → 改为"提示撞名＋回显索引（一行）＋不覆盖"。

## §借鉴 claude code（采纳 vs 拒绝）

- 采纳：frontmatter 作元数据载体；`[[name]]` 悬空引用合法＝待写标记；"只记 non-obvious"卫生规则；"回忆的记忆可能过时、先 verify"（注入防护呼应）。
- 拒绝：type 四分类（预置固定清单）；"发现错就删除"（改 overwrite＋转变）。
- 已有对应物：MEMORY.md 索引＝索引区；"不存 repo 已记录"＝外部介质三分。

## §实现方案（10-20 定案）

### 文件布局（`agent_root/memory/`，平铺）

```
agent_root/memory/
  INDEX.md          # 索引区：一行一条 name + description（长驻上下文内容源）
  <slug>.md         # 每条记忆一个文件
```

平铺、与 claude code 一致；索引文件固定名 `INDEX.md`，记忆文件用 slug 命名，二者可区分。

### slug = 确定性映射（索引不存文件名）

- `slug(name)` = trim + 折叠连续空白 + ASCII 小写 + 空白转 `-` + 移除 `/` `\` 及 `.` 前缀（防路径穿越）+ 长度截断；中文保留（UTF-8 文件名合法）。
- 撞名判断用 slug（归一化后比较）。
- INDEX.md 只存 `name + description`（模型可见）；反查文件名靠同一 `slug(name)`，不冗余存 slug。

### INDEX.md 格式

```
- <name>: <description>
```

一行一条，模型长驻可见；无 frontmatter、不存内容。

### frontmatter schema（`<slug>.md`）

```markdown
---
name: <原始 name>
description: <一行描述>
type: default
created_at: <ISO-8601 UTC>
accessed_at: <ISO-8601 UTC>
marked_at: <ISO-8601 UTC | null>
---

<content 正文，含 [[name]] 纯文本标记（不解析）>
```

### 三操作数据流

**fold(name, description, content, overwrite=false)**
1. `slug = sanitize(name)`
2. 文件不存在 → 新建：写 frontmatter（created_at=accessed_at=now、marked_at=null、type=default）＋content；INDEX.md 追加一行。返回"已新建 <name>"。
3. 文件存在（撞名）：`overwrite=false` → 返回"撞名：<name>: <description>（已存在，未改动；unfold 查看，或 overwrite=true 覆盖）"；`overwrite=true` → 覆盖 content，保留 created_at、更新 accessed_at=now，INDEX.md 该行 description 同步。返回"已更新 <name>"。

**unfold(name)**：不存在 → 报错"记忆不存在：<name>"；存在 → 读文件返回元数据＋content 全文，更新 accessed_at=now。

**mark(name)**：不存在 → 报错；已标 → 幂等 no-op 返回"已标过"；未标 → 写 marked_at=now 返回"已标 <name>"。

### 原子性与并发

MVP 只有意识层单一写者（串行），无并发；fold 先写记忆文件再改索引。元层 LLM 整理（加维度 type）未落，暂不考虑交错写。

### 归属层边界

- 意识层：只经 fold/unfold/mark 三工具间接读写，看不到物理路径。
- 元层 LLM（将来整理维度）：直接读写 `agent_root/memory/` 文件。
- 两者都动 memory/，方式不同——意识层走工具接口，元层走文件；memory 工具的 impl 即"意识层的文件读写代理"。

### 代码组织（沿用 tool-body-impl 三层）

- `memory` 工具一个文件（三 capability 能力数据＋封装）
- 底层 `impl/` 新建 memory 文件读写（或复用 `FsChannel`）
- 索引维护（INDEX.md 追加/更新）是 impl 职责，意识层不感知

### 默认倾向（已定，可改）

索引文件名 `INDEX.md`、时间戳 ISO-8601 UTC、平铺不分子目录。

### 裁定（10-20 补充）

- content **不设上限、不提示抄原文**（机制设计不以"假定模型会做什么"为前提写防御提示）。
- unfold/mark 撞不存在 → 只报错，不提示"是否新建"。
- `[[name]]` 纯文本、机制不解析（见 §6）。
- 索引区"长驻上下文"是**机制层（装配）**职责，不在工具层落码范围。
