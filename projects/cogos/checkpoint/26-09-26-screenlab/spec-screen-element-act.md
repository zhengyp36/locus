# draft｜第 8 步：元素动作（`act element`）语义稿 · 2026-09-22

> ⛔ **整份作废（2026-09-22）**：a11y 路线已判为不做（图/pointer 一条腿）。
> 替代结论见 `rationale-screen-a11y-drop.md`；代码在分支 `archive/a11y`。
> 下文仅作历史/负结果参考，**不再作为实现依据**。
>
> **状态**：🔶 第 8 步开工前决策（2026-09-22 YZ 同意思路，落码中）。
> **依赖**：`spec-screen-client-api.md` §3（`act` 已有 `element` 一格）+ §4·5（位置基准归服务端）+ §2·D9/D11；`spec-screen-ledger.md` §4·3（世代校验）。
> **本稿纪律**：双栏（`[目标]` / `[方案]`）；反证句自检；作废即删名。

## 0. 一句话

`element` 这一格**不是"用 a11y 驱动"，而是"用 a11y 定位、用可换引擎执行"**。它要交付的能力是**稳定地动一个语义元素**（目标 2/3 的稳定性），反检是后续调引擎的事。

## 1. `[目标]`（引自 §5.1，编号一致）

2. 账户有一块**可操作的图形界面**，发动作能读回结果（闭环）。
3. 操作要**像真人、不被检测**；可逐步实现，方向能加固。
7. agent **只面对客户端**，不面对平台细节。

## 2. `[方案]` 决策 A：元素引用语义（wire 的 `id` 是什么）

**问题**：a11y 树里没有稳定身份；`path` 是从 root 起的**原始子索引链**，中间任一子节点增删都会让链指向**另一个节点**。

**判定**：
- wire 的 `id` 是**服务端签发的不透明串**（客户端只回传，不解析）——合 D9（不泄平台细节）。
- 串内打包：`捕获时的 path + role + name + center + 世代号`。
- act 时服务端**按 path 重走**（忽略裁剪策略，按原始索引下降），到点后**校验 role/name 一致**（name 为空时退化为 role + center 邻近）；**不一致即拒绝，不尽力点**。
- 客户端拿到的 `id` 只在**签发它的那次捕获的世代内**有效（合 D11）。

**代价**：客户端必须"看着树、拿着该帧的 id 去点"，跨帧复用 id 会被拒。这是有意的（防"看着这帧、点着那帧"）。

## 3. `[方案]` 决策 B：写路径的超时语义

**问题**：读腿超时可安全重试（幂等）；写腿超时**不知道动作是否已落地**。

**判定**：
- a11y 写 helper 被硬 timeout 杀掉时，一律回 **`unknown`**（不是 `failed`），**绝不自动重试**（重试可能点两次）。
- 未落地语义（拒绝、找不到、无 action）回**明确错误码**，可重试。
- 服务端对 `unknown` **不自动降级到 pointer**（否则等于重试）。

## 4. `[方案]` 引擎与降级

- 统一接口"对元素动"，引擎可换：`element_engine ∈ {do_action, pointer@center}`（`SCREENLAB_ELEMENT_ENGINE` 或请求字段 `engine` 覆盖）。
- 默认 `auto`：先试 `do_action`；**无可用 action 且节点有 rect** 时降级 `pointer@center`，返回标 `degraded=true`。
- **path 校验失败不降级**（树已变，不能猜）。
- 无 rect 且无 action → 报错。

> **实测修正（2026-09-22，晚）**：早先"Chrome 不暴露 AT-SPI action"是**误判**——根因是我们调了不存在的 `Accessible.get_action_count()`（正确 API 是 `get_n_actions()`），异常被吞后每个节点都成了"无 action"。修复后 Chrome 树里 **215/286 节点有 action**，且 `do_action` **真的会触发**：网页 `<button>` 暴露 `['press','showContextMenu']`，`engine=do_action` 选中 `press` 后页面 JS 执行（标题 DA0→DA1，`degraded=false`）。
> 含义：`do_action` 在本机 **可用且更稳**（不依赖坐标），`auto` 默认走它；`pointer@center` 仍作为无 action 节点的降级。**但注意**：`do_action` 不产生真实指针事件序列，若日后"像真人/远端反检"上档，应按场景切到 pointer 引擎——这正是"引擎可换"的用处。

