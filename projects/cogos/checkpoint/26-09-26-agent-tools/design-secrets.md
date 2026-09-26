# 方案｜凭证与密码注入（secrets / askpass / write_key）· 2026-09-19

> 工作稿（未写回权威分册）。依据讨论：09-19 会话，远端 term 之后。
> 相关：`cogos/docs/design-agent-tools.md` §5.3（远端密码）、§15.2（秘密／外发防护，整体遗留）；`checkpoint-1.md` §23／§24。

## 1. 目标

1. **远端登录 agent 全程不见密码**：认证由机制自动完成，密码不进 agent 上下文、不进日志。
2. **需要 agent 主动送密码的场合**（sudo、自定义交互）仍可用，但必须是**受控出口**，不能任意外泄。
3. 密码不因"藏明文"而安全，安全靠**绑定与授权**。

## 2. 凭证槽位与句柄

- **槽位（slot）**：一条凭证 = `{id, context, name?, secret}`。
  - `context`：目标标识，如 `tangyu@localhost`；本地用途约定 `local`。
  - `id`：**不透明句柄**，`sec_<hex>` 随机；**标识槽位、不随密码值变**（轮换后 id 不变）。不是"密文"（无加解密）。
- **不按值去重**：相同 (context, secret) 不合并；避免泄露"两个 id 相等＝密码相同"，也让轮换不漂移。若将来必须按值去重，须用**每库随机盐的 HMAC** 派生，禁裸 hash。
- **解析只在机制侧**：`SecretStore.resolve(id) -> secret`。agent 只在需要时拿 id，从不拿明文。
- 存储：JSON 文件，权限 `0600`。

## 3. 远端登录：SSH_ASKPASS 自动注入（v0 主路径）

- ssh 子进程 env 注入：
  - `SSH_ASKPASS=<repo>/cogos/agent/impl/askpass_helper.py`（可执行；读 env 里的库路径+id，打印密码）
  - `SSH_ASKPASS_REQUIRE=force`（**需 OpenSSH ≥ 8.4**；否则无 tty 才用 askpass）
  - `COGOS_SECRET_STORE=<store path>`、`COGOS_SECRET_ID=<slot>`
- 效果：ssh 自己问 helper，**不弹提示、不写屏、agent 不参与**（09-19 已在真 pty 验证）。
- **硬要求**：必须给 `StrictHostKeyChecking=accept-new`（或 `no`）+ `UserKnownHostsFile`；否则 host key 提示也走 askpass，**密码会被当作 host-key 答案发出去**。
- 明文只存在于 ssh 子进程 env（同用户可经 /proc 看到，v0 接受）；不进 agent 上下文。

## 4. `write_key`：受控的手动出口

- A：`ComputerSession.write_secret(slot_id)` → manager 解析并写入 pty（追加换行，按"输密码+回车"语义）。
- **绑定校验**：`slot.context` 必须等于会话 context（远端＝`user@host`，本地＝`local`），否则拒绝（抛 `SecretBindingError`）。挡住"把凭证送到伪造提示"。
- **echo 抑制**：写入前后对 pty `tcsetattr` 清 `ECHO` 再恢复；即使处于意外状态也不回显。
- 薄 B：`terminal_write_key(id, key)`（沿用扁平名）。
- **第二刀（未实现）**：armed/一次性 token（只在"机制判定该会话正请求该凭证"时允许），以及 agent 可见的槽位列举。当前仅绑定+echo 抑制。
- **残余风险**：程序拿到 secret 后可自行打印；绑定+不给任意出口是主防线，echo 抑制只是二道。

## 5. 与既有设计的边界

- **agent 可见面**：v0 不加"列出槽位"工具；`terminal_write_key` 需调用方已知 slot id。slot id 从哪来由 provisioning 决定（v0 未接）。
- **`agent.json` 机器配置**：**本刀未接**。提案（待 YZ）：
  ```json
  "computer": {
    "root": "work",
    "sync_reachable": true,
    "ssh": {"host": "localhost", "user": "tangyu", "port": 22},
    "credential": "sec_xxxx",
    "secrets_path": "secrets.json"
  }
  ```
  缺省（无 `computer`）＝本机、无凭证。装配层（C）读取并构造 `ComputerManager`。
- **`write` vs `write_secret`**：`write` 保持原样（原始字节）；`write_secret` 是唯一能取明文写入的出口。
- **与 `sync_reachable`**：仍是 `fs.*` 暴露闸门（批次 3 定）；与凭证无关。

## 6. v0 范围

- 已实现：`SecretStore` + askpass helper + `ComputerManager(ssh_env=..., secrets=...)` + `session.write_secret` + B `terminal_write_key` + 绑定 + echo 抑制。
- 未实现（第二刀/待定）：armed/一次性 token、槽位列举、`agent.json` 电脑配置接线、密钥/ControlMaster、轮换与清理流程。
