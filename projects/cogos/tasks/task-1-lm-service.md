# task-1 — lm-service 实施

> 工位 B 执行。本文件自包含，干净会话读本文件 + 规格文档即可开工，无需工位 A 讨论上下文。

## 目标

实现 lm-service 最小版，让 `cu → lm-service` 一次调用跑通。屏蔽厂商差异（deepseek/openai 归一 + 错误归类 + 视觉 content[]），调用方只持 `internal_key` + `messages`，不碰厂商 api_key / model。

## 前置（工位 B 已备好）

- 本体：`work/B/cogos`（clone 自 `git@github.com:zhengyp36/cogos-dev.git`）
- 记忆：`work/B/locus`（clone 自 `git@github.com:zhengyp36/locus.git`）
- 本文件位于 `locus/projects/cogos/tasks/task-1-lm-service.md`
- 规格：`cogos/docs/design-lm-service-min.md`（**先通读，再动手**）

## 蓝本（搬运来源）

`agent-study/agent-study/agi-core/`：
- 服务端：`lm_service/lm_service/`（server.py / handler.py / scheduler.py / config.py / admin.py / providers/{base,deepseek,openai}.py，共 811 行）
- 客户端：`lm_call/lm_call/`（cli.py / logger.py）

## 轮次清单（每轮：实现 → 验证 gate → 记 checkpoint → 通知 /undo）

| 轮 | 内容 | 验证 gate |
|---|---|---|
| 1 | 包骨架 `cogos/cogos/lm_service/` + `config.py` 改（json→yaml 三文件 + internal_key 去 model 加 group + model 清单 + capability）+ `providers/base.py` 加 category 字段 | CLI 读写三文件成功 |
| 2 | `admin.py` 简化（api-key / internal-key / calls 三组命令 + 写三文件 + chmod 0600） | 三命令跑通 |
| 3 | 主链路：`router.py` 新增 + `handler.py`（鉴权简化 + tier/must/trace_id + 错误响应格式）+ `scheduler` 接 router | mock 一次文本调用跑通 |
| 4 | providers 归一（reasoning/视觉/content nullable）+ 防御性解析 + error category + finish_reason 特殊态 | mock 错误归类绿 |
| 5 | 调试 jsonl 落盘 + `admin calls` 子命令 | 字段齐全 + 投影/过滤可用 |
| 6 | 抽 `LmClient` async 接口（新建 client.py 封装 http 传输） | LmClient mock 调用跑通 |
| 7 | `lm_call` CLI 改造（复用 LmClient，删 logger.py） | lm_call CLI 跑通 |
| 8 | mock 测试：路由 | pytest 绿 |
| 9 | mock 测试：错误归类 | pytest 绿 |
| 10 | mock 测试：归一 + 调试记录 | pytest 绿 |

**停下点（轮 10 之后）**：真实验证（规格 6.2）需 YZ 提供真实 api_key。**AI 不擅自获取/试账号**，mock 全绿后停下，飞书通知 YZ。

## 工程规范（防走偏，已收敛）

- 三层命名：模块 `cogos.lm_service`（下划线）/ 命令 `cogos-lm-service`（连字符）/ 运行时目录 `~/.cogos/lm-service/`（连字符）
- 命令：一个入口 + 多级子命令（argparse 嵌套 subparsers，`set_defaults(func=...)` 分发，无子命令 `print_help()`），见规格 1.1
- 三文件对齐：`config.yaml` / `secrets.yaml` / `state.yaml` 靠 `(provider, account)` 对齐，`resolve` 取 `api_keys[0]`
- 错误：`category` 是字符串枚举（非数字错误码），服务端错误响应 `{"error":{"category","message"}}`，客户端解析抛 `LmServiceError(category, message)`
- mock patch 目标：`scheduler.PROVIDER_REGISTRY`（或 `ProviderBase.chat_completion`）
- 蓝本残留要删：`/v1/context-limit` 端点 + `global_context_limit()`；保留 provider 级 `base_url`

## 契约冻结（关键边界）

`LmClient.chat(messages, tier, must)` → `{content, finish_reason, usage, reasoning, raw, routed}`（规格 2.3）。此契约已冻结，工位 A 讨论 cog-runtime 依赖它。**实施中发现契约需调整 → 停下，回工位 A 讨论，不擅自改。**

## checkpoint 工作法（精简）

- 每轮结束写 `../checkpoint/`（工位 B 自己的 `work/B/checkpoint/`）：`status.md` + 本轮 `checkpoint-N.md`（锚点优先，凝练可恢复）
- 结构：当前问题 / 已做修改 `文件:行` / 关键结论 / 遗留坑
- 每轮 `status.md` 显式写「下一轮：读规格第 X 节 + 蓝本 X.py 第 Y 行起」
- 轮结束飞书通知 YZ 执行 `/undo`，新轮读 `status.md` 恢复
