# handoff｜交接给新会话 · 2026-09-23 #33

> 接 #32。本轮**转向"体系重建"**：Linux 形态裁决 **授权 = 给账户**，删掉令牌/凭证层，把图形面收成一个体系。
> **上下文 ≈257k/1M（26%）超 200K 阈值 + 本轮已收口 → 按纪律切会话。**

## 给新会话的第一句话

> 先读 `design-screen-system.md`（**滚动状态入口**）＋ `screen-goal1-progress.md` §3/§5，复述给你核；
> 然后**停下等 YZ 裁决第 5 步**：靶机验证需要 `screenlab add-agent` 建账户，而 YZ 此前明确要求"不要创建账户"。
> **别重跑已达成的结论**（服务瘦身 + 统一入口已提交、234 tests 过）。
> 本阶段**不设 timer**，人工在旁；每完成一步 `tools/feishu_notify.py` 通知 YZ。

## 本轮结论（一句话）

- 形态裁决：**授权 = 给账户**（信任前提），软件**不提供令牌/凭证层**；对外只剩一个入口 `screenlab`，三面 = 装配 / 会话 / 观察。代码（服务瘦身 + 统一入口）已提交 `c62916b`。

## 本轮关键判断（YZ 已认可）

- **授权不是软件的事**：Linux 真人世界的两种原型——账户式（ssh/RDP，给账户＝给整机）与协助码式（快速助手/VNC 密码，受限可收回）。**访问 = 账户；限制与收回 = 令牌**。YZ 选前者，后者冻结。
- **看与操作不对称**：操作必须唯一（X 只有一个指针/焦点），观察可以多路 → **多观察者 + 单控制者**，服务内一把输入锁 + 显式 `yield`。
- **viewer = 只读画面流**，人**不拿账户**；机器上只读端口（意向 tailnet），服务端对 observer 通道真拒 `act`。
- **机器级一个包**：代码共享 `/opt/screenlab`，账户只留 `~/.config/screenlab` + 自己的 blobs。

## 本轮已完成

- **提交**：`1a818f1` create 形态存档（上轮遗留）；`c62916b` 体系重建（本轮）。
- **服务瘦身**：`ledger` 三表 → 通道表 + 一把输入锁；channel 带 `role ∈ {observer, controller}`；`daemon/cli/client/protocol/launch` 删 `grant/revoke/redeem`、`authority`、`grant` 字段，`open` 带 role。
- **viewer 只读**：`viewer/bridge.py` 开 observer 通道、**无 `/act`**（POST 405），`page.html` 简化成 frame + status。
- **agent 侧清线**：`cogos/agent/{config,app,impl/terminal,impl/graphics}` 删 `graphics_credential/authority` 接线。
- **统一入口**：`screenlab {install-machine, add-agent, open, close, view}`（`screenlab/install/screenlab`）；`session-start.sh` 收敛为 **create-only** + 支持 `--prefix` 共享前缀；`session-stop.sh` 去 attach 残留；unit 模板指向 `~/.config/screenlab/*.sh`。
- **退休**：`install.sh`、`account-install.sh`、`uninstall.sh`、`screenlab.service`、`screenlab.user.service`（attach/system 时代）；Windows `install.ps1`/`uninstall.ps1` 去掉 `-Authority`/`authority`/`grant`（Windows 线仍挂起）。
- **e2e 收编**：删 `run_goal1_xvfb.sh`、`xvfb_tunnel.sh`、`guest_intervention_e2e.py`；新增 `roles_e2e.py`（观察者/控制者/单操作者）、`account_surface_e2e.py`（原 `xvfb_goal1_e2e.py`，含隔离）；`README.md` 重写。
- **文档**：`design-agent-tools.md` §16 改为指向 `design-screen-system.md`；`spec-screen-ledger.md` 标**作废**；`session-create.md` 契约同步；`screen-goal1-progress.md` §3/§5/§6 更新（阈值 150K→**200K**）。
- **自检**：`bash -n` 全过；`pytest tests/screenlab tests/agent` **234 passed, 3 skipped**；`compileall` 过。

## 本轮踩到的坑

1. **`set -u` + 未设置的 `SCREENLAB_PREFIX`**：session-start.sh 的前缀回退分支引用未设置的变量会直接退出（已修：先存 `REQUESTED_PREFIX`）。
2. **Pillow 的假象**：`import PIL` 曾显示 11.3.0，其实是 zhengyp 的 `pip --user`；**系统 python3 无 Pillow**，账户侧 daemon 起不来。已装系统级 `python3-pillow`（10.0.1）。
3. **包名 ≠ 命令名**：`xauth` 属 `xorg-x11-xauth` 包（命令名与包名不一致，装依赖清单要写对）。
4. **删凭证层会连带删测试**：`guest_intervention_e2e.py` 等绑定旧模型的测试必须一起清，否则 import 就炸。

## 靶机现状（surface-centos-9 / 100.100.137.78）

- **VM 开着**（本轮由 `VBoxManage startvm centos9 --type headless` 启动）；宿主 `ssh zhengyp@100.112.50.115`。
- **账户只剩 `zhengyp`**（agent1/agent2 已按 YZ 要求 `userdel -r`；linger 清空）。
- **依赖已装**：`xorg-x11-server-Xvfb` 1.20.11 / `xdotool` / `xorg-x11-xauth` / `openbox` 3.6.1(EPEL) / `python3-pillow` 10.0.1（系统级）。
- **gdm autologin 已关**（原指向 agent1）；gdm 停在 greeter，`Xorg :0` 由 gdm 持有，create 用 `:10+` 不冲突。
- **残留**：靶机 `/tmp/step1_cleanup.sh`（本轮清理脚本，可删）；本机 `/tmp/kilo/step1_cleanup.sh`。
- sudo：靶机 zhengyp 无本地 key，用本机 `cat ~/.secrets/centos.key | ssh zhengyp@… 'sudo -S -p "" <cmd>'`。

## 下一步（待 YZ / 待做）

1. **【待 YZ 裁决】第 5 步靶机验证**：需要 `screenlab add-agent` 建账户（YZ 此前要求不建账户）。两条路——授权我建（顺带验证 `add-agent`），或 YZ 手工建后我只跑 `open`/验证。
2. **验证内容**（`design-screen-system.md` §10 步 5）：新设备 `install-machine` → `add-agent` → `open` → 自用闭环 → 同账户两连接（一观察一控制）→ `view` 只读；证据建议 `/tmp/kilo/sys/*.png`。
3. **第 6 步文档**：`spec-screen-1.md` §0.0 关系 2 改写（"显式可收回的授权"→"授权=给账户"）；`spec-screen-client-api.md` guest/credentials 部分标作废。
4. 未并入的裁决：反检测强度、真 GPU、Wayland 真人桌面。
5. 上轮遗留的 tag：仍由 YZ 定（`feat/screenlab-p2`）。

## 入口

- **滚动状态（先读）**：`checkpoint/design-screen-system.md`
- 进度：`checkpoint/screen-goal1-progress.md`（§2 步骤表、§3 指针、§5 纪律）
- 旧目标：`spec-screen-1.md` §0.0；协议：`spec-screen-1.md` §1
- 代码：`../cogos` @ `feat/screenlab-p2`（本轮已提交：`1a818f1`、`c62916b`）
- 契约：`../cogos/screenlab/install/session-create.md`
- 上一轮：#32 `handoff-screen-32.md`；环境细节 #28
