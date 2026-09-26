# handoff｜交接给新会话 · #62 → #63（视觉 / 传输讨论 · 续）

> 接 #61 的那个新会话 = **#62**。本会话（#62）：**视觉工具脚本化 + 传输/看屏分离讨论**（含子分支 62a/b/c 三平台屏变实验，已合并）。
> **规则/环境不在本文件**——先读 `screenlab-rules.md`。
> **硬性要求：新会话读完即停，不做任何操作（不抓屏 / 不跑命令 / 不读图片），等 YZ 切会话。**

---

## 复制这段作为新会话的第一句

```
接 #62。本会话继续「视觉 / 传输」讨论，读完停下等 YZ 切会话，不要动手。
按序读（纯文本，勿读任何图片，勿跑命令）：1. ../checkpoint/screenlab-rules.md；2. ../checkpoint/screen-assist-status.md §0；3. ../checkpoint/design-vision-scripting.md（全部）；4. ../checkpoint/screen-change-detect.md；5. ../checkpoint/handoff-screen-62.md。
硬性约束：读完不要执行任何命令（不要 terminal/bash/glob/grep）、不要 capture、不要把图读进上下文；只回一句「已读完，待命」，然后等 YZ 切会话。
```

---

## 本会话做了什么（#62）

1. **视觉工具脚本化**：工具实为 cogos 的 `cogos/image_ctx/`（`see`/`mark`/`adjust_mark`/`unmark`/`coord`）+ `cogos/cog_ctx/`（上下文 K 轮老化）——非 `research/vision/` 归档。讨论"如何给 kilo 先用"，产出 `design-vision-scripting.md`（已定 1–16、待定 A、传输修正清单）。
2. **传输 / 看屏分离**：起子分支 **62a(X11)/62b(Android)/62c(Windows)** 做屏变感知实验，合并为 `screen-change-detect.md`；F 由"待定"变"已定"。
3. **未改 cogos 产品码**；只写 checkpoint 文档（`design-vision-scripting.md`、`screen-change-detect.md`、本文件、status §0）。

## 已定结论（要点；全文见 `design-vision-scripting.md` 1–16）

- **核心信条**：模型只看语义（框/看/mark），几何（缩放/crop/坐标换算）全由工具做；**裁剪/缩放唯一发生在 `render`**，画面出了工具就冻结。
- **工具机制**：模型只在 `@窗口` 动作，程序算 `@全图`/像素；`coord` 出 `@原图` 归一坐标。状态全在 `Domain` 内存（FIG=Domain 内全局 id；ANNO=per-FIG，引用须成对 `(FIG, ANNO)`）；脚本化要加 `save/load` + 每次改状态后落盘 + id 计数器入 state。
- **看图**：`image_ctx` 缓存是真 PNG，`Block.image` 是路径；kilo 直接 `read` 当附件（非 base64）。
- **capture 与视觉工具分工**：默认 capture **整屏原生**一帧 → 视觉工具全权；`capture` 的 `center/size/max_dim` 不作语义缩放，仅传输兜底。
- **传输与看屏分离（F 定论）**：**推变化事件（原生 damage + `generation`）+ 按需拉整帧 + 客户端按版本缓存**；脏区只作变化信号、不做像素级增量重建；**不做帧流**（YAGNI）。
- **机制层 vs 模型层**：机制只给「变化事实 + 素材（可取脏区像素）」，**不做判断/门闸/语义标注**；模型分析"变的是什么"、决定看/等/动手/放弃，全程有界。`act` **不等待无变化**，`generation` 不绑像素变化。
- **B/C/D/E 不再讨论**（工具问题不在封装层验证 / 模型自决 / 不做 grid / 不做脚本链验收）。

## 待定 / 下一步讨论

- **待定 A（帧身份）**：推荐 = **帧按内容寻址落盘**（`<task-root>/<blob_sha>.png`），使"同 path 幂等"语义正确；不同帧→不同 Source；**不改库**；`images/` 增长靠"按任务开域、收尾整清"控制。残余：capture 裁窗/`max_dim` 是否保留兜底（倾向先不保留，Android 全屏 PNG ~65KB）。
- **产品码修正清单**（`design-vision-scripting.md`，待 YZ 定）：杀 `daemon.py:296` 每帧 PNG sha256；Android 投影采集替代 `screencap -p`；X11 评估 XDamage；Windows DXGI。
- **视觉工具脚本化落地**（设计已定、未实现）：CLI 薄适配 + `Domain` state 持久化 + 结构化输出；先做 `see`/`mark`/`coord`。

## 锚

- 设计/已定：`design-vision-scripting.md`（+ 待定 A、传输修正清单）
- 实验：`screen-change-detect.md`（X11/Android/Windows 原语 + 实测）；探针 `tools/android-probe/`、`tools/win/62c/`
- 工具代码：`cogos/cogos/image_ctx/`、`cogos/cogos/cog_ctx/`、`cogos/cogos/img_tool/core.py`
- 前情：`handoff-screen-62a.md`/`-62b`/`-62c`（分支）、`handoff-screen-61.md`；规则 `screenlab-rules.md`、活文档 `screen-assist-status.md` §0/§4
- 父会话（#62）session id：`ses_f27b92b04ffeF5hz7zAFZPi026`（title `screenlab #62 - 电脑/视觉-讨论`）；本交接转 **#63**。
