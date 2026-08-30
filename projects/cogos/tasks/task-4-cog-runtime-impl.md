# task-4 — cog-runtime 实施

> 状态：已完成（08-30）。段 1/2 全绿 + lm-service 续轮转换补齐 + 真实 deepseek 闭环三路全绿（A 文本 / B 工具续轮 / E 401→auth），全量 pytest 777 passed。详见 `checkpoint/checkpoint-3.md`（段 1）/ `checkpoint-4.md`（段 2）/ `checkpoint-5.md`（续轮转换）。遗留：告知值默认注入先不做。

## 目标

实现 cog-runtime 最小版：**一个 cu 从创建到 done 跑完一次的最小闭环**，含「不调工具 / 调工具」两支路。代码落 `cogos/cogos/cog_runtime/`，对外 import 路径 `from cogos.cog_runtime import CogRuntime`。

## 前置

- 本体：`/home/zhengyp/work/A/cogos`（包 `cogos.cog_runtime`，新建）
- 设计（本次的规格）：`cogos/docs/design-cog-runtime-min.md`——**内部实现设计 3.5/3.6 已固化**（checkpoint-2 四问题收敛），是实现的唯一依据
- LmClient 冻结契约：`cogos/cogos/lm_service/client.py` + `providers/base.py`（`parse_response` 归一）+ `scheduler.py:165`（`routed` 在 scheduler 层加）
- 测试约定：pytest + pytest-asyncio（`asyncio_mode=auto`），mock 用 `monkeypatch`，测试落 `tests/cog_runtime/`

## 契约层（先写，防跑偏——上轮拍板「只上 1+2」）

先落类型 + 契约测试，再写 `_advance`。类型是硬约束，契约测试是 LmClient 归一响应的可执行版本。

### 1. 类型定义（`cog_runtime/` 内，dataclass + Literal）

- `Tier = Literal["basic", "advanced"]`
- 三态：`CuResultOk(content: list)` / `CuResultError(category: str)` / `CuResultInterrupted(reason: str | None = None)`
- 归一响应类型（`LmClient.chat` 返回值形状，mock 时按此断言）：
  - `content: list`（`[{type, text}]` 或 `[]`）
  - `finish_reason: str`
  - `tool_calls: list[dict] | None`（`[{id, name, args}]`）
  - `usage: {prompt_tokens, completion_tokens}`
  - `reasoning: str | None`
  - `raw: dict`
  - `routed: {tier, degraded}`
- CogUnit 字段类型（material/tier/tools/callbacks/parent/children/state/result/interrupt_reason）

### 2. 契约测试（`tests/cog_runtime/test_contract.py`，mock LmClient）

- `chat` 返回形状断言（含 `routed`，注意 provider 层无 routed、scheduler 层加）
- `tier` 透传断言（basic/advanced 原样进 `chat(tier=...)`）
- `LmServiceError(category)` → `CuResultError(category)` 六类映射断言

## 实施轮次（每轮：实现 → 验证 gate → 记 checkpoint）

| 轮 | 内容 | 验证 gate |
|---|---|---|
| 1 | 类型定义 + 契约测试（mock LmClient） | 契约测试绿 |
| 2 | CogUnit（纯数据+句柄：`wait/no_wait/interrupt/add_child`，`remove_child` 抛异常） | 单测绿 |
| 3 | CogRuntime + `_advance` 状态机（五触发源 + interrupt 检查点 + on_ready 后重查） | 支路 A 闭环绿 |
| 4 | 工具续轮（`on_tool_call` + tooling 态 + 消息 append + 再入队） | 支路 B 闭环绿 |
| 5 | 并发（`Semaphore(N)` + `max_concurrent`）+ 父子通知 + `_units` 注册表 | 并发/父子单测绿 |
| 6 | 3 个实施细节落地 + 全量回归 | 全量 pytest 绿 |

## 3 个实施细节（实施时定，不阻塞，轮 6 统一落地）

- ① 告知值注入格式（设计 2.5）：默认注入窗口预算到 material，格式待定（机制层给默认、上层可覆盖/置空）
- ② 父子 on_ready 装配完整示例（子结果如何经 on_done 收起、父 on_ready 里装配进 material）
- ③ shutdown 收尾等待策略（遍历 `_units` 统一 `interrupt("shutdown")` 后如何等待收尾）

## 工程规范（防走偏）

- 类名 `CogUnit` / `CogRuntime`，叙述性简写 cu；六类 category 沿用 `ErrorCategory`（StrEnum，值字符串）
- 结果层值传递，异常止于底层：`LmServiceError` 在 cu 内捕获转 `CuResultError`，不向上抛
- 状态机稳定点四态 `pending/queued/running/tooling`，队列只装 queued；`done` 含成功与失败
- 改动最小化：**不动 lm_service 任何代码**，cog-runtime 只依赖其冻结契约

## checkpoint 工作法（跨会话自动交接，分 2 段）

- 6 轮分 **2 段**，每段一个新会话，段间人工开新会话（最小动作 = 粘贴 `handoff.md` 提示词）
- 段 1 = 轮 1-3（契约层 + CogUnit + 状态机支路 A 闭环）；段 2 = 轮 4-6（工具续轮 + 并发 + 细节 + 全量回归）
- **每段结束自动交接**（AI 做，无需人工组织上下文）：
  1. 更新 `/home/zhengyp/work/A/checkpoint/status.md`（当前状态 + 已验证结论）
  2. 写 `/home/zhengyp/work/A/checkpoint/checkpoint-N.md`（本段已做修改 `文件:行` + 结论 + 遗留）
  3. 覆盖写 `/home/zhengyp/work/A/checkpoint/handoff.md`（下一段启动提示词，自包含）
  4. 把 `handoff.md` 全文作为最终回复输出给用户
- 人工动作 = 开新会话 + 粘贴 handoff 提示词（一句话恢复，路径用绝对路径，无歧义）
- 控 token 纪律：精准读（grep/read offset 读片段，勿全文重读设计文档与 lm_service 代码）、pytest `-q` 失败 `-x` 首败即停、分析 bug 先写小验证脚本/单测
- 停下点只有两类：① pytest gate 红（修到绿）② 3 个实施细节出现拿不准的设计分叉（question 问 YZ，不擅自定）
