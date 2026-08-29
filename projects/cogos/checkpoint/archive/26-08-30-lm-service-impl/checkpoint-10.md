# checkpoint-10 — 轮 10（归一+调试记录 mock）+ tier 改名 + 真实验证

## 当前问题

轮 10 mock（规格 6.1 归一 + 调试记录）收尾；tier 命名 cheap/expensive → basic/advanced（YZ 拍板，视觉模型归 basic 档）；用真实 deepseek key 做 6.2 真实验证（文本 / 401 / 视觉 jpg + LLM-as-judge）。

## 已做修改

- `cogos/lm_service/router.py:5-6`：`TIERS=("basic","advanced")`、`_TIER_RANK={basic:0,advanced:1}`
- `tests/lm_service/test_router.py`：全改 basic/advanced；视觉模型 `VISION_BASIC`（tier=basic + [image]）；新增 `test_image_tier_advanced_degrades_to_vision`（带图+advanced → 降级 vision basic，degraded=true）
- `tests/lm_service/test_normalization.py`（新建，6 用例）：deepseek/openai 两 adapter 端到端字段集一致 {content,finish_reason,usage,reasoning,raw} + deepseek reasoning_content→reasoning / openai reasoning=None / content null→""
- `tests/lm_service/test_recording.py`（新建，8 用例）：submit 后 calls.jsonl 落盘一行 16 字段齐全 + tier/must/routed_tier/degraded 正确 + admin calls 投影/过滤/计数/导出
- `docs/design-lm-service-min.md`：2.1 配置示例（三真实 model + basic/advanced + 视觉归 basic）、2.3 tier 语义（basic|advanced 推理能力档）、6.1 路由
- `docs/vision-system-design.md:13`、`docs/cogos-plan.md:83`：tier 改名同步

## 关键结论/决策

- tier 语义收窄为「推理能力档位」basic/advanced（非价格）；视觉是正交模态由 modalities 声明。视觉模型 deepseek-v4-flash-vision-exp 归 **basic 档**（推理=flash 级）。
- 真实 deepseek model：`deepseek-v4-flash`（basic）/ `deepseek-v4-pro`（advanced）/ `deepseek-v4-flash-vision-exp`（basic + image）。
- 真实验证全绿：文本 basic/advanced 归一字段集完整；厂商 401→auth（真实 body 无 category，服务端归类）；视觉 jpg 真读图 + judge equivalent=true。
- 调试记录 jsonl + admin calls 真实落盘可用。

## 遗留/坑

- **端口 11434 被蓝本旧 server 占用**（pid 1232，8-27 起，`~/.agi-core/lm-service.json`），本轮改用 11435 跑 cogos server。
- **deepseek thinking 默认开启**：reasoning 会吃掉 max_tokens 导致 content 空 + finish_reason=length（advanced 50 tokens、vision 1200 tokens 均触发过）。识图/简单任务需 `thinking={"enabled":false}` 或加大 max_tokens。
- **admin CLI 写文件后，运行中 server 内存不刷新**（config load 一次），加 key/ik 需重启 server 才生效——多进程真实场景需注意（设计行为，非 bug）。
- 视觉模型 latency 高（识别 11s），thinking 关闭后 137 completion tokens 快速完成。

## 验证

- 轮 10 后 `tests/lm_service/` 47 passed；全量 pytest 715 passed 无回归。
- 真实调用均经 `cogos-lm-service` CLI / `LmClient`（http 127.0.0.1:11435）完成。
