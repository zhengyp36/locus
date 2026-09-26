# screen-change-detect.md · 感知屏变方法（三平台汇总）

> #62 子分支实验汇总（**合并 62a=X11 / 62b=Android / 62c=Windows**）。纯研究，不改产品码。
> 规则见 `screenlab-rules.md`；上游设计与待定见 `design-vision-scripting.md`（待定 F）。
> 只记录**能力**（能拿到什么信号）；粒度取舍、传输形态留 #62 汇总决策。

## 目标

服务端如何高效感知屏幕变化：能拿**脏区矩形** / 仅"变了" / **免费顺带**；成本（CPU/带宽/延迟）与可靠性；接入点 + 代码锚。每平台一条推荐 + 真机实测证据。

---

## X11（#62a · surface-centos-9）

### 环境事实

- **会话拉起**：VM 冷启后 gdm **未运行**（`systemctl is-active gdm` = inactive，尽管 default=graphical.target、autologin=human）。执行 `systemctl start graphical.target` 后 gdm active，autologin 起 human 会话，X socket `/tmp/.X11-unix/X0`。
- **桌面栈**：实为 **XFCE 4.18 + xfwm4（compositing=true）+ Xorg**（`WaylandEnable=false`）——**不是** mutter/Wayland。屏幕 **1280x800**。结论可能不外推到 XWayland/mutter。
- **扩展**：`DAMAGE`、`XFIXES`、`MIT-SHM` 均可用（经 python-xlib `query_extension`）。
- **工具**：有 `xrandr`/`import`/`gcc`/`pip3.11`/`python3.11`；缺 `xdpyinfo`/`xwininfo`/`xprop`（非必需）。pypi 可达。
- **补装**：`python-xlib`、`numpy`（pip）；`libX11/Xdamage/Xext/Xfixes/Xcomposite-devel`（编译 C 探针用）。
- **DPMS 会熄屏**：抓屏前须 `xset s off -dpms` 并 XTEST 键唤醒。
- **负载**：`changer.py`（确定性窗口 move / paint），非自写 e2e（规则）。

### 结果矩阵（X11）

| 方法 | 信号类型 | 粒度 | 成本（实测） | 可靠性 | 锚点 |
|---|---|---|---|---|---|
| XDamage root, Level=**NonEmpty(L0)** | **脏区矩形** | 真实窗口矩形（如 `40,200,400,300`） | ~67 ev/4s；probe CPU ~4–6% | 好（Xorg/XFCE） | `libXdamage` / `Xlib.ext.damage` |
| XDamage root, Level=**BoundingBox(L3)** | 仅"变了" | 恒为整屏 `0,0,1280,800` | ~75 ev/5s；同量级 | 好，但**无粒度** | 同上 |
| XDamage root, Level=**Delta(L1)** | 脏区矩形 | 与 L0 相近 | 同 L0 | 好 | 同上 |
| XDamage **窗口**级 | 重绘细矩形（如 `84,20,100,60`） | 窗口内 | ~82 ev/4s | **移动时 0 事件**（须挂 root）；偶发 BadDrawable | 同上 |
| gstreamer `ximagesrc use-damage` | **无可用信号** | — | — | **不可用**：true/false 缓冲数无差别，且屡屡 0 buffer | `gst-plugins-good` libgstximagesrc |
| **MIT-SHM 抓帧 + 64 分块 diff** | 变化块数 + bbox（如 `0,192,448,320`） | tile=64 | **~5–6ms/帧，CPU ~2–3%** | 好，无需 X 扩展 | `MIT-SHM` |
| `XGetImage` + 分块 diff | 同上 | tile | ~12–15ms/帧，CPU ~10% | 好但慢 | `XGetImage` |
| 整帧 hash / x8 降采样 hash | 仅"变了" | 全帧 | ~30ms/帧，CPU **~29%**（瓶颈在抓帧，非 hash） | 该轮未捕捉到变化，**数字待复测** | `daemon.py:295 frame_hash` |
| XDamageAdd（合并多 damage） | — | — | — | 报 `BadDrawable`，未打通（次要） | `XDamageAdd` |

