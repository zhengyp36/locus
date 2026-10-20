# vision 像素回灌 · 两层架构（2026-10-20）

> 状态：**已落码**（agent `62d9620` + lm-service `3409821`），真机验收通过。承 `scratch/2026-10-20-vision-image-feedback.md` / `attachment-mechanism.md`（已收口删除）。

## 问题

body.vision 的 `see`/`mark` 返回 `image`（image_ctx 渲染 PNG 路径），被 `_vendor_tool_message` json.dumps 成字符串，像素从未到达模型输入。

## 结论 · 两层架构（无 A/B 选择）

- **内部 material**：tool 消息 content 结构化带 `image`（**data URL，落 material 时提前编**）；附件＝工具返回的原始内容，归属 tool 消息。
- **wire 序列化**：`assemble_tool_messages` 把带 data URL 的 tool 消息编译成「tool 文字（剥 image）+ user 图（`image_url` part）」——OpenAI 规范图像只能进 user 消息；user 图统一放该轮 tool 之后（配对连续、不交错）。

## 关键实现点

- **提前编分叉**：`materialize_tool_result`（`tool_base.py`）image 路径→data URL；`consciousness.on_tool_call` 分叉——`flow.process` 记路径版（段不膨胀）、material 落 data URL 版。
- **路由时序缺口**（评估补入，草稿「router 无需改」作废）：`select_model`（`scheduler.py`）在序列化**前**运行，`infer_modalities` 原只认 content list 的 `image_url` part → 补识别内部 tool content dict 的非空 `image` 字段，否则选错模型。
- **ToolDef 接口预埋**：`transform_call`/`transform_result`/`pair`（可空函数，None=恒等）+ `config`（不定型，factory 复用）；只落接口、不实现 transform。

## 验收

- 真机 vision_probe：模型从图读出 `TIGER7`（像素到达）。
- tests/lm_service 85 passed（新增拆图重排 + 路由识别测试）；全量 397 passed / 3 skipped。

## 被否 / 遗留

- **被否**：「图像并入 tool 消息数组」（偏离 OpenAI 规范，不赌）；「延迟编」（序列化层读文件、改 async，改动面大）。
- **遗留（归远景附件机制）**：老化/transform 实现；`cog_ctx` 固定格式编译、K 轮老化；material 存 data URL 的膨胀由老化解决。
- **既有 flaky（与本轮无关，未修）**：`test_browse_before_paginates_older` 毫秒级时间竞态（30 次 PASS=11/FAIL=19），属 chat.browse 的 `before` 分页边界，超本轮范围。
