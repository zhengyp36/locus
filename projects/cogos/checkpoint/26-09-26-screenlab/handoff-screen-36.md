# handoff｜交接给新会话 · 2026-09-23 #36

> 接 #35。本轮**已落码**：把 `issue-screen-surface-lifecycle.md` 的 C1–C12 / B1–B2 落地并靶机验证。
> 上下文：`screen-goal1-progress.md`；目标（唯一约束）：`spec-screen-1.md` §0.0。
> **临时执行看板 `plan-screen-surface-lifecycle.md` 已完成使命、已删**（其内容摘要见本文件）。

## 本轮做了什么（全部已验证）

- **C4 删协议 `paste`**：`proto/protocol.py` `ACT_OPS`、`service/daemon.py`、`service/cli.py`、`cogos/agent/tools.py` enum；剪贴板归命令 `surface clip`。spec §1 同步。
- **C1/C2 生命周期 = "开一个程序"**：`close` 改停**整套面**（`systemctl --user stop screenlab-session.target`，Xvfb+WM+服务全退、丢窗口）；unit **不再 enable**（不随开机/登录常驻），并 `disable` 旧安装遗留的 autostart。
- **C3 `close --destroy` 保留 resolution**：resolution 写入随 destroy 保留的 `~/.local/share/screenlab/session.json`，`open` 优先读（显式 `--resolution` > 现存 `session.env` > state）。
- **C9 `add-agent` 只装配不启动**：`session-start.sh` 新增 `--no-start`（写 unit/session.env/xauth，不拉起面）。
- **B1 `open` 复用 display**：`session-start.sh` create 路径先读 `session.env` 的 display/resolution/xauth，不再重分配。
- **C6–C9 新命令面 `surface`**（`screenlab/install/surface` → `/usr/local/bin/surface`）：`run`(detach, 用 `setsid -f`，禁 `exec`/`&`) / `windows` / `focus` / `close` / `clip`；自读 `session.env`、不暴露 `:N`；`--help` 标所属面与授权。`screenlab` 保留管理面 + `view` 观察面，头注标四面。
- **B2 `tool_loop_e2e`** 去硬编码 `1920x1080`，从 capture 的 `size` 推。
- **清账**：`spec-screen-1` §10 逐条标注 + §7 Phase 2 更新；`spec-screen-client-api.md` 标 `paste` 作废；`design-screen-system.md` §2.2/§3/§9；`cogos/docs/design-agent-tools.md` §16 回写。
- **三项形态实测**（写回 `issue-screen-surface-lifecycle.md` §三）：WebGL=**none**（无 GPU 通病，非 Xvfb 独有）· screen=1920x1080/DPR=1 · 字体 135（CJK 靠 Droid Sans Fallback）。

## 执行中发现并修（非原清单）

- **home 目录 root 归属 bug**：`/home/<acct>/.config`、`.local` 被 root 建出 → 账户侧 chrome 无法写而启动失败。修 `session-start.sh` `as_dir()`（逐级 chown 给账户）；靶机已 `chown -R` 修复 6 账户。**这是装配期 bug，影响"agent 能用电脑"**。
- **`xclip` 缺失** → `surface clip` 依赖；已加入 `install-machine` 依赖（dnf/apt）。

## 两个待 YZ 的开放项

1. **打 tag / 提交**：本轮代码**未提交**（工作树含 1 处 #35 遗留未提交：`screenlab/install/screenlab` 的 install-machine 入口修复）。按纪律未擅自提交。
2. **C5 自动部分（socket activation）**：已按 YZ 同意后置（半做会破坏懒连接，理由见 #35 handoff §2.1）；`WebGL=none` 是否要 `--enable-unsafe-swiftshader`（痕迹取舍）。

## 验证记录

- 本机：`python3.11 -m pytest tests/screenlab tests/agent -q` → **234 passed, 3 skipped**。
- 靶机：`surface` 五项全通（`run` 1.4s 返回）；`close`→target inactive/Xvfb/socket 消失；`open` 复用 `:16`；`--destroy` 后 resolution 1920x1080 保留；`tool_loop_e2e` 全绿（size=[1920,1080]，pointer 480,540）。

## 靶机与坑

- 靶机 `surface-centos-9`（100.100.137.78）；`alice` 现 **`:10` 1920x1080**（destroy 后换号；C3 只保 resolution，不保 display）。其余账户未动。
- sudo：`cat ~/.secrets/centos.key | ssh zhengyp@100.100.137.78 'sudo -S -p "" bash -c "…"'`；**多个 root 命令包在一个 `bash -c`**，账户侧 `runuser -u <acct>`。
- 部署：先 `rsync` 本机 `../cogos` 到靶机 `/tmp/cogos-src`（含新代码），再 `bash /tmp/cogos-src/screenlab/install/screenlab install-machine --prefix /opt/screenlab`（**注意 chmod 要在远端跑**，脚本在 `/tmp` 无可执行位时用 `bash` 调用）。
- e2e：`runuser -u alice -- env HOME=/home/alice XDG_RUNTIME_DIR=/run/user/1001 PYTHONPATH=/tmp/cogos-src python3.11 /tmp/cogos-src/tests/screenlab/e2e/tool_loop_e2e.py --sock unix:/run/user/1001/screenlab.sock`；跑前先 `surface run google-chrome about:blank`。
- 本机 `python3` = 3.9（`cogos/feishu/config.py` 用 `X | None` 跑不了），一律用 `/usr/bin/python3.11`。

## 入口

- 目标（唯一约束）：`spec-screen-1.md` §0.0
- 结论/依据：`issue-screen-surface-lifecycle.md`（C1–C12 + B1–B2 + 实测）
- 体系：`design-screen-system.md`；契约：`../cogos/screenlab/install/session-create.md`
- 代码：`../cogos` @ `feat/screenlab-p2`：`screenlab/{proto,service,viewer,install}`、`cogos/agent/impl/graphics.py`、`cogos/agent/tools.py`
- 上一轮：#35 `handoff-screen-35.md`；进度：`screen-goal1-progress.md`