- 组合 6s 实测：XDamage 记 **93** 事件、SHM 分块 diff 记 **81** 变化帧、负载日志 **83** 次移动 ⇒ 两者都能跟住变化。
- 注：probe CPU 含负载进程，绝对值待分离复测；相对量级可信。

### 初步推荐（X11）

**XDamage(root, Level=NonEmpty) 取脏矩形 + MIT-SHM 分块 diff 兜底/校验**。
- 要坐标/省带宽 → XDamage L0（真矩形，成本低）。
- 只要"变了"或需自证 → SHM 分块 diff（无扩展依赖、跨环境最稳）。
- **不采用** gstreamer `ximagesrc use-damage`（当前不可用）。
- 当前 `daemon.py` 的"全帧 PNG 编码后 sha256"最贵（~29% CPU 级）且依赖编码器，应替换。

---

## Android（#62b · nova 4e / SDK29）

### 环境事实

- 设备 `nova 4e / MAR-TL00`，Android 10 / EMUI 10 / **SDK29**，arm64-v8a，屏 **1080×2312@480**；wifi adb `192.168.1.175:5555`（不用 USB）。
- 无 `screenrecord` 二进制（EMUI 移除）；有 `input`、`uiautomator`（`assist` MainActivity 常刷新时 `could not get idle state`，须先停 app）。
- **研究探针**（独立包 `com.screenlab.probe`，**不动产品码**）：`checkpoint/tools/android-probe/`——MediaProjection `VirtualDisplay`+`ImageReader`，对**原始 RGBA 像素**做 per-cell 差分（每 cell 固定 4×4 样、比 RGB 差和）；另一 `AccessibilityService` 只计数事件类型。
- 负载：`adb shell input swipe` 滚设置列表（确定性 UI 变化，非自写 e2e）。
- 三档分辨率（270×578 / 540×1156 / 1080×2312）cell 尺寸都取 **≈96 全屏像素**，保证 bbox 粒度一致、只变显示分辨率/带宽。

### 结果矩阵（Android）

| 方法 | 信号类型 | 粒度 | 成本（实测，load 均值） | 可靠性 | 锚点 |
|---|---|---|---|---|---|
| `screencap`（raw RGBA，去掉 `-p`） | 需轮询/比对 | 全帧 | **~260–290ms/次**（10MB，不编码） | 好，但高频不可行 | `adb screencap` |
| `screencap -p`（PNG） | 需轮询/比对 | 全帧 | **~0.76–1.19s/次**（PNG ~134KB，编码占 0.5–0.9s）；加 wifi 传输总 ~0.8–1.5s | 好，但最贵 | 现状 `backends_android.py:78` |
| MediaProjection VirtualDisplay(270×578)+ImageReader+原始像素分块 diff | **脏区分块 bbox** | cell≈96 全屏px | diff ~2ms/帧；空闲 ~2.7% CPU（~4fps 心跳）；滑动 **~6.2% CPU（max ~13）、~29fps、56–64% 帧判定变** | 好（无原生脏区，自算） | `CaptureService.startProjection`、`tools/android-probe/ProbeService.java` |
| 同上 540×1156 | 分块 bbox | cell≈96px | diff ~2.4ms/帧；滑动 ~7.3% CPU（max ~16）、~31fps | 好 | 同上 |
| 同上 1080×2312 | 分块 bbox | cell≈96px | diff ~2.7ms/帧；空闲 ~2.7%；滑动 ~6.2% CPU（max ~13）、~28fps、chg ~64% | 好 | 同上 |
| **VirtualDisplay 帧到达节奏** | 仅"忙/闲" | 全帧 | 免费（随流）；静止后 ~0–4fps（启动突发后接近 0，均含突发）、滑动 ~29–34fps | 好（damage 驱动） | `ImageReader` 回调 |
| **AccessibilityService 事件计数** | 仅"变了" | 窗口/内容事件（**无几何**） | 空闲 ~0（~5 ev/10s）；滑动 ~5–6.5 ev/s（以 `WINDOW_CONTENT_CHANGED` 为主） | 粗触发、粒度差；视频/自绘/部分 WebView 疑盲区（未验） | `InjectService.onAccessibilityEvent`、`ProbeA11yService.java` |
| MediaProjection **原生脏区矩形** | — | — | — | **不存在**（Surface 只给 buffer，无 damage rect） | API 限制 |
| MediaCodec H.264 帧统计 / minicap | — | — | — | **未做**：EMUI 无 `screenrecord`；P 帧统计需额外编码链路；minicap 需 arm64 二进制 | — |

