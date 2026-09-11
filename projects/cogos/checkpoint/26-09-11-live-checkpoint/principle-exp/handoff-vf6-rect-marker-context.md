# handoff｜GUI 截图点击坐标 + 视觉工具矩形/十字标记 + 上下文管理重设计（09-08 早）

> 2026-09-08。上游：`handoff-read-precision-context.md`（读图精度/思考/handoff 交接）。本会话主线：用 Xftp 截图 windows.png 测「agent 点击(菜单/按钮)的坐标精度」→ 顺手给视觉工具加「矩形视野 + 中心十字标记」→ 深挖「视觉上下文怎么管理」(图不膨胀/不复读)。**两条线都推进了，工具原语已落地并接入 vf6，上下文管理已定案但未落地。**
> 新会话只读本文件即可接手；locus 记忆见 `projects/cogos/entries/2026-09-08-cogos-vision-rect-marker-context.md`。

---

## 一句话状态

- **工具原语**：矩形视野(fovea 可矩形/圆) + 中心十字(aim marker) —— 原型 `vf_box_proto.py` 验证，已接入 vf6（`Viewer.view_box` + `map_to_pano` 矩形链 + `exec_action` 接 size/shape/mark + `save_trail` 画矩形+十字），冒烟通过（模型真的发出 `shape=rect size=[0.12,0.03] mark`）。
- **上下文管理**：**设计已定案，但 vf6 还没改**。核心：图在上下文里出现一次；`LIVE` 张常驻带图(全景1+最新视图1)；旧观察降级成文字；contexts 只作动作轨迹+重看兜底。**根因诊断也定了**（复读 = 模型自己长文回喂 + 每轮同批静态图无增量 + 无收敛/增量信号）。`run_step` 的下一种组装方式**未实现**。

---

## 二、测试背景与真值

- 素材：`/tmp/kilo/vision/vf6_repl_out_new/windows.png` = **Xftp 8 (Windows SFTP)** 全屏截图，**1357×764**（注意不是 1366×768，是 1357×764）。
- 顶部菜单栏：文件(F) 编辑(E) 查看(V) 命令(C) **工具(T)** 窗口(W) 帮助(H)。
- **工具(T) 真值**：归一化中心 ≈ **[0.188, 0.042]** → 像素 ≈ (255, 32)（蓝标确认压在"工具(T)"上）。之前某次裸估/模型给 0.55 → (746,23) 是错的（飘到右侧空调工具栏）。

---

## 三、测试结论（坐标精度 / 单次前向不可信，再次坐实）

1. **裸眼(deepseek 我)全屏单次**：大方向都对，但小文字目标(菜单项)肉眼定不准，`工具/帮助` 偏 ±20px；单次前向**不能给出像素级可点击**。
2. **模型非确定性**：同一图问"工具(T)"——一次给 `[0.188,0.042]`(准)、另一次给 `[0.55,0.03]`(错 ~490px)。**单次前向不可信，必须交叉/注视=检验。**
3. **thinking 反而添乱**（本次正面证据）：no-thinking 3.1s 给准，thinking 12.3s 反而**把整张截图误读成"渐变背景+散乱方框"**，退回去用比例猜 0.55 →（与上游"思考救打转"相反，证明思考=非单调、不可靠）。
4. **复读/parroting**：模型连续 4 次发**完全相同**的 view+相同理由("还是模糊，再凑近")，center 不变 → 撞上游手记的 vf6 上下文 bug。
5. **后端是会话级**：lm-service 要重启才能用（见"七"）。端口停了 curl 连不上、报 transport error。

---

## 四、工具原语：矩形视野 + 中心十字（已完成 + 接入）

### 新增接口
`Viewer.view_box(center, size, step, shape="rect", mark=True, mark_pt=None)`
- `center=[cx,cy]` 各向异性(相对宽/高)、`size=[wx,wy]` 相对**短边**、归一化[0,1]、只缩不放大(pick_scale≤800)。
- `shape`: `rect`(默认) | `circle`；`mark`(默认true) 在返回图上画**红色十字**标注视中心(aim)，`mark_pt` 缺省=center(可指定瞄点，出界 clamp 不误导)。
- 旧 `view(center, radius, step)` = `view_box(center,[r,r],shape="circle",mark=False)`，兼容保留。
- 圆 = `size=[r,r]+shape=circle`，`size=[r,r]` 对旧 radius 兼容。

### 改动文件
- `/tmp/kilo/vision/vf_tool.py`：加 `Viewer.view_box` + `_draw_mark`，`view()` 委托。
- `/tmp/kilo/vision/vf6.py`：
  - `SYSTEM` 协议：坐标改 `center/size/radius`、`size=[wx,wy]`、`shape`、`mark`，讲清"想看表格行/列/按钮用默认 rect"。
  - `map_to_pano(ref,cx,cy,wx,wy)`：矩形扁平链上溯(父窗 px→子点→size 按子短边缩放)，旧单参 r 按圆处理。
  - `exec_action` view 分支：读 `size/shape/mark`，调 `view_box`，view 对象存 `size`/`shape`。
  - `save_trail`：画矩形框(或圆)+中心十字。
  - `new_view`/`annotate_label`：radius→size。
- `/tmp/kilo/vision/vf_box_proto.py`：原型（`view_box` 独立版，用于本次 demo）。

### 验证
- `view_box` 出图 OK；`map_to_pano` 场景恒等、嵌套 view 按父窗短边缩放正确；冒烟：模型发出 `shape=rect, size=[0.12,0.03], center=[0.55,0.03]`，crop 91×23 薄条，mark 画上。
- 产物：`/tmp/kilo/vision/proto/`（`view_001_rect.jpg`、`view_001_circle.jpg`、`_cmp_rect_circle.jpg`、`_trail_overlay.jpg`）、`_aim_cmp.png`(model vs true)。

