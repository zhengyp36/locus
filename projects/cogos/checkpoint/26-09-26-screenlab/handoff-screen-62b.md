# handoff｜#62b · Android 感知屏变方法实验（#62 子分支）

> 分支于 **#62**（视觉工具脚本化 / 传输与看屏分离讨论）；**父会话 = #62，做完回它**。
> 接 **#62a**（X11 能力矩阵已出，见 `screen-change-detect-62a.md`）；本分支补 **Android** 一节。
> 规则/环境见 `screenlab-rules.md`；上游见 `design-vision-scripting.md`（待定 F）。
> 本会话 = **纯研究**。**等 YZ 确认环境后再动手**。

---

## 复制这段作为新会话的第一句

```
接 #62（子分支 #62b）。本会话做「Android 感知屏变方法」实验，结论追加到 screen-change-detect-62a.md 的 Android 一节。按序读（纯文本，勿读图片）：1. ../checkpoint/screenlab-rules.md；2. ../checkpoint/design-vision-scripting.md；3. ../checkpoint/screen-change-detect-62a.md；4. ../checkpoint/handoff-screen-62b.md。读完不要动设备、不要抓屏、不要 adb，先等 YZ 确认 Android 环境（设备/adb/服务）后再动手。
```

---

## 背景（为什么做）

#62 讨论"传输与看屏分离"：服务端按变化主动推 / 采样、客户端本地缓存、模型从本地取图。核心未决 = **服务端怎么高效感知屏幕变化**（待定 F）。
#62a 已出 **X11** 能力矩阵；**Windows / Android 未做**。Android 是当前 #61/#62 焦点，且**无原生脏区信号**、最难——本题最该先补。

现状（Android 最糙）：
- `screenlab/service/backends_android.py:78` — 每次 `adb exec-out screencap -p` **全屏读回**再 PNG 编码（最贵）。
- `screenlab/service/daemon.py:296` — `changed` 对 **PNG 编码字节**求 sha256（贵、且依赖编码器）。

## 目标与交付物

- 把 Android 的能力矩阵**追加**进 `screen-change-detect-62a.md`（该文件已设计为滚动追加），列同 X11：
  方法 × 信号类型（给脏区 / 仅"变了" / 免费顺带）× 粒度 × 成本（CPU/带宽/延迟）× **可靠性** × 接入点 + 代码锚。
- Android **一条推荐** + 真机实测证据。
- 结论要能直接回答 #62：Android 上服务端怎么高效感知屏变。

## 候选方法（待实测，不必全做，按最小可验证）

- **AccessibilityService 事件**（`TYPE_WINDOW_STATE_CHANGED` / `TYPE_WINDOW_CONTENT_CHANGED` / `TYPE_VIEW_SCROLLED` / `TYPE_WINDOWS_CHANGED`）当"变了"的触发器：事件率/成本、覆盖盲区（视频 / 自绘 / 部分 WebView 不上报）。只当触发，不读语义树。
- **低分 VirtualDisplay（MediaProjection）+ ImageReader 常开探测**：投影分辨率自定（如 240p 或 64 分块 diff），触发后再全清抓一帧；对比每次全屏 `screencap` 的成本。
- **全屏 `screencap` 基线成本**（现状），做对照。
- **降采样/分块指纹**：对 **projection 帧的原始像素**（非 PNG 字节）做低成本指纹/分块 hash，看成本与可靠。
- **视频编码器帧间统计**：若走编码，P 帧大小 / 跳过块当变化信号（是否可用）。
- **其它 framebuffer 方案**（如 minicap）若有现成、值得一试。
- 约束：**API29 / EMUI**，无新 API（如 SurfaceCapture）；MediaProjection **无原生脏区信号**——这是核心难点。

## 环境

- 设备 `nova 4e / MAR-TL00`（Android 10/EMUI 10/SDK29）；**wifi adb** `192.168.1.175:5555`（**别用 USB**，VBox ehci 大流量会重枚举掉线）；app `com.screenlab.assist`；build `bash screenlab/android/build.sh`（~1.5min）。
- 起服务/同意等见 `screenlab-rules.md` §环境与操作、`screen-assist-status.md` §5。
- 负载用具确定性界面变化驱动（如滑动/开关菜单），**非自写 e2e**（规则）。

## 纪律

- 只研究，**不改产品码**（要改先与 YZ 议）。
- **不动 #62 的文档**（`design-vision-scripting.md`）；本文件独立；结论写进 `screen-change-detect-62a.md`。
- 真机验证；不用自写 e2e 自证。
- 设备独占（#62 已挂起、不碰设备）。
- 图不进上下文（数据层）；看图用附件。
- 完成后**飞书通知 YZ 就停**，不链式交接（防失控上限）。

## 回到 #62

- 产出：`screen-change-detect-62a.md` 的 **Android 节**（矩阵 + 推荐 + 证据）。
- 父会话 **#62**：title `screenlab #62 - 电脑/视觉-讨论`，session id **`ses_f27b92b04ffeF5hz7zAFZPi026`**。
- 恢复：`attach-kilo <session-id>`（或 `kilo attach http://127.0.0.1:4097 -u kilo -p kilo --dir /home/zhengyp/work/A/locus`）。
- 回法：把实验的**矩阵结论**带回 #62；#62 只需读 `design-vision-scripting.md` 的已定/待定，不必重读实验过程。
- ⚠️ **bridge/飞书 pin**：若 pin 仍指向 #62，入站会唤醒父会话；本分支期间应把 pin 指到 `#62b`（或确认无异步入站）。

## 锚

- `design-vision-scripting.md`（已定 13/14、待定 A/F）
- `screen-change-detect-62a.md`（X11 矩阵，Unix；本分支追加 Android）
- `screenlab-rules.md`、`screen-assist-status.md` §0/§5
- `screenlab/service/backends_android.py:78`（screencap）、`screenlab/service/daemon.py:296`（frame_hash）
