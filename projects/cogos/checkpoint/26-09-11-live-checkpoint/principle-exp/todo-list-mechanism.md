# TODO-LIST 机制（v0.6，机制主体定稿；schema / 最小验证待定）

> 2026-09-10。上游：`handoff-vision-image-fields-18.md` + `explicit-process.md`（理论存档，已挂起）。
> 定位：**显式化的最小落地**——让模型自己出流程，并**按步骤推进、不漂**。取代 S1–S8 看板 + R0–R5。
> 状态：设计稿 **v0.6，机制主体已敲定**（自审 19 条讨论队列已清）。**未实现、未验证。**
> **仅剩待定**：工具返回 schema、最小验证方案（见 §13.4）。
> v0.1：轮次边界拦截器；轮次 = 模型动作；打断 = 丢弃 + 注入。
> v0.2：加模型视角；提醒分软 / 硬；简单/复杂由"是否超上限"推出。
> v0.3：取消"软升级为硬"；软 = 计划中点纯提醒；明确调整 vs 重写。
> v0.4：补工具接口。
> **v0.5 变更（YZ 意见）**：工具拆为 5 个（语义优先），**工具名即 decision**，删去 `decision` 参数；`reason` 仅在 check-in 时必填；`todo_read` 暂缓。
> **v0.6 变更（2026-09-10，逐条敲定）**：按项记账（`planned` + `actual`、完成收紧、`retired_spent` 总和法）；**§4.4 写前校验**；两层协商 + `N_retry`；**§〇.5 使用契约**；P1 只认 `build_plan`；`status` 三态；`adjust` 权限分档；管理类不计 `actual`；软提醒改"连续自主 K 轮"节拍器。**遗留 / 暂缓见 §十三 / §13.4。**
> **讨论记录（2026-09-10，第 1 条敲定）**：硬触发**不是**电平死循环；**软才是"白名单放行"**，硬只认"触发是否消除"。§5.2 放行判据由"是不是对账类工具"改为"动作是否让触发条件变假"。
> **讨论记录（2026-09-10，第 2 条敲定）**：预算改为**按项记账**——每项同时记 `budget_rounds`（计划预算）与 `actual_rounds`（实际消耗）；约束只看两处：**计划期 `Σbudget_rounds ≤ total_budget`**、**执行期当前项 `actual_rounds` 不得超其 `budget_rounds`（达到即硬打断）**。取消含糊的全局 `spent + Σ` 算式。某步完成时机制把其 `budget_rounds` **收紧为 `actual_rounds`**（只减不增，省下的成为后续余量）。
> **讨论记录（2026-09-10，第 3 条敲定）**：① 全局上限统一为**总和法**——`retired_spent（rebuild 作废掉的旧计划实际消耗）+ Σ当前 planned ≤ total_budget`，取消 `delta` 判据；② 新增 **§4.4 写前校验**：任何写操作先逐项校验、全部通过才提交，程序状态**不被模型提交值直接覆盖**；③ 变更（adjust / rebuild）后，对 `actual > 0` 的行必须 `budget_rounds ≥ actual_rounds`，否则全局不变量断裂。
> **讨论记录（2026-09-10，第 4 条敲定）**：**"协商"分两层**——执行期（上限已定）超限**不是协商**，是"拒绝 + 给上限 + 工具自决"（能→改计划，不能→`finish_task`），全程只有工具动作；**指派期**（上限未定）才是协商，可为**机制外对话**，产出的 `total_budget` 在**接单时定格**。超限重试上限 `N_retry`（默认 2–3，≤3）。**不存在无指派方**（程序写死的预算也是指派方）。收尾：超限 / 强停时预留 1 轮给 `partial`，模型未用该轮 → `aborted`。**定格 / 恢复整块移入 §十三 遗留（v1 不实现）。**
> **遗留盘点（2026-09-10）**：以"**先跑起来验证**"为目标，把不影响最小闭环的整块移出正文（§十三）：结束 / 裸停（A5）、定格 / 恢复、`paused`、完成自报与证据、软提醒设计、停滞、交付物界定、`revision`/`history`、`drop_streak` 重置等。跑通前必补项（工具返回 schema、最小验证）**暂缓至验证阶段（§13.4）**。
> **P1 拦截定稿（2026-09-10，B8）**：P1 **只认 `build_plan`**；`build_plan` 超限 → 拒绝 + 回上限、可重试（计 `N_retry`）；**其它任何动作 / 纯文本 / 结束 → 直接中止（aborted）**，不设追问回合。参数 `R` **废弃**。
> **状态简化 + `adjust` 权限（2026-09-10）**：`Row.status` 砍为 **`pending | in_progress | done`**（`blocked` / `failed` 移入遗留）。`adjust_plan` 权限分档：**已完成行不可改**；**当前步只可把 `budget_rounds` 调到 `≥ actual`**；**后续未开始行可任意改（含删除）**；调整后超上限即失败。
> **§4.3 收尾（2026-09-10）**：`Σ actual_rounds` 与 `total_budget` 的关系是**不变量**——`==` 为用尽（合法）、`>` 绝不该发生（实现 bug，断言报错）；**管理类工具不计入 `actual_rounds`**（只有业务工具计入，管理类仍受轮次边界检查）。
> **收尾盘点（2026-09-10）**：工具返回 schema（B9）与最小验证方案（C13）**暂缓至验证阶段（§13.4）**，原 §十四 并入 §十三。修正 §十 措辞（D18：模型在"工具返回"与"触发点注入"时都能看到表）。新增两条小遗留：行 `id` 规则、"对账空转"兜底（管理类不计 `actual` 后的松动点）。
> **B10 补注（2026-09-10）**：`problem: past_row_modified` **仅对 `adjust_plan` 成立**；`rebuild_plan` 本就要能改前面，**不适用此码**（§6.4 已注明）。
> **软提醒定稿（2026-09-10，B11）**：软提醒 = **独立回顾节拍器**——`K` = 模型**连续自主运作**（无机制提醒、无用户/外部交流）的轮数，到 `K` 触发并清零，**与 `budget_rounds` 无关**；目的：避免自空转 / 偏航。**清零事件三类**（任一即清零）：① 机制注入（`[plan]`/`[status]`/`[check-in]`/`[stop]`）；② 用户/外部消息；③ 模型主动写表（`update_progress`/`adjust_plan`/`rebuild_plan`）。改掉原"计划中点"写法。`K` 取值待调。
> **新增 §〇.5 使用契约（contract）**：机制只给 `allow` / `drop` **决策**，**"执行前否决 `drop` 动作"是使用者义务**——违约即逃逸，责任在使用者。机制与运行时解耦，原"拦截点依赖运行时（实现前提）"从 §十二-5 / §十四 移出。

