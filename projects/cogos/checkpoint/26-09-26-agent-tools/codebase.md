# codebase.md · 代码认知基线

> 对代码的**当前认知快照**（就地改，不做审计；演化过程归 `checkpoint-<N>.md`/`archive/`）。
> 以代码为准；每条结论带锚点 `file:line`，用于 spot-check。规则见 `../locus/CHECKPOINT.md`。
> 用法：先读本文件；命中即答。要下关键判断时瞄锚点。改动后按 §10"漂移检查"更版本戳。

## 版本戳

- repo: `../cogos`（本机 `/home/zhengyp/work/A/cogos`）
- branch: `feat/screenlab-p2` · HEAD: `b3cc333` · tag: `screenlab-goal2-3a-2026-09-25`
- **工作树干净**（`#50` 收尾已提交，接 `e6efb50`）：`b853576` Xfce 信任（`install/screenlab` + `install/{trust-launcher.sh,screenlab-assist-trust.desktop}` + `session-create.md`）· `74aba3c` presence 自抢占抑制（`service/{presence,daemon}.py` + `tests/screenlab/test_presence.py`）· `b6e41e8` consent_app 单实例 + 请求编号（`service/consent_app.py`）· `b3cc333` 3a 回写 `docs/design-agent-tools.md` §17。靶机 `/opt/screenlab` 已装同款代码，E4 真机验收通过。
- 已提交（`e6efb50`）各条：
  - `screenlab/install/`：`screenlab`（`consent --popup` 透传；`assist` 子命令；`install-machine` 装桌面项）· `screenlab-assist.desktop` · `session-create.md` · `session-start.sh`
  - `screenlab/service/`：`channels.py` · `cli.py` · `daemon.py` · `presence.py` · `consent_app.py`
  - `screenlab/proto/`：`client.py`（去掉重名 `close`）
  - `cogos/agent/`：`app.py` · `config.py` · `impl/graphics.py` · `impl/terminal.py`
- 进度/路线：`screen-assist-status.md`（活文档）。

## 1. 三张脸 / 入口分层

- `screenlab` = **管理面 + 观察面 + 同意入口**；`surface` = **使用面**（agent 日常跑）。安装到 `/opt/screenlab`，入口落 `/usr/local/bin/{screenlab,surface}` 与 `/usr/bin/…`。`screenlab/install/screenlab:22-46`
- 子命令分派 `case`：`install-machine`(root,一次;`--desktop-user` 落桌面项) / `add-agent` / `remove-agent` / `open` / `close` / `view` / `assist`(真人桌面的托盘 helper) / `consent`(真人本地)。`screenlab/install/screenlab`（各 `cmd_*`）
- 术语纪律：`daemon`=服务进程形态；`cli.py`=客户端调试前端；鉴权=账户（Goal 1）/ 公钥（3a），无 token。`screenlab/service/channels.py:1-15`

## 2. 生命周期模型 = "开一个程序"（Goal 1 owned 路径）

- `open` 起**一套** systemd user unit 组（`screenlab-session.target` = Xvfb + openbox + service），**不 enable**；`open` 显式起、`close` 停。`session-start.sh:406-431`
- `close` 保留 `session.env`（只有 `--destroy` 删）；分辨率存 `session.json`，跨 `--destroy` 存活。`session-start.sh:393-403`
- 幂等：已在跑且应答 → `already_listening`，沿用 session.env 原值。`session-start.sh:363-366`
- `ready()` = 活性探测：配了 TCP 探 TCP，否则探 unix socket（3a 新增）。`session-start.sh:151-153`

## 3. 每账户一块面：绑在 uid 上

- socket `/run/user/<uid>/screenlab.sock`（0700，鉴权=账户）、`~/.config/screenlab/session.env`（`SCREENLAB_DISPLAY/XAUTH/RESOLUTION`）、unit 组、Xvfb display `:N`。`session-start.sh:63-67,393-396`
- `alloc_display()` 扫 `:10..:99`，查全机 `/tmp/.X11-unix/Xn`、lock、`6000+n` 端口（check-then-create，非原子）。`session-start.sh:211-235`
- daemon 由 `serve.sh` 模板按 `session.env` 起（见 §6）。`session-start.sh:183-209`

## 4. 3a attach 路径

