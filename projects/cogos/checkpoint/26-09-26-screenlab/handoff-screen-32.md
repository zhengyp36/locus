# handoff｜交接给新会话 · 2026-09-23 #32

> 接 #31。本会话把 **Goal 1 收口**：多账户缺口用「每账户自管 Xvfb」补上，落成 **create 模式**，靶机双账户全绿。
> **上下文 ≈147k/1M（15%）逼近 150k 阈值 + 本轮工作已收口 → 按纪律切会话。**

## 给新会话的第一句话
> 先读 `screen-goal1-progress.md`（**滚动状态 = 唯一工作入口**），复述 **§3 当前指针 / §4** 给我核；
> 然后**停下等 YZ 决定提交 / tag**（§4 尾，本轮唯一待办）。
> **别重跑 e2e**——create 模式已验证全绿，直接复用。
> 开工前 `set_timer` 10 分钟；到点跑 `python3 tools/ctx.py`。

## 本轮结论（一句话）
- **Goal 1 已收口**：多账户 = **每账户一块自管 headless Xvfb**（`session-start.sh create`，systemd user unit 组）；形态裁决落定 **Xvfb**；靶机双账户 e2e + 生命周期全绿；**卡在 YZ 决定提交 / tag**。

## 本轮关键判断（YZ 已认可思路）
- **形态裁决**：Xvfb（已验、隔离好、实例无限）**胜出**；Xephyr / VKMS / 多 VM 留作**真 GPU 需求**的备选。
- **GL 不作为裁决项**：真人未开 3D 的 VBox 桌面同样 llvmpipe，浏览器可见面几乎无差、`navigator.webdriver=false`（注入走 XTEST 非 CDP）；登录风险由 IP / 行为主导。
- **剩余 Xvfb 问题 = 会话工程**（DBus / linger / keyring / 自启 / 幂等），换显示服务器并不省这部分 → 落成 systemd user unit 组。

## 本轮已完成（对应 progress §2 步骤 8 / §3）
- **契约 + 模板**：`../cogos/screenlab/install/session-create.md`、`screenlab-session.target`、`screenlab-xvfb.user.service`、`screenlab-desktop.user.service`、`screenlab-daemon.user.service`。
- **代码**：`session-start.sh` 加 `create`（Xvfb + WM + 服务；幂等 / `--restart` / display 自动分配 / linger）；`session-stop.sh` 加 `destroy`（`stop` = 只停服务）；`uninstall.sh` 对称清理；`screenlab-session.target` 补 `[Install]`。
- **e2e 收编**：`run_goal1_xvfb.sh` 改驱动正式 `create`；删 `xvfb_account_prepare.sh` 原型；`README.md` 补节。
- **靶机实测**（surface-centos-9）：双账户 `create` listening（agent1 `:7` 1280x720 / agent2 `:8` 1024x768）；幂等 `already_listening`；自闭环 `changed=True` + 隔离（互访 `No protocol specified`、对方 runtime 不可读）；跨账户隧道 guest `10/10`；viewer 只读 `/frame 200 PNG` + `/status read_only` + `/act 403`；生命周期：stop 只停服务、destroy 清净、kill -9 Xvfb 自愈、`Linger=yes`。证据 `/tmp/kilo/goal1/*.png`。
- **spec 回写**：`spec-screen-1.md` §0.0 / §5.3 / §7（多账户形态 + GL 口径）；`spec-screen-ledger.md` §0（Xvfb 解禁）；`cogos/docs/design-agent-tools.md` §16（图形面，进行中）。

## 本轮踩到的坑
1. `xauth -f <file> add` 在文件不存在时把 "file does not exist" 打到 stderr → 先 `touch` 再 `add` 消除。
2. `/tmp/slrun` 由 root 创建，agent 无 sudo 删不掉 → 留在 `/tmp`（重启即清）。

## 下一步（等 YZ）
1. **提交 / tag**（YZ 定）：`../cogos` 分支 `feat/screenlab-p2`。
2. **靶机现状**：agent1 / agent2 各一个 create 会话在跑（units `enabled`，随 user manager 自启）；`/tmp/slrun` 残留。要清场用 `session-stop.sh <acct> destroy`。
3. 已知不阻塞：真 GPU（目标 3）、Wayland 真人桌面（Goal 2）、授权粒度（ledger §8）。

## 未提交清单（`../cogos` @ `feat/screenlab-p2`）
- M：`docs/design-agent-tools.md`、`screenlab/install/session-start.sh`、`screenlab/install/session-stop.sh`、`screenlab/install/uninstall.sh`、`tests/screenlab/e2e/README.md`
- ??: `screenlab/install/session-create.md`、`screenlab/install/screenlab-{session.target,xvfb.user.service,desktop.user.service,daemon.user.service}`、`tests/screenlab/e2e/{run_goal1_xvfb.sh,xvfb_goal1_e2e.py,xvfb_tunnel.sh}`

## 入口
- **滚动状态（先读）**：`checkpoint/screen-goal1-progress.md`
- 本轮契约：`../cogos/screenlab/install/session-create.md`
- 规格：`spec-screen-1.md`（已回写 §0.0/§5.3/§7）、`spec-screen-ledger.md`、`spec-screen-client-api.md`
- 代码：`../cogos/screenlab` @ `feat/screenlab-p2`（本轮改动**未提交**）
- 上一轮：#31 `handoff-screen-31.md`；环境细节 #28
