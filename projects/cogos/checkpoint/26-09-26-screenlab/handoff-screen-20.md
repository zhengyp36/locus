# handoff｜交接：M2 图形路线（第七轮）· 2026-09-22 #20

> ➡️ 接续 `handoff-screen-19.md`（第六轮）。新会话从 #20 读起。
>
> **新会话只读四样，别多读**：
> 1. **目标（唯一约束）**：`spec-screen-1.md` **§0.0** → 已提炼进 `handoff-screen-18.md` **§5.1**（用 §5.1，更干净）。
> 2. **本路线自己定的方案**：`handoff-screen-18.md` **§5.2 / §5.3 / 六 / 七**；两个 spec：`spec-screen-client-api.md`（动词面）、`spec-screen-ledger.md`（服务端账本）。
> 3. **读法纪律**：`handoff-screen-18.md` **§5.0**（双栏 + 反证句 + 作废即删名）——不是形式主义，是本轮实测有效。
> 4. **代码**：`cogos/screenlab/`（**本轮已提交 `aff18b5`，分支 `feat/screenlab-p2`**）。
>
> ⚠️ 不要读 `handoff-screen-15/16` 的目标与架构表述（已被 §5.1 取代，容易倒退）；不要用 `screenlab/install/install.sh` 与 `*.service`（旧 systemd 路线，已废）。

## 一、目标（摘要，以 §5.1 为准）

每 agent 有若干账户（账户是归属单位）；账户有一块**可操作的图形界面**，发动作能读回结果；操作要**像真人、不被检测**（逐步加固）；默认**不抢物理屏**，需要时人能看到/介入；三种关系 = 自用 / 授权他 agent（显式可收回）/ 与真人双向；**一账户同一时刻一块界面，"要"是幂等的**；**agent 只面对客户端**。

## 二、五条核心方案（已收敛，别再重新论证）

1. **界面是资源，通道是接入**：`open` 幂等作用在界面上；通道可多条（owner / 被授权 agent / 观察者），`revoke` 的对象是通道。
2. **长期身份 ≠ 接入凭证**：谁的机器谁持长期身份；外来主体一律**临时凭证**（有效期 + 可吊销 + 目标机本地判决）。凭证靠状态（一条记录一个状态：未兑换/已兑换/已吊销/已过期）。
3. **每账户一个服务，无中心**：socket 在该账户自己的 runtime dir；传输已认证 ⇒ owner。
4. **传输不入方案**：只假定"有一条能通的字节流"；网络（隧道/NAT/tailscale）由外部提供。
5. **协调在语言层，机制只保下限**：不做心跳/协商/状态机/抢占协议。

## 三、进度

| 步骤 | 状态 | 产物 |
|---|---|---|
| 1. 客户端动词面 | ✅ 定稿 | `spec-screen-client-api.md` |
| 2. 服务端最小账本 | ✅ 定稿 | `spec-screen-ledger.md` |
| 3. 最小闭环（本机） | ✅ 跑通 | `cogos/screenlab/` |
| 4. 权限语义 | 🔶 部分 | grant/revoke/单操作者/只读位已验；**观察口推流未做** |
| 5. 接入端点 | 🔶 部分 | agent↔agent（ssh 隧道）已验；**关系③a 未验** |
| 6. 装配 | 🔶 部分 | `session-start/stop` 本轮改为**用户 bus**；未做"空账户一键" |
| 7. 反检加固 | ⬜ 未开始 | 起步档"对谁隐蔽"还没定 |
| **8. a11y 反馈腿** | 🔶 **读树完成（本轮）** | `service/a11y_helper.py`；`capture mode=tree` 已通；**`act element` 未做** |

## 四、本轮成果：a11y 反馈腿（第七轮）

**YZ 决策**（2026-09-22）：第一刀**只到"读树反馈"**，`act element` 留第二刀；`capture(mode=auto)` **同时回"树 + 画面"**（同世代），而不是二选一——否则客户端要画面得再发一次 capture，必然新世代，"同源同帧"就假了。

**根因（本轮最大的坑，已修）**：会话原来用**私有 `dbus-run-session`**（dbus-daemon）。在这种 bus 上 `at-spi-bus-launcher` 会退回用 dbus-daemon 拉 accessibility bus，且 `org.a11y.Bus.GetAddress` **稳定挂死**（干净会话也复现）⇒ gnome-shell / chrome 都发现不了 a11y bus，树永远是空的（`child_count=-1`）。换成账户**自己的 systemd 用户 bus**（dbus-broker）后，launcher 用 dbus-broker 拉 a11y bus，`GetAddress` 正常应答。

