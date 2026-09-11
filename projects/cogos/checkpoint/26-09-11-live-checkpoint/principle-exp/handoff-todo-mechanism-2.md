# handoff-todo-mechanism-2｜讨论"工具返回 schema + 最小验证闭环"

> 上游：`handoff-todo-mechanism-1.md`（第一段：TODO-LIST 机制设计 + 自审 19 条问题）。
> **主产物：`todo-list-mechanism.md`（v0.6，机制主体定稿；未实现、未验证）。**
> 备份：`explicit-process.md`（S1–S8 + R0–R5 理论存档，已挂起）+ `exp-flow.md`（实验日志，冻结态）。
> 本会话脉络：逐条敲定 19 条自审问题 → 归为 敲定 / 遗留（§十三）/ 暂缓（§13.4）。
> **下一步 = 只讨论两件事：① 工具返回 schema；② 最小验证闭环。** 敲定后即可进入实现 / 验证。

---

## 一句话状态

- **机制主体已定稿**：模型写 TODO 表（计划 + 进度），机制只在**轮次边界**拦截；**表是软的，硬在闸门**。取代 S1–S8 + R0–R5。
- **工具接口 5 个**：`build_plan / update_progress / adjust_plan / rebuild_plan / finish_task`（工具名即 decision）。
- **本会话清空了 19 条讨论队列**：该敲的敲定，不影响跑通的进 §十三 遗留，跑通后再定的进 §13.4 暂缓。
- **仅剩 §13.4 两项待讨论**：
  1. **工具返回 schema**（原 B9）——各写操作 / `finish_task` 的返回结构。
  2. **最小验证方案**（原 C13）——"计划 → 软提醒 → 硬打断 / 强停"三段最小闭环 + 预期。

---

## 必读（新会话只读这些）

1. **`todo-list-mechanism.md`（v0.6）** — 主产物。重点看 **§四 计划 / §五 执行 + 提醒 / §六 工具接口 / §13.4 暂缓**。
2. **`handoff-todo-mechanism-1.md`** — 上一段：S3 冻结 → 显式化 → TODO-LIST 机制从哪来。
3. `explicit-process.md` / `exp-flow.md` — 需要时翻（理论存档 / 实验结论）。

---

## 本会话已定论（摘要，详见主产物顶部记录 + 正文）

1. **放行判据**：硬触发只认"动作是否让触发消失"（软才是"白名单放行"）。
2. **按项记账**：`Row` 同时记 `budget_rounds`（计划）与 `actual_rounds`（实际）；完成时机制把 `planned` 收紧为 `actual`；总量用 `retired_spent + Σ planned ≤ total_budget`（总和法）。
3. **写前校验**（§4.4）：先逐项校验、全通过才提交；程序状态不被模型提交值覆盖。
4. **协商分两层**：执行期超限 = 拒绝 + 回上限 + 工具自决；指派期 = 机制外对话，接单即定格 `total_budget`。`N_retry ≤ 3`；无"无指派方"。
5. **P1 只认 `build_plan`**，否则直接中止；参数 `R` 废弃。
6. **`status` 三态**：`pending | in_progress | done`。`adjust` 权限分档：已完成不可改 / 当前步 `budget_rounds` 调到 `≥ actual` / 后续行任意改（含删除）。
7. **管理类工具不计 `actual`**；`Σ actual > total_budget` 是实现 bug（断言）。
8. **软提醒**：独立回顾节拍器——`K` = 模型连续自主运作轮数，任何外部介入或主动写表即清零；与预算无关。
9. **§〇.5 使用契约**：机制只给 `allow` / `drop` 决策；"执行前否决 `drop` 动作"是**使用者义务**，违约即逃逸。机制与运行时解耦。

---

## 下一步要讨论的素材

### ① 工具返回 schema（原 B9）

现状：§6.4 只有一个通用外壳 `{ ok, table, budget, problem? }`。要定：

- **各写操作的返回**（`build_plan` / `update_progress` / `adjust_plan` / `rebuild_plan`）——成功 / 失败是否都回整表？`table` / `budget` 字段是否一致？
- **`finish_task` 的返回**——任务终结后回什么（回执 + 最终账？完整快照归 §十三 遗留）。
- **`problem` 枚举**：`schema_invalid` / `past_row_modified`（**仅 `adjust_plan`**）/ `over_total_budget` / `budget_fields_changed` / `budget_below_actual` / `actual_readonly` / P1 用 `must_build_plan_first` …，是否齐全。
- `budget` 字段：`{ total_budget, planned_total, spent, remaining, over_budget }`，`remaining = total_budget − planned_total`。
- `todo_read`：暂缓，不定义。

### ② 最小验证方案（原 C13）

- 目标：按项目纪律给"**计划 → 软提醒 → 硬打断 / 强停**"三段最小闭环 + 预期结果。
- 载体：先在 **image ctx 工具**上跑（见环境）；菜单任务（源图 / 真值见 `handoff-vision-image-fields-18.md`）。
- 要覆盖：`build_plan` 定格、软提醒触发、当前步 `actual` 撞 `budget` 的硬打断 → `adjust` / `done`、`N_retry` 耗尽 / 强停收尾（`partial` / `aborted`）。
- 参数取值（`K` / `N` / `N_retry` / `stall_threshold`）也在此阶段按实验调。

---

## 纪律 / 环境

- 纪律：先思路 → 给提示词 / 方案 → 讨论确认 → 才做 → 一起分析；不跳步。
- 设计讨论：**逐项敲**，敲定后就地记入 `todo-list-mechanism.md`。
- 环境（如需做验证实验，从 `exp-flow.md` 抄）：LM server `cd /home/zhengyp/work/A/cogos && python3.11 -u -m cogos.lm_service.cli server --port 11434`（KEY `ik_REDACTED`，头 `X-Internal-Key`）；对话工具 `/tmp/kilo/vision/image_field_chat.py`；源图 / 真值见 `handoff-18`。
