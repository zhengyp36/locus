# toolbox-walkthrough · agent 使用工具的过程 ＋ 实现计划（2026-09-28）

> **性质**：① 从 agent 视角的端到端过程推演——模型**面对和使用**这些工具的完整过场，是**目标的可执行替身**；② 围绕该过程的实现计划（S0–S5）。**实现只填推演里的格子，不新增格子。**
> **上游**：`ENTRY.md`（呈现思路 / 可用判据）、`toolbox-design.md`（工具层形状 / §11 A 定稿 / §12 消息化与送达）、`toolset-decisions.md`（分组）。
> **本轮范围 ＝ 呈现核心**（步 0 / 2 / 3 / 4）；换视角细化、错误渲染、抹痕、命令化、`wait` 参数推后。

## 0. 过程推演（agent 视角）

### 步 0 · 会话开始，模型看见什么
1. `system`：人设（**不再列工具**）。
2. `[常驻总览]`（system-reminder 消息）：
   - 当前机器：host / os / shell / home / cwd；
   - 能力目录（3 组，各带标识 ＋ 一句"能为你做什么"）：`computer` / `communication` / `vision`。
3. `tools`：**只有 `toolbox`**（schema 恒定）。
→ 模型此刻知道"**我有什么组**"，但不知道每个能力怎么写。

### 步 1 · 面对任务
"看看 home 里有什么" → 从总览定位到 `computer` 组（能跑命令 / 读写文件）→ 需要具体用法。

### 步 2 · 发现（help 逐级）
- `toolbox(help, name="computer")` → 面：`command / file / screen / web / reminder`
- `toolbox(help, name="computer.command")` → 能力：`run / observe / interrupt / send / answer_auth / open / list`
- `toolbox(help, name="computer.command.run")` → 参数 / 返回 / 时间形态
→ 每级返回进上下文（保温），模型**不用猜**。

### 步 3 · 使用（call）
- `toolbox(call, name="computer.command.run", args={command:"ls -la ~"})`
- 结果回来（输出行）→ 模型据它推理 / 回复。

### 步 4 · 异步与事件（第二条通道）
- 长任务：`run` 回"已受理 `t1`"（**对象索引**）→ 完成时**独立事件消息** `[computer.command] run 完成 t1 → <输出>`。
- 来信 / 到点：`[communication.message] …` / `[computer.reminder] …`。
- **消息丢了不慌**：凭引用（`t1`）能重取 / 重做（丢得起，`toolbox-design §12.6`）。

### 步 5 · 换视角（机制发起；后续）
机制就近追加一份新总览（另一台机器的身份 / 环境 ＋ 该机面清单）；模型**以最近为准**，不调用 switch。

### 步 6 · 出错恢复（后续）
`call` 写错路径 / 参数 → 返回带"最近的合法路径 ＋ 去 `help`"，模型自纠。

## 1. 可追溯：判据 ↔ 过程步 ↔ 切片

| 判据 | 过程步 | 实现切片 |
|---|---|---|
| 1 · 3 组总览 ＋ 单 `toolbox` | 步 0 看见 | **S3**（装配 ＋ 注入）＋ **S0**（总览内容来源） |
| 2 · 不查文档能调起来 | 步 2 发现 / 步 3 使用 | **S0**（目录）＋ **S1**（help）＋ **S2**（call） |
| 3 · 一次真实操作跑通 | 步 2 → 3 贯通 | **S5**（真实走一遍） |
| （另一条通道在） | 步 4 异步 / 事件 | **S4** |

> **切片数 < 步数**是正常的：步 1（面对任务）是**模型行为**，无机制要建；步 5 / 6 本轮不建。

## 2. 实现计划（S0–S5）

### 阶段划分（验收台阶；切片＝施工步）

| 阶段 | 切片 | 产物 | 验收（gate） |
|---|---|---|---|
| **I · 造入口**（不上线） | S0 → S1 → S2 | `toolbox` ＋ `help` 四级 ＋ `call`（含 `run` 组合）；**旧 38 工具仍暴露，agent 照旧跑** | `pytest`（catalog / toolbox / call）＋ 手动 `call` 跑 `echo` |
| **II · 上线成形** | S3 ＋ S4 | 模型只见 3 组总览 ＋ 单 `toolbox`；返回 / 事件带对象索引 | **判据 1、2**（上下文 / schema 检查） |
| **III · 跑通** | S5 | —— | **判据 3**（真实身份走一遍） |

> **先造后切**：先把新入口（`toolbox` / `help` / `call`）造好、验绿，再切换暴露（S3）——避免"拆了旧工具、新入口未成形"的中断窗口。

### 切片明细

每片：产出 / 主要改动 / 验证 / **完成定义（DoD）**。

**S0 · 目录（catalog）单一来源**
- 产出：新 `cogos/agent/catalog.py`——3 组 / 面 / 能力（`path`、一句 help、参数、绑定 impl 名或组合），数据源＝`toolbox-design §9`。
- 改动：新增模块（**不塞**已 1400 行的 `tools.py`）。
- 验证：`tests/agent/test_catalog.py`。
- DoD：路径完备；每能力可解析到绑定；与 §9 清单对得上。

