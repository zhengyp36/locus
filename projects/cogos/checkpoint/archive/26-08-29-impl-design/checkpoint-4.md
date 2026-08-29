# checkpoint-4 — LLM-Service 完整设计（目标态）+ 最小闭环（第一步态）方案

> 整理自 checkpoint-3 及后续讨论。原则：讨论成果全记录（目标态，不丢方向），另立最小闭环（第一步态，只做可行性必要项 + 移植完整性）。减法可追溯：每个后置/口子项标注影响面，验证失败时先排除「口子未补导致的假阴性」。

## 已拍板边界

- 传输：最终 unix socket（peercred + 文件权限收紧到本机可信进程）；**第一步态用 http（127.0.0.1）替代**。
- 鉴权/权限：遗留（规模化、真正部署使用才考虑；最小闭环阶段「本机无恶意进程」软假设成立）。
- internal_key：非秘密句柄，目的 = 隐藏厂商 api_key + 用量管控（分类/集合/配额/已用/剩余），**非鉴权**。现有 http 的签发/吊销/validate 是错位产物。
- 配额归 LLM-Service 管（硬执行 + 告警）；CogExecutor 只透传，不管配额。

## 完整设计（目标态，按维度，标注时机）

| 维度 | 项 | 时机 |
|---|---|---|
| 一致性 | 响应归一 `{content, finish_reason, usage, raw}` | 已具备 |
| 一致性 | thinking/reasoning 输出归一（deepseek `reasoning_content` 现被丢弃） | 第一步态必做 |
| 一致性 | 流式 | 后置 |
| 一致性 | tool call 透传（白名单加 `tools`） | 后置（CogUnit 阶段） |
| 可靠性 | ProviderError 类别字段 retryable/auth/quota/content/semantic | 第一步态必做 |
| 可靠性 | 重试/退避（可重试类指数退避，设上限） | 后置 |
| 可靠性 | 降级/账号切换/告警（401/403/404/402 旁路） | 后置 |
| 可控性 | 并发（semaphore + RPM 软约束 + `(provider,account)` 池化） | 已具备 |
| 可控性 | 用量累计记账 | 第一步态必做（并入过程记录） |
| 可控性 | 配额账本（每 agent 一组，成本/质量分级）+ 硬执行 + 告警 | 后置 |
| 安全性 | key 隔离 / 文件权限（0o700/0o600） | 已具备 |
| 安全性 | socket + peercred | 后置 |
| 可观测性 | 过程记录（每次调用 I/O 落盘，append-only） | 第一步态必做 |
| 可观测性 | 事件流（配额告警 → 能量控制的机制层信号通道） | 后置 |
| 能量控制 | 账本/速率/决策三分离 + 告警先于不足 + 阈值三级（降速/昏迷/预留整理） | 后置（设计素材） |
| 来源追踪 | 三层模型 group→internal_key→trace_id + 变更历史（append-only） | 口子（字段占位） |
| 厂商 API | 余额查询（deepseek `/user/balance`）/ 模型列表 / 成本换算（本地计价表） | 后置 |

能量控制设计素材（后置实现，先记下）：
- 账本/速率/决策三分离：真实消耗只在 LLM-Service → 账本归它；消耗快慢看 CogExecutor → 速率透传；能量控制合成两者决策。
- 告警先于不足：告警事件（异步旁路，驱动提前降速）≠ 配额错误（同步控制流，拒绝调用）。
- 阈值三级：降速阈值 / 昏迷阈值 / 预留整理能量（昏迷前用预留做内部整理再休眠，上报管理员充值，类比低血糖昏迷输液）。
- 能量控制 = 资源级元控制机制层（本能预装、不可自长）；任务优先级/砍哪类任务是策略层可自长。

## 最小闭环（第一步态）待办清单

目标：证明「一次 LLM 调用 → 结果写认知树 → 基于树二次调用」的语义运算可行性。

### 必做（4 项）

1. **移植进 cogos**：`lm_service`（server/scheduler/providers/handler/config/admin）+ `lm_call` 客户端搬进 cogos 包结构，补 pyproject 依赖，**http 传输保留**。
2. **ProviderError 类别字段**：`base.py` 加 `retryable/auth/quota/content/semantic`，provider 非 200 时分类填充。
3. **thinking/reasoning 输出归一**：deepseek `reasoning_content` 归一进结果；openai `reasoning_effort` 对应映射。
4. **过程记录最小版**：append-only，字段 = 时间 / source / provider / account / model / messages 输入 / content 输出 / usage / latency / status / 错误类别；按时间/调用方可分区。

### 口子（字段占位，逻辑后补，2 项）

5. `internal_key` 挂 `source` 字段 + `group` 字段。
6. 调用记录带可空 `trace_id` 字段。

### 替代 / 后置（不阻塞第一步态）

- socket → 先用 http 替代（影响面：无文件权限/peercred 收紧，本机可信是软假设，与鉴权遗留一致）。
- 鉴权/peercred → 遗留。
- 重试/降级/配额硬执行/告警/能量控制/成本换算/流式/tool call → 后置。

## 审核要点

- 必做 4 项是否充分且必要？
- 口子 2 项：字段现在加，还是连字段都后置？
- http→socket 替代是否认可？