### 关键观察（Android）

- **成本与差分分辨率几乎无关**（270×578 与 1080×2312 的 CPU/耗时同量级）→ 瓶颈在 VirtualDisplay 合成/回调，不在自算 diff；**可直接全分辨率原始分块 diff**，不必先降采样。
- 真正的贵点是 **PNG 编码 + 传输**：`screencap -p` 编码 0.5–0.9s，现状 `daemon.py:296` 对 PNG 字节 sha256 继承这一成本；换**原始像素 diff** 可完全绕开。
- **MediaProjection/VirtualDisplay 是 damage 驱动**：静止画面下 `ImageReader` 基本收不到新帧（空闲 3s 后帧数不再增长、CPU 掉到 ~0–3%），变化时 ~30fps 连续出帧 → "帧到达节奏"本身是**免费的忙/闲信号**。
- 脏区须自算；分块 diff 给 cell 粒度 bbox（如 `67,300,90,369`@270×578），粒度 = cell 尺寸（本测 ≈96 全屏px）。
- 低分投屏的价值在**传输/带宽**（270×578 RGBA ≈624KB/帧 vs 全屏 ≈10MB/帧），不在设备端 CPU。

### 初步推荐（Android）

**MediaProjection `VirtualDisplay`+`ImageReader` 常开 + 原始像素分块 diff** 作屏变感知：
- 空闲 ~3% CPU、滑动 ~6–7% CPU，diff ~2–3ms/帧，直接给分块 bbox；全分辨率也吃得下。
- 触发后再取帧；取帧走**原始 RGBA → 服务端 diff/编码**（或仅按需 PNG），**不要每帧 PNG**。
- 可选叠加 **AccessibilityService 事件**作粗触发（省空闲 diff），但**不能作唯一信号**（覆盖盲区、粒度粗）。
- **弃用**每帧全屏 `screencap -p` + PNG sha256（编码 0.5–0.9s/次 + 传输，无法高频）。

---

## Windows（#62c · tablet-bbt8eqb4 / Win11 26200.9457）

### 环境事实

- **会话**：`ssh zhengyp@` 落 **Session 0**（无桌面）；真实桌面在 **Session 7 = 当前 Console 会话**（`WTSGetActiveConsoleSessionId()==7`，`SM_REMOTESESSION==0`，非 RDP）。探针须以 assist 的交互令牌投进 Session 7（Task Scheduler COM，`LogonType=3`；模板 `tools/win/62c/launch_probe.ps1`）。
- **桌面/显示**：窗口站 `WinSta0`、桌面 `Default`；单一输出 `\\.\DISPLAY1`，**物理 1920×1280 @150% DPI**（非 DPI 感知进程 `GetSystemMetrics` 看到 1280×853）。适配器：Intel UHD Graphics 615（唯一有输出的适配器）+ Microsoft Basic Render Driver（无输出）。
- **工具**：venv `C:\Users\assist\AppData\Local\screenlab\venv` Python 3.11.5，装好 `PIL 12.3.0`、`numpy 2.4.6`、`comtypes 1.4.17`、`dxcam 0.3.0`；有 `csc.exe`（`C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe`，可编 C#/COM 探针）；`dotnet --list-sdks` 为空。
- **负载**：`changer_tk.py`（Tk 覆盖窗定时移动+变色，确定性 changer），非自写 e2e（规则）。
- **DPMS**：Windows 侧无 Linux 的 `xset -dpms` 问题；会话在 Console 且未锁（`LogonUI` 只在 Session 8）。

