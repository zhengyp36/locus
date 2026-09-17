# checkpoint-3｜task-5 复核 + pytest 提速(task-6) + Kilo 常驻多通道(task-7) + 主线回归建议

> 2026-09-11 晚。承接 `checkpoint-2.md`。本会话：验收 task-5、把 task-6/task-7 交给工位 B、给出回主线的建议。
> 恢复顺序：`locus/active.md` → `locus/projects/cogos/current.md` → `status.md` → `plan.md` + `state.md` → `checkpoint-2.md` → 本文件。

## 一、task-5 复核（通过）

- 范围：验收遇错即止 + phase 计时。改动仅 `cogos/agent/loop.py`、`tests/agent/test_loop.py`（B worktree `work/B/cogos-s2`，**未 commit**）。
- 契约逐条符合：`exit_codes` 长度恒=len(steps)/未跑记 `None`、`ran_steps`、`passed` 三条件、短路尾注；`perf_counter`+`round(,2)`、每步 `{model,acceptance,round}`、最终 `{setup,model,acceptance,notify,total}`、setup 计时在 `Agent()`→`init()` 间、4 处 `_notify` 全走计时闭包。
- 验证：局部 13 passed；全量 **1021 passed, 1 skipped**。
- 结论：task-5 的"计时"证明浪费主要在 pytest 每轮全量（~60s），不在单条 loop。

## 二、pytest 慢的根因 + task-6（已交 B）

- `tests/feishu/test_ws.py::TestWSClient::test_start_sets_started` ~13–18s = **首次 `import lark_oapi`**（`cogos/feishu/ws.py:179-183` `_build_handler` 懒加载；实测 import 10–11.5s）。`tests/` 无其它文件用 lark。→ mock `_build_handler`。
- `tests/feishu/test_monitor.py::test_running_heartbeat_fail` 5s = `cogos/feishu/monitor.py:39` `asyncio.sleep(5)` 未 mock。
- `tests/feishu/test_monitor.py::test_heartbeat_fail_triggers_recovery...` 5s = `monitor.py:29` `time.sleep(5)` 未 mock。
- `tests/agent/test_terminal.py::test_observe_while_busy` ~1s = 真子进程 `sleep(1)`，**语义必要**（可微缩）。
- 合计约 28s / 61s 纯浪费。交接件 `tasks/task-6-pytest-speedup.md`；gate 全量 <40s、测试数/断言不变。
- 结构性根治（A 线，未做）：**分层验收**——轮内只跑目标测试、全量只终局一次。

## 三、Kilo 常驻 / 事件唤醒 / 多通道 → task-7（已交 B）

- 讨论主线：工具调用不该阻塞对话；完成应发事件唤醒 agent。最优=事件唤醒；次优=有人聊则后台、否则前台；**ESC 问题根因=命令绑死在当前回合**（解耦后人的消息也是事件，与完成事件同队列）。
- 查证（关键事实）：
  - Kilo 有 `@kilocode/sdk`：`createKiloServer` / `createKiloClient` / `createKiloTui`；client 有 `session.prompt` / `promptAsync` / `abort` / `command` / `shell`。
  - 插件 `Hooks.event({event})` 收**全部总线事件**，含 **`session.idle`**、**`pty.exited`**（= terminal_done 等价物）、`message.part.updated`；`PluginInput.client` 可注入 prompt。
  - 飞书**出站已有** MCP：`~/.config/kilo/tool/feishu_server.py`（+ `kilo.jsonc` 的 `mcp.feishu`）；入站复用 cogos `feishu` daemon/ws。
- task-7 = **spike（可行性+设计）**，`tasks/task-7-kilo-resident-multichannel.md`；**B owner（设计+实现同一人）**。待验证 7 项 + YZ 决策（上下文共享 vs 分通道、飞书信任边界）。

## 四、分工模型调整（YZ 提出）

- 探索型任务：**一个 owner 设计+实现同一人**，避免"A 想一遍 B 再想一遍"；另一工位只在末端独立复核；开放决策 YZ 裁决。
- "A 设计 → B 按冻结 spec 实现"保留给 spec 值得冻结的活（如底层三件）。

## 五、回主线建议（本会话产出，待 YZ 开题）

- 建议 S4 第一阶 = **判据源 → agent 最小 demo**，拿**红→绿**当硬门（同时治 S3 "验收空转"）。
- 形态：只有标题的 issue → agent 先写**会失败的红测试**（停）→ 壳确认初始红 → agent 实现 → 红转绿 → 人只复核判据合理性。
- 最小机制改动：验收分两相（**判据相**要求初始红 / **实现相**红转绿）；初始非红=无效判据 → `needs_human`；复用 cu 续轮 + task-5 phase 计时。
- 验收标准：① agent 自产判据（人没写测试）；② 判据合理（初始红 + 人复核认可）。
- **先别做**：L3 自生议题、全量常驻、大重构。
- 分工适合 A（B 忙 task-6/7）。第一步：**选靶**（`locus/projects/cogos/ISSUES.md` 挑自包含可验收，或造最小靶）。

## 六、遗留 / 坑

- task-5 改动**未 commit**（B worktree）；task-6 叠加其上；均等 A 复核收尾。
- B 正在跑 task-6 / task-7 实验，结果待回。
- 工位隔离缺口（`COGOS_HOME` + 服务单例）仍开（`locus/projects/cogos/ISSUES.md`）。
- 其它待讨论：验收空转、`send_msg` 问/报不分、分层验收、红→绿证据。
