# handoff｜P1 开工：Linux 装配脊柱 · 2026-09-20 #5

> **新会话任务**：**开工 P1（Linux 装配脊柱）**——把图形服务做成"**一次装配、会话内自启、agent 自动连**"的交付物，在 **212（无头）** 与 **本机 `:0`（桌面）** 验收。协议与 P1 决议已定，本会话起落码。
> **交接语**：读本文件；细节读 `checkpoint-5.md` **§九（协议定稿）/ §十（P1 决议）**；协议本体 `spec-screen-1.md` **§1**。
> **前序**：`handoff-screen-04.md`（形态/鉴权讨论）→ 本会话（协议冻结 + P1 决议）→ 本文件。

## 本会话性质

纯讨论（未落码）。cogos 工作区干净（`45ab216`）；原型仍在 `work/A/checkpoint/screen-lab/` 未迁。

## 已定（可当既定，不要重开）

**协议 `screen/1` 定稿**（`spec-screen-1.md` §1）：

- 动词 `info / displays / state / capture / act / blob_get`（`caps`→`info`、`see`→`capture`）。
- 坐标一律**归一化 0~1、相对整屏**；`center/size` 窗口放大；`max_dim` 只是渲染、与坐标无关。
- `authority ∈ {owned, granted}`（装配注入）+ 运行时 `grant{capture, input}`。
- 世代**连接内**、单 display **单活跃**；**不做逐像素比对**（P1 = token 身份）。
- **认证不在协议里**，`screen/1` 假定已认证字节流。

**P1 决议**（`checkpoint-5.md` §十）：

- **代码放 cogos 子包，不开新仓**；`screenlab`（proto + service）**禁止 import cogos**（保住将来 `subtree split`）。
- **Python 3.11**（install 优先 `python3.11`，退系统 `python3`）；依赖 `Pillow`(pip) + `xdotool`(系统包；RHEL 系在 EPEL，本机已验证)。
- **自启**：桌面 `systemd --user`（绑 `graphical-session.target`，本机 env 现成）；无头 **system service**（`After=xvfb99.service`）。
- **端点**：`RuntimeDirectory=screen` + `screen.sock`（桌面 `/run/user/1000/screen/`，无头 `/run/screen/`）。
- **配置**：`agent.json` 的 `computer` 块加顶层 `authority` + `graphics.endpoint`（预留 `token`）；**运输由有无 `ssh` 推**（无＝同机直连，有＝`ssh -L`）。
- **装配**：`install.sh` 输出端点 → **agent 抓取并写入配置**（零人工）；唯一必须人的是"初次建立信任"。
- **客户端**：挂 `ComputerManager`（每电脑一个、单连接）、懒连接、工具名 **`screen_capture` / `screen_act`**、**agent 不接触世代**。
- **验收**：见 `checkpoint-5.md` §十（212 与 `:0` 各跑一遍；判据 7 条 + 失败判据）。

## 开工第一步（建议顺序）

1. **迁移原型** `checkpoint/screen-lab/` → **`screenlab/`（cogos 仓库根，与 `cogos/` 包并列）**：
   ```
   screenlab/
     proto/     # framing + 协议类型（无 cogos import）
     service/   # daemon + backends（x11/win32/android）
     install/   # install.sh / uninstall.sh / units / autostart
   ```
2. **改名对齐协议**：`caps`→`info`、`see`→`capture`（先不动 `act` 与世代逻辑）。
3. 先打通 **212 直连 + system service**（无头分支最简单），再攻 **`:0` 的 `systemd --user`**（P1 硬骨头）。
4. 客户端适配进 `ComputerManager`（`import screenlab.proto`），复用 term 的 `SSH_ASKPASS` + 凭据槽。

## 还缺 / 待定（不阻断开工）

- **`screenlab` 确切包布局**：建议先"仓库根 plain package"，摩擦大了再升为子发行版（独立 `pyproject`）；`import screenlab.proto` 的可用性要顺手验证。
- **wire 细节**（写码时定）：`scroll` 字段形状、`type`/`paste` 是否合并、`key` 键名表、错误码字面量。
- **前置**：212 需开机可达（偶尔 `No route to host`）；cogos 工作区干净（`45ab216`），新会话开分支。

## 环境与命令速查

- **本机（VirtualBox VM，CentOS Stream 9）**：`DISPLAY=:0`，`XAUTHORITY=/run/user/1000/gdm/Xauthority`；`systemctl --user show-environment` 已含 DISPLAY/XAUTHORITY（GNOME 已导入）；sudo：`cat ~/.secrets/centos.key | sudo -S -p '' <cmd>`。
- **212**：`ssh zhengyp@192.168.1.212` 免密；`xvfb99.service` + openbox，`DISPLAY=:99`；无 `XDG_RUNTIME_DIR`；**先确认开机**。
- **Windows `192.168.1.112`（Surface，Win11）**：`ssh screen@192.168.1.112` 免密；服务听 `127.0.0.1:9911`；`ssh -N -L 9911:127.0.0.1:9911 screen@192.168.1.112`。
- **Android（华为 `MAR-TL00`）**：`adb` = EPEL `android-tools`（装包须 `--disablerepo=tailscale-stable`）；宿主 Unix socket；（P1 不涉及）。
- **cogos**：`/home/zhengyp/work/A/cogos`；测试 `python3.11 -m pytest tests/ -q`。
- **原型**：`work/A/checkpoint/screen-lab/`（`framing.py` framing；`daemon.py` 服务；`client.py`/`cli.py` 客户端与调试前端；`backends*.py`）。

## 关键引用

- 协议：`spec-screen-1.md` §1（**定稿**）、§1.1 坐标、§2 世代、§6 客户端形态。
- P1 决议：`checkpoint-5.md` §十；协议推演：§九。
- 工具口径：`spec-tools-a.md` §5（`ComputerSession` = term + fs + graphics）。
- 凭证/配置：`design-secrets.md`（§5 `computer` 块）。
- 上游实测：`checkpoint-3.md`（X11/Wayland）、`checkpoint-4.md`（Windows）、`checkpoint-5.md` §二–§五（Android）。
- 原型：`checkpoint/screen-lab/`。

## 纪律

- 跑测试用 `python3.11 -m pytest`；结论先落 checkpoint/spec，定案再回写权威分册 `cogos/docs/design-agent-tools.md`。
- 目标侧叫"**服务**"不叫 agent；**认证不在协议里**；`screenlab/service/` **禁止 import cogos**。
- 密码类只经文件与 `SSH_ASKPASS`，绝不落进命令行或工具输出。
