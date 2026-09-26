# handoff｜交接：M2 图形路线（第八轮）· 2026-09-22 #21

> ➡️ 接续 `handoff-screen-20.md`（第七轮）。新会话从 #21 读起。
>
> **新会话只读四样，别多读**：
> 1. **目标（唯一约束）**：`spec-screen-1.md` **§0.0** → 已提炼进 `handoff-screen-18.md` **§5.1**（用 §5.1，更干净）。
> 2. **本路线自己定的方案**：`handoff-screen-18.md` **§5.2 / §5.3 / 六 / 七**；三个 spec：`spec-screen-client-api.md`（动词面）、`spec-screen-ledger.md`（服务端账本）、**`spec-screen-element-act.md`（本轮新增：元素动作语义 + 观测定界）**。
> 3. **读法纪律**：`handoff-screen-18.md` **§5.0**（双栏 + 反证句 + 作废即删名）。
> 4. **代码**：`cogos/screenlab/`（**本轮已提交 `bab728e`，分支 `feat/screenlab-p2`**）。
>
> ⚠️ 不要读 `handoff-screen-15/16` 的目标与架构表述（已被 §5.1 取代，容易倒退）；不要用 `screenlab/install/install.sh` 与 `*.service`（旧 systemd 路线，已废）。

## 一、目标（摘要，以 §5.1 为准）

每 agent 有若干账户（账户是归属单位）；账户有一块**可操作的图形界面**，发动作能读回结果；操作要**像真人、不被检测**（逐步加固）；默认**不抢物理屏**，需要时人能看到/介入；三种关系 = 自用 / 授权他 agent（显式可收回）/ 与真人双向；**一账户同一时刻一块界面，"要"是幂等的**；**agent 只面对客户端**。

## 二、五条核心方案（已收敛，别再重新论证）

1. **界面是资源，通道是接入**：`open` 幂等作用在界面上；通道可多条（owner / 被授权 agent / 观察者），`revoke` 的对象是通道。
2. **长期身份 ≠ 接入凭证**：谁的机器谁持长期身份；外来主体一律**临时凭证**（有效期 + 可吊销 + 目标机本地判决）。
3. **每账户一个服务，无中心**：socket 在该账户自己的 runtime dir；传输已认证 ⇒ owner。
4. **传输不入方案**：只假定"有一条能通的字节流"；网络由外部提供。
5. **协调在语言层，机制只保下限**：不做心跳/协商/状态机/抢占协议。

## 三、本轮定的两条原则（YZ，2026-09-22）

- **检测方 = 远端网页，本机痕迹暂不考虑**。⇒ a11y 腿可放心铺；"像真人"的着力点在**事件层**（是否有真实指针事件序列），不在 a11y 是否存在。
- **顺序 = 先做能力，再谈反检**。a11y 的定位 = "**语义定位**"；执行引擎可换。
- **观测归 agent，机制只给方法**（`spec-screen-element-act.md` §8）：动作是否生效是 agent 的语义判断；机制只提供 `capture`（`since_hash`→`changed`、发世代）、`state`、以及"act 消耗世代"；工具侧只做**说明与建议**，不代判、不代观测。

## 四、进度

| 步骤 | 状态 | 产物 |
|---|---|---|
| 1. 客户端动词面 | ✅ 定稿 | `spec-screen-client-api.md` |
| 2. 服务端最小账本 | ✅ 定稿 | `spec-screen-ledger.md` |
| 3. 最小闭环（本机） | ✅ 跑通 | `cogos/screenlab/` |
| 4. 权限语义 | 🔶 部分 | grant/revoke/单操作者/只读位已验；**观察口推流未做** |
| 5. 接入端点 | 🔶 部分 | agent↔agent（ssh 隧道）已验；**关系③a 未验** |
| 6. 装配 | 🔶 部分 | `session-start/stop` 用**用户 bus**；未做"空账户一键" |
| 7. 反检加固 | ⬜ 未开始 | 起步档"对谁隐蔽"= 远端网页（本轮定） |
| 8. a11y 反馈腿（读树） | ✅ 完成 | `service/a11y_helper.py`；`capture mode=tree` |
| **9. 元素动作 `act element`** | ✅ **第一刀（本轮）** | `service/elements.py` + daemon `_act_element`；**agent 工具层尚未暴露（见 §六·遗留 1）** |

