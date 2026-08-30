# checkpoint-3 — cog-runtime 实施 · 段 1/2（轮 1-3）

> 状态：段 1 完成，支路 A 闭环绿。段 2（轮 4-6）待开新会话。
> 验证：`tests/cog_runtime/` 18 passed；全量 pytest 751 passed 无回归（733 → 751，净增 18）。

## 已做修改

- `cogos/cogos/cog_runtime/__init__.py`（新建）— 导出 `CogRuntime/CogUnit/Tier/CuResult 三态`
- `cogos/cogos/cog_runtime/types.py`（新建）— `Tier = Literal["basic","advanced"]`(types.py:4) + 三态 dataclass(types.py:8-18)
- `cogos/cogos/cog_runtime/unit.py`（新建）— `CogUnit`(unit.py:4)：纯数据 + 句柄 `wait/no_wait/interrupt/add_child`，`remove_child` 抛 `NotImplementedError`(unit.py:46)
- `cogos/cogos/cog_runtime/runtime.py`（新建）— `CogRuntime`(runtime.py:9)：`cu()`(runtime.py:22) / `_start`(runtime.py:37) / `_on_interrupt`(runtime.py:41) / `_advance`(runtime.py:46) / `_finish`(runtime.py:97)
- `cogos/tests/cog_runtime/conftest.py`（新建）— `FakeLmClient` + `fake_client`/`make_response` fixtures
- `cogos/tests/cog_runtime/test_contract.py`（新建）— 形状断言 + tier 透传 + 六类映射（7 用例）
- `cogos/tests/cog_runtime/test_unit.py`（新建）— CogUnit 句柄单测（5 用例）
- `cogos/tests/cog_runtime/test_runtime.py`（新建）— 支路 A 闭环 + interrupt（4 用例）

## 关键结论（段 2 依赖）

- **状态机**：`_advance` 为 `while True` 循环，入口统一 interrupt 检查点。稳定点四态：`pending`(return 等子) / `queued`(await sem) / `running`(await chat) / `tooling`(段2)。状态集合 `created/pending/queued/running/tooling/done`。
- **running 两阶段**：用 `cu._resp is None` 区分"未 chat / 已 chat"。chat 返回后 `continue` 回循环入口检查 interrupt，实现"结果回来在入口发现并丢弃"（协作式），避免引入非设计状态。
- **interrupt**：`interrupt(reason)` 只置位 + `_on_interrupt`；无活跃 `_advance_task`（created/pending）才 create_task 触发，活跃（queued/running/tooling）由 task 自己在循环入口检查。queued 态 interrupt 不 cancel，靠 acquire 返回后入口检查（shutdown 收尾归段 2 细节③）。
- **sem 持有**：acquire 成功后 `_holding_sem=True`，`_finish` 里 release（finally 块保证不泄漏）。
- **`_finish` 顺序**：设 `state=done` + `result` → `on_done` → release sem → `create_task(_advance(parent))` 通知父 → pop `_units` → `set done_event`。
- **六类映射**：`LmServiceError.category` → `str(category)` 存 `CuResultError.category`（str 类型，值 = ErrorCategory 字符串）。

## 遗留（段 2）

- `runtime.py:96` `tooling` 分支 `NotImplementedError` → 段 2 轮 4 实现工具续轮。
- 并发（`Semaphore(N)` 多 cu）+ 父子通知测试 → 段 2 轮 5（逻辑已就位，缺测试覆盖）。
- 3 个实施细节 → 段 2 轮 6：① 告知值注入格式(2.5) ② 父子 on_ready 装配完整示例 ③ shutdown 收尾等待策略。
