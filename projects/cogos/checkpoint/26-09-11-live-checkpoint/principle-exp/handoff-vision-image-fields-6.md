# handoff｜视觉图组织/引用 → P1+P2 已落码（image_ctx）+ 职责边界定案 → 下一步 P3 上下文（09-08 晚收口）

> 2026-09-08 晚。上游：`handoff-vision-image-fields-5.md`（P1 规格 + 两项拍板）。**本会话完成 P1 落码 + P2 定位层落码（小原型先行验证），并经 YZ 定案「图的职责不越界」**。新会话只读本文件即可接手；接口/细节以本体 `design-vision-image-fields.md` 为准，验收以 `design-vision-image-fields-checklist.md` 为准，P1 落码以 `design-vision-image-fields-p1-spec.md` 为准。

---

## 一句话状态

- **P1 原始层 + P2 定位层均在 `cogos/image_ctx/` 落码完成并通过验收**；`image_ctx` 30 test + 项目全量 pytest **967 passed** 无回归；P1/P2 checklist 逐条勾。**「图的职责不越界」已由 YZ 定案（重点，勿踩）**：`image_ctx` 只管图对象状态，上下文/K 轮/compile 归上下文管理器。**下一步 = P3 上下文编译层（新模块，非 image_ctx），把图块注入模型上下文。**

---

## 本会话产出（新会话必须知道）

### 1. P1 原始层落码 `cogos/image_ctx/`（P1 checklist 全勾）
- `view.py`：Window/Annotation/View + 坐标换算（`view_to_window`/`window_px`/`clamp_rect`/`clamp_window_to_src`/`window_key`）。
- `domain.py`：Domain（三层存储 images/cache/desc）+ Source 图根/去重表 + `add_src`（path 幂等 + images 副本 + md5）。
- `render.py`：`fig_key(path,window,annos)` + `render`（crop + 主动降采样 + cache 命中复用）。
- `tools.py`：`load`/`view` + Block + `meta_annotation`（越界 `> ⚠️ clamp:`）。
- `tests/image_ctx/test_p1.py`（18 项）。新会话已验证 windows.png(1357×764)：`@窗口≡@全图` center 精确、全图主动降到 800×450、越界只取有效区不补边。
- 小坑：`fig_id` 存**裸 id**（如 `1000`，不带 `FIG:` 前缀）；引用 token `FIG:1000`、元注解标签 `F:1000`。

### 2. P2 定位层落码（P2 checklist 全勾）—— 小原型先行验证
- **小原型** `/tmp/kilo/vision/anno_proto.py`：验证 anno 像素叠加正确性。核心换算 = **位图像素 = `@窗口` 坐标 × 位图尺寸**（窗口整体缩放，相对位置不变，与 scale/窗口盒绝对位置无关）。程序断言全过 + 视觉确认十字压中 windows.png「工具(T)」，双确认无问题。
- `render.py` 改为**自绘 annos**（crop + 主动降采样 + `draw_annos` + save，保留 budget 检查 `estimate_peak`/`mem_budget`）。因 anno `kind` 有 7 种而 img_tool 只支持 star/rect，在 image_ctx 内自建绘制（不改 img_tool，符合"独立模块"）。
- `tools.py` 新增：`draw`/`move`/`delete_anno`/`clear_annos` + `resolve_anno` + 越界 `_clamp_anno_pts`（clamp 到 [0,1]，不报错）+ markdown 高亮 `> ⚠️ **ANNO:n 已 clamp 至 FIG:x 边界**` + `clear_fig_block` + `fig_meta`；`meta_annotation` 加 `标注: {id} {kind} @窗口 (...) {...} {color}`；`pts` 输入宽容（扁平 `[u,v]` 或 `list[list]`，`_norm_pts`）。
- `tests/image_ctx/test_p2.py`（12 项：draw/move/delete/clamp/指纹/瞬态/作用域/像素落位）。
- 像素落位测试坑：windows.png 本身含红色背景像素，整图红像素质心会被拖偏 → 用「预期十字邻域」局部检测（`_red_centroid(path, near, radius)`）。

### 3. 职责边界定案（YZ，**重点，勿越界**）
- `image_ctx` **只管图对象状态**（View/Source/Domain、坐标、去重、渲染、anno 编辑）。**不管上下文/K 轮/compile**：`earliest_fig_turn` 单指针、图块散落历史、K 轮寿命、薄状态行、摘超龄图块——**全部归上下文管理器**（cog-runtime 编译层）。
- 依赖方向：上下文管理器 → 调 `image_ctx` 接口；图模块**不反向感知**轮次/历史/当前轮。
- `image_ctx` 暴露给上下文管理器的接口面：`load/view/draw/move/delete_anno`（各产一个图块描述 Block）、`fig_meta(fig_id)`（渲染元注解，供薄状态行/重载锚）、`clear_fig_block(fig_id)`（**上下文管理器摘超龄图块时调用**，清空该 View 瞬态 annos；「何时清」归上下文管理器，「怎么清」由图模块做）。
- 工程本体 `design-vision-image-fields.md` §10 已修正：原把 `window.py(earliest_fig_turn)`/`compile.py(上下文文法)` 塞进 `image_ctx` 的建议**作废**，归上下文管理器。

---

## 设计要点骨架（不变式，详见本体）

