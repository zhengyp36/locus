# handoff｜工具实现 · 批次 3（新会话入口）· 2026-09-19

> **新会话任务**：**先审核，无问题才做批次 3**（会话衍生：`FsChannel`／`TransferEngine`）。批次 2.5（远端 term ＋ 凭证注入）已完成并提交。做完批次 3 写 `handoff-tools-04.md`。

## 入口

> `cogos` @ **`24fa192`**（`feat(agent): add remote pty sessions and credential injection`）；批次 2 在 `ecedcbb`，批次 1 在 `53c4e9f`。工作区干净。

1. **`work/A/checkpoint/plan-tools-impl.md`** ← 先读：批次划分（含 2.5）、铁律、既定决策、会话协议。
2. 权威：`cogos/docs/design-agent-tools.md`（工具分册）；总纲 `cogos/docs/design-selfdrive-agent.md`。
3. A 接口形状：`work/A/checkpoint/spec-tools-a.md` **v1.2**（§9.1 批次 2、§9.2 远端 term）。
4. 过程与裁决：`checkpoint-1.md` **§19~§24**。
5. 凭证方案（草案）：`work/A/checkpoint/design-secrets.md`。
6. 代码现状：
   - A：`cogos/agent/impl/{base,clock,draft,timer,phone,terminal,secret}.py` ＋ `askpass_helper.py`（`__init__` 汇总）。
   - 薄 B：`cogos/agent/tools.py`（time／timer／scratch／terminal specs，含 `terminal_write_key`）。
   - 装配：`cogos/agent/app.py`（`_QueueSink` 把 A `Signal` 映射成 `AgentEvent`）。
   - 测试：`tests/agent/test_impl_{clock,draft,timer,phone,term,term_remote,secret}.py`、`test_scratch.py`、`test_terminal.py`。
7. 依赖：`pyte`（批次 2）；远端 ssh 需 OpenSSH ≥ 8.4（`SSH_ASKPASS_REQUIRE=force`）。测试账号 `tangyu`/`cog-ty-0005`。

## 批次 2.5 结果（已完成 · 09-19）

- **远端 term**：`impl/terminal.py` 增 `SshTarget(host,user?,port?)`；`ComputerManager(ssh=…, ssh_bin="ssh", ssh_options=…, ssh_env=…, secrets=…)`。`ssh=None`＝本机 `$SHELL`；否则会话顶层进程＝`ssh -tt`。`session.context`（远端＝`user@host`，本地＝`local`）。
- **凭证注入**：`impl/secret.py`（`SecretStore` 槽位 id 不透明、不随值变、0600；`askpass_env`；`UnknownSecret`／`SecretBindingError`）＋ `impl/askpass_helper.py`。ssh 子进程注入 `SSH_ASKPASS*` ⇒ **登录自动完成、agent 不见密码**。`session.write_secret`／B `terminal_write_key`＝受控手动出口（**绑定校验**＋`_muted_echo` 抑制回显）。
- **验证**：`pytest tests/ -q` → **1096 passed, 3 skipped**；`_run_fake` 冒烟通过；真机 `tangyu@localhost` 验 ①手动 `write` 登录 ②`SSH_ASKPASS` 自动登录 ③`write_secret` 绑定+不回显。
- **未完成（第二刀/待定）**：armed/一次性 token、槽位列举、`agent.json`「电脑」配置接线、密钥/`ControlMaster`、设计 §5.3 `BatchMode` 措辞。

## 第一步（必做）：重审

- 审 spec §6／§7（transfer／A 信号一览）与 `design-agent-tools.md` §6／§9 是否自洽：**fs 从 term 派生**、transfer 端点／方向／`TransferAccepted.dest` 语义、**机器端通道**。
- 审 spec §10 批次 3 范围：第 5 项后半（fs 路径基准、`fs.read` 上限/超时）、第 6 项（`Machine` 对象、transfer 是否可等结果）。
- 按 09-19 讨论，**两处口径需先定**（见下「开工前待定」），定案回记 `checkpoint-1.md`。
- **有疑义 → 报告并停，问 YZ**（不悄悄改设计）。

