# locate_issue — 视觉引擎定位问题：从整图印象定位不可靠，需机制层 crop 聚焦

> 接 checkpoint-17（定位失败实证）/ checkpoint-18（主 LLM 自己看 + 工具按需加载 + 痕迹擦除）。
> 本文固化 V1 定位循环的两轮实验发现，核心议题：**LLM 必然看整图，如何做到"像人一样局部看 + 汇总信息"**。
> 新会话加载本文件即进入该议题专门讨论。

## 一句话

LLM 从整图印象做定位（"看整图 → 直接给坐标"）不可靠，会从相似元素里抓"最像的替代品"产生幻觉式定位；且它对"框没框准"无自检能力。出路是把"谁掌握 region 推进"从 LLM 手里拿走，交给机制层 crop 聚焦。

## 实验背景（两轮，均已在 /tmp/kilo/vision 跑通）

工具链：`draw`（星=点/矩形=框）+ `ImageStore/ImageResource`（资源 id、只读全景、可编辑覆盖）+ `LmClient`（vision 模型 `deepseek-v4-flash-vision-exp` 支持 `tool_calls`）。图：`/tmp/kilo/vision/detail.jpg`（4000×3000 → open 成 800×600 全景）。

**实验一：扫全图框所有 12345**（`locate_loop.py`）
- 任务：框住图上所有 "12345"。
- 结果：LLM 声称"6 处、全框住、covering well、任务完成"，2 步停止。
- 客观核对（crop 放大 + 独立清点）：6 框里 1 错 1 漏；框尺寸 w=20px 过小；最关键——**它自评"covering well"完全失真**（框错了还报对）。

**实验二：聚焦单目标**（`single_run.py`，无人工干预）
- 任务：定位"中心略靠右，两个矩形纠缠、其一近正方形"，看不见就退出，看得见就迭代画框、记录最优坐标，上限 10 步。
- 真值：那对纠缠矩形约在归一坐标中心 (0.596, 0.513)。
- 结果：单次跑对（3 步收敛，最终 (0.53,0.47,0.09,0.09)，框基本准、略偏左 16px、把旁边 `range` 罩进）。
- **多次跑不稳定**：5 次里 2~3 次错——
  - run1/run3（x≈0.55）：定位到目标那对，对。
  - run4/run5（x≈0.455）：**偏到左边的 `range` 矩形**（不是目标，偏约 80px），且自我意识到"single rectangle/single square"却不修正就走。
  - run2：一步就停（明知 off 不改）；run4/5 多次因 `finish_reason=length` 输出超长被截断停。

## 核心发现

1. **LLM 自评不可靠（元认知盲区）**：框错了还报"covering well / 任务完成"；或明知"single rectangle"也不修正。判据不能放它自己声称上，必须客观（crop 核对）。→ 接 checkpoint-17"不能听 LLM 声称"。

2. **扫全图分散注意力**：实验一的"框所有实例"是错误任务形态，人不会扫全图枚举。

3. **聚焦单目标仍不稳，栽在"初始定位"这一跳**：第一次给坐标是薄弱点，错一跳后面就在错误区域打转。它没执行"先锁定范围再看"（任务里已给"中心偏右"锚，run4/5 却偏到中心偏左去全图撒网）。

4. **信息量 = 相似多 = 判别难（checkpoint-11 实证）**：这张图大量相似矩形，从相似里找目标 = 高判别难度；LLM 会**低估这种难**、从整图印象抓"最像的替代品"。注意：是信息量问题，不是清晰度/图太大问题（checkpoint-17 已澄清整图尺度信息够）。

5. **人 vs LLM**：人先锁定目标范围（"中心偏右"）→ 局部看 → 逐块扫视汇总；LLM 缺"先聚焦再看"的执行策略，倾向"看整图 → 直接给印象答案"。

## 核心启发（已讨论出，待深化）

- **LLM 必然看整图，但"喂哪张图"是机制层决定的**：机制层 crop 局部重新采样喂它，就等于让它局部看（它做不到"自己只盯局部"，但能拿到"局部图"）。
- **局部看 = 焦点驱动逐级聚焦（focus 循环）**：第 1 级喂全景只答粗方向（"中心偏右"，它已会且准）→ 机制层按方向 crop 大区放大喂 → 再精定位 → 直到够准/看清。每级只处理"小范围+低信息量"。
- **汇总 = 机制层维护空间关系，LLM 不记**：空间记忆→region 链（checkpoint-2）；对象恒常→资源 id（checkpoint-7）；工作记忆→上下文累积（checkpoint-18 痕迹）。
- **落到已有概念**：= checkpoint-15 `focus(center/range)` + checkpoint-2 `region 链` + checkpoint-12 信息隔离 + checkpoint-18 单工具 `extract(region, max_dim)`。
- **关键差异**：谁掌握 region 推进——从"LLM 一次给全图精确坐标"改为"机制层按它的粗方向 crop、再让它判断"。

## 待讨论的核心问题

1. **如何做到"像人一样局部看 + 汇总"的具体机制**：focus 循环的推进策略、每级的 crop 范围怎么定、停的条件、region 链怎么维护换算。
2. **信息量/聚焦是否真的是关键变量**：待对照实验验证——把全景换成"只含目标那对矩形的局部 crop（少量干扰）"，看 LLM 在局部上是否稳定定位。若稳，坐实"聚焦/信息量"是关键而非定位能力缺失。
3. **是否引入机制层预筛**：用边缘/矩形检测先枚举"矩形候选"，让 LLM 从候选中选，而非从像素里找（信息量骤降，但需机械检测能力）。

## 实验产物（/tmp/kilo/vision/）

- 脚本：`locate_loop.py`（实验一）、`single_run.py`（实验二，无干预）、`ask_png.py`（单图核对，mime 自动）、`probe_toolcall.py`（验证 vision 模型 tool_calls）。
- 图片：`walk/pano_800.png`（全景）、`walk/step*_*.png`（画框过程）、`walk/center_right.png`（目标真值 crop）、`walk/llm_final_zoom.png`（最终框放大）、`walk/run2~5/`（多跑产物）。
- 轨迹：`walk/trace.jsonl`、`walk/trace_single.jsonl`。
- 注意：lm-service `web.run_app` 默认 `client_max_size=1MB`，原图 detail.jpg 1.4MB 直接传会 "invalid json body"，须先 open 成 800 全景（30KB）再喂。

## 相关

- `checkpoint-2.md`（locate 收敛 + region 链）、`checkpoint-11.md`（信息量=相似多=判别难，LLM 低估）、`checkpoint-12.md`（信息隔离/关系树导航）、`checkpoint-15.md`（focus 定位机制）、`checkpoint-17.md`（定位失败实证 + 不能听声称）、`checkpoint-18.md`（主 LLM 自己看 + 单取图工具 extract）。
