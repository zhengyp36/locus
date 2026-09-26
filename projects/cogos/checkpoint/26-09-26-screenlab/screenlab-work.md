# screenlab-work.md · 开工工作单（活文档，就地改）

> **任务态落文件**：会话可弃，进度只活在本文件。规则 `screenlab-rules.md`；设计 `design-vision-computer-fusion.md`；目标 `spec-screen-1.md` §0.0。
> **⚠️ 本文件与设计稿都是"二手描述"；动手前一律以代码 / 实测为准**（防臆断；设计里的 image_ctx API 未经本会话核对）。

## 锁定决策（2026-09-26）

- **首个平台（视觉 / 坐标闭环）= X11（surface-centos-9）**；Android 第二、Windows 第三。
  - X11 先：迭代快、地面真值现成、注入走 XTEST、**无物理同意**、可无人值守。
  - Android 第二：那是逼"通用兜底"（自算分块 diff）+ 修 #61 坐标链的地方。
- **工作方式**：任务态落文件；一会话一 work-item + 锁；无人值守（X11 先可行）；kilo 尽量独自完成，**只在目标真推不出时升级**。
- **不碰**：接进真正的 `computer` 工具（v2）、settle / change_hint、传输改造（`daemon.py:296` 等）、非 tap 动作、push / 采样。

## 切法

- **Slice 0（无设备）**：视觉适配器脚本（`see/mark/coord` + `Domain` state）在**静态 PNG** 上验。
- **Slice 1（X11）**：`look/zoom/act` 闭环 + 地面真值。
- **Slice 2（Android）**：换后端 + 修 #61 坐标链 + 传输 / 兜底。

## Slice 0（已完成）

**目标**：`../checkpoint/tools/` 下做薄 CLI 适配，包 `cogos/image_ctx`，在静态 PNG 上跑通 `see / mark / coord`，用已知像素真值验收。

**步骤**

1. 读 `cogos/cogos/image_ctx/{tools,view,domain,render,schemas}.py`，确认真实 API、以及 `Domain` 能否加 save/load（已定 3–8）。**以代码为准，纠正设计稿的臆断。**
2. 建 CLI（argv→函数 + 状态管理 + 结构化输出）；state 就地落盘 + flock；id 计数器入 state；load 重建去重表（已定 3–8）。
3. 用一张**已知图**跑 `see → mark → coord`；验收 = coord 与已知真值吻合（含缩放 / 裁剪场景）。
4. 结果记回本文件；按规则通知 YZ。

**停止门（2026-09-26 修正）**：裁决来自目标 §0.0，不由 YZ 决定（规则：只有目标真推不出才升级）。Slice 0 通过 → **依目标自决进 Slice 1**（X11 看/指/放大/点/确认最小闭环），仅当目标真推不出时飞书升级后停。

**工序**：动手前 `set_timer` 10min；`tools/snapshot.sh`（如需靶机状态）；命令走 `terminal_exec`；每步通知不等回复；**改码不 commit**。

## 状态（就地改）

