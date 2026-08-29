# task-2 — cog-runtime 设计讨论

> 工位 A 执行。继续讨论 cog-runtime 设计（阶段 1 底层三件的第二件）。

## 目标

继续收敛 cog-runtime 设计：CogRuntime 运行过程 + cu 状态机 + 工具续轮 + 并发模型。与工位 B 的 lm-service 实施并行，靠 `LmClient` 冻结契约解耦（见 task-1「契约冻结」）。

## 活文档（在工位 A 的 `../checkpoint/`）

- `status.md` — 本阶段入口 + 讨论进度
- `design-cog-runtime.md` — CogRuntime 设计活文档（已出雏形：状态机 created→pending→ready→queued→running→tooling→done；zio 流水线映射；三回调 on_ready/on_tool_done/on_done；四约束）

## 讨论素材（已归档 locus，按需取用）

- `locus/projects/cogos/checkpoint/archive/26-08-29-impl-design/checkpoint-7~13.md` — cu/ce 设计、预算归属、CogRuntime 边界、cu 最小契约、工具调用与 cu 关系
- `locus/projects/cogos/checkpoint/archive/26-08-29-impl-design/cognition.md` — 认知框架笔记（logprobs 熵信号等，待映射到意识子系统与元控制）

## 依赖的冻结契约

`LmClient.chat(messages, tier, must)` → 归一响应 + `LmServiceError(category)`，见 `cogos/docs/design-lm-service-min.md` 2.3/4.x。讨论 cu 生命周期时直接引用，不重复定义。
