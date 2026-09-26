# design｜screen 体系（工作稿）· 2026-09-23

> **状态**：工作稿（对话已定方向，落码前以此为准；定案后回写 `cogos/docs/design-agent-tools.md` §16）。
> **取代**：`spec-screen-ledger.md`（凭证/账本，**作废**）、`spec-screen-client-api.md` 的 guest/credentials 部分。
> **依据**：2026-09-23 与 YZ 的讨论（Linux 形态裁决：授权=给账户）。
> **纪律**：只写"对外体系"（对象/动词/生命周期）；内部实现（Xvfb、systemd、socket、XTEST）不算体系。

## 0. 定案（本次）

| # | 决定 |
|---|---|
| D1 | **授权他 agent = 把账户给他**（用户名/密码或公钥）。软件不提供令牌/凭证层，`grant`/`redeem`/`revoke` 删除 |
| D2 | 前提是**信任**：账户=整台电脑（`term` + `fs` + `graphics`）；不信任的场景不做 |
| D3 | **多观察者 + 单控制者**：可多人看，操作权唯一（X 只有一个指针/焦点）；服务内一把输入锁 + 显式交还 |
| D4 | **viewer 保留**：人只看，不拿账户；只读画面流，服务端真拒 `act` |
| D5 | 机器级一个包（依赖 + 本体，root 一次）；账户级一条命令装配；agent 拿到账户即可用、可自改密码 |
| D6 | 图形面运输**继续走 ssh + 账户**（不引入机器级监听/公网端口） |
| D7 | 对外**只有一个入口** `screenlab`；旧脚本退为实现 |

## 1. 体系总览

**一个对象**：agent 的电脑（= 一个账户）。它有 `term` / `fs` / `graphics` 三个能力面（`computer` 工具）。

**三个面**（彼此不混）：

| 面 | 对象 | 动词 | 谁用 |
|---|---|---|---|
| 装配面 | 设备 → 账户 | `install-machine`（一次）· `add-agent` | 运维/root |
| 会话面 | 账户的图形面 | `open` / `close` | 账户本人 |
| 观察面 | 图形面的只读流 | `view` | 人（不拿账户） |

**一种凭据**：账户本身（密码/公钥）。授权不在软件里，在"把账户交给谁"。

## 2. 装配面

### 2.1 `screenlab install-machine`（root，一次）
- 依赖：`xorg-x11-server-Xvfb`、`xdotool`、`xorg-x11-xauth`（命令名 `xauth`）、`openbox`（EPEL）、`python3-pillow`（**系统级**，账户侧 daemon 要用；`pip --user` 不算）
- 本体：共享只读路径 `/opt/screenlab`（root:root 0755），所有账户共用，**不逐账户拷贝**
- idempotent、非交互；结束时打印版本与路径

### 2.2 `screenlab add-agent <name>`（root）
- `useradd -m -s /bin/bash <name>`（Xvfb 不需要 `video`/`render` 组）
- 设初始密码并打印（交给 agent；agent 之后可自己 `passwd`）
- `loginctl enable-linger <name>`（否则退出登录图形面就没了）
- 装配该账户的图形面：unit 组（`screenlab-session.target` + xvfb/desktop/daemon）、`~/.config/screenlab/session.env`、0600 xauth —— **只装配、不启动**；面由 `screenlab open` 拉起（C9）
- blobs 与浏览器 profile 属账户状态，放 `~/.local/share/screenlab`，`close --destroy` 不删

> 手工建账户仍可接受，但**建完必须跑 `add-agent`**（或等价的装配）这一步，不能省。

### 2.3 `screenlab remove-agent <name>`（root）
- 装配面的反操作：`terminate-user` + `close --destroy` + `disable-linger` + `userdel -r`。与 `add-agent` 对称。

## 3. 会话面

- `screenlab open [--resolution WxH]`：开本账户图形面（= 现 `session-start.sh create`）。幂等：已在听 → `already_listening`。
- `screenlab close`：只停服务，Xvfb/桌面留。
- `screenlab close --destroy`：退 unit、删 env/xauth/launcher；blobs/profile 保留。
- 每账户一块自管 headless Xvfb（形态见 `screenlab/install/session-create.md`）。

## 4. 授权面（无软件机制）

- agent A → agent B：A 把**自己的账户**（用户名/密码，或写入 B 的公钥）交给 B，B `ssh` 进来即可用（`term`/`fs`/`graphics` 同权限）。
- 收回：改密码 / 删 key。**承认这是粗粒度、滞后、全量的**——这是选"信任"的代价。
- 若将来需要"不给账户、能看能操作、即刻收回"，才另立令牌面（见 §9 遗留）。

## 5. 客户端

- agent 侧动词不变：`screen_capture` / `screen_act`（薄语义层，世代客户端代持）。
- 传输：账户可用 `ssh`；远端经 `ssh -L` 把 socket 转出，或客户端直接 `--sock` 本地 socket。
- CLI（调试前端）与被 agent 使用的客户端是**同一套**。

## 6. 连接角色与单控制者

- 一条连接 = 一个通道，带角色：
  - **observer**：只有 `capture`；`act` 一律拒（viewer 用）
  - **controller**：`capture` + `act`