### 结果矩阵（Windows）

| 方法 | 信号类型 | 粒度 | 成本（实测） | 可靠性 | 锚点 |
|---|---|---|---|---|---|
| **DXGI Desktop Duplication**（`IDXGIOutput1::DuplicateOutput`） | **脏区矩形**（+ move rects、指针位置） | 真实矩形，如 `[60,60,360,175]`、`[1314,1267,1340,1274]` | 8s 抓 **102** 帧（101 帧带脏区，1–6 rect/帧）；本进程 CPU **~1.55%**；空闲帧 `AcquireNextFrame` 超时 100ms | 好（Console 会话） | `dxgi.dll` / `IDXGIOutputDuplication::GetFrameDirtyRects` |
| `IDXGIOutput5::DuplicateOutput1`（BGRA8） | 同族（脏区矩形） | 同上 | 同族（dxcam 默认走此路） | 好；本机裸调用返回 **S_FALSE**，dxcam 视为成功 | `IDXGIOutput5`（IID `80a07424-…`） |
| **`SetWinEventHook`**（全桌面 OBJECT_/SYSTEM_） | **仅"变了"触发器**（无坐标） | 全屏（事件级） | 8s **149** 事件（18.6/s）；CPU **2.3%** | 事件驱动、近零 CPU；**覆盖有盲区**（自绘/GPU 直出/DirectComposition 可能不上报） | `user32!SetWinEventHook`（`WINEVENT_OUTOFCONTEXT`） |
| **GDI `BitBlt` + 原始像素分块指纹** | 仅"变了" + 粗脏块（tile=64） | 块级 + bbox，如 `[60,60,360,240]` | 抓帧 **~26ms/帧**；raw sha256 11.7ms；**x8 降采样 hash 0.32ms**；64 分块 diff 56ms；CPU ~80%（含 PNG） | 全环境可用、无扩展依赖 | `gdi32!BitBlt` / `GetDIBits` |
| **整帧 PNG 编码 + sha256**（现状 `daemon.py`） | 仅"变了"（且依赖编码器） | 全帧 | **~45ms/帧**（最贵） | 可用但最贵 | `screenlab/service/daemon.py:296 frame_hash` |
| **Windows.Graphics.Capture（WGC）** | 帧到达（"变了"，**无坐标**） | 全帧 | 5.3s 收 **57** 帧（10.8 fps，随变化触发）；CPU **3.86%** | 需 Win10 1803+；**无脏区 API** | `Windows.Graphics.Capture` / `windows-capture` pkg |
| DXGI Desktop Duplication 失败恢复 | — | — | — | `AcquireNextFrame` 在切会话/锁屏/UAC/DWM 变化时返回 `ACCESS_LOST`/`SESSION_DISCONNECTED`，须重建 duplication | `DXGI_ERROR_ACCESS_LOST` |

- DXGI 实测同一负载下：`duplicate_output_hr=S_OK`，`access_lost=0`、`other=0`、`coalesced=0`、`protected=0`；got **move rects = 0**（Tk 窗口 `geometry` 移动被并入 dirty，未走 move rects——move rects 主要给 swapchain 内容平移）。
- 指纹等价性（GDI）：同一段负载里 changed 计数 raw hash=42、downsample(x8) hash=34、PNG hash=42（全帧 57 帧）——**x8 降采样 hash 偏差小且成本低两个数量级**。

### 初步推荐（Windows）

**DXGI Desktop Duplication 取脏区矩形为主信号 + 原始像素分块/降采样指纹兜底 + `SetWinEventHook` 作廉价变化触发器。**

