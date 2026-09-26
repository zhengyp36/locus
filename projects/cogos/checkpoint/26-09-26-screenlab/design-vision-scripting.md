# design-vision-scripting.md · 视觉工具脚本化（给 kilo 先用）

> 来源：#62 会话与 YZ 讨论（2026-09-25）。上游工具 = cogos 的 `cogos/image_ctx/`（+ `cogos/cog_ctx/`、`cogos/img_tool/core.py`），
> 设计文档 `cogos/docs/design-vision-image-fields.md`（+ p1/p3 spec、checklist）。`cogos/research/vision/` 是更早的实验归档，非包代码。
> 定位：先把该工具脚本化，让 **kilo**（当 agent 角色做图形界面验收时）能做视觉定位、拿准坐标；同一批函数日后产品 agent 复用。
> 核心信条：**模型只看语义（框/看/mark），几何（缩放/crop/坐标换算）全由工具做。**

## 工具现状（事实基线）

- 模型面工具：`see`（开图/调视野）、`mark`、`adjust_mark`、`unmark`、`coord`（纯读，出 `@原图` 坐标）。
- 对象图：`Domain`（root 目录 + `sources`）→ `Source`（`registry: FIG_id→View`、`figs: window_key→FIG_id`）→ `View`（`window` + `annos`）。
- 模型只在 **`@窗口`**（相对参考 FIG 视野）上动作，坐标可负/越界；`@全图`/像素映射由程序算（`view.py`、`anno_to_src`）。
- `render` 是唯一碰位图/缓存处：crop 窗口 → 主动降采样到 `max_dim` → 叠加标注；缓存指纹 `(path, window, annos)`。
- 状态**全在内存**：`Domain.sources` / `registry` / `annos` 不落盘；`cache/` 只存渲染 PNG，`images/` 存源图副本（`images/<md5>`）。
- FIG id 计数器 `view._id_gen = itertools.count(1000)` 是**模块级全局**，不在对象图里。
- 尚未接入 agent 运行时（`cogos/agent` 无引用）。

## 已定结论

1. **复用库函数，脚本=薄适配**：不复刻 schema、不复制逻辑；schema 层留给未来产品 agent。脚本只做 argv→函数 + 状态管理 + 结构化输出。
2. **归属**：放 `../checkpoint/tools/`，import `cogos/image_ctx`；不塞进 cogos 产品路径。
3. **状态持久化**：在 `Domain` 上加 `save/load`（或 `Domain.open(root, state=path|None)`）。`state=None` → 纯内存（= 现状，行为不变）。
4. **state 命名**：state 文件名**相对 domain 路径**命名（多 state = 多命名）；**同一 state 用 flock** 防并发。
5. **写回时机**：**每次改状态的调用后立即落盘**（`see`/`mark`/`adjust_mark`/`unmark`），不能只靠"进程退出时写回"（脚本每步一进程，可能被 cancel/SIGKILL）。
6. **id 计数器纳入 state**：load 时把 `_id_gen` 重置到 `max(已恢复 fig id)+1`，否则撞 id。
7. **恢复时重建去重表**：必须同时重建 `Source.figs[window_key]`，否则之后 `see` 同窗口会新铸 FIG（引用分叉）。
8. **作用域（跨步关键）**：
   - FIG = `(path, window)`，id 全局递增、唯一，作用域 = **Domain（进程内存）**。
   - ANNO 存在 `View.annos`，id 是 **per-FIG** 编号，引用必须**成对 `(FIG, ANNO)`**（离开所属 FIG 无意义）；寿命 = 所属 FIG。
   - 只有 `(FIG, ANNO)` 在 state 持久后才是可跨步引用的稳定锚。
9. **看图方式**：`image_ctx` 缓存是**真 PNG 文件**，`Block.image` 是**路径**（非 base64）。kilo **直接 read 该 png 路径当附件**；base64 是更下游发 LM 时的事，与本脚本无关。domain root 用**绝对路径**保证 png 路径可读、稳定；输出前确认文件存在（cache 可清，必要时重渲）。
10. **裁剪/缩放唯一发生在 `render`**：画面**出了工具就冻结**，kilo read 原样读，不得在别处再裁/缩。换视野/放大**唯一途径是 `see`**（登记 window）。归一坐标对等比缩放免疫（render 内降采样无碍），对**未登记的裁剪**不免疫。
11. **坐标产出**：`coord` 给 `@原图` 归一坐标（+像素），模型不做换算；`@原图` 归一坐标即喂 `act` 的候选（见待定 B）。
12. **建议先做最小链** `see` / `mark` / `coord`（覆盖"定位坐标"主链），`adjust_mark`/`unmark` 后补。
13. **capture 与视觉工具分工**：默认 `capture` **整屏、原生**一帧 → 交给视觉工具全权（看哪/多细/标哪/算坐标）；`coord` 的 `@原图` 归一 = 相对整帧 = 整屏 = `act` 的归一系。`capture` 的 `center/size/max_dim` **不作语义缩放**，仅在**整帧大到传输成问题**时兜底；用则须把 `window` 复合回整屏坐标（第二个裁剪点）。
    - 理由：① 坐标基准单一、不复合；② 视觉工具需**冻结帧**（重抓会漂移、旧 mark 失效）；③ 本用例带宽非瓶颈（Android 帧 ~65KB）；④ 进视觉工具的帧若再被 capture 缩一次 = 双重降采样、先丢细节。
