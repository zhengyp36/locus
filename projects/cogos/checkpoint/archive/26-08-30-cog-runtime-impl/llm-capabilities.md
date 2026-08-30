# llm-capabilities — LLM 服务调用形态（静态知识）

> 状态：静态知识，非设计结论。来源：审核 `design-cog-runtime-min.md` 时讨论「CuResult.content 为什么是 str」引出。
> 用途：理清 lm-service 未来能力面，以及它与 cu 绑定的边界。

## 一、三类形态

### 1. chat completion 变体（同一条主线 = cu 的语义加工）

| 形态 | 干什么 | 状态 |
|---|---|---|
| chat completion | 语义生成：messages → text | 已做（lm-service 主形态） |
| tool call | 语义生成 + 工具意图：messages+tools → tool_calls | 要补（意见 4 遗留） |
| 流式 chat | 同上但 token 增量返回 | 后置（短输出不流式） |
| reasoning | 思考链：附 reasoning_content | 已做（归一进 reasoning 字段） |

### 2. 其他「语义计算」形态（不是生成，是另一类能力）

| 形态 | 干什么 | cogos 位置 | 状态 |
|---|---|---|---|
| embeddings | 语义编码：text → vector | 记忆的语义召回，不走 cu | 后置（阶段二） |
| logprobs | 返回 token 概率 | 元层熵信号（流畅性） | 后置（留标志位） |

### 3. 模态扩展（跟随 LLM 生成/理解模态）

| 形态 | 干什么 | 状态 |
|---|---|---|
| 视觉输入 | 读图：content[] 含 image | 已做（模态路由） |
| 图像生成 | text → image | 后置（checkpoint-13「画图」） |
| 音频 TTS / STT | text ↔ audio | 后置（感知子系统） |

## 二、关键区分

- **cu 的语义加工 = chat completion（+ tool call 扩展）**。这就是 cu 的底层实现，所以一直说「一次 LLM 调用」。
- **embeddings 是「编码」不是「生成」**——不产语义内容，产向量表征，归记忆子系统（语义召回），不走 cu、不产 CuResult。虽也是 lm-service 未来该接的能力，但不进 cog-runtime 的 cu 状态机。
- **图像生成 / 音频是「生成模态扩展」**——checkpoint-13 已定「介质跟随 LLM 生成模态」，未来 content 数组加 `image` 等 type 时，CuResult 的消息数组形态（意见 4）直接兼容，cu 结构不用改。

## 三、与 lm-service / cog-runtime 的关系

- lm-service 未来完整能力面 = chat completion + tool call + embeddings + logprobs + 多模态。
- cog-runtime 的 cu 只绑定 chat completion（含 tool call）这一条；其余是并列能力，挂到别的子系统（记忆 / 元层 / 感知）去。
