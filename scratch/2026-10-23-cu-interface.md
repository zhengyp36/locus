# 意识上下文接口（Consciousness）（2026-10-23）

> 状态：讨论已收口，待落 entries/glossary。本件为**接口层**草稿；**数据层**（落盘格式 / 状态 / 版本演进 / 活跃判定 / 存储布局）见 `2026-10-23-cu-context-persistence.md`。

## 1. 定位与职责边界

- 意识上下文 = **被动持久化服务**，只做三件事：内存与文件保持一致 + 提供一个 cu 负责推理 + 提供"保存 + 持久化"能力。
- **不做**：加载、介入、切换、睡觉这些**策略**——它们是控制层/元层的事。意识上下文只在这些过程中提供原语。
- 类比 `EventStore`（emit/take_all/has_events，职责到此为止、接线留上层）：意识上下文暴露一组**状态转移原语**，不持有"何时做"的策略。
- 意识上下文文件 = SEQ 树的**叶子节点**；更上层节点（合并/收敛）另立模块，意识上下文不管。

## 2. 接口

### 2.1 构造

```python
Consciousness(path, on_intervening)
```

- `on_intervening`：介入回调，在介入点（on_tool_done / on_done）触发；介入决策逻辑由外部注入，意识上下文只透传素材。

### 2.2 介入回调 on_intervening 参数

| 参数 | 含义 |
|---|---|
| `type` | 介入类型：`tool`（on_tool_done）/ `finish`（on_done） |
| 当前轮次 | 推理经过多少轮次（每调 LLM 一次 = 一轮，需在 cu 里加此信息） |
| 当前 token 数 | on_tool_done 时**不含工具结果**那部分；每次调 LLM 返回后记录当前总 token |
| `wait_to_sleep` | 是否已触发睡眠、等待介入点 |

> 参数在膨胀，将来建议打包成 `InterveneContext` 对象传入（加素材不改签名）——本件先平铺列出。

### 2.3 属性

| 属性 | 含义 |
|---|---|
| `state` | `empty`/`loading`/`loaded`/`unloading`，对外映射 ASLEEP/WAKING_UP/AWAKE/FALLING_ASLEEP（**含义投影**，非状态合并） |
| `is_first_wake` | 是否**从未醒过**（全新 agent / 出生前恒 True）；因版本号不对外，用此接口判装载来源 |
| `context` | `[Message]`，当前活跃上下文，**只读视图**（写走 `append()`） |
| （版本号） | **不对外**，模块内聚 |

### 2.4 操作

| 操作 | 前置 | 动作 |
|---|---|---|
| `start_load()` | `state==empty` | 新建意识文件，追加 `loading` 行 |
| `append()` | — | 注入消息 |
| `load_done()` | — | 加载结束、启动意识（`loaded`） |
| `intervene_done(next_action)` | 介入中 | 介入结束：`next_action` = 继续推理 / 切换；切换需提供 `new_context` |
| `sleep()` | — | 置 `wait_to_sleep` 标志（最终决定，置位后必睡），等介入点 |
| `start_unload()` | 睡流程中 | 追加 `unloading` 行 |
| `unload_done()` | 元层记忆完成后 | 追加 `unloaded` 行 + 归档 |

## 3. 装载（醒）时序

```
start_load()            # state==empty，新建 <wake>.<context>.jsonl，落 loading 行
append(起点消息 ×2)      # 外部注入 system + user（起点从外传入）
load_done()             # 落 loaded 行，启动意识
```

- **`open` 起点从外传入** = 解耦关键：装载模块（记忆→2 条起点）与整理模块（蒸馏→2 条起点）各自算好起点，调同一组原语；意识上下文不关心起点来源。

## 4. 换 cu（intervene_done 切换）

- `intervene_done(next_action="切换", new_context=...)`：一次性完成「先写新文件（首 `continued` + 起点）→ 旧文件尾 `continuing` → 归档旧」（**先新后旧**，见 §6.1）。
- `new_context` 由外部**同步算好传入**（控制层整理的产物），意识上下文不参与蒸馏/重定向。
- `finish`（on_done）介入时 `next_action` **必须是切换**（自然推理结束、不续命）。

