# handoff｜交接：M2 图形路线（第九轮）· 2026-09-22 #22

> ➡️ 接续 `handoff-screen-21.md`（第八轮）。新会话从 #22 读起。
>
> **新会话只读四样，别多读**：
> 1. **目标（唯一约束）**：`spec-screen-1.md` §0.0 → 已提炼进 `handoff-screen-18.md` **§5.1**（用 §5.1，更干净）。
> 2. **本路线自己定的方案**：`handoff-screen-18.md` **§5.2 / §5.3 / 六 / 七**；三个 spec：`spec-screen-client-api.md`（动词面）、`spec-screen-ledger.md`（服务端账本）、`spec-screen-element-act.md`（元素动作语义）。
> 3. **读法纪律**：`handoff-screen-18.md` **§5.0**（双栏 + 反证句 + 作废即删名）。
> 4. **代码**：`cogos/screenlab/` + `cogos/agent/{tools.py, impl/graphics.py}`（分支 `feat/screenlab-p2`，本轮已提交 `800e5a9`、`1dfbdb5`）。
>
> ⚠️ **本轮的最大变化是"定位修正"，先读 §三再读别的**：a11y 树被**降级为可选**（图是主干）。`handoff-screen-21.md` §五/§六 里"树 + 元素表是主路径"的口径**已被本轮推翻**，别沿用。
> ⚠️ 不要读 `handoff-screen-15/16` 的目标与架构表述（已被 §5.1 取代）；不要用 `screenlab/install/install.sh` 与 `*.service`（旧 systemd 路线，已废）。

## 一、目标（摘要，以 §5.1 为准）

每 agent 有若干账户（账户是归属单位）；账户有一块**可操作的图形界面**，发动作能读回结果；操作要**像真人、不被检测**（逐步加固）；默认**不抢物理屏**，需要时人能看到/介入；三种关系 = 自用 / 授权他 agent（显式可收回）/ 与真人双向；**一账户同一时刻一块界面，"要"是幂等的**；**agent 只面对客户端**。

## 二、五条核心方案（已收敛，别再重新论证）

1. **界面是资源，通道是接入**：`open` 幂等作用在界面上；通道可多条（owner / 被授权 agent / 观察者），`revoke` 的对象是通道。
2. **长期身份 ≠ 接入凭证**：谁的机器谁持长期身份；外来主体一律**临时凭证**（有效期 + 可吊销 + 目标机本地判决）。
3. **每账户一个服务，无中心**：socket 在该账户自己的 runtime dir；传输已认证 ⇒ owner。
4. **传输不入方案**：只假定"有一条能通的字节流"；网络由外部提供。
5. **协调在语言层，机制只保下限**：不做心跳/协商/状态机/抢占协议。

## 三、本轮定的口径（YZ，2026-09-22）——**图的定位 > 树**

1. **图 = 主干**：感知 + 落点。理由：目标 2（可操作）已被图+pointer 满足；目标 3（像真人、能加固）**只有真实指针事件能往上走**，`do_action` 天生不产生指针事件序列；且图一份代码三平台通用。人的"一眼"不是基准，但 zoom + mark 能把"坐标估算不可靠"这个弱点补掉。
2. **a11y 树 = 可选的语义索引**：只在"按名字/角色精确找目标、批量列字段/链接、需要知道元素是什么"时**显式要一次**；用不上就不付代价。不是主路径。
3. **a11y 不做增量（本轮结论）**：AT-SPI 本身能做增量（事件 + 长驻客户端 + 缓存 = Orca 的做法），但我们现实现做不到，**要做对代价很大**——长驻 helper 会请回"GI 调用阻塞/挂死"的风险（helper 做成一次性子进程本就是为了躲它），还要事件 + 缓存失效 + 世代对账，且 AT-SPI/UIA/Android 三套各做一遍。**下注条件**：出现"agent 反复在大页面做批量语义操作"的场景才做，否则不做。
4. **机制不代判"看什么"**（§5.0/`spec-screen-element-act.md` §8 的延伸）：**相关性裁剪 = 代判**。`KEEP_ROLES`、"有名 or 有动作"、骨架/大纲——都属于机制替 agent 决定相关性，**应回退**。正确做法是**完整呈现 + 落成文件 + 回路径**，agent 用自己的 read/grep 决定看哪几行（样板已经有了：图不是喂像素，而是存文件回路径）。
5. **`capture` 的树必须显式获取**：`auto` 现在每帧隐式走一遍 a11y 树（~2.5s，见 §五），是**隐藏成本**。默认不走树，树降为显式请求。
6. **图路径待补两件小事**：`act` 接受**上一次 crop 帧内**的坐标（服务端换算整屏，免模型做全局换算）；`capture(center,size,mark=x,y)` 出带标记的局部图（自检落点）。
7. **`truncated` 的性质**：它是**生成树的时间/节点预算**的副产品，不是相关性判断；要"不截断"，办法是分页/长驻，而不是调大上限（见 §五·2）。

