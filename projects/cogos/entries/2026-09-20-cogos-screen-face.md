# 2026-09-20 cogos 图形面（看屏 / 操作）

> 工作流：cogos 的"图形化看电脑"。本会话把 see/act 从纸面推到**两台真机实物**，并把实测约束回写 spec。
> 产物都在工作区 `../checkpoint/26-09-26-screenlab/`（未归位 locus）。

## 产物

- 设计稿：`../checkpoint/26-09-26-screenlab/spec-screen-1.md`（screen/1 协议 + 客户端 + 平台 + 验收 + 运行时约束；§5.7 = Windows 约束；本会话新建）。
- 实测：`../checkpoint/26-09-26-screenlab/checkpoint-3.md`（X11 三段根因 / Wayland 两通路 / §五 设计级结论 / §七 安全事件 / §八 系统改动）；`../checkpoint/26-09-26-screenlab/checkpoint-4.md`（本会话：落码 + Windows 打通 + 系统改动清单）。
- 原型：`../checkpoint/26-09-26-screenlab/screen-lab/`（daemon + client + CLI，1082 行；README 有用法与验收）。
- 讨论：`handoff-screen-01.md` → `checkpoint-3.md` → `handoff-screen-02.md` → `checkpoint-4.md` → `handoff-screen-03.md` → `checkpoint-5.md` → **`handoff-screen-04.md`（下一步 = Phase 2 形态讨论）**。

## 已通（可当既定）

- **本机 X11 能跑**：三段根因 = ① modesetting 拒 llvmpipe 跑 glamor → 装 `xorg-x11-drv-vmware`；② `/dev/dri/card0` 权限 → `usermod -aG video`；③ Xfce XSMP 残留 → 改用 `gnome-xorg`。
- **daemon 必须活在目标会话内部**：GNOME Shell D-Bus 抓屏对跨会话 `AccessDenied`；rootless Xwayland 根窗口 `XGetImage` `BadMatch`。
- **`snapshot_id` 必需**：加装饰后坐标漂移（y 158→185）；`act(pointer)` 绑当次快照。
- **WM 是 `act` 前置**：无 WM 时 `_NET_ACTIVE_WINDOW` 缺失、键盘跑别处。
- **选型定案**：抓屏 Pillow（`ImageGrab(xdisplay=)`）+ 注入 `xdotool`；xlib 手写不可靠。
- **212 是最便宜的弱机场**：1 vCPU/1.7G 跑 `Xvfb :99` + openbox + chrome。

## 未决（11 项裁决，见 spec-screen-1 §10）

图 lineage（1）、自建 vs E2B（2）、客户端厚度（3）、平台（4）、212 sudo（5）、4b 关系（6）、**代码放哪 screen-lab vs cogos 子包（7）**、**Wayland 适配（8）**、Xfce 残留（9）、密码/SSH/防火墙（10）、Windows 重启（11）。

## Windows 线（09-20 打通，Surface `192.168.1.112`）

- **形态（选 A：专用标准账户占交互会话）**：建非管理员账户 `screen` → 装 SSH 公钥 → 挂启动项拉起 daemon（`pythonw`，监听 `127.0.0.1:9911`）→ 本机 `ssh -L` 隧道转出。
- **实测定案**：① Session 0（sshd 所在）**无桌面**，抓屏 `screen grab failed`；② 必须开 **per-monitor DPI 感知**，否则图像坐标与 `SendInput` 空间差 1.5×（本例 1920×1280 @150%）；③ Windows OpenSSH **不支持 AF_UNIX 转发** → loopback TCP；④ `New-LocalUser` **不自动加组**，不在 `Users` 组就无本地登录权 → 登录界面不列该账户（SSH 不受影响，易误判）。
- **闭环已过**：抓桌面 → 点开始按钮（图像 `618,1258`）弹菜单 → `Win+R` 起 notepad → 打字 75 字符。
- **实现**：`backends_win.py`（Pillow GDI `all_screens` 抓屏 + `SendInput` ctypes 注入 + DPI 感知）、`platform_backends.py`（按平台选 adapter）、传输加 `--tcp`。
- 事故/环境：`screen` 曾因不在 `Users` 组而无法登录，YZ 更新系统重启后自动进入 `screen`；daemon 未随重启丢失（启动项生效）。