## 五、本轮成果：`act element` 第一刀（第八轮）

**语义（`spec-screen-element-act.md`）**：
- **决策 A｜元素引用**：wire 的 `id` 是**服务端签发的不透明串**（`path + 捕获时 role/name/center + 世代`）。act 时**重走 path（忽略裁剪、按原始索引下降）并校验 role/name 一致**（name 空时退化为 role + center 邻近）；**不一致即拒，不尽力点**。引用只在**签发它的那次捕获的世代内**有效。
- **决策 B｜写超时**：a11y 写 helper 被硬 timeout 杀掉 → 回 `unknown`，**绝不重试**（防双点）；无 action / 找不到 / 校验失败 → 明确错误码，可重试。
- **引擎可换**：`element_engine ∈ {auto, do_action, pointer}`（`SCREENLAB_ELEMENT_ENGINE` 或请求字段 `engine`）。`auto` = 先 `do_action`，**无 action 且有 rect** 才降级 `pointer@center`（标 `degraded=true`）；**path 校验失败不降级**。
- **观测定界**：`act` 只回受理结果，**已删除动作后的像素 grab**；要观察由 agent 再 `capture`。

**关键更正（本轮最大的教训）**：曾误判"Chrome 不暴露 AT-SPI action"——**根因是我们调了不存在的 `Accessible.get_action_count()`**（正确 API 是 **`get_n_actions()`**），异常被 `except` 吞掉 ⇒ 每个节点都误报"无 action"，`do_action` 根本没被触达。修复后：Chrome 树 **215/286 节点有 action**，且 **`do_action` 真会触发**（网页 `<button>` 暴露 `['press','showContextMenu']`，`engine=do_action` 选中 `press` 后页面 JS 执行，标题 DA0→DA1，`degraded=false`）。

**改动**（`cogos/screenlab/`，已提交 `bab728e`；10 files, +838/-19）：
- `service/elements.py`（新）：不透明引用 encode/decode、`ref_matches`、`pick_action`（偏好序 `click/activate/press/dodefault/jump`）、`attach_refs`。**纯逻辑，绝不 import gi**。
- `service/a11y_helper.py`：新增 `--act` 写模式（重走 path → 校验 → `do_action`）；**`_actions` 改用 `get_n_actions`**。
- `service/backends.py`：`A11yTree.act()`（子进程 + 硬 timeout；超时/无输出 → `unknown, retryable=false`）。
- `service/daemon.py`：`capture` 给每个节点签 `id`；`_act_element`（引擎可换 + 校验拒绝）；`_dispatch_act` 带世代参数；**删除 act 后置 grab**；`handle()` 捕获 `elements.ElementError`。
- `service/cli.py`：`act element --element-id --element-action --element-engine`。
- `tests/screenlab/test_elements.py`、`test_a11y_act.py`（新，纯逻辑 + 假树 do_action 分支）。
- `tests/screenlab/e2e/`（新，`act_element_e2e.py` + `README.md`，本轮把 e2e 入库）。
- `tests/agent/test_screen.py`：**修复上一轮遗留的 7 个陈旧失败**（`platform_backends.pick` 改 4 元组、账本要求先 `open`、`act` 不再回 `hint`）。

**验证（本机 agent1，全过）**：
- 全仓 `python3.11 -m pytest tests` → **1230 passed, 4 skipped**；`tests/screenlab` → 32 passed。
- e2e（`tests/screenlab/e2e/act_element_e2e.py`）→ **all checks passed**：语义定位网页按钮 → `do_action` 生效（标题 E2E0→E2E1）；篡改引用 → `path_mismatch` 且**无副作用**；跨世代 → `stale_ref`；强制 `pointer` → 点到元素中心。

## 六、遗留 / 候选方向（**均由 YZ 定，不是待办清单**）

