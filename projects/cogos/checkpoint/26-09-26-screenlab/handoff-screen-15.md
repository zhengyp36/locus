# handoff｜交接：M2 图形路线实验（第二轮）· 2026-09-21 #15

> ⚠️ **已被 `handoff-screen-16.md` 接续**：新会话请从 #16 读起；本文件保留为细节（尤其第四节架构定案）。
> ❌ **作废 / 修正（2026-09-21 23:2x）**：**自持 / 自启整条线已撤** —— 本文件 §五 的 **A8**、§六 / §七 的 **linger / `systemd-run` 装配**全部失效（见 `handoff-screen-17.md` §十一·11.3）。**另：§4.1 首条"agent 自己没有用屏的需求"是错的**，正确口径以 `spec-screen-1.md` §0.0 为准：**反馈必须有（目标）；占屏是可选的输出方式（方案）**。
> **新会话读本文件即可开工。**
> **最重要的细节文件**：`screen-exp-log.md`（实验清单 + 逐条记录 + 脚本索引）；假设清单/计划：`screen-verify-1.md`；上一轮：`handoff-screen-14.md`；脚本：`screen-lab-verify/`。
> **注意**：上一轮的两个结论已在本轮被**推翻并修正**，见第三节；`screen-exp-log.md` 的 A4 段已改写。

## 一、一句话现状

M2（agent 自己的 headless 图形桌面）的**headless 路线已打通**：chrome 在**无 seat** 的 headless gnome-shell 里正常加载网页（缺的开关是 **`--password-store=basic`** + **`--ozone-platform=wayland`**，**不是 seat**）；**办法二（AT-SPI `Action`）的覆盖率已在自造页 + 真实站点（react.dev）实测**；**ScreenCast 取帧复核通过**。**架构已定案（第四节）。没写任何生产代码。**

## 二、本轮已证实（实测）

| 项 | 结果 |
|---|---|
| **headless 里 chrome 能上网** | ✅ tangyu 的 headless（无 logind 会话/无 seat）里，chrome 加 `--password-store=basic` 后正常加载页面（`requests: /`、`/favicon.ico`） |
| **根因** | chrome 启动时问 **Secret Service（gnome-keyring）**，密钥库锁着/不应答 → 所有 http(s) 请求一直 pending（本地文件正常、无报错、`curl` 同机正常）。已知症状：Arch 论坛 tid=312408 |
| **A4 覆盖率**（自造页 14 控件，headless，3 遍一致） | 交互类控件**全覆盖**：button/link/check/radio/submit、**`div role=button`**、**span onclick / canvas onclick（`clickAncestor`）**、**img（`click`）** 均能被 `doAction` 真正驱动 |
| **A4 值类控件** | text/textarea（entry）、range（slider）、select（combo box）在树里，但 `doAction` **不产生值变化**，需 `setText`/`setValue` |
| **方法学** | **a11y 树是渐进建立的**：连扫 3 遍一致（19 个 A4 节点 / chrome 全树 382）才算稳定；早扫会漏 |
| **A4 真实站点**（react.dev，React SPA） | ✅ 树 **1376 节点 / 227 个可动作节点**（push button 106、link 71、entry/slider/combo box 各 3…），浏览器 UI + 网页内容全覆盖 |
| **A4 懒开** | ❌ 不带 `--force-renderer-accessibility` 时树**只有 1 个 `frame` 节点**（连扫 3 遍）→ **flag 目前必需**，与 F1 指纹冲突 |
| **A1 复核 + A2** | ✅ `RecordMonitor` 出 **1920×1080** 帧；❌ 同一路流**单消费者独占**（并发第二路 rc=124 无帧），但"不新开显示/不改分辨率"成立 |
| 延续上轮 | E2/E3/E4/E5/A1/A6 见 `screen-exp-log.md`（X11 注入通、Wayland 注入未解、Wayland 坐标证伪…） |

## 三、两个被推翻的结论（务必先看，别重蹈）

1. ❌ **"chrome 必须有 seat"** → **错**。真因是密钥库不应答；`--password-store=basic` 即可，headless/无 seat 完全可行。alice（正常会话）能上网只是"keyring 恰好可用"，不是 seat 的功劳。
2. ❌ **"ARIA/自绘控件不在 a11y 树"** → **错**，是"树未建全就扫"的假象。等稳定后它们都在树里且可被驱动。

