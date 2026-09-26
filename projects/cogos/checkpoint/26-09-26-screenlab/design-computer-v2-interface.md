# design-computer-v2-interface.md · computer 工具图形面 v2（模型面，封板 2026-09-26 · #73）

> **性质**：v2 **模型面接口形状**的封板稿。二手描述；动手前以代码 / 实测为准。
> **目标（唯一约束）**：`spec-screen-1.md §0.0`（agent 有自己的电脑；图形面与 `term`/`fs` 并列；能操作+有反馈；服务端只 mechanical、唯一智能在 agent 侧、图不转文字）。
> **上游**：`design-vision-computer-fusion.md`（本稿精化其 §3 模型面）、`screenlab-tools-review.md`（#72 盘点）、`handoff-screen-73.md`。
> **状态**：接口已与 YZ 对齐封板；未落码。实现顺序见文末。

---

## 0. 一句话
v2 = **图形面只做「抓屏 / 动屏 / 存屏」三个机械动作；「看图」统一到通用视觉面**。几何、图/帧身份、settle、transport、平台差异全内化。

## 1. 面分界（本稿核心决策）
- **电脑图形面（`screen_*`）**：只做**作用在屏幕上**的机械事——抓当前屏、执行动作、存当前屏。隐藏状态仅「current frame」一个。
- **通用视觉面（image_ctx）**：看 / 放大 / 标注 / 对比，作用在**任意一张图**上。看屏幕帧与看别的图**没有区别**，因此**不在电脑图形工具里**。

**导出**：图形面无 `zoom` / `mark` / 窗口 / 帧号 / 时间戳；看的部分复用 `cogos/image_ctx`。

## 2. 不变量
1. 模型给的一切位置/区域，**都相对「current frame」**＝最近一次 `screen_fetch`/`screen_act` 交给模型的那张图；工具负责全部换算。
2. **图/帧身份、snapshot、revision、区域链、换算、平台差异，模型全不可见。**
3. **一次 `screen_act` = 动作 + 确认**：返回操作后的整屏 + 落点标记；该帧成为新 current frame。
4. **settle 不暴露、不保证**：`screen_fetch` change-gated 短等；`screen_act` 有界 settle 且只回报「仍不稳」。
5. **抓屏只在 `screen_fetch` / `screen_act` 发生**；无窗口、无观测编号。
6. **`screen_save` 是唯一产生持久文件、也是保留授权控制点的动作。**

## 3. 图形面动词（模型面）

名称用 face 前缀（同 `terminal_*` / `phone_*`）：`screen_fetch` / `screen_act` / `screen_save`。
`region = "x,y,w,h"`、`point = "x,y"`，均**归一化、相对 current frame**。

### `screen_fetch()`
- 抓当前屏幕一帧，设为 **current frame**。
- 返回：图附件 + 文件路径 + `size:[w,h]`（可选 `stable`）。
- 内部：change-gated 短 settle（已稳立即返）。

### `screen_act(op, region=None, point=None, on_change="act", text=None, keys=None, dy=None, to=None, button=1, clicks=1)`
- **落点** = `point`，缺省 `region` 中心；位置相对 current frame。无 current frame 时拒绝（先 `screen_fetch`）。
- **`op` 枚举（冻结）**：
  - 位置类：`click`(默认) · `move` · `drag`(配 `to`) · `scroll`(配 `dy`)
  - 内容类：`type`(配 `text`) · `key`(配 `keys`)
  - 打开类：`launch`(配 `text`=app/URL，无坐标)
- **`on_change ∈ {"act","skip"}`**（默认 `"act"`）：目标区相对 current frame 有变时——
  - `"skip"`：**不动作**，返回新帧 + 变化说明；
  - `"act"`：照动作，但回报 `region_changed:true`。
  - 两者**恒带** `region_changed`。
- 返回：**操作后整屏附件 + 落点标记** + `region_changed` / `stable` / `acted|skipped`；成为新 current frame。

### `screen_save(path=None)`
- 把 **current frame** 落成**持久文件**，返回路径。
- 是「截屏能力」与**保留授权**的落点：存图=永久保留，受会话授权约束（见 §6）。

