# checkpoint-3｜图形面实测：本机 X11 打通 / Wayland 阻断 / 弱机验证（2026-09-20）

> 性质：**讨论 + 实测记录，非权威口径**。本会话**改了两台机的系统配置**（见 §八），但**未动 cogos 代码**（基线仍 `cogos` @ `45ab216`，本会话只读代码）。
> 入口：`handoff-screen-01.md`。前序：`handoff-tools-09.md` → 本会话把"看屏"从纸面推到**可操作**。
> 后续会话入口：`handoff-screen-02.md`。

## 一、本会话做了什么

一句话：**把 screen/1 的 see/act 从讨论变成两台机器上跑通的实物**，顺带撞出四条设计级约束。

- 新接入第二台验证机 `192.168.1.212`（免密登录 + 无头 X）。
- 打通本机（locus 所在 VM）的**真实 X11 会话**，我隔 SSH 操作、YZ 在 VBox 窗口同步看到界面被操作。
- 找到并修掉本机 X11 起不来的三段根因。
- 摸清 Wayland 下的两条通路与各自的阻断点。
- 处置一次**密码泄露**（我的重定向失误，见 §七）。

## 二、机器清单（都是 VirtualBox 里的 CentOS Stream 9）

| 机器 | 规格 | 网络 | 用途 |
|---|---|---|---|
| 本机（locus 所在） | 2 vCPU / 3.6G（可用 ~1.1G） | NAT `10.0.2.15` + 桥接 `192.168.1.13` + tailscale `100.79.86.84` | 主验证场（真 X11 桌面） |
| 新机 `192.168.1.212` | **1 vCPU（i3-10100Y）/ 1.7G** | NAT `10.0.2.15`（同 hostname）+ 桥接 `192.168.1.212` | 弱机 / 无头 Xvfb 场 |
| Windows 宿主 `192.168.1.112` | Win11 **Home** | VBox 宿主；`22` 关，`135/139/445` 开 | Windows adapter 候选（暂停，见 §六） |

- `212` 登录：公钥已装（`~/.ssh/id_ed25519`），`ssh zhengyp@192.168.1.212` 免密；**sudo 需密码**。
- 两台均 `zhengyp` 在 `wheel`；密码同在 `~/.secrets/centos.key`（本机 sudo 也用它）。
- 本机与 212 **hostname 相同**（都是 `10.0.2.15`），是同模板克隆，别搞混。

## 三、本机 X11 打通（三段根因，逐层揭开）

### 3.1 Xorg 起不来：glamor 拒绝软件光栅

`~/.local/share/xorg/Xorg.0.log`：

```
(II) modeset(0): Refusing to try glamor on llvmpipe
(EE) modeset(0): glamor initialization failed
```

Xorg 1.20 的 `modesetting` 驱动在软件光栅（llvmpipe）上拒绝跑 glamor → 直接放弃、进程退出。
**修**：装 `xorg-x11-drv-vmware`（VBox 的 VMSVGA = VMware SVGA II，PCI `15AD:0405`；该驱动走 `VMWARE_CTRL` 扩展，不依赖 glamor）。
装后日志 `vmware(0): Output Virtual1 using initial mode 1366x643`，只有 `Render acceleration is disabled` 这类警告。

### 3.2 权限：`/dev/dri/card0` 拿不到

`card0` 是 `root:video 660` + logind 给**活动会话**的临时 ACL；zhengyp 不在 `video` 组，而 X11 会话又没激活成功 → 拿不到 ACL。
**修**：`sudo usermod -aG video zhengyp`（永久，不再依赖 ACL；注销重登生效）。

### 3.3 会话注册失败：Xfce 的 XSMP 残留

```
xfce4-session: Another session manager is already running
gdm: GdmDisplay: Session never registered, failing
```

会话管理器重复判定 → xfce4-session 自杀 → 会话不注册 → GDM 判定失败、退回 greeter。
现场有残留 `xfconfd`（用 `kill <pid>` 清；`pkill -f <pat>` 会匹配到承载脚本的 shell 自己，**踩过两次**，要用 `pkill -x`）。
**绕过**：改用 `gnome-xorg` 会话（`/usr/share/xsessions/gnome.desktop`，Exec=`gnome-session`）。Xfce 这条**没根修**，属遗留。

GDM 反复落回 Wayland，正是因为这 1–3：每次 X11 会话都秒退，就回退到 Wayland。

### 3.4 现在的本机状态（可直接用）

- `Xorg` 以 zhengyp 身份跑在 **vt2**，`DISPLAY=:0`，`XAUTHORITY=/run/user/1000/gdm/Xauthority`
- GDM 已配 **zhengyp 自动登录 + `Session=gnome-xorg`**（YZ 选择保留现状）
- **看**：`python3.11 -c "from PIL import ImageGrab; ImageGrab.grab(xdisplay=':0').save('/tmp/kilo/s.png')"`（Pillow 12.3 自带 `xcb`，无需外部工具），全屏 1366x643
- **动**：`xdotool`（XTEST）——`key alt+F2` / `type "..."` / `click X Y` / `windowactivate --sync <id>`
- 实测闭环：点掉首登对话框 → `Alt+F2` → 起 `xfce4-terminal` → 打字 `echo hello-from-xdotool; uname -r; date` → 抓屏确认输出（YZ 在 VBox 窗口同步看到）

