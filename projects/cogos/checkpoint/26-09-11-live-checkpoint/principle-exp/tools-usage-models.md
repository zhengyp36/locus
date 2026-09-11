# 工具用法说明整理｜面向模型的"图工具"介绍 + 调用协议（09-09）

> 抓取自最近实验中"关于图的工具、且面向模型（SYSTEM / schema description）的用法说明"。
> 本源：`p3probe/task*.py`、`diagnose.py`、`vf6.py`、`vf7.py`、`cogos/{image_ctx,cog_ctx,agent}`。
> 目的：对比各实验如何向模型介绍图工具用法、走 json 还是 tool_calls，供 vf7 定标准用。

---

## 0. 总览

| 实验 | 工具介绍方式 | 调用协议 | `tools=` 参数 |
|---|---|---|---|
| p3probe taskLoop/taskConf | schema（`VIEW_TOOL.description`） | 结构化 tool_calls | ✓ |
| p3probe taskA / taskB / taskC / taskD | SYSTEM 文字 + 输出一行 JSON | 文本 JSON | ✗ |
| diagnose.py | SYSTEM 文字 + JSON（兼容 `<invoke>` XML 兜底） | 文本 JSON | ✗ |
| vf6.py | SYSTEM 文字 + 末尾 JSON | 文本 JSON | ✗ |
| vf7.py | SYSTEM 文字 + 末尾 JSON | 文本 JSON | ✗ |
| cogos agent (`agent/tools.py`) | schema（`ToolSpec`） | 结构化 tool_calls | ✓ |
| cogos 图工具本体 (`image_ctx/tools.py`) | 元信息文字（`meta_annotation`）注入图块 | 函数级，不直接暴露模型 | — |

---

## 1. 结构化 schema 派（tool_calls 协议）

### 1.1 p3probe/taskConf.py（`VIEW_TOOL`）
```python
VIEW_TOOL = {
    "name": "view",
    "description": (
        "查看你正在看的这张图的某个区域，返回该区域的放大截图。"
        "用于看清局部。center 为该区域中心、size 为该区域宽/高，均相对当前这张图归一化"
        "（0..1 覆盖当前整张图）。"
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "center": {"type": "array", "items": {"type": "number"}, "description": "区域中心 [cx, cy]，相对当前图归一化 0..1"},
            "size": {"type": "array", "items": {"type": "number"}, "description": "区域宽高 [wx, wy]，相对当前图归一化 0..1"},
        },
        "required": ["center", "size"],
    },
}
```

### 1.2 p3probe/taskLoop.py（`VIEW_TOOL`，同构）
```python
VIEW_TOOL = {
    "name": "view",
    "description": "查看你正在看的这张图的某个区域，返回放大截图。center/size 相对当前图归一化 0..1。",
    "parameters": {
        "type": "object",
        "properties": {
            "center": {"type": "array", "items": {"type": "number"}, "description": "区域中心 [cx,cy]"},
            "size": {"type": "array", "items": {"type": "number"}, "description": "区域宽高 [wx,wy]"},
        },
        "required": ["center", "size"],
    },
}
```

### 1.3 cogos agent（`agent/tools.py`，`ToolSpec`）
```python
class ToolSpec:  # {name, description, parameters} 同构于 OpenAI 风格（但内部形式）
    ...
def make_read_file_spec(work_dir: Path) -> ToolSpec:
    # "description": "按行读取工作目录内的一个文本文件，返回带行号前缀的内容"
    # "parameters": {"path","offset","limit"} 每项带 description
```

> 注意（handoff-10 定案）：`LmClient.tools` 用**内部形式** `{name,description,parameters}`，
> 不是 OpenAI 的 `{type:function,function:{...}}` 包装（用包装会报 `function.name invalid type: null`）。
> 组装/拆解见 `cogos/lm_service/providers/base.py` 的 `assemble_tools` / `assemble_tool_messages` / `parse_response`。

---

## 2. SYSTEM 文字描述派（文本 JSON 协议）

### 2.1 p3probe/taskA.py（重建窗口，参考盒=全图）
```python
TASK = (
    "你收到一次 view 操作产生的「图说明元信息」(程序生成的重载锚, 参考盒=整张全图)。"
    "请仅凭这段说明, 给出重新定位到该窗口的 view 动作参数。"
    "坐标规则: center 分轴相对参考图整幅归一(0..1); size 分轴按各自维度(宽对宽、高对高)归一。"
    '输出一行 JSON: {"view":{"center":[cx,cy],"size":[wx,wy],"shape":"rect"}}'
)
SYSTEM = (
    "你是看图助手。下面是一张图的元信息说明(非图像, 是程序参考)。"
    "F:… 行给出 @全图 地图: c=中心(分轴 over 维度), s=尺寸(分轴 over 各自维度, 宽对宽/高对高), "
    "shape=窗口形状, → 位图 w×h 是实际下发的位图尺寸。请据此重建该窗口。"
)
```