## 4. 通用视觉面契约（由 image_ctx 提供）
在**一张图片路径**上：看 / 放大(region) / 标注(region) / 对比两张图。
- **坐标契约（关键）**：不论嵌套放大多少层，**标注/回读的坐标恒是「你打开的那张原图」的归一坐标**（`image_ctx` 的 `@原图`，由 `anno_to_src` 保证）。
- 因此：模型在 `screen_fetch` 给的图上放大、标注得到的坐标，**直接就是 current frame 的坐标**，交给 `screen_act` 即可——**模型全程不做换算**。
- 现状：`image_ctx` 是内部库 + 原型 CLI，**尚未注册为模型面工具**。v2 落地依赖把它暴露出来（见 §7 风险）。

## 5. `on_change` 判断位置：客户端（agent 侧）
- `ScreenChannel` 持有 current frame（本地文件路径）。`screen_act` 时**先抓一张新帧**（settle 也要用），本地把两张图的目标区裁出、用 `screen/change.py::diff_bbox` **本地比对** → 得 `region_changed` → 按 `on_change` 决定 act/skip。
- **零图片过网、零帧索引**（比对两图都在客户端）。服务端只收坐标做注入。
- 与 §0.0 一致：服务端纯 mechanical；「模型看到的帧」只有客户端知道。
- 已知弱点：diff 到注入之间是 **best-effort 窗口**（TOCTOU），非保证。若成为问题，出口 = 把 `grab→校验→注入` 折进服务端一次调用、客户端只发目标区紧凑参考——归**决策口④ transport 后置**，不阻塞 v2。

## 6. 与授权的关系
- **看是瞬时的，存是永久的**：`screen_save` 是数据外泄性质，不等同于「能操作」。
- agent 自己的电脑：默认允许。
- 借用他人账户 / 与真人共屏：应挂在该会话授权上并**留痕**（哪块屏、哪次会话、何时）。
- §0.0 的「授权粒度」本身未闭合，保留权限比它更细 → 目标级待定；**先保守 + 可审计**，不阻塞 v2。

## 7. 与设计稿 `design-vision-computer-fusion.md` 的差异
- 设计稿把 `look/zoom/mark/act` 全放图形面。本稿把 **viewing 拆出**为通用视觉面：
  - 放大/标注/对比是**图像操作**，对屏幕帧、手机照片、网页截图一致，放图形面是重复造；
  - 图形面越小越好，隐藏状态只留 current frame。
- `look` 的「自动抓屏」是隐藏副作用 → 更名 `screen_fetch`（唯一抓取动作），不再有「有时推进状态」的视图动词。
- 删掉：窗口、帧号、时间戳、`back`、「谁推进窗口」。

## 8. 决策与理由（追溯）
- **三动词 + 视觉面**：usage-first + 统一看图；图形面只留机械动作。
- **`screen_` 前缀**：仓库 face 前缀约定（`terminal_*`/`phone_*`）；扁平注册表需消歧。
- **`act` 回操作后整屏 + 落点**：一次往返完成「动 + 确认」，也是模型对比「动作作用在哪」的唯一依据。
- **`on_change` 交回模型**：「该不该点变化中的区域」是语义判断，工具只机械比对 + 诚实回报。
- **`launch` 进枚举**：Android 最小任务集必需；现在冻结避免返工；唯一触协议处（`protocol.py:15` `ACT_OPS` 加一项）。
- **settle 内化**：fetch change-gated、act 有界，只回报不保证。
- **act 硬保证**：`ScreenChannel` 每机单连接、代持 snapshot = 天然的 broker，无需另建。

## 9. 实现锚（不改 `screen/1` 主协议，除 `ACT_OPS` 加 `launch`）
- 三 `ToolDef` 进 `make_screen_specs`（`cogos/agent/tools.py:1144`，注册于 `cogos/agent/app.py:251`），替换 `screen_capture`/`screen_act`。
- 视图/last-frame/落点逻辑搬进 `ScreenChannel`（`cogos/agent/impl/graphics.py`），复用 `screenlab/tools/imgctx.py` 已验的 `look/act` 流程；去掉进程式 CLI。
- region-diff 用 `screenlab/service/change.py`；标注/落点渲染用 `cogos/image_ctx`。
- 视觉面暴露：把 `image_ctx` 的 `see/mark/coord` 注册为工具（新 `make_vision_specs` 或并入）。

