# 设计结论｜图形面生命周期 + 命令层（从目标推）· 2026-09-23

> **判据（通用规则）**：一切从**目标**推 + **易用性**。不存在"YZ 定"或"AI 定"的人为分界——定的标准就是目标与通用规则。
> **演变**：本文件前一版把这些记为"待 YZ 裁决"，**错**。目标 `spec-screen-1.md` §0.0 已写死，多数可推；只有 §0.0 自列的**未闭合项**才需讨论。
> **目标（唯一约束）**见 `spec-screen-1.md` §0.0（2026-09-21 拉通）。

## 一、推的依据（目标要点）

> **一句话**：让每个 agent 拥有一台"自己能用"的电脑（账户级），图形界面是这台电脑的一项能力——agent 能操作它、能得到反馈；这块界面平时不抢屏，需要时能和真人共屏。

已定的相关要点：

- 每 agent 一账户；图形与 `term`/`fs` 并列，是电脑的一项**能力面**。
- 核心能力 = 操作 + 反馈（闭环）；**"像真人、不被检测"属目标，不是可选**。
- **§0.0 已定**：图形面按 **"开一个程序"** 模型、**按需开/关**；**要延续的状态放磁盘**（浏览器 profile 按账户固定复用），**不靠会话常驻**。
- 由目标导出：任一时刻**至多一个有效操作者**（单控制者 + `yield`）。
- 授权 = 给账户（`design-screen-system.md` D1/D2）；面之间是**授权边界，不是身份边界**（谁持有授权谁就用，人/agent 无差别）。

## 二、确定要改的（为什么 / 怎么改）

| # | 改什么 | 为什么（目标依据） | 怎么改 |
|---|---|---|---|
| C1 | `close` 语义 = 程序退出（丢窗口），**不常驻** | §0.0「开一个程序」按需开/关 | `close` 停**整套面**（Xvfb+WM+daemon）；文档措辞对齐 |
| C2 | **不做** detach/保活；桌面不因后台任务常驻 | §0.0「不靠会话常驻，延续状态放磁盘」 | 取消"退出后留桌面"设想；延续只走磁盘（profile/blobs） |
| C3 | `close --destroy` **保留 resolution** | §0.0「要延续的状态放磁盘」 | resolution 从 `session.env` 挪到随 destroy 保留的状态文件（如 `~/.local/share/screenlab/session.json`），`open` 优先读它 |
| C4 | **删协议 op `paste`** | 图形面是电脑能力；剪贴板是桌面语义，**跨后端不成立** | `ACT_OPS` 去 `paste`；剪贴板做成命令（见 C6）；`spec-screen-1` §1 同步 |
| C5 | 面生命周期 = **open 即拉起 / 最后 close 即关** | §0.0「按需开/关」 | 通道**引用计数 + grace**；拆机器靠 systemd（`screenlab.socket` socket activation → 起 target；`StopWhenUnneeded`），不靠客户端显式 close |
| C6 | 应用/窗口层 = **命令**，不进协议 | 判据"换后端还成立吗"：WM/DE 语义不成立 | 新命令面 `surface run\|windows\|focus\|close\|clip`；自己读 `session.env`、**不暴露 `:N`**；`run` detach、**禁用 `exec`/`&`**（坑由命令层填） |
| C7 | 协议 / 命令分层判据 | —— | 设备级、**跨后端成立** → 协议（`capture`/`act`/`open`/`close`/`blob`）；WM/DE/OS 特定 → **命令** |
| C8 | **面 = 能力，授权 = 门票** | 目标：授权=给账户；人/agent 无差别 | 命令按**面**分组（管理 / 观察 / 使用），`--help` 标出所属面与所需授权 |
| C9 | agent 日常命令**单开一套** `surface` | 易用性（`--help` 只列 agent 世界、词汇里没有 display） | 运维留 `screenlab`（管理面）；`view` 归观察面；`add-agent` **不预起面** |
| C10 | **agent 机定性 = 无人无屏 (headless)**（讨论②结论） | §0.0 未闭合② 定：不显示到物理屏、不需人常驻 | Goal 1 不做物理屏/seat/共屏；"不抢屏"无需实现；**看=`view`（只读）；要操作→给账户**；管理员不设防护；"真人机+介入"归 **Goal 2** |
| C11 | **收回机制为零，收回靠惯例**（改密 / 删 key / 销毁临时账号） | D1：不提供令牌/凭证层；授权=给账户 | 写进"给账户的卫生建议"（授前临时密码、授后换新密、一授权一专用 key、禁 `ForwardAgent`、收完删行、不信任走临时账号），**不写代码** |
| C12 | 反检测口径 = **与真人 VBox 齐平**（不引真 GPU） | §0.0「像真人、不被检测」属目标；真人 VBox 同为 VM + 软件渲染，通常被正常接受 | 对手 = 普通站点 + 通用风控的**静态指纹面**；补 Xvfb 特有缺口；**不追定向检测** |
| B1 | `open --restart` 应**复用原 display** | 非目标所限；换号是分配器竞态/bug | `--restart` 读 `session.env` 的 display 复用，不重新分配 |
| B2 | `tool_loop_e2e` 硬编码 `1920x1080` | 测试 bug | 期望从 capture 的 `w/h` 推 |