## 四、Wayland 的两条通路与阻断

本机日常（YZ 自己选的"标准（Wayland 显示服务器）"）是 Wayland；以上 X11 是**为实验另开**的。

- **Xwayland 桥（`DISPLAY=:0` 指向 Xwayland）**：抓屏**不通**——rootless Xwayland 的根窗口 `XGetImage` 直接 `BadMatch`（`Image.core.grabscreen_x11` 失败）。注入（XTEST→合成器）**未验证**。
- **原生通道 `org.gnome.Mutter.RemoteDesktop`**：**可达**，从另一个登录会话也能 `CreateSession` 成功（`SupportedDeviceTypes=7`、`Version=1`）。看屏需再叠 `org.gnome.Mutter.ScreenCast` + PipeWire 流，重。
- **GNOME Shell 的 D-Bus 抓屏被拒**：`org.gnome.Shell.Screenshot.Screenshot` → `AccessDenied: Screenshot is not allowed`（跨登录会话检查）。**推论：daemon 必须活在目标会话内部**，不能作为外部进程去抓。
- **Tailscale SSH 关闭**（`RunSSH: false`）——尾网只有普通 sshd（密码/公钥）。

## 五、see/act 实测结论（设计级，进 spec 时要收敛）

1. **指针坐标会因窗口装饰漂移**：加标题栏后输入框 y 从 158 → 185，按旧坐标点空。→ 印证 screen/1 的 **`snapshot_id`（快照世代）**：`act(pointer)` 必须绑定当次快照。
2. **没有 WM 就没有焦点语义**：Xvfb 无 WM 时 `_NET_ACTIVE_WINDOW` 不存在，`getactivewindow` 报错，键盘事件跑到别处（误触发浏览器新标签页）。起了 openbox 后 `windowactivate --sync` 正常。→ **WM 是 `act` 可靠性的前置**（或显式 `windowfocus`）。
3. **X 下的窗口级抓屏可用**：`import -window <id>` 出窗口尺寸图；整屏用 `import -window root`。
4. **a11y（AT-SPI）本会话完全未验证**——handoff 里"顺带实测无头 a11y 是否可用"这条**没做**。
5. 工具选型：手写 python-xlib（XTEST）**不可靠**——Xlib 的 RandR 错误处理有 bug（`BadRRModeError object has no attribute sequence_number`），连接初始化排队错误在 `flush()` 时炸。**用 `xdotool`**。

## 六、Windows 宿主线（暂停）

- 目标：给 `192.168.1.112`（Win11 Home）开 OpenSSH Server，做成第三个 adapter 验证场。
- 已给 YZ 完整命令（`Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0` + 起 sshd + 防火墙 + **`C:\ProgramData\ssh\administrators_authorized_keys`** 特例 + `icacls` 收紧），公钥已提供。
- **YZ 反馈：装太慢，暂停。** 结论：Windows 线不阻塞 Linux 线，挂起即可。
- 参考：Windows 侧自动化栈 = UIA（`uiautomation`/`pywinauto`）+ `mss` 抓屏 + `SendInput`；有现成 **Windows-MCP** 可先对照。坑：GUI 自动化必须在**交互式会话**里跑（Session 0 无桌面）。

## 七、安全事件与暴露面（需 YZ 处置）

### 7.1 泄露（我的错）

我用 `cat ~/.secrets/centos.key | sudo -S -p '' ... | tail -12 < ~/.secrets/centos.key` —— `< file` **绑定到了 `tail`**（覆盖管道），于是 `tail` 把密码文件内容原样打印。密码因此进入：①工具输出（随请求体发给模型服务端）②本机 Kilo 会话记录文件。**无法撤回**。

### 7.2 暴露面实测

- 两台 `sshd` 都 `0.0.0.0:22` + `PasswordAuthentication yes` + firewalld `public` 放行 `ssh` → **局域网任何机器可密码登录**。
- `tailscale0` 未绑 zone，落默认 `public`（放行 ssh）→ **尾网任何设备可登**。日志里有手机尾网 IP（`100.121.180.8`）的**公钥**登录记录。
- 本机 `~/.ssh/authorized_keys` 两条：`zhengyp@10.0.2.15`、**`u0_a293@localhost`（手机钥匙）** → 手机免密可进。
- 宿主 `192.168.1.112` 开 `135/139/445`（SMB）；**若 Windows 账户同密码 → `net use \\192.168.1.112\C$` 可挂管理共享**。
- `cc-connect` 监听 `*:9810`/`*:9820`（firewalld 未放行 → 目前门外的）；`4096/tcp` 在防火墙里开着但**无监听**（残留规则）。
- `/var/log/secure` 无 `Failed password` 记录（无爆破迹象）。

