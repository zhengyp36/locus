# handoff-10 · cogos 工具呈现（阶段 I–III 完工；2026-09-28）

> 前序会话：实现 S0–S4 ＋ 阶段 I/II 真实探针 ＋ 阶段 III 主路径真实模型验收，**已封笔**。
> 本文件＝交接正文；**给新会话的第一句话单列于下**。

## 给新会话的第一句话（单列）

续 cogos「工具呈现」收尾：先读 `scratch/ENTRY.md`、`scratch/code-map.md`、`scratch/handoff-10.md`、`scratch/toolbox-walkthrough.md`（§2 计划 / §6 纪律与阶段门）。**S0–S4 代码已提交、测试全绿、阶段 I/II 真实探针 ＋ 阶段 III 主路径真实模型验收均已过**；唯一剩余＝ S5 的「真实飞书身份 / 公开入口」那一版验收（外部阻塞，需 YZ 绿灯 ＋ 指认唐钰账号）。开工即 `set_timer(600)` ＋ `start_context_watch`（20s / 150K）；先据本文件向 YZ 确认是否跑 live e2e：跑则按下方「剩余」步骤，否则按「判据 3 已覆盖」收尾（无未提交代码）。

## 状态

- **代码完成、已提交**：cogos `master`，6 commit `f8ef94a`(S0) `67011d0`(S1) `fd2752b`(S2) `8a5cdf1`(S2 修复) `42f09aa`(S3) `9183508`(S4)。工作树干净。
- **测试**：`python3.11 -m pytest tests/agent tests/cog_runtime` → **300 passed, 3 skipped**。
  - 注意：系统 `python` 是 3.9（不兼容），**必须 `python3.11`**；独立脚本运行需 `PYTHONPATH=/home/zhengyp/work/A/cogos`。
- **真实模型探针（阶段 I–III）**：先起 LM 服务 `python3.11 -m cogos.lm_service.cli server`（127.0.0.1:11434），internal key `ik_c47WkfAw7E5v6Ck8idMHgg`（real deepseek，account 尾号b111）。
  - 阶段 I：`/tmp/kilo/probe_toolbox.py`（真实模型 `help`→`call run echo`）。
  - 阶段 II：`/tmp/kilo/probe_overview.py`（只挂总览＋单 `toolbox`，模型 `help` 逐级 → 操作）。
  - 阶段 III：`/tmp/kilo/probe_mainpath.py`（`Agent` 主路径 ＋ 真实模型 ＋ FakeTelecom，`cat hello.txt`→`MAINPATH-OK`→回消息）。
  - 探针在 `/tmp/kilo`（未入库），丢可重建。

## 剩余（唯一）

**S5「真实身份、公开入口」验收**：起 agent（`cogos-feishu`）→ 发消息 → 模型看总览 → `help` → `run` → 拿结果；抓日志 / 屏做地面真值。

- **为何阻塞**：飞书是**真实租户**（`~/.cogos/feishu/accounts/*`，`app_id=cli_…`，非本地假后端）；本机**无 telecom daemon**（`daemon-mode: systemd`）；`~/.cogos/agent/tangyu` 只有 `agent.json`、**无 `profile.md`**；跑它会**真发外部消息**。
- **需 YZ**：① 绿灯（起 daemon / 租户内发消息）；② 指认唐钰对应哪个 bot / 号码、由谁发消息。
- **倾向**：判据 3（一次真实操作端到端）已由阶段 III 主路径真实模型覆盖 → 可视为完成，live 飞书版列为可选。

## 决策 / 偏差（详见 `code-map.md`）

- S0 catalog 纳入 `open/list/send`（A1/A2）；`run` 内建两处**有界等待**（shell readiness ＋ output settle，非模型参数）；`answer_auth` 仅声明（机制选槽未接）；S4 单会话短标签 `t<id>`；事件前缀映射 `term.*→computer.command` 等。

## 读什么

- `scratch/ENTRY.md`（入口）· `code-map.md`（含阶段 I 决策 ＋ II/III 状态）· `toolbox-walkthrough.md`（§2 计划 / §6 纪律）· `toolbox-design.md` · `toolset-decisions.md`。
- 代码：`../cogos/cogos/agent/{catalog.py(新), toolbox.py(新), app.py, config.py, consciousness.py, events.py}`。

## 交接纪律

- 后继**不得 `--auto`**；链式交接设上限。
- 封笔即清本会话 async 源（timer / terminal / background_process / 飞书 pin ＋ inbox）。
