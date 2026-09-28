# cogos toolbox 修复批（2026-09-28）

> 执行会话完成前一讨论会话列出的顺序 `6 → 1+2 → 3 → N2 → 4`，并裁断 N1。代码提交 `225c902`（cogos master，已 push）。
> 前一讨论工作稿：`scratch/2026-09-28-cogos-toolbox-improvements.md`（6 条建议 + N1~N4）。

## 修了什么（anchor）

- **fix 6｜重复外发 bug**：`cogos/agent/consciousness.py` 原按 `call["name"] == "send_msg"` 判去重（S3 暴露 `toolbox` 后恒假）→ 改为 registry 层记"是否已 send"：`tools.py` `_SEND_TOOLS = {send_msg, phone_send_file}` + `SendState`；`app.py` 让 exposed registry 与 impl registry **共享同一 SendState**；`on_message` 起始 `reset_sent()`、`on_done` 读 `registry.sent`。覆盖 message + file。
- **fix 1+2｜调用边界校验 + 可读错误**：`toolbox._validate_args` 在进实现层前按 `cap.params` 校验未知键 / 缺必填 / 类型，回结构化可读错误（如 `未知参数 'to'；本能力参数：target(必填) / content(必填)`）；不做模糊匹配或自动纠错。
- **fix 3｜help 去"绑定"行**：`catalog._render_capability` 删 `绑定：` 行（机制实现细节，模型用不到）。
- **N2｜catalog↔registry 启动期断言**：新增 `catalog.bindings_for_face` / `catalog.assert_bound`，`app._assert_catalog_bindings` 在启动时断言；fs/screen 条件面用 `allow_missing` 放行。

## fix 4 度量（真实 deepseek + FakeTelecom harness）

- 指标 = 往返数 `n_lm_rounds`；harness `../cogos/scripts/exp_agent_behaviour_probe.py`。
- **修复前干净基线**：help 使用 ~100%（`probe-result-10b.json` 10/10），外发 2 条/次，rounds 均值 5.25~6.40。
- **修复后（n=10，`/tmp/kilo/probe-result-fix10.json`）**：**外发 1 条 10/10**；**help 0/10**；10/10 仍先猜错 `to`，但边界错误即自纠；**`n_lm_rounds` 全为 4**。
- 结论：重复外发根除；"猜错 → 可读报错 → 一次自纠"链路成立，且比走 help 更便宜。

## N1 裁断（YZ 同意 A）

- **问题**：catalog 暴露 `computer.command.open`/`list`（`answer_auth` 仅声明、机制选槽未接），但 `toolbox` 对 observe/send/read/write/edit 强制注入**单一默认会话 id** → 模型无法操作自己刚 `open` 的会话，模型面出现"看起来能用其实不能用"的陷阱。
- **选 A（撤下）**：从 catalog 删 `open` / `list` / `answer_auth`。理由：单会话是本轮范围；撤陷阱与本批主线（机制面退出模型面＋错误便宜化）一致。
- **否 B（补齐 id 传参 = A2 多会话）**：多会话涉及会话 label 持久化、跨消息对象寻址，是独立设计；塞进 bug 修复会失焦，留 A2 再带回。
- 代码：`catalog.py` 删三个 Capability（附注释说明 N1-A）；`toolbox._NEEDS_SESSION` 去 `answer_auth`。

## 未决 / 搁置

- **N3**：`run` 固定 ~6s 有界等待可能截断输出且模型不知情（无 `wait` 参数）→ 待 YZ 确认是否感知/参数化。
- **N4**：`web_cancel` / `phone_cancel` 未进 catalog，模型无法取消长任务 → 待 YZ 确认是否有意。
- **建议 5**（按误差=切点记账）：搁置。

## 验证

- `python3.11 -m pytest tests/agent` → **272 passed / 3 skipped**。
- 全量 `python3.11 -m pytest` → 1276 passed / **1 failed**（`tests/image_ctx/test_p2.py` 缺 `/tmp/kilo/vision/vf6_repl_out_new/windows.png`，环境产物缺失，与本批无关）。
- 证据 JSON（临时）：`/tmp/kilo/probe-result-fix10.json`。

## 参考

- 行为证据：`entries/2026-09-28-cogos-toolbox-behaviour-probe.md`。
- 呈现实现：`entries/2026-09-28-cogos-toolbox-presentation.md`。
