# runtime 架子重设计（2026-10-22）

> 状态：讨论进行中，收集 YZ 要求。当前 `runtime/` 骨架（`6563b28`）几乎无用，重新讨论具体实现。

## 准则（整体要求，第一条）

1. **运行态与盘上状态一致**：任何变化都需落盘；重新上电后基本回到掉电前状态（除非掉电前写入的内容没落盘）。
   - 原子写（tmp+rename，参考 `feishu/utils.py:TmpFilePair`）**先不实现**：先简单处理（普通写），记遗留（担心掉电写坏文件，可能现在想多了）。

## agent 根目录（2026-10-22）

- agent 有一个**独立根目录**（`agent_root`，glossary 已钉）。`memory/` 是其中一个子目录；**事件是另一个子目录**（命名倾向 `events/`，待定）。
- 事件子目录访问层归属 = **程序/机制层**（收到落盘、介入点取走），非意识层、非元层 LLM。

## 事件模块（YZ 提出，2026-10-22）

### 方案

1. **通知方式 → 轮询**：不走信号通知，走轮询——介入点（on_done/on_tool_call 后）判有没有事件，有就直接处理；心跳判有没有事件，有且 ASLEEP 就唤醒。
2. **事件种类与描述**：见下方小节。

### 事件种类与描述（kilo 补全，2026-10-22）

> 事件两个形态：**盘上存储**（结构化 envelope，落 pending 文件）vs **模型可见**（渲染文本）。下面 list 两者的共用 shape。

| 事件 | 描述字段 | 现状 |
|---|---|---|
| 通信消息 | 来源（号码/群ID + 对应人名/群名）、消息时间、消息内容、（附件） | 现走 Perception 直进 consciousness，**未入事件**，需改造 |
| 提醒 remind | 到期时间 due_at、通知时间 at、标题 title、事项内容 content | 现有 `timer.notify` 有 title、无 content，**需补内容字段** |
| 终端完成 term.done | 会话索引 session、退出码 exit_code、是否取消 cancelled | 现有 |
| 终端通知 term.notify | 会话索引 session、token | 现有 |
| Web 作业完成 web.{search,fetch}_done | 句柄 WEB:id、状态 state、错误 error | 现有 |
| 文件传输完成 phone.{download,send_file}_done | 句柄 job_id、状态 state、items、错误 error | 现有 |

补充：
- **通知时间 at** 是所有事件共有字段（`Signal.at` 已有）；remind 重启补发 miss 靠 at＋overdue_seconds 判断；现 `render_event` 未渲染 at，需补进描述。
- 通信消息要从 Perception 改道入事件队列（新设计「事件是唯一输入」）。
- remind 的「事项内容」现有 Timer 无此字段，需给 Timer 补 content（或等效）。

3. **事件存储**：收到直接落盘，全部存入「未处理事件文件」（pending，append-only）。
4. **读取**：把 pending 文件 rename 成编号文件（原子取走），内容加载进上下文，介入点一次性拿到全部事件；rename 后 pending 清空（转移到编号文件）。
5. **暂不考虑**：① 突然掉电漏事件；② 历史事件文件太大。

### 文件表示与排序（2026-10-22）

- 盘上 = **JSON Lines**：每行一条事件 JSON（`{kind, payload, at}`），append 一行＝追加一条。不用单 JSON 数组（追加须重写全文件，违背 append-only＋原子追加）。
- 加载 = 编号文件逐行 parse → **按 `at` 排序**（非 append 序，因重启补发 miss 的 remind 事件 at 早于落盘时刻）→ 渲染文本进上下文。
- 渲染仍走 kind→路径前缀映射（现 `render_event`），`at` 需补进描述。

### 接口与装配（2026-10-22）

