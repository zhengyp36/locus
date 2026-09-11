# notes｜图相关工具（面向模型）讨论审视（09-09 午后，待改）

> 2026-09-09 午后。上游：`handoff-vision-image-fields-11.md`（图说明自注解定案，已落 `meta_annotation`）。
> 本 note = 对"图相关工具（load/view/draw/move/delete_anno）面向模型用法"逐项审视得出的**待改意见**，尚未动码，记录预留后面统一改。只跟交接文件放同目录，不占主状态。

> 审视基线（当前实现，`cogos/image_ctx/tools.py`）：
> `load(ref, *, note)` / `view(ref, center, size, shape, *, mark=True, mark_pt=None, note)` /
> `draw(fig_ref, kind, pts, *, id, label, color)` / `move(fig_ref, anno_id, pts, *, size)` /
> `delete_anno(fig_ref, anno_id)`。
> 结论先行：**观察+标注两链结构自洽够用；待改点集中在"重复标注通道"（mark 去重）、"命名/语义瑕疵"（circle=椭圆）、"整体工具命名/分组统一"（see + mark 族）、"注解/引用前缀不自洽"（F: vs FIG:）**。

---

## 议题 1：mark 与 draw 重叠 → 统一 draw 为唯一标注通道

### 一句话意见

`view` 的 `mark`/`mark_pt` 参数与 `draw` **功能重叠**（都在图上画十字），应把 **`draw` 定为模型唯一标注通道**，`view` 的 `mark`/`mark_pt` 从模型可调参数中收掉（改为程序默认回显注视点，或直接取消）。

## 背景 / 论证

- `view` 现状签名：`view(ref, center, size, shape, *, mark=True, mark_pt=None, note)`。
- **渲染重叠已证实**：`cogos/image_ctx/render.py:110` `elif kind in ("cross", "point", "mark")` —— `mark` 本身就是 anno 的一个 kind，与 `draw(kind="cross"/"point"/"mark")` 走**同一渲染分支**，图画出来的十字完全一样。
- 核心差异只在**语义/生命周期**，不在外观：

| | mark | draw |
|---|---|---|
| 实体 | 无，仅本次 view 产物图上一笔 | 有，创建 `Annotation` 进 `fig.annos` |
| 生命周期 | 瞬时，画完即弃 | 持久，随所属 FIG 图块 K 轮；可 `move`/`delete_anno`；摘块时被 `clear_fig_block` 清 |
| 用途 | 无状态"注视=检验"（看清楚没） | **提交锚点**（程序读它换算回源图坐标） |

- 结论：模型要"提交/定位一个点"应走 `draw`（有状态、程序回读换算）；`mark` 只剩"看一眼时顺带标我盯哪"这一个价值，且不产生需管理状态。
- **给两条都能画十字的接口 = 制造混淆**（模型到底是走 `view+mark` 还是 `draw`？），应避免。

## 待改方向（YZ 已拍板）

**采用方案 1——直接收掉 `mark`/`mark_pt`**：`see` 纯看图、不带任何画十字；模型标点只用 `mark` 动作。

> 理由：接口零冗余是硬标准（契约自明、不走双通道）；"注视=检验"反馈若要做应是**程序默认行为**，且目前未落地，不为"将来可能加"留占位参数。将来若做，用程序默认回显方式再加回，不影响模型接口。

---

## 议题 2：`shape="circle"` 实为椭圆 → 命名/语义瑕疵

### 一句话意见

`view`/`draw` 的 `shape="circle"` 名不副实——实现上按"宽对宽、高对高"的 `size` 画，**像素上通常是椭圆**，只有 `wx==wy` 且原图宽高相等（`wx*orig_w == wy*orig_h`）才是正圆。

### 论证

- `render.py:104-109`：`elif kind in ("ellipse", "circle")` —— `(cx,cy),(sw,sh) = pts[0], pts[1]`，`d.ellipse([x,y,x2,y2])` 按宽、高各画。
- 归一化 `0..1` 是分轴 over 各自维度（handoff-8 定案，`s(1.000,1.000)` 才整盒），不是像素投影；`circle` 传入的 `wx`/`wy` 虽在层内对称，换算到像素后是否正圆取决于原图宽高比。
- 名称带误导——模型以为 `circle` 是正圆，实际看到椭圆。

### 待改方向（二选一）

