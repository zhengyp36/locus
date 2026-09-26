# 验证记录 1｜按"怎么使用"重验图形面 · 2026-09-23~24

> **性质**：**正式证据底稿**（原 `tmp-screen-usage-verify.md` 提升而来，2026-09-24 收尾）。
> **结论落点**：F1–F9 / O1–O5 的**最终处置与清账**在 `issue-screen-surface-lifecycle.md`「执行中发现」；本文件是**逐条证据与过程**（A–H 清单、F1–F9 现场/根因、讨论、修复轮）。
> **规则 + 环境**：`screenlab-rules.md`（稳定）。**目标**：`spec-screen-1.md` §0.0（唯一约束）。
> **状态（2026-09-24 收尾）**：F1/F1b/F2/F5/F6/F7/F8/F9/F4 + `session.env` 空格**全部落定并靶机验证**（代码提交见 `handoff-screen-39.md`）；O1–O5 为观察/搁置；**3b 真人浏览器侧 + 关系 2 已于 #43 现场验收（见末节）**。

## 为什么这么做

- #34 宣布"全绿"= 仓库自己的 harness 自证（`roles_e2e` / `tool_loop_e2e` 都是我们写的）。
- #35 一转"真的去用"（Act 1 演示）就出问题：display 重分配、destroy 丢 resolution、e2e 硬编码分辨率、装配脆弱。
- 所以本轮**不用仓库 e2e 当验收**，改成：**从目标 §0.0 出发，按"怎么使用"列清单**——
  以 agent 身份、只用文档公开入口，把电脑真的用起来；对抗性找**新问题**。

## 判据

- 一切从**目标**推（`spec-screen-1.md` §0.0）+ 易用性；不从代码、不从"谁定的"推。
- 能从目标推出的裁决：**自行决定并记入本文件"决定"节**，不问人。
- 唯一例外：打 tag / 提交（本轮不涉及）。

## 验证清单（从 §0.0 推，按使用场景）

### A. agent 从零拿到电脑
- A1 `add-agent` 后**不预起面**（无 Xvfb、target inactive）。
- A2 `surface` 在 PATH；`--help` 标出所属面与所需授权。
- A3 账户侧 `~/.config/screenlab/session.env` 就绪且**归属正确**（root 建 home 目录 bug 的回归）。

### B. 自操作闭环（agent 用电脑 = 目标核心）
- B1 `surface run` 一个**真实网站**（非常规 `about:blank`）。
- B2 `surface windows` / `focus`。
- B3 `capture` 反馈与页面实际一致。
- B4 `act` 点击 / 打字有效（闭环）。
- B5 **连续操作**（多次 `act`）——issue L1 已写"一次 act 消耗 generation"，真用第一步就会撞。
- B6 `surface clip` 读 / 写（`paste` 协议已删，命令是否顶得上）。

### C. 生命周期 = "开一个程序"
- C1 `close` → 整套面退（Xvfb+WM+daemon 全退、窗口丢）。
- C2 再 `open` → **复用同一 display**。
- C3 `close --destroy` → resolution 保留、display 换、账户数据 / profile 在。
- C4 机器重启 / linger **不自启**（unit 不 enable）。

### D. 状态延续放磁盘
- D1 关掉再开，chrome profile（登录态 / cookie / 历史）还在。

### E. 真人侧
- E1 `view` 只读：能看不能动（`POST /act` 405）。
- E2 收回：删账号后干净。

### F. 多账户隔离
- F1 两个 agent 互不可见对方的面 / runtime。

### G. 易用性（C8/C9 的目标）
- G1 **只拿 `--help`** 能不能学会用（agent 世界词汇里没有 display）。

### H. 痕迹（机械量 + 按目标判）
- H1 复测 WebGL / screen / DPR / 字体。
- H2 按"与真人 VBox 齐平"判（见决定 D-1）。

## 决定（按目标自决，记录在此）

- **D-1：不加 `--enable-unsafe-swiftshader`。**
  依据：目标口径"反检测 = 与真人 VBox 齐平"（`issue-screen-surface-lifecycle.md` C12）。实测**无 3D 的真人 VBox 同样 `webgl=null`**（Chrome 新版不再默认回退 SwiftShader，非 Xvfb 特有）。加上它反而造出与基线不同的指纹（带 SwiftShader 迹象的 WebGL）。故**保持不加以齐平**。

## 靶机清场前现状（先记后退）

2026-09-23 23:49 采集（`surface-centos-9` / 100.100.137.78，up 5:05）：
- `/opt/screenlab` 存在（内容 `screenlab`）。
- 账户：`zhengyp`(1000) + 6 个 agent 账户 `alice/john/Lyli/alice1/john1/Lyli1`(1001–1006)，**全部 `lingering=yes`**。
- **6 个账户各有 Xvfb 在跑**（john 1329 / alice1 7430 / john1 7577 / Lyli1 7723 / Lyli 11649 / alice 21626），`alice` 还有一整棵 chrome 进程树（22115…）。
- → 这是 **#35 演示遗留态**（每个账户都预起了面），正是 C1/C2/C9 要消除的形态。

## 执行日志（时间序）

（执行时填：命令、结果、新发现、证据路径）

## 新发现的问题（已并入 `issue-screen-surface-lifecycle.md`「执行中发现」）

### F1（严重 · 目标相关）面未起时 `surface` 永久挂死；display 分配与 sshd X11 转发端口冲突