> 教训：**涉及 a11y 树的结论，必须先确认树已稳定**；单次扫描不足以下结论。

## 四、架构定案：两模式 + 单操作者（**YZ 定，2026-09-21**）

> 本节覆盖上一轮"抢屏/输出协调"的误导性表达，也覆盖一度写过的"agent 单消费者 + fan-out 给人看"。

### 4.1 出发点（纠正）
- ~~**agent 自己没有用屏的需求** → 给 agent 的电脑 / headless 桌面**默认不占屏**~~ ❌ **此条错，已作废**（见文件头修正）：**反馈必须有**；**占屏是方案层的输出方式**。下文凡以"agent 不用屏"为前提的推论，一律以 `spec-screen-1.md` §0.0 为准。
- 屏幕上要有人时，屏幕属于**真人那台机器**，不是 agent 的机器。
- A6：`card0` ACL ≈ 有申请 **DRM master** 的能力（理论上能抢输出）——与"不占屏"不冲突，只是说明"不占屏"是设计选择，不是能力缺失。

### 4.2 统一抽象：endpoint ↔ client
- 把一台机器的桌面暴露成 **endpoint**，接口 = **像素 + a11y + 输入**。任何 client（真人 / agent）都可连。
- 三种场景只是"endpoint 落在哪台机器 + 谁是 client"：
  - **场景1**：真人机 = endpoint，agent 作 client 接入操作（真人看自己的物理屏）。**唯一有本地主体**：人与 agent 共用同一屏/输入，且人机可能非 Linux（a11y 腿要换实现），授权主体是人。
  - **场景2**：agent 机 = endpoint，另一个 agent 作 client（agent 间协助）。
  - **场景3**：agent 机 = endpoint，真人作只读 client（看）。
- **场景2 与 3 同构**，只差 client 是人还是 agent；差别只在"endpoint 那台机器有没有本地物理屏和本地用户"（场景1 有，2/3 无）。

### 4.3 只有两种模式
- **模式 A（机器上没真人）**：agent 自行使用，不用屏。owner agent 持操作权，可授权给其他 agent，**可随时拿回**。
- **模式 B（机器上有真人）**：真人最高优先级，**可随时拿回**操作权；agent 们接入协助（不用屏）。
- "agent 在用电脑、真人想看" = **模式 A 的一个只读调试口**，不是独立模式；真要介入则**切到模式 B**（关掉 A 那套，改用 B）。

### 4.4 不变量与"撤销"原语（关键）
- **不变量：任一时刻至多一个"有效操作者"；操作权可被更高优先级者随时收回。**
- 两模式 = 这条不变量的两种优先级配置：A 由 owner agent 收回；B 由真人收回。
- **机制上只留一个极薄的"撤销/抢占"原语，不做排队或仲裁**：
  - 真人的**真实输入事件 = 立即抢占**，agent 的**在途动作立即作废/中止**，并 notify agent"你被抢了"。
  - agent 间用 **token**（可授权、可收回）实现同一件事。
  - 理由：agent"从看屏到动作"延迟大，真人不会"申请"权限而会直接抓鼠标 → 纯语言协调来不及。
- **语言只负责高层协调**（"我要操作""你等下"），**不负责防冲突**；防冲突交给撤销原语。
- 不可依赖的捷径：靠"语言 + 单操作者意识"避免竞态——延迟问题在模式 B 同样致命。

### 4.5 其他定案
- **观看向两处退化，几乎不需专门机制**：模式 A 的"看" = 调试口（只读观察者，可多路、分发便宜）；模式 B 的"看" = **人本机物理屏本身**，不是 client。
- **A2 结论对得上**：mutter ScreenCast 流**单消费者独占**（见实验日志）→ 不能多持有者，只能**单一持有者 + 对外分发**；正好 = "单操作者 + 多观察者"。
- **模式切换要便宜** → agent 的**推理与状态放在图形会话之外**，图形会话只是它"随时可换的一双手"。

## 五、待做实验（按 2026-09-21 定案重排）

> 已完成（本 VM）：E2/E3/E4(读树)/A1/A2/A5/A6、A4 覆盖率（自造页 **+ 真实站点**）、E5 的 X11 部分。**A4 懒开已证伪（`--force-renderer-accessibility` 目前必需）**。

