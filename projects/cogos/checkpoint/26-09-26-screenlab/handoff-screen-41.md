# handoff｜交接给新会话 · 2026-09-24 #41

> 接 #40。本会话 = **X11 闸门实验（三闸门全跑）+ 续做（修 G2、退场/剪贴板验证）**；产出 **`screen-assist-exp-log.md`**（本会话唯一新文档）。
> **规则 / 环境操作不在这里**——见 **`screenlab-rules.md`**（稳定参考，先读）。

## 给新会话的第一句话

> 先读 **`screenlab-rules.md`**（规则+环境）→ 本文件（状态/下一步）→ **`design-screen-assist.md`**（§0 边界 / §2 流程 / §4 环节 / §7 靶场 / §8 规则）→ **`spec-screen-1.md` §0.0**（唯一约束）→ **`screen-assist-exp-log.md`**（本会话实验全记录，含缺口 G1–G4）。
> **本会话把 #40 定的 X11 闸门三实验全跑完**，机制通；下一步 = **YZ 裁决 G1/G3/G4**（见下）。
> 本线**从 X11 起，Wayland 先不做**。
> 靶机 `surface-centos-9`（100.100.137.78）；宿主 VBox（Windows）`zhengyp@100.112.50.115`，`VBoxManage.exe` 在 `C:\Program Files\Oracle\VirtualBox\`（PATH 里没有）。
> 代码 `../cogos` @ `feat/screenlab-p2`（tag `screenlab-goal1-2026-09-24`）。⚠️ **工作区已有一处未提交改动**：`screenlab/install/surface`（G2 修复）。

## 本会话已做

- **环境**：靶机按 §7 建**真实 XFCE/X11 桌面**——专用账户 `human`(uid 1002，密码 `human123`) + `XSession=xfce` + GDM autologin，`systemctl restart gdm`（**未 reboot**）。桌面在 `:0`，`XAUTHORITY=/run/user/1002/gdm/Xauthority`，1920x1093。
- **三闸门**（详见 `screen-assist-exp-log.md`）：
  - **① 附着真实会话**：capture 与 `import -window root` **逐像素相同**；`surface run` / 协议 `act key` 闭环通；停 daemon 后真人桌面完好。
  - **② 物理/注入分源**：VBox `keyboardputscancode` → `/dev/input/event2` 出 8 个 `EV_KEY`；`xdotool`(XTEST) → **0** 事件。可分。
  - **③ 收回即时**：停会话 → **115ms** `connect_failed`，不挂死；但信号**非** `revoked`/`channel_closed`。
- **续做**：
  - **修 G2 并验证**：`screenlab/install/surface` 的 `resolve_window` 加 `--onlyvisible`；靶机部署后 `surface close Terminal` → **rc=0、491ms** 成功（原挂死 rc=124）。**未 commit**。
  - **退场语义**：`cli close`（松手）后 daemon 存活、新客户端仍可 capture、桌面完好 → `close` ≠ 关桌面 ✅。
  - **新 bug G4**：`surface clip` 写入报成功但 **owner 立即消失**、读回为空（写不持久）。

## 关键坐标 / 当前状态（供新会话直接接手）

- **真实桌面**：`human@:0`；`XAUTHORITY=/run/user/1002/gdm/Xauthority`；`XDG_RUNTIME_DIR=/run/user/1002`；1920x1093 XFCE。
- **attach 方式（3a 关键，不新开 Xvfb）**：写 `human:~/.config/screenlab/session.env`（`SCREENLAB_DISPLAY=:0` 等）+ 临时 systemd user 单元起 daemon。**不要用 `screenlab open`**（它写死 Xvfb——这就是 G1）：
  ```
  runuser -u human -- env XDG_RUNTIME_DIR=/run/user/1002 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1002/bus \
    systemd-run --user --unit=screenlab-attach --collect --setenv=PYTHONPATH=/opt/screenlab \
    python3 -m screenlab.service.cli daemon --display :0 --xauth /run/user/1002/gdm/Xauthority \
    --socket /run/user/1002/screenlab.sock --blob-dir /home/human/.local/share/screenlab/blobs --account human
  ```
- **靶机 `/usr/bin/surface` 已是修好的版本**（md5 `463cc06e212fee7d71bbcd62b1182dda`）；repo 同步改了、未 commit。
- **物理键盘设备** = `/dev/input/event2`（`AT Translated Set 2 keyboard`）；鼠标候选 `/dev/input/event4`（VirtualBox USB Tablet）。
- **自写 evdev 读取器**：`/tmp/kilo/evread.py`（本地）→ 已 scp 到靶机 `/tmp/evread.py`；比 `libinput debug-events` 稳（后者重定向文件被缓冲、`timeout` 杀掉丢输出）。
- **宿主注入示例**：`VBoxManage.exe controlvm centos9 keyboardputscancode 1e 9e`。
- `/opt/screenlab` 与 repo `feat/screenlab-p2` @ `90afbeb` 逐文件一致（本会话未重部署）。

## 下一步（新会话照此，先等 YZ）

1. **等 YZ 裁决三缺口**（`screen-assist-exp-log.md` §缺口）：
   - **G1｜attach 公开入口**：`screenlab open` 写死 Xvfb，缺"附着已有 `:N`"的路径（本会话用临时单元绕过）。
   - **G3｜收回语义化**：停会话后应返回 `revoked`/`channel_closed`（+ 停时 unlink socket），现为通用 `connect_failed`。
   - **G4｜`surface clip` 写入不持久**：owner 随命令退出即亡，读回为空。
2. **G2 改动是否提交**：`screenlab/install/surface` 未 commit，等 YZ 定。
3. 若继续实验（可选）：**3a 抢占机制**（物理输入 → agent 转观察/停注入；分源判据已具备）；或 **mouse 分源**（event4）。

## 入口

- **规则 + 环境（先读，稳定）**：`screenlab-rules.md`
- **本线方案（工作稿）**：`design-screen-assist.md`
- **本会话实验全记录**：`screen-assist-exp-log.md`（三闸门 + G1–G4）
- 目标（唯一约束）：`spec-screen-1.md` §0.0
- 体系：`design-screen-system.md`；生命周期/命令层：`issue-screen-surface-lifecycle.md`
- 号码体系：`../cogos/cogos/phone/`、`../cogos/cogos/feishu/telecom.py`
- 平台实测：`screen-exp-log.md`（E5/A1/A2/P1）
- 代码：`../cogos` @ `feat/screenlab-p2`
- 上一轮：#40 `handoff-screen-40.md`
