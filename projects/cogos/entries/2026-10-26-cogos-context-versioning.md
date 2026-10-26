# 意识文件版本策略 + 五元决策（2026-10-26）

## 结论（活跃，已落码 commit `2ae2e9d`/`9056050`，全量 1369 passed）

承接 10-25 方向对齐之后、LLM 接线之前，把「版本/恢复」与「介入决策」两块架子收口落码。下文区分**已落码**与**后置**（仅设计、未接线）。

### 1. 介入决策五元 Proceed/Relay/Switch/Stop/Sleep（已落码）

介入点改名 `tool`/`finish` → `tool_done`/`reasoning_done`（回调名 `on_tool_done`/`on_done` 不动）。决策由四元扩为五元：

- **Proceed**＝无助推继续，仅工具点（程序回灌工具结果）。
- **Relay**＝有助推继续，追加一条消息。
- **Switch**＝重构上下文继续，替换 LLM 上下文内容。
- **Stop**＝停止本轮：settle cu + 转 IDLE。
- **Sleep**＝入睡：settle cu + 意识层不动状态、元层 `fall_asleep` 走卸载。

why 五元：10-25 把 Sleep 降为 Stop 的去向，但 Stop 的「去向」仍有歧义（unload→ASLEEP 还是 idle）。把 Stop/Sleep 拆成两个决策，语义各归其位。默认决策＝tool_done→Proceed、reasoning_done→Stop（推理点无程序回灌，只能元层给输入或停）。换/不换＝内容「替换/追加」、非 cu；推理点原 cu 已 done、必换 cu 是实现约束。

### 2. 弃 wake_version，文件命名 + meta 三字段（已落码）

wake_version（醒次数）无独立语义，进程重启/归一化会推进它＝**进程生命周期泄漏进意识语义**。10-25 的「wake_version→day、日界推进＝full 档整理专属」一并取代：date 不再是需推进的计数器，而是**文件生成时刻系统日期的客观事实**。

文件名 `<YYYYMMDD>.TZ<offset>.V<version>.jsonl`（如 `20261024.TZ0800.V0007.jsonl`，日期段/时区段从 `current_day` 派生）。`meta.json` **始终存在**、只存两信息三字段：

- **birth**：出生精确时刻（带 offset），未出生 `null`。
- **current_day**：当前意识日起点＝该日第一份文件生成时刻，初始 `null`。
- **next_version**：下一版本号，初始 `null`。

出生时 `birth == current_day == 出生时刻`、`next_version = 2`（**非 0 点**）；之后 birth 固定、current_day 跨日/切时区/停机重启时更新、next_version 随文件递增。

### 3. 文件切换 + meta 更新＝提交点（已落码）

生成新文件的时机：`start_load`、`Switch`；`unload_done` 只追加状态后归档、**不生成新文件**。原则：**新意识内容产生时才生成新文件；生成新文件时才更新 meta**。

meta 更新规则（生成新文件时）：

1. meta 无效（`birth == null`）：出生，生成 `V0001`，`birth = current_day = 出生时刻`，`next_version = 2`。
2. meta 有效且系统时间在当日区间：用 `next_version` 作版本，生成后 `next_version + 1`。
3. meta 有效且不在当日区间：切日期，`current_day = now`，version 归 1，`next_version = 2`。

停机数日/跨多日＝规则 3 的自然情形，无特判。**meta 原子写＝文件生效的提交点**，顺序：新文件完整生成 → 原子写 meta → 旧文件封口归档。掉电在提交点前＝新文件是未提交孤儿（version＝next_version 天然选不中）、旧文件完好继续；提交点后＝新文件生效、旧文件残留待清理。

### 4. 当日定义 + 时区（已落码）

`current_day`＝该日第一份文件生成时刻（可不从 0 点起）。当日＝`[current_day, current_day 日期部分的 24:00)`，**不是** `[current_day, current_day + 24h)`；跨日判断比较绝对时间。时间全带时区、本地时间、ISO 8601 带 offset。换时区 meta 不立即变，等原 offset 当日跑到 24:00 才切日期（新 current_day 可能日期回退或跳跃，都接受）。

### 5. 废归一化 settle_to_asleep（已落码）

`settle_to_asleep` 全废（`start` 启动归一化 + `stop` 收口都废）。`stop`＝停 monitor + 停 control + `cu.interrupt("shutdown")`，停在当前状态、不进 ASLEEP。上电后如何接续归元层，意识上下文不掺和。

### 6. 上电恢复＝meta 定位上一份文件（已落码）

上电恢复不是「选活跃文件」（ASLEEP 无活跃文件），而是「恢复上次下电前状态」：meta 的 `current_day` 派生日期+TZ、`next_version - 1` 作版本，拼出确切路径。

