# design-cog-runtime-min — cog-runtime 最小版设计

> 状态：v1 讨论稿（`../checkpoint/`），内部实现设计已固化（checkpoint-2）。确定后归档 `cogos/docs/`。
> 来源：checkpoint-7~13（cu/ce 设计、预算归属、CogRuntime 边界、cu 最小契约、工具调用）+ `design-cog-runtime.md`（雏形）+ `design-lm-service-min.md`（冻结契约）+ `checkpoint-1.md`（审核意见 1~7）+ `checkpoint-2.md`（内部实现设计 4 问题）。
> 目标：**一个 cu 从创建到 done 跑完一次的最小闭环**，含「不调工具 / 调工具」两条支路。目标态中非最小项一律后置，减法可追溯。

## 一、定位与目的

cog-runtime = 把上层装配好的 cu 调度到 lm-service 上跑完的**纯执行环境**。

- **不决策、不编排、不管语义、不感知"树"**：跑什么、拆成什么 cu、装什么内容，全是上层（cog-func/业务）的活；反写树在 done 回调里由上层做。
- **解决的核心问题只有一个**：有依赖的多个 cu，**并发可控地跑完，失败可归因**（失败态带 error category 交上层决策）。
- **每 agent 一个 CogRuntime**（自己的 cu 队列 + cu 状态机），agent 内自治；agent 间只在 lm-service 竞争配额。

### 1.1 cu 的定位

**cu = CogUnit 的简称**，即**一次 LLM 语义加工的封装**。全文约定：代码/类名用 `CogUnit`，叙述性简写用 `cu`，两者同指。

cu 横跨认知/元/执行三层（哪里有语义哪里就有 cu），但 **cu 只加工语义，不决策、不发起**。决策是元层（agent 整系统）的事，工具调用是 agent 的对外行为，cu 只是链上的语义环节。

### 1.2 组件

| 组件 | 存在 | 职责 |
|---|---|---|
| CogRuntime | ✅ | cu 队列 + 推进循环 + 完成通知 |
| CogUnit | ✅ | 惰性描述 + 执行句柄 + 状态机 + 父子关系 |
| cu 队列（`cu_queue`） | ✅ | 队列 + 并发窗口 |
| LmClient（lm-service） | ✅ | 物理限流 + 归一响应 |
| CogExecutor | ❌ 被吸收 | 执行散在 cu 队列 / cu 状态机 / 推进循环三处 |

## 二、怎么使用（对外接口）

### 2.1 三个对象

上层视角**从头到尾只碰 CogUnit**；CogRuntime 每 agent 启动时建一次；LmClient 藏在 CogRuntime 里，cu 不碰。

```python
from cogos.cog_runtime import CogRuntime

rt = CogRuntime(internal_key="ik_xxx", max_concurrent=4)   # 每 agent 一个：internal_key + 并发上限

cu = rt.cu(
    material=[...], tier="basic",
    tools=[...],                          # 可选，工具清单（结构化 schema，见 4.2）
    callbacks={"on_ready": ..., "on_tool_call": ..., "on_done": ...},
)
await cu.wait()   # 或 cu.no_wait()
```

- `internal_key` 自带 base_url（lm-service 侧改动，见工位 B ISSUES），上层只持句柄、不感知 lm-service。

### 2.2 CogUnit 契约

```python
CogUnit(
    id:       str                    # 自增可读 id（cu_1/cu_2），runtime 分配
    material: 消息数组               # lm-service 定形式，纯透传
    tier:     "basic" | "advanced"  # 软倾向，可降级
    tools:    [ToolSpec] | None      # 可选，工具清单
    callbacks: {                     # 回调集（dict），发起前可改 cu.callbacks
        "on_ready": cb,              # 子 cu 就绪时（幂等装配钩子）
        "on_tool_call": cb,          # 有工具调用发生时（每轮一次、拿一组）
        "on_done": cb,               # cu 结束时
    }
    parent:   CogUnit | None         # 发起前可设，发起后冻结（不可换父）
    children: [CogUnit]              # 可增不可删（add_child / remove_child 抛异常）
)

cu.wait()       / cu.no_wait()       # 发起 → 入 cu 队列
cu.interrupt(reason)                 # 协作式取消：设标志，推进检查点读；no-op 若已 error
cu.add_child(child)                  # 运行中加子（on_ready 里用）
```

回调集说明：