（C1–C12 = 设计/命令层；B1–B2 = bug 修复。）

## 三、未闭合（§0.0 自列）

**已定（讨论②，2026-09-23）：agent 机 = 无人无屏 (headless)。**
- agent 的电脑不显示到物理屏，不需要人在面前。**按需求分两条路**：**只看（哪怕常坐看）→ `view`（只读）**；**要操作 → 才把账户交给真人**（**信任**前提）。触发点是**操作需求**，不是"看得多久"。人与 agent **身份对等**，不存在"agent 必须交账户"。
- 管理员可**后台收回**（root 事实，agent 拒绝不了）；agent **可以选择"拒绝"**（表达层），但不构成防护。
- "真人电脑 + agent 介入" 属 **Goal 2**，不在本线。
- **推导**：Goal 1 不做物理屏/seat/共屏，"不抢屏"无需实现（没有屏）；§0.0 关系 **3b = `view`（只看）+ 给账户（要操作时）** 即全部，**3a 归 Goal 2**。没有"controller 版 viewer"这条中间路——`view` 天生只读，"能操作"就等于"拿到账户"。

**已定（讨论③，2026-09-23）：授权粒度 = 操作一档（账户）；观看侧保留 tailnet。**
- **操作侧只有一档 = 账户**。不做会话级——一账户一面，账户与会话不可分，该选项为空；不做窗口级——更细必须引入令牌/凭证层（D1 已删），且属非信任场景（D2 不做）。
- **收回机制为零**，靠惯例（改密 / 删 key / 销毁临时账号），见 C11。
- **观看侧**：沿用 viewer 只读 + tailnet（设备级、粗、不按人收回）。§9「观察者凭据」（一次性、可即刻收回的链接）是唯一更细候选，**Goal 1 不实现，留 §9 遗留**。
- 信任不足 → **拒绝共享**；要限定共享范围 / 不暴露身份 → 临时账号，用完销毁。

**仍未闭合：**
1. ~~关系 3 的 a / b~~ → **定向：都要；3b = Goal 1（viewer/给账户），3a = Goal 2**。
2. ~~物理屏与常驻真人~~ → **已定 ↑**。
3. ~~授权**粒度**~~ → **已定 ↑**（操作一档 = 账户；观看侧 tailnet，「观察者凭据」留 §9）。
4. ~~反检测强度~~ → **已定（讨论④，2026-09-23）**：口径 = **与真人 VBox 齐平**（见 C12）。

### 遗留（不阻塞 Goal 1）

