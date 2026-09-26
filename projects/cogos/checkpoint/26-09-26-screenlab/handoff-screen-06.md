# handoff｜P1 落码完成 → 讨论回写与下一步 · 2026-09-20 #6

> **新会话任务**：**讨论本会话产出怎么处置、下一步往哪走**——① 文档回写（`checkpoint-5.md` §十 / 权威分册 `cogos/docs/design-agent-tools.md`）；② 分支 `feat/screenlab-p1` 是否合并、要不要 PR；③ `:0`「人工重登」这条最严格判据要不要补做；④ P2 阶梯选哪条（断连即终态 / `authority`+`grant` 的 stop / Windows 外壳 / 会话内把手 / Android app）。**不是**继续落码。
> **交接语**：读本文件即可开会话；细节读 `checkpoint-5.md` **§九（协议推演）/ §十（P1 决议）**、`spec-screen-1.md` **§1（协议定稿）/ §2（世代）/ §6（客户端）**。
> **前序**：`handoff-screen-05.md`（协议冻结 + P1 决议）→ 本会话（P1 落码 + 双机验收）→ 本文件。

## 本会话性质

**落码 + 真机验收**（不是讨论）。代码已提交、已推送，**未合并 master、未建 PR**。

- 分支：`feat/screenlab-p1`（基于 `45ab216` master），已 `push -u`。
- 提交：
  - `5adb665 feat(screenlab): add installable graphics service (screen/1)`
  - `0773e73 feat(agent): wire the graphics face onto ComputerManager`
- PR 链接（若要用）：`https://github.com/zhengyp36/cogos-dev/pull/new/feat/screenlab-p1`

## 已定（可当既定，不要重开）

**代码落点与形态**

- `screenlab/`（**cogos 仓库根**，与 `cogos/` 包并列）三层：`proto/`（framing + 协议常量 + 坐标模型 + 薄客户端）、`service/`（daemon + x11/win32/android 后端 + 调试 CLI）、`install/`（install/uninstall + units）。
- `screenlab` **禁止 import cogos**（保住 `subtree split` 退路）；`cogos` 侧只 import `screenlab.proto`。
- 装机版 = `/opt/screenlab` + `/etc/screenlab` + `/run/screen`（system）；`~/.local/share/screenlab` + `~/.config/screenlab`（user）。venv 用 `--system-site-packages`。

**协议实现口径（本会话定的实现细节，spec 里原为"未定"）**

- wire envelope 的动词用字段 **`op`**；`act` 的**动作名放在 `kind`**——JSON 里两个同名 `op` 会撞（这是落码时踩到的坑）。
- `act` 形状：`{op:"act", kind, snapshot_id, ...}` → `{ok, op, acted, hint:{frame_hash}}`；`pointer{kind:"pointer",x,y}` 的 `x/y` 是**归一化**，服务端按 display 几何换算设备像素。
- `capture` 响应= spec 形状 + 一个额外的 `capture_backend`（诊断用，additive）；`info` 额外带 `capture_backend/act_backend/pid`。
- 世代：**连接内**（`ConnState` 每连接一份，不是 daemon 全局），`capture` 每次 mint，`act` 校验后**作废**并只回 `hint.frame_hash`（下一刀 act 必须重看）；`since_hash` 命中回 `changed:false` 且不下发 blob。
- 错误码字面量：`stale_snapshot` / `consent_revoked` / `unsupported` / `not_found` / `unknown_op` / `backend_error`。
- `key` 用 `keys`；`scroll` 用 `{dy, at:{x,y}}`；`element`/`mode=tree` 未实现（返回 `unsupported`）。

**端点与自启（P1 脊柱，双机实测）**

- 桌面 `:0`：**user unit** `screenlab.service`（`PartOf`/`WantedBy=graphical-session.target`，`RuntimeDirectory=screen`）→ `/run/user/<uid>/screen/screen.sock`。
- 无头 212：**system unit** `screenlab.service` + `screenlab-xvfb.service`（Xvfb `:99` `1280x800x24` + openbox）→ `/run/screen/screen.sock`。
- **关键坑**：system unit 必须 `User=<调用者>`（install.sh 取 `SUDO_USER`），否则 `/run/screen` 归 root 0700，本机 `ssh -L` 进不来。
- **WM 是前置**：无 openbox 时 `_NET_ACTIVE_WINDOW` 缺失、键盘事件乱跑（Xvfb unit 里一起拉起 openbox）。
- 装配：`bash screenlab/install/install.sh --user | --system [--resolution WxH]`，末行打印 `SCREENLAB_ENDPOINT=unix:<path>`；`uninstall.sh` 同参。

**客户端接入**

- `cogos/agent/impl/graphics.py::ScreenChannel`：**每机一个、懒连**；`authority`/`graphics.endpoint` 来自 `agent.json` 的 `computer` 块；**没配 endpoint 就不暴露 graphics 面**。
- 运输由配置推：无 `ssh` → 同机直连 unix socket；有 `ssh` → **自动起 `ssh -L`**（`StreamLocalBindUnlink=yes`，复用 term 的 ssh options 与 `SSH_ASKPASS` env），退出即清理。
- **世代由 channel 代持**：`capture` 记 `snapshot_id`+`frame_hash`，`act` 自动带上并作废；`act` 后未重看 → `NoFrame`。`capture` 默认带上次 `frame_hash` 作 `since_hash`。
- 工具：`screen_capture`（存图到 `<work>/screen/frame-N.png` 并返回路径，可喂 `see`）/ `screen_act`。