- **现场**：`screenlab add-agent sva --resolution 1600x900`（装配成功，面未起，`session.env` 记 `:10`）后，
  执行 `surface windows` → **挂死 435s+**，`xdotool getactivewindow` 处于 `poll_schedule_timeout`，
  `surface` 在 `pipe_read` 等它；只能 `pkill` 终止（terminal 8 退出码 143）。
- **根因**：`:10` 对应 TCP 端口 **6010 被遗留的 sshd X11 转发监听占用**
  （`ss -ltnp`：`127.0.0.1:6010 LISTEN ss hd-session pid 6832`、`6011` pid 7069，均来自 `zhengyp@pts/0/1` 的 `ssh -X` 转发）。
  libX11 对 `:N` 先试 unix socket `/tmp/.X11-unix/XN`（不存在），**再退回 TCP `localhost:6000+N`** →
  连上 sshd 的空壳监听、永不完成 X 握手 → 阻塞。
- **对照实验**：`DISPLAY=:99`（无监听）→ `rc=1`，`Failed creating new xdo instance`（快速失败）；
  `DISPLAY=:10` → `rc=124`（`timeout` 到点）；`xdotool search` 同样 `124`。
- **两个缺陷**：
  1. `surface`（`run|windows|focus|close|clip`）**无超时、无"面是否活着"预检** → 违背目标"能操作且有反馈"：
     agent 会卡死而不是拿到明确错误。
  2. `session-start.sh` `alloc_display()` 只查 `/tmp/.X11-unix/XN` 与 `/tmp/.XN-lock`，
     **不查 TCP `6000+N`** → 可能选中被 sshd X11 转发占用的 display 号（且 Xvfb 默认不 listen TCP，冲突不被启动期发现）。
- **触发条件**：机器上存在 `ssh -X` 会话（很自然）且面未起。
- **目标裁决（待办，本轮未动码）**：`surface` 必须"快速失败并说明原因"（如无面/未 open），
  `alloc_display()` 应避开 TCP 占用号；对 agent 侧调用应加超时。**属代码修复**，验证阶段先记录。
- **旁证（非阻塞）**：`session.env` 第 4 行有前导空格 `  SCREENLAB_DESKTOP=openbox`
  （`session-start.sh` heredoc 缩进遗留），sourcing 可用，属 cosmetic。

### F4（中 · spec 与实现差距）`capture` 不返回 `tree`，`act element` 未落地

- spec §1 定 `capture -> {..., tree?:[{id, role, name, bounds, clickable}]}`，`act op ∈ {pointer|element|key|type|scroll}`。
- 实测：`capture` 返回 `capture_backend: "pillow"`、`image`（**无 `tree`**）。
- 全仓 grep `tree` / `clickable` / `a11y` / `atspi`：**除 channel 的 `role` 外零实现** → a11y grounding 整条没做。
- 目标影响：§0.0 要"能操作且有反馈"，坐标 + 像素**仍能闭环**（`pointer{x,y}` + `image`），
  但 spec 承诺的 `element:{id}` 宾语类型形同虚设 → 要么补实现，要么把 spec/契约改成"仅像素"。
  属**方案层差距**（§0.0 未把 a11y 列为约束），但 spec 宣称与实现不符，须清账。

### F5（中 · 痕迹）`--no-sandbox` 产生可见指纹条；默认是否必须待验

- 现场：用 `surface run google-chrome --no-sandbox …` 起的页面，截图里直接出现
  **"You are using an unsupported command-line flag: --no-sandbox. Stability and security will suffer."** 黄条。
- 说明：这条 flag 是**我在验证时自己加的**（非其默认）；但它一旦存在，就同时是
  ①人可见的痕迹 ②可被页面/风控侧察觉的自动化迹象 → 与目标"像真人、不被检测"直接冲突。
- **待验**：不带 `--no-sandbox` 时 chrome 能否在 Xvfb + 账户下正常启动；若能，
  则装配/文档**必须默认不带**；若不能（需 root 或 userns），则要给出替代（如改 `chrome-sandbox` 权限/`--user-data-dir`）
  而不是让 agent 天天带条黄杠。

### O2（观察 · 非缺陷）全新 profile 的 chrome 首次运行气泡遮挡内容

- cap2（不带 `--no-sandbox` 重启后）见图：出现 `Sign in to Chrome?`、`Can't update Chrome`、
  `New Chrome available` 等气泡/弹层，**遮挡页面**且会进入 capture。
- 影响：agent 截图里混入 UI 噪声；如要点击被遮挡内容需先关掉气泡。
- 非目标缺陷（真人全新 profile 也会看到），但**"预热 profile"**（登录一次、关掉这些）应纳入装配建议。

### O1（观察 · 非缺陷）chrome 默认窗口不铺满面

- 截图：chrome 窗口约占 1600x900 左侧 ~1064px，右侧大块黑（root window）。
- `capture` 全屏时 `window:{center:{0.5,0.5},size:{1,1}}` = 整屏，**不含单窗口 bounds**；
  配合 **F4（无 tree）**，agent 拿到归一化坐标后要自己猜窗口范围。属"反馈粒度"问题，与 F4 同源。

### F2（轻 · 可用性）`surface clip` 空剪贴板时吐裸 `xclip` 报错、rc=1

- 现场：`surface clip`（无参数，剪贴板为空）→ `xclip: Error: There is no owner for the CLIPBOARD selection`，`rc=1`。
- 问题：① 未按其它子命令的 **JSON 错误**风格（`{"error":...}`）；② "空剪贴板"对 agent 是**正常状态**而非错误，
  却以 stderr + 非零码表达，agent 会误判为失败。
