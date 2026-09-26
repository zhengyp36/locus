# handoff｜→ #73（v2 线：先与 YZ 对齐接口，再落接入）

> 规则 / 环境不在本文件——先读 `screenlab-rules.md`（含交接阈值 **150K**）。
> 本文件由 #72（目标对齐 / 工具线盘点会话）写给 **#73**；#73 完成后**就地更新本文件**（写结果 + 给后继首句）。
> 上游：`screenlab-tools-review.md`（#72 盘点）、`handoff-screen-71.md`（#71 收尾）。目标：`spec-screen-1.md §0.0`（唯一约束）。设计：`design-vision-computer-fusion.md`。

---

## 复制这段作为 #73 的第一句

```text
接 #73。任务 = 持有 graphics 的 v2 线：先把 v2 模型面接口形状与 YZ 对齐，再落 v2 接入。现在【不要动代码】，等 YZ 在对话里提出讨论。

先按序读（纯文本，别动手）：
0. ../checkpoint/tools/README.md（先 source tools/env.sh）
1. ../checkpoint/screenlab-rules.md（规则；交接阈值 150K）
2. ../checkpoint/screenlab-tools-review.md（#72 工具线状态盘点）
3. ../checkpoint/design-vision-computer-fusion.md（v2 设计：§1 第一原则、§3 模型面接口、§4 内化、§5 内部模型）
4. ../checkpoint/screenlab-work.md §状态（#62c→#72 过程）
5. ../checkpoint/handoff-screen-73.md（本文件；含 #72 的目标推导、v2 定义、四个决策口）

状态：工具线止步 Windows/Linux/Android；三平台"视觉×坐标闭环"原型 CLI（imgctx）已通并提交（cogos @ d89abd7, feat/screenlab-p2，工作树干净）。关键缺口 =【v2 未接入】：cogos/agent/ 零 image_ctx 引用——agent 还碰不到视觉闭环（原型 ≠ 工具）。

v2 = computer 工具的第二版模型面：模型只 look/zoom/mark/act；几何、图id/帧id、settle、transport、平台差异全内化；第一原则 =「工具必须保证模型作用在它看到的那张图上」。

本会话要做：① 先与 YZ 对齐 v2 接口形状（本文件 §四个决策口）；② 对齐后再落 v2 接入（先在 X11/Windows，act 能力更全）；③ Android 动作补齐排在接入之后（按冻结后的动词集补）。对齐前不改代码、不 commit。

约束：10min 闹钟（与 YZ 讨论时免）；ctx ≥150K 交接；裁决由目标 §0.0 推、能推自决；阻塞→飞书通知 YZ 后先做不阻塞的；允许 commit/push（不 tag），提交前跑测试。
⚠️ 文档是二手描述，动手前以代码 / 实测为准。
```

---

## #72 的目标推导与结论（素材）

### 目标层级（为什么 v2 是这一步）

- **顶层目标**（`design-selfdrive-agent.md`，唯一权威）：自驱 agent = 一个在转的环 + 两条链条；**外圈**（事件→弧→后果→写回）让它会动，**内圈**（经历→升格→目的→距离→燃料）闭合才叫自驱。最终态 = 双自驱共驱。
- **工具层是地基**：给 agent 感官和手脚，产出**后果**（工具结果/对方回应/沉默）与**事件**（推面），喂外圈的"后果绑定"。
- **工具线收束点（YZ 定）**：止步 Windows/Linux/Android；"agent 自己有电脑"这一能力面视为足够。不扩 macOS/Wayland（记后置）。

### 工具线现状（`screenlab-tools-review.md` §1–2）

- 已通：`screenlab/tools/imgctx.py` 原型 CLI，三平台"使用角度"验收全通（独立真值，非 selftest）；产品增量已提交（DXGI 后端 / 分块 diff / image_ctx 持久化 / session-start 默认值）。
- **关键缺口 = v2 未接入**：`cogos/agent/` 零 `image_ctx` 引用（已核对）。**原型通过 ≠ 工具可用**——不接入，graphics 对外圈不产生任何可绑定的后果。

### v2 是什么

- **v1（现状）**：`computer` 工具图形面 = `screen_capture` / `screen_act`；模型自己给归一化坐标。
- **v2（设计已定、未实现）**：把 `cogos/image_ctx` 融进 `computer`，模型面只 `look / zoom(区域) / mark(区域) / act(位置)`；几何、图id/帧id、settle（判稳）、transport、平台差异**全内化**。依据 = 第一原则「工具必须保证模型作用在它看到的那张图上」（`design-vision-computer-fusion.md §1`）。
- **"v2 接入" = `design-vision-computer-fusion.md §9.2`「融合适配：computer tool 包 cogos/image_ctx」**。

### 排序结论（#72 建议，待 YZ）

**定 v2 接口形状 → 落接入（先在 X11/Windows）→ Android 动作补齐。** 理由：

1. v2 接入是唯一阻塞项；Android 补齐谁都不阻塞。
2. Android 补齐要动 `key/type/scroll` + "launch app/URL"（后者在 `screen/1` 里**尚无归属**）——正是 v2 模型面要冻结的动词集；先补有返工风险。
3. 从目标看 Android 不是关键后果源；关键在"有意志的对方"（phone/3a 人通道）。

### 四个决策口（`screenlab-tools-review.md §3`）+ #72 倾向

1. **v2 接口形状**（模型面是否只 `look/zoom/mark/act`、几何/transport 全内化）——倾向：是。
2. **act 硬保证**（持久连接/broker vs 重抓近似）——倾向：**并进 v2 一起定**，不单独立遗留（`ScreenChannel` 本就是每机单连接、代持 `snapshot_id`，可能就是它的自然形态）。
3. **Android 动作补齐是否算"工具收尾"**——倾向：算，但**排在接入之后**，按冻结后的动词集补；最小任务集 = `launch(app/URL) + 导航(HOME/BACK/swipe/长按) + 打字`。
4. **transport 修正**（每帧 PNG 编码/哈希、Android raw MP、X11 XDamage）——倾向：后置（性能，非阻塞）。

### 一条边界（防止"收尾"收不完）

- **世界交互工具**（term/fs/graphics/phone/transfer/draft/timer/time）→ 工具收尾。
- **机制面向工具**（`load`/`retrieve`/`record_segment`/`promote`/`consolidate`/`replay`…，`design-agent-tools.md §3`）→ **它们是外圈/内圈的零件本身**，归回路阶段，别并进"工具收尾"。

### 与回路的关系（提醒）

- 工具收尾后，主线第一刀 = "把已写下的后果接到一个读者上"（`design-selfdrive-agent.md §11`）；阻塞在 §12-① 四缺口（权重构造式 / `T`·活跃度公式 / 第一刀可观察判据 / 落地位置）。
- 若目标是"自我从经历长出来"，长期最关键的是**有意志的对方**（人通道），不是更多机器。

## 锚

- 规则：`../checkpoint/screenlab-rules.md`；目标：`../checkpoint/spec-screen-1.md §0.0`
- v2 设计：`../checkpoint/design-vision-computer-fusion.md`；工具机制：`../checkpoint/design-vision-scripting.md`
- 盘点：`../checkpoint/screenlab-tools-review.md`；工作单：`../checkpoint/screenlab-work.md`
- 代码：`cogos/screenlab/tools/imgctx.py`、`cogos/cogos/agent/`（v2 接入点）、`cogos/cogos/image_ctx/`、`cogos/agent/impl/graphics.py`（ScreenChannel）
- 回路总纲：`cogos/docs/design-selfdrive-agent.md`；工具权威：`cogos/docs/design-agent-tools.md`
