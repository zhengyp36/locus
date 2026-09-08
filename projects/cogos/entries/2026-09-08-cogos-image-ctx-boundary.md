# 2026-09-08 cogos image_ctx：P1 落码 + 职责边界定案

## P1 原始层落码完成（09-08 晚）

- 模块：`cogos/image_ctx/{view.py, domain.py, render.py, tools.py}`（+ `__init__.py`）。
  - `view.py`：Window/Annotation/View + 坐标换算（`view_to_window`/`window_px`/`clamp_rect`/`clamp_window_to_src`/`window_key`）。
  - `domain.py`：Domain（三层存储 images/cache/desc）/Source 图根/去重表 + `add_src`（path 幂等 + images 副本 + md5）。
  - `render.py`：`fig_key` 指纹 `(path,window,annos)` + `render`（crop + 主动降采样 + cache 命中复用）。
  - `tools.py`：`load`/`view` 原语 + Block + `meta_annotation`（越界 `> ⚠️ clamp:` 标注）。
- 测试：`tests/image_ctx/`（conftest + test_p1.py，18 项）。P1 checklist 逐条勾（MUST HAVE 10 + MUST NOT 3）；`detail=original` 属请求层，按规格 §7-3 归 P2+。
- 验证：image_ctx 18 test 全过；项目全量 pytest **955 passed**；无禁区 API（load_many/restore/get_progress 无）；windows.png(1357×764) 探针：`@窗口≡@全图` center 精确、全图主动降到 800×450、越界只取有效区不补边。
- 小坑（已修）：`fig_id` 存的是裸 id（如 `1000`），引用 token 为 `FIG:1000`、元注解标签 `F:1000`——若把前缀存进 fig_id 会导致 `parse_ref` 剥前缀后找不到。

## 职责边界定案（YZ，勿越界）—— 本 entries 重点

**图模块不越界管上下文/K 轮**：`image_ctx` 只管图对象状态（View/Source/Domain、坐标、去重、渲染、anno 编辑），**不管**上下文组织/`earliest_fig_turn`/K 轮寿命/图块散落/薄状态行/摘超龄图块。

- 上下文/K 轮/compile 是**另一个程序（上下文管理器，cog-runtime 编译层）**的事。
- 依赖方向：上下文管理器 → 调 `image_ctx` 接口；图模块**不反向感知**轮次/历史/当前轮。
- `image_ctx` 暴露给上下文管理器的接口面：
  - `load/view/draw/move/delete_anno`：各产一个**图块描述（Block）**，上下文管理器接收后放历史、记轮次、管寿命。
  - `fig_meta(fig_id)`：渲染元注解（供薄状态行/重载锚用）。
  - `clear_fig_block(fig_id)`：清空该视图 annos / 标记图块失效——**上下文管理器在摘超龄图块时调用**。「何时清」归上下文管理器，「怎么清」由图模块做。
- **LIVE 生命周期落到 P2**：anno 的「超龄清空」不再由图模块自己判轮次——上下文管理器摘图块时调 `clear_fig_block` 触发；「重载带回/清空」由上下文管理器决定走复用 registry 视图（annos 保留）还是新图块，图模块只保证 View 上 annos 是瞬态。
- **设计 §10 修正**：原草案把 `window.py(earliest_fig_turn)` / `compile.py(上下文文法)` 放进 `image_ctx` **作废**，这两块归上下文管理器。工程本体 `design-vision-image-fields.md` §10 已更新。

## P2 定位层落码完成（09-08 续，小原型先行）

- 先做**anno 像素叠加小原型**（`/tmp/kilo/vision/anno_proto.py`）验证正确性：核心换算 = 位图像素 = `@窗口` 坐标 × 位图尺寸（窗口整体缩放，相对位置不变，与 scale/窗口盒绝对位置无关）。程序断言全过（rect/ellipse 精确、cross 误差<1px），视觉核对十字压在 windows.png「工具(T)」上——程序 + 视觉**双确认无问题**。
- 实现要点：`render` 改为**自绘 annos**（crop+主动降采样+`draw_annos`+save，保留 budget 检查）；因 anno `kind` 有 7 种而 img_tool 只支持 star/rect，在 image_ctx 内自建年标注绘制（不改 img_tool，符合"独立模块"）。
- 新原语：`draw/move/delete_anno/clear_annos` + `resolve_anno` + 越界 `_clamp_anno_pts`（clamp 到 [0,1]）+ markdown 高亮 `> ⚠️ **ANNO:n 已 clamp 至 FIG:x 边界**` + `clear_fig_block`（上下文管理器摘图块调清空）+ `fig_meta`。
- `pts` 输入宽容：接收扁平单点 `[u,v]` 或 `list[list]`（`_norm_pts`）。画作细节：`Annotation.id` 存裸 `ANNO:<n>`，`meta_annotation` 加 `标注: {id} {kind} @窗口 (...)... {color}`。
- 测试：`tests/image_ctx/test_p2.py`（12 项，draw/move/delete/clamp/指纹/瞬态/作用域/像素落位），P2 checklist 全勾（MUST HAVE 7 + MUST NOT 3）；项目全量 pytest **967 passed**（含 P1 18）。

