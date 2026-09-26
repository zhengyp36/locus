# handoff｜工具实现 · 批次 2（新会话入口）· 2026-09-18

> **新会话任务**：**先审核，无问题才做批次 2**（term 核心）。一批一会话；做完批次 2 写 `handoff-tools-03.md`。

## 入口

> 批次 1 已提交：`cogos` @ `53c4e9f`（`feat(agent): implement A-layer tool objects with thin B wiring`）；设计分册提交 `a05df97`。工作区干净。

1. **`work/A/checkpoint/plan-tools-impl.md`** ← 先读：批次划分、铁律、既定决策、会话协议。
2. 权威：`cogos/docs/design-agent-tools.md`（工具分册）；总纲 `cogos/docs/design-selfdrive-agent.md`。
3. A 接口形状：`work/A/checkpoint/spec-tools-a.md` **v1**。
4. 过程与裁决：`checkpoint-1.md` **§19／§20／§21**。
5. 代码现状：
   - A：`cogos/agent/impl/{base,clock,draft,timer,phone}.py`（`__init__` 汇总）。
   - 最薄 B：`cogos/agent/tools.py`（含 `make_time_specs`／`make_timer_specs`／scratch specs）。
   - 装配：`cogos/agent/app.py`（`_QueueSink` 把 A `Signal` 映射成 `AgentEvent`）。
   - 测试：`tests/agent/test_impl_{clock,draft,timer,phone}.py`、`test_scratch.py`。

## 第一步（必做）：重审

- 审 `spec-tools-a.md` §5／§13（term）与 `design-agent-tools.md` §5 是否自洽，尤其 pty／exec／done／cancel／observe／notify 语义。
- 审 spec §10 剩余项中批次 2 范围（第 5 项：pty 库、winsize 初值、fs 路径基准、`fs.read` 上限/超时——`fs` 属批次 3，本批只需 pty 选型与 winsize）。
- **有疑义 → 报告并停，问 YZ**（不悄悄改设计；设计问题回 `checkpoint-1.md`）。
- **无问题 → 开始批次 2。**

## 批次 2 交付（审核通过后）

- **范围**：`ComputerManager`／`ComputerSession`（term 面）。
- **文件**：`impl/terminal.py`（或 `impl/computer.py`，命名开工时定）；`tests/agent/test_impl_term*.py`。
- **语义（design §5.1 已定死）**：会话＝持久 pty 顶层进程；`exec`＝写 `command+"\n"`；`write`＝原样送字节；**命令完成不由机制推断、不发事件**；`term.done`＝shell 退出；**无 busy**；`cancel`＝`\x03` 幂等；`observe`＝pyte 渲染屏、按行。
- **最薄 B**：`TerminalManager` → `ComputerManager`，沿用 `terminal_*` 扁平名；`execute` 保留到本批上线后再删。
- **验收**：`python3.11 -m pytest tests/ -q` 绿；`_run_fake` 冒烟；单测覆盖发命令／看屏／发键／notify token／cancel 幂等。

## 批次 1 遗留注意事项

- `execute` 按计划保留，待批次 2 term 上线后删除。
- `DraftStore` id 在全部被淘汰后会复用（v0 接受）。
- `DraftStore.put`/`write` 的 `ext` 已校验（`InvalidExt`，禁路径分隔符），仅允许 `[A-Za-z0-9._-]`；多后缀（`tar.gz`）覆盖时复用原路径。
- `TimerService` 只持久化 pending，`next_id` 一并持久化；触发/取消后再 `cancel` 抛 `UnknownTimer`（非幂等，spec §5 的 `cancel` 幂等指 term）。
- **升级债务（已接受 v0）**：旧草稿布局 `scratch/active/<id>.md` + `history/` + `scratch.json` 不再读取，无迁移；旧草稿升级后不可见。
- `terminal.py` 仍是旧 pipe 实现，本批整体替换。

## 纪律（照 plan §0）

- 三问每步走；发现设计问题回 `checkpoint-1.md`；不替 agent 决定用法；旧代码对象级一次性替换。

## 收工

- 写 `work/A/checkpoint/handoff-tools-03.md`，含 plan §4 六字段：入口／已完成／未完成／验证结果／新发现／下一批（范围、依赖、开工前待定）／待 YZ。