1. **agent 工具层暴露树 + element id（最直接，能力还没对 agent 可达）**：`cogos/agent/tools.py` 的 `screen_capture` 只回图片/窗口（**不返回树**），`screen_act` 虽支持 `op="element"` 但 agent **拿不到 `id`**。要做 `act element`，得先在工具层把树（含 `id`）露给 agent，并想清 `screen_capture` 默认要不要带树。
2. **树裁剪调优**：本轮"有 action"也算保留条件后，树由 194 → **286 节点**（默认上限 `max_nodes=400`）。真实网页必然 `truncated=true`，目标元素可能不在树里 → 定位失败。与"稳定性"直接相关。
3. **观察口推流**：只读位已通，"喂给人看"的形态（网页 viewer？推流？）没做。
4. **关系③a**：真人在自己机器上装服务、agent 接入——本机只验了 agent↔agent。
5. **世代归账本**：`snapshot_id` 仍是**连接级**，而 `act element` 的引用又绑了世代，世代语义分量在变重。
6. **授权粒度**：只到账户级；会话/窗口级是遗留。
7. **反检档位**：检测方=远端网页已定；加固主项 = 渲染落真 GPU（本机 vmwgfx 弱 GPU）。**a11y 桥是本地可检测指纹**（本轮已定本机痕迹不考虑）；**`do_action` 不产生真实指针事件序列**（有 click、无 `pointerover/move/down`）→ 页面 JS 可区分，这正是"引擎可换"里 `pointer` 的用处。
8. **冷启动约 1 分钟**（会话 + 探活），体感慢。
9. **空账户一键未做**：新增了对 systemd 用户 bus 的依赖（缺 bus 要 `enable-linger` + `start user@<uid>`），装配脚本已含，但没在全新账户上验过。
- ~~验证脚本未入库~~ → **本轮已解决**（`tests/screenlab/e2e/`）。

## 七、本机环境事实（照抄可用）

- 账户：`agent1`(uid 1003)、`agent2`(uid 1004)；`zhengyp`(1000，sudo)、`tangyu`(1001)、`alice`(1002)。sudo 密码：`~/.secrets/centos.key`（喂 stdin）。
- **会话 bus**：`unix:path=/run/user/<uid>/bus`（systemd 用户 dbus-broker）。`gnome-shell` 与 `screenlab` daemon 都在它上面。
- socket：`/run/user/<uid>/screenlab.sock`；本轮 display 为 `:6`；xauth 为 `/run/user/<uid>/.mutter-Xwaylandauth.*`（文件名随会话变，用 `ls -t` 取最新）。
- a11y bus：由 launcher 拉起的 dbus-broker；`gsettings set … toolkit-accessibility true` 已设。
- 依赖：`python3`(3.9，**Pillow + PyGObject/Atspi**)、`python3.11`(**无 gi、无 Pillow**，但**有 pytest**)；`gnome-shell 40.10`、`xdotool`、`gst-launch-1.0`、`xauth`、`pipewire`（按需）、`google-chrome`（唯一现成 GUI 应用）。**`xdpyinfo`/`xwd`/ImageMagick 没装。**
- agent2 → agent1 已配免密：`ssh -o BatchMode=yes agent1@localhost`；跨账户接入用 streamlocal 隧道：
  `ssh -N -L 9911:/run/user/1003/screenlab.sock agent1@localhost`

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
... grant --bits capture,input --ttl 60 [--once]      # 输出 token
... revoke --credential <token>

# 只重启 daemon（比重启会话轻；--restart 会重起 gnome-shell）
sudo bash -c 'pkill -u agent1 -f "screenlab.service.cli daemon"; sleep 1; \
  runuser -u agent1 -- env HOME=/home/agent1 XDG_RUNTIME_DIR=/run/user/1003 DISPLAY=:6 \
  XAUTHORITY=$(ls -t /run/user/1003/.mutter-Xwaylandauth.* | head -1) \
  DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1003/bus PYTHONPATH=/home/agent1/.local/share \
  setsid python3 -m screenlab.service.cli daemon --display :6 \
  --xauth $(ls -t /run/user/1003/.mutter-Xwaylandauth.* | head -1) \
  --socket /run/user/1003/screenlab.sock --blob-dir /home/agent1/.local/share/screenlab/blobs \
  --account agent1 >>/home/agent1/.local/share/screenlab/daemon.log 2>&1 </dev/null &'

# 会话里起 chrome（a11y 要 force-renderer-accessibility）
runuser -u agent1 -- env HOME=/home/agent1 XDG_RUNTIME_DIR=/run/user/1003 DISPLAY=:6 \
  XAUTHORITY=$(ls -t /run/user/1003/.mutter-Xwaylandauth.* | head -1) \
  DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1003/bus \
  google-chrome --force-renderer-accessibility --no-first-run --no-default-browser-check \
  --user-data-dir=/home/agent1/.config/chrome-a11y --disable-dev-shm-usage about:blank &