- **单实例**：一个 agent 一个事件实例（绑定 `agent_root/events/`），多 agent 各用各的根目录天然隔离。并发点在单 agent 内多源并发写同一 pending 文件，靠实例内部锁串行化。
- **事件源连接**：统一走 `SignalSink.emit` 一个接口，**不是逐事件单独接线**。现状：terminal/web/timer/phone file 已 `sink.emit(Signal)` 发信号（sink 现在是 `_QueueSink` 内存队列）；新设计把 sink 换成一个 `EventStore` 实例即全接好（一处装配改动）。通信消息现状不走 sink（Perception 直进 consciousness），需新写「IncomingMessage → Signal」转换 + 接入同一个 sink。
- **接口**：
  - `emit(signal) -> None`：同步、非阻塞语义、append 一行 JSON 到 pending（收到即落盘）；内部锁。
  - `take_all() -> list[event]`：锁内 rename pending→编号文件（原子取走）→ 逐行 parse → 按 `at` 排序返回；无事件返回 `[]`。返回结构化事件，**渲染归调用方**。
  - `has_events() -> bool`：判 pending 文件存在且非空（心跳轮询靠它）。
- **补充（kilo 提）**：
  - **rename 竞态**：`emit` 与 `take_all` 必须共用同一把锁，否则 take_all rename 时 emit 正在 append 会丢一行。
  - **编号文件命名**：递增整数 or 时间戳，待定（重启后需从盘上已有编号推断下一编号）。
  - **fsync 后置**：emit append 后 flush 即可，fsync 每次代价高；掉电漏事件已在「暂不考虑」。
  - **人名/群名映射归属**：事件实例存原始 Signal（号码），映射在渲染时做（介入层持有 profile）；实例不持 profile、职责单一。

### 渲染（上下文组织层，2026-10-22）

- 事件模块职责**到此为止**：`emit/take_all/has_events`，返回结构化事件（kind＋payload＋at），**不碰渲染**。
- 渲染归**上下文组织层**：拿到事件列表后按统一格式转成模型可见文本；**格式定死后每种事件写一个转换函数**，新增事件类型只加一个函数，天然解耦。
- 格式约定（面向模型，一条事件＝一行）：`[<类别前缀>] <字段>=<值> ...`；类别前缀 = impl kind → 模型面类别映射（沿 `_EVENT_PREFIX`），字段 = 该事件的模型可见字段（号码→人名、内部 id→对象索引在渲染时做）。
- 即：沿用现 `render_event` 形态，把「特判」抽成「每 kind 一个转换函数」。

### 接口规格（待 YZ 审核，2026-10-22）

```python
# cogos/agent/event_store.py（新文件）

class EventStore:
    """agent 事件存储：收到即落盘（append-only pending），原子取走进编号文件。

    单 agent 单实例，绑定 agent_root/events/。全同步方法 + threading.Lock，
    锁内互斥 emit（append）与 take_all（rename），避免 rename 竞态丢行。
    """

    def __init__(self, root: Path) -> None:
        """root = <agent_root>/events/，不存在时创建；扫描已有编号文件得下一编号。"""

    def emit(self, signal: Signal) -> None:
        """锁内 open(pending, 'a') 写一行 JSON（{kind, payload, at}）+ flush。
        同步、非阻塞语义（完成返回＝已落盘）。实现 SignalSink.emit 协议。"""

    def take_all(self) -> list[Signal]:
        """锁内：无事件返回 []；否则 rename(pending → root/NNNNNN.jsonl)，
        逐行 parse（坏行丢弃）→ 按 at 排序 → list[Signal]。"""

    def has_events(self) -> bool:
        """pending 文件存在且 size > 0。"""
```

```python
# cogos/agent/events.py（改造现有 render_event）

def render_event(signal: Signal) -> str:
    """按 kind 分发到 _render_<kind>(payload, at)，
    输出 `[<类别前缀>] k=v ...`；前缀映射沿 _EVENT_PREFIX 并补 chat.message。"""
```

