# 视觉图组织与上下文注入：域 / 图(视图=FIG) + 引用规范（09-08 定稿，下午轮；09-08 晚坐标改三套化 + 建验收清单）

> 本体文档：`/home/zhengyp/work/A/cogos/docs/design-vision-image-fields.md`（设计定稿，待实现，下一步落 cogos `image_ctx`）。承接 `vision-system-design.md`（§4/§6/§14 原语）。
> 本条目为 09-08 下午这轮讨论后的**当前定稿**；上午轮的旧表述（fig_ref/view#/防复读 dup_from/源图不去重/ANNO 暂缓）、以及随后定稿的「观察场/比较场/展示集上限」均已作废/改写。

## 核心概念
- **图 ≜ (source PATH, view VIEW)**：`FIG:<id>` = 某源图 + 一个窗口。全图 = 窗口覆盖整体；**所有图都是"子图"**（自带原图尺寸/当前图尺寸/在原图的位置）。主图/子图边界对模型不存在。
- **引用 = 单一 tagged token**：`FIG:<id>`（系统生成，只抄）/ `PATH:<path>`（模型可提名，人让"打开某路径的图"）/ `(FIG, ANNO:<n>)`（图内作用域，无独立锚点）。模型**看到什么抄什么、不构造**；系统按前缀解引用（`parse_ref`/`resolve_image`/`resolve_anno`）。
  - 分工：`PATH` 只能指源文件(整图)；**派生的子视图无独立路径，只能 `FIG:`**。`PATH` 为**必需**输入通道。
- **域（Domain）**：图资源容器（images 持久/cache 可清/desc canonical），归属+共享隔离边界。
- **Source（图根）**：程序侧介于域与图之间的**身份层**——一张真实源图 + 其 FIG 注册表（`window→FIG_ID`、`FIG_ID→View`），是去重/枚举/持久化挂靠点。只在 `PATH:` 时出现；`FIG:` 不经过它。
- **无场（Field 已废弃，YZ 拍板）**：图的组织=**图块散落历史、活 K 轮（默认4、可配）**，非"观察场/比较场"集中容器。见下「图块 K 轮寿命」。
- **无 parent**：`FIG=(path,window)` 纯函数下 `View.parent` 冗余，已删——各 FIG 只靠 `path` 归属自己的 Source，无 FIG→FIG 从属链。

## 图块 K 轮寿命（上下文组织，替代「场」）
- 图块随产生它的消息**散落历史**，活 **K 轮（默认 4，可配）**；超龄**仅摘图块**、文字永续。这是"图只挂产生那一轮（1 轮存活）"的放宽——让模型可回看最近 K 轮视觉证据。
- **历史消息已固化、不重编**：compile **只编当前轮**；唯一作用于历史的是图块按龄摘除。
- **实现：单指针** `earliest_fig_turn`（最早存活图块轮次），每轮 `当前轮 - earliest > K` 即摘超龄图块并前移指针，不必扫全量。
  - **K 改大**：已摘图块**不回生**；**K 改小**：立即生效，下轮多摘。
- 所有 K 轮窗口内的图块**自然并置**：模型可并置比较任意张，跨源靠各自 `orig_w×orig_h`；**观察/比较不再区分**（原观察场4/比较场3/展示集上限均作废）。

## 坐标系（三套化，09-08 晚定稿）
- 坐标**不是单一系**，分三套各归其位、模型无需在它们之间换算：
  - **动作坐标 = `@窗口`**（窗口相对归一化）：`view`/`draw`/`move` 的 `center/size/pts` 相对**参考 FIG 的窗口框**——`0~1` 覆盖该窗口，`<0`/`>1`=窗口外偏移（平移）。参考框由动作**显式**给定（`view` 用 `ref=FIG:<id>`、`draw`/`move` 用所属 FIG），多 FIG 并存无歧义。**模型永远只在 `@窗口` 上做动作。**
  - **地图 = `@全图`**（信息性）：元注解报告每 FIG 的窗口在全图的位置（`c/s` 相对全图 `orig_w×orig_h` 归一化）。模型读它做**内心地图**（我在全图哪/覆盖多大/是否到边），**不进动作接口**。
  - **像素 = 内部/校验 + 尺寸报告**：`orig_w×orig_h`、实际下发位图 `w×h`；渲染、跨 FIG 计算、ground-truth 校验用；模型只在元注解读尺寸。
