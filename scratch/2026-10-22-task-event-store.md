# 任务：事件存储模块 EventStore + 渲染改造（2026-10-22）

> 状态：**已完成**（2026-10-22）。编码会话只读本文件即可开工，无需读讨论草稿。
> 关联：讨论草稿 `2026-10-22-runtime-redesign.md`（背景与 why，不必读）。

## 完成情况（2026-10-22）

- 交付物全部到位，接口/边界与冻结契约一致，未接线、未碰 impl 层、未实现原子写。
- commit `edcfdab`（feat(agent): add event store + per-kind event rendering）+ `d686683`（fix(agent): stabilize phone browse before-pagination boundary test），已推送 origin/master。
- 测试：定向 27 passed；全量 1347 passed, 6 skipped。
- 附带修复：全量验证时发现 `test_impl_phone.py::test_browse_before_paginates_older` 预存墙钟漂移（`_ms_ago` 两次取值），改单次 `base_ms` 基准，与事件模块无关。

## 目标

实现 agent 事件模块的**存/取/判** + **面向模型的渲染**。原则：**写好＋单测自验，不接线**（运行时装配留到整体就绪后）。

## 交付物

1. `cogos/agent/event_store.py`（新）— `EventStore`
2. `cogos/agent/events.py`（改造）— 渲染重构为「每 kind 一个转换函数」+ 补 `chat.message` 前缀 + 新增 `message_to_signal`
3. `tests/agent/test_event_store.py`（新）+ 扩展 `tests/agent/test_events.py`

## 接口规格

### EventStore（`cogos/agent/event_store.py`）

```python
from pathlib import Path
from cogos.agent.impl.base import Signal

class EventStore:
    """agent 事件存储：收到即落盘（append-only pending），原子取走进编号文件。

    单 agent 单实例（绑定 agent_root/events/）。全同步方法 + threading.Lock，
    锁内互斥 emit（append）与 take_all（rename），避免 rename 竞态丢行。
    """

    def __init__(self, root: Path) -> None:
        """root = <agent_root>/events/，不存在时创建。"""

    def emit(self, signal: Signal) -> None:
        """锁内 open(pending, 'a') 写一行 JSON（{kind, payload, at}）+ flush。
        同步、非阻塞语义（完成返回＝已落盘）。实现 SignalSink.emit 协议。"""

    def take_all(self) -> list[Signal]:
        """锁内：无事件返回 []；否则 rename(pending → root/<epoch_ns>.jsonl，
        目标已存在则加后缀防撞)，逐行 parse（坏行丢弃）→ 按 at 升序 → list[Signal]。"""

    def has_events(self) -> bool:
        """pending 文件存在且 size > 0。"""
```

要点：
- pending 文件 = `root/pending.jsonl`，JSON Lines（每行 `{"kind","payload","at"}`）。
- 编号文件命名 = 取走时刻的 `time.time_ns()`；rename 前若目标存在则追加后缀（如 `_1`）。
- 锁 = `threading.Lock`，`emit` 与 `take_all` 共用。
- **不实现原子写**（普通写即可，TmpFilePair 遗留）。

### 渲染（`cogos/agent/events.py` 改造）

```python
_EVENT_PREFIX = {
    # 现有 7 条保持不变（term.done/term.notify/timer.notify/web.*/phone.*）
    ...,
    "chat.message": "communication.message",   # 新增
}

def message_to_signal(msg: IncomingMessage, at: float) -> Signal:
    """通信消息转事件：kind="chat.message"，
    payload = {source, chat_type, content, time, attachments}。
    人名/群名映射不在这里做（原样存号码）。"""

def render_signal(signal: Signal, *, name_for=None) -> str:
    """按 kind 分发到 _render_<kind>(payload, at, name_for)。
    输出 `[<类别前缀>] k=v ...`（at 渲染为 `at=<epoch秒>` 字段）。"""

def _render_<kind>(payload: dict, at: float, name_for=None) -> str:
    """每种事件一个转换函数。chat.message 用 name_for 做号码→人名映射，
    name_for=None 时原样输出号码。"""
```

要点：
- 现有 `AgentEvent` + `render_event(AgentEvent)` 签名**保持向后兼容**（现有 `tests/agent/test_events.py` 与 `app.py` 不坏），内部重构为复用上述转换函数（at 缺省 None）。
- `_EVENT_PREFIX` 的 term 特判（`session_id`→`session="t3"` 对象索引）保留在对应转换函数内。

## 已拍板决策

1. 方法**全同步 + threading.Lock**。
2. 编号文件**时间戳命名** `<epoch_ns>.jsonl`（防撞加后缀）。
3. **原子写整体不实现**（普通写），遗留。
4. **写好自验、不接线**。

## 边界（本次不做）

- **不接线**：不改 `app.py` 的 sink 装配、不改 `perception.py::_handle` 的 `_on_message` 调用。
- **不碰 impl 层**：Timer 补 content 字段单列，本次不做。
- **不实现原子写**（TmpFilePair 遗留）。

## 关键源码锚点

- `Signal` 定义：`cogos/agent/impl/base.py:13`
- 现有 `render_event`/`_EVENT_PREFIX`：`cogos/agent/events.py:10-48`
- `IncomingMessage`：`cogos/agent/message.py:8-16`
- `Perception._handle`（通信消息来源，仅参考、不改）：`cogos/agent/perception.py:16-41`
- sink 装配（仅参考、不改）：`cogos/agent/app.py:128-142`、`:159-160`
- 现有事件渲染测试（须保持通过）：`tests/agent/test_events.py`

## 验收标准

```bash
python3.11 -m pytest tests/agent/test_event_store.py tests/agent/test_events.py tests/agent/test_message.py -q
python3.11 -m pytest tests/ -q   # 全量无回归
```

测试须覆盖：
- `EventStore.emit` 落盘一行 JSON、`has_events` 判非空、`take_all` 取走（rename 后 pending 清空）+ 按 `at` 排序。
- `emit`/`take_all` 并发（多线程 emit 不丢行）。
- `message_to_signal` 字段正确（source/content/time/attachments 进 payload）。
- `render_signal` 每 kind 前缀正确、`at` 进输出、`chat.message` 前缀 + `name_for` 号码→人名映射。

## 完成（行为要求）

0. 开工即设 **context watch 阈值 120K**（context 监测，防被动停）。
1. 编码后**主动检视代码**、修复发现的问题，跑全量测试直到通过。
2. 返回结果（不要自行接线、不要碰 impl 层）：改动文件清单、测试结果、遗留问题。
