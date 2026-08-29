# checkpoint-5 — LLM-Service 接口契约（上层调用 + key 语义 + 路由）

## 当前问题

LLM-Service 对外接口设计：cog-unit 怎么调、internal key 语义、模型选择/路由规则，收口到可实施。

## 关键结论（YZ 拍板）

- **internal key = 用途主体句柄**：一个 agent / 一个测试套件 / 一个公共模块各持一个 key；key 归 `group`（配额桶）= 归因/预算单位。key **不绑模型清单**，模型选择交 lm-service 自动路由。
- **厂商注册**：除 api-key/限速等常规信息外，声明模型清单 + 每模型 capability（`modality` 集合 + `tier` 档位），lm-service 抽象全局能力表。
- **cog-unit 调用契约**：传 `internal_key` + `tier`（可选倾向），**不指定模态**；lm-service 从上下文 `content[]` 的 `type` 自动推断模态。
- **路由优先级**：模态（硬约束）> tier（软倾向）。
- **tier = 倾向语义**：默认降级不失败；「禁止降级」是少数显式特例（must 后置）。
- **降级留痕**：`routed` 回报实际档位 + 降级信号，不静默（呼应 checkpoint-2 降级信号）。
- **trace_id 贯穿（YZ 认可，收紧）**：纵向关联键，把一次业务语义运算与其下拆出的多次底层调用串起来；**生成在上层**（CogUnit/任务/认知树节点），lm-service **只透传记录、不生成**。与 internal_key 正交：key = 哪个主体（静态用途），trace_id = 哪个任务/节点（动态实例）。
- **lm-service 无父子关系**：lm-service = 裸盘 IO（纯 LLM API 调用，类比 zfs 底层设备），不感知上层调用间关系。**span/父子结构由 cog-unit 树维护**（生成子 trace 时携带 parent），lm-service 永不实现 span，只透传 trace_id 字段——cog-unit 设计变化时 lm-service 不跟着改。

## 接口草案

- 请求：`{internal_key, trace_id?, messages: [{role, content: [{type, ...}]}], tier?: cheap|expensive, fallback?}`
- 响应：`{content[], usage, routed: {tier, modalities, cost}}`

## 遗留 / 后置

- 跨厂商自由路由：能力表统一容纳多 provider，阶段 1 单 provider 内路由，跨 provider 后置。
- 能力表字段细节：modality 声明结构、tier 档位枚举后置细化。
- `fallback`/must 字段：阶段 1 只做倾向语义，禁止降级字段后置。
- 待拍板（自 checkpoint-3 遗留 7 项中仍开着的）：配额单位结构、三层模型 group→key→trace_id 落地、source 阶段 1 粒度、重试范围、过程记录字段集。