- 目标相关：闭环反馈应"可判读"，正常态与错误态要分开。
- **修复轮补充（#37 续）**：`surface clip <text>`（写）派生的 `xclip` selection-owner **继承调用方 stdout** → 经 ssh 调用（agent 常规路径）时 **ssh 永不返回**（原 terminal 挂死即此因）。已修：写剪贴板时把 xclip/xsel 的 stdio 重定向到 /dev/null（xclip 另加 `-loops 1`）；验证经 ssh 2s 返回。

## B 组结果（自操作 · 面已起，2026-09-23 23:58）

- `screenlab open sva` → `{"event":"listening","display":":10","resolution":"1600x900"}`，**1.85s**；
  `Xvfb`(25782) + `openbox`(25783) 起、`/tmp/.X11-unix/X10` 出现 → **通过**。
- 面起后 `surface windows` → `{"windows":[]}` `rc=0`（**快速**）→ 反证 **F1 特指"面未起 + 该 display 的 TCP 端口被占"**。
- `surface clip`（空）→ 见 **F2**。
- `surface run google-chrome …` → `{"event":"started"}` `rc=0`；`windows` 列出
  `{"id":"4194307","name":"Example Domain - Google Chrome","active":true}`；chrome 进程树在（26061+）→ **`run` 通过**。
- `capture`（`--socket`，调试前端）→ `ok:true`、`image 1600x900`、`blob_sha == frame_hash`、`saved_to` 落盘 → **取帧 + blob 通路通过**。
- 地面真值对照：`import -window root` 同尺寸 1600x900 `rc=0`，与 service capture 内容一致 → **反馈真实，非自证**。
- `surface focus "Example Domain"` → `{"event":"focused","id":"4194307"}` `rc=0`；**通过**。
- `surface close "Example Domain"` → `{"event":"closed"}` `rc=0`，随后 `windows` = `[]`；**通过**。
- 窗口几何：`xdotool getwindowgeometry` = **1050x880 @ (10,10)** → 见 **O1**（不铺满满屏）。

### C 组结果（生命周期 = "开一个程序"，2026-09-24 00:01）

- `screenlab close sva`（= stop）→ `stopped screenlab-session.target (sva)` `rc=0`、**0.212s**；
  target `inactive`；**Xvfb/openbox 消失、`/tmp/.X11-unix/X10` 消失** → **窗口丢 ✓（C1 的窗口部分）**。
- `session.env`（23:58）与 `session.json` **保留** → stop 不删状态 ✓。
- `screenlab open sva` → `listening`，**复用 `:10` + 1600x900**，2.3s → **B1/C2 通过**。
- ⚠️ `close` 后**残留 chrome 孤儿进程**（`27740 chrome_crashpad`、`27742 chrome_crashpad`、`27773 chrome`）→ **F6**。

### F6（中 · 目标相关）`close` 只停 systemd 面，`surface run` 起的 GUI 进程成孤儿

- 现场：`close` 后 Xvfb/openbox 全退、X 消失，但 `surface run` 用 `setsid -f` 拉起的 chrome
  **不在 unit 里**，故不被 stop 收走：`close` 后仍留 2 个 `chrome_crashpad` + 1 个 `chrome`。
- 目标影响：§0.0 "开一个程序 / 按需开 / 关"——**窗口丢了但进程没退**：
  ① 反复 open/close 会**累积孤儿进程**；② 孤儿可能持有 **chrome profile 单例锁**，
  影响下一次 `surface run`（待验：本组随后重跑 `run` 观察）。
- 待验/待决：`close` 是否应连带清理该账户的 GUI 子进程（cgroup 归并 / pkill 会话内进程）。

### H 组结果（痕迹机械量测，2026-09-24 00:02）

方法：把探针页 `file:///home/sva/probe.html` 用 `surface run` 打开，JS 把结果写进 `document.title`，
再 `xdotool getwindowname` 读回——**不注入 CDP、不改启动参数**，避免量测本身造痕迹。

```
{"webgl":false,"webgl2":false,"screen":[1600,900,1600,900],"dpr":1,"webdriver":false,
 "cores":2,"mem":2,"vendor":"Google Inc.","platform":"Linux x86_64","tz":"Asia/Shanghai",
 "langs":"en-US,en","outer":[1050,880],"inner":[1042,789]}
```

- `webgl/webgl2 = false`、`dpr = 1`、`screen 1600x900` → 与上一轮（1920x1080）结论一致，只随面分辨率变。
- `navigator.webdriver = false`（注入走 XTEST，非 CDP）→ 无经典自动化标志。
- `fc-list | wc -l` = **135** → 与上一轮一致。
- `google-chrome --version` = **148.0.7778.96**。
- `outer/inner = 1050x880 / 1042x789` → 佐证 **O1**（窗口不铺满 1600x900 面）。

### O3（观察 · 弱 · 按口径不判偏离）tz 与语言不一致

- `tz=Asia/Shanghai` 而 `langs=en-US,en`：对中文站点是轻微不一致信号。
- 按 C12 口径"与真人 VBox 齐平"：全新 CentOS VM 同样如此 → **不算偏离**；
  但装配**未刻意设置 locale/tz**，如目标站点为中文，可考虑随账户对齐（属方案，非缺陷）。
### 待验（已回填）

`--destroy` 后 resolution 保留 + display 变更 + profile 保留；stop 后重跑 `surface run` 是否受孤儿/锁影响。
（结果：见 C 组与 F6 节——resolution 保留 ✓、无锁问题。）

### F5 结论（已验）

- **不带 `--no-sandbox`**：`surface run google-chrome --no-first-run --no-default-browser-check https://example.com`
  → 窗口 `6291459` 出现（`xdotool search --sync` 命中），chrome 以 `sva` 非 root 正常起（user namespace 沙箱可用）。
