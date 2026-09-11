# handoff｜视觉图组织/引用规范 最终定稿 → 落地 cogos image_ctx（09-08 晚）

> 2026-09-08 晚。上游：`handoff-vision-image-fields-2.md`（下午轮，FIG/域/Source 骨架）。本会话把设计收敛为**最终定稿**并**全文档审核自洽**，写入本体 `cogos/docs/design-vision-image-fields.md`；locus 记忆（current/entry/index/CHANGELOG 阶段13）同步。新会话只读本文件即可接手；接口/细节以**本体文档**为准。

---

## 一句话状态

- **设计定稿且已审核自洽**（无场/无 load_many/无 restore/删 parent/K 轮寿命/单轮恒 1 图块/像素一致性），**尚未实现**。下一步落 `cogos/image_ctx` 原始层（add_src/load/view/render，用 windows.png 验证）。

---

## 已定稿要点（详见本体，只列骨架）

- **图 ≜ (path, view)**；引用 = tagged token `FIG:<id>`/`PATH:<path>`/`(FIG,ANNO:<n>)`，模型只抄不造；PATH 为必需输入通道（人让"打开某路径图"）。
- **无场（废弃观察场/比较场）**：图的组织 = **图块散落历史、活 K 轮（默认 4、可配）**；`earliest_fig_turn` 单指针比较即可清；K 改大不回生、改小立即生效；compile 只编当前轮、历史固定只删超龄图块。
- **单轮恒 1 图块**：`load`（开一张全图）/`view`（开一窗口）产**新 FIG**；`draw`/`move`/`delete_anno` 改所属 FIG 标注并**重渲染产其最新图块**（同 FIG_ID、模型可见变化）。**无 `load_many`**（想并视多张 → 分别 load/view，K 轮窗口内自然并置）。
- **容量**：K 轮窗口总量 ≈ K 张，上界由 K 完全控制；文字不设条数（永续 + 含重载锚）。
- **坐标系**：同图根共用该源图全局系（orig_w×orig_h）；越界 clamp=**只取有效区**（方案1，不补边/平移，标注「原坐标→实际生效坐标（含实际窗口）」）。
- **像素一致性**：下发模型的是 `render(fig)` 渲染的**窗口位图**（img-tool `extract` 语义 = crop + 本机按封顶 `max_dim` 主动降采样），**非原图**；请求 `detail=original` 禁厂商二次 resize；**元注解 w×h=实际下发位图**（换算权威）；坐标安全 = 主动控图到封顶（厂商无需再裁），detail 仅保险。
- **图说明 = 元注解（`meta_annotation`）+ 模型批注（`compose_figure_text`，note 瞬态**、不进图/存储/desc）；批注回显**你的备注:**（第二人称）；元信息**短+固定序+分隔符统一、不做视觉对齐**。
- **ANNO 图内作用域**：`draw` 创建+初始定位 → `move`（带 size）改位置+尺寸 → `delete_anno` 删除；生命周期=所属 FIG 的图块在 K 轮窗口内（超龄失效清空、重载不带回）；move 移出边界 → **clamp 到边界 + markdown 高亮（`> ⚠️ **…**`）、不报错**；不入 desc。
- **无 `get_progress`/`restore`**：无场后无"图集状态"要恢复；域归属用 `open_domain`、域内图用 `list_figures`。
- **Source（图根）**=域与图之间身份层（FIG 注册表 window→FIG_ID；去重仅身份层：同 path 幂等、同 (path,window) 同 FIG_ID；**compile 无去重**）。
- **域三层存储**：`images/`（源图资产）/`desc/`（canonical: 视图+标注，不含 note）/`cache/`（可清，指纹 `(path,window,annos)`）。

---

## 待实测/验证（非讨论，靠 vf6/图像实验）

- 元信息「短+固定序」是否真降干扰（A/B，vf6/lm_service）。
- 图像 token 是否纯尺寸函数 f(W,H)（vision-system-design §14，供 usage 校准）。
- 超限行为（单图>32MiB/像素边>8192px/请求体>48MiB → 400/422）实测固化。

---

## 下一步

- **P1 原始层**：`add_src`/`load`/`view`/`render`(+cache) 落 `cogos/image_ctx`，用 `windows.png`（1357×764）复现验证 vf6 能力。
- **P2 定位**：`draw`/`move`/`delete_anno`/`clear_annos`（GUI 点击坐标刚需，目标"工具(T)" 真值 [0.188,0.042]）。
- **P3 上下文**：`compile`（文字自含 + 图块K轮过滤 + 薄状态行 + 元注解/批注缝）。
- **P4**：去重（Source 注册表）——compile 已定无去重，只做身份层。
- 实现落位：`cogos/image_ctx/{domain.py(域+Source图根), view.py(视图+坐标), window.py(图块K轮寿命/earliest_fig_turn), compile.py(上下文文法), render.py(薄封装 img_tool 取像素), tools.py(可调原语)}`（独立于 img_tool，后续再议融合）。

---

## 运行

- 后端：`cd /home/zhengyp/work/A/cogos && python3.11 -m cogos.lm_service.cli server --port 11434`（**会话级，每新会话要重开**）。KEY `ik_REDACTED`。
- 跑 vf6：`cd /tmp/kilo/vision && python3.11 vf6.py <msg.txt> --scene windows.png --out DIR [--no-thinking]`。
- 测试需 python3.11。

---

## 关键文件

- 本体（最终定稿）：`/home/zhengyp/work/A/cogos/docs/design-vision-image-fields.md`
- 上游设计：`/home/zhengyp/work/A/cogos/docs/vision-system-design.md`§4/§6/§14
- 原语/原型：`/tmp/kilo/vision/{vf6.py, vf_tool.py, vf_box_proto.py}`、`vf6_repl_out_new/windows.png`
- locus 记忆：`projects/cogos/entries/2026-09-08-cogos-vision-image-fields.md`（+ current.md / index.md / CHANGELOG 阶段13，已同步）
- 前置交接：`handoff-vision-image-fields.md`（上午版作废）、`handoff-vision-image-fields-2.md`（下午轮）、`handoff-vf6-rect-marker-context.md`、`handoff-read-precision-context.md`
