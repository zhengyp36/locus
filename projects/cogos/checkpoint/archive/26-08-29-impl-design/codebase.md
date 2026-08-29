# codebase

> 对代码的当前认知，就地改：认知变了就修正、去掉过时结论、不重复。锚点作行内引用，不单独列。

## lm_service（agent-study 现成代码，cogos LLM-Service 的整理蓝本）

- `lm_service/scheduler.py:16-93` — `AccountScheduler` 只做 `asyncio.Semaphore` + RPM 本地 sleep，是**软约束**（客户端自我限速），非硬限流；`Scheduler` 按 `(provider, account)` 维度池化账号调度器（`scheduler.py:97-108`）。
- `lm_service/providers/base.py:1-6` — `ProviderError` 只有 `status_code/message/raw`，**缺错误类别字段**（retryable/auth/quota/content/semantic），是错误归一落地前要补的点。
- `lm_service/providers/openai.py:11-56` — 已有字段映射（internal body → OpenAI req）与错误归一雏形（`ProviderError`），但**无重试、无降级、无超时重试**。
- `lm_service/handler.py:6-65` — 已做请求字段白名单 + internal key 鉴权（`resolve_internal_key`，key 对内部调用方隔离）；usage 只透传**未记账**（无用量计量/成本归因）。
- `lm_service/config.py:177-196` + `handler.py:9-16` — internal_key 机制**真实目的 = 隐藏厂商 api_key + 用量管控，非鉴权**；`add_internal_key` 的 secrets 签发、`delete_internal_key` 的 revoke、`_validate_internal_key` 鉴权都是 http 方案错位产物，整理进 cogos 时简化。
- model 抽象（`cogos/docs/vision-system-design.md:7-14`，YZ 已认可，蓝本无此）：**两正交维度 tier（cheap/expensive 强度轴） × modality（布尔开关，能力有无，自动推断路由）**。internal key 授权的是**集合**（tier 集合 + modality 开关），非蓝本的"一对一硬绑单 model"；model 是请求可选覆盖字段，只在授权集合内选。调用方不暴露厂商 model，响应含 `routed`（实际档位+模态+成本）。加模态不动外层结构：`messages[]→{role, content[]}`，content item 加 `type` 标签；MediaRef `{base64|url|file}`，阶段 1 实际 base64 内联。