## 10. 记录在案的口（不阻塞 v2）
- 视觉面暴露范围（半阻塞：不暴露则「放大点准」链断）。
- `on_change` 默认值（倾向 `act`）。
- 保留授权模型（§6，目标级未闭合）。
- transport 修正（抓取/编码全量开销；服务端原子校验+注入）——决策口④后置。
- 实现细节：ε / 指纹形式 / blob 根 `/tmp` → 持久位置。

## 11. 实现顺序（建议）
1. **只读 spike**：已done，契约 vs 真实代码一致。
2. **ScreenChannel v2**：`fetch/act/save` + current-frame 状态 + `on_change`。
3. **工具注册**：`make_screen_specs` 三动词；视觉面暴露。
4. **验证（usage 角度、非 selftest）**：X11 真值 `look→act` 落点、`on_change=skip` 生效；再 Windows。Android 动作补齐排后。
5. 回归 `tests/screenlab` + `tests/image_ctx`；commit/push（授权内、不 tag）。

---

## 附录 A · 自审核对清单（#73 视角 · 2026-09-26）
> **用途**：#77 自审 #74~76 的完成情况时，**从本封板稿的意图出发**核对，而不是顺着实现的叙述。
> **判据**：**目标 §0.0 + 第一原则是法官**；本稿的「理由」是标准。实现偏离且理由不成立 = 缺陷；若是代码/实测逼出的合理修正、理由成立 → **回填本稿**，不算缺陷。

**A1 不变量**
- [ ] 模型面只有 `screen_fetch`/`screen_act`/`screen_save`（无 `look`/`zoom`/`mark` 残留；viewing 不回流图形面）。
- [ ] 模型不可见：帧/图 id、snapshot、revision、区域链、窗口、时间戳。
- [ ] `act` 绑 **current frame**（模型看到的那张图）；一次往返给「操作后整屏 + 落点」。
- [ ] 位置/区域相对 current frame；**换算在工具侧，模型零换算**。
- [ ] settle 内化（fetch change-gated、act 有界，只回报不保证）。
- [ ] 抓屏只在 `fetch`/`act`；无窗口、无观测编号。
- [ ] `on_change ∈ {act,skip}` **客户端判** diff（零图片过网、零索引）；恒回报 `region_changed`。
- [ ] 视觉面（`see`/`mark`/`coord`）坐标恒回 **@原图**；且**已作为模型面工具暴露**（半阻塞项）。
- [ ] `screen_save` = 唯一持久化动作 + **保留授权控制点**。
- [ ] `launch` 进 `ACT_OPS`（唯一触协议处），后端逐平台实现。
- [ ] 决策口②：`ScreenChannel` 持久连接代持 current frame；**无「重抓近似」**残留。

**A2 理由核对（防为方便而偏）**
- [ ] 有没有为了实现方便把 viewing 塞回图形面、把 id/窗口暴露、把 settle 变成「保证」？
- [ ] 有没有偏离第一原则（作用在模型看到的那张图）的角落——例如 `act` 用的是「另抓一帧」的坐标而非 current frame？
- [ ] 图形面隐藏状态是否仍只有 current frame 一个？

**A3 验收核对**
- [ ] 是 **usage 角度真值验收**（非 selftest / 自证），先 X11/Windows。
- [ ] `tests/screenlab` + `tests/image_ctx` 全 passed（提交前）。

**A4 待记录项是否收口**
- [ ] `on_change` 默认值 · `launch` · 保留授权模型 · blob 根 `/tmp`→持久位置 · ε/指纹形式。

> 说明：A1/A2 是「是否忠于封板意图」；A3 是「是否真被用通」；A4 是「记录项是否落地」。三项分别独立，别互相顶替。
