# body catalog 动态裁剪 + N2 启动校验 + 消息 ts 修复

> 状态：已落码（cogos commit `0c3c148`），全量 1363 passed。触发＝真实 LLM 验证 body＋debug 工具时发现「chat 组 no-phone 接线缺口」。

## 触发（真实 LLM 验证）

- 用 `--no-phone`（离线、无飞书 daemon）＋事件注入跑通 body 工具与 debug 工具，**判据全过**（副作用落盘、on_tool_call 痕迹、stream/events 可读、pause/resume 生效）。
- 验证暴露一个接线缺口：**无 phone 时 body catalog 仍暴露 chat 组能力，但其 impl 未接线**——模型会调用一个没有实现的能力，得到 unknown_tool。三处修复一起收口。

## 三处修复

### 1. body catalog 动态裁剪（`Catalog.available`）

- `make_body_spec` 加 `catalog` 参数：装配时传 `body_catalog.catalog.available(set(impl_registry.names()))`，**模型只见已接线的能力树**。
- `available(impl_names)`：丢 `impl` 不在 registry 的 capability、丢空掉的组、丢对应 note。省略 catalog 参数＝回退全量 body_catalog（测试用）。
- why：catalog 是「工具集的分类与用法」（能力全集），registry 是「实际接线的 impl」。无 phone 时 chat 组 impl 缺，全量 catalog 会「声明了却没实现」。

### 2. N2 启动校验（catalog↔registry fail-fast）

- 复用 09-28 toolbox 的 `Catalog.assert_bound`，搬到自驱 `assemble()`：启动时断言 body catalog 绑定的每个 impl 都在 `impl_registry.names()` 里，否则 fail-fast。
- `allow_missing` 显式放行**尚未 provision 的面**：`vision`/`web`/`time` 三组＋`chat`（仅 `phone_capability is None` 时）。其余必须全部接线。
- why：动态裁剪是「读侧兜底」（不暴露未接线），N2 是「写侧护栏」（接线与 catalog 声明强一致，漏接线当场炸而不是运行时 unknown_tool）。

### 3. 消息 ts 修复（birth + relay 补 `meta.ts`）

- `birth_context()`：system/user 两行补 `Meta(ts=now)`。
- `Decider._pull()`：事件注入的 user 消息补 `Meta(ts=signal.at)`（用**事件时间戳**，非注入时刻）。
- why：debug 工具靠 ts 定位（`since`/cursor/`tail`），birth 与 relay 消息缺 ts 会在这条虚拟时间线上「没时间戳」，按时间定位/对齐事件视角会漏或错位。

## 落码要点

- `catalog.py`：`Catalog.available(impl_names)` ＋ `notes` property。
- `body.py`：`make_body_spec(registry, session, *, catalog=None)`，catalog 缺省回退全量。
- `assemble.py`：装配完 `impl_registry` 后先 N2 `assert_bound`（allow_missing 按 provision 状态算），再 `make_body_spec(catalog=available(...))`；`birth_context` 补 ts。
- `decide.py`：`_pull` 事件消息补 `Meta(ts=signal.at)`。
- 测试 +3（`test_body` 帮助反映裁剪 / `test_catalog` available 语义 4 例 / `test_decide` 事件 ts）。

## 被否 / 未采用

- **手动维护「已接线能力清单」**：易漂移，N2 `assert_bound` 自动断言替代。
- **无 phone 时把 chat 组整个砍掉（特判）**：否，chat 能力本身有效，缺的只是 impl，用 allow_missing 表达「面未 provision」而非「能力不存在」。
- **全量 catalog 暴露 + 靠运行时 unknown_tool 报错**：否，模型看到会调用、调用才失败，坏在运行时；动态裁剪让模型看不到未接线能力。
