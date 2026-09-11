# handoff｜图上下文 K 保留 bug 修复 + 六次点击『工具(T)』取证 + 「标注坐标系」正误之争（09-10 凌晨）

> 2026-09-10 凌晨。上游：`handoff-vision-image-fields-13.md`（对话图工具 `image_field_chat.py` 落地 + 点击『工具(T)』命中/非命中取证，根因=模型目测偏+没换算+没自证）。
> 本会话：① 诊断并修复 `image_field_chat.py` 图上下文 K=4 失效（全图都保留）→ 按 `_step` 逐条老化；② lm-service 加 images 统计日志并观测到 `images=5`（K 生效）；③ mark 颜色来源；④ 六次点击『工具(T)』比照；⑤ **关键发现**：正确标注法 = **直接在局部缩放 FIG 上 mark，工具自动映射回全局**，模型默认却手工换算全图坐标，只有在用户提示后才改对。
> 新会话只读本文件可接手。**本会话主线开放问题 = 「标注坐标系」的正确用法 + 如何让模型默认就做到。**

---

## 一句话状态

- **图上下文 K 保留已修复并生效**：`image_field_chat.py` 里 K=4 原失效（所有图都进上下文），根因=保留判据按 `fig_id` 是否在 `mgr.live`（而非各观察消息年龄），同图被 SEE/MARK 反复操作时其全部历史观察图块全保留。修复：观察消息记录产生时 `_step`，`prune_aged_obs` 按 `cur - s > k` 逐条摘图（`image_field_chat.py:188-226`）。
- **lm-service 请求图数可观测**：`handler.py` 加 `_count_images` + 请求日志行 `[lm-service] messages=N images=M`；实测 **`messages=52 images=5`**，确认模型侧只带 5 张图，K 老化达成。
- **mark 颜色非随机**：`render.py::PALETTE`（8 色相阶梯）+ `announce_color/next_color` 按序分配、避开 FIG 内已用色；同一 FIG 第 1 个 mark=红，第 2 个=下一色相。
- **六次点击比照（重点）**：真值『工具(T)』`@全图=[0.188,0.042]`→像素靶 `(255,32)`（windows.png 1357×764）；可点归属带 `225≤x≤278 且 12≤y≤38`，文字块带 `234≤x≤270`。**命中 = test_a / new_2 / new_3 / new_4；非命中 = new_1（偏右 296px 处的『工具/窗口』间隙）**。
- **正确与错误标注法（本会话最大发现）**：**对的做法 = 把目标放大到清晰局部 FIG（如 FIG:1001），直接 `mark ref=FIG:1001 center=<在局部图上读的位置>`，工具自动做"局部→全局"映射**。错的做法 = 模型先在局部图读位置、再**手工换算**（`0.135+0.35×0.15=0.188`）成全图坐标、用 `mark ref=FIG:1000` 输出——既多余又易错。**但模型默认走错的，只有被用户明说后才改对**。

---

## ① 图上下文 K 保留失效：诊断与修复

`image_field_chat.py`（`/tmp/kilo/vision/`），`K=4`（窗口 5 格）。

### 原 bug 根因
- `prune_aged_obs` 摘图判据 = 某 user 观察消息的 `_fig` **不在** `mgr.live`（`_is_live`/`_live_figs`）。`mgr.live` 是 `(step, fig_id, msg)` deque，仅按 `step - 队首step > k` 弹队首。
- 视觉对话常态 = SEE 一张图后反复 MARK/ADJUST 同一张图 → 同一 `fig_id` 不断被重新入 live。**只要该 fig 还在 live（被最近一次触碰续命），`prune_aged_obs` 就把整个会话里所有带这个 `_fig` 的历史观察消息的 `image_url` 全保留**（只按 fig 归属、不看消息多老）→ 几十张旧图全进 prompt。
- 次因：老化时计 `step` 按**图工具调用次数**（`manager.py:32`）而非对话轮数；且 `figctx.strip()` 只摘 manager 内部 `self.messages`，从不碰 `state.raw_msgs`（清理 raw_msgs 的只有那个按 fig 归属的粗 filter）。

