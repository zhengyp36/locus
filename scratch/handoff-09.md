# handoff-09 · cogos 工具呈现（开工）（2026-09-28）

> 前序会话：讨论 ＋ 开工前准备（**已封笔**）。后继起来**直接开工**，不再等待。
> 本文件＝交接正文；**给新会话的第一句话单列于下**。

## 给新会话的第一句话（单列）

续 cogos「工具呈现」开工（阶段 I）：先读 `scratch/ENTRY.md`、`scratch/toolbox-walkthrough.md`（§2 计划 / §4 开工前决策 / §6 纪律与阶段门）、`scratch/code-map.md`、`scratch/toolbox-design.md`、`scratch/toolset-decisions.md`；然后**按 §2 执行阶段 I：S0（catalog）→ S1（toolbox/help）→ S2（call）**，严守 §6，先跑 S0。

## 状态（准备完成，可开工）

- **思路 / 分组 / 形状 / 过程 / 计划 / 纪律 全部收口**：
  - 分组 `scratch/toolset-decisions.md`（3 组：电脑 / 通信 / 视觉）。
  - 工具层形状 `scratch/toolbox-design.md`（单 `toolbox`；§11 A 定稿；§12 消息化与送达）。
  - 过程推演 ＋ 实现计划 ＋ 纪律 `scratch/toolbox-walkthrough.md`。
  - 代码地图 `scratch/code-map.md`（**只覆盖本次开发**，交接先读）。
- **目标**：把工具做成「可用」；判据＝3 组总览＋单 `toolbox` / 不查文档能调起来 / 一次真实操作端到端跑通。
- **本轮＝呈现核心**：阶段 I（造入口 S0–S2）→ II（上线 S3–S4）→ III（跑通 S5）。
- **开工前决策（4 条）**：目录放新模块 `catalog.py`＋`toolbox.py`；本轮不做抹痕；本轮先单会话跑通 `run`；`help` 一句帮助采用 `§9「干什么」列`。
- **纪律**：见 `rules/task.md` ＋ `walkthrough §6`（入口前置 / 出口核对 / **每阶段真实探针**：无真实对照则阶段不算完成）。

## 开工第一刀

1. **阶段 I**：S0（catalog，纯代码）→ S1（`toolbox`/`help`）→ S2（`call` 含 `run` 组合）。
2. 开工即：`set_timer(600)` 盯偏航 ＋ `start_context_watch`（20s / 150K）。
3. 每片跑 `pytest tests/agent tests/cog_runtime` 后**自主提交**（片内小步）。
4. 阶段末按 §6 做**真实探针**（独立实验会话，不动主路径）再进下一阶段。

## 读什么

- `scratch/ENTRY.md`（入口）· `toolbox-walkthrough.md` · `code-map.md` · `toolbox-design.md` · `toolset-decisions.md`。
- 本体 `../cogos/docs/design-agent-tools.md`（工具权威）· `design-selfdrive-agent.md`（总纲）。
- 代码：`../cogos/cogos/agent/{catalog.py(新), toolbox.py(新), app.py, tools.py, config.py, consciousness.py}`。

## 边界

- 只填推演已有格；**新增机制格＝回讨论**；代码逼改过程＝回讨论改推演。
- 本轮**不做**：抹痕、工具命令化、`wait` 参数、换视角细化、错误渲染、内圈边界。