- 2026-09-26：建立工作单；Slice 0 已完成；Slice 1 已完成（自测 ALL PASS）；Slice 2 范围已定，环境已实测**全部就绪**（Android wifi adb + assist 8901 + Windows 9911）；已重交接 #67（`handoff-screen-65.md`）。
- 2026-09-26（#67）：Slice 2 Android 闭环 + #61 坐标链 **完成，自测 ALL PASS**；传输/兜底的通用分块 diff 原语已落地并接入验收；Android 侧"去掉每帧 PNG 编码"的 app 内 raw 路径经实测在 adb 上不划算（见下），留作 YZ 候选。
- 2026-09-26（#67）：10min 到点 ctx 153K/15% → **已交接 #68**（`handoff-screen-67.md`，Slice 3 Windows：换后端 + DXGI 采集）。Windows daemon 实测未跑、assist 交互式会话定，DXGI 实现材料已备（`/tmp/kilo/dxcam/`、`probe_dxgi.py`）。
- 2026-09-26（#68）：Slice 3 Windows **完成，自测 ALL PASS**。纠正 #67 的"daemon 没在跑"（实测 PID 在 assist session 7 监听 9911/9912）。产品 DXGI 采集后端 `DxcamCapture` + GDI 回退已落地、daemon 重启后 `capture_backend=dxcam`；新增 `tools/windows.sh` + `tools/windows_selftest.py`，`imgctx --backend win` 闭环在地面真值 Tk 靶上通过（click 落到真值中心并触发 READY→HIT）。改码未 commit。
- 2026-09-26（#68）：Slice 0–3 全完成 → **已交接 #69**（`handoff-screen-68.md`，含 #62c→#68 回顾素材）。#69 任务 = 加载上下文后**等 YZ**，与 YZ 一起回顾。
- 2026-09-26（#69）：与 YZ 回顾后定方向 = **把脚本整合进产品工具（双向补）**：视觉层留客户端、不改 `screen/1`；用工具已有的 `snapshot_id` 治理；脚本归位到 cogos（排除 `keys/`）。产品增量已 **commit+push**（3 commits → `origin/feat/screenlab-p2`：image-ctx 持久化 / DXGI 后端 / 分块 diff）。已交接 **#70**（`handoff-screen-69.md`）：Win+Android 先验，X11 天亮验。纪律更新：ctx **≤150K** 交接、**阻塞则飞书通知后先做不阻塞的**、整合期**允许 commit/push（不 tag）**。
- 2026-09-26（#70）：**客户端整合落地**。`tools/imgctx.py` 的 `look/act` 改走产品 `screen/1`（`ScreenChannel`）；`see/mark/coord` 仍走 `image_ctx` 作用在 `blob_get` 拉回的帧上。端点按 `--endpoint/--key/--ssh`（默认按 `--backend`）。`act` = 重抓（铸本连接 `snapshot_id`）→ 目标区域分块 diff 漂移只**报告** `stale/drift_bbox`（不拒；硬保证需持久连接，遗留）→ `act` → 重抓落点帧（有界 settle，命中落点即返）。**Android 回归 ALL PASS 3/3**（assist app `tcp:…:8901` + `android_agent.key` + consent-auto；`device=[338,2125]`=uiautomator 真值，Chrome 前台；产品帧切换 app 后可能滞后，故变化判据用独立 adb 两帧、稳定性只看目标区域）。**Windows 回归 ALL PASS**（session 内 consent-auto 测试 daemon `127.0.0.1:19911` + ssh 隧道；`it_daemon.ps1`/`windows.sh it-daemon`；device=真值 (900,550)，靶 READY→HIT）。脚本已归位 `screenlab/tools/`（排除 `keys/`/`blobs/`/缓存，`.gitignore`）。提交 `c9d6ad6`+`fa49a89` 已 push。**X11 切换（抛式 Xvfb → 产品图形面）留天亮验**。产品测试 71 passed。
- 2026-09-26（#71，YZ 指派 #69 审查后收尾）：① **修产品 bug** `screenlab/install/session-start.sh` create 分支——`alloc_display()` 定义无调用者、`DISP/RES/XAUTH` 空串直接跑 `rm -f ""; touch ""; xauth add ""`、`STATE/session.json` 写而不读（C3 半接线）。修法：create 分支进入前补 `[ -n "$XAUTH" ] || XAUTH="$CFG/xauthority"`、`[ -n "$DISP" ] || DISP="$(alloc_display)"`、`RES` 回读 `STATE/session.json`（缺省 `1280x800`）；同步改 `session-create.md` 默认分辨率。**实测 bare `screenlab open zhengyp`（不带任何 flag）起面成功**（display :10、resolution 1280x800、默认 xauth `/home/zhengyp/.config/screenlab/xauthority`）。② **使用角度验收（不看 selftest）**：X11——`imgctx --backend x11 look→mark→coord→act`，read 帧目测 OK 按钮 → mark，独立真值 `xdotool getwindowgeometry` 窗 `508,360 266x120`、目标侧 `xdotool getmouselocation` `X=724 Y=458`==device、`x11.sh zenity` 1→0、read post 帧确认对话框消失；Android——uiautomator 真值 Chrome 图标中心 `(338,2125)`==coord/device，`foreground` 变 `com.android.chrome/ChromeTabbedActivity`，read home 帧；Windows——Tk 靶真值 center `(900,550)`==coord/device，`windows.sh target-state` READY→**HIT `click=(900,550)`**，read 帧见靶窗。**三平台全通**。产品测试 `tests/screenlab + tests/image_ctx` 71 passed。提交见 CHANGELOG/`handoff-screen-71.md`。
- 2026-09-26（#71）：**X11 切换完成**。`tools/x11.sh` 不再自管抛式 Xvfb `:101`，改为驱动产品 surface：`start` = `screenlab open <account>`（账户级 Xvfb 单元组 + 账户 unix socket 上的 daemon）+ 在产品 display 上起 zenity 目标；`stop` = 关 zenity + `screenlab close`。`imgctx --backend x11` 经 `ScreenChannel` + ssh StreamLocal 隧道走产品 `screen/1`，**`x11_selftest.py` 形状不变 ALL PASS**（surface 1280×800，coord/act==(726,458)，zenity 1→0）。产品测试 `tests/screenlab + tests/image_ctx` **71 passed**。
  - **账户实测修正**：handoff 说的 `human`（uid 1002）**不可用**——`/run/user/1002` 0700，zhengyp 的 ssh 隧道连不进其 socket（Permission denied）；改用 ssh 登录账户 **`zhengyp`**（uid 1000，`SL_X11_*`/socket `unix:/run/user/1000/screenlab.sock`），也正合"agent 拥有自己的 surface"。
  - **发现（未改，留 YZ 定）**：`install/session-start.sh` create 分支的 `alloc_display`/默认 `RES` **从未被调用**——不显式给 `--display/--xauth` 时会 `touch ''` 失败；本次显式传参绕过。已 commit+push `14937da`（`origin/feat/screenlab-p2`，不 tag）。