- **单控制者**：服务内维护输入锁。空闲谁都能取；已持有则他人 `act` 被拒（`input_taken`）；持有者可显式**交还**（yield）。所有本地连接同 uid，不再区分 owner/guest。
- "谁该操作"的协商在**语言层**（两个 agent 说话），服务只保证同一时刻只有一个控制者。

## 7. 观察面（viewer）

- `screenlab view [--port N]`：在账户内起只读桥，连本账户 socket，开 **observer** 通道；HTTP 只暴露 `GET /frame`、`GET /status`；**无 `POST /act`**（服务端也会拒）。
- **绑定规则**：默认绑 **tailnet 接口**（`tailscale ip -4` 探测；无 tailnet 退 `127.0.0.1`），`--host` 可覆盖；`0.0.0.0` 不作默认、不做公网暴露。观察面本就该远程可达，人从 tailnet 上任意机器打开 `http://<node>:8800/` 即可看。
- **观看权 = tailnet 成员资格**（设备级，Tailscale 已认证）。承认这是粗粒度、不按人收回：要看即"在这个 tailnet 里"。要"不拿账户、只给某人看、可即刻收回"，才另立**观察者凭据**（见 §9 遗留）。
- 与 D6：图形面运输本走 ssh + 账户；观察面是**已划出的例外**——账户内的只读 HTTP 桥绑在该机 tailnet 上（非公网端口），观看权由 tailnet 而非账户兜底。
- **宿主防火墙要放行该端口**：firewalld 默认只放 ssh，其余端口以 `icmp-host-prohibited` 拒（现象是"没有到主机的路由"）。装机器时把 `tailscale0` 放进 trusted 区，或按 view 端口显式 `firewall-cmd --add-port`（见 `session-create.md`）。
- **按需起**（owner 主动开给某人看），不常驻。
- 人不拿账户：看到的是只读流，拿不到 `term`/`fs`，也不能改为操作。

## 8. 协议瘦身（`screen/1`）

- **删**：`grant` / `revoke` / `redeem`、凭证表与状态机、`authority` / `grant` 字段（凭证语义整体移除）。
- **留**：`info` / `displays` / `state` / `capture` / `act` / `blob_get`，`open` / `close`。
- **改**：`open` 带角色（`observer` | `controller`）。世代、`snapshot_id`、`since_hash`、blob 内容寻址不变。
- wire 未对 agent 开放过，**协议字符串仍记 `screen/1`**。

## 9. 与旧稿的关系 / 遗留

- `spec-screen-ledger.md`：**整篇作废**（三表+锁 → 通道表 + 一把锁）。
- `spec-screen-1.md` §0.0：关系 2 由"显式、可收回的授权"改为"**授权=给账户**"；判据只对"信任"场景负责。
- `spec-screen-client-api.md`：guest/credentials 章节作废，保留 capture/act/世代部分。
- **遗留（不在本轮）**：不给账户的受限授权（令牌面）；**观察者凭据**（capability URL：每次 `view` 一条一次性链接，替代"tailnet 内皆可看"）；真 GPU（**口径已定 = 与真人 VBox 齐平、不引真 GPU**，C12）；Wayland 真人桌面（Goal 2）；授权粒度（**已定 = 操作侧账户一档**，见 `issue-screen-surface-lifecycle.md` 讨论③）。

## 10. 实施顺序与判据

| 步 | 内容 | 判据 |
|---|---|---|
| 1 | 提交存档 | 工作区干净（✅ `1a818f1`） |
| 2 | 本稿 | 一页可据以落码 |
| 3 | 服务瘦身：删凭证层，保留通道+输入锁；`open` 带角色 | ✅ `pytest tests/screenlab tests/agent` 234 passed / 3 skipped |
| 4 | 统一入口 `screenlab`（install-machine / add-agent / remove-agent / open / close / view）+ 共享 `/opt/screenlab` | ✅ 靶机 `install-machine` → `add-agent agent1` 起面 |
| 5 | 靶机从零走：新设备 → `add-agent` → `open` → 自用闭环 → 同账户两连接（一观察一控制）→ `view` 只读 | ✅ 2026-09-23 全绿（见下），证据 `/tmp/kilo/sys/*.png` |
| 6 | 回写 `design-agent-tools.md` §16；旧稿标作废 | 🟡 `spec-screen-1` §0.0 / `spec-screen-client-api` 已标；§16 余 |

**第 5 步实测（2026-09-23，靶机 surface-centos-9）**
- 旧机清场后（仅 `zhengyp`，无 `/opt/screenlab`）从零走：`install-machine` → `add-agent agent1`（uid 1001 / `:10` / 1280x720）→ `open` 幂等 `already_listening` → `roles_e2e` 7/7 → `account_surface_e2e` 全过（自闭环 + 对 `:0` 与 zhengyp runtime 隔离）→ `view` 绑 tailnet，异机取 `GET /frame`（1280x720 PNG）、`GET /status`（observer / read_only）、`POST /act` 405。
- 顺带修：幂等 `open` 之前会重新分配 display 并报错值（`:11`），改为读 `session.env` 的真值（`:10`）。
- 坑：firewalld 默认只放 ssh，tailnet 端口被 `icmp-host-prohibited` 拒 → 需放行（见 §7）。
