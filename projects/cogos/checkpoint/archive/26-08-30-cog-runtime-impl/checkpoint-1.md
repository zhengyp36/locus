# checkpoint-1 — design-cog-runtime-min.md 审核记录

> 会话：审核 `design-cog-runtime-min.md`（v1 讨论稿）。YZ 提意见 → 我审 → 记结论。审核结束后统一改写文档。

## 意见 1（YZ）：cu 缩写未说明

**YZ 意见**：cu 是 cog-unit 的缩写，设计文档没有明确说明，开发时会不会知道这个缩写？是否应该说明？

**审核结论**：采纳。

**理由**：

1. min 文档全程用 `cu`（1.1 标题「cu 的定位」、正文、表格、假想代码注释），从头到尾没出现全称，也没有 "cu = ..." 的搭桥。读者只能靠上下文猜，文档不自治。
2. 正式术语其实是 **CogUnit**（不是连字符小写 "cog-unit"）：`cogos-concept-system.md:19`（"CogUnit / CogFunc / CogExecutor"）、`cogos-plan.md:28`（"CogUnit = 一次语义运算"）、`cogos-design-theory-summary.md:25`（"CogUnit = 推理请求的惰性描述"）。`cu` 是 checkpoint-7 讨论中自然冒出的简写，只散在 checkpoint 系列里，从未固化进任何正式文档。
3. min 文档定位是「定稿后基于它开发」，应自包含，不能默认读者先读过 checkpoint 系列才看得懂。

**处理**：在 1.1 节开头加一句 `cu = CogUnit`（一次 LLM 语义加工的封装）；同时声明全文约定——代码/类名用 `CogUnit`，叙述性简写用 `cu`，两写法同指。随审核结束后统一改写。

## 意见 2（YZ）：taskq 改名

**YZ 意见**：taskq 名不副实——队列里装的是 cu 不是 task；`taskq` 从 zio 借来，zio task=IO 操作 ≠ cu 语义加工。改名为 cu 队列。另：状态机问题不大（3.1 已有状态清单，不用改）。

**审核结论**：采纳。

**理由**：

1. 队列装的是「待下发 lm-service 的 cu」，不是 task；`taskq` 是 zio 类比名，名实不符，借名误导。
2. 名字还隐含「独立组件」，而 checkpoint-11 已定「执行散在三处、无独立执行器」，队列是实现细节，不当设计主角。

**处理**：全文 `taskq` 改为「cu 队列」，实现命名用 `cu_queue`；状态机（3.1）保留不动。

## 意见 3（YZ）：CogRuntime 收 internal_key（不感知 LmClient）+ internal_key 自带 base_url

**YZ 意见**：

1. 上层用 CogRuntime 不必感知 lm-service，只需 internal_key。
2. LmClient 的 base_url 不该有，internal_key 自带 base_url。

**审核结论**：采纳。

**事实确认**（工位 B 已完工）：`LmClient` 是类（`cogos/lm_service/client.py:29`），`LmClient(internal_key, base_url=None)` 构造对象；`chat(messages, *, temperature, max_tokens, top_p, thinking, tier, must, trace_id)` 返回归一 JSON，失败抛 `LmServiceError(category, message)`。

**理由**：

1. 分层：收 LmClient 对象 → 上层被迫 `from cogos.lm_service import LmClient` + `new`，lm-service 泄漏进上层；收 internal_key → 上层只拿句柄，底层藏进 CogRuntime。
2. 依赖方向：收对象使「上层 → lm-service」绕过 cog-runtime；收 internal_key 才是「上层 → cog-runtime → lm-service」。
3. 与 lm-service min 文档 2.2「上层只持 key 字符串，不感知绑定」一致。
4. 测试 mock 不是障碍：internal_key 自带 base_url 后，塞指向 fake 服务的 key 即可，无需 fake LmClient 类。

**处理**：

- cog-runtime 文档写 `CogRuntime(internal_key="ik_xxx")`，上层只给一个句柄。
- `internal_key` 自带 base_url 是 lm-service 侧改动 → 记工位 B `ISSUES.md`，CogRuntime 开工前先补（软前置，非硬阻塞）。

## 意见 4（YZ）：回调机制收敛——回调集 + interrupt + CuResult 三态