### 2.2 p3probe/taskB.py（同 taskA 结构，见文件）
```python
TASK = (
    '...输出一行 JSON: {"view":{"center":[cx,cy],"size":[wx,wy],"shape":"rect"}}'
)
SYSTEM = (
    "...F:… 行给出 @全图 地图... 请据此重建该窗口。"
)
```

### 2.3 p3probe/taskC.py（衍生窗口：参考盒=锚窗口，@窗口 ≠ @全图）——**坐标教学对照实验**
```python
COORD_TEACH = (
    "坐标规则：center 分轴相对参考盒归一(0..1，覆盖整个参考盒)；size 分轴按各自维度"
    "（宽对宽、高对高）归一。@窗口 相对参考盒，@全图 是该窗口在全图的地图。"
)
TASK = (
    "上面是某个窗口的图说明元信息。该窗口就是**参考盒**（ref 传入它的 FIG id）。"
    "请以它为参考盒开一个**更小的窗**：中心放在参考盒的 @窗口 (0.30,0.30)，"
    "size 取 @窗口 (0.45,0.45)，shape=rect。"
    '输出一行 JSON: {"view":{"ref":"F:<id>","center":[cx,cy],"size":[wx,wy],"shape":"rect"}}。'
    "注意 center/size 是相对参考盒（不是全图）的 @窗口。"
)
# C1 无教学: SYSTEM 只用真实 SYSTEM_HINT（中性，无坐标规则）
# C2 有教学: SYSTEM = SYSTEM_HINT + COORD_TEACH
# 判据: C1 混淆而 C2 准 → 实锤"缺坐标教学" → 推动态注入规则
```

### 2.4 diagnose.py（对话式工具，`info/extract/draw`）
```python
def make_system(img_path: str) -> str:
    return (
        "你是看图助手, 会看到一张图。\n"
        "你有三个工具可用: info(读图信息) / extract(按归一化 region 裁剪局部子图) / draw(在图上画矩形或星标注)。\n"
        f"当前首图: {img_path}\n"
        "规则:\n"
        "- 坐标一律归一化 [0,1], 相对你要操作的那张图。\n"
        "- 想看局部细节: 调 extract, 传小 region, 用 out 给产物路径。\n"
        "- 要看自己的判断: 调 draw, 用 rect=[x,y,w,h]。\n"
        "- 不要编造没看到的; 不确定就直说置信度。\n"
        "先描述你看到的, 再按需调用工具; 每次工具结果会作为新消息回到你上下文。"
    )
# TOOLS = [info, extract, draw]，field 描述如:
#   extract: "从原图按归一化 region 裁剪局部子图再缩到 max_dim 内(只缩不放大)。只看局部就传小 region。返回产出图路径+尺寸。"
#   draw: "在原图/剪图上画标注(矩形/星), 坐标归一化[0,1]相对该图。产生一张新图。"
# 协议: 结构化 tool_calls + 文本 JSON（兼容 <invoke> XML 兜底）
```

### 2.5 vf6.py（对话式视觉调试 agent，两层视野）
```python
SYSTEM = (
    "你是观察场景的看图助手。每轮你会收到一组「视野区」图片，外加一句会话文字。\n"
    "【视野区】图片按固定顺序呈现：全景 → 中央凹(时间序)。\n"
    "每张图前有一行标注 `[id] 角色·名称·属性`，用 id 指代该图。图片只在视野区出现，不进会话文字历史。\n"
    "两层视野：\n"
    "· 全景：当前打开的那张图，默认的坐标上下文；open 换图时它改变，中央凹随之切到该图的旧上下文。\n"
    "· 中央凹：由 view 动作产生的局部图序列，按源图分组记忆。\n"
    "【坐标】center/size/radius 相对你为 view 指定的图：指定了 image 就相对那张图，缺省则相对当前全景。"
    "center=[cx,cy] 指定要看的位置（cx 沿宽、cy 沿高）；"
    "size=[wx,wy] = 矩形窗口尺寸，均相对所指定图的短边（wx 沿宽、wy 沿高）；"
    "radius=圆窗半径(相对所指定图的短边)，等价于 size=[radius,radius] 且 shape=circle。"
    "shape='rect'(默认) 用矩形框，'circle' 用圆窗；mark=true(默认) 会在视野图上画十字标出注视中心。\n"
    "【动作】在回复末尾附一行 JSON，一次只发一个；不想发动作就只说话。\n"
    '  {"open":{"path":"/abs/path.jpg"}} 或 {"open":{"image":"image_1"}}\n'
    '  {"view":{"image":"image_1","center":[cx,cy],"size":[wx,wy],"shape":"rect","mark":true}}\n'
)
# 协议: 文本 JSON（split_action 解析末尾 JSON）
```

