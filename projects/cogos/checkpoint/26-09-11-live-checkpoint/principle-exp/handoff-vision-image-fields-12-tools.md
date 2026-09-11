# handoff｜图工具面向模型重构（see + mark 族）—— 交接落码（09-09 晚）

> 上游：`handoff-vision-image-fields-11.md`（图说明自注解，已落 `meta_annotation` 自注解格式）。
> 本话题（整链见 `notes-vision-tools-review.md`，**全决策拍板、无方向待定**）：把面向模型的图工具从 `load/view/draw/move/delete_anno` 重构为 **`see` + `mark` 族**（`mark`/`adjust_mark`/`unmark`），契约自明（含坐标基准集中常量），system-prompt 不再描述工具用法。
> 新会话只读：`notes-vision-tools-review.md`（决策原文）+ 本文件（实施清单）+ `tool-usage/`（3 工具用法定稿）。

---

## 一句话目标

把图工具收拢为两大领域动词：**看（`see`）+ 标注（`mark` 族）**。命名、契约、坐标约定全部自明，`system-prompt` 不提工具用法/坐标规则。

---

## 一、最终工具定稿（接口形态）

```python
see(ref, center, size, remark="")          # 打开图 / 调视野；窗口恒矩形；无 shape、无 mark/mark_pt
mark(fig, kind, pts)                       # 创建标注；无 id/color/label（全归程序）
adjust_mark(fig, anno_id, pts, *, size)    # 调整标注位置+大小；anno_id 跨轮不变
unmark(fig, anno_id)                       # 删除标注；anno_id="all" 清全部
```

字段语义（详见 `tool-usage/see-usage.md`、`tool-usage/mark-usage.md`）：
- `ref` ∈ `{PATH:<路径>, FIG:<id>}`；`PATH`→相对全图，`FIG`→相对该 FIG 窗口盒（`@窗口`）。id 取自注解 `图 FIG:<id>` 照抄。
- `center/size` 相对 ref 归一化 0..1，x 沿对象宽、y 沿对象高；标准图像坐标（x 右、y 下、[0,0] 左上）。
- `kind`：`rect`/`ellipse`（圈区域，pts=[中心,[宽,高]]）；`point`（标单点，pts=[点]，**渲染成十字**）。

---

## 二、契约常量（程序侧集中定义，各工具 description 拼入）

```python
COORD_BASE = "所有坐标相对 ref 归一化 0..1；x 以对象宽度为基准、y 以对象高度为基准；标准图像坐标：x 向右、y 向下、[0,0] 左上角、[1,1] 右下角。"
FIG_ANCHOR = "FIG 是程序给定的图身份，只引用不构造；ref=FIG 相对该图窗口盒，ref=PATH 相对全图。"
```

- **不写**"程序负责换算、模型不报源图坐标"（实现内幕）。
- 各工具 description = 工具语义 + 拼入相关常量 + 工具特有坐标句（`see`：可 <0/>1 看窗口外、越源图边界取有效区 + size 权衡；`mark` 族：坐标落在图内，越界 clamp）。
- **描述中性**：只写"能做什么"（能力契约），不写"建议怎么做"（策略/流程）——避免过度改变模型决策。"提醒可怎么用"由能力自明达成。

---

## 三、实施步骤（按文件，顺序执行）

### 1. `cogos/image_ctx/view.py`
- `Window.shape` 收敛为 `rect`；`window_key`/`px_rect_to_window` 简化，去掉 shape 分支（议题 12）。
- 确认 `view_to_window` 仍正确（越界→clamp 只取有效区，已实现）。

### 2. `cogos/image_ctx/tools.py`（核心）
- **重命名**：`load`→`see`、`view`→`see`（合并；收掉 `shape` 参数、收掉 `mark/mark_pt`——议题 1/12）、`draw`→`mark`、`move`→`adjust_mark`、`delete_anno`→`unmark`。
- `see(ref, center, size, remark="")`：`ref` 支持 PATH/FIG 双指代（拆自 load+view）；窗口恒矩形。
- `mark(fig, kind, pts)`：去 `id`/`color`/`label` 入参（id 内部 `_next_anno_id` 自动；颜色走渲染层色板——议题 8/9/13）。
- `adjust_mark(fig, anno_id, pts, *, size)`：保持 anno_id 不变、可改位置+大小。
- `unmark(fig, anno_id)`：`anno_id=="all"` 时 `fig.annos.clear()`（议题 10）。
- `meta_annotation`：注解前缀 `图 F:` → **`图 FIG:`**（议题 5）；形状字段已在 see 侧固定"矩形"。

### 3. `cogos/image_ctx/render.py`
- kind 精简：保留 `point`/`rect`/`ellipse`，删 `star`/`arrow`/`stroke`/`polyline`/`line`（议题 11）。
- `point` 渲染成**十字**（线状、成形稳；参考 `vf7.py _draw_cross` 的 `max(8,4%短边)` 下限，议题 7/11）。
- 色板感知均匀化（HSV 固定 V/S 色相均分 8 色或色盲友好 8 色）、多标注分配避开已用色、彩色线+黑/白双描边兜底对比（议题 9）。
- 确认 `mark` 作为独立 kind 是否还保留（现 `("cross","point","mark")` 分支；注意与新 `mark` 动作名撞词）。

### 4. `cogos/image_ctx/__init__.py`
- 导出名同步：`see`/`mark`/`adjust_mark`/`unmark`；删 `load`/`view`/`draw`/`move`/`delete_anno` 旧名（确认无外部依赖）。

### 5. schema / 接入（目标层，待 YZ 指令才接）
- 各工具 schema（name/description/parameters）由 `COORD_BASE`+`FIG_ANCHOR`+工具语义拼装，归一处组织（`agent/tools.py` 或 image_ctx 侧生成）。
- 接入 `ToolRegistry` + `toolset_names`（当前未接入，此步单独做，非本话题收口）。

### 6. 测试对齐 `tests/image_ctx/`
- `test_p1.py`：`test_meta_annotation_base_format`（`图 FIG:`）、`test_meta_annotation_clamp_and_mark`（mark 参数已收）、`test_load_block_downsizes_whole`；相关 circle 用例边界调整。
- `test_p2.py`：draw/move/delete_anno 调用改新名；`anno_id="all"` 清全部新用例。

---

## 四、验收标准

- `python3.11 -m pytest tests/image_ctx/ -q` 全过；`python3.11 -m pytest -q` 无回归（基线 994）。
- 无禁区 API 残留：`load/view/draw/move/delete_anno` 不再作为模型工具暴露；`meta_annotation` 出 `图 FIG:`。
- 契约自明：schema description 自带 COORD_BASE（坐标自明）；system 无工具用法段。

---

## 五、遗留 / 待定

- **`pts` 依 kind 两种写法是否统一**（mark-usage 待确认点）：`rect/ellipse`=[中心,大小]、`point`=[点]。属语法层面，落码时可一并定（倾向保留现状，描述说清即可，不强改）。
- **schema 接入与探测**：本话题只改了 image_ctx 接口层 + 契约；真正接入 `ToolRegistry` 暴露给模型、并用 vf7 探针验证"契约自明"效果，属下一步（待 YZ 指令）。
- 上下文管理（K 轮 / 图块 / `clear_fig_block`）不受本重构影响，未动。

---

## 运行

- LM server（会话级）：`cd /home/zhengyp/work/A/cogos && python3.11 -m cogos.lm_service.cli server --port 11434`；KEY `ik_REDACTED`。
- 测试：`cd /home/zhengyp/work/A/cogos && python3.11 -m pytest -q`。
