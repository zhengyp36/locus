# handoff｜#62a · 感知屏变方法实验（#62 子分支）

> 分支于 **#62**（视觉工具脚本化 / 传输与看屏分离讨论）；**父会话 = #62，做完回它**。
> 规则/环境见 `screenlab-rules.md`；本轮上下文见 `design-vision-scripting.md`。
> 本会话 = **纯研究**：只回答"各平台如何高效感知屏幕变化"，产出矩阵供 #62 回来讨论（不是普通交接，是挂起实验枝）。

---

## 复制这段作为新会话的第一句

```
接 #62（子分支 #62a）。本会话做「感知屏变方法」实验。按序读（纯文本，勿读图片）：1. ../checkpoint/screenlab-rules.md；2. ../checkpoint/design-vision-scripting.md；3. ../checkpoint/handoff-screen-62a.md。读完不要动设备、不要抓屏，先与 YZ 讨论实验方案，等 YZ 说开始再动手。完成后飞书通知 YZ 并停。
```

---

## 背景（为什么做）

#62 讨论"传输与看屏分离"：服务端按变化主动推 / 采样、客户端本地缓存、模型从本地取图。核心未决 = **服务端怎么高效感知屏幕变化**。

现状（全是最糙的"全帧截图 + 比哈希"）：
- `screenlab/service/daemon.py:296` — `changed` 对 **PNG 编码字节**求 sha256（既贵又不稳，依赖编码器）。
- `screenlab/service/backends.py:120` — X11 后端 `gstreamer ximagesrc use-damage=false`，**把现成的 damage 关了**。
- `screenlab/service/backends_android.py:78` — Android 每次 `adb exec-out screencap -p` **全屏读回**再 PNG 编码（最贵）。

候选方向（待实测）：X11 `XDamage`/`XFixes`；Windows `DXGI Desktop Duplication`（dirty/move rects）或 `Windows.Graphics.Capture`；Android `AccessibilityService` 事件 / 低分 `VirtualDisplay` 探测；视频编码器帧间统计；低成本降采样指纹。

## 目标与交付物

- **矩阵**：平台 × 方法 × 信号类型（给脏区 / 仅"变了" / 免费顺带）× 成本（CPU/带宽/延迟）× **可靠性**（尤其 mutter/Xwayland 下 damage 能不能用）× 接入点 + 代码锚。
- 每平台**一条推荐** + **实测证据**（真机地面真值）。
- 结论要能直接回答 #62：服务端怎么高效感知屏变。

## 范围与做法

- 平台：X11/Linux（surface `100.100.137.78`）、Windows（`100.112.50.115`）、Android（`nova 4e`，`192.168.1.175`）。
- 每种方法**最小可验证**即可，不铺开。
- 真机验证；**不用自写 e2e 自证**（规则）。
- 记录：方法、实测数字（CPU/延迟/带宽）、可靠性结论、锚点。

## 纪律

- 只研究，**不改产品码**（要改先与 YZ 议）。
- **不动 #62 的文档**；本文件独立。
- 完成后**飞书通知 YZ 就停**，不链式交接（防失控上限）。
- 设备独占：#62 已挂起、不碰设备。
- 图不进上下文（数据层）；看图用附件。

## 回到 #62

- 本分支产出：**`screen-change-detect-62a.md`**（能力矩阵 + 每平台推荐，滚动追加 Windows/Android）。
- 父会话：#62，title `screenlab #62 - 电脑/视觉-讨论`，session id **`ses_f27b92b04ffeF5hz7zAFZPi026`**。
- 恢复：`attach-kilo <session-id>`（或 `kilo attach http://127.0.0.1:4097 -u kilo -p kilo --dir /home/zhengyp/work/A/locus`）。
- 回法：把实验的**矩阵结论**带回 #62；#62 只需读 `design-vision-scripting.md` 的已定/待定，不必重读实验过程。

## 锚

- `design-vision-scripting.md`（已定 13/14、待定 A/F）
- `screenlab-rules.md`、`screen-assist-status.md` §0
- `screenlab/service/daemon.py:296`（frame_hash）、`screenlab/service/backends.py:120`（use-damage=false）、`screenlab/service/backends_android.py:78`（screencap）
