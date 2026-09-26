# handoff｜工具实现 · 批次 4（新会话入口）· 2026-09-19

> **新会话任务**：**先审核，无问题才做批次 4**（B/C 收口：契约层 `ToolDef`、装配层 `assemble(role/context)`、分包、prompt／白名单由装配派生、按需装配）。做完批次 4 写收尾并归位。
> **交接语**（新会话直接说）：读 `work/A/checkpoint/handoff-tools-04.md`，先审核，无问题再做批次 4。

## 入口

> `cogos` @ **`3315562`**（`feat(agent): add fs channel and transfer engine derived from sessions`）；批次 2.5 在 `24fa192`，批次 2 在 `ecedcbb`，批次 1 在 `53c4e9f`。工作区干净。

1. **`work/A/checkpoint/plan-tools-impl.md`** ← 先读：批次划分、铁律、既定决策、会话协议。
2. 权威：`cogos/docs/design-agent-tools.md`（§2 三层分离、§3 清单、§12 分包、§13 A 对象）。
3. A 接口形状：`work/A/checkpoint/spec-tools-a.md` **v1.3**（§9.1／§9.2／§9.3 变更记录）。
4. 过程与裁决：`checkpoint-1.md` **§19~§26**（批次 3 见 §25／§26）。
5. 代码现状：
   - A：`impl/{base,clock,draft,timer,phone,terminal,secret,fs,transfer}.py` ＋ `askpass_helper.py`（`__init__` 汇总）。
   - 薄 B：`cogos/agent/tools.py`（time／timer／scratch／terminal／**fs**／**transfer** specs，扁平名）。
   - 装配（临时）：`cogos/agent/app.py` 的 `_build_specs()`（**批次 4 要收口的对象**）。
   - prompt／白名单（硬编码，待装配派生）：`config.py:render_system_prompt`、`consciousness.py:toolset_names`、`experiment/selfdrive/loop.py:TASK_TOOLSET`。
6. 测试：`tests/agent/test_impl_{clock,draft,timer,phone,term,term_remote,secret,fs,transfer}.py`、`test_scratch.py`、`test_tools.py`、`test_app.py`。
7. 依赖：`pyte`、**`asyncssh`**（批次 3）；远端 ssh 需 OpenSSH ≥ 8.4（`SSH_ASKPASS_REQUIRE=force`）。测试账号 `tangyu`/`cog-ty-0005`（`COGOS_SSH_TEST=1` 跑真机例）。

## 批次 3 结果（已完成 · 09-19 · 已提交 `3315562`）

- **fs**：`impl/fs.py` `FsChannel`＋`LocalBackend`／`SftpBackend`（asyncssh，`SecretStore` 延迟取密码）；`session.fs`＝通道存在性，`session.fs_exposed = sync_reachable ∧ fs 存在`；会话关→fs 失效、不重连。
- **transfer**：`impl/transfer.py` `TransferEngine`，发起即返回 `TransferAccepted`（machine→draft 用 `DraftStore.reserve` 定 id），后台完成发 `transfer.done{handle_id, dest, bytes, error}`；纯事件不可等。
- **A 增补**：`DraftStore.reserve(ext)`／`get_bytes(id)`；fs 异常 `NotFound`／`SpecialFileUnsupported`。
- **薄 B**：`make_fs_specs`（`read_file`/`write_file`/`edit_file` 改**需会话 id**）＋ `make_transfer_spec`；旧 `work_dir` 三 spec 删除。
- **装配**：`app.py` 本地 `sync_reachable=True`、按闸门挂 `fs.*`、注册 `transfer`；`config.py`／`consciousness.py` 同步（并补遗漏的 `terminal_write_key`）。
- **验证**：`pytest tests/ -q` → **1119 passed, 4 skipped**；`_run_fake` 冒烟通过；真机 `tangyu@localhost` sftp `write`→`read` 往返通过（host key accept-new）。

## 未完成 / 遗留

- `experiment/selfdrive/loop.py:TASK_TOOLSET` 仍是旧无 `id` 的 `read_file` 语义（实验脚本，未改）。
- `agent.json`「电脑」配置（含 `sync_reachable`）接线未做 → 归 C（批次 4）。
- design §11「来源被抹平」前置 bug（事件入口 source）未动。
- 批次 2.5 旧遗留仍在：armed/一次性 token、槽位列举、密钥/`ControlMaster`。

## 第一步（必做）：重审

- 审 design §2／§12 与现状：`ToolDef` 契约表、`assemble(role/context)`、包＝命名空间前缀、白名单／prompt 单一来源。
- 审三处硬编码（`app.py`／`config.py`／`consciousness.py`，外加 `loop.py`）如何收敛为装配派生。
- **有疑义 → 报告并停，问 YZ**（不悄悄改设计）。

## 批次 4 交付（审核后拆分 · 2026-09-19）

> 审核结论：批 4 拆为 **4a（工具层收尾／B）** 与 **4b（装配／C）**。**4a 已完成**（本会话）；**4b 缓**，待出现第二个消费者再议。

- **4a（已完成）**：`ToolDef` 声明表作单一来源；registry／白名单／system prompt 由它派生；保留扁平名。见 `checkpoint-1.md` §28。验收＝`pytest` 1119 passed, 4 skipped＋`_run_fake` 冒烟通过。
- **4b（缓 · 待单独讨论）**：`assemble(role/context)`；分包（授权单位）；按需装配；`agent.json`「电脑」配置接线（§25.2）。触发条件＝机制面向工具或按机器/会话裁剪的需求出现（design §18.1 不预先造抽象）。
- **产出（4b 后）**：收尾；把 `work/A/checkpoint/` 归位 `locus/projects/cogos/checkpoint/`。

## 纪律（照 plan §0）

- 三问每步走；发现设计问题回 `checkpoint-1.md`；不替 agent 决定用法；旧代码对象级一次性替换。

## 收工

- 写收尾 handoff ＋ 归档归位；`checkpoint-1.md` 追加批次 4 小节。
