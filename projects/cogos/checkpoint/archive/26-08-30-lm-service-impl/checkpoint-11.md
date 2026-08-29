# checkpoint-11 — thinking 默认关闭（YZ 拍板）

## 当前问题

真实验证暴露：deepseek thinking 默认开启，reasoning 吃掉 max_tokens 致 content 空 + finish_reason=length。引发更本质讨论：lm-service 要不要用厂商 thinking？

## 关键决策（YZ 拍板）

- **默认关闭厂商 thinking，cogos 内部暂不开启、不使用该模式，仅保留参数用于效果对比。**
- 理由：agent 的思考行为由 cogos 上层架构承担（多轮/工具/认知树/元控制），厂商 thinking 是黑盒 CoT，与「可观测/可控制/可自长/可审计」的认知设计冲突，且两层思考叠加浪费 token/延迟。
- `thinking` 参数保留在契约里（不删），`reasoning` 归一字段默认恒 null，仅显式开 thinking 对比时才有值。

## 已做修改

- `cogos/lm_service/providers/deepseek.py`：`thinking.get("enabled", True)` → `thinking.get("enabled", False)`（默认关）。openai.py 本默认不发 reasoning_effort，无需改。
- `tests/lm_service/test_normalization.py`：新增 `TestThinkingDefault` 4 用例（deepseek 默认 disabled+temperature / 显式 enabled 无 temperature；openai 默认无 reasoning_effort / 显式 enabled=high）。
- `docs/design-lm-service-min.md`：2.3 `thinking` 字段说明（默认关、仅对比）+ 3.3 reasoning 归一语义（默认恒 null）。

## 验证

- `tests/lm_service/` 51 passed；全量 pytest 719 passed 无回归。

## 遗留

- 未 commit（连同 checkpoint-10 的 tier 改名 + 轮 10 测试一起待 YZ 裁决）。
- reasoning_effort 粒度（low/high/max）暂不暴露，后续真要用厂商 thinking 对比时再议。