- **L1 行为保真**（鼠标轨迹 / 打字节奏）——归 **agent 操作层**。
  - **机制前置**：现模型一次 `act` **消耗 generation**（`screenlab/service/daemon.py:256/263` 的 `st.void()`）→ 连续位移发不出；要落地需先改机制（允许多次 act 共享一次 capture，或新增 `move`/`drag` 带路径 + 时序）。`pointer` 用 `clicks=0` 已支持纯移动（`backends.py:328`），本身不是障碍。
  - 检测现实：页面能读 `mousemove`/`pointermove` 流与时间戳，但**看不到设备身份**（XTEST 不可见）；属**弱信号**，普通站点基本不看，风控只作多项之一。
- **已实测（2026-09-23，靶机 `surface-centos-9`，alice `:10` 1920x1080 · Chrome）**：
  - **WebGL = 无**（`getContext("webgl")` 返回 null）。原因 = Chrome 新版不再默认回退 SwiftShader，**无 GPU 的机器都如此**（含无 3D 的真人 VBox）——非 Xvfb 独有，与 C12 口径一致；若某站强需 WebGL，需显式 `--enable-unsafe-swiftshader`（属方案/痕迹取舍，待议）。
  - **`screen.width/height = 1920x1080`，`availWidth/Height = 1920x1080`，`devicePixelRatio = 1`**。
  - **字体**：系统 135 个字体；`DejaVu Sans` / `Liberation Sans` / `Arial`（映射）在；CJK 靠 **`Droid Sans Fallback`**，无 Noto CJK。

## 执行中发现（#36–#38「真用」验证轮）

**方法**（#37 起）：不用仓库自写 e2e 当验收（自证）；**从 §0.0 出发、按"怎么用"列清单**，以 agent 身份**只用文档公开入口**（`screenlab` / `surface` / `view`）真用，用 `import -window root` 抓屏做**地面真值**对照。详见 `checkpoint/tmp-screen-usage-verify.md`（验证结束、与 YZ 讨论后删）。

**A. 纯 bug（已修 + 靶机验证）**
- **F1** 面未起时 `surface` 永久挂死 → 存活预检（`/tmp/.X11-unix/XN`）+ xdotool `timeout`；实测 123ms 返回 `surface_not_running` rc=1（原 435s+）。
- **F1b** `alloc_display` 撞 sshd X11 转发 TCP → `display_in_use()` 加查 **TCP 6000+N**。
- **F2** 空剪贴板当错误 + 写路径 `xclip` 泄漏 stdio 致经 ssh 永不返回 → 空态 rc=0 无 stderr；写重定向 stdio + `-loops 1`（2s 返回）。
- 清理：`session.env` 前导空格；`--no-sandbox` 全仓残留（F5 已自决默认禁用，理由：与"像真人、不被检测"冲突，黄条是可见痕迹）。

**B. 从目标推出的机制修复（已落）**
- **F6 / F9 / F7 同源 = GUI 进程生命周期完全没被管理**。由 §0.0「能操作且有反馈 + 可控可观测」推出：
  - `surface run` → `systemd-run --user --slice=screenlab-apps.slice`（cgroup 归组、即时返回）；
  - `surface close <窗口>` → `windowactivate --sync` + `xdotool key alt+F4`（真 **WM_DELETE**，非 `windowclose`=XDestroyWindow）；
  - `screenlab close`（温和默认）→ 全体 WM_DELETE + 有界等待（`SCREENLAB_CLOSE_GRACE`，默认 10s）+ 查 slice **cgroup 实际进程**（不用 `is-active`）→ 空则停 target；非空则**保会话**报 `close_blocked` + `survivors` rc=1；`--force` 才停 slice（SIGTERM→SIGKILL）再停 target。
  - **F9 判据**：不能用 profile `exit_type`（Chrome 148 运行时也写 Crashed）→ 看下次启动是否出 `Restore pages?` 气泡（抓屏）；温和收敛后**未再出现**。
