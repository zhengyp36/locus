# CogUnit thinking 模式 + DeepSeek thinking 行为验证

> 2026-09-02。CogUnit 加 think 模式（对比用），真实验证 DeepSeek thinking 的回传行为。代码已推 origin/master（cogos）。

## 功能改动

- `CogUnit` / `CogRuntime.cu()` 加 `thinking` 参数：dict 透传（与 `LmClient.chat` 契约一致），默认 `None` = 厂商 disabled。目的保留 openai `budget_tokens` 对比粒度。
- 工具续轮回传：`_advance` tooling 分支 append assistant 消息时带内部 `reasoning` 字段（取自 `resp["reasoning"]`，`parse_response` 已把 deepseek `reasoning_content` 归一）。
- 结果带出：`CuResultOk` 加 `reasoning` 字段（默认 None），对比产出用。
- vendor 转换：`_vendor_assistant_tool_message` 把内部 `reasoning` → `reasoning_content`（仅 deepseek 触发，openai 恒 None 天然不输出，无需 provider 感知）。

改动文件：`cog_runtime/{unit,runtime,types}.py` + `lm_service/providers/base.py`；测试 +6（thinking 透传/默认、续轮 reasoning 回传、result 带 reasoning、转换层 2 例）。全量 862 passed 无回归。

## DeepSeek thinking 行为（真实验证）

矩阵（flash + pro 一致）：

| 场景 | 结果 |
|------|------|
| 漏传 reasoning_content | 200 正常作答 |
| 截断 reasoning_content（传一半） | 200 正常作答 |
| 完整回传 | 200 正常作答 |
| 无 tools 不回传 | 200 正常作答 |

结论：
- DeepSeek **不校验** `reasoning_content` 回传——官方「带 tools 请求不回传会 400」是威慑性描述，实测漏传/截断都不报错。
- 回传 `reasoning_content` 的真实作用是**质量导向**：让模型延续上一轮思考上下文，非硬约束。
- 官方另一处「thinking 默认 enabled」与 provider 现状（默认 disabled）不符；cogos 维持默认 disabled（YZ 拍板，仅留参数对比）。

## 遗留

- `assemble_tool_messages` 只对「带 tool_calls 的 assistant」做 `reasoning`→`reasoning_content` 映射；plain assistant（无 tool_calls）原样透传。单 cu 内自洽，跨 cu 多轮续聊时该轮思考不会转成 vendor 字段。实测 deepseek 不校验、不 400，仅影响思考延续质量，暂不改，等跨轮续聊再处理。
- 真实验证脚本：`/tmp/kilo/think_test*.py`、`think_provider.py`（临时，未入仓）。
