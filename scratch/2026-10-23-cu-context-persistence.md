# 意识上下文（cu）持久化与版本化（2026-10-23）

> 状态：讨论已收口（10-23 二次修正状态模型 + 接口层），待落 entries/glossary。本件为**数据层**草稿；接口层（构造/属性/操作/睡觉流程/meta.json/is_first_wake）见 `2026-10-23-cu-interface.md`。
> 关联：实现载体 `Message` 类型改造已另落任务单 `2026-10-23-cu-material-message.md`；介入点 `on_tool_done` 见 `2026-10-22-runtime-redesign.md`「意识上下文与 cu」节。

## 1. 定位

- 意识上下文 = **记忆的活跃区**，意识（推理流）在其上活动；是**过程**，非部件。
- 唯一持久实体是记忆；意识上下文是记忆的一份"活跃投影"。
- **同时存在于内存与文件，二者同步变化**。
- 意识上下文 = **当前活跃上下文**（内存 `messages` + 盘上当前版本文件）；**历史不在内存**，就在盘上所有 `<wake>.<context>.jsonl` 里——它们是**过程记录**（投影落盘），不是记忆本体；记忆是蒸馏后的持久结论。

## 2. 状态（内存 vs 盘上，两套独立，不混）

| 域 | 状态集 | 说明 |
|---|---|---|
| 内存 | `empty` / `loading` / `loaded` / `unloading` | 意识当下所处的**过程阶段**（无 unloaded/continuing/continued） |
| 盘上（文件） | `loading` / `loaded` / `continuing` / `continued` / `unloading` / `unloaded` / `idle` | 一份上下文的**生命周期**（打开/关闭方式）；`idle`＝醒着无 cu（瞬态，后必接 `continuing`/`unloading`） |

- **两套状态独立**：内存描述"意识当下过程阶段"，文件描述"这份上下文的生命周期"；不互相映射，也不合并。
- 文件态多于内存态，是**分工**不是巧合：
  - `continuing` / `continued` = **文件间的续接标记**，只在盘上有意义（内存只有"当前"，无需续接）。
  - `unloaded` = 终结态，只在盘上（内存入睡后回到 `empty`）。
  - `empty` = 无上下文，只在内存有意义（盘上表现为"无活跃文件"）。
- 转移由真实动作驱动（load→loaded、unload→unloaded），是**标记**，**不是状态机**（"状态机"在 cogos 特指 agent 的 ASLEEP/AWAKE 那套，意识上下文的状态不叫状态机）。
- `unloaded` 单向不可逆：卸载后的上下文**不能重新加载成意识**，只能从记忆重新装载。
- 状态转移在文件里落为 `type=state` 行（见 §6.1），行序即转移顺序。

## 3. 内存表示

意识上下文在内存中的表示：

```
state, state_ts                # 当前过程态 + 转移时刻（内存态 ∈ empty/loading/loaded/unloading；unloaded/continuing/continued 只在盘上）
wake_version, context_version  # 当前版本标识
messages                       # 当前活跃上下文的「下盘视图」
cu.material                    # 引用（不单独存），当前上下文的实时视图
```

- `messages` 与 `cu.material` 是**同一份数据**的两个视图：`cu.material` 实时变化（推理中 append），`messages` 在检查点同步。二者保持「material 是 messages 的前缀超集」，新增 = `material[len(messages):]`。
- `cu.material` 是**完整真相**（含最终 assistant 回复）：无 tool_calls 的最终消息也要 append 进 material（现状 runtime 放 `CuResultOk`、不 append，落码时改，方案 A）。
- `messages` **不是历史全集**：它只反映当前活跃上下文；历史全集不存在内存，就在盘上所有版本文件里。
- 对外只读视图统一叫 **`context`**（接口层 §2.4）：= 介入点检查点后的当前上下文，与盘上一致；`messages` 是内部落盘游标（已落盘前缀），不对外。
- 落盘两个触发源：
  - **状态行即时**：`state` 改变 → 当下写 `type=state` 行（ts=state_ts），不攒。
  - **消息行攒批**：检查点（`on_tool_done` / `on_done`）→ 取 `material[len(messages):]` 补入 `messages` 并写 `type=message` 行。

## 4. 版本号（唯一标识）