**P1｜把 M2 的"操作"补完整（a11y 优先路径）**
- **值类控件**：~~A4 已发现 text/range/select/textarea 的 `doAction` **不改值** → 验 AT-SPI `setText`/`setValue`/键盘输入哪条通。~~ **已做（见实验日志）**：**range ✅ `Value.set_current_value`、select ✅ `open`+子项 `select`**；**text/textarea ❌**（chrome entry 无 `editable_text`，`generate_keyboard_event` 不生效）→ **文本输入缺口并入 E5（键盘注入）**。
- **A3**：按 id 重解析 bounds、子树查询、200ms deadline 回退（树遍历代价）。
- **分发验证**（原 A2 的可行性半边）：**一个服务独占 RecordMonitor，进程内 fan-out 给 N 个订阅者**，N 路都出帧 → 把"能分发"从推断变事实（= 模式 A 调试口 / 场景 3 的底座）。

**P2｜像素/指针路径（仅当需要兜底或 humanization 时）**
- **E5**：Wayland `NotifyPointerMotionAbsolute(stream, x, y)` 注入（虚拟指针需挂 stream）。
- **Wayland 全局坐标**：`Introspect.GetWindows` 被封 → 绕法（被测应用跑 Xwayland / 视觉锚定）。
- **A3 的坐标部分**（按 bounds 点击）随此路径。

**P3｜反检测（F1，需真机配合）**
- **E4 a11y 痕迹** + **F1 flag 可指纹性**：`--force-renderer-accessibility` 现为必需 → 与"过指纹"直接冲突，须在真机一并看。
- **E1/A12**：真 3D 机器上采指纹基线。**本 VM 无 3D，做不了**。
- **E6**：humanization（轨迹 / 时序）。

**P4｜自持 / 运维**
- ~~**A8**：linger + user unit 重启自持（**需 YZ reboot**）~~ ❌ **作废**（见文件头 + `handoff-screen-17.md` §十一·11.3）。
- ~~**A11**：user unit 集群收尾。~~ ❌ **作废**（见文件头）。

**本机判"不可满足"或需换机**：E1/A12（硬件）；Wayland 全局坐标（API 被封，但可绕）；场景1 非 Linux 人机的 a11y 腿（本机无法验）。

**随两模式模型新出的**
- **撤销原语原型**：真人真实输入即抢占 + agent 在途动作作废 → 属模式 B，本机可先做"桩"验证（无真实输入源）。
- **a11y 腿是否进 endpoint 接口**：决定场景1 与 2/3 能否共用同一套操作抽象（是设计决策，非纯实验）。

## 六、环境现状与改动

> ❌ **本节 `linger` / tangyu gsettings 等条目随自持·自启作废，待清理**（见文件头；清理命令见 `handoff-screen-17.md` §十一·11.3）。保留仅作历史。

- 目标账号 `tangyu(1001)`；`gdm` active（greeter 占 seat0/tty1）；tangyu 用 linger 起 headless shell。
- **新账号 `alice(1002)`**：YZ 建的，**正常桌面会话**（seat0/tty2）。zhengyp 有 sudo，可 `sudo -u alice`。
- **持久改动**：
  - `loginctl enable-linger tangyu`（可逆）
  - 临时 ACL `setfacl -m u:tangyu:rw /dev/dri/card0`（**重启失效**）
  - tangyu 的 `gsettings ... toolkit-accessibility=true`（**本轮又给 alice 也设了 true**）
  - VBox 主机侧 3D 加速已开（YZ 改）
  - **`screenlab-shell` 当前未运行**（transient `--collect` 单元已消失，`systemctl --user status` 报 "could not be found"）→ **开工需先按第七节重启**。
- **a11y bus 的 `IsEnabled` 是运行时属性**，总线重启即失效。
- **可能残留进程**：tangyu/alice 会话里的 chrome + `/tmp/a4-serve.py`（收工前清一遍）。

## 七、入口与纪律

> ❌ **本节 `systemd-run` / linger / `terminate-user` 相关命令全部失效**（见文件头），**勿再执行**。

