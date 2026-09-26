# 2026-09-19 cogos agent 工具实现（A 层分批）

> 工作流：`cogos` 的 agent 工具实现（A 实现层）。一批一会话，逐批交接。
> 产物与依据都在工作区 `../checkpoint/26-09-26-agent-tools/`（尚未归位 locus）。

## 依据与产物

- 权威：`cogos/docs/design-agent-tools.md`（工具分册）；总纲 `design-selfdrive-agent.md`。
- 计划：`../checkpoint/26-09-26-agent-tools/plan-tools-impl.md`（4 批、铁律、会话协议）。
- 接口：`../checkpoint/26-09-26-agent-tools/spec-tools-a.md` v1.1。
- 过程/裁决：`../checkpoint/26-09-26-theory-residual/checkpoint-1.md` §19~§22；每批 `handoff-tools-0N.md`。

## 进度

- 批次 1（Clock／DraftStore／TimerService／PhoneCapability）@ `53c4e9f`。
- 批次 2（`ComputerManager`／`ComputerSession`，**本机** pty term，`execute` 删除）@ `ecedcbb`；测试 1082 passed。
- 批次 3（`FsChannel`／`TransferEngine`）未开工。

## 现状（09-19）

- term **只实现本机 `$SHELL`**（`impl/terminal.py`，`pty.fork()`）；**远端（`ssh -tt` / sftp）未实现、无测试** —— 全仓 `ssh|sftp` 零命中。
- 设计 §5.3 远端（非交互化、密码走 `write`、sftp）是未落项。
- YZ 指示（09-19）：**先实现并验证远端 term**，再回批次 3。

## 临时测试账号（09-19）

- 账号 `tangyu` / 密码 `cog-ty-0005`；家目录 `/home/tangyu`，机器根 `/home/tangyu/machine`。
- 用途：**同一账号既可当本地账号（`su - tangyu` / `sudo -u tangyu`），也可当远端账号（`ssh tangyu@localhost` 密码登录）**，同时验证本地与远端两种情况。
- 环境已就绪：本机 sshd 在 22 端口、密码登录可用（用 `SSH_ASKPASS` 验证过 `ssh tangyu@localhost` 成功）。
- 创建/清理脚本：`../checkpoint/26-09-26-agent-tools/setup-test-account.sh`（`create`/`check`/`su`/`ssh`/`clean`）。

## 远端 term（09-19 已实现并验证）

- 代码：`impl/terminal.py` 增 `SshTarget(host,user?,port?)`；`ComputerManager(ssh=..., ssh_bin="ssh", ssh_options=[...])`。`ssh=None`＝本机 `$SHELL`，否则会话顶层进程＝`ssh -tt`。密码不入 A，agent 经 `session.write` 送。`term.done`＝ssh 退出。
- 测试：`tests/agent/test_impl_term_remote.py`（fake ssh 注入 4 例 + `COGOS_SSH_TEST=1` 真实 localhost 例）。
- 真机验证：`ssh tangyu@localhost` 密码登录 → 远端 shell，`whoami`/`$HOME` 正确，`exit`→`term.done`。
- `pytest tests/ -q`：1086 passed, 2 skipped。
- 裁决与口径：`../checkpoint/26-09-26-theory-residual/checkpoint-1.md` §23；spec 升 v1.2（§9.2）。
- 待 YZ：远端目标是否接入 `agent.json`「电脑」配置 + `sync_reachable` 归属（批次 3）。

## 凭证/密码注入（09-19 已实现并验证）

- 方案草案：`../checkpoint/26-09-26-agent-tools/design-secrets.md`。原则：**登录自动完成、agent 不见密码；write_key 是受控出口（绑定+不回显）**。
- 代码：`impl/secret.py`（`SecretStore` 槽位 id 不透明、不随值变、0600；`askpass_env`）、`impl/askpass_helper.py`（SSH_ASKPASS helper）；`terminal.py` 加 `ssh_env`/`secrets`/`session.context`/`write_secret`（绑定校验+`_muted_echo`）；薄 B `terminal_write_key`。
- 真机验证：`SSH_ASKPASS_REQUIRE=force` 自动登录（无提示、agent 不参与）；`write_secret` 绑定+不回显。需 OpenSSH ≥8.4；host key 必须 accept-new/no，否则密码会当 host-key 答案。
- `pytest tests/ -q`：1096 passed, 3 skipped。
- 未实现（第二刀）：armed/一次性 token、槽位列举、`agent.json` 电脑配置接线、密钥/ControlMaster。