### 对比结论（矩形对表格/UI 是净收益）
- 聚焦文件列表行：**rect** 把整行(名称/大小/类型/修改时间)框进一张；**circle** 只有 77×77 灰角小块，读不了行。菜单项/按钮/行/列天然矩形 → 矩形 fovea 值得加。

---

## 五、上下文管理重设计（**设计定案，未实现**）

### 最终的图组织模型
- **上下文是串行有序消息流**；图是某条消息的附件，**在它产生的那条观察消息里出现一次**，下一轮编译时不再发出(图块摘掉、留文字行)。
- 图数**有界**不随动作数增长：`LIVE` 张常驻 = **全景 1 张 + 最新视图 1 张(建议 LIVE=2)**；更老的观察**降级成纯文字**(去图块、留 `观察 view_X · center(..) size(..) rect` 参数行)。
- `contexts`(原中央凹记录)：**不再为"每轮重灌组图"**，只作**动作轨迹 + 重看兜底**(存 center/size/shape，trail 画框、重看老图按 `f(源图,param)` 重算成一条观察消息)。

### 模型怎么"知道图变了/对了"（关键）
不靠"记住一堆旧图做视觉对比"。靠三样：
1. **当前新鲜图**(LIVE 里的全景+最新视图) — "Now 我看到什么"；
2. **文字状态**(我瞄哪/上步看到什么/结论) — "我此前预期什么"；
3. **可感知增量 + 十字标** — 参数行显示 center 从 0.55→0.188；**红色十字标压住目标 → 模型"看到"自己对了**；跑偏 → "看到"要挪。

「变化」= 最新图 vs 文字预期(差值/增量在参数行+十字)，**不是 N 张旧图的视觉差分**。这是"注视=检验"的落点。

### 复读根因诊断（治本，不是调参）
旧 vf6 `run_step` 每轮发：
```
[system] + [历史:纯文字(含模型自己上轮长文原文!)] + [frame_parts] + [user build_vision(全景+全部 fovea 重灌)]
```
复读 = 三因叠加：
- (a) 把**模型自己的详尽长文原样回喂** → 续写模板(parroting)；
- (b) 每轮**同批静态图重灌 + 同一句指令** → 无增量，模型无新物可回应，沿用旧文本；
- (c) **无收敛/增量信号** → 它说"还是模糊、再凑近"，可下一轮仍给"模糊+同批图"，它感知不到动作是否生效，反复同一计划。

**结论：根在"上下文组织 + 反馈信号"，不在模型能力**；单次前向不可信是放大器。治 = ①薄历史(不原文回喂模型长文) ②每轮只新增一条观察(其余文字) ③给"动作状态行+十字"作收敛信号。

### 待实现（`run_step` 下一种组装）
改 vf6 `run_step` + `State`：
- `history` 项带 `kind`（`text`/`obs`）；obs 项 `{role:user, kind:obs, path, text}`（path 为 view 产物文件，持久在 views/）。
- 每条 `view`/`open` 生成的观察 = **追加一条 obs 消息**（图出现一次）；`open` 新场景 = pano 一条 obs。
- 编译上下文：`system + [按 budget 裁到最近 N 条]`，其中 `obs` 保留**最新 LIVE 张带图**，更早的 `obs` 只留 `text`（去 image 块）；dialogue 纯文字。
- 加**薄动作状态行**（文字消息，靠近末尾）：`当前全景 image_1 · 1357x764；已做 view_latest center(..) size(..)；可做动作 view/open`。给执行落点、断"只说话不执行"。
- budget 常量：`LIVE=2`、`BUDGET≈20~24` 条（待 YZ 定）；被裁掉的旧观察**默认不留摘要**(防悬空)，可选项=留下文字摘要行。
- 顺带把 `build_vision` 删掉/替换（不再有"视野区=全景+中央凹组图"概念）。

---

## 六、下一步（按优先级）

1. **落地「五」的上下文重设计**（这是治复读/不膨胀的本，非调参）——改 `run_step` + `State`，A/B 测「工具(T)」：复读次数、命中是否收敛到 `[0.188,0.042]`。
2. 跑通后把「交叉验证/读两遍/证据引用 + 不确定出口」作为主流程并入。
3. `finish_reason=length` 处理（思考截断检测）。
4. 决策面：`shape/mark` 用**默认值兜底**(rect+mark true)，别让模型每轮谈判表示方式(哑原语边界)。

---

## 七、后端 / 运行 / 素材

- 后端：`cd /home/zhengyp/work/A/cogos && python3.11 -m cogos.lm_service.cli server --port 11434`（**会话级，每新会话要重开**；端口停后旧进程会被回收，报 "Cannot connect to host 127.0.0.1:11434"）。KEY `ik_REDACTED`。
- 跑 vf6：`cd /tmp/kilo/vision && python3.11 vf6.py <msg.txt> --scene windows.png --out DIR [--no-thinking]`。
- 素材/脚本：`vf6.py`、`vf_tool.py`、`vf_box_proto.py`；测试图 `vf6_repl_out_new/windows.png`；对照图 `_aim_cmp.png`（model vs true 工具位置）。
- 跑测试需 python3.11。

---

## 八、已改动文件清单（本会话）

- `vf_tool.py`（`Viewer.view_box` + `_draw_mark`，`view` 委托）
- `vf6.py`（SYSTEM / map_to_pano / exec_action / save_trail / new_view / annotate_label —— 全部是"矩形+十字"接入，**未含第五节上下文重设计**）
- `vf_box_proto.py`（原型）