- 图 ≜ `(path, view)`；引用 = 单一 tagged token `FIG:`/`PATH:`/`ANNO:`，只抄不造；`PATH` 为必需输入通道；ANNO 图内作用域、引用必须成对 `(FIG, ANNO)`。
- 无场：图块散落历史、活 K 轮（默认 4 可配）、单轮恒 1 图块、无 load_many；`earliest_fig_turn` 单指针摘超龄；K 改大不回生、改小立即生效（这些靠上下文管理器的 compile，非 image_ctx）。
- 存储三层：`images/`(资产)/`desc/`(canonical，不含 note，P1/P2 未落 desc)/`cache/`(可清，指纹 `(path,window,annos)`)。
- 去重仅身份层（Source 图根）：同 path 幂等、同 `(path,window)` 同 FIG_ID；跨 path 像素相同不合并；compile 不去重。（P1 已实现身份层去重，P4 由此覆盖大半，compile 不去重归 P3/上下文管理器。）
- 像素一致性：下发 `render(fig)` 窗口位图（crop + 主动降采样封顶 ≤800）、`detail=original`（请求层，P1/P2 未接）、元注解 `w×h`=实际下发；越界 view/anno 均 clamp 取有效区、不补边/平移、文字标原→生效 + `> ⚠️`。
- 坐标三套化：动作=`@窗口`（相对参考 FIG 窗口，可负/越界）、地图=`@全图`（元注解信息性）、像素=内部/校验+尺寸；模型只在 `@窗口` 动作、不换算；看全图 = load/view 全图（`@窗口≡@全图`）。
- `note` 瞬态：经 `compose_figure_text` 消费即丢（P3 才做 compose）；回显第二人称 `你的备注:`；图说明 = 元注解 + note，管理数据绝不原样泄进上下文。
- anno 瞬态：只活所属 FIG 图块在 K 轮窗口内（超龄清空、重载同 (path,window) 不带回）；参与渲染指纹，不入 desc/canonical。

---

## 下一步（P3 上下文编译层——归上下文管理器，非 image_ctx）

1. 新模块（建议独立，勿塞 image_ctx）：实现 `compile(agent, domain, acted, human, *, k=4) -> messages`——只编当前轮 + 历史图块按龄摘除（`earliest_fig_turn` 单指针，K 改大不回生/改小立即生效）+ 薄状态行 + `compose_figure_text`（元注解 + note 第二人称）。产块接口：`load/view/draw/move/delete_anno` 各产 Block，`fig_meta` 供锚，`clear_fig_block` 供摘龄时清 annos。
2. P3 验收：K 轮滚动 + 重载锚在长会话里文字自含是否足够让模型重建窗口（checklist 残留探针）；薄状态行每轮顶部；单轮恒 1 图块。
3. 元信息 A/B：短固定序 vs 冗长混乱，看定位精度/被坐标带偏（vf6/lm_service）。

---

## 运行

- 后端：`cd /home/zhengyp/work/A/cogos && python3.11 -m cogos.lm_service.cli server --port 11434`（**会话级，每新会话要重开**）。KEY `ik_REDACTED`。
- 跑 vf6：`cd /tmp/kilo/vision && python3.11 vf6.py <msg.txt> --scene windows.png --out DIR [--no-thinking]`。
- 测试：`cd /home/zhengyp/work/A/cogos && python3.11 -m pytest -q`（需 python3.11）。image_ctx：`python3.11 -m pytest tests/image_ctx -q`。
- 飞书通知：`cd /home/zhengyp/work/A/locus && python3.11 tools/feishu_notify.py "<文本>"`（默认 YZ）。

---

## 遗留 / 待办（非阻塞实现）

- `detail=original`（禁厂商二次 resize）归请求构造层（P2+/vision-func），P1/P2 未接；坐标安全靠主动控图到封顶已保住。
- 指纹 4 位小数精度是否误撞同位复合 window（必要时升 6 位）；img_tool `estimate_peak`（全幅预算）对「小口大图」是否误拒——待实测（checklist 残留 §8）。
- `desc/` canonical 层（视图 + 程序态标注）尚未落盘（P1/P2 只留内存）；超龄清空/持久化挂 Source，属上下文管理器/P4 边界范畴。
- 视觉子系统（vision-system-design §14）是否与 image_ctx 融合，后续再议（首查 `cogos/docs/vision-system-design.md`）。

---

## 关键文件

- 本体（最终定稿）：`/home/zhengyp/work/A/cogos/docs/design-vision-image-fields.md`
- 验收清单：`/home/zhengyp/work/A/cogos/docs/design-vision-image-fields-checklist.md`（P1/P2 已勾）
- P1 实现规格：`/home/zhengyp/work/A/cogos/docs/design-vision-image-fields-p1-spec.md`
- 实现：`cogos/image_ctx/{view,domain,render,tools}.py` + `__init__.py`
- 测试：`tests/image_ctx/{conftest,test_p1,test_p2}.py`
- 小原型：`/tmp/kilo/vision/anno_proto.py`、`anno_draw.png`、`anno_proto_full.png`
- 上游设计：`cogos/docs/vision-system-design.md`（§4/§6/§14）
- 前置交接：`handoff-vision-image-fields-5.md`（P1 规格+两拍板）、`-4.md`（设计定稿版）