## 下一步候选

- 回写设计（**本会话已做** → `spec-screen-1.md`）。
- 环境固化脚本：212 `Xvfb+openbox+应用` 收成 bootstrap。
- **最小 daemon + client + CLI**（Phase 1 自洽工具，不被裁决 1–3 阻塞，但受裁决 7 影响落地位置）。**本会话已落原型** → `../checkpoint/26-09-26-screenlab/screen-lab/`（746 行）；两环境 LLM 在环验收通过（212 `:99` 与 本机 `:0` 各完整 `see→act→see`；`:0` 先经 YZ 授权用密码解锁）。
  - 新观察：`act` 即时抓帧可能早于渲染 → 返回世代只当提示，判稳定态须再 `see --wait-stable`（已记入 spec §2）。
  - 安全：`act type` 响应只回 `text_length`，不回文本。
- Wayland 适配 / Android-scrcpy 场（**下一步**：`handoff-screen-03.md` 已备，待选设备/连接方式/是否 root；本机与 212 均无 `adb`/`scrcpy`）。
- 补做 a11y 实测（checkpoint-3 §五.4 记"完全未验证"）。

## Android 打通 + 术语定案（09-20 #4，本会话）

- **Android 已通**（华为 `MAR-TL00`，Android 10 / EMUI 10，`12d1:107e`）：本机 VM 需先在宿主 **VirtualBox 直通 USB**；装 `android-tools`（EPEL，`--disablerepo=tailscale-stable`）+ 自建 udev 规则；设备授权后零协议改动接入（新增 `backends_android.py` + `--backend android`），秒表闭环 `00:00.00→00:01.24→00:02.55`。
- **实测约束**：服务**不驻留目标会话内**（服务在宿主、经 adb 驱动）；screencap = input = uiautomator bounds **同一坐标空间**（无 Windows 式 DPI 偏移）；刘海只造成尺寸口径差（2312 vs 2231）不影响注入；`input text` 不支持中文。
- **术语定案**：面向 agent="**工具 → 能力面**"，面向实现="**客户端 / 服务**"。`computer` 工具三能力面 `term`/`fs`/**`graphics`**；agent 侧=**图形客户端**、目标侧=**图形服务**（目标侧不叫 agent，`daemon` 只是进程形态）。**三面目标侧支撑异构、不合并**：term→sshd、fs→sftp（既有）、graphics→**自建图形服务**；统一只在 agent 侧 `ComputerSession`，**无"一个服务全包"**。
- **Android 免 root 只有 `graphics` 面**（无 term/fs）；通用形态待定 = 设备内 app 服务（无障碍 + 前台服务 + MediaProjection），仍需一次性装配通道。
- 详情：`../checkpoint/26-09-26-screenlab/checkpoint-5.md`（§八 术语）+ `spec-screen-1.md`（§0.1 / §5.8）。

## 注意

- cogos 代码基线仍 `45ab216`、工作区干净、`master`=`origin/master`。
- 改的是**两台机的系统配置**（`checkpoint-3.md` §八，可回退）；未动 cogos 代码。
- 安全：本会话有一次密码泄露事故（重定向失误），暴露面与处置见 `checkpoint-3.md` §七。

## P1 落码 + 双机验收（09-20 #6）

- 代码落点：cogos 仓库根 `screenlab/`（`proto` / `service` / `install`），**禁止 import cogos**；cogos 侧只 import `screenlab.proto`（保住 `subtree split` 退路）。分支 `feat/screenlab-p1`（基于 `45ab216`），**未合并 master、未建 PR**。
- 协议 `screen/1` **冻结**（wire 不动）；实现细节定案见 `handoff-screen-06.md`（envelope 用 `op`、动作名放 `kind`、世代**连接内**、错误码字面量、`element`/`mode=tree` 未实现）。
- 自启外壳：桌面 `:0` = `systemd --user`（`PartOf/WantedBy=graphical-session.target`）；无头 = **system unit** + `Xvfb :99` + openbox（**WM 是前置**）；端点 `unix:`。客户端 `ScreenChannel` 每机一个、懒连、自动起 `ssh -L`；`authority`/`graphics.endpoint` 来自 `agent.json` 的 `computer` 块。
- 验收 1–7 双机（212 无头 + 本机 `:0`）通过：一次装配 / 重启自启 / 会话重登自启 / agent 自动连 / 闭环见变化 / 过期拒 + `since_hash` 去重 / 干净卸载。`pytest` **1198 passed / 4 skipped**。

## 多账户模型 + X 鉴权缺口（09-20 #7 / #8）

- **给 agent 一个账户 = 给它一个独立会话/桌面**（不是抢人的桌面）；隔离三层对齐：**账户 = 会话 = 服务**（socket 归 uid）。agent 自己占的 = `owned`（恒有 capture/input）；把人正在用的桌面让出去 = `granted`（要走 grant/consent）。
- **语义澄清**：`给 agent 一个账户` = 把 agent **放进**那个账户（agent 账户 = 服务账户 = 会话账户），这才是"零凭据直连"；要是另一个账户，就得先有该账户凭据走 `ssh -L`（实测：跨账户直连 socket → `PermissionError`）。
- **发现并修复缺口**：无头外壳的 `Xvfb :99` **没有 `-auth`**（`/tmp/.X11-unix/X99` 0777）→ **同机任意账户可抓屏/注入**（实测 zhengyp 读到 tangyu 的窗口标题、`xdotool type` 注入成功）。`账户即门` 只守住了 screenlab socket，**没守住脚下的 X**；212 同模板同样敞开。
  - 修法（`install/xvfb-start.sh` + `install/install.sh` + `service/daemon.py`，**+18 −1**）：install 期生成 cookie → `$ETC/Xauthority`（0600，chown SERVICE_USER）→ `Xvfb -auth`；daemon 设 `os.environ["XAUTHORITY"]`（Pillow `ImageGrab(xdisplay=)` 认证**只认进程 env**，修前只给了子进程 → 开鉴权后抓屏报 `X connection failed`）。**未提交**。
  - 修后双机实测：无 cookie 直连被拒（`No protocol specified`）/ 有 cookie 与经服务均正常 / 闭环 OK / `pytest` 1198。Windows 侧对应缺口是 loopback TCP 的本地 token（未做）。
- **免 root 形态未实现**：用户态无头 Xvfb + `loginctl enable-linger` 这条路还没有；当前无头只能走 root 装的 system unit。
- **实测**：本机 `tangyu`（uid 1001、**无 sudo**、不在 wheel、进程 `CapEff=0`）跑无头服务 + Chrome 实操（Bing 搜 justmysocks → 约 4570 条 → 官网 `justmysocks.net` 被拒 `ERR_CONNECTION_REFUSED`（国内 DNS 污染）→ 中文站 `jms-socks.com` 加载成功）；212 真 `systemctl reboot` 后（boot_id 变）两 unit **无人工自启**、`Xvfb -auth` 起、闭环 OK、`authority=owned`。

## Windows「登录前 / 安全桌面」（09-20 #8 讨论，未落码）

- 墙：`LogonUI` 以 **SYSTEM 跑在 Winlogon 安全桌面**，与用户默认桌面不同桌面 + UIPI 隔离 → 抓不到也注入不进。
- 三条路 + 一条替代：**A 自动登录**（最低成本；要禁锁屏策略，否则锁屏切回安全桌面照样失联；密码托管用 LSA secret / 凭据提供程序收敛）；**B UIAccess**（签名 + 装 `Program Files`，可运行在安全桌面、能抓能注入，但**不能填凭据**）；**C Credential Provider / Winlogon notify**（能填凭据、可远程解锁，代价最大、**与远控同构会被 AV/EDR 盯**）；替代：**RDP** 自己开会话（凭据由发起端给，但运输换掉、操作的是 RDP 桌面）。
- **建议**：超出 P4 口径（P4 = 已登录交互桌面），多半**不做**。Linux 同构（greeter 是别的会话/用户、Wayland 更够不着）。

## P4 议题（下一步）

- **Windows 实现面只需服务端**：协议 / 客户端 / `ssh -L` / 工具面全复用；要补的是 ① 服务端 backend（`backends_win.py` 已有、**未真机复验**）② **装配/自启外壳**（`screenlab/install/` **仅 Linux**）+ 装配期配对 `graphics.endpoint`。
- 9 项待裁决 + 新增 2 项（分支/提交策略、文档回写）见 `../checkpoint/26-09-26-screenlab/handoff-screen-08.md`。