## 批次 3 交付（审核通过后）

- **范围**：`FsChannel`（挂 `ComputerSession`）＋ `TransferEngine`（草稿根 ↔ 机器根）。
- **文件**：`impl/fs.py`、`impl/transfer.py`（命名开工时定）；`tests/agent/test_impl_fs*.py`、`test_impl_transfer*.py`。
- **语义**：fs 从会话衍生（`session.fs` 存在与否＝机器"可同步可达"）；会话 `close` → 挂它的 fs 失效（不重连）；`fs.*` 仅普通文件，无 list/search/delete；transfer 只 copy、整文件、无 offset；草稿端走 `DraftStore.put`（临时超＋本轮豁免），机器端走 `session.fs`。
- **最薄 B**：fs 接 `read_file`／`write_file`／`edit_file`（现本地实现，接上后替换）；transfer 新增 `transfer` 工具，沿用扁平名。
- **验收**：`python3.11 -m pytest tests/ -q` 绿；`_run_fake` 冒烟；单测覆盖 fs read/write/edit、transfer 双向（含二进制/大文件走 `put`）。

## 开工前待定（09-19 讨论遗留，需本会话定案）

1. **机器端通道 × 远端无 fs**：09-19 讨论倾向 **远端 term 也提供 fs 通道供 transfer 用，但不暴露给 agent**（agent 不被 fs 阻塞；远端走 transfer→草稿→读写）。⇒ spec §5 的 `不可同步可达时＝None` 与 §6「机器端走 `session.fs`」需改口径：**通道存在性 ≠ 工具暴露**；`sync_reachable` 改为 **C 层暴露闸门**。待定。
2. **`sync_reachable` 归属/配置**：作机器属性、由装配注入（A 不读配置）。是否接 `agent.json`「电脑」段（本刀未接）待定。
3. **transfer 是否可等结果**：按 design §4／§9 倾向**纯事件、不可等**（`transfer()` 仅返回 `TransferAccepted`）。
4. **fs 路径基准**：相对路径以 `machine_root` 为基（与 transfer「机器根」一致）、绝对路径原样；`fs.read` 上限沿用 2000 行/2000 字符，本机 v0 无需超时。
5. **draft 端 `ext` 来源**：机器→草稿时按源文件后缀派生？`put` 必填 `ext`。
6. **来源戳**：design §9「向草稿侧附来源戳（吸收不可信输入）」spec §6 无字段。
7. **B 层 `transfer` 端点编码**：扁平工具如何表达 `DraftRef{id}` vs `MachineRef{session_id, path}`。

## 批次 2.5 遗留注意事项

- `execute` 已删（09-19）；旧 pipe 语义由 `terminal_exec`＋`observe` 覆盖。
- `manager.stop()` **不发** `term.done`；`session.close()` 才发且 `cancelled=True`。
- `term.done` 发出前等读循环 drain ≤0.5s；Python 3.11 无 `loop.add_child_handler`，退出码用独立 `_wait_child` 任务 `os.waitpid` 收。
- `observe` 默认末尾屏（`limit` 默认＝屏行数）、offset 1-based；`total_lines`＝历史＋屏。
- `session.fs` 现返回 `None`（批次 3 接）；远端 `open(cwd=…)` 暂不生效。
- SSH 密码路径**不加 `BatchMode`**；host key 必须 `accept-new`/`no`（否则密码被当 host-key 答案）。

## 纪律（照 plan §0）

- 三问每步走；发现设计问题回 `checkpoint-1.md`；不替 agent 决定用法；旧代码对象级一次性替换。

## 收工

- 写 `work/A/checkpoint/handoff-tools-04.md`，含 plan §4 六字段。
