# checkpoint-2 — LLM-Service 目的与异常处理

## 当前问题

阶段 1 动手 LLM-Service 前，先厘清这一层的目的边界与异常处理策略，避免把语义层职责塞进基础设施层。

## 已读代码要点

- `lm_service/scheduler.py:16-93` — `AccountScheduler` 只做 `Semaphore` + RPM 本地 sleep（软约束）；`Scheduler` 按 `(provider, account)` 池化（`scheduler.py:97-108`）
- `lm_service/providers/base.py:1-6` — `ProviderError` 只有 `status_code/message/raw`，**缺错误类别字段**
- `lm_service/providers/openai.py:11-56` — 字段映射 + 错误归一雏形，无重试/无降级
- `lm_service/handler.py:6-65` — 字段白名单 + internal key 鉴权（key 隔离已做）；usage 只透传**未记账**

## 目的

LLM-Service 的定位：把 LLM 变成可靠的、可计量的外部资源。目的按五个维度组织：

### 一致性 — 屏蔽厂商差异

- 契约稳定：上层只认一种语义接口，不随厂商 API 演进改代码。
- 协议抹平：流式/非流式、thinking/reasoning、tool call 格式差异都在这一层消化。
- 真假可替换：统一接口让上层可挂 FakeLLM，替换对象是"真/假"而非仅厂商。
- 为什么有它：上层 CogUnit 若直接面对多厂商，语义运算会被厂商细节污染，且无法做测试替身。

### 可靠性 — 屏蔽异常

- 重试/退避/降级：可重试的异常（429/5xx/网络）指数退避重试，设上限。
- 消化原则：能内部消化的内部消化，消化不了归一上抛。
- 为什么有它：控制并发只是预防（不触发被动限流），API 异常不止限流，真正的可靠性靠分类处理。

### 可控性 — 并发与计量

- 并发限流：主动限流防被动限流（semaphore + RPM）。
- 用量计量与成本归因：usage 记账，按调用方归因 token 用量与成本。
- 为什么有它：喂给 CogExecutor 的资源级元控制（预算），实现"放权不放资源无限"。

### 安全性 — 权限边界

- key 隔离：厂商 API key 对内部调用方不可见。
- 内部鉴权：internal key + 请求字段白名单。
- 为什么有它：统一入口是收口权限、白名单与审计的唯一位置。

### 可观测性 — 诊断出口（待实现）

- 事件流：内部状态可被外部观察的基础设施，作为诊断出口的载体。
- 为什么有它：诊断出口在"消化成功"时也要发（承载"消化留痕"），且不依赖 catch 业务异常。
- 状态：五性中唯一未落地项，其余四性均有蓝本或方案，事件流仍是 ISSUES 缺口。

## 非目的（负向边界）

目的的完整性 = 正向目的 + 明确不做什么。以下职责不属于 LLM-Service，越界即破坏分层：

- 语义纠错 — CogUnit 的活
- prompt 编排 / 临时心智现场装配 — CogUnit 的活
- 预算策略决策 — 资源级元控制，在 CogExecutor
- 工具执行 — 高风险受控 tool call 是 CogUnit，LLM-Service 只透传协议

## 屏蔽差异的正确定位

差异不是被抹掉，而是关进 provider 适配器内部。通用分类在公共层，厂商特定处理在 `providers/<vendor>.py`。

## 增加厂商 API 标准步骤

1. 调研：鉴权 / 端点是否 OpenAI 兼容 / 请求参数差异 / 响应结构差异 / 限流规则 / 错误码与错误体 / 计费方式 / 流式协议
2. 代码：新增 provider 继承 `ProviderBase` → 字段映射 → 响应归一 → 错误码→类别映射 → 注册 `PROVIDER_REGISTRY` → 配置账号
3. 验证：单测（映射/归一/错误各一条）+ 真实 key 跑通 + 故意触发限流看类别

## 异常处理

- 分类：可重试（429/5xx/网络）→ 指数退避重试；不可重试（参数/语义/内容违规）→ 归一上抛；需旁路（401/403/404/402）→ 标记失效 + 告警/切换账号
- 分层：基础设施异常在 LLM-Service 层，语义异常在 CogUnit 层（呼应 `agent-study-hooks.md:47`），不越界
- 落地前提：`ProviderError` 需加类别字段 `retryable / auth / quota / content / semantic`

## 消化原则

能内部消化的内部消化，消化不了归一上抛。消化限定三条件：

- 有明确可自动执行的恢复手段
- 设上限（重试/降级次数+延迟），耗尽即上抛，不无限重试
- 降级成功的要在结果显式标记降级信号，留痕不静默

## 上抛两种出口

- 业务出口 = 同步返回/抛异常（控制流），业务处理"接下来怎么办"；内部再分"可自动处理（semantic）vs 转人工（auth/quota）"
- 诊断出口 = 旁路事件流（观测流），业务不感知但诊断要感知；走独立 event stream（`agent-study-hooks.md:67`），不通过 catch 业务异常来感知；消化成功时也要发（承载"消化留痕"）

## 遗留 / 坑

- `ProviderError` 缺类别字段，动手 LLM-Service 先补
- 用量计量/记账未做（资源级元控制的输入）
- observability 事件流仍是缺口，是诊断出口的载体，阶段 1 需一起定
- 流式协议 / 降级信号字段未涉及，做时再定
