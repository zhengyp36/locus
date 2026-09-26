# handoff｜图形电脑：Android 打通 + 术语/形态收敛（Phase 2 待论）· 2026-09-20 #4

> **新会话任务**：**继续把"图形服务"的形态讨论清楚**——本会话打通了第四个平台（Android），并把术语（工具 → 能力面 → 客户端/服务）与"图形服务"定位**定案写入文档**。下一步不是继续敲代码，而是**定 Phase 2 的形态与裁决项**（可安装 / 自启 / 远程 / 鉴权 / 四平台推进顺序 / Android 设备内 app）。
> **交接语**：读 `work/A/checkpoint/handoff-screen-04.md`；细节读 `checkpoint-5.md`（本会话实测 + §八 术语定案）、`spec-screen-1.md`（设计稿，**§0.1 = 术语与形态**）、`spec-tools-a.md` §5（`ComputerSession`，graphics 为第三面）。
> **前序**：`handoff-screen-01.md`（图形面讨论/阶段）→ `handoff-screen-02.md`（X11 实测）→ `handoff-screen-03.md`（Android 任务）→ `checkpoint-4.md`（落码 + Windows）→ 本会话。

## 本会话性质

**实测 + 落码 + 术语/形态讨论。** cogos 代码基线未动（仍 `45ab216` 附近、工作区干净）；**改了本机（VM）系统配置 + 设备一个电源设置**（`checkpoint-5.md` §六，可回退）。

## 本会话成果（一句话）

Android（华为 `MAR-TL00`，Android 10 / EMUI 10）接入 `screen/1`：**四平台闭环全通**，且**零协议改动**（只加 `backends_android.py` + `--backend android`）；同时把**术语与"图形服务"形态**定案落进文档。

## 已收敛结论（可当既定）

- **四平台已通**：本机 `:0`（GNOME/Xorg）、212 `Xvfb :99`、Windows Surface `192.168.1.112`、**Android `MAR-TL00`（09-20 新增）**。
- **术语定案（`spec-screen-1.md` §0.1）**：两条轴——面向 agent 是"**工具 → 能力面**"，面向实现是"**客户端 / 服务**"。
  - `computer` 工具有三个能力面：`term` / `fs` / **`graphics`**（`screen/1` 是 graphics 面的协议）。
  - agent 侧 = **图形客户端**（属 `computer` 工具）；目标侧 = **图形服务（graphics）**。
  - **目标侧一律叫"服务"，不叫 agent**；`daemon` 只是服务的**进程形态**；`CLI` 是图形客户端的调试前端。
- **形态定案**：三面的目标侧支撑**异构、一面一个、不合并**——`term`→sshd、`fs`→sftp（既有，不重造）；`graphics`→**自建图形服务**（目标上无既有"看屏/操作"通道，且必须活在交互会话内）。**统一只在 agent 侧 `ComputerSession`，不在目标机 wire 上统一**；**不存在"一个服务全包 `computer`"**，`"computer 服务"`一词作废。
- **ssh 的角色**：仍保留；在图形线里当**装配/运输层**（scp 投递 → ssh 触发会话内自启 → `ssh -L` 隧道），图形服务不重造认证/传输。
- **Android 特性**（`spec-screen-1.md` §5.8）：**服务不驻留目标会话内**（走 adb，服务在宿主）；坐标三方同空间（screencap = input = uiautomator bounds，**无 Windows 式 DPI 偏移**）；刘海/挖孔只造成尺寸口径差、不影响注入；`input text` 不支持中文；**免 root 只有 `graphics` 面**（无 `term`/`fs`）。
- **Android 通用形态**（方向）：设备内 app 服务（无障碍服务 + 前台服务 + MediaProjection），脱离 adb；但**仍需一次性装配通道**（侧载 APK/adb），且 EMUI 省电/权限需缠斗。

## 待 YZ 裁决（讨论入口）

**Phase 2（主议题）**
1. **持久形态**：图形服务做成"可安装 / 目标会话内自启 / 远程可连"的交付物——是否成立、四平台各自外壳的边界。
2. **鉴权**（前置）：现 socket/TCP **无认证**，装成常驻=裸露远程控制；token + 只绑 loopback/tailscale。
3. **四平台推进顺序**：一个平台做样板验收（"干净机器 → 一次装配 → 远程 see/act 零人工"）再铺开？建议先 Linux。
4. **Android 走哪条**：adb 装配期形态（现况） vs 设备内 app（重）；app 的 MediaProjection/无障碍/省电工作量评估。

