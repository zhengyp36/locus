# handoff｜交接给新会话 · #63 → #64（直接开工）

> 规则 / 环境不在本文件——先读 `screenlab-rules.md`。
> 本会话（#63）：**视觉 × 电脑工具的 usage-first 融合设计**（未改码）。设计 = `design-vision-computer-fusion.md`；**开工工作单 = `screenlab-work.md`**。
> **硬性要求：新会话读完直接开工 Slice 0，不再讨论设计。**
> **不要回读本会话的 transcript**：任务态已落文件，文件是唯一依据；且本会话可能有臆断。
> 新会话 session id = `ses_f25fb1a23ffeSr0SSyTkHX8gwX`（title `screenlab #64`）；旁观：`attach-kilo ses_f25fb1a23ffeSr0SSyTkHX8gwX`。

---

## 复制这段作为新会话的第一句

```
接 #63。本会话直接开工（Slice 0），不再讨论设计。
按序读（纯文本）：1. ../checkpoint/screenlab-rules.md；2. ../checkpoint/screenlab-work.md（工作单，重点）；3. ../checkpoint/design-vision-computer-fusion.md；4. ../checkpoint/design-vision-scripting.md；5. ../checkpoint/handoff-screen-63.md。
⚠️ 文档是二手描述，动手前一律以代码 / 实测为准（尤其 image_ctx 的 API，设计稿未经核对）。
然后按 screenlab-work.md 开工 Slice 0：先 set_timer 10min，再读 cogos/cogos/image_ctx/{tools,view,domain,render,schemas}.py 确认真实 API → 在 ../checkpoint/tools/ 建薄 CLI 适配 → 用已知图跑 see/mark/coord 并用已知真值验收。每步通知 YZ、不等回复；改码不 commit。到停止门（Slice 0 验收通过）停下报 YZ。
```

---

## 本会话做了什么（#63）

1. 吸取教训，**从目标 §0.0 推导、usage-first 重做融合设计** → `design-vision-computer-fusion.md`（取代中间那版机制/本体汇总，不另记）。
2. 定了：第一原则（工具保证"模型作用在所见图"）；模型面极简 5 动作、**不暴露任何 id**；settle 短时试稳 + 升级；定位与内容分离；传输按图 id 去重（模型不感知）。
3. 讨论并锁定开工决策 → `screenlab-work.md`：**平台顺序 X11 先行**、任务态落文件、无人值守、kilo 尽量独自完成。
4. **未改 cogos 产品码**；只写 checkpoint 文档。

## 已定要点（详见 `design-vision-computer-fusion.md`）

- 模型面：`look` / `zoom` / `act`（act 回**整屏 + 落点标记**）/ 可选 `mark`；**模型不接触 id、不做坐标换算、不判稳**。
- 内部：**图 id（内容）/ 帧 id（观测）**，只在传输层；定位（窗口 / mark）；settle = 事实层（revision + 脏区）目标区域静默 T；坐标链"所见图 → 设备"全在工具内（#61 根因）。
- 平台 seam：`capture_raw` + `change_hint`(可选) + `bind`；**顺序 = X11 → Android（逼兜底 + 修 #61）→ Windows**。
- 传输：capture 图恒为整屏；已推过的图只回 id；`zoom` 是 render 派生裁图，同套 id。
- 后置封存：环形缓冲 / push / 采样 / 时间对齐 / 动作不全 / 跨帧 mark 复用。

## 下一步：Slice 0（本会话不讨论，交 #64 直接做）

`../checkpoint/tools/` 建薄 CLI 适配包 `cogos/image_ctx` → 静态 PNG 上跑通 `see / mark / coord` + `Domain` state 持久化（已定 3–8）→ 已知真值验收。细节与停止门见 `screenlab-work.md`。

## 锚

- 工作单：`screenlab-work.md`；设计：`design-vision-computer-fusion.md`、`design-vision-scripting.md`（1–16）
- 实验：`screen-change-detect.md`；规则：`screenlab-rules.md`；活文档：`screen-assist-status.md`
- 目标：`spec-screen-1.md` §0.0