- 2026-09-26（#72）：#71 收尾（bug 修复 `d89abd7` + 三平台使用角度复验全通）后，YZ 要求新会话先加载上下文再**等 YZ**，一起回顾 #62c→#71 开发过程、对齐目标（§0.0）、**从使用角度盘点现状**。已起 #72（`ses_f241ace12ffeUvd2lSD6ZAkTmc`）；下一步方向待 YZ 在对话中提出。
- 2026-09-26（#72，目标对齐）：与 YZ 拉通目标/路线后定——工具线**止步 Windows/Linux/Android**；**收尾关键 = v2 接入**（原型≠工具：`cogos/agent/` 零 `image_ctx` 引用）；顺序 = **定 v2 接口形状 → 落接入（先 X11/Windows）→ Android 动作补齐（排后，按冻结动词集）**；`act` 硬保证并进 v2 一起定；transport 修正后置；**边界**：机制面向工具（record_segment/retrieve/promote…）归回路，不并进工具收尾。已交接 **#73**（`handoff-screen-73.md`）：持有 v2 线，**先与 YZ 对齐接口形状、对齐前不改代码**。本会话（#72/目标对齐）挂起，YZ 需要时再回。
- 2026-09-26（#69 审查）：核 #70/#71 完成度。已 commit+push（`c9d6ad6`/`fa49a89`/`14937da`），`tests/screenlab + tests/image_ctx` **71 passed**、`imgctx_selftest` ALL PASS、工作树干净无 secrets 入库。**纠正方法**：selftest "ALL PASS" 是自证，不算验收 → #69 现场按**使用角度**补验 X11：靶机曾内核 panic（VBoxManage running 但 tailscale offline）→ `VBoxManage controlvm centos9 reset` 恢复后，以 agent 身份 `imgctx --backend x11` 跑 look→mark→coord→act，**独立真值** xdotool 窗几何 (508,360,266×120)、点击后 `x11.sh zenity` 1→0、pointer==device (726,458) → **通过**。**bug 确认**：`session-start.sh` create 默认值未接线（详见 `handoff-screen-71.md`）。**已按 YZ 指派交 #71 续做**（修 bug + 使用角度复验 Win/Android；`handoff-screen-71.md`）。