**YZ 意见**（多轮收敛）：

1. CogRuntime 不该统一 tool_executor——不是所有 cu 有 tool，不同 cu 工具集不同，工具归 cu 级。
2. 回调做成一个集（dict），cu 修改这个集。
3. 提前结束用 `cu.interrupt(reason)`，简单；interrupt = 失败中止；不覆盖已出错；reason 带细节。
4. CuResult 用三种类型（tagged union），content 用消息数组（对称输入）。

**审核结论**：采纳。

**收敛过程要点**：

- `on_tool_done` 改名 `on_tool_call`（覆盖「一次工具调用发生、请上层处理」整个时相，非仅「结束」）。
- 工具执行 = `on_tool_call` 回调，不设独立 tool_executor；工具集 `tools` 是 cu 构造参数。
- 结束 cu 的能力对称给所有干预回调（on_ready / on_tool_call 都能 interrupt），on_done 是结果出口不能。
- 「成功提前结束」不存在：成功结果只能来自 LLM 语义产出；工具成功但选择中止的善后，由上层在自己的上下文中自理（上层持 cu 上下文）。
- interrupt 设置标志、CogRuntime 在推进检查点读；已 error 则 no-op（不抹 lm 真实错误类别）；最小版只在回调里调，资源控制取消走 defer 线。

**结论**：

```python
CogRuntime(internal_key="ik_xxx")       # 只留一个参数，去 tool_executor

cu = rt.cu(
    material=[...], tier="cheap",
    tools=[...],                          # 可选，工具清单
    callbacks={"on_ready": ..., "on_tool_call": ..., "on_done": ...},
)

cu.interrupt(reason)                      # 失败中止；no-op 若已 error

@dataclass
class CuResultOk:        content: list    # 消息数组（type 化）
@dataclass
class CuResultError:     category: str    # 六类 category
@dataclass
class CuResultInterrupted: reason: str | None = None

CuResult = CuResultOk | CuResultError | CuResultInterrupted
```

- `LmServiceError` 在 lm-service 边界抛出，cu 捕获转 `CuResultError(category)`；异常止底层，结果层用值传递。
- content = 消息数组（对称输入 material），归一归 lm-service 本职。

**处理**：

- design-cog-runtime-min.md 改写时应用。
- lm-service 遗留新增两条：tool call 透传 + 输出 content 归一 `content[]`（记工位 B ISSUES）。

## 附：LLM 能力面（静态知识）

审核「content 为什么是 str」时引出 LLM 服务除 chat completion 外的调用形态，独立记 `llm-capabilities.md`（静态知识，非设计结论）。要点：cu 只绑 chat completion（含 tool call）；embeddings 归记忆（不走 cu）；图像/音频是模态扩展（消息数组兼容）。

## 意见 5（YZ）：tool call 内部化统一 + 工具轮次上限归上层

**YZ 意见**：

1. 工具轮次上限由上层自己做——工具调用本就是上层在调用，`on_tool_call` 回调可统计轮次、决定结束。
2. 其余内部化/统一化：CogRuntime / lm-service 定义内部规范，不跟厂商接口走；lm-service 负责组装厂商格式。
3. 工具集协议复杂，但代码不是 YZ 写，不简化问题不大（用结构化 schema）。

**审核结论**：采纳。

**支撑（DeepSeek tool call 用法，静态知识）**：

- 三步：`tools` 参数进上下文（JSON Schema 数组 + `tool_choice` auto/none/指定函数）→ 提取 `finish_reason=="tool_calls"` + `message.tool_calls` 数组（`arguments` 是 JSON 字符串，要 parse）→ 回填 assistant(tool_calls) 消息 + `role:tool` 结果，再发下一轮。
- `content` 与 `tool_calls` 是**并列可选字段**，可同现/同无；判断续轮只看 `tool_calls`，不看 content；content 有值要保留（回填时整体 append assistant 消息，content 自然带上）。
- `reasoning_content`（thinking 模式）暂不考虑——cogos 不用 thinking 模式，故归一契约暂不含此字段。

**结论**：