| 回调 | 时机 | 用途 |
|---|---|---|
| `on_ready` | 子 cu 就绪时 | 幂等装配钩子：改 material + 加子/中断（签名见下）|
| `on_tool_call` | 有工具调用发生时 | 上层执行工具、返回结果（见 3.4）；可 interrupt |
| `on_done` | cu 结束时（成败都调） | 结果 + 完整 material 交上层，失败态带 category |

`on_ready` 签名与约束（装配钩子）：

```python
async def on_ready(cu: CogUnit, material: list) -> None:
    # 装配：原地改 material（append 已完成的子结果）
    # 干预：cu.add_child(...) / cu.interrupt(...)
```

- material **传引用原地改**，返回 None；上层保证增量装配不重复（自己知道哪些子新完成）。
- material 只经 on_ready 参数改；`cu.material` 其余时间只读（工具回填是 cu 内部 append，上层不碰）。
- runtime 不自动汇总子结果进父 material——子 done 由上层 on_done 收结果存起，父 ready 时在 on_ready 里装配。
- on_ready 返回后 runtime 重查一次依赖：有未完成子 → 退回 pending；无 → 入队。
- on_ready 是上层「发起后改 material」的唯一合法入口。

### 2.3 CuResult 三态

```python
@dataclass
class CuResultOk:          content: list           # 消息数组（type 化，对称输入 material）
@dataclass
class CuResultError:       category: str           # 六类 category
@dataclass
class CuResultInterrupted: reason: str | None = None

CuResult = CuResultOk | CuResultError | CuResultInterrupted
```

- 结果层用**值传递**：`LmServiceError` 在 lm-service 边界抛出，cu 捕获后转 `CuResultError(category)`；异常止于底层，不向上抛。
- `interrupt` = 失败中止，不覆盖已 error（no-op）；成功结果只能来自 LLM 语义产出。
- material（完整对话历史，过程留痕）不进 CuResult，是 `on_done(result, material)` 的独立参数——结果三态与过程留痕是两个正交维度。

### 2.4 假想调用（最小闭环两支路）

**支路 A：不调工具**（回一句话）

```python
async def reply(msg: str) -> None:
    async def on_done(result: CuResult, material: list) -> None:
        # material = 完整对话历史（过程留痕），默认不用，需要追溯时再看
        match result:
            case CuResultOk(content):
                phone.send(content)                    # 内容透传，上层消费/反写树
            case CuResultError(category):
                ...                                    # 上层决策：换策略/求助/放弃
            case CuResultInterrupted(reason):
                ...

    cu = rt.cu(material=[{"role": "user", "content": msg}], tier="basic",
               callbacks={"on_done": on_done})
    await cu.wait()
```

**支路 B：调工具**（查记忆再回话）

```python
async def recall_and_reply(msg: str) -> None:
    async def on_tool_call(cu, tool_calls: list) -> list:
        results = []
        for tc in tool_calls:                          # 业务自行决定串行/并发
            try:
                results.append(exec_tool(tc))
            except Exception:
                results.append(error_result(tc))       # 失败占位，保持位置对应
        return results                                 # 与输入等长等序

    async def on_done(result: CuResult, material: list) -> None:
        ...

    cu = rt.cu(material=[{"role": "user", "content": msg}], tier="basic",
               tools=[...],
               callbacks={"on_tool_call": on_tool_call, "on_done": on_done})
    await cu.wait()
```

要点：上层在支路 A/B 里只写回调，从不碰「入队 / 装配 / 提交 lm-service / 通知父」——那是 runtime 内部。

### 2.5 告知值默认注入

CogRuntime 默认自动在 material 注入窗口预算（工作预算/输出预算，checkpoint-7「告知值」）；默认值，上层可覆盖/置空。机制层给默认、上层有控制权。

## 三、运行过程（状态机 + 最小闭环）

### 3.1 状态机

```
created → pending(等子cu) → ready(装配) → queued(排队) → running(lm-service) → done
                                                          ↘ 有 tool_call → tooling(工具中) → 重查 ready → 再入队
```

`done` 含成功态与失败态，两者都结束。

### 3.2 调度与执行

1. **查 ready**：所有子 cu 是否完成。回调可动态改关系（加子 cu），每次入队前都重查，不做「恒真」假设。
2. **调度子 cu**：有子 cu 则调度，子完成后**通知父**（事件驱动，父不常驻轮询）。
3. **装配**：上层在 `on_ready` 里把已完成的子结果汇总进 material（runtime 不自动汇总，见 2.2 on_ready 签名）。装配是可选机制点，创建时装配还是 `on_ready` 时改由上层决定。
4. **入队**：调 lm-service 前排队，控制并发度 + 预留优先级口子。
5. **交 lm-service**：running 态调 `LmClient.chat`，完成即拿归一响应，可能成功或失败。
6. **工具续轮**：有 `tool_call` 走工具；无则 `done`。