### 修复（已合入 `image_field_chat.py`）
- `push_observe(obs, fig_id, step)` 记录 `_fig` + `_step`（产生时 `mgr.step`）。
- `prune_aged_obs` 改按逐条 `_step`：`cur - s > self.mgr.k` 摘 image_url，**同 FIG 的多条观察图各自独立判龄、互不牵连**。
- `_load` 从持久化消息回填 `mgr.step = max(_step)`（resume 可复现）。
- 观测：`[lm-service] messages=52 images=5` → K 生效。

> 遗留（小）：旧 raw.jsonl 无 `_step` 的历史消息会被 `s is None` 跳过而不老化，需新会话/重跑才完全生效。

---

## ② lm-service 请求图数日志（`cogos` 仓库，已改）

`cogos/lm_service/handler.py`：
- 新增 `_count_images(messages)`（统计 content 列表中 `type=="image_url"` 块数）。
- `handle_chat_completions` 校验通过后、提交前 print：`[lm-service] messages=N images=M trace_id=...`（对所有合法请求都打，含 images=0）。
- **注意坑**：后台进程/管道下 `print` 块缓冲不立即刷——需 `python3.11 -u` 启动或设置 `PYTHONUNBUFFERED=1` 才能实时看到。

---

## ③ 六次点击『工具(T)』比照（各 run 最终十字源图 px）

| run | 最终归一化 | 源图 px | 命中? | 轮数/工具数 | 方法 |
|---|---|---|---|---|---|
| test_a | (0.187,0.042) | (253.8,32.1) | ✅ | 20 msgs/4 shot/2 cross | see→放大→mark→缩窄窗口核对→adjust 一次 |
| new_1 | (0.218,0.045) | (295.8,34.4) | ❌ | 11/2/1 | 放大(中心0.25偏右)→1 次 mark→不核对收口 |
| new_2 | (0.180,0.043) | (244.3,32.9) | ✅ | 91/19/11 | 放大→mark→**反复回全图自我怀疑**，x 在 0.17↔0.188 抖动 10 次 |
| new_3 | (0.183,0.037) | (248.3,28.3) | ✅ | 17/3/2 | 放大→**算相对坐标**（公式对）→adjust 一次 |
| new_4(先) | (0.184,0.045) | (249.7,34.4) | ✅ | —/7/3 | 手动换算全图坐标，来回 3 次 |
| new_4(后) | 局部坐标 (0.45,0.5) on FIG:1001 → src_norm(0.1838,0.0445) | (249.4,34.0) | ✅ | —/1 mark | **在局部 FIG 上直接标，工具自动映射** |

**结论**：
- **new_1 是唯一非命中**：放大窗口中心选偏右（0.25），且 1 次 mark 后不核对，落进『工具(T)』与『窗口(W)』之间。
- **test_a / new_2 / new_3 / new_4 都命中**，但路径明显两极：test_a、new_3、new_4(后) 走"放大→读位置→（换算/直接标）→再核对→收口"，快而准；**new_2 绕圈**。
- **new_2 为何绕 91 条**：放大视图已看清"当前位置在工具(T)上"，但每次切回**全图**（`see [0.5,0.5]/[1,1]`，5 次）验证，把**实际略偏左的十字误读成"落在工具/窗口之间"**（全图示读数系统性偏右），于是朝**错误方向（左）反复 adjust**，x 从 0.18 漂到 0.17 又拉回，10 次打转。它从未做"把放大窗口对准十字本体再看一眼"这种一步定胜负的动作。

---

## ④ 标注坐标系：全图坐标 vs 局部图坐标（重点，本会话开放线）

### 观察 vs 标注是两回事
- `see ref=FIG:1000 center=C size=S` = 在 FIG:1000 上开窗渲染，产一张**局部放大图**（FIG:1001+）——**模型看到的是局部图**。
- 但 `mark`/`adjust_mark` 的坐标语义取决于 **ref 指向哪个 FIG**：
  - `ref=FIG:1000`（全图）→ center 为**全图归一化**坐标，十字所属窗口 `[0.5,0.5]/[1,1]`，`src_norm=cross_rel`。
  - `ref=FIG:1001`（局部窗）→ center 为**相对该窗口**的坐标；工具 `gx=cx−size/2+u×size` 自动映射回全局（`image_field_chat.py:140-148`）。

### 结论：正确做法 = 在局部图上标，让工具映射
- new_4 第 4 条 cross 即证明：`fig=1001, win_c=(0.1898,0.0445), win_s=(0.1201,0.0497), cross_rel=[0.45,0.5] → src_norm=(0.1838,0.0445) px(249.4,34.0)`，命中『工具(T)』。
- 模型**不换算**，只需在局部图上目测"工具(T) 位于窗口 (0.45,0.5)"，直接 `mark ref=FIG:1001 center=[0.45,0.5]`，全局自动正确。