## 验收记录（P1 判据 1–7，双机真机）

| # | 判据 | 结果 | 证据 |
|---|---|---|---|
| 1 | 一次装配 | ✓ | `install.sh` 单次执行，输出端点 |
| 2 | 重启后自启、无人起服务 | ✓ | 212 `sudo reboot` 后两 unit `active`、socket 在、openbox 在 |
| 3 | 会话重登后自启 | ✓ | `:0` 用 gdm 重启造新会话，unit 随 `graphical-session.target` 自动 active |
| 4 | agent 自动连 | ✓ | 远端无手工 daemon、无手工隧道（`ScreenChannel` 自建） |
| 5 | `capture→act→capture` 见预期变化 | ✓ | 212：chrome 输入框被输入 `hello screen/1 from ComputerManager`；`:0`：点顶栏时钟弹出日历面板 |
| 6 | 过期 token 拒 + `since_hash` 回 `changed:false` | ✓ | 服务端 `stale_snapshot`；静态区域 `changed:false` |
| 7 | 干净卸载无残留 | ✓ | 双机：unit/文件/进程/`/run` 全清 |
| — | wire 形状未变 | ✓ | 逐字段脚本核对 `info/displays/capture/act/state` |

测试：`python3.11 -m pytest tests/ -q` → **1198 passed / 4 skipped**（新增 `tests/agent/test_screen.py` 17 条）。

## 待 YZ 裁决（本会话刻意没做）

1. **文档回写**：`checkpoint-5.md` §十 要不要增补"落码结果"？权威分册 `cogos/docs/design-agent-tools.md` 要不要回写？按纪律是"定案后再回写"，故停在等你。
2. **合并**：`feat/screenlab-p1` → `master`？走不走 PR？（我按 handoff「新会话开分支」落的，没动 master。）
3. **`:0` 最严格判据**：本会话是 gdm 重启造的新会话验证自启；**真"人工登出→登入"没做**（且实测 **GDM 登出后不会自动登录**，自动登录只在会话启动时生效，登出会停在 wayland greeter，而 greeter 上 `xdotool` 够不着）。
4. **P2 选哪条**（`checkpoint-5.md` §九阶梯）：P2 断连即终态 / P3 `authority`+grant 的 `stop` / P4 Windows 外壳 / P5 会话内可见把手 / P6 Android app。
5. **flake**：`tests/agent/test_impl_term_remote.py::test_write_secret_resolves_and_mutes_echo` 在并发负载下偶发失败（单跑必过），与本批改动无关，是否单开一条 ISSUE。
6. **打包**：`pyproject.toml` 未显式声明 `screenlab`（setuptools 自动发现能捡到，但没跑过 `pip install .` 验证）；P1 装机走的是"拷目录 + venv"，wheel/zipapp 属后置。

## 环境与命令速查

- **cogos**：`/home/zhengyp/work/A/cogos`；分支 `feat/screenlab-p1`；测试 `python3.11 -m pytest tests/ -q`。
- **screenlab 调试 CLI**：`cd <PREFIX> && python3.11 -m screenlab.service.cli info|capture|act|...`，端点用 `SCREEN_SOCKET`。
- **本机 `:0`**：端点 `/run/user/1000/screen/screen.sock`；`systemctl --user status screenlab.service`；`~/.local/share/screenlab/serve.sh`。
- **212**：`ssh zhengyp@192.168.1.212` 免密；sudo 用 `~/.secrets/centos.key`（**实测有效**：`cat ~/.secrets/centos.key | sudo -S -p '' <cmd>`）；unit `screenlab.service` + `screenlab-xvfb.service`；端点 `/run/screen/screen.sock`。
- **验收入口脚本**（本会话临时件，在 repo 外）：`/tmp/kilo/accept_screen.py <endpoint|remote:unix:/run/screen/screen.sock> '[{act…}]'`。
- **`:0` 解锁（实测可行，非必须）**：密码从 `~/.secrets/centos.key` 走 stdin → `xdotool type --file -`；**先确认 `sudo fgconsole` == 用户会话 VT**（否则是在 GDM greeter 上白忙）；截图前先动鼠标唤醒（**DPMS 超时全 0，屏幕会立刻黑**，黑帧≠出错）。
- **锁屏判据**：`loginctl show-session <sid> -p LockedHint`（别看像素）。

## 关键引用

- 协议：`spec-screen-1.md` §1（定稿）、§1.1 坐标、§2 世代、§6 客户端形态。
- 决议：`checkpoint-5.md` §九（推演）、§十（P1 决议 + 验收判据 + 失败判据）。
- 凭证/配置：`design-secrets.md` §5（`computer` 块）。
- 上游实测：`checkpoint-3.md`（X11）、`checkpoint-4.md`（Windows）、`checkpoint-5.md` §二–§五（Android）。
- 代码：`screenlab/`（proto/service/install）、`cogos/agent/impl/graphics.py`、`cogos/agent/tools.py::make_screen_specs`、`tests/agent/test_screen.py`。

## 纪律

- 跑测试用 `python3.11 -m pytest`；结论先落 checkpoint/spec，定案再回写权威分册 `cogos/docs/design-agent-tools.md`。
- 目标侧叫"**服务**"不叫 agent；**认证不在协议里**；`screenlab/` **禁止 import cogos**。
- 密码类只经文件与 `SSH_ASKPASS`，绝不落进命令行或工具输出。