- 存在 → 读末态（last_state）还原。
- 不存在 → 已归档 → ASLEEP。

「存在/不存在」＝「上次是否 ASLEEP」的完整判据。删 `ACTIVE_STATES`（实现时加的冗余判据）：归档靠 rename 天然移出根目录，掉电残留多文件时「拼确切路径 + 判存在」就够。副作用：还原不忠实（UNLOADING 被还原成 ASLEEP）+ `_FILE_TO_STATE` 的 UNLOADING 映射成死代码 + 中间态文件泄漏。

### 7. heartbeat.json（已落码，只埋不消费）

独立 `heartbeat.json` 记录进程生命周期，与 `meta.json`（意识版本）正交。动机＝wake_version 的病根是「进程生命周期泄漏进意识语义」，heartbeat 把进程信息放回它该待的地方。

字段：`startup`（进程启动时刻）、`last_heartbeat`（最近心跳）、`shutdown`（优雅退出时刻）。`shutdown` 只在优雅退出时写入；异常下电（kill -9/断电）来不及写，故 `shutdown: null` 本身传达「上次非正常下电」。

写入三约定：**原子写**（TmpFilePair，保证读方不见半截 JSON）、**周期独立于 tick**（`HEARTBEAT_PERIOD = 1.0` 独立常量，不从 tick 推导）、**节流用 monotonic、写出的值用墙钟**（monotonic 跨进程/重启无意义，写进文件的必须带 offset 的 ISO）。

### 8. 醒/睡解耦 + 出生判断（已落码）

文件生命周期绑「上下文代际（Switch 换一份）+ 日期（跨日换一份）」，**不绑「一次醒」**：一次醒可多份文件（多次 Switch），也可一份（无 Switch）。醒/睡状态完全由 active 文件的 FileState 承载，meta 不再承载醒/睡状态。`is_first_wake` → `Consciousness.birth`（null＝未出生 / 出生时间）。

### 9. 状态机与决策→文件操作（不变）

五元决策下状态机不变：FileState 七态 + State 五态 + 决策→状态映射均不变，版本方案（文件名/meta）与状态推导正交。决策→文件操作：Proceed/Relay 不动文件（Relay 注入消息经 checkpoint 落盘，非决策触发的状态变更）；Switch 新文件 CONTINUED、旧文件 CONTINUING；Stop 追加 IDLE；Sleep 意识层不动、元层 `fall_asleep` 走 `start_unload`/`unload_done` 追加 UNLOADING/UNLOADED。

## 被否 / 取代

- **wake_version（醒次数）** → 废。
- **10-25「wake_version→day、日界推进＝full 档整理专属」** → 被版本方案取代。
- **is_first_wake** → 由 `birth` 取代。
- **current_day 存日期字符串（`2026-10-24+0800`）** → 否，改精确时刻（当日起点），以正确表达切时区后「新一日非 0 点起」。
- **current_day＝旧 current_day 日期部分的 24:00（切日期时）** → 否，改事实值（该日第一份文件生成时刻）。
- **当日＝`[current_day, current_day + 24h)`** → 否，改 `[current_day, current_day 日期部分的 24:00)`。
- **settle_to_asleep（start 启动归一化 + stop 收口）** → 废。
- **ACTIVE_STATES（状态过滤选文件）** → 删，改 meta 定位 + 存在性。
- **「选活跃文件」表述** → 改「恢复上次下电前状态」。
- **介入决策四元 Proceed/Relay/Switch/Stop** → 10-26 扩为五元（Sleep 从 Stop 去向回升为决策）。

## 后置（仅设计、未落码，随 LLM 接线）

- **恢复判据**：元层据恢复态 + 时间戳决定 resume/switch/收口；`Consciousness.resume()` 接口（重开 cu、不改状态、不写 state 行）未落码。
- **状态时间戳**：`last_state` 返回 ts（文件最后一行 ts，append-only 自然产物），随恢复判据后置。
- **Relay 形状**＝`Relay(new_messages)` + append 后继续（机械最小，G7 留白）。
- **meta 值存 `+08:00`**（`isoformat` 带冒号）、文件名 offset 用 `%z` 得 `0800`，一处 cosmetic 差。
- **`_FILE_TO_STATE` 未补 UNLOADED→ASLEEP**（死代码，归档文件不进根目录）。

## 代码影响点

- `consciousness.py`：`ConsciousnessStore` meta 读写（birth/current_day/next_version）、文件命名、`previous_file`；五元决策 + `InterveneType`（tool_done/reasoning_done）；`_restore`（meta 定位）；删 `ACTIVE_STATES`；`is_first_wake`→`birth`。
- `meta_layer.py`：五元决策 `_default_decision`；废 `settle_to_asleep`；`stop` 停当前状态；Monitor 循环顶部写 `heartbeat.json`。
