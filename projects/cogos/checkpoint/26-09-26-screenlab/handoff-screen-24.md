# handoff｜交接：搭建人侧 viewer（第十一轮）· 2026-09-22 #24

> ➡️ 接续 `handoff-screen-23.md`（第十轮）。新会话从 #24 读起。
>
> **新会话只读四样，别多读**：
> 1. **目标（唯一约束）**：`handoff-screen-18.md` **§5.1**。
> 2. **本路线方案**：`handoff-screen-18.md` **§5.2 / §5.3 / 六 / 七**；`rationale-screen-a11y-drop.md`；两个 spec：`spec-screen-client-api.md`（动词面，**已含本轮 `yield` 与 §4·15 修订**）、`spec-screen-ledger.md`（服务端账本）。
> 3. **读法纪律**：`handoff-screen-18.md` **§5.0**（双栏 + 反证句 + 作废即删名）。
> 4. **代码**：`cogos/screenlab/` + `cogos/agent/{tools.py, impl/graphics.py}`（分支 `feat/screenlab-p2`；**本轮改动未提交**，见 §三）。
>
> ⚠️ `spec-screen-element-act.md` **整份作废**；别读 `handoff-15/16` 的目标与架构表述；别用 `screenlab/install/install.sh` 与 `*.service`、`xvfb-start.sh`（旧 Xvfb/systemd 路线，已废；机器上 root 的 `Xvfb :99` + `/opt/screenlab` 仍在跑，与新路线无关）。
> ⚠️ a11y 已在 #23 整体剥离；#22 §三/§四/§五·1·3·4 关于"树 = 可选语义索引"的口径**已推翻，别沿用**。

## 一、目标（摘要，以 §5.1 为准）

每 agent 有若干账户（账户是归属单位）；账户有一块**可操作的图形界面**，发动作能读回结果；操作要**像真人、不被检测**（逐步加固）；默认**不抢物理屏**，需要时人能看到/介入；三种关系 = 自用 / 授权他 agent（显式可收回）/ 与真人双向；**一账户同一时刻一块界面，"要"是幂等的**；**agent 只面对客户端**。

## 二、本轮（第十轮）做了什么 · 2026-09-22

**判定：owner / guest 只是一个区别**——一个账户 = 一个服务 = 一块界面（幂等）= **一个 owner + N 个 guest**；owner = 传输已认证的长期身份，guest = 凭证换出的通道。**人一律是 guest**（`{看}` = 观察，`{看,操作}` = 介入），人从不映射成 owner。四种关系（①自用 / ②agent↔agent / ③a agent 接人的机 / ③b 人看 agent 机）只是"谁持 owner"的排列。

**为此新增第 8 个动词 `yield`**（持有输入者让位、保留通道）：guest 不能从 owner 手里抢输入，须由 owner 显式让位；owner 下次 `act` 自动抢占取回。作废"人一动手即夺回输入"（该句只在 **人 = owner** 即 ③a 时成立）。

**修好 pixels（本轮最大工程件）**：mutter 把 X11 窗口重定向，抓 Xwayland **root 只有黑底+指针**；抓**窗口 xid** 正常。新增取帧后端 `x11-windows`：`libX11`(ctypes) 走 `XQueryTree`（序即 z 序）+ `XGetWindowAttributes` + `XTranslateCoordinates`，逐窗 `gst ximagesrc xid=` 抓图合成到逻辑屏画布。`pick_capture` 在 X11 上默认优先它。

**代码（`feat/screenlab-p2`，未提交）**：
- `screenlab/service/backends.py` — 新增 `X11CompositeCapture`（name `x11-windows`）+ `pick_capture` 默认优先 windows
- `screenlab/service/daemon.py` — `op_yield` + 注册 + 模块头动词表
- `screenlab/proto/client.py` — `yield_input()`（wire 动词 `yield`；`yield` 是 Python 关键字）
- `tests/screenlab/test_ledger.py` — owner 让位 → guest 接 → owner 自动取回
- `tests/screenlab/e2e/guest_intervention_e2e.py` — **新** live 校验（10 步，见 §五）
- `tests/screenlab/e2e/README.md`
- `checkpoint/spec-screen-client-api.md` — 修订横幅 + `yield` 行 + §4·15 + §6
- 另有**上轮遗留未提交**：`screenlab/install/install.ps1`（Windows 端口选择，非本轮）