- 用户 profile `/home/sva/.config/google-chrome/{Default,WidevineCdm,Last Version,Variations}` 正常生成。
- **裁决（按目标）**：默认**不应带** `--no-sandbox`（可见黄条 + 自动化迹象，违背"像真人不被检测"）；
  装配/文档/示例里**不得**出现该 flag。

### B 组·闭环（act）结果（2026-09-24 00:00）

- `capture --out cap2.png` → `ok:true`，`frame_hash` 与 cap 不同（重起了 chrome，符合预期）。
- `act key --keys ctrl+l --snapshot auto` → `{"ok":true,"op":"key","acted":{"key":"ctrl+l"}}`
- `act type --text "https://duckduckgo.com/?q=screenlab"` → `{"ok":true,"acted":{"text_length":35}}`
- `act key --keys Return` → `{"ok":true}`
- 随后 `xdotool search --sync --name DuckDuckGo` 命中 `6291459`；`surface windows`
  → **`duckduckgo.com - Google Chrome`** → **操作 → 反馈闭环真实成立（含真实网站导航）**。
- 说明：三次 `act` 是**三次独立 CLI 连接**（每次自带一次 capture 拿 generation），故未触及 L1 的
  "单连接连续 act 消耗 generation" 机制问题——L1 仍属"搁"。

## 问题总表（供讨论）· 2026-09-24 00:06

**已通过（清单）**：A 装配/不预起/归属 · B 闭环+取帧真值+act+clip 往返 · C close/open/destroy ·
D profile 落盘 · E view 只读 + remove-agent · 多账户隔离 · H 痕迹量测（与上轮一致）。

**高（直接违背目标"能操作且有反馈"）**
| # | 问题 | 证据 |
|---|---|---|
| F1 | 面未起时 `surface` **永久挂死**；无超时、无"面是否活着"预检 | `xdotool` 挂 435s；`:10` rc=124 vs `:99` rc=1 |
| F1b | `alloc_display` 只查 unix/lock，**不查 TCP 6000+N** → 与 sshd X11 转发撞号 | sshd 占 6010/6011；Xvfb 不 listen TCP 故启动无感 |
| F6 | `close` 不收敛 `surface run` 起的 GUI 子进程（孤儿） | close 后仍留 crashpad+chrome，数秒后自行退 |
| F7 | **残留实例**使后续 `surface run google-chrome` 不可靠（窗口消失/黑屏/无错） | 干净态复现：KILL-all 后窗口持续；有残留时窗口消失 |

**中**
| # | 问题 | 证据 |
|---|---|---|
| F8 | `run` 无条件报 `started`，且**丢弃子进程输出** → 失败零线索 | `run /nonexistent-cmd-xyz` → `started` rc=0 |
| F4 | `capture` 不返回 `tree`；`act element` 未实现（**spec §1 与实现不符**） | 全仓无 a11y 实现；capture 只有 pillow/image |
| F9 | 粗暴关闭在 profile 留 `didn't shut down correctly` + `Restore pages?` | task.png 可见 |
| F5 | （已定）默认**禁用** `--no-sandbox`：否则可见黄条 | 无该 flag 也能起 → 裁决：禁用 |
| F2 | `surface clip` 空剪贴板吐裸 xclip 错、rc=1（正常态当错误） | `xclip: Error: There is no owner…` |

**低 / 观察**
O1 窗口不铺满面 & capture 只给整屏 bounds（与 F4 同源）· O2 全新 profile 气泡遮挡 ·
O3 tz(Asia/Shanghai) 与 langs(en-US) 不一致（按"齐平"口径不判偏离）· `/status` focus 陈旧 ·
`session.env` 第 4 行前导空格。

**处置（已落，2026-09-24）**：F1/F1b 修法（超时+存活预检+避开 TCP 号）、F6/F7/F9 修法（`close` 优雅收敛 GUI 进程 / `run` 记录并暴露子进程状态）、F4 改 spec 承认仅像素、F8 失败可判读——**全部落码 + 靶机验证**，逐条结果见下方「修复轮」「实现」两节与 `issue-screen-surface-lifecycle.md`「执行中发现」。

## D 组结果（状态延续，2026-09-24 00:02）

- 优雅关闭：`surface close PROBE` → `{"event":"closed","id":"6291459"}` `rc=0`；随后
  `Default/History` = **163840B**，`grep -a -o` 同时命中 **`probe`** 与 **`example`**
  → **浏览状态确实落盘并在 profile 里保留** → **D1 通过**（目录 + 内容 persistence，跨 close/open/destroy）。
- 注：`surface close` 关窗后 chrome 进程数秒内未全退（crashpad/zygote 残留），随后自行收束 → 与 **F6** 同源。

## E 组结果（观察面，2026-09-24 00:02）

- `screenlab view --host 127.0.0.1 --port 8800`（以 `sva` 身份）：`GET /frame` → **HTTP 200**（4267B PNG）。
- `GET /status` → `{"read_only":true,"role":"observer","bits":{"capture":true,"input":false},
  "input_holder":null,"geometry":{"w":1600,"h":900},"display":":10"}` → **只读确证**。
- `POST /act` → **405** → **E1 通过**。
- 小瑕疵：`/status` 的 `focus.window_id` 在窗口已关闭后仍报 `6291459`（陈旧值）。

## 隔离组结果（多账户，2026-09-24 00:02）

