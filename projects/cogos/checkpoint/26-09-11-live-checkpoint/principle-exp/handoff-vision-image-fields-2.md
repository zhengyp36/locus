# handoff｜视觉图组织/引用规范定稿（域·FIG·场）→ 落地 cogos image_ctx（09-08 下午）

> 2026-09-08 下午。上游：`handoff-vision-image-fields.md`（上午版，fig_ref/view#/防复读 dup_from 等**已作废**）。本会话把图设计收敛为**当前定稿**并写入本体 `cogos/docs/design-vision-image-fields.md`，同步更新 locus 记忆（entry/current/index/CHANGELOG 阶段13）。
> 新会话只读本文件即可接手；设计细节、接口签名以**本体文档**为准（本文只做指针与未定项）。

---

## 一句话状态

- **设计已定稿，尚未实现**（下一步落 cogos `image_ctx` 原始层）。核心跃迁：**FIG ≜ (path, view)**、引用单一 tagged token、图根 Source 只做身份去重、**compile 无去重**、**文字必须自含**（工具痕迹可抹）。

---

## 已定稿要点（详见本体，此处只列骨架）

- **图 ≜ (根源图 PATH, 视野窗口 VIEW)**：`FIG:<id>` = 某源图 + 一个窗口；全图 = 窗口覆盖整体；**所有图都是"子图"**（自带原图尺寸/当前图尺寸/在原图位置），主/子边界对模型不存在。
- **引用 = 单一 tagged token**：`FIG:<id>`（系统生成，只抄）/ `PATH:<path>`（模型可提名；**必需**——人让"打开某路径的图"）/ `(FIG, ANNO:<n>)`（图内作用域，无独立锚点）。模型只抄不造；系统 `parse_ref`/`resolve_image`/`resolve_anno` 解引用。`PATH` 只能指源文件(整图)，派生子视图无路径、只能 `FIG:`。
- **Source（图根）**：域与图之间的身份层——一张源图 + 其 FIG 注册表（`window→FIG_ID`、`FIG_ID→View`），去重/枚举/持久化挂靠点；只在 `PATH:` 出现。
- **去重 = 仅身份层**：`FIG=(path,window)` 纯函数——同 path 幂等（同 Source+同 src_fig）、同 (path,window) 同 FIG_ID；跨 path 像素相同不合并。**compile 无去重**：上下文是否重复呈现不归图管理程序，模型可反复看同一图，图管理层不干预、不提示。
- **坐标系**：同图根共用该源图全局系（`orig_w×orig_h`）；不同源各成一棵。越界 → 边界窗口图 + 「原坐标→实际生效坐标」。
- **上下文注入**：文字永续（重载锚：FIG_ID+orig+window）+ 图瞬时（砍降级文字）；**文字必须自含**（工具痕迹可能被抹→锚/窗口/坐标写进文字）；每轮薄状态行。
- **图说明 = 元注解 + 模型批注**：元注解由 `meta_annotation(fig_meta)`（程序事实：FIG_ID/尺寸/窗口/越界/源自/场级）渲染；`compose_figure_text(fig_meta, note)` 拼上批注——**管理数据绝不泄进上下文**；note 当轮瞬态、不进图/存储/desc。
- **批注人称**：回显用第二人称 **`你的备注:`**（模型读自己写的）；程序事实行与 `> ⚠️` 保持中性。
- **元信息降干扰**：字段短 + 顺序固定 + 分隔符统一、**不做视觉对齐**（对齐空格是额外 token）；机制≈低信息量/高可预测/短 token，**非视觉显著性**。元信息单独紧凑一行、与主思考内容物理分段 + system 提示"元信息非内容、需时读"。
- **ANNO 图内作用域（定稿）**：`draw` 创建(初始定位)→`move/adjust`(改位置+尺寸)→`delete_anno`；生命周期=所属 FIG 在窗口内（淘汰失效清空、重载不带回）；move 移出所属 FIG 边界 → **clamp 到边界 + markdown 高亮（`> ⚠️ **…**`）、不报错**；不入 desc。
- **接口（模型可调）**：`load_view_field(ref=FIG|PATH, note)` / `load_compare_field([{ref,note},…])`(≤3超截断) / `view(ref=FIG, center, size, shape, *, mark, mark_pt, note)` / `draw(fig_ref, kind, pts, *, id, label, color, note)` / `move(fig_ref, anno_id, pts, *, size, note)` / `delete_anno(fig_ref, anno_id)`。系统侧：create_domain/open_domain/add_src(→Source)/render(缓存键=(path,window,annos))/delete_source/clear_annos/get_progress/restore/compile(纯呈现)。