### 2.6 vf7.py（对话式视觉定位 agent，无预设/单图层级）
```python
SYSTEM = (
    "你是看图助手，能看到一张「当前图」。你通过动作来观察和标注它。\n"
    "【动作】在你的回复末尾附一行 JSON，一次只发一个；不想发动作就只说话。\n"
    '  {"open":{"path":"/abs/path.png"}}\n'
    '  {"view":{"center":[cx,cy],"size":[wx,wy]}}\n'
    "   从当前图割一个矩形子图，成为新的当前图（放大看清局部）。center/size 均相对当前图归一化，"
    "width对宽度、height对高度。size 越小越放大。\n"
    '  {"draw":{"x":0.4,"y":0.2}}\n'
    "   在当前图上画一个十字（点击锚点），坐标相对当前图归一化。\n"
    '  {"move":{"x":0.5,"y":0.2}}\n'
    "   把当前图上的十字移动到新的位置（坐标相对当前图归一化）。\n"
    "【坐标约定】所有 center/size/x/y 都是一律【相对当前可视图】的归一化 0..1 小数，"
    "不是相对源图、不是像素。程序负责把它换算回源图。\n"
)
# 协议: 文本 JSON（split_action 解析末尾 JSON）
# 图前标注: `[{id}] {label}  {w}x{h}` + 已打开图 id 列表提醒（未含 @全图 窗口定位，见下）
```

---

## 3. cogos 图工具本体的"图前元信息文字"（真正给模型看的图块说明）

`cogos/image_ctx/tools.py::_compose_text` → `meta_annotation(fig)`，每次 load/view/draw/move 后作为图块前置文字：

```python
def meta_annotation(fig, *, clamped=None, mark=None, highlights=None) -> str:
    base = (
        f"F:{fig.fig_id} | {fig.orig_w}×{fig.orig_h} | "
        f"@全图 c({w.center[0]:.3f},{w.center[1]:.3f}) s({w.size[0]:.3f},{w.size[1]:.3f}) "
        f"{w.shape} → 位图 {fig.w}×{fig.h}"
    )
    lines = [base]
    for a in fig.annos:
        lines.append(f"标注: {_anno_str(a)}")   # f"{a.id} {a.kind} @窗口 (u,v) {a.color}"
    # clamped/mark/高亮 时附加 > ⚠️ / @窗口 复核行
    return "\n".join(lines)
```

> 参考盒语义（`cog_ctx/context.py`）：
> - `F:… / 标注: / > ⚠️` 是**程序生成的参考信息（重载锚/定位用），不是图像内容**。
> - `SYSTEM_HINT = "【图】元信息行（F:… / 标注: / > ⚠️）是程序生成的参考信息（重载锚/定位用），不是图像内容，需要时才读；请基于图像本身推理，结论写进 `你的备注:`。"`
> - `compose_figure_text`: `f"{fig_meta}\n────────\n你的备注: {...}"`
> - 坐标语义（`view.py` 注释）：`@全图 Window`(storage) = center/size 归一、center over dims、size over dims(宽对宽、高对高)；`@窗口 Window`(action) = center/size 相对参考 FIG 的窗口盒。

---

## 4. 差异要点（整理结论）

1. **两套坐标归一语义并存**：
   - cogos / p3probe taskA-D：`center` 分轴 over 全图 & `size` 分轴（**宽对宽、高对高**）。
   - vf6 / vf7：`size` 有历史歧义（vf6 用**短边**分母；vf7 用**宽/高**分母）。
   - ⚠️ vf7 若改用 cogos 的 `meta_annotation` 文字，须把坐标基准统一到 cogos 的分轴归一律，否则基准病换形式复现。

2. **界面（图前/图块文字）信息量差异**：
   - cogos `meta_annotation`：含 `@全图 c(…) s(…)` 世界定位参照（模型能说清"我看到的图在全图哪块"）+ `标注: … @窗口` 锚点。
   - vf7 当前 `[{id}] {label} {w}x{h}`：**缺 @全图 窗口定位**，模型无"这块图在全图位置"的参照。

3. **面向模型的"坐标教学"必要性**（taskC 对照实证）：`@窗口 ≠ @全图`（参考盒≠全图）时必须显式教坐标规则（分轴归一 + size 宽对宽高对高），否则模型混淆 → 换算偏。这是 handoff-10 基准病的直接结论。

4. **调用协议**：对话式实验（diagnose/vf6/vf7）用**文本 JSON 动作**；p3probe 与 cogos agent 用**结构化 tool_calls**（内部形式 `{name,description,parameters}`，非 OpenAI 包装）。