- 内部化三块分开落：tool_calls 输出 → `[{name, args: dict}]`（lm-service 负责 parse arguments）；回填 → `[{name, result}]`（lm-service 补 tool_call_id、拼 role:tool、对齐 assistant 消息）；工具集 → 结构化 schema（JSON Schema 等价，lm-service 只补 strict 等外围字段，不简化成自然语言）。
- 工具轮次上限归上层：`on_tool_call` 里统计轮次，超限 `cu.interrupt()`；不新增「调用前」回调。
- 回填归属：`on_tool_call` 只返回结果内容，cu 负责协议回填（append 进 material）——与意见 4「on_tool_call 覆盖整个工具调用时相」一致。
- 归一响应契约补 `tool_calls`：`{content?, tool_calls?, finish_reason, usage, ...}`，content/tool_calls 独立判空。

**处理**：

- design-cog-runtime-min.md 改写时应用（内部化契约进「四、与 lm-service 衔接」）。
- lm-service 遗留追加：工具集 / tool_calls / 回填的内部化组装（记工位 B ISSUES，与意见 4「tool call 透传」合并）。

**遗留收敛（多 tool_call 语义）**：`on_tool_call` 每轮一次、拿一组 `[...]`、返回一组；业务自行决定串行/并发（cu 不管）；结果按**位置对应**回填——内部无厂商 id，顺序不能乱（乱了结果张冠李戴、不报错），失败返回占位结果；内部 id + 部分回填留目标态。

## 意见 6（审核收尾）：机制字段清单收敛 + done 顺序确认

**结果侧机制字段最终清单（4 个，封闭）**：

| 字段 | 用途 |
|---|---|
| `finish_reason` | 判续轮（==`tool_calls` 走 tooling，否则 done） |
| `tool_calls` | 续轮数据，交 `on_tool_call` |
| `usage` | 速率反馈（资源控制） |
| `routed` | 降级留痕 |

- `content` 透传（进 `CuResultOk.content`）、`reasoning` 暂不用（无 thinking）、`raw` 调试用 cu 不读。
- 旧表述「读 status 判成败」作废——成败靠 `LmServiceError` 异常 + CuResult 三态（意见 4）。

**done 顺序**：保持 checkpoint-11 暂定「先 done 后父」，无场景不改。

**处理**：min 文档改写时应用（「四、与 lm-service 衔接」里「读 status」改为机制字段清单 + CuResult 三态映射）。

## 意见 7（YZ）：工具消息组装归 cu + on_done 透传 material

**YZ 意见**：

1. 工具消息组装不是问题——消息格式是 lm-service 定的（对外契约），cu 知道怎么填，按格式 append 即可。
2. `on_done` 加一个 material 参数，把中间过程完整透传；无实质用处、暂时没想好用途，只是放在那里；失败/中断都可能有中间过程。

**审核结论**：采纳。

**收敛要点**：

- **工具消息组装归属修正（改意见 5）**：cu 按消息格式 append `assistant(tool_calls)` + `role:tool` 消息进 material；lm-service 只做厂商格式转换（工具集 schema、arguments parse、错误分类），**不补 id、不维护对话**。`tool_calls` 归一输出带统一 id：`[{id, name, args: dict}]`。之前意见 5「lm-service 补 tool_call_id、拼 role:tool」作废——那是把消息格式（对外契约）误当厂商格式藏了。
- **中间 content**：保留进 material（cu append assistant 消息自然带上，必须，否则断上下文），**不单独返回**；`CuResultOk.content` 只 = done 轮（`finish_reason != tool_calls`）的 content。`on_tool_call` 最小版只传 `tool_calls`，不传 content。
- **on_done 签名**：`on_done(result: CuResult, material: list)`。material = done 时完整消息历史（输入 + 中间轮 + 最终轮），**独立于 CuResult 三态**（过程留痕 vs 结果三态，两个正交维度）；Ok/Error/Interrupted 三态都透传。Ok 时 material 末轮 content == result.content；Error/Interrupted 时 material 是「到失败为止」的历史，诊断价值更高。

**处理**：min 文档改写（2.2 回调签名、2.3 CuResult 不变、2.4 支路 on_done 签名、3.4 续轮 cu 拼消息、4.1/4.2 tool_calls 归一带 id + 回填归 cu）。

## 待审意见池（未处理）

（暂无）——意见 1~7 全部收敛，待统一改写 `design-cog-runtime-min.md`。