**S1 · `toolbox` 元工具 ＋ `help`**
- 产出：`make_toolbox_spec`（schema `{command, name, args}`）；`help` 四级（空 / 组 / 面 / 能力）走 catalog。
- 改动：新 `cogos/agent/toolbox.py`。
- 验证：`tests/agent/test_toolbox.py`。
- DoD：四级输出稳定；未知路径报错并引回 `help`。

**S2 · `call` 路由**
- 产出：`call` → catalog → impl；**先打通组合能力 `computer.command.run`**（open ＋ exec ＋ observe）。
- 验证：`call computer.file.read` 真读到文件；`call computer.command.run` 真跑 `echo`。
- DoD：组合能力端到端真跑通（判据 3 的贯通点）。

**S3 · 单 `toolbox` 装配 ＋ 常驻总览**
- 产出：对外只暴露 `toolbox`；`system` 之后注入常驻总览（机器环境 ＋ 3 组）。
- 改动：`app.py._build_specs` / context；`config.py.render_system_prompt` 去工具清单 ＋ 补机器环境（os / shell / home / cwd）。
- 验证：`tests/agent/test_app.py` / `test_config.py`。
- DoD：上下文含总览；schema 只剩 `toolbox`。

**S4 · 事件 ＋ 对象索引（最小）**
- 产出：会话短标签贯穿 `run` 返回与完成事件。
- 验证：`tests/agent/test_consciousness.py` / `test_app.py`。
- DoD：返回与事件带同一短标签；事件渲染为 `[computer.command] …`。

**S5 · 端到端验收（按 `rules/task.md`）**
- 真实身份、公开入口：起 agent → 发消息 → 模型看总览 → `help` → `run ls` → 拿结果；抓日志 / 屏做地面真值。
- DoD：判据 3 条全中。

**节奏**：开工即 `set_timer(600)` 盯偏航 ＋ `start_context_watch`（20s / 150K）；每片跑 `pytest tests/agent tests/cog_runtime` 后**自主提交**（片内小步提交）。

## 3. 确保与目标相符（四条机制）

1. **每片 DoD ＝ 过程里那一步能观察到**，不是"函数写完"（S1 的 DoD 是"四级能查到任一能力"）。
2. **唯一验收脚本 ＝ 本推演走一遍**（真实身份）；单测只做**片内保真**，不替代验收。
3. **偏航检查**：`timer` 到点回本文件对照；**代码逼着改过程 → 回讨论改推演，不偷改目标**。
4. **只填已有格**；要新增机制格（抹痕 / 命令化 …）＝**回讨论**（防范围蔓延）。

## 4. 开工前已定（本轮决策）

- 目录放**新模块**（`catalog.py` ＋ `toolbox.py`），不塞 `tools.py`。
- **本轮不做抹痕**：`call` 结果仍走厂商 `role:tool`，内容是我们的文本；抹痕随步 5 之后。
- **本轮先单会话**跑通 `run`（`open` 惰性）；多会话标签随 `A2` 第二步补。
- `help` 的一句帮助**采用 §9「干什么」列**。

## 5. 本轮边界

- **做**：步 0 / 2 / 3 / 4 贯通，跑通一次真实操作。
- **不做（推后）**：步 5 换视角细化、步 6 错误渲染、抹痕、工具命令化、时间形态参数化（`wait`）、内圈边界。
- **实现时自决**：`toolbox` 参数名、渲染角色 / 归属头、`command.open` 形式、内圈边界清单。

## 6. 执行纪律与阶段门（开工后严格执行）

### 纪律

- **来自 `rules/task.md`**：目标内能推的**自决并记录**；**自主提交 / 推送**（先跑测试；`secrets` 不入库）；长任务 `set_timer`(600s) **只盯偏航** ＋ `context_watch`(20s / 150K)；验收**从目标推、不用自写 e2e、真实身份真用**；上下文卫生（图的数据不进上下文）；不可逆 / 外溢才停。
- **本轮约定**：只填推演已有格，**新增机制格＝回讨论**；代码逼改过程＝**回讨论改推演**；每片 DoD ＝ **过程步可观察**。

### 阶段门

**入口前置（每阶段开始逐条勾）**
1. 上一阶段 gate 通过（测试绿 ＋ 真实探针过）。
2. 依赖就绪（S2 需 S0 绑定；S3 需 S1/S2 的 `toolbox`）。
3. 工作树干净、可回退。
4. **写明本阶段的"真实对照点"**——写不出，标"纯内部"并缩短它。

**出口核对（每阶段结束逐条勾）**
1. 片内测试绿。
2. **真实探针过**（见下）。
3. **回本文件对照**：产物与推演一致；不一致→回讨论改推演。
4. 提交。

### 每阶段真实探针（硬纪律：无真实对照 ⇒ 阶段不算完成）

- **阶段 I 末**：真实模型挂 `toolbox`（**独立实验会话，不动主路径**），自己 `help` → `call` 跑通 `echo`。
- **阶段 II 末**：真实模型看总览 → 判据 1、2。
- **阶段 III**：主路径 e2e → 判据 3。

> 理由：S0 / S1 / S2 / S4 是**机制层**，绿了 ≠ 向目标前进；只有"**真实模型走过程**"才是 agent 视角的对照。

## 锚

- 入口 `ENTRY.md`；工具层形状 `toolbox-design.md`；分组 `toolset-decisions.md`