---

## 〇、一句话

**模型写一张表（计划＋进度）；机制只在轮次边界做拦截，必要时注入提醒或丢弃本轮动作。表是软的，硬在闸门。**

---

## 〇.5 使用契约（contract）

> **机制提供"决策"，兑现决策是使用者的义务。** 这是采用本模块的**前置约束**，不属机制实现；机制不提供检测或兜底。

1. 机制在轮次边界会给动作一个处置决定：**`allow`** 或 **`drop`**。
2. **被标记 `drop` 的动作，使用者必须"执行前否决"，不得产生任何副作用。**
3. **违反此约定 = 逃逸**：责任在使用者——机制已给出决定，不再保证其表 / 计数 / 触发的正确性。
4. 使用者的适配方式（执行前钩子、middleware、permission deny 等）由使用者自定；机制只声明该要求。
5. 因此 **本机制与运行时解耦**：不关心谁执行、如何循环，只需宿主持有并兑现上述义务。

---

## 一、原则（沿用，不重复论证）

1. **无角色**：勾由**产物**推出，不由谁打。
2. **流程显式 ＋ 产物显式**：表 = 流程；完成标志 = 产物。
3. **硬约束必须外部**：计数、触发、封顶都在机制侧；模型只能提方案，不能自批。
4. **机制与流程解耦**：不拥有控制流，不规定 agent 是循环还是事件驱动，只挂轮次边界。
5. **提示词只能请求**：给模型看的规则**不承担强制**；强制靠闸门（丢弃 + 阻塞）。
6. **语义明确优先于接口少**：模型要自驱，靠名字自解释，好过参数里藏枚举。

---

## 二、两个对象

### 2.1 表（schema 固定，值由模型填）

```
Row {
  id            // 稳定标识
  step          // 步骤描述
  budget_rounds // 计划预算：该步预计花几轮（模型自估，软）
  done_marker   // 完成标志 = 这一步凭什么算完（产物）
  status        // pending（未开始）| in_progress（进行中，唯一）| done（完成）
  actual_rounds // 实际消耗：该步已执行的轮次（机制记，见 §4.3）
  note?         // 可选说明（失败原因等）
}
Table {
  rows: Row[],
  total_budget,     // 指派方硬上限（不可超）
  planned_total,    // Σ budget_rounds（计划期约束：≤ total_budget；rebuild 后为 retired_spent + planned_total ≤ total_budget）
  spent,            // Σ actual_rounds（当前表实际消耗，派生 / 展示 / 兜底；不含 retired_spent）
  revision
}
```

> **记账要点**：每项**同时记** `budget_rounds`（计划）与 `actual_rounds`（实际）。全局没有独立计数口径——`planned_total` / `spent` 都是**各行的求和**，不再是"另一个口径的 spent"。

### 2.2 机制（外部状态 + 拦截钩子）

```
MechState {
  phase         // assigned | planning | executing | stopping | done | aborted
  retired_spent // rebuild 作废掉的旧计划实际消耗累计（供上限校验）
  total_budget  // 指派方硬上限
  frozen_plan   // 定格计划（对账基准）
  last_table    // 上张表（diff 用）
  stall_count   // 硬对账里连续无变化次数
  drop_streak   // 连续被打断但未对账次数
  history       // 修订历史（供强停总结）
}
```

---

## 三、生命周期

```
T   指派        机制注入"给出计划"
P1  计划闸门      只认 build_plan
      ├─ build_plan 合法 → 校验 schema → 预算判定 → 定格 → P2
      ├─ build_plan 超限 → 拒绝 + 回上限（可重试，计 N_retry）→ 留 P1
      └─ 其它任何动作 / 纯文本 / 结束 → 中止（aborted）
P2  执行        每个动作前拦截（见 §5）
      ├─ 软触发 → 注入状态（本轮照走，可不回应）
      ├─ 硬触发 → 丢弃动作 + 注入对账（须工具动作回应）
      ├─ 硬上限 → 丢弃动作 + 注入强停（P3）
      └─ 全 done / 收到 finish_task → P4
P3  强停        注入"总结并汇报"（预留 1 轮）→ 收结构化总结 → done
P4  完成        正常提交
```

> **P1 可重入**：`rebuild_plan` 会回到计划阶段（见 §七）。

---

## 四、计划（P1）

### 4.1 硬闸门
**没收到计划 = 指派未完成 → 不许执行。** P1 **只认 `build_plan`**：其它任何动作（含 `finish_task` / 纯文本 / 结束）→ **直接中止（aborted）**，**不设追问回合**（接单时已注入 `[plan]` 告知）。

