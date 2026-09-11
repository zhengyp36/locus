# Handoff — 视觉引擎：draw 定位工具 + 图资源模型（换会话交接）

> 新会话直接读本文件 + `status.md` + `checkpoint-18.md` + `checkpoint-17.md` + `codebase.md` 接手。
> 当前阶段：checkpoint-18 架构（主 LLM 自己看 + 工具按需加载 + 痕迹擦除）下，已实现**定位 draw 工具**和**图资源模型**，下一步是**手动走 V1 定位循环验证**。

## 当前在做什么

视觉引擎从 checkpoint-17 走通 open 后，checkpoint-18 反转为"主 LLM 自己看图 + 单取图工具 + 调用后擦痕迹"。本会话进一步：
1. 确定实验方法论：**自己扮演 LLM 走过程，关键环节调用真实 LLM 验证**（两者走同一条路径对照），不是"考 LLM"。
2. 提出并实现 **draw 工具**（定位用：图上画星星=点定位 / 矩形=区域定位，解决"预估坐标直接 crop 丢上下文"的问题）。
3. 提出并实现 **图资源模型**（draw 从无状态原语升级为资源操作）。

## 图资源模型（已拍板 + 已实现）

- **图在上下文成为资源**，有 `id` 可引用。四要素：`description`（可选，LLM 写、**覆盖式**，历史由 LLM 自己维护）+ `id` + `editable`（只读/可编辑）+ 像素内容。
- **全景图只读**（`editable=False`），draw 不能原地覆盖它，只能输出新资源或覆盖可编辑资源。
- **draw 契约**：`draw(resource_id, marks, description?, output_id?)`
  - 输入 = 在哪个图资源上画（`resource_id`）
  - 输出 = `output_id` 不指定 → 生成新资源；指定已存在 → **原地覆盖**（上下文长度不变，某条消息内容持续变化 = checkpoint-18 痕迹擦除的落地）
  - 只读资源可当画布，但 `output_id` 指向只读资源时拒绝
  - description 传了才覆盖，不传保留旧值
- **覆盖 vs 追加**：不加 mode 参数，图永远是「原图 + 本次传入的全部 marks」全量重渲染；LLM 想追加就把历史坐标一起传，想只看最新就只传最新。

## 本次代码改动（cogos 仓库 `/home/zhengyp/work/A/cogos/`）

- `cogos/img_tool/core.py`：新增 `do_draw` + `render_marks`（画星/框标注，do_draw 与 resource 共用）+ `_draw_star`/`_star_vertices` + 默认色板。坐标归一 0~1，star=`x,y` 点、rect=`x,y,w,h`（与 extract region 同约定）。
- `cogos/img_tool/cli.py`：`draw` 子命令（`--star X,Y` / `--rect X,Y,W,H` 可重复）。
- `cogos/img_tool/stub.py`：`async draw(...)` 返回 bytes。
- `cogos/img_tool/resource.py`（新）：`ImageResource`（id/image/description/editable）+ `ImageStore`（`open`→只读全景、`draw`→新资源或原地覆盖、`export`→bytes）。
- `cogos/img_tool/__init__.py`：导出 `ImageResource`/`ImageStore`/`draw`。
- 测试：`tests/img_tool/test_resource.py`（11 个）+ core/stub/cli 补 draw。

**验证：全量 937 passed 无回归**（基线 915 → 926 → 937）。真实图 `detail.jpg` smoke 已验证 open/draw/覆盖/只读拒绝。

## 下一步：手动走 V1 定位循环（还没做）

用机械 draw + `ask_vision.py`（`/tmp/kilo/vision/ask_vision.py`，LmClient 视觉模型一条命令验证）串定位闭环：

```
看全景 → 想指目标 → 给粗糙坐标 → draw 标上去 → 看标偏哪 → 调整坐标再 draw → 标准了 → extract(region) 取子图看内容
```

**V1 要验证的三个点**（重点先砸 V1）：
1. **region 形式**：LLM 自然给的是归一化坐标 / 比例"左下1/4" / 纯语义？→ 决定 checkpoint-12"关系树 vs 全图坐标"和 18"坐标约定躲不掉"怎么落地。
2. **定位准不准**：在**清晰全景**上还犯 17 那种"落到 12345"的错吗，还是只在模糊全景错？
3. **收敛/停**：一次到还是迭代、怎么修正、怎么判"读到了"和"读不到"。

判据要客观（拿图上客观位置核对），不能听 LLM 声称（17 的教训）。

## 后置（本次明确不做）

- 资源生命周期：纯内存，LRU 淘汰/落盘后置。
- `open` 未走 img-cli 的 mem budget 检查（与预算机制脱节）。
- 未接 agent registry / ToolSpec：契约依赖 V1 结果，闭环走通再定。
- draw 与 extract 的衔接（star 点 → 定 range → region）待 V1 摸清。

## 参考

- `status.md` — 全项目状态入口（当前进行中 = checkpoint-18）
- `checkpoint-18.md` — 架构反转结论（主 LLM 自己看 + 工具按需加载 + 痕迹擦除）
- `checkpoint-17.md` — open 已通 + 定位失败实证 + `ask_vision.py` 用法（**须 python3.11**）
- `codebase.md` — 代码认知（img_tool 段，需补 draw/resource）
- 测试图：`/tmp/kilo/vision/detail.jpg`（全景读不出小字 `(456,123)`，适合 V1）、`p062.jpg`