- 2026-09-26（#73，v2 接口对齐）：与 YZ 逐轮讨论定形 v2 模型面，**封板**（详见 `design-computer-v2-interface.md`）。要点：**图形面只留 `screen_fetch`/`screen_act`/`screen_save` 三个机械动词**；**看图（zoom/mark/对比）拆到通用视觉面**（复用 `image_ctx`，坐标恒回原图空间，模型零换算）；**删掉窗口/帧号/时间戳/back**；`act` 绑 current frame、回操作后整屏+落点、`on_change ∈ {act,skip}`（客户端判 diff）；`launch` 进冻结 op 枚举；`save` = 保留授权控制点；act 硬保证由 `ScreenChannel` 持久连接天然成立。时延降级为决策口④ transport 项（网络非瓶颈，全量抓取/编码才是）。只读 spike 已核：契约与 `ScreenChannel`/`image_ctx`/`change.py` 一致。**未动代码**；ctx 138k 逼近阈值 → 已交接 **#74**（`handoff-screen-74.md`，含实现顺序+只读 spike 结论）。
- 2026-09-26（#73→审核交接）：YZ 告知链条已完成——**#74 落码**（`8b4e685`）、**#75 X11/Windows usage 验证**（`6b78e58`）、**#76 Android 动作补齐+真机验证**（`837b51d`；`ACT_OPS` 加 `drag`、Java `assist` 扩 launch/drag/key）。均在 `origin/feat/screenlab-p2`、工作树干净。YZ 指派：新会话先**独立审核**、再**通知 YZ**、随后**与 YZ 一起讨论** → 已交接 **#77**（`handoff-screen-77.md`，含审核口径与自述缺口 A/B/C）。
- 2026-09-26（#74，落 v2 接入，代码已 commit+push `8b4e685`）：按封板稿落码（**未做 ⑤ usage 真机验证**）。
  - `ScreenChannel` v2（`cogos/agent/impl/graphics.py`）：加 **current-frame 状态**；新增 `fetch/act/save`；`act` = pre-grab→本地 `change.diff_bbox` 判目标区→`on_change∈{act,skip}` 客户端判→注入（模型 op→协议 op：click/move→pointer、scroll/type/key、launch；drag 暂 `unsupported`）→有界 settle→恒回报 `region_changed`、`stable`、`skipped`。旧协议 act 更名 **`raw_act`**（`screenlab/tools/imgctx.py`、`screenlab/tools/agent.py` 已跟进）。
  - 工具注册（`cogos/agent/tools.py::make_screen_specs`，注册于 `cogos/agent/app.py`）：改为 **`screen_fetch`/`screen_act`/`screen_save`** 三动词；`screen_act` schema 含 `region/point/on_change/op∈{click,move,drag,scroll,type,key,launch}/text/keys/dy/to/button/clicks`。
  - **视觉面暴露**：新增 `make_vision_specs`（`see`/`mark`/`coord`，包 `cogos/image_ctx`），app.py 无条件注册；`work_dir/vision` 作 image_ctx 域根；落点标记由工具层 `_render_landing` 用 image_ctx 叠十字（best-effort，失败回退原帧）。
  - `launch` 进 `screenlab/proto/protocol.py::ACT_OPS`（唯一触协议处）。**daemon 尚无 launch 后端**（`_dispatch_act` 未接）→ 现在调用会回 `backend_error`；Android 动作补齐时补后端。
  - 测试：`tests/agent/test_screen.py` 重写（v2 channel fetch/act/save + 三动词 + 视觉面 see/mark/coord）；全量 `pytest` **1231 passed, 4 skipped**；提交前跑过 `tests/screenlab` + `tests/image_ctx`（94 passed）。
  - **已知缺口（非本任务范围，记录）**：模型面工具结果只带图片**路径**；cogos 的 LM 管线 `assemble_tool_messages`（`cogos/lm_service/providers/base.py`）把 tool content JSON 化、`router.infer_modalities` 只看 user content 的 `image_url` → **tool result 的图路径目前不会变成模型可看的附件**。"图不转文字"在 cogos 产品 agent 内尚未真正接通；需另立小任务（Kilo 侧附件机制是另一回事）。
- 2026-09-26（#75，v2 usage 真机验证，全过）：按 #74 交接做 ⑤ 使用角度真机验证，**未动 v2 接口/产品码**。
  - **新增 `screenlab/tools/v2_usage_selftest.py`（X11）+ `v2_usage_win_selftest.py`（Windows）**：走**模型面入口**（`make_screen_specs` 的 `screen_fetch`/`screen_act`/`screen_save` + `make_vision_specs` 的 `see`/`mark`/`coord`）驱动 live `ScreenChannel`（非 `imgctx` CLI）。地面真值独立取：X11 = `xdotool` 窗几何 + pointer；Windows = Tk 靶自报物理 rect/center。`x11.sh` 增 `target-start`/`target-stop`/`target-geom`（重摆/移除/取 zenity 靶窗几何）供真值。
  - **X11 ALL PASS**：surface 1280×800；`screen_fetch` 返整屏原生 PNG(1280×800)；视觉面 `see→mark→coord` 回读 == zenity 窗中心真值 (641,420)，0.15 放大链后仍回同真值；`screen_act(click,point=中心)` 的 `acted`+xdotool pointer ==真值，返回帧含落点标记（与 `screen_save` 原始帧比对，中心邻域有差异像素）；**`on_change=skip`**：fetch 后外部移除目标 → 目标区已变 → **不注入**（pointer 不变）、`region_changed=true`、返回新帧；再点真 OK 按钮（由窗几何推得）→ zenity 1→0，证注入真实有效。
  - **Windows ALL PASS**：it-daemon(`tcp:127.0.0.1:19911`, consent-auto) + Tk 靶真值 center (900,550)/screen 1920×1280；`screen_fetch` 整屏；`coord`==真值（含 0.3 放大链）；`screen_act` 落点==真值、靶 **READY→HIT**(click=[900,550])、落点标记存在。
  - **观察（记录，未改接口）**：`screen_act` 成功路径返回的 `acted` 是**协议 act 的整包**（`{ok,op,acted:{x,y,button,clicks}}`），模型要取的落点像素在**内层 `acted`**——多一层包壳，属 #74 落码形状，是否收平留 YZ/后续定。
  - 回归：`pytest tests/screenlab tests/image_ctx` 71 passed、`tests/agent/test_screen.py` 24 passed。提交 **`6b78e58`**（`origin/feat/screenlab-p2`，不 tag）。