---

## 待讨论清单（逐项未定，新会话从这开始）

- **#2 观察场展示集 vs 历史窗口 vs 薄状态行**：4 张图上限、"更早降文字锚"、历史条数默认 K（可配、摘要保留含锚一句）——这几个容量概念怎么协调、由谁控。
- **#3 比较场**：观察/比较如何切场；跨源坐标系；3(比较) vs 4(观察) 不对称；view 替换某位的宏观归属。
- **#4 越界 clamp 的图语义（view 侧）**：view 越界怎么裁（补边/画布 vs 只取有效区）、坐标怎么回显——**ANNO 侧已定**（clamp+高亮），view 侧未细定。
- **#5 parent/继承是否必要**：`FIG=(path,window)` 纯函数下 `View.parent` 冗余。**我的倾向：去掉 parent（方案2）**——观察场轨迹=历史消息序列本身，模型靠序列顺序自然追溯连续性；去掉更纯粹（除非要跨场/会话精确追溯"子图自哪张父图 view 来"）。**待 YZ 拍板 1(保留) 还是 2(去掉)**。

---

## 下一步

- **P1 原始层**：`add_src` / `load_view_field` / `view` / `render`(+cache) 落进 `cogos/image_ctx`，用 `windows.png`（1357×764）复现验证 vf6 能力。
- **P2 定位**：`draw` / `move` / `delete_anno` / `clear_annos`（GUI 点击坐标刚需，目标"工具(T)" 真值 [0.188,0.042]）。
- **P3 上下文**：`compile`（文字自含+图瞬时+薄状态行+元注解/批注缝）。
- **P4**：`load_compare_field` / 去重(Source 注册表) / 历史窗口——不过 compile 已定无去重，源图去重只做身份层。
- 元信息"短+固定序"是否真降干扰 → A/B 验证（vf6/lm_service）。
- 实现落位 `cogos/image_ctx/{domain.py(域+Source图根), view.py, compile.py, render.py, tools.py}`（独立于 img_tool，后续再议融合）。

---

## 运行

- 后端：`cd /home/zhengyp/work/A/cogos && python3.11 -m cogos.lm_service.cli server --port 11434`（**会话级，每新会话要重开**）。KEY `ik_REDACTED`。
- 跑 vf6：`cd /tmp/kilo/vision && python3.11 vf6.py <msg.txt> --scene windows.png --out DIR [--no-thinking]`。
- 测试需 python3.11。

---

## 关键文件

- 本体（定稿）：`/home/zhengyp/work/A/cogos/docs/design-vision-image-fields.md`
- 上游设计：`/home/zhengyp/work/A/cogos/docs/vision-system-design.md`
- 原语/原型：`/tmp/kilo/vision/{vf6.py, vf_tool.py, vf_box_proto.py}`、`vf6_repl_out_new/windows.png`
- locus 记忆：`projects/cogos/entries/2026-09-08-cogos-vision-image-fields.md`（+ current.md / index.md / CHANGELOG.md 阶段13）
- 前置交接：`handoff-vision-image-fields.md`（上午版，已作废参照）、`handoff-vf6-rect-marker-context.md`、`handoff-read-precision-context.md`
