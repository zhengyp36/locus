# handoff｜环境建立（测试靶机）· 2026-09-23 #28

> 接 #27。本轮不是方向讨论，是**把测图形的环境定下来并清干净**（= 之前计划的 **Step 0**）。
> 目标：为"XFCE/X11 上验 `capture → act → capture`"准备一台干净、可用 tailscale 访问的靶机。

## 一、网络与访问（定案：走 tailscale）

| 节点 | tailnet | 桥接 | 说明 |
|---|---|---|---|
| acer host | `desktop-7cmfggs` 100.119.42.62 | 192.168.1.155 | ⚠️ ssh 22 超时（无 sshd/被挡），暂不可进 |
| **acer/vbox:centos（本机）** | `acer-centos-9` 100.79.86.84 | 192.168.1.13 | 开发/讨论环境 |
| surface host | `tablet-bbt8eqb4` 100.112.50.115 | 192.168.1.112 | Win11，`ssh zhengyp@` 管理员可用 |
| **surface/vbox:centos（靶机）** | `surface-centos-9` 100.100.137.78 | 192.168.1.212 | 测试环境 |

- 两台 VBox 之间 tailscale 均为 **direct**（靶机 via `192.168.1.212:41641`，23ms）→ 地址层稳定，替代桥接。
- 访问：靶机 `ssh zhengyp@100.100.137.78`；surface 宿主 `ssh zhengyp@100.112.50.115`。
- ⚠️ `VBoxManage` 不在 Windows PATH，须全路径 `"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"`。
- 靶机开机：`ssh zhengyp@100.112.50.115 "\"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe\" startvm centos9 --type headless"`。

## 二、本轮改动（已落地）

**靶机 surface-centos-9（= centos9）**
- 旧 screenlab 全清：`screenlab.service` / `screenlab-xvfb.service` **disable + 删除**；`/opt/screenlab`、`/etc/screenlab`、`/var/lib/screenlab`、`/run/screen` 全删；只剩 `X0`（`X99` 消失）。
- **machine-id 换新**：`7db571b599fc4cb8947ff29fcb7ec69d`（原 `f9ece535…`，与 acer 相同）。
- **hostname → `surface-centos`**（tailnet 名仍是 `surface-centos-9`，未改名）。
- 重启一次（`systemctl reboot`）。

**本机 acer-centos-9（未动 machine-id、未改 hostname）**
- 旧 screenlab 全清：units 删除、`/opt/screenlab`、`/etc/screenlab`、`/var/lib/screenlab` 全删。
- **账户 `alice` / `agent1` / `agent2` 已删除**（`userdel -r` + 清 linger）；`/home` 只剩 `zhengyp`、`tangyu`。
- **tangyu 的 screenlab 会话终止**：它跑的是 `gnome-shell --headless --virtual-monitor 1920x1080 --wayland-display=screenlab-0`（pid 1462）；已 `loginctl terminate-user tangyu`，并删 `~/screenlab`、`~/.config/systemd/user/screenlab-shell.service`。tangyu 账户保留。

## 三、验证结果

**靶机**
- `hostname` = `surface-centos`；`machine-id` = `7db571b599fc4cb8947ff29fcb7ec69d`。
- 无 screenlab 单元/文件；`/tmp/.X11-unix/` 只有 `X0`。
- 桌面正常：`gdm` + `graphical.target` **active**，`gdm-x-session --run-script startxfce4`，**Xorg vt2 → `:0`**，`xfce4-session`，`xrandr` **1920x1080**。
- `tailscaled` enabled；tailnet `100.100.137.78` direct。

**本机**
- 无 screenlab 单元/文件；`/home` 只剩 `zhengyp`、`tangyu`；我们的 ssh 会话未中断。

## 四、插曲（教训）

- `rm /etc/machine-id` 后执行 `systemd-machine-id-setup --commit` 报 `Failed to determine whether /etc/machine-id is a mount point`，**machine-id 一度缺失**。
- 修法：`touch /etc/machine-id && systemd-machine-id-setup`（再从随机源生成），最后 `chmod 444`。→ **正确顺序是先建空文件再生成，别用 `--commit` 于不存在的文件。**

## 五、遗留（待 YZ 裁决）

- zhengyp 自己 `~/.local/share/screenlab`（09-20 旧拷贝）**未动**。
- 本机 hostname 仍为空（按"本机不动"未设）；两台 NAT hostname 都是 `10.0.2.15`（克隆所致，暂不影响）。
- 靶机 `vboxadd.service` 仍 degraded（内核模块编译失败，不影响图形）。

## 六、下一步

- **Step 0（环境）已完成**。
- **Step 1（未做，唯一闸门）**：在靶机 `:0`（XFCE/X11）里开 `xfce4-terminal` + `zenity` + Chrome，**用原始命令**（`import -window root` / `xwd`）抓一次，判定"X11 下能否看见一类 GTK/GL 窗口"（B2 反例）。
  - 结果可见 → XFCE/X11 单形态成立，可进 Step 2（收敛取帧后端）。
  - 仍黑 → 形态假设推翻，停下重议。