- 2026-09-26（#76，Android 动作按冻结动词集补齐 + 真机验证，全过）：按封板稿 §3 冻结枚举补 Android 的 `launch`/`drag`，导航（back/home/recents）**走冻结的 `key` op**（§3 无独立 nav op；Android 键名映射到 Accessibility `performGlobalAction`）。
  - **协议**：`screenlab/proto/protocol.py::ACT_OPS` 加 `drag`（`launch` 已于 #74 加入）。
  - **Python daemon 后端**（`_dispatch_act`）：加 `launch`（app/URL，无坐标）与 `drag`（配 `to`，归一化起终点→设备像素）；三个后端补齐 `drag`/`launch`——`AdbAct`（`input swipe` / `am start` URL 或 `monkey` 包名）、`XdotoolAct`（mousemove+mousedown/up；`xdg-open`）、`SendInputAct`（mouse event 序列；`os.startfile`）。launch 回显统一为 `{target, as}`。
  - **模型面**：`ScreenChannel._inject` 把模型 `op=drag` 映射为协议 `kind=drag`（`x,y,to`）；`cli.py act` 补 `launch`/`drag`/`--to`。
  - **Android app 服务**（`screenlab/android/src/.../AssistServer.java`）：`act` 由只支持 `pointer` 扩到 `pointer/drag/key/launch`——`drag`→`InjectService.swipe`、`key`(back/home/recents)→`performGlobalAction`、`launch`→`ctx.startActivity`（URL 或包名）。`InjectService` 已有 `swipe`/`global`，本次接上。**APK 已用 `build.sh` 编译通过**；但**未重装到设备**（重装会丢 MediaProjection，需人工重新授权），故 app 端点未做真机验证（记录为缺口）。
  - **真机验证（usage 角度，模型面入口）**：新增 `screenlab/tools/v2_usage_android_selftest.py`——走 `make_screen_specs` 的 `screen_fetch`/`screen_act` 驱动 live `ScreenChannel`（host daemon `--backend android`，adb 采集/注入），真值独立取 `dumpsys activity ... mResumedActivity` / `dumpsys window ... mCurrentFocus`。**23/23 ALL PASS**：`screen_fetch`==`wm size` 1080×2312 原生 PNG；`launch(app)`(com.android.chrome)/`launch(URL)` 真值前台 == Chrome；`key(back)`/`key(home)` 真值前台 == launcher；`key(recents)` 离开 Chrome；`drag` 从顶边下划 → 真值 `mCurrentFocus=Window{... StatusBar}`（通知栏展开），`acted` 回显起终点设备像素。
  - 回归：`tests/agent + tests/screenlab + tests/image_ctx` 299 passed, 3 skipped（`test_impl_term_remote.py::test_write_secret_resolves_and_mutes_echo` 单独跑过、全量下偶发，与本改无关）。提交见下（`origin/feat/screenlab-p2`，不 tag）。
  - **遗留缺口（#75 记录，未动接口）**：① 工具结果图路径未成模型附件；② `screen_act` 的 `acted` 多一层整包包壳；③ 新增：Android app 服务（Java）动作已编译未真机验证（需重装 + MediaProjection 重授权）。
- 2026-09-26（#78，v2 接口独立验收 + 与 YZ 讨论定论）：独立验收 #74~76（证据：代码 + git `d89abd7..HEAD` + 实测；X11/Windows `v2_usage_*` 复跑 **ALL PASS**，回归 99 passed）。**结论：v2 接口层通过**——三动词/不变量/坐标模型/客户端 on_change/settle 内化/save 控制点均与封板稿一致。
  - **接口层仅剩 D2**：`screen_act` 的 `acted` 透传底层协议整包，**设备像素**上模型面（违反「模型可见坐标恒归一化」）。**根因在边界 A**：模型面 = `ToolDef.fn` 的返回（返回即 tool_result；`ToolRegistry.call` `tools.py:1422-1432`→`runtime.py:135-142`→`base.py:166-174`）；协议 = 边界 B，模型不可见。`ScreenChannel`（内部客户端）持协议形状无错，错在 adapter `_act` 没翻译——`path` 收了名（`raw_path`→`path`），`acted` 整包 copy（`tools.py:1201-1202`）把 B 抬过 A。修法只在此处：`acted` 收成状态、落点回归一化 `landing`。
  - **「模型看图」↑ 上层装配**（非 v2 接口）：接口已给图引用（`path`/`image` 字段）；`assemble_tool_messages`/`infer_modalities` 不装配成附件 → gap A 升级为**独立小任务**，决定 §0.0「有反馈」端到端达成。
  - **合理修正（应回填封板稿）**：协议 `ACT_OPS` 加 `drag`（§3 冻结 op 含 drag，原协议无载体）；Android nav 走冻结 `key`。
  - **记录**：gap C（Android app 端点 Java 未真机验证）；保留授权/审计、blob 根 `/tmp` 未收口。
  - 报告：`acceptance-screen-78.md`（修订版）；本轮只审不改、未 commit。

