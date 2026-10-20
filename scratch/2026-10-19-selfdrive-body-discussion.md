# 自驱 agent · body 工具开发前置讨论（2026-10-19）

> 状态：**执行中（scratch，未收口）**。Step 1（catalog 抽取）/ Step 2（meta-tool 抽取）/ Step 3（body 首批落码）**已落码**：`b3273b4` / `3546acf`（body 首批 8 能力）。**10-20 body.vision 已落码（`675a906`）**；**10-20 web 重实现 + 删 draft/transfer 已落码（`e5dbcda`，tag `pre-prune-draft-transfer`）**：web 5 能力（search/fetch/browse/cancel/close）为 `WEB:<id>` + `work_dir/web` 缓存目录，body 现 16 能力。**待续**：memory 工具、spool 删除 + phone 下载改造（下一轮）、chat.browse（归 phone 消息缓存落点轮）、body/toolbox 暴露关系（待裁）。收口时蒸馏进 `entries/`、钉术语（撞名/新词）、回写 `current.md`。承 `entries/2026-10-19-cogos-tool-design.md` 的「已定 vs 待定」。

## 背景

工具先行：先落 body/toolbox/memory 工具，再谈「意识过程→记忆沉淀」。本轮聚焦 **工具代码如何组织**，作为 body 落码的前置准备。

## 现状代码组织（为何这样）

三层：实现层 `tools.py`（`ToolDef` + 各 `make_*_spec`）/ 目录层 `catalog.py`（`Capability` + `help_for`/`resolve`）/ meta-tool 层 `toolbox.py`。

**历史演进链**（不是一次性设计）：
1. 早期工具平铺 → tools 数组随工具集变化 → **prefix cache 失效**；
2. 收成单 meta-tool `toolbox`（schema 常量，能力不进 tools 数组）→ 靠 `help` 发现；
3. meta-tool 需要"能力目录"路由 help/call → 长出 `catalog.py`；
4. 模型可见参数 ≠ 实现参数（终端 session id 不外泄、`to`→`target`）→ `Capability` 带 model-facing `params` + `impl` 绑定 + `arg_map`。

**两条硬约束（真实）**：① prefix cache；② 实现面 / 模型可见面隔离。

**包袱（非最终态）**：`tools.py` 单文件塞全部实现工具；schema/文字散落、中英混杂；`catalog` 是硬编码数据而非机制；通用机制（`ToolDef`/`ToolRegistry`/`validate`）分处 `tools.py` 与 `toolbox.py`。

## 新组织（共识）

1. **三层**：通用机制（一个文件）｜每工具一个文件（body/memory/file 各一）｜底层实现 `impl/` 复用。
2. **catalog 拆机制 vs 数据**：寻址/校验/绑定/渲染 help = 机制；能力内容（path/summary/params/impl/arg_map）= 数据。body 与 toolbox 复用同一机制、注入不同数据。
3. **文字集中 + 全英文**：schema/prompt/description 抽模块级常量；机制层全英文（交流语言由场景决定）。
4. **意识层 tools = [body, memory]**，元层 tools = [file]。

## meta-tool 语义（共识）

- **body / toolbox 都是 meta-tool**：一个工具名，`help`/`call` 展开多用法。
- **help 的目的 = 藏工具**：平铺则工具无法藏（token、prefix cache、选择负担都压不住）。
- **help 统一语义**：`help(prefix)` = 子树一览（非叶子）/ 叶子详情；一览 + 逐级是同一机制在不同前缀粒度，不是两个模式。点号路径由 schema description 的 example（`computer.command.run`）教给模型。
- **工具结果当轮有效、跨轮消失**：当轮 = 同一 flow（runtime 把 tool 结果 append 进当前 material；跨 flow `consciousness.on_message` 重建 material 即消失）。**只留用过的那条用法**（缓存），其余自动消失。
- **body 精简入口 + 显式指路到 toolbox 全集**：body 每组只留核心（如 `body.chat` 仅 speak/browse），help 里写明"更多见 toolbox.communication"，解决 body/toolbox 子集重叠的选择困难。

## 用法缓存 vs 工具经验（两条线，不混）

- **用法缓存**：退化为**当轮内修剪**——只留用过的那条用法、其余自动消失，非跨轮 LRU；工具结果「当轮有效」扩展到大多数工具。
- **工具经验**：长期，另一条线，agent 自己 `fold` + `keep` 进 memory。

## 关键判定

- **`time_form`(sync/async) 去掉**：无执行逻辑依赖（所有调用皆 `await tool.fn(...)`），仅剩声明校验与 help 渲染一行。其职责由**工具形状自证**承担：返回 `job_id` 回执 + `xxx.done` 事件 + `cancel` + `observe`/`browse` 取结果，即"异步作业闭环"齐全；再由三动词判据（read/browse/observe）内化"结果怎么取"。**形状自证 > 标签声明**。`ToolDef` 随之只剩 schema/fn/prompt 三项。

