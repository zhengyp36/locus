# handoff｜聚焦-扫描 第 6 轮：极简对话式视觉调试 agent（工具集收敛到 view）

> 2026-09-07 上午。上游：`handoff-focus-scan-foveation-4.md`（第 5 轮：对话式视觉调试 agent 设计）。
> 本会话：**实现了第 5 轮 agent（含初跑命中 A），随后 YZ 连续纠正设计方向——从"让 agent 完成任务"转成"极简对话式、一起摸索"，工具集收敛到 `view`，砍掉 look_ref/answer/collapse 及滑窗/归档机制**。
> **新会话只读本文件即可接手**；回溯看 `handoff-focus-scan-foveation-4.md` 即可，无需旧会话上下文。

---

## 一句话状态 + 结论

第 5 轮 agent 已实现+初跑（能自主 view 并命中 A，但暴露"先谈思路→纯 talk 复读卡壳""全程高清未远看"等问题）。YZ 据此纠正定位：**对话式 = 极简 = 一起摸索，不是让 agent 完成任务**。已拍板方向：**模型每轮 = 它的话 + 可选一次 `view`；目标/思路/收口全在对话里，由人主导追问**；工具集收敛到**一个正交的 `view(center, radius, focal)`**，其余（look_ref/answer/collapse/滑窗/归档/自动脚本判定）全部废弃。

---

## 二、已拍板的设计方向（本会话 YZ 敲定，别再翻案）

### 1. 定位：极简对话式，非任务执行器
- **对话式 = 通过聊天观察它**：人问思路→它说；人问看哪→它看。不是预设任务让 agent 独自完成。
- **思路不写进 system**（写了→它会把"要看X"当履行义务反复说、卡壳）。思路靠人**问出来**（"你打算怎么看？"），不问它就自然看。
- **目标/收口/思路全在对话里**：模型把判断在和人的对话里说，人对照/追问。不用 answer 这种结构化收口。
- **不写自动脚本**（--auto 初跑、max_steps 自动循环、dA 判定这类"逼成功"骨架全作罢），用**命令式逐条**与它沟通。

### 2. 工具集：只要一个 `view(center, radius, focal)`，三参数正交
- **center**：注视中心（全局归一化 [0,1]）。
- **radius**：**隔离**——圈定"看多大范围"，**圆窗**（以 center 为圆心、radius 为半径的圆，归一化半径）。radius 只回答"多大一块"，与清晰无关。
- **focal**：**该范围内看得多清晰**——范围固定时独立表达的锐度意图。可"大范围但求清晰"，也可"小范围只求轮廓"。
- **三者正交**。此前"2 参数、由 radius 派生清晰度"是**错误合并**，根因是惦记"省 token"；YZ 明确：**token 不是实验阶段考虑的事**（厂商已封顶、保持 img-tool 默认）。

### 3. 废弃的机制（连同其存在理由一起拆掉）
- **look_ref**：图该留在上下文/可由人丢一句"再看刚才那"用 view 重发参数实现；"挤掉再拉回"是上下文管理件，极简下不需要。
- **answer**：任务收口残余；结论靠对话说。
- **collapse**：清窗管理件，同弃。
- **滑窗/归档/可查区**：look_ref 存在的理由，随之一并拆。视野区简化 = "当前这张 view 的图"（每次 view 替换）。
- **system 里的目标/流程层**（"先谈思路""找目标""最终用 answer 给中心""一步步来"）全部移除；system 只留协议层。

### 4. system prompt 只留协议层（示意，供沿用）
```
[两类内容] 视野区=工具生成图（每次 view 出的图出现在消息末尾）；会话=你我对话文字（图不进会话，只有编号引用）。
[坐标] 全局归一化 [0,1] 相对源图；center=中心，radius=圆窗半径（0.5≈整幅，0.05≈特写），focal=清晰度（范围内看得多清）。
[工具] view(center, radius, focal)。
```

---

## 三、保留可复用（勿丢）

- **后端**：`python3.11 -m cogos.lm_service.cli server --port 11434`，KEY `ik_REDACTED`。**新会话需重启。**
- **`LmClient`**：`cogos.lm_service.client.LmClient`（`client.chat(messages, ...)` 不传 model）。
- **`cogos.img_tool.core`**：`do_info`/`do_extract`/`do_draw`。**保持 img-tool 默认（max_dim=800），token 不考虑。**
- **素材/GT**：`/tmp/kilo/vision/locate_exp/`：`detail.jpg`(4000×3000 高清)、`pano_800.png`(800×600 全景)、`p_target_bw_t145.png`(198×222 目标)；GT A(0.595,0.512)、B(0.044,0.680)。归一化坐标两图通用。
- **已实现骨架**（需按新方向大改）：`/tmp/kilo/vision/vf_tool.py`（Controller：open_view/view/look_ref/collapse/answer + 滑窗/归档/全局编号）、`/tmp/kilo/vision/vf_repl.py`（REPL + ContextBuilder + OpLogger + 交互/自主双模式）、`/tmp/kilo/vision/smoke.py`（非交互验证驱动）。
- **初跑结果/观察**：任务自动初跑命中 A（answer=[0.63,0.50] dA=0.037）；观察①约 4 轮纯 talk 复读"让我放大确认"却没发 view，卡壳后才执行 ②全程 focal=3 高清局部，未兑现"先远看全局"、未用 look_ref/collapse ③从全景语义直接跳到 (0.63,0.50) 候选命中。产物 `/tmp/kilo/vision/vf_task_out/`（图+ops.jsonl+history.jsonl）。

---

## 四、待 YZ 拍板（下一会话继续收敛）

1. **focal 实现口径**（二选一，与"radius 独立于清晰度"都兼容）：
   - 降采样档：范围内裁出的图，focal 高→保留原像素（不缩），focal 低→降采样变糊。
   - 取图层：focal 高→从高清原图取（细），focal 低→从全景层取（已是缩略、粗）——handoff-4 的"远看全景/近看高清"原意。
2. **radius 圆窗的归一化基准**：相对**短边**（正方形注视野，推荐）还是相对宽；圆形怎么呈现（方形 crop + 圆 mask，还是直接给圆）。
3. **是否保留 `view` 之外的任何动作**（现倾向不保留，一切靠对话；collapse 是否并入对话由 YZ 定）。

---

## 五、实现方向提示（改骨架）

- 从 vf_tool 重做成：**单一 `view(center, radius, focal)`** + 圆窗裁剪 + 无滑窗/归档/可查区；focal 按已定口径映射到成像。
- 从 vf_repl 重做成：system 只留协议层；去掉 --auto/auto_run/dA/answer 收口；保留 ContextBuilder（视野区快照+会话历史）+ OpLogger（ops/history 落盘）作为观察侧。
- 命令式交互：`input()` REPL，每轮 = 人话 + 模型的话/一次 view；图存文件只显路径，人用视觉模型 read 看图。