### 3.3 支路 A（无工具）：一次 LLM 调用，自然结束

lm-service 返回无 `tool_call` → `done`。默认 cu 只有一次 LLM 调用，**不存在独立的"循环终止条件"**——无 tool_call 就结束。

### 3.4 支路 B（有工具）：工具续轮

- 有 `tool_call` 时，lm-service 归一返回 `tool_calls = [{id, name, args: dict}]`（含统一 id）；cu 把 `[{name, args}]`（剥 id）作为**一组**交给 `on_tool_call` 回调。
- **cu 完全不感知工具**：不知道工具有哪些、怎么执行、同步异步；只提供「把 tool_call 交给上层、收回结果」的机制。
- 上层自行决定串行/并发执行，执行完返回一组结果（**按位置对应**，失败返回占位结果）。
- cu 按消息格式把 `assistant(tool_calls)` 消息 + `role:tool` 消息（`tool_call_id` = lm-service 给的 id，按位置配回结果）append 进 material → **重查 ready**（关系可能已被回调改变）→ 再入队 → 新一轮 LLM 调用。
- **工具轮次上限归上层**：`on_tool_call` 里统计轮次，超限 `cu.interrupt()`。

### 3.5 推进循环（_advance）

- **一次 `_advance(cu)` = 一个短 task**（`asyncio.create_task`），推进到稳定点即结束；「短」= 不常驻（无 worker while 循环），非「不 await」（running 态 await LmClient 是挂起）。
- **五个触发源**：`wait/no_wait`、子完成通知、队列出队、`LmClient` 返回、`on_tool_call` 返回——每个触发一次 `_advance`。
- **稳定点四态**：`pending`（等子）/ `queued`（等窗口）/ `running`（await lm-service）/ `tooling`（await on_tool_call）。队列里**只有 queued 态**，其余靠事件/await 挂起。
- **interrupt 检查点**：统一在 `_advance` 入口一处——置位即转 `done(interrupted)` 跳过推进，五个触发源都覆盖。running 期间 interrupt 不打断当前调用（协作式），结果回来在入口发现并丢弃。
- **on_ready 后重查**：on_ready 返回后重查一次依赖，与 pending 等子完成后的重查是同一个「查 ready」步骤。

### 3.6 类结构与注册表

- **CogUnit = 纯数据 + 句柄**，不含推进逻辑；字段见 2.2，方法仅 `wait/no_wait/interrupt/add_child`。
- **CogRuntime = 主动引擎**，推进集中 `_advance`；持 cu 队列（`asyncio.Semaphore(N)`）+ `LmClient` + `_units` 注册表。
- **父子通知**：子 `_advance` done 分支先调 `on_done`、再 `asyncio.create_task(_advance(parent))`；父每次被喊全量遍历 children 查 done，最后一个子 done 时一查全 done → ready（与「重查 ready」统一，天然支持动态加子）。
- **cu 注册表 `_units: dict[id, CogUnit]`**：创建登记、done 移除；用途 shutdown（遍历未 done 统一 `interrupt("shutdown")`）+ 调试。id = 自增可读 `cu_1/cu_2`。

## 四、与 lm-service 衔接

衔接只有一处：**cu 在 running 态调 `LmClient.chat`**，其余传输/路由/错误分类/工具组装全被 LmClient 藏住。

### 4.1 归一响应与机制字段

```python
resp = await client.chat(messages=material, tier="basic", must=False, tools=tools)
# 成功 → {content, tool_calls, finish_reason, usage, reasoning, raw, routed}
# 失败 → 抛 LmServiceError(category, message)
```

cu 对归一结果**「机制字段读、内容字段透传」**。机制字段清单（4 个，封闭）：

| 字段 | 用途 |
|---|---|
| `finish_reason` | 判续轮（==`tool_calls` 走 tooling，否则 done） |
| `tool_calls` | 续轮数据（`[{id, name, args}]`），交 `on_tool_call` |
| `usage` | 速率反馈（资源控制） |
| `routed` | 降级留痕 |

其余：`content` 透传（进 `CuResultOk.content`）、`reasoning` 暂不用（无 thinking）、`raw` 调试用 cu 不读。

失败：cu 捕获 `LmServiceError`，读 `category` → `CuResultError(category)`，category 随失败态交上层。

### 4.2 工具调用内部化（cogos 定规范，lm-service 组装厂商格式）

