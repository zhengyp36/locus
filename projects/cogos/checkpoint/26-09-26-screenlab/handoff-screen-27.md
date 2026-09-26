# handoff｜交接：Surface Go 3 上的 CentOS 9 图形机 · 2026-09-23 #27

> 接续 `handoff-screen-26.md` #26。**#26 是"讨论方向"，本轮不是**——本轮 YZ 明确把话题压回一件具体事：
> **在 Surface Go 3 的 VBox 上，把 Linux 图形目标机弄好，用来"验图形功能"。**
>
> **给新会话的第一句话**：先读本文件，把**事实 / 作废 / 现状 / 下一步**复述一遍给 YZ 核，再继续。
> 不要把 #26 的"方向讨论 / GNOME-Wayland 之争"带进来——YZ 在本轮纠正过一次。

## 一、本轮目标（YZ 口径）

- **就是验图形功能**：在 Linux GUI 上跑通 `capture → act → capture` 闭环（对齐之前四平台验收口径）。
- 不预设桌面生态、不预设发行版；**能提供那个 GUI 会话就行**。

## 二、网络与访问（YZ 亲自给的口径，别混淆）

| 位置 | IP | 说明 |
|---|---|---|
| acer 宿主 | `192.168.1.155` | 笔记本 |
| acer/vbox:centos（= 当前本机 workspace） | `192.168.1.13`（桥接） | CentOS Stream 9，`/home` 有 5 用户 |
| surface 宿主 | `192.168.1.112` | Surface Go 3，Windows |
| surface/vbox:centos9（= 本轮目标） | `192.168.1.212`（桥接） | CentOS Stream 9，`/home` 只有 zhengyp |

- ⚠️ 两台 VM 的 VBox **NAT 默认都是 `10.0.2.15`**，hostname 也是它 → **必须按桥接 IP 区分**，别混淆。
- ⚠️ 两台 VM **machine-id 相同**（`f9ece5358eec46b8a3ff1a47b0932005`）= 克隆关系；同网段两台一致属潜在小隐患（DHCP DUID 等），暂不影响。

**访问方式**
- `ssh screen@192.168.1.112`：标准用户，权限很受限（读不到 WMI/服务/进程，`VBoxManage` 报 `E_ACCESSDENIED`）。key 免密；**screen 账户密码 2026-09-22 改过，不影响 key 登录**。
- `ssh zhengyp@192.168.1.112`：**管理员**。本轮由 YZ 把本机公钥（`~/.ssh/id_ed25519.pub`，zhengyp36@gmail.com）加进 `C:\ProgramData\ssh\administrators_authorized_keys` 才通的；`VBoxManage` 在这个身份下可用。
- `ssh zhengyp@192.168.1.212`：guest，**key 已存在可直接进**。
- guest 与宿主 `zhengyp` 的 **sudo/登录密码 = 本机密码**（`~/.secrets/centos.key`）。

## 三、事实（本轮已验）

**Surface 宿主**
- Surface Go 3 / Intel **i3-10100Y**（2C/4T）/ **8GB RAM** / C: 118.1GB 总、**剩 41.5GB** / **Windows 11 Home**（build 26200.9457）/ **VBox 7.2.8**。
- **VBS/HVCI 在跑**：`EnableVirtualizationBasedSecurity=1`、`HypervisorEnforcedCodeIntegrity\Enabled=1`、`IsSecureKernelRunning=1`、`Enum\ROOT\VMBUS\0000` 存在（= hypervisor 已加载；`msinfo32` 亦报"已检测到虚拟机监控程序"）。
- **但 VBox 照样能起 VM**（YZ 实测 centos9 可启动）→ **"必须关内存完整性 + 开口子"的整套判断作废**（那是通用清单，不适用于此机器）。

**Surface 的 centos9 VM（= 目标机 192.168.1.212）**
- 目录 `C:\Users\zhengyp\VirtualBox VMs\centos9\`；`centos9.vdi` 20GB + `centos9_data.vdi` 60GB（实际占 ~10.7GB）。
- 原始配置：1 CPU / 2048MB / VRAM16 / VMSVGA / 3D off / NIC1 NAT(2222→22) / NIC2 bridged。
- **GA 7.2.8 已装**（`/opt/VBoxGuestAdditions-7.2.8`），但 `vboxadd.service` 重建内核模块**编译失败** → 系统 `degraded`；`vboxguest/vboxvideo/vboxsf/vmwgfx` **已加载可用**（显示/共享文件夹正常）。
- guest 上**已有旧的 screenlab**：`/opt/screenlab` + `screenlab.service` + `screenlab-xvfb.service`（`Xvfb :99` 正在跑）。
- guest 有 internet、EPEL、gcc/make/kernel-devel 均在（克隆自带）；kernel `5.14.0-700.el9`；`/` 13G 可用、`/home` 56G 可用。

## 四、本轮改动（已落地）

| 位置 | 改动 |
|---|---|
| VM 设置 | `modifyvm centos9 --cpus 2 --memory 3072 --vram 64 --accelerate3d off` |
| guest `/etc/systemd/system/default.target` | → `graphical.target` |
| guest `/etc/gdm/custom.conf` | `AutomaticLogin=zhengyp` + `WaylandEnable=false` |
| guest `/var/lib/AccountsService/users/zhengyp` | `XSession=xfce` |
| guest `~zhengyp/.config/autostart/fix-resolution.desktop` | 开机把 `Virtual-1` 钉到 **1920x1080** |

- **没装任何新包**（XFCE/gdm/GA 都是克隆自带的）。

**验证结果**：`graphical.target` + `gdm` active；会话 `zhengyp seat0/tty2`；`Xorg vt2`（socket `X0`）+ `xfce4-session/xfwm4/xfdesktop`；`xrandr` **current 1920x1080**。

## 五、作废名单（本轮）

- **关内存完整性**（VBS 不是拦路虎）、**提权计划任务 / `LocalAccountTokenFilterPolicy`**：作废，不用做。
- **装 Debian 13 + XFCE 的方案**：作废——前提是"要新造一台轻 VM"，而**已有一台能启动的 CentOS 9**，加桌面即可。
- **装 CentOS 10**：非必要；对本目标（验图形）与 9 无本质差别。
- 我一度把 #26 的方向讨论（GNOME/Wayland 版本之争）带进来 → **YZ 纠正，作废**。

## 六、现状与下一步

- **当前 VM 由我以 `--type headless` 起的** → **没有 VM 窗口**，Manager 里只有预览缩略图；YZ 想看到画面需切 **GUI 模式**（`acpipowerbutton` → `startvm --type gui`），**待 YZ 发话**。
- Scaled Mode 还原：**只能在 VM 窗口的 View 菜单**操作（headless 下没有）；host key 默认右 Ctrl，**Surface Go 无此键** → 可改 `File → Preferences → Input → Host Key Combination`（建议右 Alt 或左 Win 键）。
- 原则：**Scaled Mode 只缩放显示、不改 guest 分辨率**（安全）；**Auto-resize Guest Display 会改分辨率**（要取消勾选，正是要避免的漂移源）。
- **Step 3（未做）**：先停掉旧的 `screenlab-xvfb.service` / `screenlab.service`（避免与真桌面 `:0` 打架），再在 **`:0` 会话内**装配 screenlab 图形服务，跑 `capture → act → capture`。

## 七、清理项（待 YZ 裁决）

- 是否 mask 掉失败的 `vboxadd.service`（消 degraded）。
- 是否停用旧的 screenlab/Xvfb 单元。
- 管理员 SSH 公钥（`administrators_authorized_keys`）是否保留；不留则删除该行。
