# checkpoint-8 — LLM-Service 窗口与 token 估算

## 当前问题

lm-service 如何对待上下文窗口（限制 vs 提供参数）与 token 计数（估算手段）。

## 关键结论（YZ 拍板）

### 窗口：提供参数 + 校验，不限制

- lm-service **不「限制」窗口大小，只「提供参数」**，由上层业务设置；lm-service 做的是**校验**——判断参数是否超厂商上下文上限（如池子里最小厂商上限 100K，则窗口 ≤ 100K）。
- **厂商上下文上限进能力表**（capability 字段之一，与 modality/tier 并列，checkpoint-5）。
- **物理窗口建议固定 64K**：几乎全厂商支持、小窗口绰绰有余，上层不用跟着厂商变。具体值待调。
- 三个窗口量（从大到小）：厂商上限（能力表）≥ 物理窗口（64K，请求参数）> 工作预算/告知值（LLM 感知可用空间，16K 量级，进 prompt）——后者属语义层，非 lm-service（见 checkpoint-7）。

### token 估算：count_tokens 接口，tiktoken

- lm-service 提供 `count_tokens(messages) -> int` 接口，**用 tiktoken 估算**（YZ 拍板）。
- 抽象进 `ProviderBase`，各 provider 实现（OpenAI tiktoken 精确 / DeepSeek tiktoken 近似 / 其他字符估算兜底），差异关进适配器。
- **无跨厂商精确解**：tokenizer 厂商私有，精确计数追不上；正确姿势 = 近似 + 余量。

### 估算定位：天花板粗校验

- lm-service 只需**粗校验防超厂商上限**，近似 + 余量足够（64K 比 100K 低 36%，远大于近似误差）。
- **精确 token 计数（工作预算管理）归上层**，非 lm-service 的活；上层靠「装得少」不靠「数得准」。
- 输出侧：`max_tokens` 是物理兜底（截断），非「约束」；「主动控制输出」靠上层告知值进 prompt（checkpoint-7「告知值<物理值」）。

## 遗留 / 待调

- 物理窗口值（64K）、工作预算值（16K）、输出预算值（4K）/ 物理值（6K）及比例，均待调。