### 4.2 预算判定（不做语义复杂度判断；按项记账）

**约束只有两条**，全部落在"项"上：

1. **计划期**：`planned_total = Σ budget_rounds ≤ total_budget`。
2. **执行期**：当前项的 `actual_rounds` **不得超**其 `budget_rounds`；达到即**硬打断**（§5.2），模型只能三选一：
   - `adjust_plan` **调大该项预算**（受约束 1 兜底：调大后 `planned_total` 不得超 `total_budget`）；
   - 把该步标 `done`（真完成）；
   - `finish_task` 结束。

**计划超上限 = 拒绝 + 给上限 + 工具自决**（执行期，**不叫"协商"**）：

- `planned_total ≤ total_budget` → **直接接受**，定格。
- `planned_total > total_budget` → **拒绝提交、程序状态不变**（§4.4），并回**上限 X**。模型自行判断：
  - **能** → 重调 `build_plan`（首次）/ `adjust_plan` / `rebuild_plan`，压到 ≤ X；
  - **不能** → `finish_task` 结束。
- 全程**只有工具动作**，机制**不发"是非问"、不需要"回答"通道**（化解"只认工具动作"的矛盾）。
- **重试上限 `N_retry`**（默认 2–3，**不得超过 3**）：同一计划期连续无效提交（超限 / schema 非法 / 写错行）达上限 → 走强停收尾（§八）。

**"协商"只发生在指派期（机制之外）**：
- 指派任务时，可先让模型评估、给出建议预算，再与指派方**对话**定下 `total_budget`。此步在机制之外，**不受"只认工具动作"约束**。
- **接单 = 协商结束 = `total_budget` 定格**，机制自此接管（→ T 指派 → P1）。
- **不存在无指派方**：程序里的机制行为**也是指派方**（预算写死）；实现时应**预留余量**（写死值不会随实际变）。

**收尾收紧（关键）**：某步标 `done` 时，若 `actual_rounds < budget_rounds`，机制把该步 `budget_rounds` **收紧为 `actual_rounds`**，二者持平，省下的预算**成为后续余量**；机制**不动后续计划**（怎么用余量是模型自己的事，走 `adjust_plan`）。
- 收紧**只减不增**，故永不违反约束 1。
- 由约束 2 + 收紧 + rebuild 校验，恒有 **`retired_spent + Σ actual_rounds ≤ retired_spent + Σ budget_rounds ≤ total_budget`**——**全局自动不超**。
- **`== total` 是用尽（合法），`>` 绝不该出现**：一旦 `retired_spent + Σ actual_rounds > total_budget` 即**实现 bug**（不变量被破坏），报错 / 强停——这是**断言**，不是常规触发路径。

- `total_budget` 由指派方（人 / 程序写死）给定；模型只能提方案，不能批预算；**定格值不得单方更改**（机制收紧除外，见 §4.3）。

### 4.3 计数与当前步（实现定义）

> 第 2 条暴露：光"同时记 planned + actual"还不够，**谁在何时 +1、以哪项为准、冲突时谁优先**必须写死，否则实现行为不唯一。

**D1. 当前步**：机制取表中**显式 `in_progress`** 的行；若没有 `in_progress`，取**第一个 `pending`**。同时出现**多个 `in_progress` → `schema_invalid`**，要求修正。`done` 为终态、不作当前步。

**D2. `actual_rounds` 归谁**：只有**业务工具**调用（已执行）→ 当前步 `actual_rounds` **+1**。**不计入**的有：**管理类工具**（`build_plan` / `update_progress` / `adjust_plan` / `rebuild_plan` / `finish_task`）、裸停、机制注入、被丢弃的动作（没执行）。管理类调用**仍受轮次边界检查**（软 / 硬提醒照常可能触发），只是不消耗工作预算——"一个步骤的状态变化就那几种，管理动作不算工作轮"。

**D3. 冲突优先**：先判**终态**（`finish_task` / 全 `done`），再判**该步撞线**（`actual_rounds ≥ budget_rounds`）。即"完成优先于撞线"。撞线那轮若动作不满足 `clears_trigger()` → 丢弃。

**不变量（断言，非触发）**：`retired_spent + Σ actual_rounds > total_budget` 绝不该发生（`==` 为用尽，合法）；一旦 `>` 即实现 bug，报错 / 强停（见 §4.2）。

### 4.4 写前校验（validate-then-commit）

> **原则**：模型的每次写操作（`build_plan` / `update_progress` / `adjust_plan` / `rebuild_plan`）都**先逐项校验，全部通过才提交**；任一不通过 → **拒绝 + 返回 `problem`，程序内状态保持不变（原子性）**。**绝不拿模型提交的数据直接覆盖程序状态**，否则轮次统计会被模型随意改坏。

| 写操作 | 校验项（全部通过才提交） | 失败 `problem` |
|---|---|---|
| **首次 `build_plan`** | `Σ planned ≤ total_budget` | `over_total_budget` |
| **`rebuild_plan`** | `retired_spent + Σ新 planned ≤ total_budget` | `over_total_budget` |
| **`adjust_plan`** | ① `retired_spent + Σ调整后 planned ≤ total_budget`；② **已完成行**不可变更；③ **当前步**只可改 `budget_rounds` 且须 `≥ actual_rounds`（"只要 ≥ actual 即可"）；④ **后续未开始行**可任意改（含删除行） | `over_total_budget` / `past_row_modified` / `budget_below_actual` |
| **`update_progress`** | ① 只允许改 `status`（及 `note`）；② **不得改 `budget_rounds`**（计划轮次模型不能改）；③ **不得改 `actual_rounds`**（实际消耗由程序统计，模型不能改） | `budget_fields_changed` / `actual_readonly` |