### Slice 0 结果（2026-09-26，#64）

- **API 核对（以代码为准）**：`see/mark/adjust_mark/unmark/coord` 签名与设计稿一致；`Block = (text, image=PNG绝对路径, image_size)`。**偏差**：① `Domain` 原无 `save/load`（纯内存）；② fig id 计数器 `view._id_gen = itertools.count(1000)` 是模块级全局；③ `Source.figs`（去重表）是 `window_key→FIG_ID`。
- **改了 cogos 产品码（未 commit）**：`cogos/cogos/image_ctx/domain.py` 加 `Domain.open(root, state=None)` + `save/load`（JSON，原子写；state=None = 原内存行为）+ `_source_to/from_dict`；load 重建 `registry/figs` 并把 `_id_gen` 重置到 `max(fig_id)+1`（已定 3–8）。
- **新建工具**：`tools/imgctx.py`（argv→函数 + flock state + 单行 JSON；`image` 为真 PNG 路径，直接当附件读）；`tools/imgctx_selftest.py`（已知真值验收）。
- **验收（仿真图 800×600，真值已知）**：`see→mark→coord` 全过，含 ① 整图 cross @原图 (600,150) 像素吻合；② `see` 开窗 0.25 放大后再 mark，coord 仍回 (600,150)（缩放链）；③ rect 尺寸 @原图 (40,30) 像素吻合；④ 跨进程 state 去重回 FIG:1000、id 递增不撞；⑤ 越界 clamp 生效窗口 240×600；⑥ 未知 FIG 报错。`imgctx_selftest.py` exit 0 = ALL PASS。
- **停止门**：Slice 0 验收通过 → 依目标自决续做 Slice 1（裁决者是目标，非 YZ；已报 YZ）。

### Slice 1 结果（2026-09-26，#65，完成）

- **目标机**：surface-centos-9 默认离线 → 已用宿主 VBox 拉起（`ssh zhengyp@100.112.50.115 '"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" startvm centos9 --type headless'`）。**开机后无图形会话**（human :0 不在），故用自管 Xvfb。
- **新增 `tools/x11.sh`**：目标机上自管 Xvfb `:101` + openbox + zenity 点击靶；启动走 systemd-run 瞬态单元（`sl1-xvfb/openbox/zenity`，ssh 不持有后台子进程）。子命令：`start/stop/geometry/capture/click/pointer/windows/zenity/status`。capture **每帧唯一路径**（`blobs/frame-<ts>.png`，因 image_ctx `add_src` 按 path 字符串去重）。`zenity` 按 **class** 数对话框（`xdotool search --class zenity`）；裸 `windows`（`--name ".*"`）会数进 openbox/GTK 内部窗口（实测 26），**不可作存在性判据**。
- **`imgctx.py` 加 Slice 1 动作**：`look`（x11 capture → image_ctx 新 FIG）/ `act`（anno 的 `@原图` 归一 → ×屏幕几何=设备像素 → `xdotool` 点击 → 重抓 → 整屏 + 落点 mark）。
- **新增 `tools/x11_selftest.py`**（已知真值验收，**ALL PASS**，exit 0）：自起 surface（1280×800）→ `look → mark → coord → act`。断言：① 原图 1280×800、渲染图幅 800×500（render `max_dim=800` 降采样）；② coord 像素 = 真值 (726,458)；③ zoom 子窗（0.2×0.2 → 256×160）内 mark 0.5,0.5 的 coord 仍回 (726,458)（缩放链 @原图 不变）；④ `act` device=(726,458)、pointer==device、返回 landing FIG + 整屏；⑤ zenity 窗口 1→0。
- **纠正**：`image_size` = **渲染后**图幅（受 render `max_dim=800` 降采样），非原图尺寸；原图尺寸看 text 里的 `（W×H）`。坐标换算不受降采样影响（`@原图` 归一）。
- **README** 已记 `x11.sh`（含 `zenity`）与 `x11_selftest.py`。**未 commit**（`domain.py` + tools 新增/改动）。