1. **改名**：`shape` 值 `circle` → `ellipse`（如实），不再承诺正圆。
2. **加约束**：`circle` 时要求 `wx==wy`（归一化相等），并在注解里说明"是否为正圆取决于原图宽高比"。

> （倾向 1：改名最省事、无歧义；若想保留"用两个参数表达同一轴"的写法再加约束。）

### 关联

- circle 命名问题**已被议题 12 消解**（see 已无 shape）；此议题仅余历史记录/`mark` kind 侧无碍（mark 用 `ellipse` 命名，无语义问题）。
- vf6/vf7 用 `shape='circle'` + `radius`，与 image_ctx 的 `size=[w,h]` 不是一套，待统一时一并收敛。

---

## 议题 3：整体工具命名/分组统一 → `see` + `mark` 族（YZ 已拍板）

### 一句话意见（定案）

把面向模型的图工具收拢成**两大领域动词**，命名据语义统一（YZ 已拍板）：

| 领域 | 动词 | 职责 |
|---|---|---|
| 看 | `see` | 打开图 / 调整视野与清晰度（收拢原 load+view） |
| 标注 | `mark` / `adjust_mark` / `unmark` | 创建 / 调整 / 删除标注（替换原 draw/move/delete_anno） |

### 论证 / 关键点

- **`see` 收拢 load+view**：语义明确、用法统一，既可看指定路径图、也可在图上调整视野。YZ 认可可行。
  - `see(ref, center, size, remark)`：`ref` ∈ `{PATH, FIG}`；`ref=PATH` → 相对该图全图，`ref=FIG` → 相对该 FIG 窗口盒（`@窗口`）。**坐标基准由 ref 锚定**，避免模型自行拼窗口构造（那是基准病来源，见 handoff-10/11）。
  - 窗口恒矩形（无 `shape`，议题 12）；`mark`/`mark_pt` 已由议题 1 拍板收掉。
- **为什么反对"任选 `(path+center+size+shape)` 自由指代"**：描述的是窗口而非图，且缺"相对谁"；FIG 是程序侧去重/生命周期锚 + 模型的省力记忆锚，模型应"只抄不造"。
- **标准动作只落已存在的图，用 FIG**：标注必须落在某张已存在的图上，不可用窗口拼新图再标。延续 `(FIG, ANNO)` 定稿指代。
- **`adjust_mark` 而非 `move_mark`**：现 `move` 可改**位置+大小**（`size` 非空时 `[pts[0], size]`），非纯平移，故叫 `adjust_mark` 更准（YZ 已拍板）。

### 字段（示意，后续见用法文档）

```python
see(ref, center, size, remark="")             # 窗口恒矩形（无 shape，议题 12）
mark(fig, kind, pts)                          # 创建标注（id 程序自动编号、颜色程序分配、无 label/color——议题 8/9/13；从返回文字拿 ANNO:n）
adjust_mark(fig, anno_id, pts, *, size)        # 位置+大小
unmark(fig, anno_id)                           # 删除标注（anno_id="all" 清全部，议题 10）
```

### `see` 用法（已定稿，YZ 认可；写入 /tmp/kilo/vision/see-usage.md）

```
name: see
description: >
  打开一张图，或在已打开的图上调整视野（观察区域与放大程度）。

  坐标（相对 ref 所指向的对象，归一化 0..1）：
  - x 以对象宽度为基准、y 以对象高度为基准；标准图像坐标：x 向右、y 向下、[0,0] 左上角、[1,1] 右下角。
  - 坐标值允许小于0或大于1，表示位置在当前视野之外；若所示位置超出源图边界，程序只取图内有效区。

  调整：center 定视野中心在对象内的位置，size 定区域大小（矩形窗口）。

  视野权衡：
  - size 大 → 范围大、利于搜索目标，但每目标像素少、清晰度低；
  - size 小 → 专注局部、看清细节，但像素受源图本身分辨率上限约束；
  - size 过小 → 目标可能不在框内、只剩极少数像素，失去观察意义。
```

- `ref`：`PATH:<路径>` 打开新图；`FIG:<id>` 在已出现的图上调整（id 取自注解 `图 FIG:<id>` 照抄）。
- `center` [cx,cy] / `size` [wx,wy]：相对 ref 归一化 0..1，x 沿对象宽、y 沿对象高。
- 窗口恒矩形（无 `shape`，议题 12）；`remark` 回显为「你的备注:」。
- 措辞已统一「源图」（技术性指代真实坐标根/整图，与代码 Source/orig 咬合）。

