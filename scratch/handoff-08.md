# handoff-08 · cogos 工具呈现（2026-09-28）

> 前序会话：`26/09/27-工具呈现-讨论-7`（已封笔）。后继起来后 **先加载、等 YZ 讨论**，不推进、不落码。

## 给新会话的第一句话（单列）

续 cogos「工具呈现」：先读 `scratch/ENTRY.md` ＋ `scratch/toolset-decisions.md` ＋ `scratch/toolbox-design.md`（思路已收口、工具分组与工具层形状已定、归机制漏项审计已列）；本轮目标＝把工具做成"可用"；先加载、等 YZ。

## 状态（已收口）

- **工具分组定稿**：3 组 —— 电脑 / 通信 / 视觉（`toolset-decisions.md`）。
- **工具层统一形状定稿**：单 `toolbox`（help/call）；能力用 `组.面.能力` 路径；机器＝路径的**隐含上下文**；事件＝第二条通道（`toolbox-design.md`）。
- **整理结果**：38 个实现工具 → **~21 个模型面能力**；系统性归机制：会话 id / `job_id` / spool（`toolbox-design.md` §9）。
- **协助（screenlab）接入**：＝ `screen` 面的后端；那台机器成为另一个视角（只声明 `screen`）；同意/被抢/收回走事件（§6）。
- **机器命名规则**：名字 ＝ 机器身份，**不区分人 / agent**。
- **归机制漏项审计**（§10）：三处要紧 —— `terminal_write`（非行输入）、`terminal_open/list`（并发 / "在跑什么"）、`phone_spool`（收到的文件落在哪）。

## 未定（待 YZ 讨论）

- 命名：模型面标识已定＝英文路径（`toolbox-design.md §2`）；余 `toolbox` 参数名。
- 三处要紧漏项的补法：`command.send` / 会话语义 / 文件落地位置。
- 密码输入：自动注入的提示识别策略、凭据"按目标绑定"的形状。
- 跨机单步动作（A → B）与"当前视角"的张力。

## 读什么

- 入口 `scratch/ENTRY.md`；分组 `scratch/toolset-decisions.md`；工具层形状 `scratch/toolbox-design.md`。
- 本体 `../cogos/docs/design-agent-tools.md`（§12 分包 / §17 协助）、`../cogos/docs/design-selfdrive-agent.md`。
- 代码事实 `../cogos/cogos/agent/app.py:227`（`_build_specs`）、`tools.py`、`config.py:36`、`impl/graphics.py`。

## 边界

- 本轮仍**只讨论 / 记录，不落码**；方向由 YZ 定。