**继承旧项（`spec-screen-1.md` §10，多未动）**
5. 图 = 持久资产（`image_ctx` 有根）还是临时介质（`img-tool` 无根）。
6. 自建电脑 vs E2B 类云桌面。
7. 客户端薄到哪（纯管道 vs 带薄语义层）——原型按"带薄语义层"写。
8. **代码放哪**：新仓 `screen-lab` vs cogos 子包（**未定**）。
9. 是否做 Wayland 适配（YZ 日常是 Wayland）——**唯一仍阻断的桌面平台**。
10. a11y：`mode=tree` / `act element`（未实现；Android 是最顺落地场，`uiautomator` 通路已验可用）。
11. Windows 线是否继续/收编 `zhengyp` 桌面为第二个 Windows 场。
12. 安全：密码轮换 / 关 SSH 密码登录 / 收紧 firewalld；Windows `screen` 账户可被局域网密码登录（密码明文在 `/tmp/kilo/screen.win.pw`）；`tailscale-stable` 源 GPG 报错未修（阻断 dnf）。
13. 212 是否给 sudo（本机已给）；Xfce XSMP 残留治法。

## 下一步：把形态与裁决讨论清楚（不写码）

- 从 **Phase 2 的"服务"该长什么样**起：安装/自启/运输/鉴权四件事，Linux 先行做样板。
- 讨论时注意：**协议统一、能力面按目标挂**（Android 只挂 graphics，Linux/Windows 挂三面）。
- 讨论清楚再落文档；**不替 agent 决定用法**，设计问题回 checkpoint 记。

## 环境与命令速查

- **本机（VirtualBox VM，CentOS Stream 9）**：`DISPLAY=:0`，`XAUTHORITY=/run/user/1000/gdm/Xauthority`；sudo：`cat ~/.secrets/centos.key | sudo -S -p '' <cmd>`（**别把 `< file` 放管道末尾**）。
- **212**：`ssh zhengyp@192.168.1.212` 免密；`xvfb99.service` + openbox，`DISPLAY=:99`；**本会话末仍可能 `No route to host`，先确认开机**。
- **Windows `192.168.1.112`（Surface，Win11）**：`ssh screen@192.168.1.112` 免密；图形服务由 `screen` 登录启动项拉起、听 `127.0.0.1:9911`；本机 `ssh -N -L 9911:127.0.0.1:9911 screen@192.168.1.112`。
- **Android（华为 `MAR-TL00`）**：
  - `adb` = EPEL `android-tools`（`1.0.41`）；装包须 `--disablerepo=tailscale-stable`。
  - 设备 `12d1:107e`；UDEV 规则 `/etc/udev/rules.d/51-android.rules`；**必须先在 VM 宿主把 USB 直通进 VM**。
  - 授权：设备开 USB 调试并允许本机指纹；`svc power stayon true` 保常亮；息屏用 `KEYCODE_WAKEUP`。
  - 起服务：`python3.11 -m screenlab.cli --backend android daemon --socket /tmp/kilo/droid/run/screen.sock --blob-dir /tmp/kilo/droid/blobs`
  - 客户端：`python3.11 -m screenlab.cli --socket <SOCK> see --out droid.png` / `act pointer --x .. --y .. --snapshot SID`
- **原型**：`work/A/checkpoint/screen-lab/`（README 有 X11/Windows/Android 用法；新增 `backends_android.py`）。

## 关键引用

- 设计稿：`spec-screen-1.md`（**§0.1 术语与形态**、§5.8 Android、§7 平台、§9 原型、§10 裁决）。
- 本会话实测/系统改动/术语：`checkpoint-5.md`（§八 = 术语定案）。
- 工具口径：`spec-tools-a.md` §5（`ComputerSession` = term + fs + graphics）。
- 上游实测：`checkpoint-3.md`（X11/Wayland）、`checkpoint-4.md`（Windows）。
- 讨论：`handoff-screen-01.md`（工具分域 / 协议 / 客户端形态 / 阶段）。
- 原型：`screen-lab/`（`backends.py` X11、`backends_win.py` Windows、`backends_android.py` Android、`platform_backends.py`、`daemon.py`、`client.py`、`cli.py`）。
- 分册口径：`cogos/docs/design-agent-tools.md` §5.4 / §6 / §12；`cogos/docs/vision-system-design.md` §14 / §168–170。

## 纪律

- 跑测试用 `python3.11 -m pytest`（系统 `python` 是 3.9）。
- 结论先落 `checkpoint-5.md` / `spec-screen-1.md`，定案再更新权威分册 `design-agent-tools.md`。
- **目标侧叫"服务"，不叫 agent**；协议统一、能力面按目标挂。
- 不替 agent 决定用法；发现设计问题回 checkpoint 记，不悄悄改设计。
- 密码类只经文件与 `SSH_ASKPASS`，绝不落进命令行或工具输出。