## 四、本轮已落地的代码（已提交，`feat/screenlab-p2`）

| 提交 | 内容 |
|---|---|
| `800e5a9` | 工具层暴露树/元素：`screen_capture` 回 `elements`（不透明 `id`/role/name/center/actions）；`screen_act` 增 `engine`；`element_digest` 有"滤 Chromium 通用动作"的**相关性裁剪（§三·4 计划回退）**；a11y keep 规则改为"有名 or 真动作 or KEEP_ROLES"（**同样计划回退**）、非 shell 应用先走、深度截断如实报；daemon 默认 `max_depth` 12→20；`ScreenClient.capture` 透传树预算 |
| `1dfbdb5` | **修真 bug**：`ScreenChannel` 从不发 `open`，agent 侧每次 capture/act 都回 `no_channel` —— "`act element` 对 agent 不可达"比 #21 说的更严重（不只是缺 id）。现首次使用自动 `open`（owner / 带 token），断线重连重开。新增 `tests/screenlab/e2e/tool_loop_e2e.py`（走工具层的完整闭环） |

**验证**：全仓 `python3.11 -m pytest tests` → **1248 passed, 4 skipped**；`tool_loop_e2e.py` → **all checks passed**。
未提交的只剩 `screenlab/install/install.ps1`（**Windows 侧旧改动，与本轮无关，别碰**）。

## 五、第九轮真机事实（照抄可用）

1. **元素表实测**（react.dev，agent1）：树 331 节点 / 194 元素；194 项 ≈ **47KB**（≈244B/项），默认取 40 项 ≈10KB。**默认 40 条被浏览器自身 UI 占满**（前 40 全是窗口按钮/工具栏/地址栏/Chrome 内置提示），页面内容一条不进——这是"扁表当默认"造成的（`element_digest` 拍平了树，结构丢失，也就丢了消歧与收敛路径）。
2. **走树成本**：AT-SPI 每节点要多次**同步 D-Bus 调用**（role/name/actions/states(7 次)/rect/children）⇒ 实测 **~7ms/节点，331 节点 ~2.5s**；整桌面（多 app + 真实 DOM）上万节点 ⇒ 几十秒，helper 有硬 timeout，走到一半被杀就产生 `truncated`。**daemon 每次 capture 起新 helper 进程 ⇒ 无缓存**（真人的 AT 是长驻连接 + 暖缓存 + 事件增量，所以不慢）。
3. **Chromium 给每个 DOM 节点都挂 `showContextMenu`（通常还有 `doDefault`）** ⇒ "有 action"不含信息量；`MEANINGFUL_ACTIONS = {click, activate, press, jump}` 才是真信号。
4. **同名元素靠区域消歧**：react.dev 上有两个 `React` link（logo 与正文）——扁表无解，树有解。
5. **`do_action` 能导航内容链接**：default（auto→do_action）对 'v19.3' 链接 `navigated=True`；`pointer` 点击同链接 → 标题变 `React Versions – React`、元素 194→173。上一轮"do_action 在链接上不导航"是**误判**（那次点的是首页 logo 链接）。
6. **工具层闭环全过**（`tool_loop_e2e.py`）：capture 回图+元素表、`max_elements` 生效且 `elements_total` 如实、导航/取 id/`act element` 生效（data: 页按钮标题 TL0→TL1）、stale id → `stale_ref`、无 capture 就 act → `no frame`、`pointer` 命中元素中心。

## 六、遗留 / 候选方向（**均由 YZ 定，不是待办清单**）