- 校验通过后，机制**用程序内计算结果**回填并回显**完整规范表**（§6.4），模型看到的永远是机制认可的版本，而非它自己提交的原始值。
- **收敛**（某步 `done` 且 `actual < planned` → `planned := actual`）是**机制行为**，在校验通过后由机制执行，不属模型改写。
- 校验失败**计一轮**（§9），但**计划期**的失败（超限 / schema / 写错行）**不计入 `actual_rounds`**——计划期尚未开始工作，只累计 **`N_retry`** 次数。
- **连续无效提交（超限 / schema 非法 / 写错行）达 `N_retry`**（默认 2–3，≤3）→ 不再接受新计划，走强停收尾（§八）。提交合法计划即**清零** `N_retry`。

---

## 五、执行 + 提醒（P2）

### 5.1 触发（确定性，不用概率）

| 触发 | 条件 | 严重度 | 动作 |
|---|---|---|---|
| 软提醒（回顾） | 模型**连续自主运作**累计 **K 轮**（期间无任何回顾 / 介入） | **软** | 注入状态（陈述句）→ 本轮照走；计数清零 |
| 阶段超预算 | 当前步 `actual_rounds ≥ budget_rounds` | **硬** | 丢弃 + 注入对账（须动作回应） |
| 不变量断言（bug 检测） | `retired_spent + Σ actual_rounds > total_budget`（`==` 合法） | 报错 | 视为实现 bug → 强停 |
| 停滞 | 硬对账里连续 2 次表无变化 | **硬** | 升级（暂停 / 通知） |
| 完成 | 全 `done`，或收到 `finish_task` | — | P4 |

- **软提醒 = 独立的回顾节拍器**：`K` = **模型连续自主运作**（无机制提醒、无用户 / 外部交流）的轮数；到 **K** 触发并**清零**；**与 `budget_rounds` 无关**（不看预算、也不受 `adjust` 影响）。
- **清零事件**（任一发生即清零）：
  1. **机制注入**：任何 `[plan]` / `[status]` / `[check-in]` / `[stop]`（机制对模型说话）；
  2. **用户 / 外部消息介入**；
  3. **模型主动回顾**：写表动作 `update_progress` / `adjust_plan` / `rebuild_plan`。
  
  **三者任一即清零**：模型主动写表 = 它在正常运作中的一次回顾；外部介入通常需要它响应，故能**打断空转**。二者都说明"它没在闷头空转"，重新计时。
- **计入 `K` 的**：模型自主的**业务工具**轮次。**不计入**的：管理类工具、工具返回、被丢弃的动作、机制注入本身。
- **目的**：避免模型**自空转 / 偏离目标**——连续自主跑太久就让它停下来看看方向、要不要调整计划。
- **软是纯提醒**：模型**不回应完全可以接受**——不升级、不阻塞；"继续动作"即为正常。
- **为什么不把软升级为硬**：硬锚在**计划时钟**（当前步 `actual` 撞 `budget`）上，与"回没回软"无关。
- `K` 默认值待调（§13.4）。

### 5.2 拦截模型（不是 driver loop）

**轮次 = 一次模型动作**：一次工具调用，或一次结束动作。**完成也当作动作**——否则模型静默停下会**逃逸拦截点**。但计入 `actual_rounds` 时**只有已执行的动作算**，被丢弃的不算（§4.3 D2）。

```
on_action(action):                          # 一轮开始
  if action is finish_task or all done:    finish()            # 终态优先
  if hard_trigger_fires():                 # 该步撞线 / 停滞（+ 不变量断言另计）
      if action clears_trigger():          allow(action)      # 使触发消失 → 放行
      else:                                drop(action); inject(check_in)
  elif soft_trigger_fires():               # 计划中点
      inject(status_note); allow(action)                      # 照走，不强求
  else:                                    allow(action)      # 正常走
  # 注：actual_rounds +1 在动作“已执行”后记，被丢弃的动作不计（§4.3 D2）
```

**软 / 硬的区别（关键，勿混）**：
- **软** = **陈述句状态告知** + **白名单放行**：`inject(status_note); allow(action)`，动作**照走**，不问、不阻塞；模型可理会可不理会，**不升级**。
- **硬** = **丢弃 + 阻塞**：触发成立时，**非"消除触发"的动作一律丢弃**。**硬里没有"对账类工具白名单放行"**——一个动作是不是对账类工具（`update_progress` / `adjust_plan` / `rebuild_plan` / `finish_task`）**不是放行判据**，那只是"可用来回应的工具集合"。硬触发的判据只有一个：**动作是否让触发条件变假**。

**放行判据 `clears_trigger()`（硬触发专用）**：动作执行后触发不再成立才放行。允许的三种：

| 动作 | 如何消除触发 | 之后 |
|---|---|---|
| `update_progress` 把该步标 `done` | 当前步结束，触发点移到下一步 | 继续 |
| `adjust_plan` / `rebuild_plan` 把预算调到 `budget_rounds > actual_rounds`（**严格大于**） | 当前步不再超预算 | 继续（受 `total` 兜底） |
| `finish_task` | 进入终态 | P4 |

