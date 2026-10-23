# 任务：cu.material 改造 list[dict] → list[Message]（2026-10-23）

> 状态：**已完成**（2026-10-23）。
> 关联讨论：意识上下文持久化 + Message 类型（scratch/2026-10-22-runtime-redesign.md 的延伸，未收口到 entries）。

## 完成情况（2026-10-23）

- commit `2fcac25`（feat(cog-runtime): cu.material as Message list with meta.ts），16 files, +242/-123，**未 push**。
- 测试：定向 93 passed；全量 1356 passed, 6 skipped（较基线 1347 净增 9 = test_message.py 用例，无回归）。
- 关键不变量成立：`fake_client.calls[i]["messages"]` 断言未改，`to_lm_dict` 与改造前 dict 等价。

## 目标

把 `CogRuntime` 的 `cu.material` 从 `list[dict]`（＝ LmService internal-form 协议格式）改成 `list[Message]`（内部语义类型，带 `meta.ts` 时间戳），出站时转回 internal-form dict。**消息产生处记录时间戳**，为后续意识上下文落盘做准备。

## 已拍板决策（勿再纠结）

1. **彻底改，不做兼容层**：`cu(material=...)` 只接受 `list[Message]`；所有构造 material 的调用方和测试**全部适配成 Message**。
2. **类型命名**：`Message`（一条消息），`Meta`（元信息，`meta.ts`），不用 `Context`/`ts`。
3. **`meta` 不参与相等比较**（`field(compare=False)`），测试断言 runtime 产生的消息时忽略动态时间戳。
4. **`to_lm_dict` 输出必须与现有 internal-form dict 完全等价**——这是核心不变量：provider 层 `assemble_tool_messages` 和 `FakeLmClient` 断言都不受影响。
5. **`LmClient` 与 provider 层不动**（frozen contract）。

## 类型定义（新文件）

`cogos/cog_runtime/message.py`：

```python
from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class Meta:
    """消息元信息，ts = epoch seconds (UTC)，在消息产生处记录。"""
    ts: float | None = None


@dataclass
class Message:
    """内部对话消息（internal form 语义），meta 不参与相等比较。"""
    role: str
    content: str | list | dict | None = None
    tool_calls: list | None = None      # assistant
    tool_call_id: str | None = None     # tool
    reasoning: str | None = None
    meta: Meta | None = field(default=None, compare=False)

    def to_lm_dict(self) -> dict:
        """还原 internal-form dict（不含 meta），与改造前等价。"""
        out: dict = {"role": self.role}
        if self.content is not None:
            out["content"] = self.content
        if self.tool_calls is not None:
            out["tool_calls"] = self.tool_calls
        if self.tool_call_id is not None:
            out["tool_call_id"] = self.tool_call_id
        if self.reasoning is not None:
            out["reasoning"] = self.reasoning
        return out
```

要点：
- `content` 语义按 role 分层：system/user/assistant = `str`（纯文本）| `list`（多模态 parts）；tool = `dict`（`{ok, result}` 包装）。**不做归一**，出站原样透传。
- tool 的 `content` 保持 `dict`，`json.dumps` 在 provider 层 `_vendor_tool_message` 做，不在 Message 层做。
- `Meta.ts` 类型与 `Signal.at` 一致（float epoch seconds）。

## 改动清单（分文件）

### 1. `cogos/cog_runtime/message.py`（新）
如上。

### 2. `cogos/cog_runtime/__init__.py`
导出 `Message`、`Meta`，加入 `__all__`。

### 3. `cogos/cog_runtime/unit.py`
- `CogUnit.__init__` 增加两个内部属性并初始化为 `None`：`self._resp_ts = None`、`self._tool_results_ts = None`。
- `material` 类型注解改为 `list[Message]`（可选，建议改）。

### 4. `cogos/cog_runtime/runtime.py`（核心）
- 顶部 `import time`，`from .message import Message, Meta`。
- `cu()` 签名：`material: list[Message]`。
- **出站**（现 76-82 行）：`chat(messages=...)` 改为
  ```python
  cu._resp = await self._client.chat(
      messages=[m.to_lm_dict() for m in cu.material],
      ...
  )
  cu._resp_ts = time.time()   # assistant 消息产生时刻
  ```
  `cu._resp_ts` 记在 `await` 返回后**紧接着**。
- **入站/tool 结果**（现 111 行）：`cu._tool_results = await on_tool_call(...)` 之后紧接着 `cu._tool_results_ts = time.time()`。
- **构造 assistant/tool 消息**（现 120-135 行）改为：
  ```python
  assistant_msg = Message(
      role="assistant",
      tool_calls=tool_calls,
      content=content or None,
      reasoning=reasoning or None,
      meta=Meta(ts=cu._resp_ts),
  )
  cu.material.append(assistant_msg)
  for tc, res in zip(tool_calls, results):
      cu.material.append(Message(
          role="tool",
          tool_call_id=tc["id"],
          content=res,
          meta=Meta(ts=cu._tool_results_ts),
      ))
  ```

