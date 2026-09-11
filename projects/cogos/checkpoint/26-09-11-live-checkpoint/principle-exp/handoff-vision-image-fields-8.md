# handoff｜坐标基准统一(宽对宽/高对高) + P3 目的层任务 A/B LLM 探针双过 → 下一步"衍生推理"档（09-08 深夜收口）

> 2026-09-08 深夜。上游：`handoff-vision-image-fields-7.md`（P3 落码 + P4 签证收口 + P3 目的层 vf6 探针前置）。本会话完成：**① 坐标系基准统一**（`@全图`/`@窗口` 的 size 分母改"各自维度"，即宽对宽、高对高）+ **② P3 目的层任务 A/B LLM 探针均通过** + **③ 记一条遗留**（坐标规则动态注入暂缓）。新会话只读本文件即可接手；接口/细节以本体 `design-vision-image-fields.md` 为准，验收以 `design-vision-image-fields-checklist.md` 为准。

---

## 一句话状态

- **代码/几何层**：坐标基准从"size over 短边"统一成"**size over 各自维度（宽对宽、高对高）**"，全量 pytest **992 passed** 无回归。改动**未提交**。
- **LLM 层（P3 目的层探针）**：**任务 A**（纯文字锚 → 重建窗口）与 **任务 B**（图块超龄被摘 → 纯锚重定位）**双双通过**，重放 delta 全 0。
- **下一步 = "衍生推理"档**：用锚去做**新的相对窗口**（如"在该窗口再往上一点"），这才会真正触到**坐标教学的必要性**（即那条暂缓的动态注入规则）。本轮任务 A/B 验证的是"锚自含可重定位"，**不含**"用锚做衍生推理"。

---

## 本会话产出（新会话必须知道）

### 1. 坐标系基准统一：size over 各自维度
- **改动**：`cogos/cogos/image_ctx/view.py`（`window_px`/`px_rect_to_window`/`view_to_window` 的 size 分母从 `short_side` 改 `orig_w`/`orig_h`；docstring）+ `domain.py`（全图窗口 `size=[1.0,1.0]`）。
- **测试**：`tests/image_ctx/test_p1.py` 里为旧"÷短边/被宽高比放大"写的断言改为宽对宽。
- **效果（新不变式，sanity 已确认）**：
  - 全图窗口 = 干净的 `s(1.000,1.000)`。
  - **参考图 = 全图时，`@窗口` 与 `@全图` 的 c/s 逐位一致**（无换算、不用心算）。
  - 锚格式例：`F:1001 | 1357×764 | @全图 c(0.188,0.043) s(0.120,0.030) rect → 位图 163×23`。

### 2. P3 目的层 LLM 探针（`/tmp/kilo/vision/p3probe/`）——任务 A + B 双过
- **`taskA.py`（任务 A）**：只给锚文字（无图），问"重建该窗口"→ 模型照锚填值 → 回放 delta 全 0。（taskA.py 里 SYSTEM/TASK 带坐标教学。）
- **`taskB.py`（任务 B）**：真实 `FigContextManager(step/k/live)` 走老化——一图轮 `next(act)` + 连续 `advance()` 至超龄 → 验证"图被摘 / text 留底 / annos 已清 / live=0" → 然后**只给幸存锚文字**（无图、**无坐标教学**，用真实 `SYSTEM_HINT`）问重定位 → 回放 delta 全 0。
  - 关键：**口径①（纯锚、无规则）就过**——证明锚**自含**，无坐标教学也能重定位。

### 3. 遗留一条（已记 `locus/projects/cogos/ISSUES.md`）
- **坐标规则注入：静态前置 → 应随图动态注入（暂缓）**：现状是静态 system 前置（`FigContext.system_prompt()`/`SYSTEM_HINT`）；后续想改成"有图才注入、只一条、随最近图走、无图则删"。附带判据：图全消失后模型纯锚重定位必须能行——**本轮任务 B 已实证这点**。

