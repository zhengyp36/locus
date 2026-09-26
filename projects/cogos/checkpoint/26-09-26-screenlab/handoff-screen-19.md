# handoff｜交接：M2 图形路线（第六轮）· 2026-09-22 #19

> ➡️ **已被 `handoff-screen-20.md`（第七轮）接续**（变化：会话改用账户 systemd 用户 bus；a11y 读树已接、已提交 `aff18b5`）。新会话从 #20 读起；本文件此后作为**代码现状（§四）/ 环境事实（§五）/ 坑（§六）**的历史引用。

> **新会话只读四样，别多读**：
> 1. **目标（唯一约束）**：`spec-screen-1.md` **§0.0** → 已提炼进 `handoff-screen-18.md` **§5.1**（用 §5.1，更干净）。
> 2. **本路线自己定的方案**：`handoff-screen-18.md` **§5.2 / §5.3 / 六 / 七**；两个 spec：`spec-screen-client-api.md`（动词面）、`spec-screen-ledger.md`（服务端账本）。
> 3. **读法纪律**：`handoff-screen-18.md` **§5.0**（双栏 + 反证句 + 作废即删名）——**不是形式主义，是本轮实测有效**。
> 4. **代码**：`cogos/screenlab/`（含第 3 步新增的 ledger / 动词 / 装配脚本）。
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
| 3. 最小闭环（本机） | ✅ 跑通 | `cogos/screenlab/` 代码，见 `handoff-screen-18.md` §七 |
| 4. 权限语义 | 🔶 部分 | grant/revoke/单操作者/只读位已验；**观察口推流未做** |
| 5. 接入端点 | 🔶 部分 | agent↔agent（ssh 隧道）已验；**关系③a（真人在自己机器上装服务）未验** |
| 6. 装配 | 🔶 部分 | `session-start/stop` 可远程无交互、幂等；未做"空账户一键" |
| 7. 反检加固 | ⬜ 未开始 | 起步档"对谁隐蔽"还没定 |

## 四、代码现状（`cogos/screenlab/`，**未提交**）

**动词**（wire）：`open / close / state / capture / act / grant / revoke / info / displays / blob_get`。

**账本**（`service/ledger.py`）：`screen{opened, input_holder, generation}` · `credentials{token→bits,scope,expiry,once,state}` · `channels{id→credential,bits,subject,alive}`；不变量 = 至多一个输入持有者、通道位 ⊆ 凭证位、不可用凭证不得再兑换。

**关键实现点**：
- 判权在服务端、按**通道的位**（`ledger.require` / `take_input`），不靠客户端自律。
- `revoke` → 凭证转态 + **连带断掉派生通道**（客侧下一次调用 `no_channel`）。
- 一次性=兑换通道时转态（已建通道继续活）；有效期同时界定通道寿命。
- 表在内存，重启即失效（安全默认）。

**装配**（`install/`）：
- `account-install.sh <account>`：把包装进 `~/.local/share/screenlab`。
- `session-start.sh <account> [--restart] [--with-pipewire]`：起会话（`gnome-shell --headless --virtual-monitor` + Xwayland）+ 服务；**幂等**；root 或账户自己都能跑。
- `session-stop.sh <account> [--session]`。

## 五、本机环境事实（照抄可用）

- 账户：`agent1`(uid 1003)、`agent2`(uid 1004)；`zhengyp`(1000，sudo)、`tangyu`(1001)、`alice`(1002)。建账户用 `checkpoint/setup-test-account.sh create <u> <p>`。
- socket：`/run/user/<uid>/screenlab.sock`；display 由脚本探出（本轮为 `:6`）。
- 依赖：`python3`(3.9，**Pillow 10**)、`python3.11`(无 Pillow)、`gnome-shell 40.10`、`xdotool`、`gst-launch-1.0`、`xauth`、`pipewire`（按需）。**`xdpyinfo`/`xwd`/ImageMagick 没装。**
- agent2 → agent1 已配免密：`ssh -o BatchMode=yes agent1@localhost`；跨账户接入用 **streamlocal 隧道**：
  `ssh -N -L 9911:/run/user/1003/screenlab.sock agent1@localhost`

