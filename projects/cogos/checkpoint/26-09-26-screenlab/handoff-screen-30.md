# handoff｜交接给新会话 · 2026-09-23 #30

> 接 #29。本会话把 **Step 2–6 全部做完**（代码只改不提交），靶机跑通自活闭环、跨账户授权 e2e、跨 tailscale 只读 viewer。
> **上下文到 ~157k（≥150k 阈值）→ 按纪律切会话。**

## 给新会话的第一句话
> 先读 `screen-goal1-progress.md`（**滚动状态 = 唯一工作入口**），复述 **§2 步骤表 / §3 当前指针 / §4 待 YZ** 给我核；
> 然后**按 §3 做 Step 7 剩余**：spec 回写、清理靶机/后台进程、打 tag —— **tag 时机先跟 YZ 确认**（§4）。
> **开工前 `set_timer` 10 分钟**；到点跑 `python3 tools/ctx.py`，对照 §3 看是否偏离、是否 ≥150k。
> 别重新发现环境——锚点都在 progress §1。

## 本轮结论（一句话）
- **Goal 1 的六步全绿并已提交推送**：取帧收敛为 Pillow 单后端；X11 版会话脚本（删 Xvfb）；靶机 `:0` `capture→act→capture` 闭环；跨账户 `grant/revoke` e2e 10/10；viewer 默认只读 + 跨 tailscale 实测。

## 本轮已完成（对应 progress §2）
- **Step 2**：`service/backends.py` `pick_capture` 去掉四后端探测，默认唯一 = `PillowCapture`；`windows`/`x11-windows`/`gst`/`import` 降为 `SCREENLAB_CAPTURE` 显式 override。
- **Step 3**：`install/session-start.sh` 改 X11 版（定位账户既有桌面 `:0` + `$RT/gdm/Xauthority`，限时探测，不再起 headless 合成器 / 不探 cookie）；`session-stop.sh` 只停服务；**删** `install/xvfb-start.sh` + `screenlab-xvfb.service`，`install.sh`/`screenlab.service`/`uninstall.sh` 同步去除 Xvfb 路线与 `--resolution`。
- **Step 4**：靶机 `:0` 自活闭环跑通（`act pointer` 归一化坐标 + `type` + `key Return`，第二帧 `changed`，终端回显）；前置 = 分辨率钉 1920x1080、keyring 空密码、屏保锁关。
- **Step 5**：靶机建 **agent2**（uid 1002）+ agent2→agent1 免密；agent2 经 **streamlocal 隧道**接入 agent1 服务，`guest_intervention_e2e.py` **10/10**。
- **Step 6**：`viewer/bridge.py` 默认 **read-only**（只 `/frame` + `/status`，`/act`→403；`--allow-act` 才可操作），`page.html` 同步；本机跨 tailscale 起桥实测。

## 本轮提交（`../cogos`，分支 `feat/screenlab-p2`，**已推送**）
- `d840ccd` refactor(screenlab): settle on the plain X11 form
  （`service/backends.py`、`service/platform_backends.py`、`install/`：session-start/stop、install.sh、screenlab.service、uninstall.sh；删 `xvfb-start.sh`、`screenlab-xvfb.service`）
- `c23dab3` feat(screenlab): make the viewer read-only by default
  （`viewer/bridge.py`、`viewer/page.html`、`tests/screenlab/test_viewer.py`）
- 自检阶段另修 4 处小疵（docstring、`install.sh`/`session-start.sh` 的 `set -e` 边界、platform 文案）。

## Step 7 剩余（新会话做）
1. spec 回写（`cogos/docs/design-agent-tools.md`，账本稿 §3 提到过）。
2. 清理：靶机 `~/cogos`、`/tmp/slrun`、`~/chrome.log` 等临时物；后台隧道 + viewer 进程随会话结束即停。
3. **打 tag**（时机/名待 YZ）。

## 工作纪律（务必执行）
1. **每个动作前** `set_timer` 10 分钟；到点三件事：① `python3 tools/ctx.py`；② 对照 progress §3 判断是否偏离；③ **上下文 ≥150k（≈15%）或路径偏 → 就地更新 progress + 写新 handoff + `tools/feishu_notify.py` 通知 YZ 切会话**。
2. **每完成一步**就地更新 `screen-goal1-progress.md`，§6 记一行；随后 `tools/feishu_notify.py` 通知 YZ，**若无须 YZ 介入则直接继续下一步**。
3. **边界**：改代码/操作测试机 = 我做；**提交/推送/tag、动 zhengyp/本机、改目标 = YZ 定**；判据失败 → 停下报结论。
4. 自检命令在 `../locus` 跑：`python3 tools/ctx.py`。

## 入口
- **滚动状态（先读）**：`checkpoint/screen-goal1-progress.md`（§1 锚点含靶机部署/隧道/viewer 起法）
- 环境细节：#28 `checkpoint/handoff-screen-28.md`
- 规格：#1 `spec-screen-1.md`；账本 `spec-screen-ledger.md`；客户 API `spec-screen-client-api.md`
- 代码：`../cogos/screenlab` @ `c23dab3`（分支 `feat/screenlab-p2`，已推送）