### 4. 读法（诚实，别过度解读）
- **已被证明**：① checklist §139 核心——"图超龄被摘后，文字自含锚能否让模型重建窗口"→ **能**，且是在无坐标教学下。② 坐标统一后 `@窗口==@全图`（全图 ref），锚即答案，模型抄即对，无换算。
- **仍未覆盖**：用锚做**衍生推理**（新相对窗口），那才是坐标教学真正需要的场景。任务 A/B 的"重建"本质是"读锚并照填"，非"理解后再派生"。

---

## 关键决定（已定案/暂缓，新会话别推翻）

1. **坐标基准统一**：`@全图` 与 `@窗口` 的 center/size 均**分轴 over 各自维度（宽对宽、高对高）**；`@全图` size 不再用短边。全图窗口 size `[1.0,1.0]`。
2. **任务 B 判据 = 口径①纯锚无规则**（对应 ISSUES 那条自含判据/checklist §139）。本轮已过。
3. **坐标规则动态注入**：暂缓。保持静态前置（`SYSTEM_HINT`），后续再改成"随图动态注入/无图则删"。
4. P1/P2/P3/P4 边界（上游定案，勿踩）：`image_ctx` 只管图对象状态；`fig_meta`/`clear_fig_block` 是给上下文管理器的接口面；老化归 `FigContextManager`；去重归身份层。

---

## 下一步（到新会话讨论"衍生推理"档）

- **目的**：验证"用锚做新窗口"（不是重定位原窗口，而是在该窗口基础上派生/换相对框），检验**坐标教学的必要性**——这也是那条例外（动态注入规则）真正上场的地方。
- **候选场景**：先给模型看锚窗口（文字），再问"在该窗口基础上往左上移一点、开一个更小的窗"，看它能否给出正确 `@窗口`（此时 `@窗口` ≠ `@全图`，因为 ref=子窗口盒）。若它在此**混淆**，就实锤"缺坐标教学"→ 推动态注入规则；若仍准，再评估其必要性。
- **判据**：重放后 `@全图` window 与目标真值 delta 接近 0；并记录"无教学"时是否出错（对照）。

---

## 运行

- 后端：`cd /home/zhengyp/work/A/cogos && python3.11 -m cogos.lm_service.cli server --port 11434`（会话级，每新会话重开）。KEY `ik_REDACTED`。
- 测试：`cd /home/zhengyp/work/A/cogos && python3.11 -m pytest -q`（需 python3.11；现 992 passed）。
- 探针：`cd /tmp/kilo/vision/p3probe && python3.11 taskA.py` / `python3.11 taskB.py`。
- 飞书：`cd /home/zhengyp/work/A/locus && python3.11 tools/feishu_notify.py "<文本>"`（默认 YZ）。

---

## 遗留 / 待办（非阻塞）

- **坐标规则动态注入**：暂缓（见 ISSUES）；"衍生推理"档若无教学会错，则推它。
- 代码改动（view.py/domain.py/test_p1.py）**未提交**；如需提交自行处理。
- 上游遗留（-7 已列）：超龄回收 `Source.registry`/`cache/` 积压、`detail=original` 未接、指纹 4 位小数/`estimate_peak` 误拒待实测、`desc/` canonical 层未落盘、视觉子系统融合后议。

---

## 关键文件

- 坐标统一改动：`cogos/cogos/image_ctx/{view,domain}.py` + 测试 `cogos/tests/image_ctx/test_p1.py`
- LLM 探针：`/tmp/kilo/vision/p3probe/taskA.py`、`taskB.py`（本会话 NEW）
- 遗留：`locus/projects/cogos/ISSUES.md`（坐标规则动态注入·暂缓）
- 设计本体（最终定稿）：`cogos/docs/design-vision-image-fields.md`
- 验收清单：`cogos/docs/design-vision-image-fields-checklist.md`（P1-P4 已勾，§139 探针残留）
- 上游实现：`cogos/cogos/image_ctx/*`、`cogos/cog_ctx/*`
- 上游交接：`handoff-vision-image-fields-7.md`（P3+P4）
