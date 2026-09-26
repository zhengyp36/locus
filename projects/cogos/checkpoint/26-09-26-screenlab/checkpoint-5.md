# checkpoint-5｜图形面：Android 验证场打通（2026-09-20 #4）

> 性质：**实测 + 落码**。打通第四平台 Android，原型零接口改动接入；改了本机（VM）系统配置与设备一个电源设置（见 §六，可回退）。
> 入口：`handoff-screen-03.md`（新会话任务=Android）→ 本会话。
> 上游：`checkpoint-4.md`（X11 落码 + Windows）、`spec-screen-1.md`（设计稿）。

## 一、本会话做了什么

一句话：把 `screen/1` 接入 **Android（华为 `MAR-TL00`，Android 10 / EMUI 10）**，四平台（X11 / Windows / Android / +212 无头）全部 LLM 在环通过。

1. 确认「本机」是 **VirtualBox VM**，USB 未直通 → 手机先直通进 VM。
2. 装 `android-tools` + udev 规则 → `adb` 认到设备并授权。
3. 手工验通道（screencap / input / uiautomator）并**确定坐标映射**。
4. 新增 `backends_android.py` + `--backend` 选择，图形服务跑宿主。
5. 在时钟「秒表」上跑「看 → 点 → 再看」闭环 + 过期快照/内容寻址/`since_hash` 全套。

## 二、环境打通（含坑）

- **坑 1：本机是 VM，USB 不直通**。`lsusb`/sysfs 只见 VirtualBox 虚拟设备（`80ee`）。手机插在 VM 宿主上，VM 里 `adb devices` 为空。→ 由 YZ 在 **VirtualBox 宿主窗口「设备→USB」勾选手机**直通进 VM（VM 已配 EHCI，未另装 Extension Pack）。直通后 sysfs 出现 `12d1:107e MAR-TL00`。
- **坑 2：udev 权限**。设备先报 `no permissions`。EPEL 的 `android-tools` **不带 udev 规则**，需自建：`/etc/udev/rules.d/51-android.rules` 里 `SUBSYSTEM=="usb", ATTR{idVendor}=="12d1", MODE="0666", GROUP="users"`，再 `udevadm control --reload-rules && udevadm trigger` + `adb kill-server`。
- **坑 3：设备授权**。修好权限后为 `unauthorized`，需手机弹「允许 USB 调试」→ 勾「始终允许」。（EMUI 有时要先切「传输文件」才弹框。）
- **坑 4：宿主 dnf**。EPEL 有 `android-tools-1:33.0.3p1-1.el9`（`adb` 1.0.41），但 `tailscale-stable` 源 GPG 报错会阻断 dnf → 装包须带 `--disablerepo=tailscale-stable`。
- **坑 5：EMUI 10 = Android 10，无「无线调试」**（那是 Android 11+）。Android 10 无线 adb 需先 USB 跑 `adb tcpip 5555`。本会话走 USB，未做无线。

## 三、实测约束（设计级，已进 `spec-screen-1.md` §5.8）

- **daemon 不在设备会话内**（与前三平台相反）：设备侧只有 `adbd`，daemon 跑宿主经 adb 驱动。
- **坐标三方同空间**：`screencap` 输出 = `input` 坐标 = `uiautomator bounds`，**无 Windows 式 DPI 偏移**。实测 a11y 中心 (540,2012) 直接命中秒表按钮；顶边探针 y=2060/2200 均命中。
- **刘海/挖孔**：`wm size` 1080×2312 vs a11y 根 1080×2231（差 81px = 顶部 cutout），**原点一致、注入不受影响**。
- **`input text` 受限**：空格须 `%s`，**不能输非 ASCII**（中文无效）。
- **旋转**：翻转坐标空间，须按 `displays.rotation` 修正（本会话 rotation=0，未实测旋转）。
- **a11y 树顺手**：`uiautomator dump` 直接给树，坐标与像素同空间（比 AT-SPI 省事）——`mode=tree` / `act element` 仍是未实现项，但 Android 侧通路已确认可用。
- **无 WM 概念**：`focus` 取 `dumpsys window` 的 `mCurrentFocus`；`pointer` 恒 `null`。
- **息屏**：`KEYCODE_WAKEUP`；长实验 `svc power stayon true`。

## 四、原型改动（`screen-lab/`）