### 关联 / 注意

- `mark` 作为领域动词，与旧 `view` 里的 `mark` 参数（议题 1 要收掉的）是两回事——新命名里 `mark` 是**标注动作**，正是议题 1 的落点（标注收进 `mark`，`view` 不再带 mark）。两者衔接。
- 分组介绍给模型时写清"看（see）/ 标注（mark 族）"两大族，避免模型把 mark 当"顺带画十字的看图参数"。

---

## 议题 4：工具契约自明 + 程序侧集中定义描述（YZ 已拍板）

### 一句话意见（定案）

**工具契约（含坐标基准）全部自明**，由一组**程序侧常量**集中定义（`COORD_BASE` 等）、各工具 `description` 引用拼入。**system-prompt 不再提任何工具用法/坐标规则**，只留身份/任务/叙事；工具分工与立场由契约自明吸收，模型自行编排。

### 顶层立场：给模型的"图工具的用法"

"图工具的用法"应能在**工具 schema 自身**自明，`system-prompt` 不提。最终形态：**没有全局 prompt 一段工具用法；没有散落四处的手写重复；每一处契约都在工具 schema 里、且源自唯一常量。**

### 关键结论（推翻我早前"必须在 system 留一句"）

1. **坐标基准可重复进工具** → 每个工具拿到完整契约（鲁棒：早期上下文被裁工具契约仍在；符合"工具自明"直觉）。
2. **重复的漂移风险由程序消掉** → 基准句做成一个常量 `COORD_BASE`，各工具 description 拼装引用；人只改一处，产物重复但来源唯一。
3. **token 成本可忽略** → token 大头在图片/多轮历史/模型错误用法反复试错的重试轮次，不在工具几行字；自描述省下的重试 token 远大于成本。
4. **分工/流程不要全局声明** → "先 see 后 mark"是模型应自行涌现的编排，非工具契约，塞进任何处反而教条。
5. **立场性规则可消解进自描述** → 坐标相对 ref、FIG 只引用不构造，由各工具契约承载即可；**不单独声明"谁换算"这类实现内幕**（YZ 定案：不给模型无用背景）。
6. **"全局一层"与"工具自明"合流** → 当 `COORD_BASE` 成为全局常量、被各工具引用后，它既全局（定义唯一）又自明（各工具都带）。不再是"二选一"。

### 工具契约常量（示意，程序侧集中定义）

```python
COORD_BASE = "所有坐标相对 ref 归一化 0..1；x 以对象宽度为基准、y 以对象高度为基准；标准图像坐标：x 向右、y 向下、[0,0] 左上角、[1,1] 右下角。"
FIG_ANCHOR = "FIG 是程序给定的图身份，只引用不构造；ref=FIG 相对该图窗口盒，ref=PATH 相对全图。"
```
每个工具 `description` = 该工具语义 + 拼入相关常量 + 工具特有的一句坐标补充（见下）。

### 坐标处理（YZ 已拍板）

- **`COORD_BASE` 只保留模型用法所需**（相对谁 / 归一化范围 / 原点方向）。
- **删掉"程序负责换算回源图、模型不需要报源图坐标"**——这是实现内幕（后台谁换算），不属于模型用法；契约自明只给"怎么用"，不给实现。且各工具 description 已写明坐标相对 ref，模型自然不困惑。
- **各工具特有坐标句**（拼进各自 description，不与 COORD_BASE 冲突）：
  - `see`：坐标值允许 <0 或 >1，表示位置在当前视野之外；若超出源图边界，程序只取图内有效区。＋ `size 大/小/过小` 权衡。
  - `mark` 族：坐标落在图内，越界将被 clamp 到图边界。

### 描述要中性（写能力、不写策略）

- **写**：工具**能做什么**（能力契约）——如 `adjust_mark`"改位置/大小、调整后仍是同一标注（anno_id 不变）"。
- **不写**：**建议你怎么编排**（策略/流程）——如"建议先 mark 标大概再微调"。这会过度改变模型决策，把"该不该用"从模型手里抢走。
- **提醒可怎么用 = 由能力自明达成**：写清能力（能改位置、同 id），模型自会推断"可以标大概再调整"，无需明说。
- 若要更显式但仍中性，可并列摆**两条路径**（如"想重定位可 unmark+mark，或直接调整"），同为选项、非推荐，让模型自行权衡。
- 落地：`adjust_mark` 中性措辞见 `mark-usage.md`（含"也可删后重标"并列句）。

