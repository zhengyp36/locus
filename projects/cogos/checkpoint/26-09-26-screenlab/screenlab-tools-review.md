# screenlab-tools-review.md · 工具线状态盘点（#72 会话审阅 · 2026-09-26）

> **用途**：把 #62c→#71 工具开发的**真实现状**收成一处，供后续会话免于重读全部 handoff/design。
> **性质**：二手描述；动手前以**代码 / 实测**为准。规则 `screenlab-rules.md`；目标 `spec-screen-1.md §0.0`。
> 上游素材：`screenlab-work.md`、`design-vision-computer-fusion.md`、`design-vision-scripting.md`、`screen-change-detect.md`、`screen-android-issues.md`、`handoff-screen-{67,68,70,71}.md`。

## 0. 这条线是什么

**「视觉 × 坐标闭环」线**（≠ 之前的 3a 平台线）。目标 = usage-first 地把 graphics 面做成**模型能真的**"看图 → 指位置 → 点 → 确认"，并让视觉工具（`cogos/image_ctx`）承接几何/缩放/坐标。核心信条：**模型只看语义（look/mark/act），几何全由工具做**。

产物 = 一个 **CLI 原型** `screenlab/tools/imgctx.py`（驱动产品 `screen/1`）+ 一批产品机制增量。

## 1. 状态（分三层）

### 1.1 模型面（设计已定，未落产品）
- `design-vision-computer-fusion.md §3`：模型面只暴露 `look` / `zoom`(走 `see` 开窗) / `mark`(可选) / `act`；**settle 内部化**；图 id / 帧 id 全内化（模型不可见）。
- 终态 = **并入 `computer` 工具（v2）**，模型面只此一个入口。
- **状态：设计完，未实现。**

### 1.2 原型 CLI（已通、已提交）
- `screenlab/tools/imgctx.py` 动词：`see / mark / adjust-mark / unmark / coord / look / act`；`--backend {x11,android,win}`。
- `look/act` 走产品 `screen/1`（`agent/impl/graphics.py::ScreenChannel`）；`see/mark/coord` 走 `image_ctx`，作用在 `blob_get` 拉回的帧上；`act` = 重抓→目标区分块 diff 只**报告** `stale/drift_bbox`（不拒）→`act`→有界 settle 落点帧。
- 后端脚本：`tools/{x11.sh,android.sh,windows.sh}`（+ `*_selftest.py`）；传输兜底 `tools/screendiff.py`。
- **三平台使用角度验收全通（独立真值，非 selftest）**：#71
  - X11：`imgctx --backend x11 look→mark→coord→act`；真值 `xdotool getwindowgeometry` 窗 `508,360 266x120`、pointer==device `(724,458)`、`x11.sh zenity` 1→0。
  - Android：uiautomator 真值 Chrome 图标 `(338,2125)`==coord/device，`foreground` 变 Chrome activity。
  - Windows：Tk 靶真值 center `(900,550)`==coord/device，READY→**HIT**。
- **仓库**：`feat/screenlab-p2` @ `d89abd7`，**工作树干净、与 origin 同步**；`tests/screenlab + tests/image_ctx` **71 passed**。
  - 相关提交：`832e085`（Domain 持久化）· `23c04e8`（DXGI 后端+GDI 回退）· `975cc60`（分块 diff）· `c9d6ad6`（vision loop 走产品 screen/1）· `fa49a89`（act settle + drift 只报告）· `14937da`（X11 走产品面）· `d89abd7`（`session-start.sh` create 默认值 bug 修复）· `0dc9a2b`（Windows 3a + Android app）。

### 1.3 机制增量（产品码，局部落地）
- `screenlab/service/backends_win.py` 加 `DxcamCapture`（真 DXGI）+ `pick_capture()`（默认 dxcam，`SCREENLAB_CAPTURE=gdi` 强制）。
- `screenlab/service/change.py`：`fingerprint`（x8 降采样 hash）+ `diff_bbox`（分块 bbox），平台无关兜底；单测 5 passed。
- `image_ctx/domain.py`：`Domain.open(root, state=)` + `save/load`（原子写、重建去重表、`_id_gen` 重置）。
- `install/session-start.sh`：create 分支补默认值（`alloc_display()` / `RES` 回读 `session.json` / XAUTH 默认）。