### Slice 2（依目标 §0.0 定，待 YZ 知悉）

> §0.0：一台自用电脑、图形面与 `term`/`fs` 并列的能力、能操作 + 有反馈的闭环；服务端只 mechanical、唯一智能在 agent 侧、图不转文字。X11 最小闭环（看/指/放大/点/确认）已成 → 目标导出下一刀 = **换平台验证同一闭环可跨平台，并逼出通用兜底**。

- **范围**：Android 后端打通同一 `look/zoom/mark/coord/act` 闭环 + 修 **#61 坐标链**（模型看到的那张图与 act 作用坐标系绑定，见 `design-vision-computer-fusion.md` §1）+ 传输/兜底（自算分块 diff 替代每帧 PNG 编码传输，见 `design-vision-scripting.md` 传输修正清单）。
- **验收（三平台共用判据，X11 已跑通的可直接复用形状）**：地面真值对照——capture 对已知元素 / `mark-coord-act` 往返（tap 后 pointer/落地与 coord 吻合）/ 屏幕变化确认。
- **不做**：接进真正 `computer` 工具（v2）、settle / change_hint、非 tap 动作、push / 采样。
- **环境（#65 实测，就绪）**：Windows 就绪（assist/zhengyp 可 ssh，daemon `127.0.0.1:9911` 在听）。Android 就绪（USB 已开 wifi adb，`adb -s 192.168.1.175:5555` 在线；assist 已装/进程在跑/InjectService 已启用；服务 `8901` 在听；MAR-TL00，Android 10/SDK29，1080×2312@480）。事实在 `tools/env.sh`（`SL_ANDROID_*`、`adb_dev`、`SL_WIN_*`）。`tools/android.sh` helper 未建。
- **后续范围（YZ 2026-09-26 明示）**：Android 之后**还需完成 Windows 侧相关工作**（Slice 3：换后端 + DXGI 采集，见 `design-vision-scripting.md` 传输修正清单）。连续范围 = Android → Windows。
- **不等待原则（YZ 2026-09-26 明示）**：任一环境阻塞（设备掉线/通道断），**直接切另一个环境继续，不等**；Android ↔ Windows 互为回退。
- **交接**：#66 随客户端退出被回收；已重交接 **#67**（handoff-screen-65.md 已更新为环境就绪版 + 首句）。

### Slice 2 结果（2026-09-26，#67，Android；自测 ALL PASS）

- **新增 `tools/android.sh`**：机械 Android 后端（adb）——`capture` 走 `exec-out screencap -p`（唯一 blobs/ 路径）、`tap X Y` 走 app 的 **InjectService**（`am broadcast -n com.screenlab.assist/.CmdReceiver --es op tap --ef x/y`，即 `dispatchGesture`，设备像素）、`foreground`（mResumedActivity）、`ui-bounds TEXT`（uiautomator 真值）、`consent-auto`（dev 关同意，未用上）。**免同意、无人值守**。CmdReceiver 带 `android.permission.DUMP`，adb shell 可达。
- **`imgctx.py` 加 `--backend {x11,android}`**（env `SL_SCREEN_BACKEND`）；`look`/`act` 走所选后端。
- **#61 坐标链修法（核心）**：`act` 由 `FIG.orig_w/orig_h`（**模型看到的那一帧的像素尺寸**）算设备坐标，不再另查 `x11.sh geometry`。即"作用在模型看到的那张图上"，平台无关。
- **新增 `tools/android_selftest.py`**（真值验收，**exit 0**）：home 屏 `uiautomator` 得 Chrome dock 图标中心 (338,2125) → `look`（原图 1080×2312）→ `mark`/`coord` 像素吻合 → `see` 0.15 子窗 `mark 0.5,0.5` coord 仍回真值（未 clamp）→ `act` 落点=真值、`screen`=[1080,2312]、落点 FIG、帧哈希变化 → Chrome 变前台。**换 Chrome 图标而非屏幕中心**是因为 dock 在屏底、0.2 子窗会 clamp；0.15 保证不 clamp。
- **#61 根因实测**：不是映射算错——(0.125,0.599)→设备 (135,1385) 正落在"支付宝"格内；Chrome 在 dock 却在 0.26,0.77 估算。错在模型按渲染图目测归一坐标；现由 `coord` 回读精确坐标再 `act`。
- **传输/兜底（通用分块 diff）**：新增产品机械层 `cogos/screenlab/service/change.py`（`fingerprint` x8 降采样 hash + `diff_bbox` 分块 bbox），单测 `tests/screenlab/test_change.py` 5 passed；薄 CLI `tools/screendiff.py`；接入 Android 验收（home 两帧 `same`；act 前后帧 `changed` 且 bbox 含落点）。平台无关兜底（无原生 damage 时）。
- **Android 侧 raw 传输实测结论**：`screencap`（raw RGBA，10MB）经 adb 取一帧 **15.0s**，`screencap -p`（PNG，1.6MB）**4.9s** → 在本链路"去 PNG 编码改传 raw"**不划算**。真正的传输修正需 app 内 MediaProjection raw + 协议改造（`backends_android.py:78` / `CaptureService.grabPng` 每帧 PNG 编码），属设计稿"待 YZ 定"，未动。
- **回归**：`x11_selftest.py` 在 imgctx 改动后重跑 **ALL PASS**。
- **未 commit**：`tools/android.sh`、`tools/android_selftest.py`、`tools/screendiff.py`、`tools/imgctx.py`、`tools/README.md`、`cogos/screenlab/service/change.py`、`cogos/tests/screenlab/test_change.py`；另有 #64/#65 遗留。