### system-prompt 的保留范围

- 身份 / 任务 / 叙事。
- **不含**：工具用法、坐标规则、工具分工——这些一律由工具 schema 自明。

### 边界（唯一保留的观点，属设计判断非契约）

- 工具契约装不下**意图层面的取舍**（何时用 circle/rect、何时回看全图）——模型判断，非契约。
- 只读 vs 写的关系写在各自 description（如 `mark`：标注会改动图的状态）即可自明，可下沉。

---

## 议题 5：注解前缀 `F:` 与引用前缀 `FIG:` 不自洽（待改）

### 一句话意见

图注解显示 `图 F:1001`，但模型**引用**时要用 `ref="FIG:1001"`——前缀 `F:` 与 `FIG:` 不一致，模型需自己推断"注解里的 `F:1001` 到 ref 是 `FIG:1001`"，破坏"契约自明"。ID 本体（`1001`）清楚，**前缀不自洽**。

### 论证

- `view.py:55` 设计意图：`fig_id` 存裸 id（如 `"1000"`），**引用 token `FIG:1000`、元注解标签 `F:1000`**——即注解用 `F:`，ref 用 `FIG:`，前缀不同。
- `tools.py:230` 报错、`tooltip` 也都用 `FIG:`（引用前缀），而 `meta_annotation`（`tools.py:182`）出的是 `F:`。
- 矛盾：模型**看见**的是 `F:1001`（注解），**要用**的是 `FIG:1001`（ref）。这恰是 `see` 描述写 `FIG:<id>`、注解却出 `F:1001` 的裂缝。

### 定案（YZ 已拍板）

**统一为 `FIG:`**：注解改为 `图 FIG:1001`，与 ref 完全一致，模型照抄即用，零推断。`FIG:/PATH:/ANNO:` 前缀体系全局统一无歧义。

> （方案 2「注解出裸 id」已否：ID 语义要靠 `see` 描述额外说，多一处依赖。）

### 关联 / 注意

- 改动点：`meta_annotation`（`tools.py:182` `图 F:` → `图 FIG:`）；`_anno_str`/`_pixel_diag` 等处若引用 `F:` 同步；`test_p1.py` 相关断言。
- 与议题 3 的 `see` ref 措辞、议题 4 契约常量衔接——`FIG:` 前缀是引用约定，注解须自带。

---

## 议题 7：标注的可见性模型 —— 对比度 + 大小（YZ 已拍板）

### 一句话意见（定案）

模型看标注要"看得见"，取决于**两个维度**：**对比度**（标记色 vs 周围背景，决定像素差多少）+ **大小**（标记跨若干 patch，决定差异能否成形）。两者共同刻画同一本质——**模型制造的像素差异强度**。**模型无大小/色负担，这层归程序保证**。

### 论证：模型"看"与人的区别（YZ 洞察）

- 模型视觉输入是**像素数值**（patch 化、token 化），**没有人的"视觉显著性/注意力"失明机制**——标记改变了该 patch 像素值，差异**一定进了输入**，比人看到微小差异可靠。
- 故"看不见只因为与背景相同"（对比度不足）是**绝对瓶颈**；但"只要画上去就能看见"过头——受 **patch 编码分辨率**约束：标记若比 patch 小很多，只是污染一个 patch 的几个像素，token 差异 < 编码分辨率，被近似成"略脏的背景"，模型**认不出是标记**，只当噪声。
- 所以"可见"需同时满足：① 对比度（标记色 ≠ 周围背景）；② 足够形成"属于一个图案"的像素规模（跨过 patch 成形），否则只是噪声。

### 对三标注工具的设计含义

- **对比度优先**：`mark` 默认色须与常见背景区分——现用红 `#FF3B30` + 黑描边/白底双描边（`line_w+2`）即为对比，此条保留。
- **大小归程序自适应，不给模型 size 参数**（模型无法预览、易乱调，且与 `adjust_mark` 的 size 语义撞）。
- **不用孤点**：印刷状面状/线状标记（十字、框、椭圆）成形稳；**实心小点最难成形**，且叠加于小、对比度也吃亏——倾向弃用或改画可见范围够大的标记。`cross` 保留十字。
- 大小下限比 vf7（≥8px、3–4% 短边）可放宽，但**要有下限**保证成形——这层是"跨过 patch 成形"，不是"让模型看清"。
- 遮挡 vs 可见：优先**保证可见**；若担心十字遮目标，用"十字中心留空/仅四臂"缓解，而非缩成小点。