- **无全图绝对动作坐标**：看全图 = load/view 全图（此窗口=整体 ⇒ `@窗口 ≡ @全图`），模型只需 `@窗口`。
- 坐标可负/可>1；越界 → 返回边界窗口图 + 标注「原坐标→实际生效坐标」。
- **view 越界 clamp（方案1 定稿）**：越界 → clamp 窗口到源图边界、**只取图内有效矩形**（实际可能<请求 size），**不补边、不平移**；文字标注「原坐标→实际生效坐标（含实际窗口）」。与 ANNO 侧 clamp 对称。
- **像素一致性（主动裁剪，禁厂商二次 resize）**：下发的是 `render(fig)` 渲染的**窗口位图**（img-tool `extract` 语义 crop + 本机按封顶 `max_dim` 主动降采样），**非原图**；请求带 **`detail=original`** 禁厂商二次 resize；**元注解 `w×h`=实际下发位图尺寸**（换算权威）。超大原图不进请求体，出现即实现未按此设计。承接 vision-system-design.md §14「精确给」+ 官方 `detail=original`。

## 去重（仅身份层，compile 无去重）
- **去重只指"身份不重复"**：`FIG=(path,window)` 纯函数——同 path 幂等（同 Source+同 src_fig）、同 (path,window) 同 FIG_ID；跨 path 像素相同不合并。挂图根 Source 上。
- **compile 不去重**：上下文是否重复呈现/防复读**不归图管理程序**；模型可反复看同一图，图管理层不干预、不提示。

## 上下文注入（文字永续含锚 + 图块K轮寿命 + 文字自含）
- 图块随产生它的消息散落历史、活 K 轮；超龄仅摘图块、文字永续（砍降级文字——冗余）。
- **文字 = 语义 + 重载锚**（FIG_ID+orig+window），模型丢图可从文字 load/view 拿回。
- **文字必须自含（硬底线）**：**工具调用痕迹可能被后续设计抹掉** → 重载锚/窗口/坐标/尺寸必须写进图说明文字，不能依赖工具参数。
- 每轮顶部薄状态行（当前域+当前图+最新窗口）；视线轨迹 = 历史消息序列本身。

## 图消息规范
- 图操作返回 = 成对 text/image；text 拆**元注解(程序事实) + 模型批注**。**元注解由 `meta_annotation(fig_meta)` 从管理数据渲染；`compose_figure_text(fig_meta, note)` 拼上模型批注**——管理数据绝不原样泄进上下文。
- **元注解**含：FIG_ID(重载锚)/orig尺寸/窗口参数/越界标注。**模型批注 note 只当轮生效、不进图/存储/desc**。
- **人称**：批注回显用第二人称 **`你的备注: …`**（模型读自己写的；"模型:"是第三人称易混）。程序事实行与 `> ⚠️` 警告保持中性。
- **ANNO 定稿**：图内作用域，@(FIG,ANNO)。生命周期=所属 FIG 的图块在 K 轮窗口内（超龄即失效清空，重载不带回旧 anno）。流程：`draw` 创建+初始定位 → `move/adjust` 改位置+尺寸 → `delete_anno` 删除。坐标=全局系；move 移出所属 FIG 边界 → **clamp 到边界不报错 + markdown 高亮提示**（`> ⚠️ **…**`）。不入 desc。**draw/move/delete 重渲染产出所属 FIG 的最新图块**（同 FIG_ID、位图含/去标注，模型直接看到变化，非新增 FIG）。

## 元信息降干扰原则
- **字段短 + 顺序固定 + 分隔符统一，不做视觉对齐**（对齐空格是额外 token，模型看 token 不看版式）。
- 生效机制 ≈ **低信息量/高可预测/短 token**（样板元数据训练中被跳读），**非视觉显著性**（人看整齐=背景，模型看可预测=低权重）。
- **可测**：vf6/lm_service 可做 A/B（短+固定序 vs 冗长混乱）看是否真被忽略/带偏。列入待验证项。