1. **图主干落地**（首推）：`auto` 不再隐式走树（去掉每帧 ~2.5s 暗成本）；`act` 收 crop 内坐标；`capture` 带 `mark` 出标记局部图；量一次"图路径 vs 树路径"的点数/延迟/token。
2. **回退 a11y 相关性裁剪；树改"显式获取 + 完整落成文件 + 回路径"**（机制只呈现，agent 自己 read/grep）。
3. **图/树产物**：图已是本地文件 + 路径；树照抄（新增 `tree_path`，含 id，行导向无损格式）。
4. **a11y 增量缓存**：按 §三·3 的**下注条件**判断，不满足不做。
5. **⑤ 世代归账本**：`snapshot_id` 仍是连接级，而 element 引用已绑世代（语义债，等取景定了再一起收）。
6. **③ 观察口推流**：只读位已通，"喂给人看"的形态没做。
7. **④ 关系③a**：真人在自己机器装服务、agent 接入——本机只验了 agent↔agent。
8. **⑥ 授权粒度**：只到账户级；会话/窗口级是遗留。
9. **⑦ 反检加固档**：检测方 = 远端网页（已定）；加固主项 = 渲染落真 GPU；**图/pointer 是能加固的那条腿**。
10. **⑧ 冷启动约 1 分钟**；**⑨ 空账户一键未做**。

## 七、本机环境事实（照抄可用）

- 账户：`agent1`(uid 1003)、`agent2`(uid 1004)；`zhengyp`(1000，sudo)、`tangyu`(1001)、`alice`(1002)。sudo 密码：`~/.secrets/centos.key`（喂 stdin）。
- **会话 bus**：`unix:path=/run/user/<uid>/bus`。`gnome-shell` 与 `screenlab` daemon 都在它上面（本轮 daemon pid 35557，socket `/run/user/1003/screenlab.sock`，`9月22 03:36`）。
- **本轮 display `:6`**；xauth 为 `/run/user/1003/.mutter-Xwaylandauth.*`（**文件名随会话变，本轮 `N9TAW3`**，用 `ls -t` 取；zhengyp 读不到 `/run/user/1003`，要 `sudo`）。
- chrome 仍在这一会话里跑（主进程被 runuser 包着，子进程 `/opt/google/chrome/chrome … --user-data-dir=/home/agent1/.config/chrome-a11y`）。
- 依赖：`python3`(3.9，Pillow + PyGObject/Atspi)、`python3.11`(**system 无 gi/Pillow/pyte**；**pyte 等客户侧依赖在 `/home/zhengyp/.local/lib/python3.11/site-packages`**)。
- **跨身份跑客户侧的坑**：`/home/zhengyp` 是 700，agent1 读不到仓库。跑 `cogos` 客户侧 harness 的可用姿势（本轮实测）：
  ```bash
  # 1) 把仓库的 cogos/ screenlab/ 拷到 /tmp（a+rX），或直接在 root 下跑
  sudo env PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/tmp/kilo/harness:/home/zhengyp/.local/lib/python3.11/site-packages \
    /usr/bin/python3.11 /tmp/kilo/harness/tool_loop_e2e.py --sock unix:/run/user/1003/screenlab.sock
  ```
  （root 能读仓库也能进 `/run/user/1003`；daemon **不做 peer-uid 校验**，所以 root 连上去仍是 owner 通道）

**常用命令**
```bash
# 装配 + 起屏（root 或账户自己）
sudo bash cogos/screenlab/install/account-install.sh agent1
sudo bash cogos/screenlab/install/session-start.sh agent1 [--restart]

# 客户端（以该账户身份跑；跨机时用隧道 + --tcp 127.0.0.1:9911）
runuser -u agent1 -- env PYTHONPATH=/home/agent1/.local/share python3 -m screenlab.service.cli \
  --socket /run/user/1003/screenlab.sock open
... capture --mode auto|tree|pixels | act pointer --x 0.25 --y 0.35
... act element --element-id <id> [--element-action press] [--element-engine auto|do_action|pointer]
... grant --bits capture,input --ttl 60 [--once] / revoke --credential <token>

# 只重启 daemon（--restart 会重起 gnome-shell）
sudo bash -c 'pkill -u agent1 -f "screenlab.service.cli daemon"; sleep 1; \
  runuser -u agent1 -- env HOME=/home/agent1 XDG_RUNTIME_DIR=/run/user/1003 DISPLAY=:6 \
  XAUTHORITY=$(ls -t /run/user/1003/.mutter-Xwaylandauth.* | head -1) \
  DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1003/bus PYTHONPATH=/home/agent1/.local/share \
  setsid python3 -m screenlab.service.cli daemon --display :6 \
  --xauth $(ls -t /run/user/1003/.mutter-Xwaylandauth.* | head -1) \
  --socket /run/user/1003/screenlab.sock --blob-dir /home/agent1/.local/share/screenlab/blobs \
  --account agent1 >>/home/agent1/.local/share/screenlab/daemon.log 2>&1 </dev/null &'

# 单测（必须 3.11）
python3.11 -m pytest tests/screenlab -q
python3.11 -m pytest tests -q                    # → 1248 passed, 4 skipped
```

