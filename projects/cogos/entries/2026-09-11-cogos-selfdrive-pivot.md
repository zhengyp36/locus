# 2026-09-11 转向自驱回路 + 行业定位评估

## 结论

从"视觉/机制细节"转回主线：造**能自驱推进**的 cogos agent（人不在场时自己思考并推进，人在场时一起裁决）。定为**自主度阶梯**，入口 = dogfood（agent 维护 cogos 自身）：

| 阶 | 能力 |
|---|---|
| L0 | 给定任务执行（已有） |
| L1 | 做完能自验（缺口 = 触发 + 通道） |
| L2 | 无人时自启动/续跑下一步 |
| L3 | 自己决定"什么值得做" |
| L4 | 与人异步共驱（目标） |

**不押实现 L4**，押"把回路建起来、逐阶抬升"。

## 行业定位评估（为何转向）

- **定位（vision）已商品化**：ScreenSpot-Pro 早期最好 18.9% → 2026-09 榜首 ~87.9%（Claude Opus 4.8）/ Qwen3.8 Max 84.5%；OSWorld-Verified 12%（2024）→ 86.1%（Qwen3.8 Max），人类基线 72.36%。自建定位精度无价值。
- **交互式搜索/逐步放大也是业界既有**：ScreenSeekeR、RegionFocus、UI-Zoomer、AutoFocus、Visual Test-time Scaling（ICCV'25）等。
- **未解在长程**：OSWorld 2.0（中位任务人类 1.6h）最强仅 20.6%；HORIZON（arXiv 2604.11978）证失败是断崖式、归因 planning + memory；per-step 错误率随进度上升（Illusion of Diminishing Returns, ICLR 2026）。
- **验证是活跃区但非空白**：VeriGUI（action-effect verification 作 RL 目标）、VSA（动作前逻辑验证）、verifier agent、reward model。可差异化在 **harness 层**（触发/通道/归因/记忆 resurface），而非再造 verifier。
- 判断：cogos 的独特价值在"自省/自验证回路 + 过程误差归因"，不在视觉。

## 保命收编

- `/tmp/kilo`（易失）→ `cogos/research/`（脚本 + raw.jsonl 等非图片，526 文件；图 133MB 未收）；push `c3ad76f`。
- 旧活文档 `../checkpoint` 87 文件 → `locus/projects/cogos/checkpoint/26-09-11-live-checkpoint/`；push `ace9c95`；随后清理 `../checkpoint`（留 README 指针）。
- LM key `ik_c47...` 在新提交替换为 `ik_REDACTED`（原值仍在 locus 历史；YZ 已知，内部 key 外部不可用）。

## S0 状态面（缺口）

回路 `议程 → 触发 → 执行 → 验证 → 写回`，缺三格：
1. **机器可读议程**（现仅人写的 ISSUES/tasks/ROADMAP）；
2. **自触发**（有消息/timer 原语，缺"从议程自启动/续跑"）；
3. **agent 内自验证**（能力已证存在，缺触发 + 通道）。

执行层齐（lm_service / cog_runtime / agent.consciousness+tools+terminal）；感知视觉（img_tool / image_ctx / cog_ctx）库完成但**未接入 consciousness 工具集**；记忆缺跨会话持久。

## 产物锚

- 计划：`../checkpoint/plan.md`
- S0 状态面：`../checkpoint/state.md`
- 交接：`../checkpoint/status.md`
- 架构视阈：`cogos/agent/*`（consciousness/tools/terminal/timer/events/perception）
