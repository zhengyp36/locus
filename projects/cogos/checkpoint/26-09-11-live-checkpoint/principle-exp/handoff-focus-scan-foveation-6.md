# handoff｜聚焦-扫描 第 7 轮：极简对话式视觉调试 agent 落地（view 两参数 + 全景常驻 + 轨迹累积）

> 2026-09-07 下午。上游：`handoff-focus-scan-foveation-5.md`（第 6 轮：极简对话式，工具集收敛到 view）。
> 本会话：**从"多轮纸面推演"走到落地——按 YZ 连续纠正，重做成 `vf6.py` 一次性脚本 + 单一 `view(center,radius)` + 全景图常驻视野 + 中央凹滑动窗口（多图累积=视线轨迹）；图逻辑用 smoke 验证通过，真实对话两轮跑通，模型自发"看全景→定位候选→放大→否定→继续扫"。**
> **新会话只读本文件即可接手**；回溯看 `handoff-focus-scan-foveation-5.md` 即可，无需旧会话上下文。

---

## 一句话状态 + 结论

工具成型可跑：`vf6.py` 命令式逐条（msg.txt 一次性退出）、视野区 = 全景图(常驻) + 目标图(常驻) + 中央凹轨迹(view 累积)、唯一工具 `view(center, radius)`。两轮真实对话验证通过，模型行为符合"对话式观察它怎么扫"。仍待收敛：模型"看图后"常又发第二次 view 的边界处理。**新会话专注调试与实验。**

---

## 二、本会话拍板/纠正的方向（YZ 敲定，别再翻案）

1. **程序必须自限像素 ≤800×800、等比不变形，并在上下文如实告知"是否已达上限/源真实像素"**。不能赌厂商去裁（厂商裁了模型看到的像素信息就不准）。固定输出帧 = 圆窗裁出的正方形，等比缩到长边 ≤800，**只缩不放大**（特写小窗如实输出小尺寸 + 报"源只有 N×N"，比插值假清晰诚实）。
2. **收敛为两参数 `view(center, radius)`**。focal（独立清晰度旋钮）砍掉——原因：输出尺寸固定后，清晰度完全由 radius 派生（radius 越小，那块在固定输出上占更多像素→越清）；且"单源 + token 不考虑"下 focal 只能"主动变糊"（无需求）或"换低分辨率层"（引第二源，复杂）。按"命令式逐条"，清晰度语义由 radius 自然承担。
3. **全景图必须常驻视野**（周边视野/全局参照，看整体结构和目标方位）。**中央凹是一个滑动窗口，多图累积 = 视线轨迹**（scan path），不是"每次 view 替换"。这是"对话式观察它怎么扫"的核心。
4. **视图中必须有全景图才有意义**——全景常驻，中央凹在其上沿注视点滑动。
5. **用 diagnose.py 的一次性脚本模式，不用 input() REPL**（input() 对 kilo/CLI 不友好）。echo 对话到 msg.txt → 传文件 → 执行一次退出 + history 持久化。
6. **图是对话资源，agent 需要看图时通过 view 看；但全景/目标/高清原图作为素材由程序挂载常驻**（命令行 `--pano/--target/--src` 是初始化，不是每轮对话参数）。
7. **do_extract 保持长宽比（只缩不放大）是对的正确行为**，view 复用它；view 自己补的只是"各向同性半径→正方形 region→越界补边→圆 mask"。

---

## 三、当前实现

文件都在 `/tmp/kilo/vision/`：

### `vf_tool.py` — `Viewer`（纯裁图，不存轨迹）
- `Viewer(src_path, out_dir, start_step=0)`：probe 源图尺寸。
- `view(center, radius) -> dict`：**圆窗** = 外接正方形 crop + `_circle_mask`（圆外中性灰 128）+ 越界补边 + 等比缩到长边 ≤800（只缩不放大）。
- radius 各向同性 = `radius * min(W,H)`；center 各向异性（cx 相对宽、cy 相对高）。
- 返回 dict 含 `path/center/radius/src_px/out_px/clipped/at_max/step/annotate`；`annotate` 形如 `view#2 center(0.350,0.550) r0.150 src900x900 out800x800 @800`。
- `start_step` 支持跨运行连续编号（文件 `view_NNN.png` 不冲突）。