**改动**（`cogos/screenlab/`，已提交）：
- `install/session-start.sh`：会话 bus 从私有 `dbus-run-session` 改为账户自己的 systemd 用户 bus（`unix:path=$RT/bus`）；`gsettings set … toolkit-accessibility true`；把 `DBUS_SESSION_BUS_ADDRESS` 传给 daemon。空账户缺 bus 时 root 侧 `loginctl enable-linger` + `systemctl start user@<uid>.service`。
- `install/session-stop.sh`：停会话时清 `at-spi-bus-launcher` / `at-spi2-registryd` / a11y broker（原来不清，跨重启累积成僵尸 bus）。
- `service/a11y_helper.py`（新）：一次性 AT-SPI 读树，吐**裁剪后的一行 JSON**（`path/role/name/rect/actions/states/children`；`rect` 是屏幕像素，daemon 侧归一化）。裁剪：只留"有名字 / 有 action / 属于 KEEP_ROLES"的节点 + 数量与深度上限 + 只往下递归"showing"的子树。
- `service/backends.py`：新增 `A11yTree`（子进程封装 + 带 TTL 的可用性探测）。**daemon 绝不 import gi**——helper 会挂死，靠子进程 + 硬 timeout 隔离。
- `service/platform_backends.py`：`pick()` 第 4 个返回值 = a11y 树（win/android 为 None）。
- `service/daemon.py`：`capture(mode=auto|pixels|tree)` 路由；`_norm_node/_norm_tree` 把像素 rect 转归一 `center/size`；`_tree_meaningful` 判"有意义的树"（**gnome-shell 自己永远有树，不算**）；`info` 补 `modes/a11y_backend/a11y_available`。
- `service/cli.py`：`capture --mode`。

**验证（本机 agent1，全过）**：
- `tree` = 只出树（194 节点，含 Google Chrome）；`auto` = 图 + 树，**同一 `snapshot_id`**；`pixels` = 只图。
- 反例：杀掉 chrome 只剩 shell 时，`auto` 只出图不出树（退化正确）。
- `act pointer` 往返正常（0.3,0.4 → 576,432）；`state` 一致。
- `python3.11 -m pytest tests/screenlab` → **8 passed**（见坑 #9：不能再用 `pytest` 直跑）。

## 五、本机环境事实（照抄可用；**会话 bus 已变**）

- 账户：`agent1`(uid 1003)、`agent2`(uid 1004)；`zhengyp`(1000，sudo)、`tangyu`(1001)、`alice`(1002)。
- **会话 bus（本轮起）**：`unix:path=/run/user/<uid>/bus`（systemd 用户 dbus-broker）。`gnome-shell` 与 `screenlab` daemon 都在它上面。
- socket：`/run/user/<uid>/screenlab.sock`；display 由脚本探出（本轮为 `:6`）；xauth 为 `/run/user/<uid>/.mutter-Xwaylandauth.*`。
- a11y bus：由 launcher 拉起的 dbus-broker（地址可用 `org.a11y.Bus.GetAddress` 问）；`toolkit-accessibility=true` 已设。
- 依赖：`python3`(3.9，**Pillow 10 + PyGObject/Atspi**)、`python3.11`(**无 gi、无 Pillow**，但**有 pytest**)、`gnome-shell 40.10`、`xdotool`、`gst-launch-1.0`、`xauth`、`pipewire`（按需）、`google-chrome`（唯一现成 GUI 应用，GTK 应用未装）。**`xdpyinfo`/`xwd`/ImageMagick 没装。**
- agent2 → agent1 已配免密：`ssh -o BatchMode=yes agent1@localhost`；跨账户接入用 streamlocal 隧道：
  `ssh -N -L 9911:/run/user/1003/screenlab.sock agent1@localhost`

**常用命令**
```bash
# 装配 + 起屏（root 或账户自己）；本轮起会切到用户 bus
sudo bash cogos/screenlab/install/account-install.sh agent1
sudo bash cogos/screenlab/install/session-start.sh agent1 [--restart]

# 客户端（以该账户身份跑；跨机时用隧道 + --tcp 127.0.0.1:9911）
runuser -u agent1 -- env PYTHONPATH=/home/agent1/.local/share python3 -m screenlab.service.cli \
  --socket /run/user/1003/screenlab.sock open
... capture --mode auto|tree|pixels | act pointer --x 0.25 --y 0.35
... grant --bits capture,input --ttl 60 [--once]      # 输出 token
... revoke --credential <token>

# 会话里起 chrome（a11y 要 force-renderer-accessibility）
runuser -u agent1 -- env HOME=/home/agent1 XDG_RUNTIME_DIR=/run/user/1003 DISPLAY=:6 \
  XAUTHORITY=$(ls -t /run/user/1003/.mutter-Xwaylandauth.* | head -1) \
  DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1003/bus \
  google-chrome --force-renderer-accessibility --no-first-run --no-default-browser-check \
  --user-data-dir=/home/agent1/.config/chrome-a11y --disable-dev-shm-usage about:blank &

# 单测（必须走 3.11，见坑 #9）
python3.11 -m pytest tests/screenlab -q
```