**常用命令**
```bash
# 装配 + 起屏（root 或账户自己）
sudo bash cogos/screenlab/install/account-install.sh agent1
sudo bash cogos/screenlab/install/session-start.sh agent1 [--restart]

# 客户端（以该账户身份跑；跨机时用隧道 + --tcp 127.0.0.1:9911）
runuser -u agent1 -- env PYTHONPATH=/home/agent1/.local/share python3 -m screenlab.service.cli \
  --socket /run/user/1003/screenlab.sock open
... state | capture --out /tmp/a.png | act pointer --x 0.25 --y 0.35
... grant --bits capture,input --ttl 60 [--once]      # 输出 token
... revoke --credential <token>
```

## 六、已知坑（都踩过，别再踩）

1. **Pillow `ImageGrab` 在 Xwayland root 上取帧失败**（`X get_image failed`）→ 已改用 `gst ximagesrc`（`pick_capture` 探测式）。
2. **由 root 启动会话必须带 `HOME / XDG_RUNTIME_DIR / USER / LOGNAME`**，否则 gnome-shell 用 root 的 home → **X server 假死**（能连上、永不回应）。这是本轮最大的坑，已修在 `session-start.sh`。
3. **`xdotool` 在假死 display 上无限阻塞**，`timeout` 都难杀掉 → 探活一律 `timeout -s KILL 3`。
4. **`set -e` + `pipefail`**：`ls` 取不存在的 auth 文件会直接退出脚本 → 用 `{ ... || true; } | head`。
5. **停会话要 TERM→KILL 升级**，并清理 stale `/tmp/.X11-unix/X*` 与 `.mutter-Xwaylandauth.*`，否则毒害下一次启动。
6. mutter 的 X cookie **不绑 display 号**（`xauth list` 里 display 为空）→ 探 display 要用"谁拥有 X socket"来枚举。
7. `pkill -f`/`pgrep -f` 会**自伤**（匹配到自己这条命令行）→ 用 `-x` / PID / 放进脚本文件。
8. 旧路线残留：root 的 `Xvfb :99` + `/opt/screenlab`（旧 systemd 原型）仍在跑，**与新路线无关**，是否退役待 YZ。

## 七、遗留 / 候选方向（**均由 YZ 定，不是待办清单**）

1. **接 a11y**（反馈的第二条腿）——遗留第一条。做法：把 `checkpoint/screen-lab-verify/a4-atspi.py` 那套读树搬成 `backends.py` 的一个后端，与 `GstX11Capture` **共享同一次 capture 的世代**，再按 `capture(mode=auto|pixels|tree)` 路由（§5.3·1 / §4·14）。**注意**：AT-SPI 要挂在**账户会话的 session bus** 上，装配脚本现在正好在会话里起进程，路已通。
2. **观察口推流**：只读位已通，但"喂给人看"的形态（网页 viewer？推流？）没做。
3. **关系③a**：真人在自己机器上装服务、agent 接入——本机只验了 agent↔agent。
4. **世代归账本**：现在 `snapshot_id` 仍是**连接级**（`spec-screen-1` §2 原样），账本里 `generation` 还没接管。
5. **授权粒度**：只到账户级；会话/窗口级是遗留（目标 §0.0 曾列为未闭合）。
6. **反检档位**：起步"对谁隐蔽"未定；加固主项 = 渲染落真 GPU（本机是 vmwgfx 弱 GPU）。
7. **冷启动约 1 分钟**（会话 + 探活），体感慢。
8. **验证脚本未入库**：本轮的 e2e（owner 闭环 / 凭证 13 项 / 跨账户）都在 `/tmp/kilo/`（临时，重启即失）；单测 `tests/screenlab/test_ledger.py` 在**本机跑不起来**（仓库 conftest 要 py≥3.10，本机 pytest 绑 py3.9）。
9. **代码未提交**；`screenlab/install/install.ps1` 有**旧的无关注改动**，别顺手带上。

## 八、纪律（沿用，实测有效）

- **双栏**：每条陈述标 `[目标]` / `[方案]`；**只有 `[目标]` 有否决权**。
- **目标段禁实现名词**；**方案段必须挂账**（满足目标的哪一条 + 代价）。
- **反证句自检**：说"因为已验/已定案/以前这么做"就暂停——那是本轮三次走偏的来源（`Xvfb` 起步、共屏=热订阅、把"形态"当待选项）。
- **作废即删名**：`热订阅` / `关闭重开` / `"形态（全桌面 vs 最小 X）"作选项` / `Xvfb 作起步形态` / `网络/NAT/打洞`。
- 开工起 **10–15 分钟闹钟**；用 `terminal_exec`（非阻塞），**不要 sleep 轮询**；到点先落结论再继续。
- 一次只跑一条实验命令；sudo 密码只喂 stdin（`< ~/.secrets/centos.key`）。
