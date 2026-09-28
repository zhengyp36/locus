# 验收证据 · toolbox 模型面修订（N3+A+B / N4 / `to`）· 2026-09-28

> 事实类证据（可复现原始数据）。结论/why/被否进 `entries/2026-09-28-cogos-toolbox-run-semantics.md`。

## 被测状态

- cogos `ab46a5b`（feat，code）＋ `ea2812c`（docs）。A 工位 `/home/zhengyp/work/A/cogos`。
- `python3.11 -c "import cogos"` → `/home/zhengyp/work/A/cogos/cogos/__init__.py`。

## 单测

- `python3.11 -m pytest tests/agent -q` → **277 passed, 3 skipped**。
- `python3.11 -m pytest -q`（全量）→ **1281 passed, 5 skipped, 1 failed**。
  - 唯一 fail：`tests/image_ctx/test_p2.py::test_mark_pixel_lands_on_tool` —— FileNotFound `/tmp/kilo/vision/vf6_repl_out_new/windows.png`（缺外部素材，与本改无关）。

## 行为复跑（真实 deepseek + FakeTelecom，harness `scripts/exp_agent_behaviour_probe.py`）

- 触发句（S5 类）：`你好，请用你的电脑能力，在你当前工作目录执行 cat E2E-S5.txt，然后把命令输出发回给我。`
- 命令：`LM_INTERNAL_KEY=<尾号b111 ik> PROBE_OUT=… python3.11 scripts/exp_agent_behaviour_probe.py 10`
- 原始结果：`probe-after-n10.json`（本目录）。

| 指标 | 本改后（n=10） | 基线（`225c902` 时，n=10） |
|---|---|---|
| 成功（回发含 `S5-REAL-E2E-OK`） | 10/10 | 10/10 |
| `n_lm_rounds` | 5（全部）| 4（恒定）|
| 用 help | 0/10 | 0/10 |
| 工具错 | 0/10 | 0/10（当时仅 `to` 猜错）|
| 参数 `to` 错 | 0/10 | 10/10 |

- 轨迹（10/10 一致）：
  1. `call computer.command.run {"command":"cat E2E-S5.txt"}`
  2. `call computer.command.run {"command":"cat E2E-S5.txt > …/_out.txt 2>&1; echo done"}`
  3. `call computer.file.read {"path":"…/_out.txt"}`
  4. `call communication.message.send {"to":"COGOS002:A0001","content":"…S5-REAL-E2E-OK"}`

## 复查修复（09-28，`8bb00b3`）

检视本次改动时发现两处内部 session id 泄漏（均为模型面，非崩溃）：

1. **工具结果泄漏 numeric `id`**：N3 后 `observe` 成为主取值路径，而 `terminal_observe`/`_exec`/`_write`/`_cancel` 结果都带 `id=<n>`（机制内部会话号），模型会看到一个无法合法回传的句柄——正是 B 要消除的"session 诱导"。修：`toolbox._call` 对所有需注入 session 的能力，结果统一 `pop("id")`。
2. **事件键不匹配**：`impl/terminal.py` 事件 payload 用 `session_id`，而 `events.render_event` 只认 `id` → `term.done`/`term.notify` 实际渲染成 `session_id=1 …`（泄漏内部名、S4 的对象标签从未生效）。修：render_event 对 term 事件把 `session_id`/`id` 映射为 `session="tN"`；测试改用真实 payload 键。
3. 附带：`catalog.py` 顶部 docstring 仍写"binding … or a composition of them"，随 `steps` 移除一并改。

- 修复后测试：`tests/agent` 278 passed / 3 skipped；全量 1282 passed / 5 skipped（同一无关 image_ctx fail）。
- 修复后复跑（n=10，`probe-after-n10-fixed.json`）：结果与修复前一致（10/10、help 0、错 0、往返 5），确认无回归。

## 对照：批 0 冒烟（N3 模拟，run 不取值，未改仓库）— 停回讨论的依据

- `scratch` 已删；摘要见 `entries/2026-09-28-cogos-toolbox-run-semantics.md` 与旧 `batch0-gate-result`（收口前）。
- 当时：成功 10/10，但往返 7~11（均值 ≈8.2）、help 10/10、工具错 10/10（`to` ×10 + `session` ×5）；取值 9/10 走 `observe`。