- 新增 `screenlab/backends_android.py`：`Adb`（`-s serial` 封装）、`AdbCapture`（`exec-out screencap -p`）、`AdbAct`（`input tap/swipe/text/keyevent`，含 `_KEYMAP` 键名映射）、`list_displays`（`wm size`/`wm density`/cutout rotation）。
- `platform_backends.pick(display, xauth, backend, adb_serial)`：显式 `backend` 优先，默认仍按宿主 OS。
- `daemon.py`：`ScreenDaemon`/`serve`/`serve_tcp` 增 `backend`/`adb_serial`；`platform` 报 `android`。
- `cli.py`：顶层加 `--backend {x11,win32,android}` 与 `--adb-serial`；`daemon` 允许无 `--display`（Android）。
- **接口零改动**：client/协议/快照/去重/wait_stable 全部照旧，仅加 adapter 与选择项。

## 五、验收（秒表闭环）

`python3.11 -m screenlab.cli --backend android daemon --socket ... ` 起 daemon
（`platform=android, capture=adb-screencap, act=adb-input`），随后：

- `see0` hash `cd0335aff532` → `act pointer (540,2012)`（开始）ok，新 hash `484c1880a355`
- 旧 `snapshot_id` 再 `act` → **被拒 `stale_snapshot`**
- `see1` hash `beb348b7aa57`（秒表 `00:01.24`，按钮变暂停）
- `act pointer`（暂停）ok → `see2 --wait-stable 2` hash `7e3829e87ae3`（`00:02.55`）
- `see3 --since-hash <hash2>` → `unchanged:true`
- blob 目录内容寻址，CLI `see --out` 自动 `blob_get` 落盘，字节与原图一致。

## 六、系统改动清单（可回退）

**本机（VirtualBox VM，CentOS Stream 9）**
- 装 `android-tools-1:33.0.3p1-1.el9` + `protobuf-3.14.0-17.el9`（EPEL）。
- 新建 `/etc/udev/rules.d/51-android.rules`（华为 `12d1`，MODE 0666）→ 删文件即回退。
- 临时文件 `/tmp/kilo/droid/`（截图、blob、`loop.py`）。

**设备（华为 `MAR-TL00`）**
- `svc power stayon true`（USB 时常亮）→ `svc power stayon false` 回退。
- 开发者选项开 USB 调试 + 已授权本机指纹。

## 七、遗留

- **`input text` 中文不可用**：Android 的「看/点」闭环已通，但「打字」需另找通道（`uiautomator` / IME / 剪贴板）。
- **旋转 / 多屏未实测**，`displays.rotation` 已有但未验。
- **无线 adb（Android 10 `adb tcpip 5555`）** 未做；USB 已够。
- `mode=tree` / `act element`（a11y）**通路已确认可用但未实现**——Android 是最顺的落地场。
- 手机是 YZ 旧机、**日常可用**（有 PIN、锁屏）；实验期间需保持授权与解锁。
- `tailscale-stable` 源 GPG 报错仍未修（影响 dnf）。
- 代码放点（裁决 7）等判决项未动。
- **Phase 2（图形服务持久化）未定案**：可安装 / 会话内自启 / 远程可连 / **鉴权**（现无认证），见 §八。四平台推进顺序、Android app 工作量亦未定。

## 八、术语与形态（本会话讨论定案）

**两条轴：面向 agent 是"工具 → 能力面"，面向实现是"客户端 / 服务"。**

| 概念 | 术语 | 归属 | 对应 |
|---|---|---|---|
| 工具 | `computer`（另有 `phone` / `web`） | agent | `ComputerManager` / `ComputerSession` |
| 能力面 | `term` / `fs` / **`graphics`** | `computer` 工具 | `ComputerSession` 的三个面 |
| agent 侧实现 | **图形客户端** | `computer` 工具的一部分 | 原型 `client.py`（`cli.py` 是调试前端） |
| 目标机侧实现 | **图形服务**（graphics） | 支撑 `computer` 工具 | 原型 `daemon.py` |

- **`graphics` = `computer` 工具的第三个能力面**（继 `term` / `fs`）；`screen/1` 是这一面的协议。
- **三面的目标侧支撑异构、一面一个，不合并**：`term`→sshd、`fs`→sftp（既有，不重造）；`graphics`→**图形服务（自建）**（目标上无既有"看屏/操作"通道，且必须活在交互会话内）。
- **统一只在 agent 侧**（`ComputerSession` 把三面并成一个会话对象），**不在目标机 wire 上统一**——**不存在"一个服务全包 `computer`"的形态**，`"computer 服务"`一词作废。
- 类比：`phone` 靠 feishu 服务（外部既有）；`computer.term/fs` 靠 sshd/sftp（既有）；`computer.graphics` 无既有通道 → 自建**图形服务**。
- **图形服务借 ssh 做装配/运输**（Linux/Windows）：scp 投递 → ssh 触发会话内自启 → `ssh -L` 隧道；不重造认证/传输。**Android 无 sshd、只有 `graphics` 面**，改走 LAN 直连/反连（或 `adb forward`）。
- **术语纪律**：目标侧一律叫**服务**、**不叫 agent**；`daemon` 只是服务的*进程形态*；`CLI` 是图形客户端的调试前端。