## 2. 关键缺口（评估核心）

1. **原型 ≠ 工具**：`cogos/agent/` **无任何 `image_ctx` 引用**（已核对）→ agent 还碰不到视觉闭环。**v2 接入是唯一明确未做的关键动作**（当初被列进"不做"）。
2. **第一原则只近似满足**：`design-vision-computer-fusion.md §1` 要求"模型必须作用在它看到的那张图"；`#70` 用**重连重抓近似**（跨 CLI 调用保不住同一 `snapshot_id`）。硬保证需**持久连接 / 客户端 broker**（已记遗留）。
3. **Android 控制能力不全**（`screen-android-issues.md`）：只有单点 tap；**无启动 App/URL、无打字、无导航手势（HOME/BACK/swipe/长按）**。按"能力完整"（`design-agent-tools §1`）Android 不算收尾——只完成"看+点"。
4. **transport 修正未做**（标"待 YZ 定"）：`daemon.py` 每帧 PNG 编码/哈希、Android raw MediaProjection 路径、X11 XDamage。性能项，非阻塞。
5. **`capture→see` 源图身份**（`design-vision-scripting.md` 待定 A）：是否保留 capture 裁窗 / `max_dim` 未定。

## 3. 待 YZ 的决策口（阻塞"继续"）

- **v2 接入形态**：模型面是否只暴露 `look/zoom/mark/act`、几何与 transport 全内化？
- **act 硬保证**：做持久连接/broker，还是接受重抓近似？
- **Android 能力补齐**是否算"工具收尾"范围（倾向：算）。
- **transport 修正**现在做还是后置（倾向：后置）。
- （沿用上一轮对齐）工具线**止步 Windows/Linux/Android**；`agent 自己有电脑` 这一能力面视为足够。

## 4. 建议的"收尾定义"与下一步

> **工具线收尾 = 模型面并入 `computer` 工具（v2）＋ 三平台以 agent 身份真用一遍 ＋ Android 补到"能完成一般任务"（至少导航 + 打字 + launch）。**

- 顺序：先定 v2 接口形状（设计，阻塞项）→ 落接入 → 补 Android 能力；transport 修正后置。
- "所有工具收尾后再汇总、再谈外圈/内圈"——顺序仍成立；但**先区分"原型通过"与"工具可用"**，否则会误判工具已收尾。

## 5. 文档卫生提醒

真实现状目前分散在 6+ 份（`screenlab-work.md` / `design-vision-scripting.md` / `design-vision-computer-fusion.md` / `screen-change-detect.md` / `screen-android-issues.md` / 多份 handoff）。**本轮即为一次汇总时机**：把"已通(原型) / 未做(v2 接入) / 待定(4 口) / Android 缺口"收成可判定清单（即本文件 §2–§4），后续会话不必再拼读。

## 6. 锚

- 代码：`cogos/screenlab/tools/{imgctx.py,*_selftest.py,x11.sh,android.sh,windows.sh,env.sh}`、`cogos/screenlab/service/{change.py,backends_win.py}`、`cogos/cogos/image_ctx/domain.py`、`cogos/screenlab/install/session-start.sh`
- 环境（`screenlab/tools/env.sh`）：CentOS `100.100.137.78`（账户 `zhengyp` uid 1000，socket `unix:/run/user/1000/screenlab.sock`，display `:10`，1280x800）；Windows `100.112.50.115`（assist/zhengyp）；Android `192.168.1.175:5555`（MAR-TL00，API29）
- 设计/目标：`spec-screen-1.md §0.0`、`design-vision-computer-fusion.md`、`design-vision-scripting.md`
