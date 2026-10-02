# 第一刀执行日志 / 决策点（无人值守，10-03 夜）

> 目标（自 ENTRY + 讨论）：**骨架＋认领**。
> - 骨架：事件 → 装载 → 流 → 生成⇄动手 → 判结 → 落段（单流，多次动手仍只落一段；段含思考原话＋工具事实）。
> - 认领：装载产出「定性＋采纳」；同一事件换两套『我』→ 采纳与行为分叉。
> 性质：机制用测试做对，认领留接口、靠一次运行看现象。**不是**经验赌注（YZ 指出换『我』必有不同反应，真不变只说明装载坏了）。

## 环境侦察（先验可行性）

- 真实模型：**可用**。本地起 `python3.11 -m cogos.lm_service.server`（读 `~/.cogos/lm-service`），关键源＝`~/.cogos/lm-service/state.yaml` 的 active internal key（account 尾号b111）。实测 `pong`，非 degraded。
- 基线：`tests/agent` 278 passed / 3 skipped。
- 真实身份：`~/.cogos/agent/tangyu` 与 feishu accounts(COGOS001-A0001 等) 在，可做真机 e2e；首刀语义探针走 **真实模型＋FakeTelecom**（无外部副作用，同既有 behaviour probe 标准）。
- 结论：**当前环境可验证**。

**运维注记**：`lm-service` 用 `background_process` 起；**会话切换会被自动停**，故探针出现 `cu failed: retryable`（`rec.rounds=0`，模型没返回）时，先查进程是否还在，重启即可。探针脚本已能从 `~/.cogos/lm-service/state.yaml` 自取 active key（无需手填 `LM_INTERNAL_KEY`）。

## 决策点（目标内自决；裁决者＝目标）

- **D1 循环形态＝甲**：复用现有"一个运行时单元内部多轮模型⇄工具"，不物理拆"生成拍/动手"。why：目标只要求可观察行为；甲不引入易碎的结构化出口协议，不动 runtime；概念上生成/动手未物理分开，但**可观察结果相同**（"行为不变即非冲突"）。**被否**：乙（生成拍=tools=[] 单次 cu＋驱动层循环＋结构化出口）——留待单趟不够时。
- **D2 认领分叉**：`理` → 跑生成⇄动手；`搁置` → 不推进、段记"未了"；`不理` → 不推进、段记"了"、不回复。why：让探针判据清晰（采纳不同→行为不同），最小。回边（未了→张力→下一轮）只占位不接线。
- **D3 『我』按运行注入**（`Agent(..., me=...)`／`Consciousness(me=...)`），不改 profile 语义。why：探针要同一事件换两套『我』。
- **D4 流边界**：一个到达事件（飞书消息 / system 事件）＝一条流。不做挂起/续流/并发多流。
- **D5 段存储**：`memory/segments.jsonl` 追加；字段按 v2.2 §3.7。
- **D6 判结**：模型收束（无工具调用结束）＝`了`；撞硬闸（`MAX_TOOL_ROUNDS`）或出错/被打断＝`未了`。
- **D7 捕获**：每轮 `cu._resp` 的 reasoning（或该轮 content）在 `on_tool_call` 记入段的`过程`；工具调用+结果同点记入。末轮 reasoning 在 `on_done` 记入。
- **D8 探针**：FakeTelecom＋真实 deepseek，固定事件 × 两套『我』，各跑一次；比对`采纳`／是否动手／落段。

## 改动清单

- 新增 `cogos/agent/flow.py`：`Flow`、`segment_from_flow`、`SegmentStore`、`parse_verdict`。
- 改 `cogos/agent/consciousness.py`：接入 装载/流/段；material 改为按流现装。
- 改 `cogos/agent/app.py`：构造默认『我』＋ `SegmentStore`，透传；`Agent(..., me=...)`。
- 测试：`tests/agent/test_flow.py`；`test_consciousness.py` 增认领/落段用例。
- 探针：`scripts/exp_first_cut_claim.py`。

## 探针结果（脚本 `scripts/exp_first_cut_claim.py`，真实 deepseek-v4-flash + FakeTelecom）

同一事件（"执行 cat HELLO.txt 并回传"）× 两套『我』：

| | 采纳 | 定性 | 工具事实 | 外发 | LM 轮 | 段 |
|---|---|---|---|---|---|---|
| take（YZ＝搭档，分内事） | 理 | "…属于 cogos 项目的分内任务" | toolbox×4 | 1 | 6 | 结=了，过程 6 项（思考＋动手） |
| ignore（陌生来源，与我无关） | 不理 | "…与我无关" | 0 | 0 | 1 | 结=了，内容"未推进（采纳=不理）"，过程空 |

`采纳 diverged: True`。段按流装配、只落一段；`过程` 含每轮思考＋每次工具调用/结果。**骨架跑通、认领分叉成立。**

## 状态

- [完成] 实现＋单测。
- [完成] 真实模型探针：采纳/行为随『我』分叉。
- [待办] 全量测试回归。
- [未做] 真实 Feishu 身份 e2e（探针为真实模型＋假电信，无外部副作用）。