- `screenlab open [<account>] --attach --display :N --xauth PATH [--tcp H:P --auth REGDIR] [--consent auto|stdin|event] [--consent-socket P] [--consent-timeout S]`。`screenlab/install/screenlab:31-39,152`
- `--attach` = 服务**已存在**的 display（真人真实 `:0`），**不起 Xvfb/WM**，靠 `xdotool getdisplaygeometry` 探活。`session-start.sh:263-288`
- 约束：`--tcp` 仅配 `--attach`、且必配 `--auth`（免凭证端口不允许）；attach 状态写 `SCREENLAB_ATTACH=1`，后续裸 `open` 沿用。`session-start.sh:254-258,313-321`
- attach 服务单元 `screenlab-attach.service`（无 Xvfb/desktop）。`session-start.sh:324-331`
- 参数经 `session.env` 的 `SCREENLAB_TCP/AUTH/CONSENT/CONSENT_SOCKET/CONSENT_TIMEOUT/PRESENCE` 拼进 daemon argv。`session-start.sh:195-201`

## 5. agent 侧寻址：靠 computer 对象，不靠 display

- `ComputerManager` 每台电脑/账户一个；构造带 `graphics_endpoint` + **`graphics_key`**，`graphics` 属性懒建一个 `ScreenChannel`。`cogos/agent/impl/terminal.py:338-339,356-358,477-496`（`ScreenChannel(...)` @`:484`）
- 由 `app.py` 注入 `config.computer.graphics_endpoint/graphics_key`。`cogos/agent/app.py:166-167`；配置读 `computer.graphics = {endpoint, key}`。`cogos/agent/config.py:48-49,71-72`
- endpoint 形态 `unix:/path` 或 `tcp:host:port`；远端可走 `ssh -L` 隧道。`cogos/agent/impl/graphics.py:37-47`
- **3a（E1 新增）**：`key_path` 非空时，TCP 连接先跑 `AuthClient.attach()`（0 阶段：hello→challenge→verify→result），再 `ScreenClient.from_channel()` 复用同一通道。`cogos/agent/impl/graphics.py:59,106-112,155-170`；`close()` 一并释放 auth `:134-136`。缺省 None = 旧 unix/明文 tcp 路。
- `ScreenChannel` = one channel per machine：懒连接、每次 connect 后开成 **controller**、代持 `snapshot_id`/`frame_hash`（agent 见不到世代）。`cogos/agent/impl/graphics.py:89-119,223-235`
- agent 工具 `screen_capture`/`screen_act` **无 display/target 参数**。`cogos/agent/tools.py:1148-1250`

## 6. daemon / 会话 / 角色 / 生物在场

- daemon 分发表 `_HANDLERS`：`info/displays/open/close/state/capture/act/yield/blob_get`。`screenlab/service/daemon.py:384-398`
- ⚠️ 协议 `open`（`op_open`）= **开通道**（`role=observer|controller`,`subject`），不是生命周期 `screenlab open`。`screenlab/service/daemon.py:172`（`op_state` `:235`、`op_capture` `:255`）
- 角色位：observer=`{capture:true,input:false}`；controller=`{capture:true,input:true}`；单输入持有者 + 显式 `yield`。`screenlab/service/channels.py:29-33,145-161`
- `Channels.generation` 会话级单调；**释放输入即滚代**（`_drop_holder`），旧快照作废。`screenlab/service/channels.py:90-99`
- **真人优先 `preempt()`**：物理输入 → 当前 holder 降 observer + 滚代，返回被降席位。`screenlab/service/channels.py:165-181`
- **席位身份**：过 auth 后取 server 验证过的 `Record`（非客户端自报）。`screenlab/service/daemon.py:448-452`
- `--presence`（全局）：有 display 且装了 `xinput` 时起 `PresenceMonitor`，回调 `channels.preempt()`；另可传 `on_takeback` → `daemon.revoke_all()`（物理热键收回，键 = `SCREENLAB_TAKEBACK_KEYS`，默认 `Ctrl+Alt+Shift+Escape`）。`screenlab/service/daemon.py:88-112`
- **注入抑制窗口**：`daemon._dispatch_act` 注入前调 `presence.note_injection(window=0.5)`；`PresenceMonitor._activity` 窗口内忽略活动——VBox guest 上 XTEST 回声被 mouse-integration/PS2 复读成"物理"，按 id 分源失效，故注入方自标窗口（`daemon.py:363-369`、`presence.py:160-173,228-233`）。热键 `_key` 不看该窗口。
- `--tcp/--auth/--consent`：仅 `--auth` 设了才装 `AuthServer`；`consent=event` 装 `ConsentEndpoint`（`on_cancel` → `daemon.revoke_all()`）。`screenlab/service/daemon.py:543-570`
- **真人端桌面入口**：`screenlab/service/consent_app.py`——无窗口 Gtk 托盘（状态灯 + 弹窗同意 + 右键显示**协助地址**/收回/退出），订阅 `<registry>/consent.sock`（同 CLI hook）；`--manage-daemon` 用 `screenlab open/close` 起停守护。地址缺省 = `SCREENLAB_TCP` 否则 **tailscale IP + 8911**（`_assist_host/_assist_port`，`SCREENLAB_ASSIST_HOST/PORT` 可覆盖）；首次（无 attach+TCP 的 session.env）自动带 `--attach --tcp --auth --consent event` 起，真人免手敲长命令。入口 = `screenlab assist`（`install/screenlab` 子命令）→ 桌面项 `install/screenlab-assist.desktop`。
- **单实例 + 请求编号**（`consent_app.py`）：`_acquire_single_instance()` 持 `$XDG_RUNTIME_DIR/screenlab-assist.lock` flock，重复启动静默退出；`_request_label()` = `#N (rid[:6])`（同 request_id 复号），`_ask` 一次只弹一个（队列）+ `_handled` 去重。
- **物理热键解析**：`screenlab/service/presence.py` 从 `xinput test-xi2` 流解析按键（`EVENT type`+`detail`=keycode），只认非 XTEST 源；`keysym_keycodes()` 经 `xmodmap -pke` 解析 keysym。
- **Xfce 4.18 启动器信任**：`install/trust-launcher.sh` 写 gvfs `metadata::xfce-exe-checksum`=sha256（幂等）；`install-machine --desktop-user` 装 helper 到 `/usr/local/bin/screenlab-trust-launcher`、装 `~/.config/autostart/screenlab-assist-trust.desktop`（登录自愈），并借会话总线装时即打信任。