- 要坐标 / 省带宽 / 低成本 → **DXGI Desktop Duplication**（真矩形，CPU ~1.5%）。接入点 = 服务端按 `AcquireNextFrame` + `GetFrameDirtyRects`，仅在脏区上传/编码；空闲用 `AcquireNextFrame(timeout)` 阻塞等待，天然省 CPU。
- 无 DXGI 或需自证/跨环境 → **原始像素分块 diff / x8 降采样 hash**（无扩展依赖）；**切勿**再对整帧 PNG 编码后求 sha256（`daemon.py:296` 最贵，应替换）。
- `SetWinEventHook` 可作"变了"的廉价触发器（近零 CPU）来补充，但**不能作为唯一信号**（覆盖盲区）。
- WGC 实测：只给"帧到达（随内容变化触发，10.8 fps 对齐 changer 100ms 节拍）"，**无脏区**；适合整帧低延迟采集，不适合省带宽的变化检测。

#### ⚠️ 接入陷阱（本次踩过，务必记录）

1. **vtable 布局**：`IDXGIOutput` 继承 **`IDXGIObject`**（不是 `IDXGIDeviceSubObject`）。`IDXGIOutput` 方法起于槽 7（`GetDesc`）；`IDXGIOutput1` 的 `DuplicateOutput` 在 **槽 22**（其前是 `GetDisplayModeList1`/`FindClosestMatchingMode1`/`GetDisplaySurfaceData1`），**不是槽 19**。槽位错位会得到 `DXGI_ERROR_INVALID_CALL(0x887A0001)` 或原生 AV，极难定位。权威顺序参照 DXcam `dxcam/_libs/dxgi.py` / `dxcam/core/dxgi_duplicator.py`。
2. **建 D3D11 device**：`D3D11CreateDevice(adapter, D3D_DRIVER_TYPE_UNKNOWN, …, flags, …)`，device 必须与 output **同一 adapter**（DXcam `flags=0` 即可；`D3D11_CREATE_DEVICE_BGRA_SUPPORT` 非必需）。device 与 output 不同 adapter → `DuplicateOutput` 返回 `INVALID_CALL`。
3. **DPI**：装置非 DPI 感知时会看到缩放后的 1280×853，脏区坐标/抓帧尺寸须与 act 的坐标系一致（建议进程 DPI 感知，统一用物理 1920×1280）。
4. **会话**：必须在交互会话（Console）内跑；ssh 的 Session 0 会出现"调用成功但抓空桌面"的静默错误。

---

## 跨平台小结（整理时提炼，供 #62）

- **脏区矩形**：X11（XDamage `NonEmpty`）与 Windows（DXGI）都能拿**真矩形**；**Android 无原生矩形**（只能自算分块 bbox）。
- **免费变化信号**：Windows 有 DXGI **阻塞等变化**（`AcquireNextFrame(timeout)`，空闲 ~0 CPU）+ WGC "帧到达"；Android 有 VirtualDisplay **damage 驱动的帧到达**（静止不出帧）；X11 需挂 XDamage。→ "服务端按变化推送"的原语**各平台都有**，Windows 最干净。
- **通用兜底**：**原始像素**的分块 diff / x8 降采样 hash（无扩展依赖、成本极低）。
- **共性铁律**：贵的是**全帧 PNG 编码 + 传输**（Windows PNG 45ms vs x8 hash 0.32ms；Android PNG 0.5–0.9s vs raw diff ~2ms；X11 PNG sha ~29% CPU vs SHM diff 2–3%）→ **三平台都指向"杀掉每帧 PNG"，改原始像素低成本指纹**。
- **廉价粗触发**（都不能作唯一信号，有盲区）：Windows `SetWinEventHook`、Android `AccessibilityService` 事件。
- **会话约束**：采集都须在**用户交互会话内**（Windows Session 7/Console 非 ssh 的 Session 0；Android 需投影前台；X11 需 human display）。

## 待办 / 未决（三平台合并）