### 参见

- `render.py:110-114`（`cross`/`point`/`mark` 同分支、`r=max(4,2%短边)` 偏小）；`vf7.py _draw_cross`（`max(8,4%短边)` 更醒目，作基线参考）。

---

## 议题 8：`mark` 不接收用户指定 `id`（YZ 拍板）

### 一句话意见（定案）

`mark` **去掉 `id` 参数**。标注 id 由程序自动编号（`tools.py:271` `anno_id = id or _next_anno_id(fig)`，`id` 本就可选）；模型**创建后从返回文字里读 `标注: ANNO:n`**（`_anno_str` 输出 `{a.id} ...`），用于后续 `adjust_mark`/`unmark` 引用。

### 论证

- 创建时模型**无需预知/指定 id**（还不知、也不必关心将来编号）——手动指定是额外心智负担，且 id 是程序侧持久命名，不属"标注动作"语义。
- 创建 = **程序发号、模型读号**更自明：模型只管"在哪标、标什么"，号由程序给、从返回拿。
- 同步：`mark(fig, kind, pts, *, label)`（去 id，且 colors 由程序分配、模型不指定——议题 9）；`mark-usage.md` 字段表去 `id` 和 `color`、description 补"返回该标注 id"与"颜色程序分配"。

### 涉及改动

- `cogos/image_ctx/tools.py`：`draw`→`mark` 签名去 `id` 入参（仍可内部 `_next_anno_id` 自动编号）。
- 议题 3 字段示意 / `mark-usage.md` 已同步去 id。

---

## 议题 9：颜色由程序决定 + 选色方法（YZ 拍板）

### 一句话意见（定案）

**颜色归程序，`mark`/`adjust_mark` 均不给模型 color 参数**。选色方法 = **感知均匀色板按序轮转（区分多标注）+ 黑/白双描边兜底（对比背景）**。不做"采样背景挑最反差色"（复杂图上判断哪个是背景本身不稳，且与多标注区分冲突）。

### 论证：为什么程序选色合适（回应"模型是否需判断图中多了什么"）

- **模型识别标记主要靠文字，不靠颜色**：mark 返回的元注解有 `标注: ANNO:n {kind} …`（id/形状/坐标），模型**从文字直接知道**标了什么、在哪，图像是同步确认，**无需去"看图中多了什么"**。
- 颜色职责有两个，都该由程序保证：
  1. **对比背景**（单标注在复杂图上清晰）；
  2. **区分多标注**（多个标注不撞色）。

### 选色方法（推荐，复杂度低且稳）

1. **色板**：感知均匀的高区分度板——HSV 固定 V/S、色相均分（8 色，如 0/45/90/135/…度），或色盲友好 8 色板（参考现有 `core.py:23` `_DEFAULT_COLORS` 6 色，可扩充到感知均匀）。
2. **分配**：按标注序号 `i % len(色板)`，**同图内自动避开已用色**（冲突则顺延），避免相邻标注撞色。
3. **对比度由渲染层描边兜底**：保持彩色线 + 黑（或白）描边双线（`render.py` 现为彩色 + 黑边 `line_w+2`）。**哪怕彩线颜色跟背景对比不足，靠描边层保证轮廓可见**——对比度的主要保证。彩线只负责区分多标注。

### 为什么不做"采样背景挑最反差色"

- 需判断"哪个是背景"，复杂图上难（目标铺满、多区域、图案混杂）。
- 且最反差色可能被别的标注占用，与**区分多标注**目标冲突。
- 故**分层**：彩线管区分（色板轮转）、描边管对比（黑/白双线），两者解耦、都稳定。

### 涉及改动（并入待改清单）

- `render.py`：色板感知均匀化、多标注分配避开已用色、描边层保证对比；`mark`/`adjust_mark` 不暴露 color。

---

## 议题 10：`unmark` 支持 `anno_id="all"` 清全部（YZ 拍板）

### 一句话意见（定案）

`unmark(fig, anno_id)` 的 `anno_id` 取 `"all"` 表示**清空该图全部标注**；否则删单个 `ANNO:n`。

### 论证

