# checkpoint-3 — LLM-Service 定位、来源追踪、传输、配额/能量设计讨论

## 当前问题

阶段 1 LLM-Service 动手前，收口目的五性盘点、过程记录、来源追踪、传输方式、配额归属与能量控制边界，明确「必须做 / 可遗留」分界。

## 已拍板（YZ 明确）

- 传输方式 = 本地 unix socket（替代 http）。http 只解决「局域网可达」，未解决「本机多用户/多进程可达」；socket 文件权限（0700 目录）+ peercred 收紧到「本机可信进程」。
- 鉴权 = 暂不考虑，作遗留（当前非重点，后续完善再考虑）。
- internal_key 重定位 = 非秘密句柄，目的 = **隐藏厂商 api_key + 用量管控**（分类/集合/配额/已用/剩余），**非鉴权**。现有 http 那套（`add_internal_key` 的 secrets 签发、`delete_internal_key` 的 revoke、`_validate_internal_key`）是错位产物，整理时简化。
- 配额归 LLM-Service 管（硬执行 + 告警）；CogExecutor 只管推理调度/透传，不管配额。

## 目的五性现状盘点（蓝本 = agent-study `lm_service`）

- 一致性：响应已归一 `{content, finish_reason, usage, raw}`（openai.py:48-55）；**缺 thinking/reasoning 输出归一**（deepseek `reasoning_content` 被丢弃，deepseek.py:48-51）；流式无（硬编码 `stream: False`）；tool call 白名单无 `tools`。
- 可靠性：`ProviderError` 缺类别字段（retryable/auth/quota/content/semantic，base.py:1-6）；无重试/退避/降级，仅 120s timeout。
- 可控性：并发已有（semaphore + RPM 软约束 + `(provider,account)` 池化，scheduler.py:16-108）；usage 透传未记账。
- 安全性：key 隔离/内部鉴权/白名单/文件权限已落地（config.py:198-219, handler.py:6-16, config.py:38-47）；按新定位鉴权部分要简化。
- 可观测性：事件流未实现（ISSUES 缺口，hooks.md:67）；讨论后事件流获得新用途 = 「配额告警 → 能量控制」的机制层信号通道。

## 过程记录（新增必做，从可观测性域独立）

- 定位：每次调用 append-only 记输入/输出/usage/latency/status，用途=调试分析「给定输入得到什么输出」+ raw trace 源头（hooks.md:57 认知树回链 raw trace 靠它）+ 计量原料。
- 服务端做（统一入口保证「每一次」留痕），非客户端（agent-study `lm_call/logger.py` 是客户端手动日志，可绕过）。
- 分层：结构化调用记录=必做；成本换算（token→钱，本地计价表）+ 归档清理自动化=可遗留；存储结构按时间/调用方可分区。

## 来源追踪 → 三层模型（待拍板）

来源标识 vs 用量归因是两个正交维度，现有 internal_key 混为一处。建议三层：

- `group` = 预算桶/归因单位（公开标签，非 key）。
- `internal_key` = 来源主体 + 路由（provider/account/model）+ 归因（非秘密句柄）。
- `trace_id` = 动态实例（CogUnit/任务/认知树节点），请求可选字段携带，raw trace 回链靠它。

变更历史（key/group 增删改 + 映射变更）走 append-only 日志，与过程记录同一套基础设施。

## 厂商 API 面（哪些要考虑）

| API | DeepSeek | OpenAI | 判断 |
|---|---|---|---|
| chat/completions | 有 | 有 | 核心，已有 |
| usage（token 用量） | 随响应 | 随响应 | 计量原料，已有 |
| 独立 token 计数 | 无 | 无稳定端点（本地 tiktoken 近似） | 遗留（用 usage） |
| 余额查询 | `/user/balance` | 无稳定公开端点 | 遗留到账号告警 |
| 模型列表 `/models` | 有 | 有 | 遗留 |
| embeddings / completions / files | — | — | 不做 |

## 配额 / 能量控制（YZ 主导，方向已定，细节待拍板）

- **账本/速率/决策三分离**：真实消耗只在 LLM-Service → 账本归它；消耗快慢看 CogExecutor 执行过程 → 速率透传；能量控制合成两者做决策。
- **告警先于不足**：告警事件（异步旁路，驱动提前降速）≠ 配额错误（同步控制流，拒绝调用）。两个时机。
- **能量控制定位**（待拍板）= 资源级元控制机制层（本能预装、不可自长）；降速/昏迷/休眠是生理本能安全阀，任务优先级/砍哪类任务是策略层可自长。
- **阈值三级**：降速阈值 / 昏迷阈值 / 预留整理能量（昏迷前用预留做内部整理再休眠，上报管理员充值，类比低血糖昏迷输液）。
- **一组配额**：每 agent 一组（后续按成本/推理质量分级 API，每级一个配额）；阶段 1 先单级，结构预留为「一组」。

## 阶段 1 划界（结合「不全做」）

- 必做：unix socket；internal_key 非秘密句柄 + source→group 映射；配额账本（先单级 token）+ 硬执行（不足→错误）+ 告警阈值 emit 事件；用量累计记账；过程记录（结构化调用记录）；ProviderError 类别字段；thinking/reasoning 归一（待拍板）。
- 可遗留：鉴权；能量调控策略（降速/昏迷/休眠/上报）；成本分级多级配额；速率感知消费端；成本换算/余额查询；流式；tool call 透传；降级/账号切换；事件流消费者；peercred 精细识别。

## 遗留 / 待拍板（7 项）

1. 配额单位与结构：token 单级先落地，多级结构预留？
2. 能量控制定位：机制层本能（不可自长），策略才自长？
3. 三层模型：group（标签）→ internal_key（句柄）→ trace_id？
4. source 阶段 1 粒度：模块级 or 预留 agent？
5. 重试：只补 ProviderError 类别字段 or 连最简退避重试？
6. thinking/reasoning 归一：阶段 1 是否做？
7. 过程记录字段集：8 字段够否，是否含完整 `raw`？

## 坑

- 若 cogos 后续跑 docker，socket 要挂 volume 共享、peercred 的 uid 映射要处理（先记，不展开）。