cu / CogRuntime 不跟厂商接口走，内部定规范；**消息格式（messages 数组）是 lm-service 对外契约，cu 按契约操作**。lm-service 只负责与厂商格式互转：

| 环节 | 内部形式 | 职责 |
|---|---|---|
| 工具集输入 | 结构化 schema（JSON Schema 等价） | lm-service 组装厂商 `tools` 格式、补 strict 等外围字段 |
| tool_calls 输出 | `[{id, name, args: dict}]` | lm-service parse `arguments`（JSON 字符串→dict）+ 归一统一 id |
| 结果回填 | `[result]`（按位置对应） | cu 拼 `assistant(tool_calls)` + `role:tool` 消息 append 进 material |

- `content` 与 `tool_calls` 是**并列可选字段**，可同现/同无；判断续轮只看 `tool_calls`，不看 content；content 有值要保留（cu append assistant 消息时 content 自然带上）。
- 结果按**位置对应**回填：业务不见 id（cu 持 id 拼消息），顺序不能乱（乱了结果张冠李戴、不报错），失败返回占位结果。部分回填 / 并发乱序留目标态。

## 五、并发模型

- asyncio **短 task**，事件驱动，**非常驻**：一次 `_advance` 一个短 task（见 3.5）。短 task 的意义 = 隔离异步挂起，一个 cu 的 `await` 不阻塞别的 cu。
- **cu 队列 = `asyncio.Semaphore(N)`**：内部 FIFO 即队列、计数即并发窗口；`queued` = `await acquire()`，acquire 成功 = 出队进 running，done/再入队 release。第一版优先级不实现（缺场景，checkpoint-11），未来换优先队列接口不变。
- **两层并发分离**：
  - cu 队列（`Semaphore(N)`）= 逻辑调度，N = `max_concurrent`（构造参数，默认 4），卡在 lm-service 前。
  - lm-service = 物理限流闸门（服务端 `AccountScheduler`，semaphore+RPM，已实现不动）。
  - 两层叠加独立：agent 内先限 N，N 个 cu 同时打 lm-service，服务端再按 (provider, account) 限。

## 六、核心约束（平台规范）

1. **进程内零同步阻塞**：所有回调、工具执行必须返回 awaitable（async）；同步的由上层自行 `run_in_executor`。这是「假并发」成立的前提。
2. **计算密集任务另起进程**：不进 cogos 运行进程。
3. **cu 层不重试**：重试需「重试前信息有变化」，而变信息靠上层提供，cu 与 lm-service 都做不到。失败即 `CuResultError`，由上层决定。**无状态重试归 lm-service**（网络/限流，输入不变，安全）。
4. **失败态携带错误类别**：`CuResultError` 带 category（retryable/auth/quota/content/semantic/invalid_request），上层才有决策依据。
5. **短输出不流式**：输出短 → 流式无意义，非流式 + 单总超时（卡住触发总超时归可重试）。

## 七、最小版 vs 目标态（减法可追溯）

| 维度 | 目标态 | 最小版 |
|---|---|---|
| 优先级调度 | zfs zio 按 IO 类型，有场景 | 后置（缺场景，FIFO + 并发窗口） |
| defer | 纯暂停机制（delay 自动唤醒） | 后置（缺真实场景，同优先级；阶段三资源控制再引入）|
| 工具 | 三类（工作簿/记忆/世界交互） | 机制走通即可，具体工具清单随子系统 |
| 工具内部 id / 部分回填 | 支持并发乱序、跳过失败 | 后置（位置对应） |
| 电脑工具 | 读写文件/执行命令 | 后置（阶段一 A 档够跑通） |
| 流式 | 长输出传输优化 | 不做（短输出） |
| logprobs 熵 | 元层流畅性信号 | 后置（lm-service 也只留标志位） |
| 多 key/多账号 | 负载均衡/切换 | 后置（lm-service 内部） |
| 事件流 / 诊断出口 | 每阶段都有 | 后置，随阶段三 |

## 八、遗留 / 待定

- done 回调 vs 通知父的精确顺序：**暂定先 done 后父**（让父被唤醒时子副作用已落定），无场景不改。
- 工具集内部 schema 的最终形态（是否 pydantic model 直出 JSON Schema）：待 lm-service 实现时定，原则已定（结构化 schema、不简化成自然语言）。
- lm-service 侧遗留（工位 B ISSUES，task-3 已开工）：internal_key 自带 base_url、tool call 内部化组装、输出 content 归一 `content[]`。
