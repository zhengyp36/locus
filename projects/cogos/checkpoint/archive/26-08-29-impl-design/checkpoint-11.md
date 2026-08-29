# checkpoint-11 — CogRuntime 边界收紧：不感知反写树 + 优先级待场景

## 当前问题

顺着 zio 映射想清 CogRuntime 运行过程后，修正两处：CogRuntime 是否感知「反写树」；优先级是否现在实现。

## 关键结论（YZ 澄清）

### CogRuntime = 纯执行环境，不感知「反写树」

- cu 的运行过程（zio 映射）：创建（惰性描述）→ 发起 wait/no_wait 统一入 taskq → 推进 pipeline（查 children 就绪→装配→提交 InferNode→结束）→ done。
- **执行散在三处，无独立执行器**：taskq（队列+并发窗口）、cu 状态机（pipeline 推进+依赖检查+父子通知）、推进循环。之前的 CogExecutor 被这三者吸收，不存在。
- **CogRuntime 只做**：调度 cu 跑完（交 InferNode）→ 结束后触发 done 回调 → 通知父 cu。
- **反写树是上层的活**：上层在 done 回调里消费结果、决定反写；CogRuntime 不知道「树」存在。回流触发点 = done 回调，与 checkpoint-7「cu 无状态、连续性在树」一致。

### cu done 语义 + 回调/通知顺序

- `cu.done` = 这个 cu 结束（lm-service 成功返回 / 重试成功 / 失败 / 重试仍失败返回），都算结束。
- done 后动作顺序**暂定**：先 done 回调（结果交上层消费，可能含回写）→ 再通知父 cu。理由：让父被唤醒时子的副作用已落定。无场景不定死，留待校准。

### 优先级：有想法、缺场景，第一版不实现

- zfs 的 zio 优先级按 IO 类型（read/write/sync/async）定，有场景支撑；cogos 缺场景。
- 第一版用最简单队列（FIFO + 并发窗口），不实现优先级；等真实场景（如紧急回复 vs 后台整理）再引入。

### 多 agent：多 CogRuntime，lm-service 令牌仲裁

- 每 agent 一个 CogRuntime（自己的 taskq + cu 状态机），agent 内自治。
- agent 间在 lm-service 竞争，按 internal_key（= 配额桶）令牌分配；一个 agent 一个 key = 一个令牌桶，天然隔离。
- CogRuntime 无状态轻量，按 agent 实例化。配额是否「相同」是资源控制策略，lm-service 只执行令牌桶。

## 命名（先过程后组件，浮现结果）

| 组件 | 是否存在 |
|---|---|
| CogRuntime（= taskq + 推进循环 + 完成通知） | ✅ |
| CogUnit（惰性描述 + 执行句柄 + 状态机 + 父子关系） | ✅ |
| taskq | ✅ |
| InferNode（= LLM-Service） | ✅ |
| CogExecutor | ❌ 被吸收 |

## 遗留 / 待场景

- done 回调 vs 通知父的精确顺序（暂定先 done 后父）。
- 优先级怎么定（待真实场景）。
- 修正 checkpoint-9「ce 优先级调度」措辞：优先级降级待场景；checkpoint-10 三流图「结果写回树」应在 done 回调（上层）而非机制层。
