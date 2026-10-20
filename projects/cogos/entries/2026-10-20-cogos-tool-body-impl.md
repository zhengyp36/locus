# body 落码 · 代码组织与机制抽象（2026-10-20）

> 状态：**已落码**。承 tool-design §body（能力口径）＋ `scratch/2026-10-19-selfdrive-body-discussion.md`（前置讨论，已收口删除）。本件记**落码期暴露的结构决策**——工具代码如何组织，是 tool-design 设计层的下游。

## §1 代码组织三层（共识）

1. **通用机制一个文件**（`tool_base.py`）：`ToolDef` / registry / validate 等。
2. **每工具一个文件**（body/memory/file 各一）：能力数据 + 封装。
3. **底层实现 `impl/` 复用**：`FsChannel` / terminal / phone / image_ctx 等底层，body 与 toolbox 共用。

历史演进链（非一次性设计）：工具平铺 → prefix cache 失效 → 收成单 meta-tool `toolbox` → 需要能力目录路由长出 `catalog.py` → 模型可见参数 ≠ 实现参数长出 `Capability`（model-facing params + impl 绑定 + arg_map）。**两条硬约束**：① prefix cache；② 实现面/模型可见面隔离。

## §2 catalog 拆「机制 vs 数据」

- **机制**（`catalog.py` 只剩机制）：寻址/校验/绑定/渲染 help——`Catalog` 类（数据注入）+ `Capability`（去 label、notes 泛化为 FACE_NOTES）；职责＝能力树查询（resolve/children）+ help 渲染（help_for）+ 启动校验（assert_bound/bindings_for_face），纯读不执行。
- **数据**：`toolbox_catalog.py` / `body_catalog.py`，各建一个 `Catalog` 实例（能力内容 path/summary/params/impl/arg_map）。
- body 与 toolbox **复用同一机制、注入不同数据**；body_catalog 由 toolbox_catalog 投影派生（见 tool-design §判定）。

## §3 meta-tool 机制

- `make_meta_tool(name, schema, prompt, catalog, registry, session)`：help/call 入口 + 调用链加工（validate → arg_map → 注入共享 session → registry.call → 隐藏 id）。
- **help 目的＝藏工具**：平铺则 token / prefix cache / 选择负担都压不住；body/toolbox 都是 meta-tool（一个工具名，help/call 展开多用法）。
- **help 统一语义**：`help(prefix)` = 子树一览（非叶子）/ 叶子详情；一览 + 逐级是同一机制在不同前缀粒度。
- **工具结果当轮有效、跨轮消失**：当轮 = 同一 flow（tool 结果 append 进当前 material）；跨 flow 重建 material 即消失。
- **body 精简入口 + 显式指路 toolbox 全集**：body 每组只留核心，help 里写明"更多见 toolbox.xxx"，解决子集重叠的选择困难。
- 一览渲染约定：叶子行 `name: summary`；组标题 `- <id>: <desc>`；头（group/face）永不截断，叶子按组设上限 N（默认 20）超出 `… (+K more; help(<path>) to list)`；备注只在聚焦视图尾部渲染。

## §4 用法缓存 vs 工具经验（两条线，不混）

- **用法缓存**：退化为**当轮内修剪**——只留用过的那条用法、其余自动消失，**非跨轮 LRU**（修正 tool-design §body 早期"最近用法缓存（条数上限，LRU）"口径）。
- **工具经验**：长期，另一条线，agent 自己 `fold` + `keep` 进 memory（依赖 memory 工具，未落码）。

## §5 形状自证 > 标签声明

`time_form`(sync/async) **去掉**：无执行逻辑依赖（所有调用皆 `await tool.fn(...)`），仅剩声明校验与 help 渲染一行。其职责由**工具形状自证**承担：返回 `job_id` 回执 + `xxx.done` 事件 + `cancel` + `observe`/`browse` 取结果，即"异步作业闭环"齐全；再由三动词判据（read/browse/observe）内化"结果怎么取"。`ToolDef` 随之只剩 schema/fn/prompt 三项。此判例后续复用（见 content-access 的 `Capability.root` 被否）。

## §6 落码 commit 链

- Step 1 · catalog 抽取 `81e4c26`：`Catalog` 类 + `toolbox_catalog` 数据 + 去 label + 统一 help。
- Step 2 · meta-tool 抽取 `0e60992`：`make_meta_tool`；`needs_session` 搬进 `Capability`；共享 session 注入；纯重构。
- Step 3 · body 落码 `b3273b4`（label/overview）+ `3546acf`（body 首批 8 能力：chat.speak / file.read·write·edit / terminal.run·observe·send·interrupt）；`DefaultSession` 提为公共机制；`replace_all` 去掉（impl `fs.edit` 无此参数，暴露即陷阱）。
- 后续：body.vision `675a906`、web 重实现 `e5dbcda`、spool 删除 `e003135`、chat.browse `dfd07a5`（各见对应 entry）。

## §被否

- **body 平铺**（每个 `body.xxx` 一个 schema 常驻 tools 数组）：被"藏工具"硬约束否决，body 也是 meta-tool。
- **`time_form` 标签**：被"形状自证"取代（§5）。

## 待裁（不阻塞，进 current 开放问题）

- body/toolbox 暴露关系（`[toolbox]` vs `[toolbox, body]` vs `[body]`）。
- `render_overview` 仍中文（system-reminder 层）。
- 记号表不统一（点号路径 / `FIG:`/`WEB:`/`TERM:` / `t{sid}`）。
