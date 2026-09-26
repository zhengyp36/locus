# handoff｜交接给新会话 · 2026-09-23 #35

> 接 #34。上一会话做了三件事：**诊断并修好靶机崩溃**（非 screenlab 问题）→ **Act 1 演示**（图形面能力全跑通）→ 把**图形面的生命周期 / 命令层**从目标推出一套结论，记入 `issue-screen-surface-lifecycle.md`。
> **本轮未落码**；下一步由新会话动手改。
> 上下文见 `screen-goal1-progress.md` §3/§5。

## 给新会话的第一句话

> 先读 **`issue-screen-surface-lifecycle.md`**（本轮核心：C1–C12 + L1 + 未定清单）＋ **`spec-screen-1.md` §0.0**（**目标，唯一约束**）。
> **结论已定，不要再讨论**——本轮只剩："**做** C1–C12 / B1–B2、**量**三项形态小项、**搁** L1"。
> 目标机 `surface-centos-9`（100.100.137.78）在跑，账户 `alice/john/Lyli/alice1/john1/Lyli1`；**`alice` 现在是 `:16` / 1920x1080**（不是 `:10`）。
> 本阶段人工在旁、**不起 timer**；每完成一步 `tools/feishu_notify.py` 通知 YZ。

## 本轮结论（一句话）

图形面从目标推出：**面=能力、授权=门票**；**生命周期随通道**（open 即拉、最后 close 即关，不常驻、按需）；**WM/应用/窗口语义做命令**（新 `surface` 面），**协议只留手眼**；反检测口径 = **与真人 VBox 齐平、不引真 GPU**。

## 要做的（照 `issue-screen-surface-lifecycle.md` 执行）

**做（改动）**
- `C1/C2/C5`：会话面 = 开一个程序、按需开/关；`close` 停**整套**面；通道**引用计数 + grace**，拆机器靠 systemd（socket activation + `StopWhenUnneeded` 候选）；`add-agent` **不预起面**（C9）。
- `C3`：`close --destroy` **保留 resolution**（挪到随 destroy 保留的状态文件）。
- `C4`：**删协议 op `paste`**（`proto/protocol.py` `ACT_OPS`）；剪贴板改命令。
- `C6/C7/C8`：新增命令面 `surface run|windows|focus|close|clip`——自己读 `~/.config/screenlab/session.env`、**不暴露 `:N`**、`run` **detach（禁 `exec`/`&`）**；`--help` 标所属面与授权。运维留 `screenlab`（管理面），`view` 归观察面。
- `B1`：`open --restart` **复用** `session.env` 的 display（现会重分配，见下坑）。
- `B2`：`tool_loop_e2e` 去硬编码 `1920x1080`，从 capture 的 `w/h` 推。

**量（一次，几分钟，量完 ④ 才真闭合）**
Xvfb 下 Chrome 的：**WebGL 可用性**、`screen.w/h` + DPR、**字体集**。

**搁（不阻塞）**
`L1` 行为保真（鼠标轨迹/节奏）——归 agent 操作层；**机制前置**：现模型一次 `act` **消耗 generation**（`screenlab/service/daemon.py:256/263` `st.void()`）→ 连续位移发不出；要落地得先改机制（多 act 共享一次 capture / 新增 `move`|`drag`）。`pointer` 用 `clicks=0` 支持纯移动（`backends.py:328`）。

**清账 / 流程（不用讨论）**
`spec-screen-1.md` §10 逐条标"已定/仍开/作废"；§7 Phase 2 持久形态更新（"无认证"已由**账户级 socket 权限**解决）；`design-screen-system.md` §9；打 tag；`cogos/docs/design-agent-tools.md` §16 回写。

## 靶机与坑（重要）

- **sudo**：`cat ~/.secrets/centos.key | ssh zhengyp@100.100.137.78 'sudo -S -p "" bash -c "…"'`。**同一 ssh 里二次 sudo 拿不到密码**——多个 root 命令包在**一个** `bash -c` 里，账户侧用 `runuser -u <acct>`。
- **账户/面现状**：`alice` 1001 `:16` 1920x1080（重启后换的，见 B1）；`john` 1002 `:11` 1920x1280；`Lyli` 1003 `:12` 1280x720（被 destroy 重开后丢了原 1366x768，即 C3）；`alice1` 1004 `:13`；`john1` 1005 `:14`；`Lyli1` 1006 `:15`。`linger=yes`，重启自愈。
- **本轮演示跑过的准备**：靶机 `python3.11` 已 `pip install pyte aiohttp`（系统级）；`chmod -R a+rX /tmp/cogos-src`。`/tmp/cogos-src` 是源码**副本**，跑 e2e 前先 `rsync` 本机 `../cogos`（`python3` 是 3.9，**别用**）。
- **e2e**：`runuser -u alice -- env PYTHONPATH=/tmp/cogos-src XDG_RUNTIME_DIR=/run/user/1001 python3.11 /tmp/cogos-src/tests/screenlab/e2e/tool_loop_e2e.py --sock unix:/run/user/1001/screenlab.sock`（1280x720 时 pointer 那项必 FAIL，是 B2）。
- **VM 崩溃史（本轮修过）**：靶机在一次 `add-agent`×3 后**硬挂**、重启卡 dracut。**根因非 screenlab**：宿主 VBox 日志 `AHCI#0: Port reset` + `TM: Giving up catch-up…`（VM 落后墙钟 ~54min），guest 根盘读不出。**修法**：`ssh zhengyp@100.112.50.115 '"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" controlvm centos9 reset'`（取 VM 截图：同目录 `controlvm centos9 screenshotpng C:\Users\zhengyp\cap.png`）。
- **既有噪声**：`vboxclient.service` 无限重启（`VBoxDRMClient: VERR_INVALID_HANDLE`）→ 内核 `remove_proc_entry … leaking 'irq/20' … 'vboxguest'` WARNING，**自 13:16 起就有**，与 screenlab 无关，别当成回归。
- **靶机 `/opt/screenlab` 保留**（机器级包，无 `uninstall-machine`）；本机 `../cogos` @ `feat/screenlab-p2` **干净**（`14fca90`，已推送）——**本轮没改代码**。
- Act 1 证据在本机 `/tmp/kilo/demo/`（`act1-*.png`、`vm*.png`）。

## 入口

- **本轮核心（先读）**：`checkpoint/issue-screen-surface-lifecycle.md`
- 目标（唯一约束）：`spec-screen-1.md` §0.0
- 体系工作稿：`design-screen-system.md`；契约：`../cogos/screenlab/install/session-create.md`
- 代码：`../cogos` @ `feat/screenlab-p2`（`14fca90`）：`screenlab/{proto,service,viewer,install}`、`cogos/agent/impl/graphics.py`、`cogos/agent/tools.py`
- 上一轮：#34 `handoff-screen-34.md`；进度：`screen-goal1-progress.md`
