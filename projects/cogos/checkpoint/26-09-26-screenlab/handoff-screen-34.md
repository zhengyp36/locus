# handoff｜交接给新会话 · 2026-09-23 #34

> 接 #33。本轮把"体系重建"**收口并验证**：清债 + 第 5 步靶机从零验证全绿 + 提交推送。
> **上下文 ≈180k/1M（18%），未超阈值**——本轮已收口，按纪律切会话。

## 给新会话的第一句话

> 先读 `design-screen-system.md`（**滚动状态入口**）＋ `screen-goal1-progress.md` §3/§5，复述给 YZ 核；
> **代码已提交推送**（`14fca90` → `origin/feat/screenlab-p2`），第 5 步靶机验证已全绿，别重跑。
> 停下等 YZ 定两件事：**打 tag**、**第 6 步 `design-agent-tools.md` §16 回写**。
> 本阶段不设 timer，人工在旁；每完成一步 `tools/feishu_notify.py` 通知 YZ。

## 本轮结论（一句话）

- 体系重建落定：**授权 = 给账户**，一个入口 `screenlab`（`install-machine` / `add-agent` / `remove-agent` / `open` / `close` / `view`），三面 = 装配 / 会话 / 观察；**靶机从零走通并全绿**，代码提交推送。

## 本轮已完成（提交 `14fca90`，已推 `origin/feat/screenlab-p2`）

- **view 绑 tailnet**：`screenlab view` 默认绑 `tailscale ip -4`（无 tailnet 退 loopback）；`bridge.py` 去写死 `/run/user/1003`。**跨机可用**（本轮实测：靶机 8800，本机取帧）。
- **`remove-agent`**：`add-agent` 的反操作（`terminate-user` + `destroy` + `disable-linger` + `userdel -r`）。
- **`install-machine` 自检**：`Xvfb xdotool xauth openbox python3` + `python3 -c 'import PIL'`，缺一即 `exit 1`（`pip --user` 的 Pillow 不算；无 WM 会让 `act` 静默失效）。
- **去死值默认**：`viewer/bridge.py`、`service/cli.py` 的旧路径/uid 常量改从运行时推。
- **幂等 open 报真值**：`session-start.sh` 已经在听的路径改为从 `session.env` 读 display/resolution/xauth（原来会重新分配 display 并报错值 `:11`）。
- **改名**：`service/ledger.py` → `channels.py`（`Ledger` → `Channels`，`LedgerError` → `ChannelError`），`tests/.../test_ledger.py` → `test_channels.py`。
- **文档**：`design-screen-system.md` §7（绑定规则 + 防火墙）§2.3（remove-agent）§10（进度表）；`spec-screen-1.md` §0.0 关系 2（授权=给账户）+ 单控制者；`spec-screen-client-api.md` 顶部标 guest/credentials 作废；`session-create.md` 同步。

## 第 5 步靶机验证（✅ 2026-09-23，全绿）

- 靶机 `surface-centos-9`（100.100.137.78）清场后（仅 `zhengyp`，无 `/opt/screenlab`）从零走：
  `install-machine` → `add-agent agent1`（uid 1001 / `:10` / 1280x720）→ `open` 幂等 `already_listening` → `roles_e2e` **7/7** → `account_surface_e2e` **全过**（自闭环 `changed=True` + 对 `:0` / zhengyp runtime 隔离）→ `view` 绑 tailnet，**异机**（本机）取 `GET /frame`（1280x720 PNG）、`GET /status`（observer / `read_only` / input_holder=null）、`POST /act` **405** → `remove-agent` 后账户干净。
- 证据本机 `/tmp/kilo/sys/`：`before.png` / `after.png`（账户内闭环）、`view_frame.png`（异机取帧）、`view_page.html` / `view_frame.hdr` / `view.log`。
- 自检：`pytest tests/screenlab tests/agent` **234 passed, 3 skipped**（用 `python3.11`——默认 `python3` 是 3.9，缺 `pyte`）；`bash -n` 全过。

## 本轮踩到的坑

1. **firewalld 默认只放 ssh**：靶机 tailnet 上开 8800 后，异机 curl 报"没有到主机的路由"——firewalld 以 `icmp-host-prohibited` 拒非 ssh 端口。**临时** `firewall-cmd --add-port=8800/tcp` 即可（未加 `--permanent`）；部署时应把 `tailscale0` 放进 trusted。已写入 `design-screen-system.md` §7 / `session-create.md`。
2. **幂等 `open` 报错 display**：已经听着的账户，`open` 会重新 `alloc_display` 并打印新号（`:11`），真值是 `session.env` 里的 `:10`。已修。
3. **`screenlab` 脚本进不了 PATH**：rsync 到靶机的文件非可执行，且要用 `bash <path>` 调用（或先 `chmod +x`）；`install-machine` 自己会 `chmod` 并建 `/usr/local/bin/screenlab` 软链。
4. **同一 ssh 里二次 sudo 要不到密码**：`sudo -S` 的密码只喂一次。多个 root 命令要包在**一个** `sudo bash -c` 里，里面用 `runuser -u <acct>` 而非再次 sudo。

## 靶机现状（surface-centos-9 / 100.100.137.78）

- **账户只剩 `zhengyp`**（本轮建的 `agent1` 已用 `remove-agent` 清掉，`/run/user/1001` 与 `/home/agent1` 都没了）。
- **`/opt/screenlab` 与 `/usr/local/bin/screenlab` 保留**（机器级包，**没有 `uninstall-machine`**；要清需手工 `rm -rf /opt/screenlab /usr/local/bin/screenlab`）。
- **firewalld 8800 规则已移除**（只加过 runtime）。
- 依赖齐：`Xvfb` / `xdotool` / `xauth` / `openbox` / `xfce4-terminal` / `python3-pillow`(**系统级 10.0.1**) / `google-chrome`；`zhengyp` 的 `pip --user` Pillow 是 11.3.0（**别被它骗了**——账户侧 daemon 看不到）。
- 源码副本留在靶机 `/tmp/cogos-src`（rsync 自本机 `../cogos`，可删）。
- sudo：靶机 zhengyp 无本地 key，用本机 `cat ~/.secrets/centos.key | ssh zhengyp@… 'sudo -S -p "" bash -c "…"'`。

## 下一步（待 YZ / 待做）

1. **【待 YZ】打 tag**：`feat/screenlab-p2` 的 tag（上轮遗留，YZ 定）。
2. **【第 6 步】文档回写**：`cogos/docs/design-agent-tools.md` §16 指向 `design-screen-system.md` 并复述体系（其余旧稿已标作废）。
3. **未并入的裁决**：真 GPU、Wayland 真人桌面、**观察者凭据**（capability URL——替代"tailnet 内皆可看"，见 `design-screen-system.md` §9）；Windows/backends 线仍挂起。
4. 可选清债：`backends_win/android`、`install.ps1`；机器级 `uninstall-machine`（当前缺）。

## 入口

- **滚动状态（先读）**：`checkpoint/design-screen-system.md`
- 进度：`checkpoint/screen-goal1-progress.md`（§3 指针、§5 纪律）
- 目标/协议：`spec-screen-1.md` §0.0 / §1；客户端动词稿：`spec-screen-client-api.md`（guest/credentials 已作废）
- 代码：`../cogos` @ `feat/screenlab-p2`（本轮已提交推送：`14fca90`）
- 契约：`../cogos/screenlab/install/session-create.md`
- 上一轮：#33 `handoff-screen-33.md`；环境细节 #28