## P3 上下文落码 + P4 去重（09-08 晚续，handoff-7）

- **P3 上下文编译层**：`cogos/cog_ctx/`（`context.py` + `manager.py` + `__init__.py`）。
  - `FigContext(compile/strip)`：纯原语。`compile(FigureAct)` 把一次图工具调用（`{op, fig_id, note, status(ok|warn|error), block, detail}`）编成一条定格式消息（元信息锚 + 标注 + `> ⚠️` 异常 + 分段线 + `你的备注:`）；`strip` 只摘图块、text 零改动。**不感知 agent/人/轮次、不做 K/剪龄决策**。
  - `FigContextManager(domain, k=4)`：外层**管理者**，持有 `step`/`k`/`live deque`；`next(act)`=有图轮（推进步 + 老化 + 编消息 + 登记活块），`advance()`=纯文字轮（只推进 + 老化）；`_age()` 从队头摘 `step 差 > k` 的图块（strip）+ 调 `image_ctx.clear_fig_block` 清该 FIG 最后活块的 annos。
  - `FigureAct/FigMessage/compose_figure_text`。测试 `tests/cog_ctx/{test_p3.py, test_manager.py}`。
- **P4 去重**：Source 身份层（同 path 幂等 / 同 `(path,window)` 同 FIG_ID / 跨 path 像素相同不合并），`tests/image_ctx/test_p4.py`。
- 全量 pytest **992 passed**（P1+P2+P3+P4）。

## 坐标基准统一 + P3 目的层探针（本会话 handoff-8 收口）

- **坐标基准统一（size over 各自维度）**：`window_px`/`px_rect_to_window`/`view_to_window` 的 size 分母从 `short_side` 改 `orig_w`/`orig_h`（宽对宽、高对高）；`domain.py` 全图窗口 `size=[1.0,1.0]`。新不变式：全图窗口=干净 `s(1.000,1.000)`；**参考图=全图时 `@窗口 ≡ @全图` c/s 逐位一致**（无换算）。旧「÷短边」在横向图（windows.png 1357×764）把宽稀释 56%。
- **P3 目的层 LLM 探针**（`/tmp/kilo/vision/p3probe/`，非仓库）：
  - `taskA.py`（任务A）：只给锚文字（无图、带坐标教学）→ 模型重建窗口 → 回放 delta 全 0。
  - `taskB.py`（任务B）：真实 `FigContextManager(step/k/live)` 走老化（一图轮 `next` + 连续 `advance` 至超龄）→ 验证图被摘/text 留底/annos 已清 → 只给幸存锚文字（**无图、无坐标教学**，用真实 `SYSTEM_HINT`）问重定位 → 回放 delta 全 0。**口径①（纯锚、无规则）就过**——证明锚自含。
  - `probe138.py`（§138 换算精度）：纯几何，全图 ref 上 `@窗口→@全图` delta≈0、实际下发像素偏差 0.56px（亚像素）、目标工具T(0.188,0.042) 仍覆盖、无短边失真；45 窗口回环最大 0.56px。
- **checklist 回勾**（本会话）：§0 行为 6 项 + §0 禁区 3 项 + `文字预算摘要`（取消）+ 残留待核 `§138`（probe138 过）、`§139`（taskB 过）。P1~P4 原有 `[x]` 未动。
- **遗留（本会话）**：坐标规则动态注入暂缓（静态前置照旧）；`desc/` canonical 层未落盘；超龄回收（Source.registry/cache 积压）未做；待实测 3 项（A-B 元信息短序 / 图像 token 纯尺寸函数 / 超限行为固化）未测。
- **已交接** `checkpoint/principle-exp/handoff-vision-image-fields-8.md`（下一步=**衍生推理档**：用锚做新相对窗口，检验坐标教学必要性）。