- `add-agent svb --resolution 1024x768` → `assembled` display `:11`；`open svb` → `listening :11`；
  `ls /tmp/.X11-unix/` = **X0 X10 X11**（两面并存，互不挤占）。
- 关键旁证：Xvfb `:11` 在 **sshd 占着 TCP 6011** 时仍正常启动、且 6011 归属仍是 sshd
  → **证实 Xvfb 默认 `-nolisten tcp`**；故 F1 的 display 冲突**只发生在客户端缺 unix socket 时**，
  不影响 Xvfb 启动。
- 双向越权（runtime 隔离）：`svb` 读 `/run/user/1001` → `Permission denied`；
  `sva` 读 `/run/user/1002` → `Permission denied` ✓
- `surface windows`（作 `svb`）= `[]`（只见自己的面）✓ → **隔离通过**。

## 端到端任务（真实使用，2026-09-24 00:03）

- 第一次尝试（`run … duckduckgo.com/?q=screenlab+agent`）：`run` 报 `started`、
  `xdotool search --sync --name "[Dd]uck"` 命中，但**随后 `surface windows` = `[]`、
  capture/import 均**整幅全黑** → 窗口消失。
- **定因（复现）**：先 `pkill` 干净（`pgrep` = 0）再 `run` → 窗口 t2–t6 **持续存在**；
  即上次失败源于**上一个 chrome 实例残留**（见 F6/F7）。
- **干净版 capstone 通过**：`act ctrl+l → type https://example.com → Return` 三步 `ok:true`；
  `xdotool search --sync --name "Example Domain"` 命中；`capture --wait-stable 2` → `ok:true`、新 `frame_hash`；
  `task.png` **有真实内容**（Example Domain 渲染）→ **端到端"操作 + 反馈"闭环成立**。

### F9 / O5（中 · 痕迹）粗暴关闭在 profile 留下"非正常关闭"状态

- `task.png` 里出现 **`Restore pages? Chrome didn't shut down correctly.`** 弹层 ——
  源于前面 `pkill`/X 消失式关闭（F6/F7 同源）。
- 目标影响：① 人可见的异常态；② "上次未正常关闭"是**弱指纹**，真人日常 profile 少有；
  ③ 每次都会弹 `Restore pages?` 遮挡内容（叠加 O2）。
- 方向（待议）：`close` 应先**优雅收敛** GUI 进程（发 WM_DELETE / SIGTERM 再退 X），
  而非直接让 X 消失。

### F7（高 · F6 的实务后果）残留实例使后续 `surface run google-chrome` 不可靠

- 机制：`surface run` 用 `setsid -f` 起 chrome，不管理其生命周期；若上一个 chrome 实例
  （哪怕无窗口）仍在，新进程经 **profile singleton** 把 URL 交给旧实例后**自行退出**，
  旧实例随后收束 → **窗口消失、`surface windows` 为空、capture 全黑**。
- 目标影响：违背"能操作且有反馈"——agent 看到 `run` 报 `started`，却拿不到任何窗口/画面，
  且**无错误**。属 F6 的直接后果（`close` 不收敛 GUI 子进程）。

### F8（中 · 可观测性）`surface run` 丢弃子进程全部输出

- `run` 行：`setsid -f "$@" </dev/null >/dev/null 2>&1`，且**无条件**报
  `{"event":"started"}`。启动失败/崩溃/依赖缺失**零线索**（本次即无从解释 F7 的首现）。
- 目标影响：闭环反馈不止"画面"，也含"命令结果"；失败态必须可判读。

## G 组（易用性：只拿 `--help`）分析

依据已抓到的 `screenlab --help` / `surface --help` 原文：

- `screenlab --help`：头注讲清**三面**（管理 / 会话 / 观察），并**点明 use 面是另一个入口 `surface`**；
  Options 段列出各子命令与参数 → **管理/会话面可自学**。
- `surface --help`：列全 5 个子命令，明说 `Face: use`、`Authorization: the account`、
  **`display numbers … never exposed here`** → **使用面可自学**。
- **结论：help 本身够用**。可用性风险不在 help，而在行为/词汇一致性：
  1. **两个 `close` 撞名**：`surface close <id|name>` 关**窗口**，`screenlab close [--destroy]` 关**整面** →
     词汇层易混（文档有区分，但名字一样）。
  2. 面未起时 `surface` 的错误不可判读（**F1** 直接挂死；只有缺 `session.env` 才报 JSON），
     help 也没写"需先 `screenlab open`"。
  3. `run` 无条件 `started`、失败不可判读（**F8**）。
  4. `add-agent` 输出**明文密码**，未标注为秘密（收回靠惯例，见 C11）。

## A 组结果（装配面，2026-09-23 23:50）

- L1 从零装配 **通过**：清场（只剩 zhengyp/gdm）→ `install-machine --prefix /opt/screenlab` rc=0，
  `/usr/local/bin|/usr/bin` 各得 `screenlab`+`surface`，`/opt/screenlab/screenlab` 树完整。
- A1 `add-agent sva`（uid 1001）→ 事件 `assembled`（display `:10`），
  `screenlab-session.target` = **inactive + disabled**，`ps` 无 Xvfb/openbox/screenlab → **不预起面，通过**。
- A2 `surface --help` 输出头注完整（标 Face: use / Authorization: the account / display 不暴露）→ **通过**。
- A3 归属：`/home/sva/.config`、`.local`、`.local/share/screenlab` 全部 `sva sva` → **root 建目录 bug 回归通过**。
- &#9888; A 组最后一条 `surface windows` 撞上 **F1**（挂死），非装配问题。
- 附：`add-agent` 返回明文密码 `m2ne1Xo2rhyambVP`（临时口令，供 ssh 登录；收完应改密——见 C11）。