## 六、已知坑（都踩过，别再踩）

1. **私有 `dbus-run-session` 下 a11y 必死**：`org.a11y.Bus.GetAddress` 挂死，树永远空。会话必须跑在**账户自己的 systemd 用户 bus** 上。（本轮根因）
2. **helper 的 `DISPLAY` 必须是会话那个**：`Atspi.init()` 会去连 `DISPLAY`；继承到 ssh 转发的 `localhost:10.0` 就挂死在 TCP 6010。daemon 传 `DISPLAY`/`XAUTHORITY` 给 helper。
3. **`pgrep -x` 对超 15 字符的进程名失效**：`comm` 被截断（`at-spi-bus-launcher`→`at-spi-bus-laun`），一律用 `pgrep -f`（脚本文件里用，避免 `-f` 自伤）。
4. **Pillow `ImageGrab` 在 Xwayland root 上取帧失败**（`X get_image failed`）→ 已改用 `gst ximagesrc`（`pick_capture` 探测式）。
5. **由 root 启动会话必须带 `HOME / XDG_RUNTIME_DIR / USER / LOGNAME`**，否则 gnome-shell 用 root 的 home → **X server 假死**（能连上、永不回应）。已修在 `session-start.sh`。
6. **`xdotool` 在假死 display 上无限阻塞** → 探活一律 `timeout -s KILL 3`；helper 同理靠硬 timeout。
7. **`set -e` + `pipefail`**：`ls` 取不存在的 auth 文件会直接退出脚本 → 用 `{ ... || true; } | head`。
8. **停会话要 TERM→KILL 升级**，并清理 stale `/tmp/.X11-unix/X*` 与 `.mutter-Xwaylandauth.*`。
9. **pytest 直跑绑 py3.9**（`Path | None` 报错）→ 用 `python3.11 -m pytest`。
10. `pkill -f`/`pgrep -f` 会**自伤**（匹配到自己命令行）→ 放进脚本文件，或按 PID。
11. 旧路线残留：root 的 `Xvfb :99` + `/opt/screenlab`（旧 systemd 原型）仍在跑，**与新路线无关**，是否退役待 YZ。
12. a11y 的**裁剪策略是经验值**（KEEP_ROLES / 深度 / 数量）：大树（复杂网页）会被截断，`truncated=true` 时节点不全，需按场景调。

## 七、遗留 / 候选方向（**均由 YZ 定，不是待办清单**）

1. **`act element`（第二刀，最直接）**：用树节点的 `path` 重新定位并 `do_action`；无 action 时按 `center` 用 xdotool 点，但要标为降级。仍要过 ledger 的 input 位 + snapshot 世代校验。
2. **观察口推流**：只读位已通，"喂给人看"的形态（网页 viewer？推流？）没做。
3. **关系③a**：真人在自己机器上装服务、agent 接入——本机只验了 agent↔agent。
4. **世代归账本**：现在 `snapshot_id` 仍是**连接级**（`spec-screen-1` §2 原样），账本里 `generation` 还没接管。
5. **授权粒度**：只到账户级；会话/窗口级是遗留。
6. **反检档位**：起步"对谁隐蔽"未定；加固主项 = 渲染落真 GPU（本机 vmwgfx 弱 GPU）。**a11y 桥本身是可检测指纹**，要进加固清单。
7. **冷启动约 1 分钟**（会话 + 探活），体感慢。
8. **验证脚本未入库**：本轮的 e2e（owner 闭环 / 凭证 13 项 / 跨账户 / a11y 三模式）都在 `/tmp/kilo/`（临时，重启即失）。
9. **空账户一键未做**：本轮新增了对 systemd 用户 bus 的依赖（缺 bus 要 `enable-linger` + `start user@<uid>`），装配脚本已含这段，但没在全新账户上验过。

## 八、纪律（沿用，实测有效）

- **双栏**：每条陈述标 `[目标]` / `[方案]`；**只有 `[目标]` 有否决权**。
- **目标段禁实现名词**；**方案段必须挂账**（满足目标的哪一条 + 代价）。
- **反证句自检**：说"因为已验/已定案/以前这么做"就暂停。
- **作废即删名**：`热订阅` / `关闭重开` / `"形态（全桌面 vs 最小 X）"作选项` / `Xvfb 作起步形态` / `网络/NAT/打洞`。
- 开工起 **10–15 分钟闹钟**；用 `terminal_exec`（非阻塞），**不要 sleep 轮询**；到点先落结论再继续。
- 一次只跑一条实验命令；sudo 密码只喂 stdin（`< ~/.secrets/centos.key`）。