- **显式表达优于隐式**：`"all"` 必须主动写才清空，不会因"忘填 id"而误清全部（优于让 `anno_id` 可选、缺省=全部的方案）。
- **无魔数冲突**：真实标注 id 恒为 `ANNO:n`（`tools.py` `_next_anno_id` 中 `{a.id}` 格式），`"all"` 不会撞任何真实 id。
- description 写清两用法即可自明。

### 字段 / 用法

```
anno_id: string  必填。"ANNO:<n>" 删单个；"all" 清空该图全部标注。
```

### 涉及改动

- `cogos/image_ctx/tools.py`：`delete_anno`→`unmark` 支持 `anno_id=="all"` 时 `fig.annos.clear()`（对齐系统侧 `clear_annos(fig_id, None)` 语义）。
- `mark-usage.md` 已同步（字段 + 示例 + description）。

---

## 议题 11：标注 kind 集合精简 → 只留"点/矩形（+椭圆变体）"（YZ 拍板）

### 一句话意见（定案）

kind 集合精简到**两种语义**：**标记单点（`point`）+ 圈区域（`rect`/`ellipse`）**。砍掉 `star`/`arrow`/`stroke`/`polyline`/`line`（描述复杂形状，定位任务用不上，徒增模型记忆负担）。

### 论证（从"标注语义"出发，非视觉多样性）

- 定位任务只需两种语义：**标记单个位置**（"就是这里"）+ **圈一块区域**（"这个范围内"）。
- `point` + `rect` 覆盖两者，语义最小时集。
- 其余形状：
  - `ellipse`：圈非方形目标（圆钮/图标）时更贴，是 rect 的低成本视觉变体，**保留**（可精简删，但留也自洽、不冲突）。
  - `cross`：与 `point` **语义冗余**（都标单点，仅画法不同）。按议题 7 十字更易成形，故**合并为 `point` 一种语义、渲染成十字**（清晰可见）。
  - `star`/`arrow`/`stroke`/`polyline`/`line`：描述复杂形状，非定位所需，**删**。

### 单点画法（YZ 定案，免实测）

- **`point` 渲染成十字**：议题 7 论证实心孤点难过 patch 成形（对比度+成形双吃亏），十字是线状、跨像素多、成形稳；且 vf7 已验证十字能把模型带到位（`vf7.py _draw_cross`）。不做探针。

### 涉及改动（并入待改清单）

- `cogos/image_ctx/render.py`：kind 渲染分支精简——保留 `point`/`rect`/`ellipse`，删 `star`/`arrow`/`stroke`/`polyline`/`line`；`point`（原 `cross` 语义）渲染为十字（画法待实测定）。
- `mark-usage.md`：已同步（kind 描述 + 字段表值 + 示例改为 point/rect/ellipse）。

---

## 议题 12：`see` 的 `shape` 收掉 → 窗口恒矩形，形状交给 `mark`（YZ 拍板）

### 一句话意见（定案）

**`see` 去掉 `shape` 参数，窗口恒为矩形**。形状的多样性只保留在 `mark`（真实渲染）。`see` 只管"看哪、看多大"，不管什么形状。

### 论证：`see` 的椭圆是"伪特性"

- **render 恒按矩形裁剪**（`render.py:170` `img.crop(box)`）——`shape` **不影响实际裁剪**，窗口永远是矩形。
- `shape` 只进元信息（`tools.py:180` 显示"矩形/椭圆"）与 `window_key`，属**展示性假象**：告诉模型"这是椭圆窗口"，却送回矩形位图，制造不一致。
- 与 `mark` 的 `kind` 不同层：`mark` 的 `kind` 影响**真实渲染**（`draw_annos` 真画椭圆/矩形/十字）；`see` 的 `shape` 是虚的。
- 若 `see` 报"椭圆窗口"却给矩形裁剪位图，认知不一致（模型以为看到椭圆、实际矩形），故收掉。

### 职责分工（干净）

- `see`：看哪、看多大（矩形窗口）。
- `mark`：在图上画什么形状（`point`/`rect`/`ellipse`，真实渲染）。

### 涉及改动（并入待改清单）

- `cogos/image_ctx/view.py`：`Window.shape` 收敛为 `rect`（或保留字段但 see 不再传非 rect）；`window_key`/`px_rect_to_window` 相应简化。
- `cogos/image_ctx/tools.py`：`see` 签名去 `shape`（或收为内部恒 rect）；`meta_annotation` 形状字段固定"矩形"。
- 议题 2（circle=椭圆）随之**不再适用 see**（see 已无 shape）；circle 命名问题只残余在 `mark` kind 侧（若 mark 保留 ellipse 命名，则无语义问题）。
- `see-usage.md` 已同步（去 shape；字段表/description/示例）。