## 修复轮（#37 续，2026-09-24）—「原因清楚且纯 bug」批

按 handoff 步骤 1 修复并靶机验证（`surface-centos-9`，rsync + `install-machine` 重新部署）：

- **F1 surface 挂死**：加"面是否活着"预检（查 `/tmp/.X11-unix/XN`）+ xdotool 统一 `timeout` 兜底。验证：面关后 `surface windows` **123ms** 返回 `{"error":"surface_not_running",...}` rc=1（原挂死 435s+）。
- **F1b alloc_display 撞 TCP 号**：新增 `display_in_use()`，除 unix socket / lock 外**查 TCP 6000+N**。验证：ssh -X 占 6010/6011 时 `add-agent` 跳过 :10/:11（选 :13/:12）。
- **F2 空剪贴板**：读空剪贴板改 rc=0、无 stderr；并修**写路径 xclip 泄漏 stdio**（经 ssh 挂住，见 F2 节补充）。验证：空读 rc=0/无错、set/get 往返正常、写经 ssh **2s** 返回。
- **session.env 缩进**：删前导空格（`cat -A` 确认行首干净）。
- **`--no-sandbox` 残留**：全仓 grep 无残留，无需清。
- 另：`surface --help` 改为**不依赖 session.env / 面**（G1：help 可独立自查）。

代码改动**未提交**（等 YZ）。

## 讨论（#37 续）— 第一条 F6/F9（close 与 GUI 进程）· 2026-09-24

> 背景：F6/F7/F9 **同源** = `surface run` 起的 GUI 进程**完全没被管理**。本节目标是定 `close` 该干什么。

### 1. 从目标（§0.0）推出（不是选择）
- 生命周期 = "开一个程序"：按需开/关；要延续的状态放磁盘、**不靠会话常驻**。
- 操作像真人、不被检测；命令要有可判读反馈。
- 推出 `close` 语义 = **桌面注销**：先请应用**优雅退出**（保存状态），会话再结束。要**保活就别关面**；非图形进程归 `terminal`/user service，图形面不背。
- 现状为何错：`close` 只停 systemd target，`surface run`（`setsid`）起的进程不在 unit → 孤儿（F6）；X 消失时应用被"断线" → Chrome 记非正常关闭（F9）；残留实例让下次 `run` 不可靠（F7）。

### 2. 机制：归组（已靶机验证可行）
- `surface run` 改走 `systemd-run --user --unit=… --slice=screenlab-apps.slice --collect --setenv=DISPLAY/XAUTHORITY …`：经 systemd 接管、**即时返回**（不再有 `setsid` 进程挂住 ssh）、进程可被 slice 统一 stop。
- 验证：`stop screenlab-apps.slice` 秒级收走 `sleep`；cgroup 路径 `/sys/fs/cgroup/user.slice/user-1001.slice/user@1001.service/screenlab.slice/screenlab-apps.slice`。
- `close` 顺序：先对所有窗口发 **WM_DELETE**（优雅）→ 有界等待 → 再 `stop` slice（systemd 按 SIGTERM→SIGKILL 收残余）→ 最后停 target / Xvfb。

### 3. 讨论确定的技术结论
- **用 cgroup、不记 pid**：进程自退/被关都**自动脱组**；stop 时现场枚举成员 → **无 pid 复用、无时间间隙、无误杀**（记 pid 才有这些坑）。应用即使 `setsid` 脱离会话、或 crashpad 被 init 收养，仍在同一 cgroup。
- SIGTERM 对整个 cgroup **并行**发（不逐个等）；超时后 SIGKILL 同样一次性对剩余全部发。
- **不做弹窗 / 否决**：Linux 的"应用阻止关机"只在完整桌面会话（GNOME/KDE + logind inhibitor）有，且只是**有界延迟**；我们 headless 面无此物。不做理由：① 这里的"用户"是 agent，弹框没人点 → 命令不可判读；② 否决会被卡死应用滥用 → close 永不完成；③ 把决定权从 agent 挪给被操作、可能已卡的程序。可借鉴的只是"有界延迟"。
- **优雅关窗原语现在是坏的**：`surface close <窗口>` 用 `xdotool windowclose` = **XDestroyWindow**（销毁窗口、不结束应用）→ 实测 chrome 仍 12 进程、profile 记 Crashed。须修成真 WM_DELETE（`wmctrl -c` 加依赖，或无依赖"激活窗口 + XTEST 关闭键"，与 `act` 同路径）。
- **F9 判据**：不能用 profile `exit_type`（Chrome 148 运行时也写 Crashed，alt+F4 / SIGTERM 全读 Crashed）→ 改用**下次启动是否出现 `Restore pages?` 气泡**（抓屏）。

### 4. 语义选择：两个正交原语 + 中间选择
- `surface close <窗口>` = **优雅关单窗**（可被拒 / 可没退）。
- `screenlab close` = **结束会话**。
- 关键：agent 要像真人关机对话框那样有**中间选择**（等 / 强制 / 取消），而非"一锤子不可反悔" → 强制应作为**显式选项**（`--force`）。**撤回**之前"温和会成为常态负担"的说法（不成立）。
- 对照：系统层 logout（logind）其实是**自动强制 + 有界**、不可取消；可取消的是桌面"关机对话框"。所以"温和默认"对应关机对话框层，"强制默认"对应 logout 层——**是语义选择，不是复杂度选择**。
- 复杂度判断（已验）：强制与温和**共用归组前提**；温和的增量仅"查 cgroup 是否空 + 报 survivors"，**很小** → "因复杂而取强制"的理由不成立。

