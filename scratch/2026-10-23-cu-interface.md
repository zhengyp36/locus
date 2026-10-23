# 意识上下文：接口 + 生命周期（2026-10-23）

> 状态：**讨论中**（方案已重组，部分待议）。本件记录**当前方案全貌** + **已定结论** + **待讨论点**。
> 数据层见 `2026-10-23-cu-context-persistence.md`（**待同步**：§2 状态集加 idle、§6.1 枚举加 idle、§11 活跃判定区分「在跑 vs idle」）。
> 已定结论见 §9 的「已定」；待议见 §9 的「待议」。

## 0. 分层（重要）

- 意识上下文 = **被动持久化服务**，只提供原语（§2）。
- **启动归一化 / 醒触发 / 睡眠编排 / IDLE 唤醒触发** = 上层（控制层/元层）编排，**不属于意识上下文**；写出来只为看全貌。
- **介入决策**（准入判断 + LLM 判是否/如何介入）= `on_intervening`（元层/控制层注入）。
- **驱动边界**：介入点 = **有 cu 运行时的唯一决策点**；心跳 = **无 cu（ASLEEP/IDLE）时的唯一驱动**。二者按「有无 cu 在跑」划分，互补而非并列。

## 1. 构造与状态

### 1.1 构造

```python
cons = Consciousness(path, on_intervening)
```

- 构造时从盘上读意识上下文，初始化 `state`、版本号、`messages` 等。

### 1.2 对外状态（state 直接用对外态）

| 状态 | 含义 | 盘上表现（活跃文件最后 state 行） |
|---|---|---|
| `ASLEEP` | 无活跃文件 | 无（正常目录只有 meta.json） |
| `WAKING_UP` | 装载中 | `loading` |
| `AWAKE` | 有活跃 cu 在推理 | `loaded` |
| `IDLE` | 醒着、无 cu（意识活动停） | `idle` |
| `FALLING_ASLEEP` | 卸载中 | `unloading` |

- **IDLE 逻辑上 = AWAKE**（已定）：都是「醒着、有已完成的意识内容要整理」，只差「有无活跃 cu」。
- 盘上态集合（`type=state` 的 `state` 枚举）七态：`loading` / `loaded` / `continuing` / `continued` / `unloading` / `unloaded` / **`idle`**。
- **idle 是瞬态**（已定）：正常流程后必接 `continuing`（被事件唤醒）或 `unloading`（入睡），永不收尾；文件真正收尾态仍只有 `loaded` / `continuing` / `unloaded`。
  - crash 可能把 idle 留在文件末尾 → 恢复按 AWAKE 处理（`start_unload` 在 idle 后补 `unloading`），不另开路径。

### 1.3 started_before_last_shutdown（掉电恢复判据）

- `started_before_last_shutdown` = 「上次进程终止（掉电/异常/正常停）前，这份上下文是否已开始（产生过推理输出）」；用于区分「已 loaded 但无输出（可安全丢弃）」vs「真正开始推理」。
- **以盘上为唯一真相**（已定）：`loaded` 行之后有无 `message` 行。
- 归一化时从盘上一次性读出（局部判据），**不设运行期字段、不做维护**。

## 2. 接口（Consciousness 原语）

### 2.1 回调 on_intervening（外部注入，同步纯函数）

```python
def on_intervening(ctx: InterveneContext) -> InterveneDecision: ...
```

- **同步**：介入点 = 暂停点（cu 不在 await chat），回调同步执行、同步返回。
- **必须 return**：返回 `InterveneDecision`；返回 `None`（漏 return）= 代码 bug，直接退出 agent，不兜底（静态靠类型标注 + 运行时 None 检查）。

### 2.2 InterveneContext（回调参数，打包）

| 字段 | 含义 |
|---|---|
| `type` | `tool`（on_tool_done）/ `finish`（on_done） |
| `rounds` | 当前轮次（需 cu 加字段） |
| `tokens` | 当前 token 数（不含工具结果；需 lm_client 返回 usage） |
| `wait_to_sleep` | 是否有睡眠请求在等待介入点（标记仅告知，睡由元层决定、无法强制） |

### 2.3 InterveneDecision（tagged union）