## 接口（模型可调哑原语）
```
load(ref=FIG|PATH, *, note) -> 消息块   # 打开一张图(src_fig全图) -> 1图块, 散落历史, 活K轮
view(ref=FIG, center, size, shape, *, mark, mark_pt, note) -> 消息块
draw(fig_ref, kind, pts, *, id, label, color, note) -> 消息块   # 结果文字给 ANNO:<n>
move(fig_ref, anno_id, pts, *, size, note) -> 消息块
delete_anno(fig_ref, anno_id) -> 消息块
```
系统侧：create_domain/open_domain/add_src(→Source)/render(→cache指纹=(path,window,annos))/delete_source/clear_annos/compile(纯呈现,无去重)。（无 get_progress/restore——无场后无"图集状态"要恢复，域归 open_domain、域内图用 list_figures）

## 验证/下一步
- 验收清单：`cogos/docs/design-vision-image-fields-checklist.md`（09-08 晚新建；分 P1~P4，每组【行为 MUST HAVE + 禁区 MUST NOT】+ 回指设计 §条款 + 可验证手段；自检两问=功能完整 / 是否偏离设计）。
- **P1 实现规格**：`cogos/docs/design-vision-image-fields-p1-spec.md`（09-08 晚写；坐标换算@窗口→@全图 / 越界clamp / render指纹(path,window,annos) / add_src·load·view·render 签名+输出形状；只写规格未落码）。
- 用 windows.png 复现 vf6 能力验证原始层（add_src/load/view/render）。
- A/B 验证"元信息短+固定序"是否真降干扰。
- 实现落位：`cogos/image_ctx/{domain.py(域+Source图根), view.py, window.py(图块K轮寿命/earliest_fig_turn), compile.py, render.py, tools.py}`（独立于 img_tool，后续再议融合）。
- 后端：lm_service server（会话级）；跑 vf6：python3.11 vf6.py <msg> --scene windows.png --out DIR。

## YZ 已拍板（09-08 晚）
- **§7-1 `load` 产新 FIG**：全图=普通 FIG，按 `(path,全图窗口)` 去重——首次建、再次复用（恒同 src_fig）；与 P4「同 path 幂等」不冲突，"新"=首次不存在才建。load 与 view 对称，均走 dedup。
- **§7-2 `@窗口` size 基准 = 方案 A**：center、size 均分轴 over 参考 FIG 窗口盒（`1,1`=整盒）；**不取短边倍数**（Y 认为短边随 view 变是移动基准、心智负担；A 单一基准、贴"0~1 覆盖该窗口"）。接受 `@窗口≡@全图` 仅对象级（size 数值不等，不碍正确性）。

## 论证脉络（下午轮）
定稿于上午轮之后：① 实现应落 cogos 本体而非 vf6 → image_ctx 独立模块（不与 img_tool 融合，后续再议）→ ② 三个视角（协议/状态模型/编译）→ ③ 图说明 = 元注解 + 瞬态 note，管理数据不泄上下文 → ④ note 不进图的管理层（只在上下文）→ ⑤ `FIG:/ANNO:/PATH:` 命名，FIG 为 (path,view) 纯函数，全图/子图不区分 → ⑥ PATH 为必需输入通道（人让打开某路径图）→ ⑦ 需要 Source(图根) 作为单源管理者（图生了多少 FIG、去重挂靠点）→ ⑧ compile 无去重（模型可反复看图，图管理层不干预）→ ⑨ 去重仅身份层, 源图同 path 幂等 → ⑩ ANNO 图内作用域定稿（draw→move→delete，clamp+高亮）→ ⑪ 元信息降干扰（短+固定序，非视觉对齐；A/B 可测）→ ⑫ 文字自含（工具痕迹可抹）。

## 关键文件
- 本体：`cogos/docs/design-vision-image-fields.md`；上游 `vision-system-design.md`。
- /tmp/kilo/vision/{vf6.py, vf_tool.py, vf_box_proto.py}；交接 `checkpoint/principle-exp/handoff-vision-image-fields.md`。