---

## 议题 13：`mark` 去 `label`；"K 轮超龄"不写进 description（YZ 拍板）

### 一句话意见（定案）

1. **`mark(fig, kind, pts)` 去掉 `label`**（模型识别标注靠文字注解 `标注: ANNO:n {kind} …` 的 id/形状/坐标；颜色归程序、形状用 kind、位置用 pts，`label` 重复表达且可能被忽略；模型要备注走 `remark`/文本批注）。
2. **"标注随图块 K 轮超龄被清"不写进 description**——是生命周期/实现细节，非模型"怎么用"契约（议题 4：不给实现内幕）；模型当轮即可见 id/形状/坐标。

### 论证

- **label 删**：`mark` 参数收敛到 `(fig, kind, pts)`，id/color/label 全部归程序，契约最简（model 只需"在哪标、标什么"）。
- **K 轮不写**：标注生命周期属上下文组织，当轮模型用不到"超龄"信息；若真因标注消失困惑，应从上下文管理层面解决，不是靠 description 打补丁。

### 涉及改动（并入待改清单）

- `cogos/image_ctx/tools.py`：`draw`→`mark` 签名无 `label`、无 `id`、无 `color`＝`mark(fig, kind, pts)`。
- `mark-usage.md`：字段表删 `label`（id/color 已删）；description 不从寿命角度提 K 轮。

---

## 待改清单（后面统一做，不现在动）

- `cogos/image_ctx/tools.py`：**命名重组** `view→see`（**去 shape，收 mark/mark_pt**——议题 12/1）、`draw→mark`（**去 id/color/label 入参**，议题 8/9/13）、`move→adjust_mark`、`delete_anno→unmark`（**`anno_id="all"` 清全部**，议题 10）；**注解前缀 `F:`→`FIG:`**（议题 5）。
- **新增工具契约常量层**（`COORD_BASE` / `FIG_ANCHOR` 等，程序侧集中定义）→ 各工具 `description` 拼装引用；schema 归一处组织（`agent/tools.py` 或 image_ctx 侧生成）。
- `cogos/image_ctx/render.py`：确认 `mark` 作为独立 kind 是否还需保留（`("cross","point","mark")` 分支，注意与新 `mark` 动作名撞词）；**kind 精简——保留 `point`/`rect`/`ellipse`，删 `star`/`arrow`/`stroke`/`polyline`/`line`（议题 11），`point` 渲染为十字（YZ 定案，免实测）**；**`circle`（窗口 shape）已收敛 rect（议题 12），椭圆命名只余 `mark` 侧无碍**；**`cross`/`point` 大小下限视对比度/成形原则校准（议题 7），不做实心小点**；**色板感知均匀化 + 多标注分配避开已用色 + 描边层保对比（议题 9）**。
- `cogos/image_ctx/__init__.py`：导出名同步。
- `cogos/image_ctx/view.py`：`Window.shape` 收敛为 `rect`（`window_key`/`px_rect_to_window` 相应简化），见议题 12。
- `tests/image_ctx/test_p1.py`（`test_meta_annotation_clamp_and_mark` 用 mark 参数）/ 相关 `circle` 用例边界调整。
- 相关 design 文档 §接口 同步。
- probe/实验（vf6/vf7/diagnose）用文本 JSON 动作，`mark`/`circle` 语义各异，待统一时一并收敛。

## 记录状态

- 仅意见，未落码（议题 3、4、5、7、8、9、10、11、12、13 已全部拍板；议题 1 已拍板取方案 1 收 mark/mark_pt；议题 2 已被议题 12 消解——see 已无 shape）。
- 本会话（09-09 傍晚）补完全部剩余裁决，现**无剩余待定**（见下方「本会话定论追加」）：pts 已拍板方案 B（center+size）、SYSTEM_HINT 已拍板整删、kind 定为 cross/rect（删除 ellipse；点语义用 cross）、schema 确认为新装。
- 落码时机：YZ 后续指令（回到"动手改代码"时统一改）。

## 本会话定论追加（09-09 傍晚）

> **落码修正（09-09 傍晚晚段，YZ 拍板）**：标注 kind 命名定为 **`cross`/`rect`**（非 point）——`cross` 命符一致（渲染即十字，且 vf7 已验证清晰），避免 `point` 名不副实。下文出现的 `point` 一律理解为 `cross`。