### 5. 待定（唯一）
- `screenlab close` 默认取 **温和**（只发 WM_DELETE + 有界等；有存活则**会话不动**、返回/事件报 `{closed:false, survivors:[…]}`；强制走 `--force`），还是 **自动强制**（有界后自动收干净、返回 `forced` 列表）？
- 倾向：**温和默认 + 显式 `--force`**（保留中间选择；合理且增量小）。
- 未决参数（定了默认再谈）：宽限时长、档位。

> 第二条 F8（`surface run` 可观测性）**尚未开始**。

## 实现（#37 续，2026-09-24）— F6/F9/F7：close 与 GUI 进程

决策：`screenlab close` 默认**温和** + 显式 `--force`（YZ 定）。已落码并靶机验证（rsync + `install-machine`）：

- `surface run` → `systemd-run --user --collect --slice=screenlab-apps.slice --unit=screenlab-app-<pid>-<rnd>`（组进 cgroup、即时返回；失败报 `{event:failed}` 而非假 `started`，成功报 `{event:started,unit}`）。
- `surface close <窗口>` → `windowactivate --sync` + `xdotool key alt+F4`（WM 发**真 WM_DELETE**，与 `act` 同路径）；实测 chrome 13→1、窗口消失；事件 `close_requested`。
- `screenlab close`（温和）：对所有窗口发 WM_DELETE → 有界等待（`SCREENLAB_CLOSE_GRACE`，默认 10s）→ 查 slice **cgroup 实际进程**（不用 `is-active`：cgroup 空后 slice 仍会短暂报 active）→ 空则停 target 报 `{closed,forced:false}`；非空则**不动会话**、报 `{close_blocked,closed:false,survivors:["<pid>:<comm>"]}` rc=1。
- `screenlab close --force`：polite ask 后 `stop screenlab-apps.slice`（SIGTERM→SIGKILL）**再**停 target，报 `{closed,forced:true}`。
- 契约 `session-create.md`、`surface --help`、`screenlab` usage 已更新。

验证（靶机）：
- 温和关闭：run chrome → `surface close` 窗口 → 静候 → `screenlab close` = `{closed,forced:false}` rc=0、target inactive、**无真实 chrome/crashpad 残留**（此前 `pgrep -c chrome`=1 是 pgrep 匹配到自身）。
- 阻塞：`surface run sleep 300` → `screenlab close` = `{close_blocked,survivors:["50624:sleep"]}` rc=1、target 仍 active；`--force` → target/slice 全 inactive。
- **F9**：两轮 open/run/close 后重开 chrome 抓屏 `bubble.png` → **无 `Restore pages?`**（仅无关的 update 气泡）→ 优雅关闭成立。
- **F7**：循环 run 均正常起窗，不再出现"残留致窗口消失"。


## 收尾轮（#39，2026-09-24）— 跨机 view / C4 / F8-A

从目标推导依次执行；靶机 `surface-centos-9`（rsync + `install-machine` 重新部署）。

### ① 关系 3b 跨机 view ✅（此前只验 loopback）
- 面：`screenlab open sva` → `listening :10 1600x900`；`screenlab view --host 100.100.137.78 --port 8800`（账户内）。
- 异机 **acer(100.79.86.84)** 经 tailnet 取 target(100.100.137.78):8800：
  - `GET /status` → `{"ok":true,"alive":true,"read_only":true,"role":"observer","bits":{"capture":true,"input":false},"display":":10","geometry":{"w":1600,"h":900}}`
  - `GET /frame` → **HTTP 200** PNG 1600x900；与靶机 `import -window root`（在 `:10`）**逐像素相同**（`ImageChops.difference` bbox=`None`，各通道 max diff=0）
  - `POST /act` → **405**；`GET /` → **200**
- 面上内容随真实程序变化：`surface run zenity --info --text=CROSS-VIEW-PROOF-2026` → frame 由 4267B 变 13189B、内容不同 → 证通路 live 且指向正确 display。
- 副发现：`install-machine` **不放行宿主 firewalld** → 8800 默认被 `public` 区拒，需手工 `firewall-cmd --add-port=8800/tcp`（`design-screen-system.md` §7 已列为手工步骤）。

### ② C4 重启不自启 ✅（静态判断；靶机有 dracut 前科，不真重启）
- `systemctl --user is-enabled`：`screenlab-session.target` / `screenlab-xvfb.service` / `screenlab-desktop.service` / `screenlab.service` 全 **disabled**。
- 无 `*.socket` 单元；无 `~/.config/autostart`、无 `*.wants` 符号链接；`screenlab-session.target` = `WantedBy=default.target` 但**未 enable** → 开机/登录不自启，只由 `screenlab open` 显式起。

### ③ F8-A 落码 + 验证 ✅（`screenlab/install/surface`）
- `cmd_run` 改：`systemd-run --property=Type=exec`（坏命令在 launch 即失败）+ `StandardOutput/StandardError=append:$HOME/.local/share/screenlab/run.log`（每次 launch 打 `--- <unit> <ISO time> <cmd> ---`）+ 短暂探测后报 `{event,unit,pid,alive,exit_code,log,command}`。
- 实测（作 `sva`）：
  - `run sleep 300` → `{"event":"started","unit":...,"pid":57902,"alive":true,...}` rc=0
  - `run /nonexistent-cmd-xyz` → `{"event":"failed","detail":"Failed to find executable … No such file or directory",...}` rc=1
  - `run true` → `started,alive:false,exit_code:0`；`run false` → `started,alive:false,exit_code:1`
  - `run sh -c 'echo HELLO-RUNLOG; sleep 300'` → `run.log` 含 `HELLO-RUNLOG`
