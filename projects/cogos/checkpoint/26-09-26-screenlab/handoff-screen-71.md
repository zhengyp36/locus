# handoff｜#69 → #71（续做：修 bug + 使用角度复验）

> 规则 / 环境不在本文件——先读 `screenlab-rules.md`。
> 本文件由 **#69 审查后**写给 **#71**（YZ 指派让 #71 接手收尾）。#71 完成后**就地更新本文件**（写结果 + 给后继的首句），无需另起新编号。
> 交接原因：#69 审查发现 X11 只是 selftest "ALL PASS"、未按**使用角度**验收；且产品有一个已确认的 bug。

---

## 复制这段作为续做 #71 的第一句

```
接 #71（续，YZ 指派 #69 审查后来收尾）。本会话两件事，做完更新 ../checkpoint/handoff-screen-71.md + ../checkpoint/screenlab-work.md：
① 修产品 bug：screenlab/install/session-start.sh 的 create 分支未接线默认值——alloc_display() 定义在 :227 但无调用者、DISP/RES/XAUTH 默认空串(:39-41)、create 直接拿空值跑 rm -f "$XAUTH"; touch "$XAUTH"; xauth add "$DISP"(:388-391)；且 STATE/session.json(:402 写) 从未回读（C3 记忆分辨率）半接线。影响：全新 bare create（不带 --display/--xauth/--resolution）会失败；重开因 session.env 回填(:239-252) 正常、x11.sh start 总显式传参(:50) 故从未触发。修法：create 分支补 [ -n "$XAUTH" ] || XAUTH="$CFG/xauthority"、[ -n "$DISP" ] || DISP="$(alloc_display)"、[ -n "$RES" ] || RES=<回读 STATE/session.json，缺省 ${SCREENLAB_RESOLUTION:-1280x800}>。
② 使用角度验收（不看 selftest "ALL PASS"）：修完后用 bare `screenlab open <account>`（不带任何 flag，指到该账户的 surface 的 create 命令）成功起面；再以 agent 身份用公开 CLI `imgctx --backend x11` 真实跑 look→mark→coord→act，用**独立真值**核对（xdotool getwindowgeometry 窗几何 / `x11.sh zenity` 计数 1→0 / `x11.sh pointer` 与 device 一致），并实际 read 帧图确认。Android/Windows 也做同样使用角度复验（不只 selftest）。
先读（纯文本）：1. ../checkpoint/screenlab-rules.md；2. ../checkpoint/screenlab-work.md §状态；3. ../checkpoint/handoff-screen-71.md（本文件，含 #69 审查结论与 bug 分析）。
纪律：10min 闹钟；ctx ≥150K 交接；裁决由目标（spec-screen-1.md §0.0）；阻塞→飞书通知 YZ 后做不阻塞的；允许 commit/push（不 tag），提交前跑测试。
⚠️ 文档是二手描述，动手前以代码/实测为准。
```

---

## #69 审查结论（素材）

### 已完成（#70/#71，已 commit+push 到 origin/feat/screenlab-p2）
- `c9d6ad6` 客户端整合（imgctx look/act 走产品 screen/1）· `fa49a89` act settle + drift 只报告 · `14937da` X11 走产品 surface。
- 我复跑：`tests/screenlab + tests/image_ctx` **71 passed**；`imgctx_selftest.py` ALL PASS；工作树干净、与 origin 同步、无 keys/blobs 入库。

### X11 使用角度验收（#69 现场做，独立真值）— 通过
- 靶机曾**内核 panic 卡死**（VBoxManage 报 running 但 tailscale offline、console 卡在 systemd-shutdown Call Trace）→ `VBoxManage controlvm centos9 reset` 后恢复。
- 以 agent 身份：`imgctx --backend x11 look` → read 帧图看到 zenity "screenlab slice1 click target" → 目测 OK 按钮 `mark 0.567,0.572` → `coord` 回 **px (726,458)** → `act` device=(726,458)、pointer=(726,458)、`stale=false`、返回 landing FIG。
- **独立真值**：xdotool 窗几何 `508,360 266x120`；点击后 `x11.sh zenity` **1→0**；post 帧黑（对话框消失）。
- 结论：X11 走产品 screen/1 是**真通**（但这条是用 selftest 之外的手动真值补验的）。

### 已确认的 bug（#71 曾发现未修，实际可修）
- 文件：`cogos/screenlab/install/session-start.sh`。
- 根因：create 分支（`:348` 起）没有默认值接线；`alloc_display()`（`:227`）/`display_in_use()`（`:211`）定义但 `alloc_display` 无调用者；`DISP`/`RES`/`XAUTH` 初值空串（`:39-41`）；create 直接用空值（`:388-391`）。`STATE/session.json`（`:402` 写）无任何回读 → C3 "记忆分辨率" 半接线。
- 触发：**全新 bare create**（不带 `--display/--xauth/--resolution`）→ `rm -f ""` / `touch ""` / `xauth add ""` 失败。重开（`session.env` 存在）因 `:239-252` 回填而正常；`x11.sh start` 因 `:50` 总显式传参故从未触发。
- 修法：create 分支使用前补 `XAUTH` 默认、`DISP="$(alloc_display)"`、`RES` 回读 `STATE/session.json`（缺省 `${SCREENLAB_RESOLUTION:-1280x800}`）。
- **#71 为何没修**：其 session 记录显示它 grep/diff 过 `alloc_display`（"compare installed copy"），但把它当作**出本会话任务范围**（任务是 X11 tools 切换，非 installer），只记 "待 YZ 定"。**它没有给出按 §0.0 的目标推导**；从目标看，"每个 agent 能起自己的 surface" 是基本能力，这属**应自决并修的 bug**，不该只挂起——这是流程上的漏（发现≠裁决）。