### 关键问题：模型默认不这么做，要人提示才改对
- 模型默认心智 = "我必须产出全图归一化坐标"，于是主动读局部图 + **手工换算**（`0.135+0.35×0.15=0.188`），既多余又易错。
- 用户明说"不要在不同子图间切换坐标、直接在局部图上 mark、工具会映射"后，模型立即改为 `mark ref=FIG:1001` 一次收敛。
- **这是 schema/系统提示的空档**：`figure_tool_schemas()`（`image_ctx/schemas.py`）只写"坐标相对 ref 归一化 0..1"，没告诉模型这条策略——"应 mark 在你看到目标的那个缩放 FIG 上，工具会自动映射；不要换算成全图坐标"。**不是模型能力问题，是提示没把这层用法讲清。**

### mark 能否在不同图之间移动？
- **不能**。`adjust_mark(domain, fig_ref, anno_id, ...)` 先 `_resolve_fig(fig_ref)` 定位 FIG，再 `resolve_anno(fig, anno_id)` **只在那个 FIG 的 annos 里找**（`tools.py:233-237`），换 fig_ref 会对不存在的 anno 抛 `RefError`。标注被绑定在所属 FIG（`fig.annos.append(a)`，`tools.py:289`）。
- 要"移到另一张图"只能 `unmark`（删）→ `mark`（重建）。
- 注意坐标含义：anno pts 相对**所属 FIG 窗口**归一化（`_clamp_anno_pts` 按 `fig.w/fig.h`），同一 `u=0.5` 在全图 FIG 与局部窗 FIG 是**两个不同的原图位置**。

---

## 下一会话要讨论的问题（开放主线）

1. **「局部图上直接标、工具自动映射」如何变成模型默认行为**？候选：
   - 在 `figure_tool_schemas` 的 mark schema / SYSTEM prompt 里写明策略："看到目标后，把 see 放大到该目标所在局部 FIG，mark 的 ref 指向该 FIG、center 为该局部图内位置；坐标会由工具自动映射回全局，无需换算"。
   - 或约束链路："mark 前必须先 see 把目标放大到清晰；mark 时 ref 指向当前子图"。
2. **如何抑制"回全图验证"导致的自我怀疑循环**（new_2 现象）？是否需要约定"标后把放大窗口对准十字本身再核对一次"（对标 new_4(后)/test_a 的有效动作）+ 禁用"回全图目测标注位置"。
3. 各 run 工具用法/命中比照可沉淀进 `checkpoint/principle-exp/tools-usage-models.md`。

---

## 运行

- **LM server（会话级，需重开；务必 -u 以便看日志）**：`cd /home/zhengyp/work/A/cogos && python3.11 -u -m cogos.lm_service.cli server --port 11434`；KEY `ik_REDACTED`。
- **对话工具**：`cd /tmp/kilo/vision && python3.11 image_field_chat.py --repl --out <dir>`（或 `--msg "..."` 单轮 / `--resume` 重开）。
- 测试：`cd /home/zhengyp/work/A/cogos && python3.11 -m pytest -q`。

---

## 关键文件

- 本会话探针：`/tmp/kilo/vision/image_field_chat.py`（已含 K 修复，非仓库）；验证目录 `/home/zhengyp/work/A/workspace/{test_a,new_1,new_2,new_3,new_4}`（raw.jsonl + crosses.jsonl + shots/）；源图 `/home/zhengyp/work/A/workspace/windows.png`（1357×764）。
- 图工具本体：`cogos/cogos/image_ctx/{tools,view,schemas,render,domain}.py`；上下文：`cogos/cogos/cog_ctx/{context,manager}.py`；schema：`image_ctx/schemas.py::figure_tool_schemas()`。
- LM server：`cogos/cogos/lm_service/{handler,client,server,cli}.py`（已加 `_count_images` + 日志行）。
- 目标真值：『工具(T)』`@全图=[0.188,0.042]`→像素靶 `(255,32)`；可点归属带 `225≤x≤278 且 12≤y≤38`；文字块带 `234≤x≤270`。
- 工具用法整理：`checkpoint/principle-exp/tools-usage-models.md`。
