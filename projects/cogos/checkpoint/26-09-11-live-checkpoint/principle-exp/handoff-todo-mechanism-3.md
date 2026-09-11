# handoff-todo-mechanism-3｜机制最小实现跑通 + 转向"强规则遵从"实验

> 上游：`handoff-todo-mechanism-2.md`（v0.6 主体定稿，剩 schema + 最小验证两项）。
> **主产物：`todo-list-mechanism.md`（v0.6 + §十四 最小验证临时约定 + §十五 定稿提示词）。**
> 代码产物：`/tmp/kilo/vision/mech.py`（机制最小实现）+ `image_field_chat.py`（宿主，新增 `--mech` / `--strict`）。
> 本会话脉络：审核 v0.6 → 纠正明显逻辑错误 → YZ 重定目标（先证遵从，再谈机制）→ 写机制最小实现 → 跑通 → 转"强规则能否让模型遵从"实验。
> **关键转折：YZ 判断"先证明人工干预能把它拉回计划，再谈机制"；并把'遵从'与'正确'分成两条轴。**

---

## 一句话状态

- **机制最小实现已跑通**（`mech.py` + `image_field_chat.py --mech`）：`build_plan` 定格 → 撞线硬打断 `[check-in]` → 模型用 `update_progress` 消触发 → `finish_task` 收尾；**无逃逸、无死循环**。
- **YZ 重定优先级**：目的 = 模型**遵从按步骤**。先证"偏离时能停、人工干预能拉回"，**人工干预有效之后**才固化成机制。原则（提示词只能请求）让位于目的。
- **方案重定向**：不再扩机制，改试"**强规则 prompt**"。V1 已让**过程基本遵从**（逐个标注、每步声明 + 证据、不提前收尾）。
- **两条轴要分开**：**过程合规**（规则可控）vs **结果正确**（需可验证反馈，规则补不了）。
- **下一步候选**（待 YZ 定）：(a) 修 V1 两条漏点重跑；(b) 跑 3 组看稳定性；(c) 据数据决定机制缩到多小。另有**单步调试器**（人工干预入口）已设计、未实现。

---

## 必读（新会话只读这些）

1. **本文件**。
2. **`todo-list-mechanism.md` v0.6 + §十四 / §十五** — 机制正文 + 最小验证临时约定 + 定稿提示词。
3. **最新实验**：`/tmp/kilo/vision/todo_strict1/`（强规则）、`todo_exp1/` `todo_exp2/`（机制）——`raw.jsonl` + `shots/` + `run.log`。
4. **代码**：`/tmp/kilo/vision/mech.py`、`/tmp/kilo/vision/image_field_chat.py`（`STRICT_SYSTEM` 在文件顶部）。

---

## 本会话已定论

### 1. 对 v0.6 的纠错（已改入正文，属"明显逻辑错误直接改"）
- `remaining` 漏扣 `retired_spent`：改为 `total − retired_spent − planned_total`（§6.4）。
- 不变量口径统一为 `retired_spent + Σ actual_rounds ≤ total`（§4.2 / §4.3 / §5.1 / 八 共 4 处）。
- `N_retry` 措辞统一为"连续无效提交（超限 / schema / 写错行）"（§4.2 / §4.4）。
- 删 `MechState.spent` 冗余字段；`Table.spent` 注明不含 retired。
- `planned_total` 注释补 rebuild 语义。

### 2. 最小验证临时约定（写入 §十四）
- 返回最小版 `{ok, table, budget}`；`problem` 只实现 7 个码。
- 完成语义：`finish_task` 唯一终态；全 done 转注入"请 finish_task"；`status` 只 `completed / partial`。
- 参数：`total_budget=15`、`K=5`、`N_retry=2`；`N / stall / drop_streak` 第一轮不实现。
- **`note` 字段砍掉**（用途不明，与 `reason` 重叠）。
- **当前步由机制自动置 `in_progress`**（D1 隐含补丁）。
- **`max_inner` 用尽 = 一种强停**：[stop] + 预留 1 轮 → partial / aborted。
- 多工具口径：每个业务工具 `actual +1`，一组执行完再判撞线。

### 3. 提示词定稿（§十五）
- `[status]` 措辞：**不写"可忽略"**，改"请对照计划审视：进度是否偏航、计划是否仍成立、有无风险；无异常则无需调用工具，继续执行"。
- 系统提示词 + 5 条注入消息 + 人给任务提示词，全文见 §十五。

### 4. YZ 的目标重定（本会话最重要）
- **目的优先于原则**：先把"遵从"做出来，做不到原则无意义。
- **顺序**：先证"偏离 → 停机 → 人工干预 → 拉回"，**有效之后**才谈机制固化。
- **Kilo 为什么能照 todo 走**（分析结论）：不是模型天生照 todo，而是 harness 凑齐了 **①强制流程 prompt ②结构化 todo 工具 + 每轮回显 ③细粒度循环 + 每步反馈 ④可验证反馈（测试/编译）⑤后训练先验**。视觉坐标任务缺 ②③④ → 漂。
- **两轴分离**：规则能压"过程"（跳步/批量/不收尾），压不动"判断"（它做错却自认为对）——后者要可验证反馈。

