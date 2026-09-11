# handoff｜聚焦-扫描 第 8 轮：落地「单一视野三层 + 图对象统一 + open 路径化 + view 参数化」，整合一次性/REPL

> 2026-09-07 下午。上游：`handoff-focus-scan-foveation-6.md`（第 7 轮：极简对话式断言，tool 收敛到 view 两参 + 全景常驻 + 轨迹累积）。
> 本会话：**把模糊的"单一视野/驻留/对照"从纸面谈清成可实现的模型——与 YZ 一轮轮纠正后落地 vf6 整合版（一次性 + REPL 共用一套 core）。核心改动：单一视野三层（驻留/全景/中央凹）、图对象统一（路径+属性，view 参数化不存图）、open 只 open 原图（用户给绝对路径，同路径去重）、view 产物图入专用目录不作可 open 原图。**
> **新会话只读本文件即可接手**；回溯看 `handoff-focus-scan-foveation-6.md` 即可，无需旧会话上下文。

---

## 一句话状态 + 结论

工具可用可跑：`vf6.py` 整合版 + `vf_tool.py` viewer + `smoke.py`。视野 = 单一视野三层（驻留≤2 + 全景 current + 中央凹 fovea view 参数轨迹）；`view` **参数化**（不注册为图对象、产物图入 `views/` 供人看，带 source+center+radius 可重放）；`open` **只 open 原图**（用户给绝对路径或已注册 id，同路径去重，拒 view 产物目录）；模型可**循环 view**（看图后继续发直到不再发，剥离 json 只存纯文字）。smoke + 一次真实对话 + REPL 均通过。**下一步想法：用"用户给第二场景路径 → open 两张原图 → 跨图对照"做实验。**

---

## 二、本会话拍板/纠正的方向（YZ 敲定，别再翻案）

1. **Agent 只有一个视野**，所有图从一个视野进入（与人一致）。多图对照不是"叠加双视野"，而是"单一视野 + 随时间切换当前图/驻留保留"。
2. **视野三层**：驻留(≤2 滑动窗口) + 全景(current, 当前 open 原图, 唯一可 view 主体) + 中央凹(fovea, view 参数轨迹, open 换图清空)。
3. **图对象 = 路径 + 属性**：任何图（scene/ref/view）都是对象。view 图不是"独立图"，而是**参数 JSON `{source, center, radius}`**——执行时在专用目录生成一张裁剪图给人看，但**不作可 open 原图**。重新看某 view = open 它的 source + 按参数重放。
4. **open 只 open 原图**：接受用户给的**绝对路径**（不做相对解析）或已注册 id；同路径**去重**（复用同 id）；**拒 open view 产物目录**的图；open 换图**丢旧上下文是正常**（单一视野），要保留就 pin。
5. **驻留图（全图或 view）都带路径+view 参数**，脱离全图能凭参数重看。
6. **整合两脚本**：`vf_repl.py`(REPL 旧) 并入 `vf6.py`（`--repl` 模式），共用一套 core；旧 `vf_repl.py` 删除。
7. **P2（body 超限）真因是传输字节非 token**：800×800≈342 token 很便宜；`invalid json body` 是 base64 字节超 server 限制 → view 产物改 **JPEG(quality 90)** 降字节。
8. **P1 修复**：模型"看图后"常又发 view（想连续扫）——改为**一次运行内循环 view**（直到不再发动作），且**剥离 json 只存纯文字**（动作记忆由状态/标注承载，不进对话历史）。

---

## 三、当前实现（/tmp/kilo/vision/）

### `vf_tool.py` — Viewer（可变源圆窗裁剪）
- `Viewer(out_dir)`：`set_src(path)` 换源(open 语义)；`view(center, radius, step)` → 圆窗 = 外接正方形 + 圆 mask(128 灰) + 越界补边 + 等比缩到长边≤800(只缩不放大)。
- 输出 JPEG(quality 90)，文件名 `view_{step:03d}.jpg`，存到 out_dir（vf6 传 `out_dir/views/`）。
- 无状态，不存轨迹；编号由外部传入。

### `vf6.py` — 整合版（一次性 + REPL 共用 core）
- **State**（`out_dir/state.json` + `history.jsonl`）：
  - `images`: dict[id→原图]（scene/ref，**可 open**）。
  - `current`: 当前全景原图 id。
  - `fovea`: list[dict] (**view 参数对象**，不注册进 images)。
  - `pinned`: list[dict] (**驻留对象**：原图快照或 view 对象)，`pinned_max=2` 满则挤最老。
  - `counter`(原图 id 递增) / `view_step`(view_NNN 编号)。
- **图对象**：
  - scene `{id,kind,name,src_path,pano_path,src_w,src_h}`；ref `{id,kind,name,src_path,src_w,src_h}`。
  - view `{id:`view_N`,kind,name:`view@source`,source,center,radius,src_path(产物图),annotate}`。
