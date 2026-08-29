# status — lm-service 实施（task-1，工位 B）

## 当前目标

实现 lm-service 最小版，`cu → lm-service` 一次调用跑通。规格 `cogos/docs/design-lm-service-min.md`，任务 `locus/projects/cogos/tasks/task-1-lm-service.md`。

## 状态

**轮 10/10 完成，mock 全绿 + 真实验证全绿（YZ 已提供真实 deepseek key）。**

- mock：`tests/lm_service/` 51 passed；全量 pytest 719 passed 无回归。
- tier 改名 basic/advanced（YZ 拍板），视觉模型归 basic 档。
- thinking 默认关闭（YZ 拍板，checkpoint-11）：cogos 内部不用厂商 thinking，仅保留参数对比。
- 真实验证：文本 basic/advanced 归一字段集完整；厂商 401→auth；视觉 jpg + vision-exp + LLM-as-judge equivalent=true。
- 详细：`checkpoint-10.md`（轮10+真实）、`checkpoint-11.md`（thinking 决策）；代码认知见 `codebase.md`。

## 待 YZ 裁决

- 是否 commit（tier 改名 + 轮 10 测试 + 文档）。真实 key 验证已完成，无需再 mock 停下。
- 视觉验证的 judge 判据已通过；是否需要补 openai 真实调用（现仅 deepseek，openai 需 YZ 另供 key）。

## 轮次清单（task-1 表，10/10 完成）

1. ✅ 包骨架 + config.py 改 + base.py category
2. ✅ admin.py 简化
3. ✅ 主链路 router + handler + scheduler
4. ✅ providers 归一 + 防御解析 + category + finish_reason
5. ✅ 调试 jsonl + admin calls
6. ✅ LmClient（client.py）
7. ✅ lm_call CLI 改造
8. ✅ mock 路由
9. ✅ mock 错误归类
10. ✅ mock 归一 + 调试记录（本轮）

## 锚点

- 蓝本服务端：`agent-study/agent-study/agi-core/lm_service/lm_service/`
- 本体包：`cogos/cogos/lm_service/`
- 真实 deepseek model：deepseek-v4-flash / deepseek-v4-pro / deepseek-v4-flash-vision-exp
- 冻结契约：`LmClient.chat(messages, tier, must)` → `{content, finish_reason, usage, reasoning, raw, routed}` + `LmServiceError(category)`
- 运行：server 用 11435（11434 被蓝本旧 server 占用）