| 版本号 | 含义 | 持久化位置 |
|---|---|---|
| **醒版本号** `wake_version` | 出生第一次醒=1，之后每次睡后再醒 +1 | meta.json（无意识文件时）/ 意识文件名（有意识文件时） |
| **上下文版本号** `context_version` | 每次醒后初始=1 | 在上下文文件名里（醒内计数） |

- 合成 **`<wake_version, context_version>` = 全局单调唯一 ID**，唯一确定一份意识上下文。
- **wake / context 都从 1 开始，不对外**；版本号来源判定（有意识文件 vs meta.json）见 interface.md §6。
- 版本演进规则（边界 = cu）：
  - **追加式（cu 内部）**：事件插入 + 工具循环，`context_version` 不变，消息条数增。
  - **重组（cu 边界）**：cu done 整理 或 cu 中部整理，`context_version` +1，上下文重置为 2 条 `(system, user)`。
- 一个版本 = **一次自然推理**（从一次对齐到下一次对齐）。

## 5. 元层介入对版本的影响

| 介入结果 | 上下文 | `context_version` |
|---|---|---|
| 清理痕迹后**不干预** | 不变 | 不变 |
| 清理痕迹后**干预** | 多一条干预消息 | 不变 |
| **整理上下文**（cu 中部，太长/偏） | 重置为 2 条 `(system, user)` | **+1** |
| **cu done 整理**（自然推理结束，常规） | 重置为 2 条 `(system, user)` | **+1** |

- 前两行发生在 **cu 内部**（追加式）；后两行发生在 **cu 边界**（换 cu）。整理有两种触发：cu done（常规，每次自然推理后）与 cu 中部（应急，上下文太长/目标偏）。

## 6. 落盘

- **方式**：**append-only**，追加到"当前版本号文件"尾部，不重写已有行。

### 6.1 每行格式（type 分派）

每行 = 一条 JSON，顶层 `type` 字段区分行型，两类行混存同一文件，**行序 = 权威顺序**：

```jsonl
{"type":"state","state":"loading","ts":"2026-10-23T11:50:27+08:00"}
{"type":"message","ts":"2026-10-23T11:50:28+08:00","role":"system","content":"..."}
{"type":"message","ts":"2026-10-23T11:50:29+08:00","role":"user","content":"..."}
{"type":"state","state":"loaded","ts":"2026-10-23T11:50:30+08:00"}
```

换 cu 新文件首行（承接前版本，无 `loading`/`loaded`）：

```jsonl
{"type":"state","state":"continued","ts":"2026-10-23T11:52:00+08:00"}
{"type":"message","ts":"2026-10-23T11:52:01+08:00","role":"system","content":"..."}
```

- **`type=message`**：一条 `Message`（`role`/`content`/`tool_calls`/`tool_call_id`/`reasoning`），`meta.ts` 平铺为顶层 `ts`。
- **`type=state`**：状态转移标记，`state` ∈ `{loading, loaded, continuing, continued, unloading, unloaded, idle}`。状态转移与内容追加共享同一条时间线，是唯一能保证二者顺序一致的存法（也因此否掉"文件名后缀 / 单独 manifest"两个备选）。
- **顺序语义**：
  - **醒时装载**：`loading` 行 → 起点消息（`system`,`user`）→ `loaded` 行；`loaded` 是装载结束标记，起点消息是装载的产出，排在它前面。
  - **换 cu（承接）**：新文件首行 `continued`（= 承接前版本、直接就绪，无 `loading`/`loaded`），后跟起点消息。旧文件尾追加 `continuing`（= 本版本正常关闭、同 wake 有后继）。
- 显式 `type` 分派 > 隐式猜字段（有无 `role`/`state`），将来加第三类行不破坏判据。

### 6.2 时间戳（ts）

- 在**消息产生处**记录 `meta.ts`（assistant = `chat` 返回时刻、tool = `on_tool_call` 返回时刻），append 复用该 ts。**无差值问题**（早期"落盘时统一填 ts、有差值"的表述已作废）。
- **磁盘存 ISO 8601 + 本地时区偏移**（`"2026-10-23T11:50:28+08:00"`），**内存 `meta.ts` 仍 float epoch seconds**，序列化层映射一次：写盘 `float → datetime.astimezone().isoformat()`，读盘 `fromisoformat()` 转回。
- **带偏移必须显式写**：`datetime.now().isoformat()` 对 naive datetime **不带偏移**（产生歧义），须 `datetime.now().astimezone().isoformat()`（或 aware now）。
- 排序/比较一律用转换后的 float，不依赖字符串字典序。
- 与事件文件的时间格式刻意不同：事件 = 短命消费队列，`at` 存 epoch float；意识 = 留档历史，`ts` 存 ISO 本地偏移。用途不同，格式不同。
- `ts` 只做"何时"的墙钟元数据，默认不进模型可见文本。
- content 形态（详见 Message 任务单）：文本消息 `str | list[parts]` 不归一；tool 内部 `dict`、出站 `json.dumps` 成 str。