## #71 收尾时要做的

1. 修上述 bug（create 分支默认值 + session.json 回读）。
2. 使用角度验收：bare `screenlab open` 起面成功 + imgctx 真跑闭环 + 独立真值；Android/Windows 同样复验。
3. 更新 `screenlab-work.md` §状态；**就地更新本文件**（追加结果 + 给后继的首句）。
4. commit/push（不 tag），提交前跑测试。

## #71 结果（收尾完成 · 2026-09-26）

### ① 产品 bug 已修并落产品仓
- `cogos/screenlab/install/session-start.sh` create 分支补默认值（提交 `d89abd7`，已 push `origin/feat/screenlab-p2`）：
  - `[ -n "$XAUTH" ] || XAUTH="$CFG/xauthority"`、`[ -n "$DISP" ] || DISP="$(alloc_display)"`、
    `RES` 回读 `STATE/session.json`（缺省 `${SCREENLAB_RESOLUTION:-1280x800}`）。
  - 同步 `session-create.md` open-sequence 默认分辨率 → `1280x800` + 说明回读。
- 部署：`screenlab/tools/deploy.sh`（rsync → `/opt/screenlab`，install-machine 重装）。
- **实测 bare create 成功**：`screenlab close zhengyp --destroy`（保留 `session.json={"resolution":"1280x800"}`）后，
  `screenlab open zhengyp`（**不带任何 flag**）→ `{"event":"listening","display":":10","xauth":"/home/zhengyp/.config/screenlab/xauthority","resolution":"1280x800"}`。

### ② 使用角度验收（以 agent 身份、公开 CLI、独立真值；非 selftest）
- **X11**：`imgctx --backend x11 look`（read 帧目测 zenity OK 按钮）→ `mark 0.566,0.572` → `coord` px `(724,458)`
  → `act` device `(724,458)`、`stale=false`、landing FIG。独立真值：`xdotool getwindowgeometry` 窗 `508,360 266x120`；
  目标侧 `xdotool getmouselocation` `X=724 Y=458`==device；`x11.sh zenity` **1→0**；read post 帧确认对话框消失、落点红叉可见。
- **Android**：`imgctx --backend android`（assist app screen/1 `tcp:…:8901` + `keys/android_agent.key`）`look` → read home 帧 →
  目测 Chrome dock 图标 mark → `coord` px `(338,2125)`（==`android.sh ui-bounds Chrome` 真值中心）→ `act` device `(338,2125)`；
  独立真值 `android.sh foreground` 变 `com.android.chrome/ChromeTabbedActivity`。read post 帧受已知 MediaProjection 滞后影响仍显 home（已记录 caveat），前台真值 + 落点一致为准。
- **Windows**：`windows.sh deploy` + `it-daemon start`（19911 consent auto）+ `target-start`（Tk 靶真值 `center=(900,550)`）→
  `imgctx --backend win` `look`（read 帧见靶窗）→ mark → `coord` px `(900,550)` → `act` device `(900,550)`；
  独立真值 `target-state` READY → **HIT `click=(900,550)`**。（注意 Tk 靶 30s 超时，须在起靶后尽快 act。）
- **三平台全通**。验证：`tests/screenlab + tests/image_ctx` **71 passed**。

### 环境遗留
- 靶机 zhengyp 账户的 X11 产品面仍开在 `:10`（1280x800，socket `unix:/run/user/1000/screenlab.sock`）——即 agent 自己的 surface；要收可 `screenlab close zhengyp`。
- Windows 测试 daemon 已 `it-daemon stop`；真 daemon（9911, consent=event）未动。

## 给后继的第一句话

```text
接 #71（已收尾）。① 产品 bug（session-start.sh create 默认值）已修并 push（cogos d89abd7, origin/feat/screenlab-p2）；② 三平台使用角度验收（独立真值，非 selftest）全通，结果见 ../checkpoint/handoff-screen-71.md「#71 结果」。本会话无待办，等 YZ 给下一步方向；未决候选见 spec-screen-1.md §0.0「仍未闭合」与 screenlab-work.md。
纪律：10min 闹钟；ctx ≥150K 交接；裁决由目标（spec-screen-1.md §0.0）；阻塞→飞书通知 YZ 后做不阻塞的；允许 commit/push（不 tag），提交前跑测试。
⚠️ 文档是二手描述，动手前以代码/实测为准。
```

## 锚

- 规则：`../checkpoint/screenlab-rules.md`；工作单：`../checkpoint/screenlab-work.md`；目标：`../checkpoint/spec-screen-1.md` §0.0
- 代码：`cogos/screenlab/install/session-start.sh`、`cogos/screenlab/tools/{imgctx.py,x11.sh,*_selftest.py,env.sh}`
- 环境：CentOS `100.100.137.78`（account `zhengyp` uid 1000，socket `unix:/run/user/1000/screenlab.sock`，display `:10`，1280x800）；Windows `100.112.50.115`（assist/zhengyp）；Android `192.168.1.175:5555`