### 7.3 已做 / 未做

- 已做：`~/.secrets/` 权限收紧（目录 `700`、文件 `600`；212 无此目录）。
- 未做：**改密码**（唯一彻底关闭项，须 YZ 亲自 `passwd`，两台都要，且不要与 Windows 同密码）；关 SSH 密码登录；收紧 firewalld（YZ 看过选项、暂未处置）。

## 八、系统改动清单（都可回退）

**本机**
- `usermod -aG video zhengyp`
- 装 `xorg-x11-drv-vmware`、`xdotool`
- `/etc/gdm/custom.conf`：加 `AutomaticLoginEnable=true` / `AutomaticLogin=zhengyp`（备份 `custom.conf.bak`）
- `/var/lib/AccountsService/users/zhengyp`：`Session=xfce` → `gnome-xorg`
- 脚本：`/tmp/kilo/see.py`（Pillow 抓屏）、`/tmp/kilo/act.py`（**已弃用**，Xlib 版）、`/tmp/kilo/askpass.sh`（ssh 免 TTY 取密码）

**212**
- 装 `xorg-x11-server-Xvfb`、`xdotool`、`xwd`、`ImageMagick`、`openbox`（`scrot` / `xorg-x11-apps` **不在仓库**，别用这俩名字）
- `xvfb99.service`（transient，`Xvfb :99 -screen 0 1280x800x24 -nolisten tcp`）**在跑**；openbox `setsid` 起、**在跑**；chrome demo 已清
- 212 的 `sudo` 用法：`cat <pwd-file> | ssh zhengyp@192.168.1.212 'sudo -S -p "" <cmd>'`

## 九、命令备忘（新会话直接用）

```bash
# 本机：看 / 动
DISPLAY=:0 XAUTHORITY=/run/user/1000/gdm/Xauthority \
  python3.11 -c "from PIL import ImageGrab; ImageGrab.grab(xdisplay=':0').save('/tmp/kilo/s.png')"
DISPLAY=:0 XAUTHORITY=/run/user/1000/gdm/Xauthority xdotool key alt+F2
DISPLAY=:0 XAUTHORITY=/run/user/1000/gdm/Xauthority xdotool type --delay 40 "hello"; xdotool key Return
DISPLAY=:0 XAUTHORITY=/run/user/1000/gdm/Xauthority xdotool mousemove 110 185 click 1

# 本机：sudo（绝不要把 < file 放在管道末尾）
cat ~/.secrets/centos.key | sudo -S -p '' <command>

# 212：无头场
ssh zhengyp@192.168.1.212 'DISPLAY=:99 import -window root /tmp/s.png'
ssh zhengyp@192.168.1.212 'DISPLAY=:99 xdotool search --name "." getwindowname %@'
```

## 十、待 YZ 裁决（继承 handoff-screen-01 的 6 项 + 本会话新增）

1. 图 = 持久资产（`image_ctx` 有根）还是临时介质（`img-tool` 无根）——两条 lineage 未并。
2. 自建电脑 vs E2B 类云桌面。
3. 客户端薄到哪（纯管道 vs 带薄语义层）。
4. 先做哪个平台：**Linux/X11 已打通**；Android/scrcpy 未试；Windows 暂停。
5. 是否给 sudo（本机已给；212 未给）。
6. 旧遗留 4b 装配 / 按需加载与本线的关系。
7. **代码放哪**：新仓 `screen-lab` vs cogos 子包。
8. **是否做 Wayland 适配**（YZ 日常用 Wayland；当前实验环境是另开的 X11 会话）。
9. Xfce 会话的 XSMP 残留是否要根修（还是就停用 Xfce）。
10. 密码轮换 / 是否关闭 SSH 密码登录 / 是否收紧 firewalld。
11. Windows 线何时重启（需 YZ 在宿主上执行那条 PowerShell）。

## 十一、下一步候选（按当前信息排序，供 YZ 选）

1. **回写记忆/设计**：把本 checkpoint 的 §五 收敛进 spec（`snapshot_id` 依据、WM 前置、daemon 必须在会话内）。
2. **环境固化脚本**：把 212 的 `Xvfb + openbox + 应用` 收成一条 bootstrap，本机直接用 `:0`。
3. **最小 daemon + client + CLI**（handoff-screen-01 的 Phase 1 自洽工具）：mechanical 子集 `displays / state / see / act / blob_get` + Unix socket + Pillow/xdotool 后端 + 内容寻址 blob + 快照世代。**不被 §十 的 1–3 阻塞**，可在 `:0` 与 `:99` 两个环境跑 LLM 在环验收。
4. **Wayland 适配**（Mutter RemoteDesktop + ScreenCast/PipeWire）。
5. Android/scrcpy 场（handoff 里"最便宜的 adapter 验证场"，未动）。

> 纪律：跑测试用 `python3.11 -m pytest`（系统 `python` 是 3.9）；结论先落 checkpoint，定案再更新权威分册 `cogos/docs/design-agent-tools.md`。