- **未 done 的 `update_progress`（只改 note / 非 done 状态）不消除触发** → 不满足 `clears_trigger()` → 继续丢弃 + 重注入 `[check-in]`。
- ⚠️ 触发条件是 `actual_rounds ≥ budget_rounds`，故消除它必须把预算调到 **严格大于** `actual_rounds`。把预算调到**恰好等于** `actual_rounds` 是**合法取值**（§4.4 允许 `≥ actual`），但**不能**消除触发，下一轮仍会被拦。两者别混：`≥ actual` 是"允许取值的下限"，`> actual` 才是"消抖条件"。
- 模型反复交**无效对账** → 累积 `drop_streak` → 到 `N` 强停（§9）。
- ⚠️ **别把"是不是对账类工具"当成放行条件**——这正是早期写法的措辞错误：它会放行未 done 的 `update_progress`，让硬触发退化成"check-in 死循环"。硬触发**不靠"放行对账"收敛，靠"动作消除触发"收敛**。
- （`actual_rounds` 在"该步 done 后是否从 0 起算"属计数口径，见待议第 3 条；此处只要求该步 done 后**触发点移到下一步**。）

**为什么"丢弃动作再注入"**：
- LLM 行为是**算出来的**：同上下文重推，大概率还是同一个动作 → 丢弃这条**信息不丢**。
- 在**执行前**打断可**避免副作用**——优于"执行后再注入"。
- **真正的强制是"闸门"，不是"丢弃"**。

### 5.3 对账协议（check-in）

见 §6.3 消息模板；模型**必须**用工具动作回应（对账类工具四选一），且**带 `reason`**；且该动作须满足 `clears_trigger()`（§5.2）——**四选一不等于都放行**，未消除触发的照旧被丢弃。

- 机制校验：**表变了吗？`done` 行有完成标志吗？合法吗？**
- **重注入**：对账时把"当前表 + 预算状态"注入（兼作防漂锚点）。

### 5.4 表 diff（白捡）

每次写表返回整表 → 机制 **diff 相邻两张**，自动得到"推进 / 计划变更 / 预算变更"。
→ 对账不必让模型自报。

---

## 六、模型视角：交互契约与工具接口

> 这些是"机制要模型怎么做"。**它们是给模型看的请求，强制靠闸门（§5.2）**。

### 6.1 契约要点

1. **计划先行**：动手前先 `build_plan`；**没有计划，动作不执行**。
2. **回应通道**：机制消息是**系统消息**；程序只认**工具动作**——语义理由写进 `reason`，**不要用自由文本作答**。（**唯一例外**：**指派期的预算协商在机制之外**，可为对话；一旦接单、`total_budget` 定格，即回到"只认工具动作"。）
3. **软 / 硬**：软 = 可不理会；硬 = 必须用工具动作回应。
4. **结束**：用 `finish_task` 显式结束。
5. **计划变更**：`adjust_plan`（调整）/ `rebuild_plan`（重写）。

### 6.2 工具接口（5 个；**工具名即 decision**）

**① `build_plan`** — 制定计划（首次）
```
build_plan({ todos: [ Row ] })
```
- **仅在尚无计划时有效**；已有计划 → 拒绝。
- 返回整表 + 预算状态；超限则**拒绝并回上限 X**（§4.2），模型可重调，累计 `N_retry`。

**② `update_progress`** — 更新进度（≈ `continue`）
```
update_progress({
  updates: [{ id, status, note? }],   // 只动状态 / 说明
  reason?: string                      // check-in 时必填
})
```
- `budget_rounds` / `step` / `done_marker` **不可改**（要改 → `adjust_plan`）。

**③ `adjust_plan`** — 调整计划（≈ `re-estimate`）
```
adjust_plan({
  updates: [{ id, step?, budget_rounds?, done_marker?, status?, note? }],
  deletes?: [id],                      // 删除后续未开始行
  reason?: string
})
```
- **权限分档**（§4.4）：**已完成行不可改**；**当前步只可把 `budget_rounds` 调到 `≥ actual`**；**后续未开始行可任意改（含删除）**。
- 写前校验：`retired_spent + Σ调整后 planned ≤ total_budget`（不够预算 → `adjust` 失败）。

**④ `rebuild_plan`** — 重新制定计划（≈ `replan`）
```
rebuild_plan({ todos: [ Row ], reason?: string })
```
- 整表重写；**想改前面的计划只能用这个**。
- 写前校验（§4.4）：旧表实际消耗计入 `retired_spent`，`retired_spent + Σ新 planned ≤ total_budget`；旧版进 `history`。

**⑤ `finish_task`** — 结束任务（完成 / `abort`）
```
finish_task({
  status: "completed" | "partial" | "aborted",
  summary: { done: [], undone: [], residual_uncertainties: [], evidence: {} }
})
```
- **终态**；`spent` 由机制填。
- `status` 语义：`completed` = 真完成；`partial` = 超限 / 强停时**预留 1 轮**总结提交；`aborted` = 模型**未用**该轮、由机制代收尾（异常，正常不应出现）。
- `summary` 须写全；**计划期超限的 `partial` 还应给出"估计还需多少预算"**（供后续裁决）。

> `todo_read`：**暂缓**（用户未议）；因每次写都回显整表，可能冗余。

### 6.3 机制 → 模型：注入消息

```
[plan]     任务开始。请先调用 build_plan 给出计划；未收到计划前不执行其它动作。

[status]   （软）当前第 k 步，已用 a/b 轮。无需回应，继续即可。

[check-in] （硬）当前步已超预算 / 停滞。请用工具动作回应：
           update_progress / adjust_plan / rebuild_plan / finish_task，
           并在 reason 里说明（进度 vs 计划）。仅回文本无效。

[stop]     已达预算上限 / 计划连续超限。请用 finish_task 给出结构化总结（预留 1 轮）。

[over-budget]（硬）计划超上限 X，未提交。请压到 ≤ X（build_plan / adjust_plan / rebuild_plan），
             或 finish_task 结束；连续超限 N_retry 次将强停。
```

