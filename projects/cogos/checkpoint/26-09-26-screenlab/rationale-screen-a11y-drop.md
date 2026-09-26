# decision｜不做 a11y：图/pointer 一条腿 · 2026-09-22 #22.1

> **性质**：对 `handoff-screen-22.md` §三·2（"a11y 树 = 可选语义索引"）的**再收窄**。
> 新口径：**不用 a11y**。语义一律由视觉侧解决（图 / 后续的检测与 OCR）。
> **纪律**：双栏（`[目标]` / `[方案]`）；反证句自检；作废即删名。

## 0. 一句话

a11y 是**为辅助技术设计的**，不是为 agent 设计的。它唯一独有的事（把语义声明给屏幕阅读器）**不是我们要的能力**；我们要的感知 / 落点 / 像真人，图 + pointer 全包。故不做，代码与结论分离归档。

## 1. 判定（2026-09-22 YZ）

- `[目标 2]` 可操作：图 + pointer 满足。
- `[目标 3]` 像真人 / 可加固：**只有真实指针事件能往上走**；`do_action` 天生不产生指针事件序列。
- ⇒ 树在两条目标上都**不是必需**，且它独有的"精确语义"是便利、非能力。

## 2. 为什么不是"保留但默认关"（反证）

"默认关掉成本≈0"不成立：只要还在，`capture` 就回 `elements`、API 就带 `element_id` / `engine`，**接口与心智模型被它塑造**——这才是真成本。且它擅长的场景（大页面批量语义操作）当前零场景，持有即纯负债。"以后可能要"也不成立：真要回来时是**重新设计**（web 走 CDP、原生走检测器），不是复用这套 AT-SPI helper。

## 3. 负结果（照抄可用，别重踩）

1. **走树成本是结构性的**：AT-SPI 每节点多次**同步 D-Bus 往返**（role/name/actions/states(7次)/rect/children）⇒ 实测 **~7ms/节点，331 节点 ~2.5s**；整桌面上万节点几十秒，helper 硬 timeout 一到就被杀 → 产出 `truncated`。真 AT（Orca/NVDA）靠**长驻连接 + 暖缓存 + 事件增量**掩盖，我们每次起新 helper ⇒ 无缓存。做对代价很大（长驻 helper 会请回 GI 调用阻塞/挂死；还要事件 + 缓存失效 + 世代对账，AT-SPI/UIA/Android 各做一遍）。
2. **"有 action"不含信息量**：Chromium 给每个 DOM 节点挂 `showContextMenu`（通常还有 `doDefault`）⇒ 真信号只有 `{click, activate, press, jump}`。任何 keep 规则都是经验补丁。
3. **扁表丢结构**：react.dev 194 项 ≈ 47KB；默认 40 条被浏览器自身 UI 占满（窗口按钮/工具栏/地址栏），页面内容一条不进。同名元素（logo 与正文的 `React` link）**扁表无解、树有解**——但这是"树相对扁表"的优势，不是"树相对图"的优势。
4. **`do_action` 不产生指针事件**：绕过 OS 输入栈 ⇒ 反检测上吃亏，也难保"动作生效"。
5. **相关性裁剪（`KEEP_ROLES` / "有名 or 有动作" / 骨架）是机制代判"看什么"**：属于 §5.0/`spec-screen-element-act.md` §8 禁止的那类，应回退。
6. **平台四分五裂**：AT-SPI / UIA / AX / Android 四套模型各写一遍。
7. **既有语义债**：元素引用绑世代，而 `snapshot_id` 仍是连接级（§⑥）。

## 4. 代码怎么了

- **归档分支**：`archive/a11y`（= 剥离前的 `feat/screenlab-p2` HEAD，含全部 a11y 代码与其单测/e2e，可 `git show` / `cherry-pick` / 运行）。**不入主线**，也不算幽灵模块。
- **主线摘除**（a11y-only）：
  - `screenlab/service/a11y_helper.py`、`elements.py`（删）
  - `backends.py` 的 `A11yTree`、`platform_backends.pick` 的第 4 返回值
  - `daemon.py` 的 `capture mode=auto|tree`、tree 归一化/世代、`act element`（含 `engine`、pointer-fallback）、`ElementError` 分支
  - `proto/protocol.py` 的 `CAPTURE_MODES`、`ACT_OPS` 去 `element`
  - `proto/client.py` 的 `mode/tree_max_*`、`cli.py` 的 `--mode/--element-*`
  - `cogos/agent/tools.py` 的 `elements` 输出 / `engine` / `element_id`；`impl/graphics.py` 的 `element_digest`
  - `session-start.sh` 的 a11y 桥（`toolkit-accessibility`）、`session-stop.sh` 的 helper 收割
  - 单测/e2e：`test_a11y_act / test_elements / test_tree_trim / act_element_e2e`（删），`test_screen.py` / `tool_loop_e2e.py` 改像素腿
- **连带作废**：`spec-screen-element-act.md`（整份）；`spec-screen-client-api.md` §3 `act` 的 `element` 格与 §4·14 的"树"一支。
- **留住的通用件**（没连坐）：`1dfbdb5` 的 auto-open 修 bug；`ledger.py` + 动词面（open/close/grant/revoke）；账户 systemd user bus 基建；blob→path 模式；e2e 闭环骨架。

## 5. 什么时候该回来（下注条件）

出现 **"agent 反复在大页面做批量语义操作"** 的真实场景时，按场景重引入：**web → CDP 的 `Accessibility.getFullAXTree`**（廉价可靠），**原生 → 检测器（OmniParser 类）**。都**不是**今天这套 AT-SPI helper。