### `vf6.py` — 一次性对话脚本（主入口）
- 用法：`python3.11 vf6.py msg.txt [--src--pano--target--out--max-tokens]`，默认素材在 `locate_exp/`。
- 流程：读 msg.txt → 组装 messages（system 协议层 + 文字历史 + 本轮 user 含全景/目标/轨迹图）→ chat → 若模型带 `view` 则执行 → **图回灌**（user 消息带新图）→ 再 chat 让模型看图说话 → 写回 state/history → 退出。
- SYSTEM 只留协议层：视野区（全景/目标/轨迹）、会话（图不进历史）、坐标（归一化 [0,1]、radius 短边基准）、工具 `view`。
- 落盘（`--out` 默认 `vf6_out/`）：
  - `view_NNN.png`：轨迹图。
  - `state.json`：`{"views":[{path,center,radius,annotate}]}`，跨轮累积。
  - `history.jsonl`：文字历史（`{role,text}`：user 人话 + assistant 模型两次回复）。

### `smoke.py` — 纯图逻辑验证（不调模型）

---

## 四、验证结果（已通过）

- **smoke**（不调模型）：整幅 r0.5 → src3000×3000 out800×800 @800；特写 r0.05 → src300×300 out300×300（不放大）；角落越界 → clipped 补边；极小 r0.01 → src60×60 out60×60；`start_step=4` → 编号 view#5。圆 mask 生效（四角 128 中性灰，中心真实内容）。
- **真实对话两轮**（`vf6.py msg.txt`）：
  - 轮1「先看全景…」：模型看全景说结构 → 猜候选 center[0.15,0.35] → view r0.15 → 看图后否定，又发第二次 view[0.85,0.45]（未执行，见遗留）。
  - 轮2「继续看你说的右侧中部」：模型引用上一轮轨迹 view_001 → view[0.35,0.55] → 看图后否定 → 又发第二次 view[0.08,0.55]（未执行）。
  - 轨迹累积正确：state.json 2 views，跨轮视野带全量轨迹图。
- 命令：`cd /tmp/kilo/vision && echo "<话>" > msg.txt && python3.11 vf6.py msg.txt`。

---

## 五、观察到的行为/发现

1. 模型自然采用"看全局 → 缩小半径放大 → 评估 → 否定 → 再移动"的扫描循环，与"中央凹滑动窗口/视线轨迹"一致。
2. 模型会对**上一轮 view 的轨迹图有记忆**（轮2 开口引用"右侧中部这个局部视图"），说明轨迹图回灌有效。
3. 模型倾向在"看图后"的回复里**再发一个 view**（想继续移动），当前实现"一次运行一次 view"把它挡了——json 混进 text2 存进历史。这是与"命令式逐条"需权衡的点。

---

## 六、待 YZ 拍板 / 遗留

1. **模型"看图后"又发 view 如何处理**（二选一）：
   - 维持现状：一次运行一次 view，第二次 view 不进执行，只作下轮追问依据（kilo 看输出决定下一句）。
   - 图回灌后允许继续循环 view（直到模型不再发 view），一次运行内可多条视线。
   - 备注：第二次 view 的 json 会混进 text2 存进 history，若继续现状可考虑剥离 json 只存纯文字。
2. **radius 语义精度**：各向同性圆窗(短边基准) vs 各向异性图(4:3)，`r=0.5` 横轴只盖 75%（横向留边），是否要在 SYSTEM 把话说准（"0.5=圆直径=短边，横向上留边"）。
3. **是否给 view 加可选 `path`**，让 agent 也能放大看全景图/目标图的细节（现只滑高清原图 detail）。

---

## 七、可复用（勿丢）

- **后端**：`python3.11 -m cogos.lm_service.cli server --port 11434`，KEY `ik_REDACTED`。**新会话需重启。**
- **`LmClient`**：`cogos.lm_service.client.LmClient`（`client.chat(messages, ...)` 不传 model）。
- **`cogos.img_tool.core`**：`do_info`/`do_extract`/`do_draw`。`do_extract` 只缩不放大、保持长宽比。**保持 img-tool 默认 max_dim=800，token 不考虑。**
- **素材/GT**：`/tmp/kilo/vision/locate_exp/`：`detail.jpg`(4000×3000 高清)、`pano_800.png`(800×600 全景)、`p_target_bw_t145.png`(198×222 目标)；GT A(0.595,0.512)、B(0.044,0.680)。归一化坐标 detail 与 pano 通用（等比 4:3）。
- **样本产物**：`/tmp/kilo/vision/vf6_out/`（view_001/002.png、state.json、history.jsonl），可直接看轨迹。