- **`resolve(obj)`**：统一对象表示，dict 直接用 / str 查 images 或 fovea。
- **`display_path(img)`** = `pano_path or src_path`（view=产物图；scene=缩略 pano）。
- **`annotate_label(role,img)`**：view→`[id] 角色·view@source·c(..) r..`；scene/ref→`[id] 角色·name·全图 WxH`。
- **`open_image(id|path)`**：id 在 images→切 current+fovea 清空；path 存在→去重注册(`_register_from_path` 查同 src_path)→切 current；path 在 `views/` 目录→拒绝；不存在→报错。
- **`pin/unpin(ref)`**：`resolve` → 进/出 pinned（≤2 挤最老）。
- **`build_vision(state, human_msg)`** → content：顺序 `[驻留(跳过 current) → 全景(current) → 中央凹(fovea 时间序，跳过已在 pinned)]`，每张前紧贴一行标注，图不进历史。
- **`exec_action`**：view → 生成 view 参数对象入 fovea + 产物图(views/) + 返回该对象；open → 切 current + set_src + 返回 current id；pin/unpin → 无图。
- **`run_step`**：循环（max_inner=4）——搭 messages → chat → `split_action`(剥离 json) → `pick_action` → `exec_action` → 若产图 `resolve`(dict/str) 回灌再 chat → 直到无动作 → 写 history(纯文字)。
- **`split_action(text)`** → (clean_text, dec)：把末尾动作 JSON 从正文剥离（历史只存 clean）。
- **`make_viewer`**：Viewer 指向 `out_dir/views/`。
- **SYSTEM 协议**：三层视野 + 坐标(归一化[0,1], radius 相对短边) + 工具 `{view|open|pin|unpin}` JSON，open 用 path/image。

### `smoke.py` — 纯图逻辑验证（不调模型）

---

## 四、验证结果（已通过）

- **smoke**：view 产物不入 images；`open` 同路径去重(同 id)、拒 view 产物目录、open 清空 fovea；`pin` 原图+view；`build_vision` 去重(驻留 view 只现一次)；fovea 为参数对象、`src_path` 在 `views/`。
- **真实对话**（`vf6.py msg.txt --out vf6_out4`）：模型看全景→定位 HELLO→连续 view(view_1, view_2)，产物入 `views/view_001/002.jpg`，fovea 为 view 参数对象，`images` 只含 scene/ref 原图；无崩溃。
- **REPL**（`vf6.py --repl`）：多轮跑通，连续 view 不崩。
- 命令：`cd /tmp/kilo/vision && echo "<话>" > msg.txt && python3.11 vf6.py msg.txt [--out DIR]` 或 `python3.11 vf6.py --repl`。

---

## 五、遗留（待 YZ 裁决 / 下一步）

1. **"模型如何知道盘上有哪些图可打开"**：按 YZ 定实现为"用户给路径 agent 自己打开"；若未来要真开放式，可加图库浏览工具（暂不做）。
2. **多图对照素材缺口**：现素材只有 1 张 scene(detail) + 1 张 ref(target)。open 两张原图对照需要用户给**第二张场景路径**（现库无独立第二 scene，其余 800 级都是 detail 派生物）。
3. **pinned 的 view 重看**：`open` 后 fovea 清空但 pinned 保留 view —— 重看需模型自行 "open 该 view 的 source + 按参数 view"（open+view 组合重放），系统不自动做。
4. **view 产物 JPEG 有轻微有损**（quality 90），如需"如实像素"在特写核对时可调高或切 PNG。

---

## 六、可复用（勿丢）

- **后端**：`python3.11 -m cogos.lm_service.cli server --port 11434`，KEY `ik_REDACTED`。**新会话需重启**（本会话已启动并验证）。
- **`LmClient`**：`cogos.lm_service.client.LmClient`（`chat(messages, temperature=..., max_tokens=...)` 不传 model）；`LmServiceError(category, message)` body 超限等会抛。
- **`cogos.img_tool.core`**：`do_info`/`do_extract`/`do_draw`/`pick_scale(long_side,max_dim)`(sc<1 缩小)。保持 img-tool 默认 max_dim=800，token 不考虑。
- **素材/GT**：`/tmp/kilo/vision/locate_exp/`：`detail.jpg`(4000×3000, 主 scene)、`pano_800.png`(800×600 全景缩略)、`p_target_bw_t145.png`(198×222 黑白目标 ref)。GT A(0.595,0.512)、B(0.044,0.680)。
- **样本产物**：`/tmp/kilo/vision/vf6_out4/`（views/view_001/002.jpg、state.json(含 fovea view 参数/views_dir)、history.jsonl 纯文字）。`views/` = 中央凹产物目录。