| 决策 | payload | 含义 |
|---|---|---|
| `Resume()` | — | 继续当前 cu 推理 |
| `Switch(new_context)` | `new_context` | 换 cu，新起点由外部同步算好传入 |
| `Sleep()` | — | 入睡 |

### 2.4 属性

| 属性 | 含义 |
|---|---|
| `state` | 对外状态（§1.2 五态） |
| `is_first_wake` | 从未醒过（判装载来源：出生配置 vs 记忆装载） |
| `context` | `[Message]`，只读视图（写走 `append()`）；元层只在**介入点**访问（介入点 = 检查点后，视图与盘上一致） |
| 版本号 | 不对外，模块内聚 |

### 2.5 操作

| 操作 | 前置 | 动作 |
|---|---|---|
| `start_load()` | `state==ASLEEP` | 新建意识文件 + `loading` 行；清 `_wait_to_sleep` |
| `append(msgs)` | — | 注入消息（单条或数组） |
| `load_done()` | — | 追加 `loaded` 行、启动意识 |
| `request_sleep()` | — | 置 `_wait_to_sleep=True`，立即返回 |
| `start_unload()` | 睡流程 | 追加 `unloading` 行（纯落盘，不 interrupt） |
| `unload_done()` | 元层记忆完成后 | 追加 `unloaded` 行 + 归档 + 清 `_wait_to_sleep` |
| `revoke(context)` | `state==IDLE` | 无 cu 的 Switch：直接 `do_switch(context)`（见 §2.7） |
| `reset()` | 归一化 | 丢弃部分唤醒内容，回 ASLEEP |

### 2.6 介入点包装（Consciousness 内部）

- `_intervening_on_tool()` = `await _on_intervening("tool")`，作 `cu.on_tool_done`。**`on_tool_done` 是新增回调**：插入在 runtime `_advance` tooling 分支「assistant+tool 消息 append 进 material **之后**、`state=pending` 之前」，保证介入点时 material 已含本轮工具结果。**成败都触发**：程序层成败随回调传入——工具调用正常返回（含返回错误结果）＝成功；runtime 层抛异常/超时/无法执行＝失败。
- `_intervening_on_finish()` = `await _on_intervening("finish")`，作 `cu.on_done`。**成败都触发**：`result==OK` / `interrupt` ＝成功；其余（含 LLM 环境异常）＝失败。
**介入点 = 两层流程叠加**（已定）：
- **意识上下文通用流程**（`_on_intervening` 主体）：**先判成败**（程序层失败 → 打日志 + 异常退出；成功才继续）→ 打包 `InterveneContext` → 调 `on_intervening` → 按决策做 cu/state 机械维护。意识层只负责「怎么机械执行」，不决定「是否/如何介入」。
- **元层/控制层流程**：① `on_intervening` 内部（准入判断 → LLM 判是否/如何介入 → 算 `new_context` → 定 `Resume/Switch/Sleep`）；② 介入点之后编排（睡眠三段式、唤醒、归一化），不在 `_on_intervening` 内。

**介入点内 cu 机械维护 = 两件事分离**（已定）：
- 第一件事·结束旧 cu：只在 **tool 介入点**（finish 时 cu 已结束，无需 interrupt）。开始时先记 `cur_cu = self.cu`（换 cu 后拿不到旧 cu），结束时按策略决定 `cur_cu.interrupt()`：`Switch`/`Sleep` → interrupt；`Resume` → 不 interrupt。
- 第二件事·换新 cu / 置 None（`cu=None` 的两个时机：①→IDLE（resume/finish）；②→Sleep）：
  - `Switch` → `do_switch(new_context)`（开新关旧 + 起新 cu，`new_context` 由元层算好传入；旧 cu 由第一件事 interrupt）。
  - `Sleep` → `cu=None`（state 走 FALLING_ASLEEP，由后续 `start_unload` 置，**不经 IDLE**）。
  - `Resume`/finish → `cu=None` + `state=IDLE`（追加 idle 元信息）。
  - `Resume`/tool → cu 不变，继续。