**决策点（YZ 已拍板，2026-10-22）**：
1. 方法**全同步 + threading.Lock**：临界区内无 await 点 → threading.Lock 够；单事件循环下同步函数天然不抢占，锁主要为防御未来线程化＋文档化；若将来文件 I/O 异步化（aiofiles）才换 asyncio.Lock 且 emit 也 async。
2. 编号文件**时间戳命名** `<epoch_ns>.jsonl`（防撞：目标已存在则加后缀）；事件本身有 `at` 时间戳（排序用它，与文件名时间戳两回事）。
3. **原子写整体先不实现**（普通写），记遗留——不止事件，全部先简单处理。
4. **本次实现范围**：`EventStore` + `render_event` 改造 + 通信消息转 Signal 的转换函数（**写好＋单测自验，不接线**）；接线（sink→EventStore、on_message 改道）留到整体就绪。其他事件源（timer/terminal/web/phone file）Signal 已构造好、无需新写，只留接线；remind 的 content 字段（Timer 补）单列。

## 意识上下文与 cu（已收口 → 见 `2026-10-23-cu-context-persistence.md`）

- 目标：**意识上下文的任何变化都增量落盘**，跟事件 pending.jsonl 同用 append-only JSONL（机制对称；语义/格式不同——事件=消费队列 epoch `at`，意识=留档历史 ISO `ts`，见 `2026-10-23-cu-context-persistence.md` §6）。
- cu.material 的 append（改造前现状观察，仅作背景）：`_advance` tooling 态末尾 `append(assistant_msg)` + `append(tool_msg)`（runtime.py:127-135）；初始内容在 `cu()` 创建时传入。新模型下 append 有多处——事件插入、`on_done` 最终 assistant、工具循环（见该件 §8/§10）。
- **介入点落点 = 新增 `on_tool_done` 回调**（YZ 定）：`_advance` tooling 态分两次进循环——第一次调 `on_tool_call`（工具执行前，回调内执行工具）、第二次 append assistant+tool 进 material → `state=pending`。`on_tool_done` 落点＝**第二次 append material 后、`state="pending"` 前**，即「工具执行完、结果入 material、下一轮 chat 前」。
- `on_tool_done` **仅成功路径触发**；失败路径（`on_tool_call` 抛异常→Error("tool_error") / 为 None→invalid_request / interrupt→Interrupted）都汇到 `on_done`。
- `on_tool_call` **不能作介入点**（工具执行前）；旧 glossary「介入两调用点 on_done/on_tool_call」表述不准，收口时改。
- 待定 → **已收口**（见 `2026-10-23-cu-context-persistence.md`）：① 真相 = 落盘文件是投影的持久载体，记忆才是唯一持久实体；② 落盘粒度 = **每条消息一行**（含 `type=state` 状态行），详见该件 §6.1。

## 遗留问题

- **意识停摆 vs 心跳失察**：是否存在某些情况下意识已停止、但心跳判断不出来。若出现，事件无法经介入点通知到 agent（agent 已停摆）。不仅影响事件，可能波及其他层面（具体影响暂不分析，只记录）。
- **AWAKE 且 idle 无法通知**：无 cu 在跑（如 wait 阻塞）时介入点不触发，事件靠谁发现未定（心跳 AWAKE 也判事件 vs 只靠介入点）。
- **事件内容过多爆上下文**：一次取走的事件总量过大可能撑爆上下文，**暂不处理，后面遇到再说**。
- **原子写（TmpFilePair）暂不实现**：先普通写，担心掉电写坏文件，可能想多了，记遗留。
- **工具调用不应走异常失败**（YZ 提，后续排查）：工具失败应**让模型知道**（报事实喂回，LLM 自己决策），而非 `on_tool_call` 抛异常 → cu 以 `tool_error` 终止（现状偏粗暴，且失败轮内容不落盘、丢失）。排查点＝区分「工具返回失败结果」（喂回）vs「工具执行抛异常」（现状废 cu）；与准则"任何变化都落盘"有张力。

## 后续要求（待补）