14. **B/C/D/E 不再讨论**：B（帧/设备坐标空间）= 工具问题，不在封装层验证（怀疑就直接验工具本身）；C（闭环/预算/停缩窗门槛/重试上限）模型自决，工具不限制；D（精度/grid overlay）不做，模型在局部图自己 `mark` 自查即可；E（用真值图验收脚本链）不做——工具已验证。
15. **传输与看屏分离（F 定论；证据 = `screen-change-detect.md`，#62a/b/c 三平台实验）**：分三层——
    - **变化感知层**（常开、**推**）：服务端用**原生 damage** 产出「脏区矩形 + 版本 `generation` + `changed`」；空闲近零成本。平台原语：Windows `DXGI AcquireNextFrame(timeout)`（真脏区、~1.5% CPU、空闲阻塞等变化）；Android MediaProjection VirtualDisplay（**damage 驱动帧到达**；**无原生脏区**，自算分块 bbox）；X11 `XDamage NonEmpty`（真脏区，Xorg/XFCE）。**通用兜底** = 原始像素分块 diff / x8 降采样 hash（无扩展依赖、极便宜）。
    - **取帧层**（按需、**拉**）：模型要看时拉**一帧新整帧**；**不跑帧流**（Android 全屏 RGBA ~10MB/帧、低分 270×578 也 ~624KB/帧，流式带宽不可行）。
    - **看屏层**：视觉工具在该整帧上工作（= 已定 10 / 13）。
    - **客户端按 `generation` 缓存**：版本未变 → 复用缓存帧、不重取（即"本地取图/N 帧缓存"的收益，不背流式带宽）。
    - **脏区只作变化信号，不做像素级增量重建**（那会退化成视频码流：base 帧 + 周期 keyframe + 丢包恢复）；`move rects` 属 swapchain 平移场景，与 UI 协助无关。
    - **廉价粗触发**（Windows `SetWinEventHook`、Android `AccessibilityService` 事件）有盲区，只作**补充**、不作唯一信号。
    - 真 push/帧流（订阅 + 环形缓冲）留到确有**低延迟持续感知**需求（等 toast/弹窗/动画）时再上——现在 YAGNI。

16. **机制层提供"变化"，模型分析"变化"并决策**：机制层（传输/感知）只给「脏区矩形 + 版本 `generation` + 时间戳」+ **判断所需素材**（能按脏区/版本按需取到像素：脏区小图 / 变化前后对比）；**不做判断、不做门闸、不语义标注**（不贴"弹窗/加载中"）。模型层分析"变的是什么"、判断是否影响当前意图、决定**看/等/动手/放弃**，全程**有界**（防 livelock）。前提 = 已定 15 的按需供图；变化区域只是视觉工具又一个"要看的地方"（`see`→`mark`→判断）。
    - 推论：`act` 不等待"无变化"；变化只用于"是否再看"与 act 后校验（`generation` 保持"座位/世代"语义，**不绑每次像素变化**）。

## 传输层修正清单（产品码，待 YZ 定）

> 由实验实测支撑；均为**待改**，非已定。核心铁律：**杀掉每帧 PNG 编码 + 传输**。

- `screenlab/service/daemon.py:296` 全帧 **PNG 编码后 sha256**（最贵：X11 ~29% CPU / Win ~45ms / Android 继承 0.5–0.9s 编码）→ 换**原始像素分块 diff / x8 降采样 hash**或改用原生 damage。
- `screenlab/service/backends_android.py:78` 每次 `adb exec-out screencap -p`（0.76–1.19s）→ 改 **MediaProjection 投影采集（raw）**。
- `screenlab/service/backends.py:120` X11 `ximagesrc use-damage=false`（把现成 damage 关了）→ 评估开 **XDamage**（Xorg/XFCE 下可用；Wayland/mutter 另验）。
- Windows 采集 → **DXGI Desktop Duplication**（真脏区、~1.5% CPU）；注意 vtable 槽位 / 同 adapter / DPI / 必须在交互会话（见 `screen-change-detect.md` 接入陷阱）。

## 待讨论

- **A. capture→see 的源图身份**：`add_src` 按 **path 字符串**幂等、资产拷成 `images/<md5>`；同一路径重复 `see` 会拿旧 Source/旧帧。
  - 现状事实：`screen/1` 的 `capture` 已把帧存成**每帧唯一路径**（`/tmp/screenlab-frames/frame-<pid>-<seq>.png`，`_seq` 自增）；服务端 `_crop_resize` 已具备 range+scale。
  - 已被已定 13 大幅收敛（默认 capture 整屏原生 → 视觉工具）；残余待定：是否保留 capture 裁窗兜底、`capture` 的 `max_dim` 是否保留。
- **F（已定）**：传输与看屏分离的结论见已定 15；实验证据见 `screen-change-detect.md`。

## 锚

- 工具代码：`cogos/cogos/image_ctx/{tools,view,render,domain,schemas}.py`、`cogos/cogos/cog_ctx/{context,manager}.py`、`cogos/cogos/img_tool/core.py`
- 设计：`cogos/docs/design-vision-image-fields.md`（+ `-p1-spec` / `-p3-spec` / `-checklist`）、`cogos/docs/vision-system-design.md`
- 缺口清单：`screen-android-issues.md`（2b）、活文档：`screen-assist-status.md` §0/§4、规则：`screenlab-rules.md`
- 屏变感知实验（#62 分支，三平台）：`screen-change-detect.md`（X11/Android/Windows 原语 + 实测）；探针 `tools/android-probe/`、`tools/win/62c/`