## 7. 存储布局

```
agent_root/
  consciousness/                              # 目录名待定
    meta.json                                 # 无意识文件时的版本号权威 {next.wake_version, next.context_version}
    <wake_version>.<context_version>.jsonl    # 当前活跃文件（唯一，append-only，JSON Lines）
    archive/
      <wake_version>.<context_version>.jsonl  # 已关闭文件（continuing / unloaded 后归档）
```

- **正常目录只放当前活跃文件**（唯一）；文件落 `continuing` 或 `unloaded` 后**移入 `archive/`**（文件名不变，靠 `<wake>.<context>` 全局唯一标识版本）。
- 无活跃文件时以 `meta.json` 为版本号权威（有意识文件则删 meta.json），语义见 interface.md §6。
- 版本号用于**历史回溯 / SEQ 标识**，不用于"找当前活跃文件"（活跃文件 = 正常目录下那一个）。

## 8. cu 生命周期与事件处理

- **事件 = 插入当前 cu**（类似干预），不是新建 cu：事件源 `EventStore.emit` 落盘 pending → 介入点 `take_all` 取走 → 渲染 → 作为消息 append 进 `cu.material`。无并发（`emit`/`take_all` 锁互斥；介入点是状态机稳定点位，取走时 cu 不在 `await chat`）。
- cu 是**执行单元**，生成/换的时机由意识上下文决定：
  - **生成**：意识空 + 醒 → 生成 cu，cu 与意识上下文一致（material = messages 起点）。
  - **保持（不换）**：正常推理自行推进；介入不干预；介入只插一句。
  - **换 cu**：**cu done**（一次自然推理结束）或 **cu 中部整理**。
- **cu 销毁是自动的**：done → runtime `_finish` pop；未 done 要停 → `cu.interrupt()` 设 flag，`_advance` 循环顶部走 `_finish(Interrupted)` → pop。无需显式销毁（旧注记「销毁权上收 / 只在整理时销毁」作废）。

## 9. cu done = 整理 = 版本切换

- cu done（一次自然推理结束）**不续命**，换 cu。
- cu done 整理上下文合理：**快速蒸馏**（保留结论 + 关键信息，不留所有细节）+ **重新定向**（结合目标/动机，判主题继续/换，定下一方向）。
- cu done 整理 与 cu 中部介入整理**统一**：都是「压缩 + 重定向」，触发不同（自然结束 vs 上下文太长/目标偏）。
- 故 **cu 消失 = 版本切换**（由上述分析得出，非固守）。

## 10. 生命周期全流程（串成一条线）

```
出生 → 第一次醒 wake_version=1
  → 生成 cu，落 <1.1>.jsonl：loading / system / user / loaded
  → 推理（cu 内部，追加式）：
      事件插入 → 作为消息 append，context_version 不变
      工具循环 → on_tool_done 落盘（append assistant+tool，各带 ts）
  → cu done（自然推理结束）→ on_done 落盘最终消息
      → 控制层整理：蒸馏 + 重新定向（判主题继续/换）
      → 换 cu：先写新 <1.2>.jsonl（首落 continued + 起点消息 system / 重定向 user）
              再旧 <1.1>.jsonl 尾落 continuing → 归档进 archive/
      → context_version +1
  → （重复：事件插入 → 推理 → cu done 整理换版本）
  → 睡觉：写 meta.json({wake+1,1}) → 当前文件落 unloading → unloaded → 归档进 archive/，wake_version 递增
  → 再醒 wake_version=2 → 从记忆重新装载 → 生成 cu，落 <2.1>.jsonl：loading / system / user / loaded
```

