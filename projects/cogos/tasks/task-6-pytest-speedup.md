# task-6 — 测试套件提速（消除纯浪费）

> 状态：待执行。工位 B 执行。自包含，干净会话读本文件 + 代码锚点即可开工，无需工位 A 讨论上下文。
> 背景：全量 pytest 单次 ~61–68s（1021 passed）。其中约 28s 是**纯浪费**（一条测试首次 import lark + 两处漏 mock 的 sleep），无产品价值，且自驱回路每轮都要付一次。本任务只消掉这些浪费，**不牺牲任何断言**。

## 目标

全量 `python3.11 -m pytest -q` 单次时长显著下降（目标 **< 40s**），**测试数与断言一律不变**。

## 证据（工位 A 已实测，直接可用）

| # | 测试 | 耗时 | 根因 |
|---|---|---|---|
| 1 | `tests/feishu/test_ws.py::TestWSClient::test_start_sets_started` | ~13–18s | **不是 sleep**：首次 `import lark_oapi`（`cogos/feishu/ws.py:179-183` `_build_handler` 懒加载；实测 import 10–11.5s）。`tests/` 下**无其它文件**用 lark，所以这笔只为这一条付。 |
| 2 | `tests/feishu/test_monitor.py::TestHeartbeatToDaemon::test_running_heartbeat_fail` | 5s | `cogos/feishu/monitor.py:39` `await asyncio.sleep(5)`（heartbeat 失败分支）**未被 mock**。 |
| 3 | `tests/feishu/test_monitor.py::TestMainLoop::test_heartbeat_fail_triggers_recovery_then_heartbeat_again` | 5s | `cogos/feishu/monitor.py:29` 同步 `time.sleep(period=5)`（`_start_daemon`）**未被 mock**；该测试只 mock 了 `monitor.asyncio.sleep`。 |
| 4 | `tests/agent/test_terminal.py::test_observe_while_busy` | ~1s | 真跑 `time.sleep(1)` 子进程测 busy——**语义必要**，可选微缩，非必需。 |

去掉 1–3 ≈ 省 23–28s / 61s。

## 前置

- 本体：`work/B/cogos-s2`（worktree，分支 `s2-selfdrive-loop`）。
  - **注意：该 worktree 已有 task-5 的未提交改动**（`cogos/agent/loop.py` + `tests/agent/test_loop.py`）。**保留，不要 commit、不要回滚**；在其之上继续。
- 跑测试必须 `cd work/B/cogos-s2` + `python3.11 -m pytest`（editable 钉工位 A，cwd 进 sys.path 才 import 到 B 的代码）。
- 基线：`python3.11 -m pytest -q` → `1021 passed, 1 skipped`，约 61–68s。
- 单文件基线：`test_ws.py` ~20s / 31 passed；`test_monitor.py` ~10s / 13 passed。

## 改动面（文件归属冻结）

- 只改：`tests/feishu/test_ws.py`、`tests/feishu/test_monitor.py`。
- 可选：`tests/agent/test_terminal.py`（仅缩短 sleep，小收益）。
- **不改**任何 `cogos/` 产品代码；不改断言语义；不减少测试数；不重构。
- 若发现必须动产品代码才能达标 → **停下，飞书通知 YZ，回工位 A**。

## 契约（先读后写）

### ① test_ws：让 lark_oapi 在测试期间永不 import

在 `TestWSClient` 内加 autouse fixture，mock 掉 `WSClient._build_handler`（返回值不参与断言）：

```python
@pytest.fixture(autouse=True)
def _no_real_handler(monkeypatch):
    monkeypatch.setattr(WSClient, "_build_handler", lambda self, on_event: None)
```

- 理由：`test_start_sets_started` 只断言 `_started`；`test_ws.py` 里语义测试用的是 `WSClient._parse_event`（`test_ws.py:377+`），不依赖真 handler。
- **验收口径**：全量跑测期间 `lark_oapi` 不应被 import。若其它路径（如 WSManager startup）仍触发，一并处理到"全量测试进程内 grep 不到 lark 加载"。

### ② test_monitor：补两个漏掉的 mock

- `test_running_heartbeat_fail`：补
  ```python
  async def fake_sleep(sec): pass
  monkeypatch.setattr("cogos.feishu.monitor.asyncio.sleep", fake_sleep)
  ```
- `test_heartbeat_fail_triggers_recovery_then_heartbeat_again`：在已有 `asyncio.sleep` mock 之外，补
  ```python
  monkeypatch.setattr("cogos.feishu.monitor.time.sleep", lambda _: None)
  ```
- 断言、`heartbeat` mock、`_Break` 流程一律不动。

### ③（可选）test_terminal

`test_observe_while_busy` 的 `time.sleep(1)` 可缩到 0.3–0.5（仍能观测到 busy）；若缩后会 flaky 则不做。

## 轮次清单（每轮：实现 → gate → 记 checkpoint → 通知）

| 轮 | 内容 | 验证 gate |
|---|---|---|
| 1 | test_ws mock `_build_handler` | `pytest tests/feishu/test_ws.py -q` → 31 passed 且 **< 3s**（原 ~20s） |
| 2 | test_monitor 两处补 mock | `pytest tests/feishu/test_monitor.py -q` → 13 passed 且 **< 1s**（原 ~10s） |
| 3 | 全量回归 | `pytest -q` → **1021 passed, 1 skipped 不变**，总时长 **< 40s** |

## 停下点

三轮 mock/本地测试全绿即停。**不 commit**（task-5 改动亦未提交，一起等工位 A 复核）。飞书通知 YZ。

## 工程规范（防走偏）

- 只改 mock/fixture；断言不得改弱；测试数不得减少。
- 每轮开始前先跑单文件拿到"改前耗时"，改后再跑"改后耗时"，记录到 checkpoint（这是本任务的核心证据）。
- 不改产品代码。

## checkpoint 工作法

- 每轮结束写 `work/B/checkpoint/`：`status.md` + 本轮 `checkpoint-N.md`（锚点 `文件:行` 优先、凝练可恢复）。
- 结构：当前问题 / 已做修改 / 关键结论 / 遗留坑；每轮 `status.md` 写"下一轮读什么锚点"。
- 轮结束飞书通知 YZ。