### 5. 调用方（构造 material 的 dict 字面量 → Message）

- `cogos/agent/consciousness.py`：
  - `_build_material`（170-190 行）内多处 `{"role": ..., "content": ...}` → `Message(role=..., content=...)`。
  - `_load`（108-112 行）同样。
  - `_handle_done`（207 行）`material.append({"role": "assistant", "content": result.content})` → `material.append(Message(role="assistant", content=result.content))`。
- `cogos/agent/app.py`：`self._context`（211-217 行）两条 dict → Message。
- `cogos/agent/runtime/stream.py`：`build_cu`（12-15 行）`{"role": entry.role, "content": entry.content}` → `Message(role=entry.role, content=entry.content)`。
- `cogos/experiment/selfdrive/loop.py`：所有构造 material 的 dict 字面量（`grep '"role":' cogos/experiment/selfdrive/loop.py`，约 531/532/633/699/718/721/735/750/765/768/782/812 行）→ Message；`on_done`（342 行）`mat.append({"role": "assistant", ...})` → Message。

调用方构造的 Message **不带 meta**（`ts=None`，落盘相关后续再填），保持最简。

### 6. 测试

- **构造 material 的 dict 字面量 → Message**：所有 `material=[{"role": ..., "content": ...}]`、`rt.cu(material=[...])` 里的 dict 改 `Message(role=..., content=...)`。
- **断言 material 元素是 dict → Message**：如 `assert material[0] == {"role": "user", "content": "hi"}` → `assert material[0] == Message(role="user", content="hi")`。因 `meta` `compare=False`，动态 ts 不干扰相等比较。
- **断言 `fake_client.calls[i]["messages"]` → 不改**：出站 `to_lm_dict` 还原 dict，与现有断言等价。
- 受影响测试文件：
  - `tests/cog_runtime/test_runtime.py`、`test_tool_loop.py`、`test_concurrency.py`、`test_lifecycle.py`、`test_contract.py`、`test_unit.py`
  - `tests/agent/test_consciousness.py`、`tests/agent/test_flow.py`
  - `tests/experiment/test_loop.py`
- **新增** `tests/cog_runtime/test_message.py`：覆盖
  - `to_lm_dict`：user/assistant/tool 三种 role 的字段还原正确、`meta` 不出现在输出、`content=None`/`tool_calls=None` 等缺省字段不出现。
  - `meta` 不参与相等比较：`Message(role="user", content="hi", meta=Meta(ts=1.0)) == Message(role="user", content="hi")`。
  - tool 消息 `content` 为 dict 时 `to_lm_dict` 原样透传（不 dumps）。

## 时间戳记录点（精确）

| 消息 | 记录点 | ts 来源 |
|---|---|---|
| assistant | `await self._client.chat(...)` 返回后 | `cu._resp_ts = time.time()` |
| tool | `await on_tool_call(...)` 返回后 | `cu._tool_results_ts = time.time()` |

同一轮多个 tool 消息共享 `_tool_results_ts`（微秒级差异无意义）。消息产生即记 ts，append 复用，无差值问题。

## 验收标准

```bash
python3.11 -m pytest tests/cog_runtime/ tests/agent/test_consciousness.py tests/agent/test_flow.py tests/experiment/test_loop.py -q
python3.11 -m pytest tests/ -q   # 全量无回归
```

关键不变量：`fake_client.calls[i]["messages"]` 的所有既有断言不改且通过 —— 证明 `to_lm_dict` 与改造前 dict 等价。

## 边界（本次不做）

- **不接线**：不改 app.py 的 sink/装配逻辑，只改 `_context` 字面量类型。
- **不落盘**：意识上下文落盘、版本号、`meta` 序列化到文件均属后续，本次只做类型改造。
- **不动 LmClient / provider / cog_ctx**（`cog_ctx/context.py` 是另一套 `text` 字段消息，与 cog_runtime 无关）。
- **不实现原子写、不做 dict→Message 兼容层**。

## 关键源码锚点

- `CogUnit`：`cogos/cog_runtime/unit.py:10`
- `_advance` 出站/构造：`cogos/cog_runtime/runtime.py:76`（chat）、`:111`（on_tool_call）、`:120-135`（assistant/tool 构造）
- `material` 现在是 internal-form dict，provider 转 vendor：`cogos/lm_service/providers/base.py` `assemble_tool_messages`
- `FakeLmClient` / `make_response`：`tests/cog_runtime/conftest.py`

## 完成（行为要求）

0. 开工即设 context watch 阈值 120K。
1. 编码后主动检视代码、修复发现的问题，跑全量测试直到通过。
2. 返回结果：改动文件清单、测试结果、遗留问题。