- **F8** `surface run` 无条件 `started` 且丢弃子进程输出 → 改 **`Type=exec` + 输出落 `STATE/run.log` + 报 `{unit,pid,alive,exit_code}`**；实测 `sleep 300`=alive:true、`/nonexistent`=failed rc1、`true`/`false`=exit_code 0/1，F6 `close` 回归仍正确。
- **F4** `capture` 无 `tree`、`act element` 未实现，与 spec §1 宣称不符 → 因 §0.0 已把「a11y 与像素如何分工」列为**方案层**，故**改 spec 承认 Goal 1 仅像素**（`spec-screen-1.md` §0.0 加清账、§1/§7 标 tree/element 候选未实现），a11y 记候选；同步契约 `session-create.md`。

**C. 本轮补验（#38）**
- **关系 3b 跨机 view** ✅：异机 acer(100.79.86.84) 经 tailnet 取 target(100.100.137.78):8800；`/status`=observer+read_only+`input:false`、`/frame`=1600x900 且与 `import -window root` **逐像素相同**（diff bbox=None）、`POST /act`=405、`GET /`=200。
- **C4 重启不自启** ✅（静态判断，靶机有 dracut 前科故不真重启）：4 个 unit 全 `disabled`、无 `.socket` 单元、无 `~/.config/autostart`、无 `.wants` 符号链接；只由 `screenlab open` 显式起。

**D. 副发现 / 观察（不阻塞，记候选）**
- **装配面缺口**：`install-machine` **不管宿主防火墙** → `view` 端口默认被 firewalld `public` 区拒（`design-screen-system.md` §7 已列为手工步骤）；"装配一步到位"可作候选改进。
- **O1** 窗口不铺满面、`capture` 只给整屏 bounds（与 F4 同源）· **O2** 全新 profile 首跑气泡遮挡 · **O3** `tz=Asia/Shanghai` 与 `langs=en-US` 不一致（按"与真人 VBox 齐平"口径**不判偏离**）· **`/status` `focus.window_id` 在窗口关闭后陈旧**（openbox 未重置死窗口焦点，非缓存）· **F7** 随优雅收敛**未再复现**。

## 四、流程教训

- 先读目标（§0.0 及其指向的裁决）再判"谁定"；把**目标已定**的问题推给人 = 错。
- 判据永远是**目标 + 通用规则（易用性等）**；只有 §0.0 未闭合项才值得讨论。

## 五、其它未定清单（待清账）

§0.0 的"仍未闭合"已全部闭合（①–④）。别处有几张**旧账本**——**不是讨论项**（本次验证一条都没触发、也不影响目标落地，只值一次清账 / 文档更新）：

- `spec-screen-1.md` §10「未决」11 条：多数已实质定（2 自建电脑、3 薄语义层、4 Linux 先行、7 代码落 cogos 子包 `screenlab/`），需逐条标"已定 / 仍开 / 作废"。
- `spec-screen-1.md` §7「持久形态（Phase 2）未定案」：本轮 `install-machine` / `add-agent` + 账户内 socket 已基本实现；其中"现 socket/TCP 无认证"已由**账户级 socket 权限**解决，该更新。
- `design-screen-system.md` §9：真 GPU（已折入 C12）、Wayland 真人桌面（Goal 2）、**观察者凭据**（仍开）。
- 流程：打 tag、`cogos/docs/design-agent-tools.md` §16 回写。

**结论：本轮不需要再开讨论。** 剩下只有"做（C1–C12 / B1–B2）、量（三项形态小项）、搁（L1）"；其余是清账与流程。

## 锚

- 目标：`spec-screen-1.md` §0.0（唯一约束）
- 体系：`design-screen-system.md`
- 契约：`../cogos/screenlab/install/session-create.md`
- 代码：`../cogos/screenlab/`（proto / service / viewer / install）、`../cogos/cogos/agent/impl/graphics.py`
- 演示：`/tmp/kilo/demo/act1-*.png`
