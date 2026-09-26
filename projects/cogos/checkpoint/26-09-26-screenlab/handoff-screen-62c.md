# handoff｜#62c · Windows 感知屏变方法实验（#62 子分支）

> 分支于 **#62**（视觉工具脚本化 / 传输与看屏分离讨论）；**父会话 = #62，做完回它**。
> 与 **#62b**（Android）**并行**；两分支**各写独立产出文件**，避免并发写冲突。
> 规则/环境见 `screenlab-rules.md`；上游见 `design-vision-scripting.md`（待定 F）；X11 格式参照 `screen-change-detect-62a.md`。
> 本会话 = **纯研究**。**等 YZ 确认环境后再动手**。

---

## 复制这段作为新会话的第一句

```
接 #62（子分支 #62c）。本会话做「Windows 感知屏变方法」实验，结论写入独立文件 screen-change-detect-62c-win.md（勿动 62a 的滚动文件与其它共享文档）。按序读（纯文本，勿读图片）：1. ../checkpoint/screenlab-rules.md；2. ../checkpoint/design-vision-scripting.md；3. ../checkpoint/screen-change-detect-62a.md；4. ../checkpoint/handoff-screen-62c.md。读完不要连 Windows、不要跑命令，先等 YZ 确认 Windows 环境后再动手。
```

---

## 背景（为什么做）

#62 讨论"传输与看屏分离"：服务端按变化主动推 / 采样、客户端本地缓存、模型从本地取图。核心未决 = **服务端怎么高效感知屏幕变化**（待定 F）。
#62a 已出 **X11** 能力矩阵；**Windows / Android 未做**。本分支补 **Windows**（#62b 同时补 Android）。
现状（Windows 最糙同全线）：每次抓帧后对 **PNG 编码字节**求 sha256 判 `changed`（`screenlab/service/daemon.py:296`），贵且依赖编码器。

## 目标与交付物

- 产出**独立文件** `screen-change-detect-62c-win.md`，矩阵列同 X11：
  方法 × 信号类型（给脏区 / 仅"变了" / 免费顺带）× 粒度 × 成本（CPU/带宽/延迟）× **可靠性** × 接入点 + 代码锚。
- Windows **一条推荐** + 真机实测证据。
- 结论要能直接回答 #62：Windows 上服务端怎么高效感知屏变。
- **不写** `screen-change-detect-62a.md`（那是 62a/62b 的滚动文件）；合并留给 #62。

## 候选方法（待实测，按最小可验证）

- **DXGI Desktop Duplication**（`IDXGIOutputDuplication::AcquireNextFrame`）：直接给 **dirty rects + move rects**，且新帧在 GPU 纹理里——最优候选。
- **Windows.Graphics.Capture（WGC，Win10 1803+）**：`Direct3D11CaptureFrame` / frame pool，看是否给脏区/变更语义。
- **`SetWinEventHook` 事件**（`EVENT_OBJECT_*` / `EVENT_SYSTEM_*`）当"变了"的触发器：事件驱动、近零 CPU；覆盖盲区（自绘/GPU 直出可能不上报）。
- **GDI `BitBlt` 基线**：现状类比的成本对照。
- **降采样/分块指纹**：对原始像素（非 PNG 字节）做低成本指纹/分块 hash。
- **视频编码器帧间统计**：若走编码，P 帧大小 / 跳过块当变化信号。
- 记录可靠性：权限/会话要求、是否需管理员、DPI/多显示器、后台会话（Session 0）限制。

## 环境

- Windows 机 `tablet-bbt8eqb4` / `100.112.50.115`（Win11 build 26200）；`ssh zhengyp@100.112.50.115`；`tools/win/` helper（用法见其 README）。
- ⚠️ **Session 限制**：`ssh` 落在 **Session 0**（1024×768 非真屏）；**真实桌面在交互会话（Session 6/Console）**。DXGI Desktop Duplication / 抓屏须在**交互会话内**运行（参照 W1：daemon 跑在 Session 6），不要在 ssh 的 Session 0 里测屏变。
- 账户/打包见 `screenlab-rules.md` §环境与操作、`screen-assist-status.md` §5。

## 纪律

- 只研究，**不改产品码**（要改先与 YZ 议）。
- **不动共享文档**：不改 `screen-change-detect-62a.md` / `design-vision-scripting.md` / `screen-assist-status.md`；产出只写 `screen-change-detect-62c-win.md`。
- 与 **#62b（Android）并行**：各用各的目标机与临时目录（本分支用 `tools/win/` 或 Windows 侧独立目录），拉回 `tools/blobs/` 避免同名。
- 真机验证；不用自写 e2e 自证。
- 图不进上下文（数据层）；看图用附件。
- 完成后**飞书通知 YZ 就停**，不链式交接。

## 回到 #62

- 产出：`screen-change-detect-62c-win.md`（Windows 矩阵 + 推荐 + 证据）。
- 父会话 **#62**：title `screenlab #62 - 电脑/视觉-讨论`，session id **`ses_f27b92b04ffeF5hz7zAFZPi026`**。
- 恢复：`attach-kilo <session-id>`（或 `kilo attach http://127.0.0.1:4097 -u kilo -p kilo --dir /home/zhengyp/work/A/locus`）。
- 回法：把 Windows 矩阵结论带回 #62（#62 统一合并 62b/62c 两份）。
- ⚠️ **bridge/飞书 pin**：与 #62b 并行时，pin 只能指一个会话；确认指到当前需要 YZ 交互的那个。

## 锚

- `design-vision-scripting.md`（已定 13/14、待定 A/F）
- `screen-change-detect-62a.md`（X11 矩阵 + 格式参照）、`handoff-screen-62b.md`（并行分支）
- `screenlab-rules.md`、`screen-assist-status.md` §0/§5
- `screenlab/service/daemon.py:296`（frame_hash）、`tools/win/`