## 5. 睡觉流程

### 5.1 触发（两条路径，收敛到同一条线）

| 触发源 | 动作 |
|---|---|
| agent 主动 | 调 `go_to_sleep` 工具 → 工具内 `sleep()`（**立即返回**，只置标志）→ 工具结束后 on_tool_done 介入点走流程 |
| 强制 | 元层直接调 `sleep()` → 最近介入点走流程 |

### 5.2 流程

```
on_intervening 发现 wait_to_sleep=True
  → start_unload()      # 落 unloading
  → 元层处理记忆         # 读这次 wake 全部版本（archive 里 continuing + 当前 unloading）
  → unload_done()       # 落 unloaded + 归档
```

### 5.3 idle 边界

- `sleep()` 置标志后**有活跃 cu** → 等介入点走流程。
- **无活跃 cu（idle/空）** → 推理已停、安全点即当下，可直接 `start_unload()`，无需等介入点（否则 wait_to_sleep 一直挂着——即旧遗留"AWAKE 且 idle 无法通知"）。

### 5.4 入睡拆两段 vs 换 cu 一段（不对称，要钉明）

- 入睡 = `start_unload` → **元层记忆（异步，可能调 LLM）** → `unload_done`，两段夹异步窗口。
- 换 cu = `intervene_done("切换", new_context)` 一次性（新起点外部同步算好传入）。
- 不对称根源：元层记忆处理**异步** vs 控制层整理**同步算好传入**。

## 6. 版本号来源（meta.json）

- **wake / context 都从 1 开始**，不再用 0 表示无效。
- 版本号**不对外**，来源判定（模块内部）：
  - **有意识文件** → 以意识文件名为准（`<wake>.<context>`）。
  - **无意识文件** → 以 `meta.json` 为准（`{next.wake_version, next.context_version}`，即下次醒用的版本号）。
- **一旦有意识文件**（`start_load` 创建）→ 删 `meta.json`。
- **初始化**（agent 配置完、未出生）→ 写 `meta.json = {1, 1}`。

### 6.1 统一原则：关闭当前活跃文件前，必先落下"下一个权威"

| 场景 | 后继权威 | 顺序 |
|---|---|---|
| 切（continuing→continued） | 新意识文件 | 先写新文件 → 归档旧 |
| 睡（unloading→unloaded） | meta.json | **先写 meta.json（{wake+1,1}）→ 归档旧** |

- 保证"正常目录下**要么意识文件、要么 meta.json**"恒成立，掉电安全，也免去"全量扫 archive 找版本号"。

### 6.2 顺序（先建后删）

- **醒**：读 meta.json → `start_load` 建文件 → 删 meta.json（先建后删；若"删后建前"掉电则版本号丢）。

## 7. is_first_wake

- 从 `is_new` 改名（`is_new` 太泛，撞"新上下文/新版本/新 agent"）。
- 语义：**是否从未醒过**（出生前恒 True）；表达"第一次醒来"这一信息。
- 用途：版本号不对外后，外部用它判**装载来源**（True → 出生配置；False → 记忆装载）。
- 与 `meta.json` 正交：`is_first_wake` 判装载来源，`meta.json` 判版本号，别混。

## 8. 遗留（仍开）

1. **on_intervening 同步/异步未定**：介入层做蒸馏/重定向可能调 LLM；若同步回调会阻塞意识上下文，若异步则 `intervene_done` 由外部事后调——控制流要定死。
2. **轮次 / token 素材来源**：轮次需在 cu 里加字段（对 runtime 的改动点）；token 需确认 lm_client 的 chat 返回带 usage。
3. **元层处理记忆的执行机制**：蒸馏由谁执行、何时产出"下次醒 2 条起点"，具体形态未定（与 persistence §15 遗留 2/3 同源）。
4. 掉电恢复细节见 persistence §15（meta.json 先写后删已覆盖主要窗口，原子写整体后置）。