**Phase 2 方向（未定案）**：图形服务做成"**可安装、目标会话内自启、远程可连**"的交付物；四平台各自一个外壳；验收=一次装配后零人工远程 `capture/act`；**前置=鉴权**（现 socket/TCP 无认证）。

## 九、协议 screen/1 定稿（09-20 讨论）

**推演路径**：服务形态 → 从客户端用法倒推（两个时间尺度：装配罕见 / 使用频繁）→ 客户端看到什么 → 坐标怎么定（放大局部看提精度）→ 鉴权（借平台的门）→ `authority` 模型 → 增量阶梯 → 命名冲突 → 定稿。**协议已冻结，落 `spec-screen-1.md` §1。**

**核心判断**

- **鉴权不在协议里**：`screen/1` 假定"已认证字节流"；认证借平台的门（Linux/Win 借 sshd、Android 装配期借 adb、app 借独立配对协议）。服务默认只绑 loopback；Windows loopback TCP 任何本地进程可连，需本地 token。
- **授权是机器级属性**：`authority ∈ {owned, granted}`（agent 自己开出来的机器=owned；人的机器=granted）。term/fs 的"收回"＝**通道死掉**（无需改机制，agent 视为终态、不重连）；graphics 的收回＝服务内 grant 被撤。撤回**整机**，各自在自己那层执行。
- **坐标归一化 + 窗口**：照搬 `image_ctx` 模型（`center/size` 归一化 0~1）——放大局部看提高估坐标精度；`max_dim` 降级为渲染细节、与坐标无关。
- **世代按帧**：换窗口看图不作废世代；`act` 有效 ⇔ 帧未变。

**五条裁决（定稿默认）**

1. 世代作用域 ＝ **连接内**，断连即作废。
2. 同一 display **单活跃、串行**。
3. 断连原因：**协议内用错误码**（`consent_revoked`）表达收回；**传输断连不区分、一律终态**。
4. `act` 坐标 **只收相对整屏的归一化坐标**（窗口相对是糖，后置）。
5. `authority` **只由装配注入**；运行时只有 `grant` 会变。

**命名**：`see` → **`capture`**（避开看图工具 `image_ctx.see`）；`caps` → **`info`**（capabilities，与 capture 撞脸）。

**Phase 2 阶梯（待开工）**：P0 协议定稿 → **P1 Linux 装配脊柱**（install + `systemd --user` 自启 + 客户端自动隧道 + manager 接线）→ P2 断连即终态 → P3 `authority` + granted 的 `stop` → P4 Windows 外壳 → P5 会话内可见把手 → P6 Android app。**P1 阻塞项＝代码放哪（裁决 7）**。

**未定（实现细节，不阻断）**：`scroll` 字段形状、`type`/`paste` 是否合并、`key` 键名表、错误码字面量。

## 十、Phase 2 · P1（Linux 装配脊柱）决议（09-20 讨论）

**P1 目标**："干净机器 → 一次装配 → 之后远程 `capture/act` 零人工；重启后仍成立"。

**代码与语言**

- **裁决 7 定案：放 cogos 子包 `cogos/screen/`，不开新仓**；`screenlab` 做成独立包（`proto` + `service`，**禁止 import cogos**），cogos 客户端只 import `screenlab.proto`——保住将来 `git subtree split` 的退路。理由：服务是"要装到目标机的交付物"，需独立打包，但不需要独立仓；cogos 里 feishu 已有服务端先例。
- **语言 Python 3.11**（install 优先找 `python3.11`，没有退系统 `python3`）。理由：`proto` 与 cogos 共享，不该被 3.9 语法限制。实测 CentOS Stream 9 `python3.11` 在**官方 appstream**。
- 依赖：`Pillow`（pip，装 venv 内）+ `xdotool`（系统包；RHEL 系在 **EPEL**，本机已验证）。`xdotool` 主流发行版都有、非风险；后手是 ctypes 直调 `libXtst`。

**自启外壳（两种）**

- **有交互桌面（`:0`）**：`systemd --user`，`PartOf`/`WantedBy=graphical-session.target`。实测本机 `systemctl --user show-environment` 已有 `DISPLAY=:0` 与 `XAUTHORITY=/run/user/1000/gdm/Xauthority`（GNOME 已导入）→ 不用 env 桥。**判据：`show-environment` 里有 DISPLAY 就直接用 unit；没有则装 XDG autostart 桥**（先 `import-environment DISPLAY XAUTHORITY` 再 start）。
- **无头（212 `:99`）**：**system service**，`After=xvfb99.service`（跨 manager 无法排序，故不用 user unit；无头用 `loginctl enable-linger` 的替代方案放弃）。
- 服务生命周期 = 图形会话/显示：会话没了服务就死。