### Slice 3 结果（2026-09-26，#68，Windows；自测 ALL PASS）

- **环境纠正（以实测为准）**：`handoff-screen-67.md` 的"daemon 没在跑"**已过期**——实测 daemon PID 8368 于 assist 交互式 **session 7** 监听 `9911/9912`（`qwinsta` 不在 ssh PATH，用 `Get-Process ... SessionId`）。已停旧 daemon + tray 并重启，载入新码。
- **产品 DXGI 采集后端（核心，未 commit）**：`cogos/screenlab/service/backends_win.py` 新增 `DxcamCapture`（`dxcam` = 真 DXGI Desktop Duplication / `IDXGIOutput5.DuplicateOutput1`；只发整屏抓取、用 dxcam 的 per-region 缓存应对静态桌面"无新帧"，裁剪/缩放在 Python 侧）+ `pick_capture()`（默认 dxcam，`BackendError` 回退 GDI `PillowCaptureWin`；`SCREENLAB_CAPTURE=dxcam|gdi` 强制）。`platform_backends.pick` win32 分支改走 `win.pick_capture()`。**dxcam 必须懒 import**：Session 0 里 `import dxcam` 就会因 DXGI 无桌面枚举失败（实测 COMError `0x887A0022`）。
- **落地验证**：`windows.sh info` / 62c probe 确认 auto pick=`dxcam`、act=`sendinput`；daemon 重启日志 `capture_backend=dxcam`。62c 交互式 probe（`probe_backend_dxcam.py`）用产品 backend 抓帧：整屏 1920×1280（DPI 物理）、region(0,0,200,100)→200×100、max_dim=320→320×213，与 GDI 同帧 3 点像素 `delta=0`。
- **新增 `tools/windows.sh`**：机械 Windows 后端（Linux 侧驱动），**跑产品 backend**（DXGI 采集 + SendInput），在 assist 交互式会话内逐操作执行——经 admin ssh + 62c Task-Scheduler harness（`launch_probe.ps1` 跑 `win_io.py`，读 `win_io.req` 写 `win_io.result`）。子命令 `deploy/capture/tap/click/info/active-window/target-start/target-state/cat/rm`。无 daemon、无同意。
- **新增 `tools/windows_selftest.py`**（真值验收，**RESULT: ALL PASS**，exit 0）：`target_tk.py` 在交互式会话起 **topmost、per-monitor-DPI-aware** 的 Tk 靶（400×300 @+700+400），自报物理 rect+中心（真值 (900,550)，屏 1920×1280）→ `imgctx --backend win` `look`(FIG:1000, 1920×1280) → `mark`/`coord` 像素=真值 → `see` 0.3 子窗 `mark 0.5,0.5` coord 仍回真值 → `act` device=(900,550)、screen=[1920,1280]、landing FIG、pointer 回声 → 帧哈希变化、`screendiff` bbox 含落点 → **靶 marker READY→HIT、click=(900,550)**（注入点击真落到靶上）。
- **`imgctx.py` 加 `--backend win`**（`_BACKEND_SH` 表；tap 动词 win/android=tap、x11=click）。
- **未 commit**：`cogos/screenlab/service/backends_win.py`、`platform_backends.py`、`tools/windows.sh`、`tools/windows_selftest.py`、`tools/win/62c/{win_io.py,target_tk.py,probe_backend_dxcam.py}`、`tools/imgctx.py`、`tools/README.md`、本文件；另有 Slice 0–2 遗留。安装副本已 push（运行中 daemon 用新码），但仓库未 commit。