## 八、已知坑（都踩过，别再踩）

1. **私有 `dbus-run-session` 下 a11y 必死**（`org.a11y.Bus.GetAddress` 挂死）→ 会话必须跑在账户自己的 systemd 用户 bus 上。
2. **helper 的 `DISPLAY` 必须是会话那个**；继承 ssh 的 `localhost:10.0` 会挂死。
3. **`Atspi.Accessible` 没有 `get_action_count`**，正确是 **`get_n_actions()`**；用错会被 `except` 静默吞掉 ⇒ 全树误报"无 action"。
4. **`pgrep -x` 对超 15 字符进程名失效**，用 `pgrep -f`（放脚本文件里避免 `-f` 自伤）。
5. **Pillow `ImageGrab` 在 Xwayland root 上取帧失败** → 用 `gst ximagesrc`（`pick_capture` 探测式）。
6. **由 root 启动会话必须带 `HOME / XDG_RUNTIME_DIR / USER / LOGNAME`**，否则 gnome-shell 用 root home → X server 假死。
7. **`xdotool` 在假死 display 上无限阻塞** → 探活一律 `timeout -s KILL 3`；helper 靠硬 timeout。
8. **`set -e` + `pipefail`**：`ls` 取不存在的 auth 文件会直接退出脚本。
9. **pytest 直跑绑 py3.9**（`Path | None` 报错）→ 用 `python3.11 -m pytest`。
10. **`pkill/pgrep -f` 自伤** → 放进脚本文件，或按 PID。
11. **别把"起 daemon"和别的命令塞进同一个 `bash -c`**（logind 会判会话已死）。
12. **a11y 裁剪历史上是经验值**：本轮后按 §三·4 要回退相关性裁剪，别再往 `KEEP_ROLES` 上打补丁。
13. 旧路线残留：root 的 `Xvfb :99` + `/opt/screenlab` 仍在跑（**与新路线无关**，是否退役待 YZ）；机器上还有较早遗留的 `runuser -u agent1 … python3 -` 挂住进程，未清理。
14. **工具层"能跑"不等于"好用"**：`1dfbdb5` 之前 `screen_capture/screen_act` 是**完全不可用**的（从不 open），而单测全绿——所以客户侧改动必须过 `tool_loop_e2e.py`，别只看 pytest。
15. **客户侧 import 需要 pyte 等依赖**：system `python3.11` 没有，要用 `/home/zhengyp/.local/lib/python3.11/site-packages`（见 §七）。

## 九、纪律（沿用，实测有效）

- **双栏**：每条陈述标 `[目标]` / `[方案]`；**只有 `[目标]` 有否决权**。
- **目标段禁实现名词**；**方案段必须挂账**（满足目标的哪一条 + 代价）。
- **反证句自检**：说"因为已验/已定案/以前这么做"就暂停。
- **机制不代判**（本轮加强）：不代判动作生效、**也不代判"看什么"**（相关性裁剪/骨架/大纲都属代判）。
- **作废即删名**：`热订阅` / `关闭重开` / `"形态（全桌面 vs 最小 X）"作选项` / `Xvfb 作起步形态` / `网络/NAT/打洞`。
- 开工起 **10–15 分钟闹钟**；用 `terminal_exec`（非阻塞），**不要 sleep 轮询**；到点先落结论再继续。
- 一次只跑一条实验命令；sudo 密码只喂 stdin（`< ~/.secrets/centos.key`）。