**端点**

- 服务声明 `RuntimeDirectory=screen`，socket＝`screen.sock`：桌面 `/run/user/1000/screen/screen.sock`，无头 `/run/screen/screen.sock`（systemd 自动建目录、owner/权限对，不依赖 `XDG_RUNTIME_DIR`）。路径在重启后稳定。

**配置（`agent.json` 的 `computer` 块）**

- 扩 `design-secrets.md` §5：加顶层 `authority: owned|granted` + `graphics.endpoint`（预留 `token`）。
- **运输从配置推**（不加开关，与 term/fs 同构）：无 `ssh` → 同机直连 unix socket；有 `ssh` → 客户端起 `ssh -L`。
- P1 只实现 `transport: "unix"`；`token` 只预留。

**装配流程**

- `install.sh` 在目标机执行 → 输出端点路径 → **agent 抓取输出并写入 `agent.json`**（零人工）。装配留 agent 侧（`spec-screen-1.md` §0）；**唯一必须人的是初次建立信任**（交 ssh 凭据 / 设备授权 / 系统同意框）。`provision` 自动化包装后置。

**打包与落点**

- `install.sh`（探测 python/venv/xdotool/有无图形会话 → 建 venv → 装依赖 → 拷包 → 写配置 → 装 unit/autostart → enable → **打印端点**）＋ `uninstall.sh`（停、禁自启、删文件）。
- 落点：system＝`/opt/screenlab` + `/etc/screenlab/` + `/run/screen/`；user＝`~/.local/share/screenlab` + `~/.config/screenlab/` + `/run/user/<uid>/screen/`。
- P1 直接 scp 目录 + 跑 `install.sh`；wheel/zipapp/PyInstaller 后置。
- 范围＝**通用 Linux/X11**（核心不写发行版假设，distro 差异收在 `install/`），验证只在 **CentOS Stream 9 + GNOME/Xorg**；**Wayland 不在内**。

**客户端接线**

- **graphics 客户端挂 `ComputerManager`（每台电脑一个，单连接）**；`ComputerSession` 只当寻址句柄（与 fs 一致）。
- **懒连接**（首次用才建），持有到 `stop()`；P1 不做空闲断开。
- 工具名 **`screen_capture` / `screen_act`**（避开看图工具 `see`/`mark`）。
- 运输选择与凭据复用 term 那套（`SSH_ASKPASS` + `COGOS_SECRET_*`），不新造。
- 装配层 C 读 `computer` 块构造 `ComputerManager`。

**世代语义（agent 可见面）**

- **agent 不接触 `snapshot_id` / `frame_hash`**；客户端按 display 自动绑最近一次 `capture` 的世代（B 层代持；A 核心不代持）。
- **P1 服务端校验＝token 身份**（必须最新签发；act 后作废、**强制重看**）。**不做逐像素比对**——屏幕一直在变（时钟/光标/动画），逐像素相等会导致每次 act 都被拒。
- 后置：`frame_changed` 提示（不阻断）；`act element` 时按 id **重新解析 bounds**（防布局漂移，随 a11y）；粗比对容差**不做**。

**验收判据**（212 与 `:0` 各跑一遍）

1. 一次装配；2. 重启/重登后**自启、无人起服务**；3. agent **自动连**（不手工 daemon / 不手工隧道）；4. 真实 `capture → act → capture` 且第二次见**预期变化**；5. 过期 token 被拒、`since_hash` 命中回 `changed:false`；6. **干净卸载**无残留；7. wire 形状未变。

- **212**：验无头外壳、install/uninstall、世代；agent 从本机 `ssh -L` 过去。前置：212 可达（偶尔 `No route to host`）。
- **`:0`**：验 `systemd --user` 会话内自启、同机直连、闭环（P1 真正的硬骨头）。
- **失败判据**：需人工登录目标机才能用（**会话登录本身不算**）、需人工起服务/建隧道、重启失效、只有手工起 daemon 才通（现况）。
- **不在 P1**：鉴权/同意（granted）、Windows、Android app、多客户端、Wayland、a11y/element、`provision` 自动化。

> 纪律：跑测试用 `python3.11 -m pytest`；结论先落 checkpoint / spec，定案再更新权威分册 `cogos/docs/design-agent-tools.md`。