> 基于本笔记落码风险审视后，YZ 逐项拍板补完。**此节为最新定论，覆盖上方正文中与之冲突的旧表述。**

### 动作全集（旧五个全清，无残留）

| 族 | 动作 | 收编自 | 备注 |
|---|---|---|---|
| 看 | `see` | load + view | 唯一开图/调视野入口；产 FIG 进 live，上下文须记录 |
| 标注 | `mark` | draw | 建 |
| 标注 | `adjust_mark` | move | 改（位置+大小） |
| 标注 | `unmark` | delete_anno | 删；`anno_id="all"` 清全部 |

- 不再保留 load/view/draw/move/delete_anno 任何旧名。

### 各工具最终签名（重点更新正文）
- `see(ref, center, size, remark="")`：窗口恒矩形（无 shape，议题 12）、无 mark/mark_pt（议题 1）。
- **`mark(fig, kind, center, size=None)`**：kind 定为 **`cross`/`rect`**（**ellipse 删除**，推翻正文议题 11 的"保留 ellipse"；点语义用 `cross`，名符一致）；**pts 改为方案 B（`center` + `size` 分开，center=位置、size=尺寸且仅 rect 有效）**，替代正文"同一 pts 依 kind 两种写法"；无 id/color/label（议题 8/9/13）。
- `adjust_mark(fig, anno_id, center, size=None)`：size 不给则保留原尺寸（仅 rect 有意义）；方案 B。
- `unmark(fig, anno_id)`：`"all"` 清全部（议题 10）。

### 议题 4 落地
- `SYSTEM_HINT`（原 context.py:51）**整条删除**：一切自说明——图注解行自明参考信息、工具 description 自明用法，system 不叠调用/坐标/编排/内幕。连带消解其在 context.py 的 `F:` 字面问题。
- 工具契约自明：坐标/引用描述**集中常量化**（`COORD_BASE`/`COORD_VIEW`/`COORD_FIG`/`FIG_ANCHOR` 全在 tools.py 一处定义，schemas 只引用拼装，不分散）；**description 严格按意见定稿措辞**（see 对齐 see-usage.md、标注族对齐 mark-usage.md 措辞；窗口恒矩形无 shape）。`FIG_ANCHOR` 用模型视角措辞（**无「窗口盒」**——那是实现语义，见 see-usage 待确认点；改为"只引用不构造 + id 取自注解「图 FIG:<id>」照抄"）。**schema 层确认为新装**（现未接进任何 LLM tool-call 机制；`agent/tools.py` 的 ToolSpec 不含 image_ctx，`cog_ctx` 无 schema 生成）。落地顺序：**先定格最终函数签名，再建 schema 生成器（常量拼装），独立成批验证**。

### 议题 5 前缀统一
- 统一 `FIG:`（正文已定）。`F:` 字面残留点：`tools.py:182`（`图 F:`→`图 FIG:`）、`view.py:55`（注释）；context.py 因 `SYSTEM_HINT` 整删而消解。

### `FigureAct.op` 同源枚举化（本会话新增）
- `op`（context.py:18）是真实字段非注释，改名须同步；收敛为**同源枚举/常量**（函数名 / op / schema name 三处引用同一处定义），呼应议题 4"唯一来源、产物一致"。op 全集 `{see, mark, adjust_mark, unmark}`。

### 渲染层（低险，有实测先例）
- kind 精简：保留 `cross`(渲染十字)/`rect`；删 `star/arrow/stroke/polyline/line`（均只出现在分支列举、查无实测）。`ellipse` 因本会话删除。底层 `img_tool`（`core.do_draw` + `type:"star"`）是另一入口，非级联，不受影响。
- `cross`→十字同源于 vf6/vf7 已验证中心十字；色板感知均匀化 + 双描边保对比；窗口 `circle` 已收敛 rect（议题 12）。
- 无自动化断言能验"像素级可见"，全凭真实试跑确认（YZ 接受，开发阶段遇问题即调）。

### 已知遗留核对点（落码时注意）
- 删 `ellipse`/`circle` kind 前，确认 `test_p1/p2`、`img_tool` 低层无 `kind="ellipse"/"circle"` 依赖。
- `SYSTEM_HINT` 删除后，确认 `FigContext.system_prompt()`（context.py:75-77）无别处引用，有则一并处理。