- `_on_intervening(intervene_type)` 流程：
  0. **先判成败**：程序层失败 → 打日志（cu 状态 / rounds / tokens / material 尾部，留足信息触发分析）+ 异常退出；成功才继续。
  1. **检查点（tool / finish 统一）**：**元层介入前**先对齐上下文并存盘——取 `material[len(messages):]` 补入 `messages` 并写盘（此刻 `context` == 盘上）。两个介入点都如此。
  2. tool：记 `cur_cu = self.cu`。
  3. 构造 `InterveneContext` → `self.on_intervening(ctx)` 拿回决策。
  4. 第二件事（换 cu / 置 None，见上）。
  5. 第一件事：tool 且策略非 `Resume` → `cur_cu.interrupt()`。

### 2.7 do_switch（换 cu 统一动作）

- `Switch` 决策 与 `revoke` 共用 `do_switch(context)`：
  1. **盘上**：开新文件（`<wake>.<context+1>.jsonl`，首落 `continued` + 起点消息）→ 关旧文件（尾补 `continuing`）→ 归档旧文件；`context_version+1`。
  2. **内存**：起新 cu（context）+ `no_wait`，替换 `self.cu`。
- 起点 `context` 由外部（元层 / 装载）算好传入，`do_switch` 不算。
- **不碰整理**：元层算 `context` 时可能整理了、也可能只是理解＋决策；整理是元层独立的事，可随时回读盘上文件再整理。意识层只管 **cu 管理 + 存盘 + 流程配合**。
- 有 cu 的 `Switch`：第一件事（interrupt 旧 cu，仅 tool）在 `do_switch` 之前；`revoke`（无 cu）：直接 `do_switch`。

## 3. 启动归一化（上层编排）

```
# started_before_last_shutdown = 盘上 loaded 行后有无 message（启动时读一次）
if cons.state != ASLEEP:
    if cons.state == WAKING_UP or not started_before_last_shutdown:
        cons.reset()          # 丢弃部分唤醒，回 ASLEEP；可能丢事件（遗留）
    elif cons.state in (AWAKE, IDLE):
        cons.start_unload()
        # 整理记忆
        cons.unload_done()
    else:                     # FALLING_ASLEEP
        # 继续整理记忆
        cons.unload_done()
assert cons.state == ASLEEP
```

- 恒收敛到 ASLEEP：agent 每次启动从 ASLEEP 起步，再由心跳决定是否醒。

## 4. 醒（上层触发 + 原语）

- 触发（心跳，满足其一）：① 有事件待处理且 ASLEEP；② 白天且 ASLEEP。
- 流程：

```
cons.start_load()
cons.append(msgs)   # 装载模块算好起点（system + user）
cons.load_done()
```

## 5. 睡眠（上层编排 + 原语）

1. **启动归一化中的睡眠**：`start_unload` → 整理记忆 → `unload_done`。
2. **AWAKE 下睡眠**：agent 主动（`go_to_sleep` 工具）或机制层 → `request_sleep()` → `_wait_to_sleep=True` → 介入点（元层判是否/何时睡，**无法强制**）→ `start_unload` → 整理记忆 → `unload_done`。
3. **IDLE 下睡眠**：心跳检测到晚上 → `start_unload` → 整理记忆 → `unload_done`。
4. **`_wait_to_sleep` 清除**：① `unload_done()`（真睡完成）；② `start_load()`（醒来，防御兜底）。请求睡之后只能**真睡**或**醒来**才清。

- 「start_unload → 整理记忆 → unload_done」的编排归属：**元层/控制层**，不在 `_on_intervening` 内（已定，见 §9 已定-6）。

## 6. IDLE 被事件唤醒

- 触发：心跳检测到事件且 IDLE。
- 流程：事件 + 记忆加载得 context → `cons.revoke(context)`。
- `revoke` = **无 cu 的 Switch**（已定）：无旧 cu 可 interrupt，直接 `do_switch(context)`（§2.7）。

## 7. meta.json 版本号来源

- wake / context 都从 1 开始；版本号不对外。
- 有意识文件 → 以文件名为准；无意识文件 → 以 `meta.json` 为准。
- `start_load` 建文件后删 `meta.json`；初始化（未出生）写 `meta.json={1,1}`。
- 统一原则：关旧前先落新权威（切先写新文件、睡先写 meta.json）。

## 8. is_first_wake