## 三、当前 Linux 状态（已齐）

- **目标 2 闭环**：`capture`（pixels / crop / `changed`+`since_hash` / `wait_stable` / blob→文件→路径）+ `act`（pointer/key/type/paste/scroll）；工具层 `screen_capture`/`screen_act` 走通。
- **目标 5/6 骨架**：`open/close/grant/revoke` + **`yield`**、per-account ledger、通道可多条、位（capture/input）、ttl/once/revoke。
- **owner/guest 模型**：见 §二；`take_input` 的抢占只给 owner。
- **目标 7**：客户端不露 `snapshot_id`/`frame_hash`；工具面已收敛成图/pointer。
- **目标 4 的一半**：默认 `gnome-shell --headless --virtual-monitor`，不抢物理屏。
- **pixels**：`x11-windows` 合成后端，能真看到 X11 窗口内容（Wayland 原生 app 看不到，与 XTEST 输入边界一致）。
- **装配**：account-install / session-start / session-stop，幂等，账户自己的 systemd user bus。
- **验证**：`python3.11 -m pytest tests -q` → **1209 passed, 4 skipped**；`tool_loop_e2e` **7/7**；`guest_intervention_e2e` **10/10**。

## 四、本轮任务：搭人侧 viewer（让 YZ 验收"看 + 操作"）

**要交付的东西**：一个**人侧的"显示屏"**——YZ 能在自己浏览器里**看 agent 操作 agent1 的屏**，并且**能自己操作**。这就是关系③b + 介入的端到端验收（目标 4 后半 + 目标 5 关系③）。

**已定的形态（`[方案]`，可换）**：
- **小网页 + stdlib HTTP 桥**：桥进程用 `http.server`，跑在**能连到 daemon 的一侧**（agent1 socket 可达处）；YZ 用浏览器经隧道打开它。**不放 GUI 工具包**（本机 `python3.11` 无 tkinter）。
- **下行**：`GET /frame` → `capture(since_hash=上次)` → 返回 PNG；页面轮询渲染（spec 起步不做推送）。
- **上行**：页面鼠标/键盘 → 归一化坐标 → `POST /act` → `act(pointer/key/type/scroll, snapshot_id=当前帧)`。
- **凭证**：桥以 **guest** 身份 `open(credential=<token>)`（token 由 owner 发、在对话里递）。观察位 `{看}`、介入位 `{看,操作}` 都走同一桥。
- **让位/取回**：agent（owner）持输入时人的 `act` 会 `input_taken`；owner **`yield`** 后人才能操作；人停手，owner 下次 `act` **自动取回**（人不需要自己让位）。桥要显示 `state.input_holder`，并在被拒时提示"agent 正在操作"。
- **硬约束**：`act` 必须带**当前帧的 `snapshot_id`**（连接级世代，D11）；所以"看"和"操作"天然是**同一个循环**——每次先 `capture` 拿帧与世代，再用它发 `act`。

**前置缺口（viewer 要好用必须先补，`[方案]`）**：`pointer` 目前只有"点"（`button`+`clicks`，`daemon.py` 的 `_dispatch_act`），**没有 move/press/release** ⇒ 拖动（选字/拖窗/拖滑块）做不了。要么先给 `act` 补拖动，要么接受 click-only。

**验收流程（YZ 要的终验）**：
1. 我当 agent，agent1 owner，开程序并操作（`screen_capture`/`screen_act`）。
2. 我发一张一次性 `{看,操作}` 凭证，起 viewer 桥，把 URL 给 YZ。
3. YZ 开页面 → 看到我的画面随我操作更新。
4. YZ 点/打字 → 我 `yield` → YZ 的操作落到屏上 → YZ 停手 → 我下次 `act` 自动取回。
5. 我 `revoke` → YZ 页面立刻失效。
**判据**：步骤 3–5 都成立；轨迹与"人操作真实桌面的手感一致"（拖动取决于是否补了 pointer）。

**素材**：`tests/screenlab/e2e/guest_intervention_e2e.py`（guest 接入 + 让位序列，直接照抄）；`/tmp/kilo/composite_proto.py`（合成原型，可选参考）。

## 五、缺口清单（**待 YZ 讨论定方向**，不是待办）

