# 电脑独立 = 一等公民机器（10-30 落码）

> 状态：已落码（cogos commit `907fe23`）。电脑从"agent 进程内单台 ComputerManager"升为"按账户寻址、可命名、可切默认的一等对象"；隔离边界从"进程降权"纠正为"电脑账户身份"。
> 来路：讨论"给 agent 独立账户怎么适配"→ 发现方案 A（进程级降权）放错边界 → 定"电脑独立、agent 进程统一、body 工具走默认机器"。

## 核心结论

### 电脑 = 账户（不是进程）

- **隔离在"电脑"，不在 agent 进程**：agent 进程保持统一（一个普通 uid，管自己的 agent_root 元数据）；body 工具（terminal/fs/vision）的副作用发生在**电脑的账户身份**下。本机独立账户 = `ssh tangyu@localhost`，局域网/远程主机账户 = `ssh user@host`，二者同一抽象（`SshTarget`）。
- **为什么不是进程降权**：agent 进程降成 tangyu uid 后，它反而能直接 file 读自己的 `memory/state/events`（都是自己文件），破了"意识层不可见 agent_root"这条访问层纪律。正确边界是 directory-roots 的两个根：agent_root 靠访问层归属管、machine_root 靠账户身份管。

### 机器抽象（MachineSpec / MachineRegistry）

- `MachineSpec`：`{name, root, target(SshTarget|None), secret_id, sync_reachable, graphics_*}`。`target=None` = local（进程身份）；`SshTarget(host,user,port,identity_file)` = 账户身份（key 认证）。
- `MachineRegistry`：`dict[name→ComputerManager]` + `current` 指针 + `add/remove/get/switch/list/names`。**add/remove 保持普通方法**（不假设只从 config 调），预埋将来 inbound 协助：入站事件 = 运行时 `registry.add` 一个临时机器，上层不动。
- 多机 transport 插拔：将来 inbound 只是 `MachineSpec` 多一种来源（事件注入），不是新架构。

### body 走默认机器 / toolbox 切默认

- terminal/fs spec 工厂改为接受 **callable manager**（`_resolve_manager`），每次调用解析 `registry.current` → body 自动作用在"当前默认机器"。
- `DefaultSession` 加 `machine_key`（当前机器名），切机器后缓存 session id 失效、在新机器重开。
- `machine.list`/`machine.switch` 进 body 的 `machine` 组（切默认电脑让 body 跟着切）；完整 toolbox（含 screen/web/vision）留后续。

### ssh key 认证（专用 key）

- `SshTarget.identity_file` + `ComputerManager._ssh_argv` 加 `-i`；`SftpBackend` 加 `client_keys`（key 认证时不解析密码）。
- 专用 key（非复用 zhengyp 通用 id_ed25519）落在 `agent_dir/secrets/id_<machine>`，公钥追加到目标账户 authorized_keys。

## why（为什么对）

- 电脑是"agent 的肢体延伸"，不是 agent 本身——agent 自己（思考/记忆/决策）和它操作的外部机器是两个东西，账户边界正好画在这条线上。
- 本机账户/远程账户/将来"协助他人"是同一个抽象（账户寻址），不需要三套机制；这也是预埋的核心。
- "系统默认丢、agent 主动记"同构：电脑账户能碰什么由 OS 定，agent 碰不碰得到凭据由 SecretStore/key 边界定，两层都靠"机制隔离"而非"模型自觉"。

## 被否 / 纠错

- **方案 A 进程级降权**（agent 进程换 tangyu uid）→ 否：破"意识层不可见 agent_root"，且飞书/lm 凭据仍在 agent 进程里、攻击面更大。
- **方案 B 会话级 setuid**（pty child 里 setuid）→ 否：需 root/CAP_SETUID 入口，fs 的 LocalBackend 在主进程直接 Path.read_bytes 不走子进程、仍以主账户读，隔离不彻底。
- **方案 C 本机 loopback ssh** → 复用为当前实现（本机账户 = ssh localhost），但"反向 ssh 协助"那半留待 inbound。
- **root 默认拼 name 的 bug**（显式 root 也被拼 `/<name>`）→ 修：默认才 `machine/<name>`，显式 root 原样用。

## 落码结果（`907fe23`）

- `machines.py`（新）：MachineSpec + MachineRegistry。
- `config.py`：`computers` 列表 + `default_computer`（agent.json），向后兼容（空则 fallback 一台 local）。
- `assemble.py`：MachineRegistry 接线 + ssh/identity + terminal/fs resolver + body 走默认。
- `tools.py`：`_resolve_manager` + `make_machine_specs`（machine.list/switch）。
- `body_catalog.py`：加 `machine` 组。
- `meta_tool.py`：DefaultSession 加 `machine_key`。
- `impl/terminal.py` / `impl/fs.py`：SshTarget.identity_file + SftpBackend client_keys。
- 测试：`test_machines.py`（新）+ test_config 多机解析 + test_body 切机器重开 session；全量 1333 passed（+新增 ~10）。

## 验证（真机）

- 专用 key `~/.cogos/agent/tangyu/secrets/id_tangyu` → tangyu authorized_keys（免密 ssh）。
- terminal 在 tangyu 身份（`whoami`=tangyu、cwd=/home/tangyu）；fs（sftp key auth）读写 tangyu home。
- 隔离验证：tangyu 身份 `cat /home/zhengyp/.ssh/id_rsa`、`ls ~/.cogos`、`~/.secrets` 全部"权限不够"。

## 悬置 / 遗留

- **多台切换真实端到端**未验（当前只配 tangyu 一台）；machine_key 切换逻辑有单测。
- **vision/screen 未 resolver 化**（make_vision_specs/make_screen_specs 仍绑单 manager）——body 当前未接 vision，不影响；接 vision 时一起做。
- **body 的 vision/web/time 未接线**（impl 不在 impl_registry）——既有接线缺口，非本次引入；10-29 已标"未验证"。
- **tangyu 密码登录未关**（可选项，key 已通）；tangyu 是临时账户、密码临时。
- inbound 协助 transport 未实现（只预埋 registry add/remove 接口）。