- 是否从未醒过（出生前恒 True）；判装载来源；与 `meta.json` 正交。

## 9. 讨论状态

### 已定

1. 介入回调**返回决策** `Resume/Switch/Sleep`（不回调 side-effect）。
2. 参数打包 `InterveneContext`。
3. 介入决策**同步**、入睡记忆**异步**（异步窗口在回调返回后）。
4. **IDLE = 对外新状态，逻辑 = AWAKE**（归一化进 AWAKE 分支，走 `start_unload → 整理 → unload_done`）。
5. 盘上**加 idle**（瞬态：后必接 continuing/unloading；crash 留末尾按 AWAKE 恢复）。
6. 介入点 = 两层流程：**意识上下文通用流程**（打包 ctx + 按决策做 cu/state 机械维护，`_on_intervening` 主体）＋**元层流程**（`on_intervening` 内做准入/LLM 判/new_context/定决策；介入点之后编排睡眠三段式/唤醒/归一化）。睡眠编排归元层，不在 `_on_intervening` 内。
7. **interrupt 两件事分离**：第一件事·结束旧 cu（仅 tool 介入点，先记 `cur_cu`、结束时按策略 interrupt：Switch/Sleep 才 interrupt）；第二件事·换新 cu/置 None（`cu=None` 两时机：→IDLE、→Sleep）。`start_unload` 纯落盘不 interrupt、`unload_done` 不碰 interrupt。
8. **`sleep()` 改名 `request_sleep()`**；`_wait_to_sleep` 清除点 = `unload_done`（真睡）+ `start_load`（醒来，防御兜底）；睡由元层决定、无法强制（标记仅告知）。
9. **`revoke` = 无 cu 的 Switch**：封装 `do_switch` 统一换 cu（`Switch` 决策与 `revoke` 共用）；`do_switch` = 关旧开新（盘上版本切换）+ 起新 cu，**不碰整理**（起点 context 外部传入；整理是元层独立事，可回读盘上再整理）。

### 待议（逐条过，过完勾掉）

- [x] 3. `started` → `started_before_last_shutdown`：以盘上为唯一真相（loaded 后有无 message），归一化时读一次、不设运行期字段。
- [x] 4. 睡眠编排归属：`start_unload → 整理记忆 → unload_done` 属元层/控制层，不在 `_on_intervening`（已定，见已定-6）。
- [x] 5. `interrupt` 位置：**收进 `_intervening_on_tool`（介入点），两件事分离**；`start_unload` 纯落盘不 interrupt、`unload_done` 不碰 interrupt（已定，见已定-7）。
- [x] 6. `revoke` = 无 cu 的 Switch：封装 `do_switch` 统一换 cu（已定，见已定-9）。
- [x] 7. 新实现点（已确认，编码任务单另列；`interrupt()`/`no_wait` 已存在、无需落地）：① `on_tool_done` 回调（runtime 现只有 on_ready/on_tool_call/on_done；**新增，插入在工具结果 append 进 material 之后**）；② `rounds` 字段（cu 加轮次计数）；③ `tokens`（lm_client 返回 usage）；④ **最终 assistant 消息 append 进 material**（现状 running 分支把最终回复放 `CuResultOk`、不 append，检查点会漏；方案 A）。
- [x] 8. 「醒后完全靠介入」不准确 → 已定：介入点 = 有 cu 时的唯一决策点；心跳 = 无 cu（ASLEEP/IDLE）时的唯一驱动；边界写入 §0。
- [x] 9. 归一化条件已清晰（§1.3 定义判据 + §3 注释写明），无需改；`state==WAKING_UP` 虽被 `not started_before_last_shutdown` 逻辑涵盖，但显式写出以表意图，保留。
- [x] 旧遗留：失败路径不进介入 → **方向已定（继续遗留、不落码）**：工具**业务失败**转「成功 + 失败结果给模型」（runtime 层处理），cu 生命周期无岔路；工具**程序失败**（runtime 抛异常）与 `on_done` 非 OK/非 interrupt 失败 ＝ BUG → 意识上下文介入点打日志 + 异常退出（留足信息触发分析）。`interrupt` 是主动行为、不算失败。LLM 环境异常也按失败退出、**不引入重试**。
