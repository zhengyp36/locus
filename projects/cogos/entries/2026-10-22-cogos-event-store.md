# 事件存储 EventStore + 渲染改造（2026-10-22）

## 结论（活跃）

事件模块 = agent 事件存储积木（与意识上下文同级），已落码 `edcfdab`（`event_store.py` + 渲染改造）+ `d686683`（顺带修 phone browse 墙钟漂移）。**写好自验、不接线**（运行时装配留整体就绪后）。

- 载体：`cogos/agent/event_store.py`（`EventStore`）+ `cogos/agent/events.py`（渲染重构为「每 kind 一个转换函数」+ `chat.message` 前缀 + `message_to_signal`）。

## 接口

- `emit(signal)`：同步非阻塞，锁内 append 一行 JSON 到 `pending.jsonl`（`{kind,payload,at}`）+ flush。
- `take_all() -> list[Signal]`：锁内 rename `pending → <epoch_ns>.jsonl`（防撞加后缀）→ 逐行 parse（坏行丢弃）→ 按 `at` 升序返回。
- `has_events() -> bool`：pending 存在且 size>0（心跳轮询靠它）。

## 已定决策

- **全同步 + `threading.Lock`**：`emit`/`take_all` 共用同一把锁，避免 rename 竞态丢行；单事件循环下同步天然不抢占，锁为防御未来线程化＋文档化。
- **编号文件时间戳命名** `<epoch_ns>.jsonl`：文件名 = 取走时刻；与事件自身 `at` 是两回事（排序用事件 `at`）。
- **原子写整体不实现**（普通写），遗留（`TmpFilePair` 后置）。
- **渲染归上下文组织层**：事件模块只 `emit/take_all/has_events`、返回结构化事件，不碰渲染；`render_signal(signal, name_for=None)` 按 kind 分发，人名/群名映射在渲染时做（实例不持 profile）。
- **通信消息经 `message_to_signal` 转 `chat.message` 事件**（改造自 Perception 直进 consciousness），未接线。

## 被否方案

- 单 JSON 数组存事件 → 否（追加须重写全文件，违背 append-only＋原子追加）。
- 逐事件单独接线 → 否，统一走 `SignalSink.emit`，把 sink 换成 `EventStore` 实例即全接好（一处装配改动）。

## 遗留

- 接线（sink→EventStore、`on_message` 改道）留整体就绪。
- Timer 补 remind `content` 字段单列。
- 掉电漏事件、历史事件文件过大：暂不考虑。