## 5. `[方案]` helper 写模式

- `a11y_helper --act --path a,b,c [--role R] [--name N] [--center x,y] [--action NAME]`：
  一次进程内**重走 path + 校验 + `do_action`**；输出一行 JSON（含解析到的 role/name/rect 与所用 action/index）。
- action 选择：给 `--action` 则按**名字匹配**（大小写不敏感）；不给则按偏好序 `click / activate / press / do default / jump` 取首个命中，只有唯一 action 时取之，其余回 `ambiguous_action`。
- daemon **绝不 import gi**；写模式仍是子进程 + 硬 timeout（见决策 B）。

## 6. `[方案]` 明确不做

- **不做 element 级别的"等稳定/等出现"**（协调在语言层）。
- **不做跨帧 id 迁移**（换帧即换 id）。
- **不把 path 结构暴露进客户端契约**（只回传不透明串）。
- **不做反检参数**（拟真度/延时/随机化不进签名，沿用 `spec-screen-client-api.md` §4·7）。

## 8. `[方案]` 边界：观测归 agent，机制只给方法（2026-09-22 YZ）

- 动作是否**生效**是**语义判断**；**要不要观测由 agent 决定**。机制**不代做观测**，只提供观测**方法**。
- 机制已提供的方法：`capture`（带 `since_hash` 回 `changed`、发新世代）、`state`（当下状态 / 指针 / 输入者）、`act` 消耗世代（迫使想继续操作的 agent 先 `capture`）。
- 工具侧只做**说明与建议**：建议 act 后 capture 观察，机制不代判生效。
- **收回**一个错误倾向：曾想"act 后服务端返回 `changed`"——那是机制代做观测，越界。
- **已删（2026-09-22）**：`op_act` 动作后自做一次像素 grab 并回 `hint.frame_hash`，属"机制弱观测"且被光标移动污染。已移除：`act` 只回"受理结果"（`{ok, op, acted}`）；观测交给 agent 的 `capture`。


## 7. `[方案]` 本轮实测（2026-09-22，agent1，全过）

测试脚本已入库：`cogos/tests/screenlab/e2e/`（`act_element_e2e.py` + `README.md`），本轮合并提交 **`bab728e`**（分支 `feat/screenlab-p2`）。

- **引用签发**：`capture --mode tree` 每个节点都带 `id`（194/194，含 `g=pid-gen`）。
- **语义定位 + 真实点击**（强 e2e）：页面 `<button onclick="document.title='SL1'">` → 按 `role/name` 定位到按钮 → `act element`（auto，降级 pointer）→ 点击落在按钮中心 → **帧标题由 "SL0" 变 "SL1"**、按钮 `states` 出现 `focused`。证明：语义定位 + 真实指针事件 + 可观测效果，闭环成立。
- **校验拒绝**：篡改 `id` 里的 name → `path_mismatch`，**未点击任何东西**。
- **跨帧拒绝**：用上一世代的 `id` → `stale_ref`。
- **do_action 真的会触发**（修复 API bug 后）：网页按钮暴露 `['press','showContextMenu']`，`engine=do_action` 选中 `press` → 页面标题 DA0→DA1，`engine=do_action, degraded=false`。
- **写路径语义**：`engine=do_action` 对**确实无 action** 的节点 → `no_action`（**不降级**）；timeout → `unknown`（代码路径，未实测触发）。
- **踩坑**：`Atspi.Accessible` 没有 `get_action_count`，是 `get_n_actions`；用错则"全树无 action"且**静默**（异常被吞）。已修 `a11y_helper._actions`。
- 单测：`python3.11 -m pytest tests/screenlab` → **32 passed**（含 `elements` 引用语义 + helper `do_action` 分支假树测试）；全仓 `python3.11 -m pytest tests` → **1230 passed, 4 skipped**。
- e2e（入库后）干净复跑 **all checks passed**：do_action 生效、篡改拒绝且无副作用、stale 拒绝、pointer 命中中心。