## 7. screenlab-auth /1 + consent

- 独立包 `screenlab/auth/`，是同 socket 的**第 0 阶段**，过了才进 `screen/1`。`screenlab/auth/__init__.py:1-7`
- `Key`（Ed25519，`<path>`=JSON `{pubkey,privkey}`）/ `AuthClient.attach(host,port)->Channel`。`screenlab/auth/client.py:29-94`
- `Registry(dir)`（登记表 `registry.json`）；`AuthServer.serve(chan)`：hello→查表（不在表= `unknown_key`）→challenge→verify（`bad_sign`/`expired`）→ consent → result。`screenlab/auth/server.py:69-144`
- consent v1：`auto_consent` / `stdin_consent`。`screenlab/auth/server.py:41-66`
- `ConsentEndpoint`（`<registry>/consent.sock`）：向真人入口广播 `request` 事件、等 `answer`；`cancel` → `on_cancel`（收回）。弹窗 slice 3 复用该签名。`screenlab/auth/consent.py:37-104,173-185`
- 真人入口 CLI：`screenlab consent` / `python -m screenlab.service.cli --auth … consent [--once|--cancel]`。`screenlab/service/cli.py:240-291`

## 8. surface（使用面）要点

- 自己读 `session.env` 定位 display；display 号不暴露给 agent。`screenlab/install/surface:16-21,33-44`
- 存活预检：`/tmp/.X11-unix/X<disp>` 不在 → `surface_not_running`（防 F1 挂死）；xdotool 全套 `timeout`。`screenlab/install/surface:50-58`
- `resolve_window` 用 `xdotool search --onlyvisible --name`（G2 修复）。`screenlab/install/surface:60-72`
- 子命令：`run`(systemd-run 瞬态单元) / `windows` / `focus` / `close`(activate+alt+F4) / `clip`。`screenlab/install/surface:74-192`

## 9. 已知缺口

- **G1｜attach 公开入口** → **已补**（§4）：`screenlab open --attach`。
- **G2｜surface close 选错窗口** → **已修**（`--onlyvisible`）。
- **G3｜收回信号非语义化** → **已改**：客户端把关闭映射为 `channel_closed`（`channel_closed` 由 `ScreenClient.call` 抛）。`screenlab/proto/client.py:103-109`
- **G4｜`surface clip` 写入不持久**：`printf | xclip -loops 1` owner 随命令退出即亡。`screenlab/install/surface:163-192`（**仍开**）
- **测试残留**：跑 consent 测试别留 `yes y` 进程（会误批准）。见 `screen-assist-exp-log.md` §5。

## 10. 漂移检查（怎么用版本戳）

- 快查 HEAD 是否动：`git -C ../cogos rev-parse --short HEAD`（= `b3cc333` 则未动）。
- 定位漂移：`git -C ../cogos diff b3cc333 -- <覆盖文件…>`；只重读变动文件，改本文件并更版本戳。
- 工作树干净；未 commit 的改动直接读 worktree。

## 11. 覆盖范围声明

- 已读透：§1–§9 引到的文件/区段（含 3a 新代码：`auth/*`、`service/presence.py`、daemon/cli 3a 段、agent 侧 graphics/auth 接线）。
- 未读/未记（问到时再读）：`screenlab/service/backends*.py`（平台 adapter 全量）、`screenlab/viewer/`、`session-stop.sh`/`session-create.md` 全文、`cogos/agent/impl/graphics.py` 之外的 ComputerManager 面（term/fs）。