### 6.4 机制 → 模型：工具返回

```
{
  ok: boolean,
  table: [...规范化整表...],
  budget: { total_budget, planned_total, spent, remaining, over_budget },
           // remaining = total_budget − retired_spent − planned_total（后续可用余量）
  problem?: "schema_invalid" | "past_row_modified" | "over_total_budget" | "budget_fields_changed" | "budget_below_actual" | "actual_readonly" | ...
}
```

- 关键：返回**整表 + 预算状态**，模型不必靠记；出问题返回 `problem`，要求修正。
- **`problem` 作用域**：
  - `past_row_modified` **仅对 `adjust_plan` 成立**（它不许改当前及后续之外的行）。
  - **`rebuild_plan` 不适用此码**——重写整份计划本就要能改前面；它受 `retired_spent + Σ新planned ≤ total_budget` 与"旧表 `actual` 进 `retired_spent`、不可撤销"约束，但**不会**因"改了前面的行"被拒。
  - 其余码按字面对应各自校验（§4.4）。

---

## 七、计划变更：adjust vs rebuild

**判据 = 每次重算总和**（不用 `delta`，避免增量算错）：任何变更后都须满足

```
retired_spent + Σ当前 planned ≤ total_budget
```

- 超则**拒绝 + 回上限 X + 工具自决**（能→再改，不能→`finish_task`），连续达 `N_retry` → 强停（§4.2）。
- 已完成行的预算已被机制**收紧为 `actual`**（§4.2），故 `Σplanned` 里不含虚高；未完成行用其 `planned`，是保守估计。

**A. 调整（`adjust_plan`）**——就地改，**权限分档**：
- **已完成行**：不可改（既成事实）。
- **当前步**：只可改 `budget_rounds`，且须 `≥ actual_rounds`（"只要 ≥ actual 即可"）。
- **后续未开始行**：可任意改（`step` / `budget_rounds` / `done_marker` / `status` / `note`），**含删除行**。
- 校验见 §4.4（调整后 `retired_spent + Σplanned ≤ total_budget`，超则失败）。

**B. 重写（`rebuild_plan`）**——重列：
- 想改**前面**的计划，**唯一方式就是重写整份计划**。
- 旧表整体作废，其**实际消耗全部计入 `retired_spent`**；新表各行 `actual` 从 0 起。
- 上限判据：`retired_spent(含旧表实际消耗) + Σ新 planned ≤ total_budget`；**已用不补回**。
- **过程不白费**：旧计划 / 失败**留在上下文，不清空**。
- `frozen_plan` 换为新计划，旧版进 `history`。

> **"机制收紧" ≠ "模型改前面"**：完成时机制把该行预算改成 `actual` 是**机制行为**，不算违反"模型不能改前面行"；返回整表时需让模型看到收紧后的值，免困惑（§6.4）。

---

## 八、强停（P3）

- 触发：`drop_streak` 超限 / 停滞升级 / **计划期 `N_retry` 用尽** /（不变量断言 `retired_spent + Σ actual_rounds > total_budget` = 实现 bug）。
- **预留 1 轮**用于总结（总结轮不受"已撞上限"影响）。
- 模型用该轮发 `finish_task(partial, summary)` → 收完即 `done`；**过程证据全程留痕**。
- 模型**没用**该轮（发别的 / 纯文本）→ 判 `aborted`，机制**代收尾**。`aborted` 属异常收尾，正常不应出现。

---

## 九、兜底 / 异常

| 情形 | 处理 |
|---|---|
| P1 未交 `build_plan`（其它动作 / 纯文本 / 结束） | **直接中止（aborted）**，不追问 |
| schema 非法 | 返回 `problem` + 要求修正（计一轮） |
| 工具与状态不符（如已有计划却 `build_plan`） | 拒绝 + 提示正确工具 |
| 对账未交表 / 交**无效对账**（未消除触发，如未 done 的 `update_progress`） | 重注入 1 次 → 仍无 → 视为停滞 → 强停 |
| 对账只回纯文本 | 重注入 + 加重 ×N → 仍纯文本 → 强停（元 agent 暂缓） |
| 连续被打断不对账 | `drop_streak ≥ N` → 强停 |
| 计划超上限 | 拒绝 + 回上限 X + 工具自决；连续达 `N_retry` → 强停 |
| 计划期连续超限 / 无效提交 | 达 `N_retry`（2–3）→ 强停；预留 1 轮 → `partial`，未用 → `aborted` |
| 指派期预算 | 机制外**对话**定 `total_budget`，接单即定格 |
| 原地打转 | 停滞触发 → 升级 |

---

## 十、数据流

- 表**住机制侧**（外部、持续）。
- 模型在**工具返回时**（call 参数 + 返回整表进历史）和**触发点注入时**（`[status]` / `[check-in]` 会带上当前表）看到表。
- **不每轮注入**；只在**触发点**注入。
- 注入消息标 `synthetic`，便于过滤。

---

## 十一、参数

| 参数 | 来源 | 性质 |
|---|---|---|
| `total_budget` | 指派方 | 硬（不可超） |
| `budget_rounds`（逐项） | 模型自估 | 软（完成时机制收紧为 `actual`） |
| `K`（软提醒间隔轮数，与预算无关） | 机制（默认待调） | 配置 |
| ~~`R`（计划追问次数）~~ | — | **已废弃**：P1 只认 `build_plan`，否则直接中止 |
| `N`（连续打断 / 纯文本重注入上限） | 机制（默认 2–3） | 配置 |
| `N_retry`（计划连续超限拒绝上限） | 机制（默认 2–3，**≤3**） | 配置 |
| `stall_threshold` | 机制（默认 2 次无变化） | 配置 |