- 换 cu 与入睡是**两种不同的关闭方式**：换 cu → 旧文件尾 `continuing`（有后继）；入睡 → `unloading`/`unloaded`（醒终结）。旧模型两者都落 `unloaded`，已修正。
- 关闭顺序（异常安全，统一原则）：**归档/关闭旧文件前，必先落下后继权威**。切 → 先写新文件（`continued` + 起点）→ 旧尾落 `continuing` → 归档旧；睡 → 先写 meta.json → 归档旧。见 interface.md §6.1。

## 11. 活跃判定

- **活跃文件不在 `archive/` 下**：在 `archive/` = 已不活跃（历史）。
- 当前活跃文件 = **正常目录（非 archive）下**、文件内**最后一条 `type=state` 行的 `state`** ∈ `{loading, loaded, continued, idle}` 的那一个（正常时唯一）。
- 存在活跃文件 → **意识在跑**（最后 state 行 ∈ `{loading, loaded, continued}`）；最后 state 行 = `idle` → **醒着但无 cu**（意识活动停，非睡，后必接 `continuing` 或 `unloading`）；**正常目录无活跃文件** → 意识停（睡/空），须从记忆装载新上下文。
- `empty`（内存）= 正常目录无活跃文件（出生前 / 入睡后未再醒），历史都在 `archive/`；此时正常目录有 `meta.json` 作版本号权威。
- 异常时正常目录可能有两个文件：① 旧 `continuing` + 新 `continued`（旧已关、活跃唯一=新）；② 旧 `loaded` + 新 `continued`（写新后关旧前掉电，两个都"活跃"，恢复靠比较版本号取大）。

## 12. 两层「整理」与失效文件

两层整理，别混：

| 层 | 触发 | 输入 | 产出 |
|---|---|---|---|
| **控制层整理** | cu done（常规）/ cu 中部（太长·偏） | 当前活跃上下文（刚结束的推理） | 新版本 2 条起点（system + 重定向 user） |
| **元层整理** | 睡后（start_unload 与 unload_done 之间） | 这次 wake 全部版本（archive 里中间 `continuing` + 当前末版本 `unloading`） | 记忆更新 + 下次醒的 2 条起点 |

- `archive/` 里的文件**元层可访问**（整理记忆的原料），只是不会变回意识。
- 一次 wake 对应多个版本文件（`<wake>.1` 尾 `continuing`、`<wake>.2` 尾 `continuing`、…、`<wake>.n` 尾 `unloaded`）：`continuing` 标记同一 wake 的连续分段，`unloaded` 标记 wake 终结。元层处理时末版本还在 `unloading`（未归档），`unload_done` 后才落 `unloaded` + 归档。
- 整理流的输入 = 这些版本文件；产出 = 记忆更新 + 下次醒的 2 条起点。

## 13. SEQ 树化

- **叶子 = 最原始意识内容**（每次醒的每个版本文件）。
- 远期 SEQ 可**合并简化**，像树一样向内收敛。
- 每条消息的 `meta.ts` 支撑"时间维度"沉淀（合并/淘汰以时间为依据）。

## 14. 与 Message 类型改造的关系

本体系落盘的**数据载体** = `list[Message]`（`Message` 含 `meta.ts`，内存 float）。该类型改造已冻结成任务单 `2026-10-23-cu-material-message.md`，已完成（commit `2fcac25`）。落盘序列化 = `Message` → JSON Lines 一行（`type=message`，`meta.ts` 平铺为顶层 `ts`、值转 ISO 本地偏移字符串，见 §6）。

## 15. 缺口 / 遗留（仍开）

1. **掉电恢复**（方案已适当考虑，未覆盖的记遗留，不追求全）：
   - 已覆盖：统一原则「关闭前必先落下后继权威」（切先写新文件、睡先写 meta.json），保证正常目录下「要么意识文件、要么 meta.json」恒成立，无"无活跃文件"窗口。
   - 未覆盖（留待后置）：① 切：写新文件后、关旧前掉电 → 正常目录两个活跃文件（旧 `loaded` + 新 `continued`），恢复靠"比较版本号取大"；② append-only 掉电最多丢"最后半行/半轮"（原子写整体后置）。
2. **装载机制**：记忆 → 2 条 `(system, user)` 的具体接口（装载/蒸馏），接草稿待议的"装载模块"。
3. **整理/重定向的执行机制**：cu done 整理的蒸馏+重定向由谁执行（元层 LLM 还是意识层判走向），具体形态未定。
4. **目录名**：`consciousness/` 还是别的，待定。