- 复测稳定数字（多轮、分离 probe 与负载 CPU、带宽/事件大小）；DXGI 空闲阻塞的延迟/唤醒成本。
- **XWayland/mutter** 情形未测（X11 现为 Xorg/XFCE）——如产品要覆盖 Wayland 再另验。
- DXGI `move rects` 实测为 0，需换 swapchain 平移场景（视频/游戏）复测其粒度；多显示器未测。
- Android：MediaCodec H.264 帧统计 / minicap 未做；a11y 盲区未验。
- WGC `frame_buffer` 在 `windows-capture` 中的格式/尺寸语义未细究。
- **粒度取舍（dirty vs move rect）与传输形态（脏区推送 vs 整帧推送 + 本地缓存）留 #62 汇总决策。**

## 证据

- **X11**（靶机 `/tmp/x11/`，临时未回拉）：`changer.py`、`xdamage_probe.py`/`.c`、`xcap_probe`、`framehash_probe.py`、`*.log`。
- **Android**：`checkpoint/tools/android-probe/`（`ProbeService.java`、`ProbeA11yService.java`、`probe-run.sh`、`drive.py`、`analyze.py`、`runs/`）。
  - 代表数（load 均值）：q270 `fps≈29, proc≈2.0ms, cpu≈6.2%(max13), chg≈57%`；h540 `fps≈31, proc≈2.4ms, cpu≈7.3%(max16), chg≈56%`；full `fps≈28, proc≈2.7ms, cpu≈6.2%(max13), chg≈64%`。idle：`~4fps, proc≈2.5–3.5ms, cpu≈2.5–3%`。
  - a11y（clean 单实例）：idle ~5 ev/10s；load ~105 ev/16s（≈6.5/s，`WINDOW_CONTENT_CHANGED` 为主）。
  - `screencap`：raw 5× 261–287ms；`-p` 3× 759/765/1189ms（134KB）。
- **Windows**：`tools/win/62c/`（`probe_dxgi.py`、`probe_dxcam.py`、`probe_winevent.py`、`probe_gdi.py`、`probe_wgc.py`、`changer_tk.py`、`launch_probe.ps1`、`launch_cmd.ps1`）。临时产物在靶机 `C:\Users\assist\screenlab-62c\`（未回拉）。
  - DXGI 关键输出：`duplicate_output_hr=0x00000000`；`acquired=102`、`frames_with_dirty=101`、`dirty_min=1`、`dirty_max=6`；示例脏区 `[1314,1267,1340,1274]`（光标区）、`[60,60,360,175]`（changer 窗）；`cpu_pct=1.55`。
  - WinEvent：`total_events=149`、`events_per_sec=18.6`、`cpu_pct=2.34`；分布以 `OBJECT_STATECHANGE` 为主。
  - GDI：`grab_ms.avg=25.99`、`digest_downsample_ms.avg=0.32`、`tile_diff_ms.avg=55.9`、`png_encode_sha_ms.avg=45.18`。
  - WGC：`frames=57`、`fps=10.82`、`cpu_pct=3.86`。

## 锚

- `screenlab/service/daemon.py:296`（`frame_hash`，全帧 PNG sha256）
- `screenlab/service/backends.py:120`（X11 `ximagesrc use-damage=false`）
- `screenlab/service/backends_android.py:78`（`adb exec-out screencap -p` 全屏）
- 探针（研究，非产品）：`checkpoint/tools/android-probe/`（Android）、`tools/win/62c/`（Windows）、靶机 `/tmp/x11/`（X11）
- DXGI 权威定义：`dxcam/_libs/dxgi.py`、`dxcam/core/dxgi_duplicator.py`
- API：`XDamage`/`MIT-SHM`（X11）、`MediaProjection`/`AccessibilityService`（Android，均无原生脏区）、`IDXGIOutputDuplication`/`Windows.Graphics.Capture`（Windows）
- 规则 `screenlab-rules.md`；上游 `design-vision-scripting.md`（待定 F）