---

## 实验结果（3 组，均已完成）

| 组 | 配置 | 过程 | 结果（中心 px） |
|---|---|---|---|
| `todo_exp1` | `--mech` budget=15 | build_plan → see×2 → **drop mark×7** → update → mark×7 → **drop see** → update → coord×7 → update → finish | `42,113,185,258,330,402,474` |
| `todo_exp2` | `--mech` budget=5 | 多次撞线 drop（see / mark×7 / adjust×7 / coord×7）→ 末轮 `update_progress + coord×7` 混调 → finish | `33,85,138,191,244,297,350` |
| `todo_strict1` | `--strict`（无机制） | **逐个标注**（7 轮各 1 个 mark）+ 每步复述 + 给证据 + 不提前收尾；coord 一轮 ×7 | `33,98,163,228,293,358,423` |

- 真值：x = `34,88,142,197,252,308,366`，y ≈ 34（块宽 ~36–42）。
- **机制组**：闭环成立（拦截 + 消触发 + 收尾），但**软提醒 K 从未触发**（burst 硬打断抢占）；`coord`（只读）也被计入 `actual`；一轮 7 工具 → `actual +7` 粒度粗；budget=5 仍跑完，**partial 未逼出**。
- **强规则组（V1）**：过程**明显改观**——逐个标注、每步声明、给证据。**证明规则对"过程合规"有效**。
- **正确性两轴**：三组都是**系统性越拉越开**（间距 65 vs 真值 ~55），规则没修好它。

### V1 强规则的两个残留漏点
1. **rule 1 与宿主冲突**：规则要求"第一轮只出计划、不做别的"，实际它把计划与第一个 `see` 放同一轮。且我们的单步循环在"只出文字、无工具"时会直接 break，**rule 1 若不改，纯计划独轮会导致运行立即结束**。
2. **`coord` 批量 ×7**：rule 4 只写了"一次观察或一次标注"，`coord` 未纳入 → 一次全读。

---

## 下一步候选（待 YZ 裁决，勿自行推进）

- **(a) 修 V1 两条漏点重跑**：把 `coord` 纳入"一次一个"；去掉/改写 rule 1（或宿主加"续推"）。
- **(b) 稳定性**：同配置跑 3 组，分别记 **过程合规率** 与 **坐标偏差** 两轴。
- **(c) 定机制范围**：若规则已压住过程，机制缩到"续推 + 偏航兜底"这类轻强制；`--mech` 代码先留着。
- **(d) 单步调试器**（已设计未实现）：独立程序（如 `todo_debug.py`），**复用** `image_field_chat.py` 的图工具 + `ChatState`，每工具调用前停；命令 `n`/`a`/`drop`/`say <文本>`/`s`/`q`。定位 = **机制的手动原型**（人工 `drop + say` == 机制的 `drop + 注入`）。掐掉有 A（整批不落地）/ B（回"用户打断"作废回执）两法，**倾向 B**。默认只观测、不介入，留纯观测对照。

---

## 未决（v0.6 遗留，仍未定，本会话未碰）

- **A3 完成语义**：全 done 自动收尾 vs `finish_task` 显式，两条终态关系（本会话临时取后者）。
- **B5** `drop_streak` 与 `stall_count` 职责边界（无效对账归哪个）。
- **B6** `finish_task.status` 枚举语义（`aborted` 是模型主动 vs 机制代收尾）。
- **C8** `rebuild_plan` 是否约束"已完成行不可降级重做"。
- §十三全部遗留照旧。

---

## 产物 / 环境 / 纪律

- 代码：`/tmp/kilo/vision/mech.py`、`/tmp/kilo/vision/image_field_chat.py`（`--mech`、`--strict`、`--total-budget`、`--k`、`--n-retry`）。
- 实验产物：`/tmp/kilo/vision/todo_exp1`、`todo_exp2`、`todo_strict1`（`raw.jsonl` / `shots/` / `run.log`）。
- 文档：`/home/zhengyp/work/A/checkpoint/principle-exp/todo-list-mechanism.md`（v0.6 + §十四/§十五）。
- LM server：`cd /home/zhengyp/work/A/cogos && python3.11 -u -m cogos.lm_service.cli server --port 11434`（KEY `ik_REDACTED`；头 `X-Internal-Key`）。
- 跑法：`cd /tmp/kilo/vision && python3.11 image_field_chat.py --strict --msg '<任务>' --out <dir>`（强规则）；`--mech ...`（机制）。
- 源图 / 真值：`/home/zhengyp/work/A/workspace/windows.png`（1357×764）；菜单 7 项真值 x = `34,88,142,197,252,308,366`，y≈34。
- 纪律：先思路 → 给方案/提示词 → 讨论确认 → 才做 → 一起分析；不跳步。判读**分开记过程合规与结果正确两轴**。
- 注意：宿主在"模型只出文字、无工具"时会结束本轮——设计"纯计划独轮"等规则时要考虑（见 V1 漏点 1）。
