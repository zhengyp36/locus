# CogRuntime 运行过程与 cu 生命周期（设计）

> 状态：讨论稿（活文档，`../checkpoint/`）。确定后归档 `cogos/docs/`。来源：checkpoint-11/12/13 + 本轮 cu 生命周期讨论。

## 一、cu 的定位

cu = **一次 LLM 语义加工的封装**。哪里有语义哪里就有 cu，故 cu 横跨三层（认知/元/执行），不绑认知层。但 cu **只加工语义，不决策、不发起**——决策是 agent 整系统（元层）的事，工具调用是 agent 的对外行为，cu 只是链上的语义环节。

## 二、创建与发起

- **创建**：输入 `material`（消息数组，纯透传）+ 参数配置（tier 等）。material 在创建时可能已装配好。
- **发起**：`cu.wait()`（同步等结束）/ `cu.no_wait()`（异步不等待）。父子关系发起前可设、发起后冻结。

## 三、状态机

```
created → pending(等子cu) → ready(装配) → queued(排队) → running(lm-service) → done
                                                          ↘ 有 tool_call → tooling(工具中) → 重查 ready → 再入队
```

`done` 含成功态与失败态，两者都结束。

## 四、调度与执行（zio 流水线映射）

1. **查 ready**：所有子 cu 是否完成。因为回调可动态改关系（加子 cu），每次入队前都要重查，不做"恒真"假设。
2. **调度子 cu**：有子 cu 则调度，子完成后**通知父**（事件驱动，父不常驻轮询）。
3. **装配**：父 cu 把子结果汇总进 material。装配是可选机制点，调用方决定在创建时装配还是 `on_ready` 时改装配。
4. **入队**：在调 lm-service 前排队，控制并发度 + 预留优先级口子。
5. **交 lm-service**（`io_start`）：lm-service 完成即 `io_done`，可能成功或失败。
6. **工具续轮**：lm-service 返回后，若有 `tool_call`，走工具；无则 `done`。

## 五、工具调用机制（cu 不感知工具）

- 默认 cu 只有**一次** LLM 调用。工具调用是后置能力，**有 tool_call 才多轮，无则自然结束**——不存在独立的"循环终止条件"。
- **判据**：`finish_reason == "tool_calls"`（结果里 `tool_calls` 非空）。`content` 与 `tool_calls` 是**并列可选字段**，两者可同现；判续轮只看 tool_calls，content 有值则保留进 material（工具续轮回填时整体带回）。
- cu 内有一个机制函数，把 LLM 返回的 tool_call 信息（调什么、参数）交给**上层提供的工具执行函数**，由它完成调用。
- **cu 完全不感知工具**：不知道工具有哪些、怎么执行、同步异步。cu 只提供"把 tool_call 交给上层函数"这个机制，工具执行函数由调用方注入。
- **回填归属**：工具执行函数只返回**结果内容**，cu 负责**协议回填**——把 assistant 的 tool_calls 消息 + `role:tool` 结果消息 append 进 material（回填格式是 lm-service 定的，cu 只机械 append，不碰语义）。
- **内部化/统一化**：CogRuntime/lm-service 定义内部规范，不跟厂商接口走；lm-service 负责组装成厂商格式。
  - 工具集（进请求）：内部用**结构化 schema**（JSON Schema 等价），不自然语言简化；lm-service 补厂商外围字段（strict 等）。
  - tool_calls 输出：内部形式 `[{name, args: dict}]`（arguments 已 parse）。
  - 回填结果：内部形式 `[{name, result}]`，`tool_call_id` 藏进 lm-service。
- **工具轮次上限归上层**：cu 不设轮次上限；上层在 `on_tool_done` 回调里统计轮次、超限即 end。
- 工具执行结束后回填结果 → **重查 ready**（关系可能已被回调改变）→ 再入队 → 新一轮 LLM 调用。

## 六、回调点

| 回调 | 时机 | 用途 |
|---|---|---|
| `on_ready` | 子 cu 就绪时 | 装配子结果 + 用户干预口 |
| `on_tool_done` | 工具调用结束时 | 用户可改状态、提前结束、加子 cu |
| `on_done` | cu 结束时（成败都调） | 结果交上层消费；失败态携带错误类别 |

## 七、并发模型

- asyncio **短 task**，事件驱动，**非常驻**：每个推进阶段一个短 task（入队→提交→处理→销毁），子完成通过回调通知父，父重新入队。
- 短 task 的意义：隔离**异步挂起**——一个 cu 的 `await` 不阻塞别的 cu，各自独立推进 stage。
- 独立推进不是绝对的：调 lm-service 前必须**排队**（并发窗口），这是为优先级留的口子。
- **两层并发分离**：cu 队列 = 逻辑调度（可做优先级）；lm-service = 物理限流（无脑闸门，超厂商数才排队）。

## 八、核心约束（平台规范）

1. **进程内零同步阻塞**：所有回调、工具执行函数必须返回 awaitable（async）；同步的由上层自行包 `run_in_executor`。这是"假并发"成立的前提。
2. **计算密集任务另起进程**：不进 cogos 运行进程。
3. **cu 层不重试**：cu 重试需"重试前信息有变化"，而变信息靠上层提供，cu 与 lm-service 都做不到，故无意义。失败即 `done(失败态)`，由上层决定（换策略/求助/放弃）。**无状态重试**归 lm-service（网络/限流，输入不变，安全）。
4. **失败态携带错误类别**：`done` 的失败结果须带 error category（retryable/auth/quota/content/semantic），上层才有决策依据。
