# status — task-3 lm-service 遗留三项（工位 B）

## 每轮规则

1. 读本目录新增信息（`status.md` + 最新 `checkpoint-N.md`）恢复上下文，再开始新一轮。
2. 完成当轮任务（`task-3-lm-service-fixes.md` 轮次清单）；验证只跑 `python3.11 -m pytest tests/lm_service/`（不跑全量——feishu/phone tests 耗时且不受影响，全量回归留轮 5）。
3. 新增 `checkpoint-<N>.md` 说明情况（当前问题/已做修改 `文件:行`/关键结论/遗留坑）。
4. 更新本 `status.md`（状态 + 轮次清单打勾 + 显式写「下一轮：读规格第 X 节 + codebase 锚点」）。
5. 有新代码认知则 append 更新 `codebase.md`（锚点优先，只增不改旧结论）。
6. 提交 cogos 本体工程代码修改（`git -C /home/zhengyp/work/B/cogos`）。
7. 飞书通知 YZ 执行 `/undo`，然后停下等下一轮。

## 当前目标

lm-service 三项遗留：① internal_key 自带 base_url ② tool call 内部化 ③ 输出 content 归一 `content[]`。

- 任务：`locus/projects/cogos/tasks/task-3-lm-service-fixes.md`
- 代码认知：本目录 `codebase.md`
- 规格：`cogos/docs/design-lm-service-min.md`（冻结契约 2.3 / 响应归一 3.3）+ `design-cog-runtime-min.md`（4.x 与 lm-service 衔接）

## 状态

**task-3 全部完成（含真实 tool call 验证）。** 5 轮 mock 全绿 + 全量 733 passed 无回归 + 真实验证全绿（deepseek tool call 同构 openai、arguments 真实 parse、strict 忽略不补）。代码已提交 `c74b0d0`。详见 `checkpoint-6.md`。

## 轮次清单

1. ✅ ① 删 `LmClient` base_url 参数，服务端地址走环境变量/默认
2. ✅ ③ `parse_response` content 归一 list + recorder/scheduler 记录改
3. ✅ ② `tool_calls` 归一输出（parse arguments + id + finish_reason 校验）
4. ✅ ② `tools` 输入组装厂商格式（deepseek/openai）+ 白名单加 tools
5. ✅ 全量回归 + 调试记录字段补齐（tool_calls）
6. ✅ 真实 tool call 验证（deepseek，YZ 提供 key）

## 待 YZ 裁决

- 规格 `design-lm-service-min.md` 第五节调试记录字段清单是否同步加 `tool_calls`（轮 2/5/6 遗留）。
- `cli.py _cmd_call` 非 raw 模式 content 打印 list repr，是否美化。

## 锚点

- 本体：`/home/zhengyp/work/B/cogos`，包 `cogos/cogos/lm_service/`
- 测试：`tests/lm_service/`（test_errors 194 / test_normalization 115 / test_recording 210 / test_router 171）
- mock patch：`scheduler.PROVIDER_REGISTRY`（或 `ProviderBase.chat_completion`）
- 冻结契约：`LmClient.chat(messages, tier, must)` → 归一响应 + `LmServiceError(category)`（形状不变，仅扩展字段：加 `tools` 入参 / 加 `tool_calls` 出参 / `content` 变 list）