**A. 实质（对着目标）**
1. **人侧 viewer 未做** ← **本轮任务**。
2. **目标 3 加固一点没做**（真 GPU 渲染、时序/拟真）。**Linux 上最大缺口**。
3. **真人侧接入（③a）没验**：本机只验了 agent↔agent / 人=guest。真人在自己机器装服务、agent 接入没走过。

**B. 图主干**
4. `pointer` **无拖动**（move/press/release）；viewer 前置候选。
5. `act` 收**上一次 crop 帧内**坐标、`capture(mark=x,y)` 出带标记局部图（#22 §三·6）。
6. `x11-windows` 看不到 **Wayland 原生 app**；要盖 Wayland 需 portal ScreenCast（接口/pipewire 都在，但 headless 下请求等不到 Response，需啃授权）。

**C. 工程收尾**
7. blob 目录**无 GC**；`_geometry` 缓存不随分辨率失效。
8. 授权粒度只到账户级；冷启动 ~1 分钟；空账户一键未做。
9. 旧路线残留未退役（root 的 `Xvfb :99` + `/opt/screenlab`）。

## 六、环境 & 常用命令

**环境事实见 `handoff-screen-22.md` §七/§八**（socket/display/xauth/跨身份姿势、已知坑 14 条，契约未变）；其中 **daemon pid / display 号以现测为准**。

```bash
# 部署本轮代码（改了 screenlab/ 就要做，否则 daemon 还是旧包）
pkill -u agent1 -f "screenlab.service.cli daemon"; sleep 2
sudo bash cogos/screenlab/install/account-install.sh agent1
sudo bash cogos/screenlab/install/session-start.sh agent1     # 需要时 --restart

# 现测环境（本轮实测）：socket /run/user/1003/screenlab.sock，display :6，
#   xauth /run/user/1003/.mutter-Xwaylandauth.N9TAW3，account agent1，
#   capture_backend x11-windows，act_backend xdotool，pid 42298（以现测为准）

# 客户端（owner = 不带凭证；guest = 带 token）
sudo -u agent1 env PYTHONPATH=/home/agent1/.local/share python3 \
  -m screenlab.service.cli --socket /run/user/1003/screenlab.sock open
#   ... capture [--center X,Y] [--size W,H] | act pointer --x 0.25 --y 0.35
#   ... grant --bits capture,input --ttl 60 [--once] / revoke --credential <token> / yield

# 单测（必须 3.11）
python3.11 -m pytest tests/screenlab -q
python3.11 -m pytest tests -q          # → 1209 passed, 4 skipped

# e2e（客户端闭环；见 tests/screenlab/e2e/README.md）
sudo env PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPATH=/home/zhengyp/work/A/cogos:/home/zhengyp/.local/lib/python3.11/site-packages \
  /usr/bin/python3.11 tests/screenlab/e2e/tool_loop_e2e.py --sock unix:/run/user/1003/screenlab.sock
sudo env PYTHONPATH=/home/zhengyp/work/A/cogos \
  python3.11 tests/screenlab/e2e/guest_intervention_e2e.py --sock /run/user/1003/screenlab.sock
```

## 七、纪律（沿用 #22 §九，实测有效）

- **双栏**：每条陈述标 `[目标]` / `[方案]`；**只有 `[目标]` 有否决权**。
- **目标段禁实现名词**；**方案段必须挂账**（满足目标的哪一条 + 代价）。
- **反证句自检**：说"因为已验/已定案/以前这么做"就暂停。
- **机制不代判**：不代判动作生效，也不代判"看什么"。
- **作废即删名**：`热订阅` / `关闭重开` / `"形态"作选项` / `Xvfb 作起步形态` / `网络/NAT/打洞` / `a11y` / `元素表` / `act element` / **`人一动手即夺回输入`（仅 ③a 成立）**。
- 开工起 **10–15 分钟闹钟**；用 `terminal_exec`（非阻塞），**不要 sleep 轮询**；到点先落结论再继续。
- 一次只跑一条实验命令；**sudo 密码只喂 stdin**（`< ~/.secrets/centos.key`），**注意重定向位置**（写到管道/`head` 末尾会把密码喂错对象并打印出来）。
- 改了 `screenlab/` 的代码必须**重新 account-install + 重启 daemon**，否则跑的是旧包（`PYTHONPATH=/home/agent1/.local/share`）。
