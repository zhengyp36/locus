# handoff｜工具现状过目与讨论（新会话入口）· 2026-09-20

> **新会话任务**：**过目当前工具现状，再讨论**（谈方向/取舍，**先不动遗留**）。不是开工批次，不写代码。
> **交接语**：读 `work/A/checkpoint/handoff-tools-09.md`，先过目工具现状（下面已给盘点），再谈。
> 前序：`handoff-tools-08.md`（web 异步化）→ `handoff-phone-files-01/02.md`（phone 文件收发，本批已收束）。

## 入口

- 权威分册：`cogos/docs/design-agent-tools.md`（**落后于代码**，见"现状 vs 分册"）。
- 批次计划：`work/A/checkpoint/plan-tools-impl.md`（批次 1~4，4b 缓）。
- 讨论记录：`checkpoint-1.md`（§16~§28）、`checkpoint-2.md`（§一~§二十，工具时间形态/模型可见面/事件面）。
- spec：`spec-tools-a.md` v1.4、`spec-tools-web.md`、`spec-phone-files.md`。
- 代码基线：`cogos` @ **`45ab216`**（已 push `origin/master`，工作区干净）。
- 测试：`python3.11 -m pytest`（系统 `python` 是 3.9，缺依赖）；全量 **1181 passed / 4 skipped**。

## 现状盘点（本会话过目 · 09-20）

### 三层分离：A/B 已落，C 半落

- **A 实现层** `cogos/agent/impl/`：能力对象，普通签名，不懂 schema/LLM/role，可脱离 cu 单测。
- **B 契约层** `cogos/agent/tools.py`：`ToolDef(schema+name / fn / time_form / prompt)` **单一来源**（批次 4a 已落，registry／白名单／system prompt 由它派生）。
- **C 装配层** `cogos/agent/app.py::_build_specs()`：仍是**硬编码拼表**；`assemble(role/context)`／分包／按需（4b）**未做**。

### 工具清单（`_build_specs` 实际装配，32 个）

| 包 | 工具 | time_form |
|---|---|---|
| phone | `send_msg`、`phone_download`、`phone_send_file`、`phone_cancel`、`phone_spool_list`、`phone_spool_delete` | async×3 / sync×3 |
| web | `search`、`fetch`、`web_cancel` | async×2 / sync |
| draft（旧名 scratch） | `scratch_write/read/edit/mark/unmark/list` | 全 sync |
| transfer | `transfer` | async |
| term | `terminal_open/exec/write/write_key/observe/cancel/list/close`（8） | 全 async |
| time | `time_now`、`set_timezone` | sync |
| timer | `set_timer`、`cancel_timer`、`list_timers` | sync |
| fs | `read_file`、`write_file`、`edit_file` | sync（**条件装配**：`sync_reachable=True` 才挂） |

### A 层对象（`impl/`）

`Clock` · `DraftStore`(443) · `TimerService` · `PhoneCapability`＋`Spool` · `ComputerManager`/`ComputerSession`(653, pty+VT) · `FsChannel`(Local/Sftp) · `TransferEngine` · `WebService` · `SecretStore`＋`askpass_helper`。返回普通值/类型化异常；Signal 独立于 `AgentEvent`。

### 事件面（推）

`Signal` → `app._QueueSink` → `AgentEvent` → `_consume_events` → `IncomingMessage(source="system")` → `consciousness.on_message`。事件工具面：`phone.receive`、`timer.notify`、`term.done`/`term.notify`、`transfer.done`、`phone.download_done`/`send_file_done`。

### 测试

`tests/agent/` 22 文件；`test_impl_{clock,draft,timer,phone,phone_files,spool,term,term_remote,secret,fs,transfer,web}.py` ＋ `test_tools.py`(452)。

### 现状 vs 权威分册 `docs/design-agent-tools.md`（**文档落后于代码**）

- §3 清单**缺** web 三件、phone 文件/spool 六件、`terminal_write_key`、`time_now`。
- §4 未把 `search`/`fetch` 列为 async。
- §14 仍写「`search`/`fetch` 冻结、不改动」——**已异步化**（`impl/web.py`）。
- §10 phone 已追平（files 落）。

## 可讨论的点（**只讨论，先不动**）

1. **C 装配形态**：4b 的 `assemble(role/context)`／分包（授权单位）／按需／`agent.json`「电脑」接线；触发条件＝出现第二个消费者。
2. **`time_form` 是死元数据**：只声明、无人消费（已 grep），"异步不阻塞"无机制保证，靠 B 自觉＋测试兜底——要不要补机制或去元数据。
3. **term 时间形态**：`term.*` 整族一刀切 async，但 `observe`/`list`/`cancel` 实为取值。
4. **异步工具的作业/事件面统一**：并发上限、在途调用可观测列表、`transfer` 无 cancel、统一事件信封、草稿淘汰保护、历史回读面。
5. **文档追平**：§3/§4/§14 与代码对齐的时机（定案后还是现在）。
6. **机制面向工具**（`load`/`retrieve`/`record_segment`…）整体未做——是否仍在当前范围。

## 遗留（**本会话动过盘点，未处理**；详见 `plan-tools-impl.md` / `handoff-tools-08.md` 与 `locus/projects/cogos/ISSUES.md`）

- 4b 装配；并发上限 `max_inflight_jobs`；同 URL 在途去重；草稿淘汰保护；统一事件信封；作业可观测列表；上下文压缩/丢弃（`checkpoint-2.md` §十八）。
- `transfer` 无 cancel；`time_form` 死元数据；`experiment/selfdrive/loop.py:TASK_TOOLSET` 旧 `read_file` 语义。
- 批次 2.5 旧遗留：armed/一次性 token、槽位列举、密钥/`ControlMaster`、轮换与清理。
- design §11「来源被抹平」入口 bug；草稿 id 复用坑（`DraftStore._scan_next_id`）。
- phone 侧：transfer `scheme:path` 未落、spool 原始文件名未持久化、批量/并发、`/FILE` 幂等内存态、`/FILE` 失败不重试（ISSUES 已记）。
- 流程：`plan-tools-impl` §4b 的**归位**动作（`work/A/checkpoint/` → `locus/projects/cogos/checkpoint/`）未做。

## 纪律（照 `plan-tools-impl.md` §0）

- 结论先落 `checkpoint-2.md`／spec，定案再更新权威分册 `design-agent-tools.md`。
- 不替 agent 决定用法；发现设计问题回 `checkpoint-1.md` 记，不悄悄改设计。
- 跑测试用 `python3.11 -m pytest`。

## 收工

- 若讨论出定案 → 更新 `design-agent-tools.md`（§3/§4/§14 等）并另起 handoff。
- 若只是过目无定案 → 记回 `checkpoint-2.md` 续节。