---

## 十二、未决 / 风险

1. **完成标志怎么判定**（地基）：外部可查 vs 模型自报。现靠"产物 + 表 diff"减压，但**未解决**。
2. **丢弃重推的非确定性**：同上下文重推可能给出不同参数 / 动作；接受此成本。
3. `K` / `N` / `N_retry` / 停滞阈值 的取值（`R` 已废弃）。
4. **元 agent 升级**：模型只回纯文本时引入另一个 agent——**暂缓**。
5. ~~拦截点依赖运行时~~ → 已归入 **§〇.5 使用契约**：`drop` 的"执行前否决"是**使用者义务**（违约即逃逸），**不是机制风险 / 前提**。
6. 注入消息的**上下文噪声 / 压缩**。
7. **上下文压缩会驱逐计划**："计划在上下文中"成立到 compaction 之前；靠 `[check-in]` 重注入兜底。
8. `todo_read` 是否要提供（**暂缓**）。

---

## 十三、遗留（v1 不实现）

> 目标 = **先跑起来验证**。以下均**不影响最小闭环**，v1 暂标遗留，跑通后再定。

### 13.1 结束 / 裸停（讨论队列 A5）

- 模型不调 `finish_task`、直接结束回合（"裸停"）的处理**暂缓**（方案未想清；后续应非难点）。
- 两种运行时语义，**先确认属于哪种**：
  - **(a) 裸停 = 任务终止** → 唯一缺口是"**没有结构化终态**（`summary` / `undone` / `evidence`）"，属"**账没结**"，不是逃逸。
  - **(b) 裸停后系统再唤醒** → 会**绕过轮次边界拦截**（逃逸），才需要专门处理。
- v1 不实现完整处理；若影响实验观测，可**最小记一笔事件**（区分"模型主动停"与"机制跑挂"）。

### 13.2 定格 / 恢复（讨论队列第 4 条延伸）

- **任务定格（快照）**：`finish_task` 时冻结 `total_budget` / 整表（`planned`、`actual`）/ `retired_spent` / `history` / `summary` / **产出引用**（文件、工件、坐标）。
- **`resume`（恢复）**：指派方发起；同 task id + `epoch`（运行次数）；从定格态继续。
- **恢复后预算**：沿用旧 `total_budget` 续算，还是重新协商（新预算）——**关键约束：旧消耗必须纳入新约束，否则 `abort → resume` 成为绕过 `total_budget` 的后门**。
- **可恢复范围**：`partial` / `aborted` 可恢复；`completed` 不 `resume`（要续做则作新任务、以快照为输入）。
- **衍生**：`N_retry` 在 `resume` 后是否重置；`epoch` 与 `retired_spent` 的并入关系。
- ⚠️ **"上下文保留"不是可靠的定格存储**：compaction 会驱逐（§十二-7），恢复需另立**持久层**，不能指望上下文。

### 13.3 其它暂缓

- **行级 `blocked` / `failed` 状态**：v1 **砍掉**，`status` 只留 `pending | in_progress | done`；"暂时受阻 / 某步失败"用 `adjust_plan`（改 / 删行）或 `rebuild_plan` 表达；真遇到再加状态。
- **`paused` 状态缺失**（B7）：§4.2 / §9 用"暂停"但 `phase` 无此值；v1 用不到僵持升级。
- **完成自报 / 证据**（A6，地基）：`done_marker` 是**计划时判据**、不是**证据**；空 ✓ 未堵；证据存哪未定。v1 靠"模型自报 + 表 diff"减压。

- **停滞触发**（B12）偏弱：依赖硬对账"连续 2 次无变化"，若硬对账难接连发生则难触发。
- **交付物 vs `finish_task.summary`**（C14）：真正的产出（坐标 / 文件改动）落在哪，未界定。
- **`revision`（表）与 `history`（MechState）语义重叠**（D17）。
- **`drop_streak` 重置条件未写**（D19）。
- **元 agent 升级**：模型只回纯文本时引入另一个 agent——暂缓（§十二-4）。
- **行 `id` 规则未定**：`adjust_plan` 删行、`rebuild_plan` 换表后，`id` 如何生成 / 保持稳定，未界定（`id` 目前只写"稳定标识"）。
- **"对账空转"兜底**：管理类工具不计 `actual` 后，模型可反复对账而不推进工作轮；需靠**停滞触发**（B12，偏弱）与 `drop_streak` 兜底——两者偏弱，属已知松动点。

### 13.4 暂缓至验证阶段

- **工具返回 schema（B9）**：各写操作 / `finish_task` 的返回结构（`ok` / `table` / `budget` / `problem`）**暂缓**。
- **最小验证方案（C13）**："计划 → 提醒 → 强停"三段最小闭环 + 预期——**暂缓**（待进入验证阶段再定）。
- 参数取值（`K` / `N` / `N_retry` / `stall_threshold`）：**待跑通后按实验调**。

---

## 十四、最小验证（临时定，2026-09-10；跑通后回填 / 细化）

> 目标：最快跑通"计划 → 软提醒 → 硬打断 / 强停"最小闭环，证明方向可行。载体：image ctx 菜单任务。

### 14.1 临时约定