```bash
# tangyu
ssh tangyu@localhost
export XDG_RUNTIME_DIR=/run/user/1001 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
# 起 headless 桌面（单元名统一 screenlab-*）
systemd-run --user --unit=screenlab-shell --collect --setenv=NO_AT_BRIDGE=0 \
  --property=StandardError=file:/tmp/screenlab-shell.err \
  -- gnome-shell --headless --virtual-monitor 1920x1080 --wayland-display=screenlab-0
# chrome（headless 会话里必须带这两个，否则：pending / 起不来）
google-chrome --password-store=basic --force-renderer-accessibility --ozone-platform=wayland <url>
# headless shell 必须先关空闲锁定，否则 ScreenCast 被拒（Session creation inhibited）
gsettings set org.gnome.desktop.session idle-delay 0
gsettings set org.gnome.desktop.screensaver lock-enabled false
# alice（正常会话，从本机以 sudo 操作）
sudo -S -k -u alice -H bash /tmp/<script>.sh < ~/.secrets/centos.key
```
- **sudo**：`sudo -S ... < ~/.secrets/centos.key`（本机必须 `-S`，密码只喂 stdin）。
- **`pkill -f <pattern>` 会自伤**（匹配到自己命令行 → 命令被切断）→ 用 `-x` 或 PID，或把 pkill 放进脚本文件。
- `xdg`/`X` 探测：Xwayland display 会飘（`:0/:1/:2`），**auth 文件也要配**，用组合探测（见 `a4.sh`）。
- 每条结论**先落 `screen-exp-log.md`**。

## 八、已知坑（本轮新增，其余沿用 #14）

- **会话里 chrome 页面全 pending → 先试 `--password-store=basic`**（根因是 keyring/Secret Service 不应答，**不是网络、不是 seat**）。
- **a11y 树渐进建立** → 扫描要等稳定（连扫一致）再下结论。
- **跨用户 /tmp 文件属主**会挡住日志写入（alice 写不了 tangyu 的 `/tmp/a4-serve.log`）→ 用各自路径或先清。
- **测试 HTTP 服务要线程化**（chrome 的 preconnect 空闲连接会堵死单线程服务器）。
- 沿用 #14：ScreenCast `RecordMonitor`、`Introspect` 被封、RemoteDesktop session 只对同连接暴露、`pkill` 自伤、journal 读不到要靠 `StandardError=file:`。
- **headless 里 chrome 默认走 X11 后端**，但 Xwayland 的 auth 对不上（`Invalid MIT-MAGIC-COOKIE-1 key`）→ 必须 **`--ozone-platform=wayland`**（比配 XAUTHORITY 稳）。
- **ScreenCast `CreateSession` 报 `Session creation inhibited`** → 先查 `org.gnome.ScreenSaver.GetActive`；是 headless shell **自己屏保/锁定**了 → 关 `idle-delay`/`lock-enabled`。见第七节命令。
- **不带 `--force-renderer-accessibility` 就是空树**（AT-SPI 已启用、chrome 已注册，但树只有 1 个 `frame` 节点）→ 懒开在本设置下不生效，**flag 目前必需**（与 F1 指纹冲突）。

## 九、脚本（`screen-lab-verify/`）

| 文件 | 用途 |
|---|---|
| `a4-page.html` | A4 可控测试页（14 个已知控件，激活时 `fetch('/hit?c=NAME')`） |
| `a4-serve.py` | 多线程回执服务（含 accept/request 日志） |
| `a4-atspi.py` | 遍历 chrome a11y 树、`doAction`、判真触发 |
| `a4-dump.py` / `a4-probe.py` | 树结构 dump / frame·document 探查 |
| `a4-run.sh` / `a4-alice*.sh` / `a4-basic*.sh` | 各会话启动+扫描（tangyu/alice、带/不带 password-store） |
| `a4-real.sh` / `a4-real-probe.py` | 真实站点启动（headless+`--ozone-platform=wayland`，`LAZY=1` 切无 flag）/ 树统计+role 直方图 |
| `a2.sh` / `a2b.sh` / `screencast-mon.py` | 流复用：单消费者对照 / 并发持有竞争者；持 session 拿 node id |

## 十、建议的首次动作

1. 第四节架构已由 YZ 定案（两模式 + 单操作者 + 撤销原语 + 调试口 + 状态在会话外），照此设计，无需再讨论。
2. 按第五节 **P1** 先跑：**值类控件（setText/setValue）** → **A3（重解析+子树+deadline）** → **分发验证（一个服务 fan-out N 路）**。
