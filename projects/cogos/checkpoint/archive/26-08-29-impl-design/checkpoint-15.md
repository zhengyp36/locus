# checkpoint-15 — DeepSeek 错误码 + 已知 bug/异常 查证

## 当前问题

错误清单系统梳理（checkpoint-14 遗留）第一步：查证 DeepSeek 官方文档记载的错误码与已知异常行为，作为「厂商差异 + 已知 bug」归类规则的输入。

## 查证来源（官方文档，2026-08 现行）

- 错误码：`https://api-docs.deepseek.com/quick_start/error_codes`
- Chat Completions 参考：`https://api-docs.deepseek.com/api/create-chat-completion/`
- 视觉指南：`https://api-docs.deepseek.com/guides/vision`
- Change Log：`https://api-docs.deepseek.com/updates`

## 官方错误码（7 类）

| 状态码 | 含义 | 建议 category（草案） |
|---|---|---|
| 400 Invalid Format | 请求体格式错 | semantic（调用方错误，非内容违规） |
| 401 Authentication Fails | API key 错 | auth |
| 402 Insufficient Balance | 余额不足 | quota |
| 422 Invalid Parameters | 参数无效 | semantic（同上，待定） |
| 429 Rate Limit Reached | 请求过快 | retryable |
| 500 Server Error | 服务端异常 | retryable |
| 503 Server Overloaded | 过载 | retryable |

注意：DeepSeek 的 400/422 是「格式/参数错」而非「policy 内容违规」。design-lm-service-min.md 3.3 现规则「400 含 policy→content、其余→semantic」需核对：DeepSeek 无显式 policy 状态码，内容违规走 `finish_reason=content_filter`（见下），不走 400。→ 归类规则待下一步「错误清单」统一，此处只记事实。

## 已知 bug / 异常行为（文档明确记载）

1. **JSON mode 无限空白流**（create-chat-completion 参考 + json_mode 指南）：「不提示模型输出 JSON 就开 `response_format:{type:"json_object"}`，模型可能生成不终止的空白流直到 token 上限，表现为长时间卡住的请求」。→ 卡死/超时类，靠 120s 单总超时兜底，归 retryable；但提示「上层开 json mode 必须自带 JSON 指令」。
2. **`finish_reason` 新增 `insufficient_system_resource`**：推理系统资源不足导致请求中断（200 响应内的非正常结束态）。→ 等价服务端资源不足，可重试，归 retryable。
3. **`finish_reason=content_filter`**：内容被过滤、content 被省略。→ 归 content（上层改 prompt/换措辞）。
4. **`finish_reason=length`**：content 可能被截断（超 max_tokens 或超上下文）。→ 非错误，是正常信号，记录留痕。
5. **`content` 为 `string nullable`**：可为 null（非仅空串）。蓝本 `msg.get("content") or ""` 已兜底 None，但需在归一层显式声明该约定。
6. **`reasoning_content` 为 nullable**：仅 thinking mode 返回，非 thinking 模式 null/缺失。→ 归一 `reasoning` 置 null 的既有约定成立。
7. **视觉参数限制**（vision 指南 Restrictions）：
   - 图只能放 `user` 消息，`system`/`assistant` 带图 → 400。
   - 非视觉模型收图 → 400（"This model does not support image"）。
   - 用户文本含保留图片占位 token → 400。
   - → 这些是「调用方传错」，理想在上层装配就避免；漏到 lm-service 时归 semantic/content（待定）。
8. **视觉格式**：仅 JPEG/PNG/GIF/WebP，按文件内容判格式（非扩展名/MIME）；inline base64 计入 48 MiB body 上限，单图 base64/URL ≤32 MiB。

## Change Log 揭示的历史 bug（曾存在，已修）

- 2025-09-22 V3.1-Terminus：修复用户报告的「中英混排、偶发异常字符」（`occasional abnormal characters`）——与「空行/异常」印象吻合的最近线索。
- 2024-05-17：JSON 输出解析率 78%→85%（历史 JSON 输出不稳定）。

## 与「空行」的关系

现行非流式文档已无「空行」表述；流式 SSE 天然含 keep-alive 空行（`data: [DONE]` 前）。最小版非流式（stream:False）不涉及 SSE 空行，但「响应体不符合协议（空/非 JSON）」的防御性解析仍必须做（见上轮思路），与 bug 是否仍在无关。

## 遗留 / 下一步

- 错误清单表（错误来源 × category × 最小版处理 × 目标态处理）待 /undo 后继续梳理，把本查证结论并进去。
- category 映射草案中 400/422 归 semantic 还是 content、视觉参数错误归类，两项待 YZ 定。