- **工具返回最小版**：`{ok, table, budget}`；`problem` 仅实现 `schema_invalid` / `over_total_budget` / `past_row_modified` / `budget_fields_changed` / `budget_below_actual`。`budget.remaining = total_budget − retired_spent − planned_total`。
- **完成语义临时**：`finish_task` 为**唯一终态入口**；全 `done` 不自动收尾（转为注入"请 finish_task"）；`status` 只 `completed` / `partial`；`summary` 简化 `{done, undone}`。
- **参数**：`total_budget=15`、`K=5`、`N_retry=2`。`N` / `stall` / `drop_streak` **第一轮不实现**（强停只靠 `N_retry` 撞线 + `max_inner`）。
- **`note` 字段砍掉**：用途不明、与 `reason` 重叠（§6.2 同步删）。
- **当前步自动置 `in_progress`**：D1 的隐含补丁——机制选定当前步时自动置 `in_progress`（机制填的进度，非模型写表）。
- **`max_inner` 用尽 = 一种强停触发**：注入 `[stop]` + 预留 1 轮 → `partial`；模型未用该轮 → 机制代收尾 `aborted`。
- **多工具口径**：每个业务工具调用 `actual +1`（一轮 = 一次业务工具调用）；一组执行完再判撞线；一轮混含管理 + 业务时只处理管理工具。

### 14.2 载体与命令

- 机制最小实现：`/tmp/kilo/vision/mech.py`；宿主：`/tmp/kilo/vision/image_field_chat.py --mech`。
- 命令：
  `python3.11 image_field_chat.py --mech --msg '<任务>' --out /tmp/kilo/vision/todo_exp1 --total-budget 15 --k 5 --n-retry 2`
- 任务：读出 `windows.png` 顶部菜单 7 项区域坐标（真值 x=`34,88,142,197,252,308,366`）。

### 14.3 覆盖与判读

- 覆盖：`build_plan` 定格 → 软提醒（K）→ 当前步 `actual` 撞 `budget` 硬打断 → `adjust` / `done` 消触发 → `finish_task` 收尾。
- `partial` 路径需**单独跑紧预算**（如 `total_budget=5`）逼出。
- 判读区分**机制行为**（闭环、拦截、逃逸、收敛）与**视觉质量**（坐标精度）——后者不作机制成败判据。

---

## 十五、最小验证提示词（定稿，2026-09-10）

### 15.1 系统提示词（SYSTEM，会话级）

```
你是看图助手，通过一组图工具观察图片并标注。你可以：
- see 打开一张图（PATH:路径）或调整当前视野的窗口；
- mark 在图上画十字（cross 单点）或圈矩形（rect 区域）；
- adjust_mark 移动/改已有标注；unmark 删标注。
工具坐标规则见各工具说明（一律相对 ref 归一化 0..1）。
观察时优先看全图定位、再放大到目标细节；标注到目标后用十字表示你确认的点击点。
每轮你只回复文字；若想用工具，就调用对应工具（一次可附多个）。不是每轮都必须用工具。

---- 任务计划 ----
你还可用以下计划工具：
- build_plan：动手前先给执行计划。todos = [{step, budget_rounds, done_marker}]：
  · step：这一步做什么；
  · budget_rounds：预计花几轮（一轮 = 一次图工具调用）；
  · done_marker：这一步“凭什么算完成”的可检查标志。
- update_progress：更新某步 status（pending / in_progress / done）。只改状态，不改计划。
- adjust_plan：调整计划——改后续未开始步骤、删行，或给当前步加预算（须加到 > 已用轮数）。
- rebuild_plan：整份计划重写（要改前面已完成的部分只能用这个）。
- finish_task：任务结束，交 summary（status: completed 真完成 / partial 部分完成）。

规则：
1. 先 build_plan，否则业务动作不执行。
2. 工具名即决定：想改计划就调计划工具，想干活就调图工具。
3. 机制消息：软提醒 [status] 请对照计划审视方向；硬提醒 [check-in] 必须用工具动作回应（仅回文字无效），回应时在 reason 里写“进度 vs 计划”。
4. 图工具调用消耗当前步预算轮次；计划工具不消耗。
```

### 15.2 机制注入消息（轮次级，占位符为实际值）

```
[plan] 任务开始。请先调用 build_plan 给出执行计划（每步写 step / budget_rounds / done_marker）。
任务总预算：15 轮。未收到计划前，其它动作不执行。

[status]（回顾）你已连续自主运作 5 轮。请对照计划审视一下：进度是否偏航、计划是否仍成立、有无风险。无异常则无需调用工具，继续执行。
（当前第 2 步「放大核对第 2 项」，已用 2/3 轮）

[check-in] 当前步「放大核对第 2 项」已用 3 轮，达到预算 3 轮。请用工具动作回应：
- update_progress 把该步标 done（若已完成）；
- adjust_plan 把该步预算调到 > 3；
- rebuild_plan 重写计划；
- finish_task 结束任务。
并在 reason 里说明进度 vs 计划。仅回文字无效。

当前计划：
1. [done] 定位全图（用 2/2 轮）
2. [in_progress] 放大核对第 2 项（用 3/3 轮） ← 撞线
3. [pending] 标注第 3 项（用 0/2 轮）
剩余预算：5 轮

[stop] 已达预算上限 / 计划连续超限。请用 finish_task 给出结构化总结（status=partial，summary 列出 done / undone）。预留 1 轮。
```

### 15.3 人给任务提示词（`--msg`）

```
读出 /home/zhengyp/work/A/workspace/windows.png 顶部菜单栏 7 项菜单的区域坐标，输出归一化坐标。
```

（预算由机制 `[plan]` 告知，人给提示词不重复。）