- **F6 回归**：`screenlab close sva` → `{"event":"close_blocked","closed":false,"survivors":["57902:sleep","57950:sleep"]}` rc=1（会话保留）；`--force` → `{"event":"closed","forced":true}`，target `inactive`、无 Xvfb。
- `surface --help` 头注同步（alive/exit_code/run.log）。
- `pytest tests/screenlab` → **15 passed**。

### ④ F4 改 spec ✅（清账）
- `spec-screen-1.md`：§0.0「不属于目标」加清账（a11y 属方案层 → Goal 1 只承诺像素、`tree`/`element` 系候选、未落不算欠账）；§1 wire `mode`/`tree`/`element` 标候选未实现；§7「a11y 未验证」→「未实现且不作要求」。
- 契约 `session-create.md` 同步 `surface run` 新语义。

## 真人验收轮（#43，2026-09-24）— 关系 3b + 关系 2 现场

> 背景：此前 Goal 1 的"验收"全是机械通路（单次 `curl /frame` 得 PNG 即算过）。本轮 YZ 在电脑旁，补**真人环节**：以 agent 身份、只用公开入口真用；地面真值 = 靶机 `import -window root` **＋ YZ 肉眼**。

### 结果（Goal 1 三关系）

- **自活 ✅**：靶机 `sva`（uid 1001）无头面 `:10`（1600x900）。`surface run google-chrome https://example.com` → `capture → act(ctrl+l/type/Return) → capture`，`frame_hash` 逐次变化；`example.com` / `cn.bing.com` 真实渲染；service capture 与 `import -window root` 内容一致（人工核对）。**不抢屏**：面在无头 Xvfb，不点亮/不独占物理输出。
- **关系 3b（人 viewer）✅**：`screenlab view --port 8800`（sva 内，绑 tailnet `100.100.137.78`；firewalld 放行 8800）。YZ 用浏览器 `http://100.100.137.78:8800/` **亲见 live 画面**，并看到随 agent 操作的**实时变化**（zenity `SCREENLAB-GOAL1-HUMAN-ACCEPTANCE-2026` 弹出、页面从 bing 切到 example.com）。`POST /act → 405 read_only`；`GET /frame` 与 service capture **md5 相同**。
- **关系 2（agent 间授权 = 给账户）✅**（现场）：
  - `screenlab add-agent svb`（uid 1003，面 `:11` 1024x768）+ `open`。
  - 隔离：svb 自己面 `windows=[]`；svb 读 `/run/user/1001` → `Permission denied`、连 `:10` → `No protocol specified`。
  - 授权：把 svb 公钥写入 `/home/sva/.ssh/authorized_keys` → svb `ssh sva@localhost` 后在 **sva 的面**上 `surface run zenity ...` 成功（起出 `GUEST-SVB-DROVE-SVA-FACE`）。
  - 单控制者：两条 controller 连接并发，c1(owner) `act` 占锁 → c2 `act` 被拒 `input_taken`（"held by sva-owner"）→ c1 `yield` → c2 `act` ok。
  - 收回：删 sva `authorized_keys` 中该公钥 → svb `ssh sva` 立即 `Permission denied`。（粒度=账户：粗、滞后、全量，合 `design-screen-system.md §4`。）

### 新发现的问题

#### F11（中 · 关系 3b 真人可看）viewer 首屏破图

- **现象**：YZ 浏览器打开 viewer，头部「已连接 / 只读」正常，但图区**破图**（`img` 一直空）。
- **根因**（`viewer/bridge.py` 两处叠加）：
  1. `ScreenBridge.frame()` 把客户端**显式传的空 `since`** 当成"未提供"，回退到 `self.last_hash` 去重 → 画面静止时只回 JSON（`changed:0`）、不回 PNG；
  2. handler 用 `parse_qs(parsed.query)`（默认 `keep_blank_values=False`）把 `?since=` 解析成 `{}` → `since=None`，进一步触发上述回退。
  `page.html` 只在收到 `image/png` 时设 `img.src` → 首屏永远拿不到图。
- **为何此前"通过"**：机械验收只做**单次** `curl /frame`（此时 `last_hash=None` → 全帧 PNG）；真人打开时 `last_hash` 已被前序请求推进，即暴露。
- **修**：`frame()` 尊重显式 `since`（仅 `None` 才回退 `last_hash`）；`parse_qs(..., keep_blank_values=True)`。
- **验证**：首帧 `X-Changed:1` + `image/png`（165313B）；同 hash 复取仍然 `changed:0`（去重未破）；viewer 帧 = service capture（md5 同）。
- **判据**：目标「人可 viewer 看」（`spec-screen-1.md §0.0` 关系 3b）。

#### F9 复现观察（未处置）

- 本次 `surface run google-chrome` **首次启动**即出现 `Restore pages? Chrome didn't shut down correctly.`（遗留 profile 处于非正常关闭态）。属 F9 类：人可见 + 弱指纹。是否复验「优雅 `close` → 重开无气泡」，待 YZ。

### 说明

- 本轮改动 = `screenlab/viewer/bridge.py`（F11，2 处）+ `screenlab/install/surface`（`--onlyvisible`，G2/F10，承接 #42 未提交）。
- 靶机遗留：账户 `svb`（面 `:11` 在跑）；sva `authorized_keys` 已清空。清理：`screenlab close svb --destroy` + `screenlab remove-agent svb`。