## 待裁（后续，不阻塞）

- body 参数细节：`body.chat.speak(to, text)` 的 `arg_map={to:target, text:content}` 双重改名；`body.file.edit` 的 `replace_all?` 已裁（10-20）：去掉（impl `fs.edit` 无此参数，暴露即陷阱）。
- body/toolbox 暴露关系（`[toolbox]` vs `[toolbox, body]` vs `[body]`）。
- `render_overview` 仍中文（system-reminder 层）。
- 记号表不统一（点号路径 / `FIG:`/`WEB:`/`TERM:` / `t{sid}`）。

> 原「LRU 条数上限」悬置已解除：缓存退化为当轮内修剪（只留用过的那条用法），非跨轮 LRU。

## 动手顺序：轻整理已完成，先抽 catalog 机制

### 轻整理（2026-10-19 完成）

三动作全落地：`tool_base.py`（通用机制）／`toolbox.py`（meta-tool 模板）／`time_form` 删除。存量文字已全英文（toolbox/catalog/tools，仅 `@原图` 为 image_ctx 固定记号）。验证：工具层 4 测试 + 全量 `pytest` 全绿（1298 passed / 6 skipped，需 python3.11）。

### 开发 body · 已定方案与落码顺序（2026-10-19 收口）

**机制抽象（三层，已定）**：

- **catalog 机制**（`catalog.py` 只剩机制）：`Catalog` 类（数据注入）+ `Capability`（去 label、notes 泛化 FACE_NOTES）；职责 = 能力树查询（resolve/children）+ help 渲染（help_for）+ 启动校验（assert_bound/bindings_for_face），纯读不执行。
- **meta-tool 机制**（`meta_tool.py`）：`make_meta_tool(name, schema, prompt, catalog, registry, session)`；职责 = help/call 入口 + 调用链加工（validate → arg_map → 注入共享 session → registry.call → 隐藏 id）；使用 catalog，不反向依赖。
- **数据模块**：`toolbox_catalog.py`（现在）/ `body_catalog.py`（以后），各建一个 `Catalog` 实例；body/toolbox 独立不耦合，只差数据规模。

**一览渲染约定（已定）**：

- 叶子行 = `name: summary`（复用 summary，不加新字段）；组标题 = `- <id>: <desc>`（去 label）。
- 头（group/face）永不截断；叶子按每个头下清单设上限 `N`（默认 20），超出 `… (+K more; help(<path>) to list)`。
- 备注只在聚焦视图（`help(<path>)`，path 恰为 note 路径）尾部渲染；叶子详情不变（path/summary/Params/Returns）。

**落码顺序**：

1. **Step 1 · catalog 抽取**（✅ `81e4c26`）：`Catalog` 类 + `toolbox_catalog` 数据 + 去 label + 统一 help；`toolbox.py` 只改 import/访问；改 `test_catalog`。
2. **Step 2 · meta-tool 抽取**（✅ `0e60992`）：`make_meta_tool`；`needs_session` 搬进 `Capability`（现为 toolbox 里 `_NEEDS_SESSION` 路径集）；共享 session 注入；纯重构不改行为。
3. **Step 3 · body 落码**（✅ `b3273b4` label/overview + `3546acf` body）：首批 `chat.speak` / `file.read·write·edit` / `terminal.run·observe·send·interrupt`（零新底层能力）+ `body_catalog`。`DefaultSession` 提为公共机制（`meta_tool.py`），body/toolbox 共享同一默认 session；`replace_all` 去掉。暴露关系未动（`toolset_names` 仍 `["toolbox"]`，body 挂 registry 但未模型可见）。

**内容层（已定稿，随 body 落码）**：

- body 5 组内容与参数（收口件 §19-47 已定稿）；body 精简入口、help 指路 toolbox 全集。
- memory 四操作正交（fold/unfold × keep/forget）+ 位置即强度 + 规模演化。
- 句柄 FIG / WEB / TERM；异步作业闭环（web：search/fetch→browse/cancel/close；terminal：run/observe/interrupt）。
- 截断机制（总量上限 + `truncated`）。
- 经验缓存（工具经验）：长期，agent 自己 fold+keep 进 memory（依赖 memory 工具）。
- 附件投影三档：内联（小内容持久）/ 附件（当轮有效）/ 指针（只给句柄）；主动拉取→附件、被动推送→通知+指针。
- `tools.py` 拆文件随 body 落码顺带做。

## 被否

- **body 平铺**（每个 `body.xxx` 一个 schema 常驻 tools 数组）——被"藏工具"硬约束否决，body 也应是 meta-tool。
- **`time_form` 标签**——被"形状自证"取代。