# 单测（必须走 3.11，见坑 #9）
python3.11 -m pytest tests/screenlab -q          # → 32 passed
python3.11 -m pytest tests -q                    # → 1230 passed, 4 skipped

# e2e（需要会话 + chrome；以 socket 属主身份跑）
runuser -u agent1 -- env PYTHONPATH=/home/agent1/.local/share python3 \
  cogos/tests/screenlab/e2e/act_element_e2e.py --sock /run/user/1003/screenlab.sock
```

## 八、已知坑（都踩过，别再踩）

1. **私有 `dbus-run-session` 下 a11y 必死**：`org.a11y.Bus.GetAddress` 挂死，树永远空。会话必须跑在**账户自己的 systemd 用户 bus** 上。
2. **helper 的 `DISPLAY` 必须是会话那个**：继承到 ssh 转发的 `localhost:10.0` 会挂死。daemon 传 `DISPLAY`/`XAUTHORITY`。
3. **`Atspi.Accessible` 没有 `get_action_count`**（本轮根因）：正确 API 是 **`get_n_actions()`**。用错会被 `except` 静默吞掉 ⇒ **全树误报"无 action"**，且看不出错。取 action 名用 `get_action_name(i)`，触发用 `do_action(i)`。
4. **`pgrep -x` 对超 15 字符的进程名失效**：用 `pgrep -f`（放脚本文件里，避免 `-f` 自伤）。
5. **Pillow `ImageGrab` 在 Xwayland root 上取帧失败** → 用 `gst ximagesrc`（`pick_capture` 探测式）。
6. **由 root 启动会话必须带 `HOME / XDG_RUNTIME_DIR / USER / LOGNAME`**，否则 gnome-shell 用 root 的 home → **X server 假死**。
7. **`xdotool` 在假死 display 上无限阻塞** → 探活一律 `timeout -s KILL 3`；helper 靠硬 timeout。
8. **`set -e` + `pipefail`**：`ls` 取不存在的 auth 文件会直接退出脚本 → 用 `{ ... || true; } | head`。
9. **pytest 直跑绑 py3.9**（`Path | None` 报错）→ 用 `python3.11 -m pytest`。
10. `pkill -f`/`pgrep -f` 会**自伤**（匹配到自己命令行）→ 放进脚本文件，或按 PID。
11. **别把"起 daemon"和别的命令塞进同一个 `bash -c`**：`setsid` 起 daemon 会导致 logind 把该 shell 的会话判死（现象：`会话已终止，正在杀死 shell`）。起 daemon 单独一条命令，或直接用 `session-start.sh`。
12. a11y 的**裁剪策略是经验值**（KEEP_ROLES / 深度 / 数量）：大树会被截断，`truncated=true` 时节点不全。**本轮后带 action 的节点都保留，树更大（286），真实网页更易截断**（见 §六·2）。
13. 旧路线残留：root 的 `Xvfb :99` + `/opt/screenlab`（旧 systemd 原型）仍在跑，**与新路线无关**，是否退役待 YZ。
14. 机器上有一个**较早遗留的 `runuser -u agent1 … python3 -` 进程**（约 02:07 起，读 stdin 挂住），与本路线无关，未清理。

## 九、纪律（沿用，实测有效）

- **双栏**：每条陈述标 `[目标]` / `[方案]`；**只有 `[目标]` 有否决权**。
- **目标段禁实现名词**；**方案段必须挂账**（满足目标的哪一条 + 代价）。
- **反证句自检**：说"因为已验/已定案/以前这么做"就暂停。
- **作废即删名**：`热订阅` / `关闭重开` / `"形态（全桌面 vs 最小 X）"作选项` / `Xvfb 作起步形态` / `网络/NAT/打洞`。
- **观测归 agent**：机制不代判动作生效；只给方法（`capture`/`state`/世代）。
- 开工起 **10–15 分钟闹钟**；用 `terminal_exec`（非阻塞），**不要 sleep 轮询**；到点先落结论再继续。
- 一次只跑一条实验命令；sudo 密码只喂 stdin（`< ~/.secrets/centos.key`）。
