# Checkpoint 25 — phone 事件流实现（events.log）

## 当前问题

phone 可观测性第一步：只做事件记录（append `events.log`），不做 snapshot/tail 接口。YZ 拍板：观测 = 读盘，观察者直接看文件，snapshot()/tail() 缓做（YAGNI，无 Python 观察者消费者）。

## 已做修改

- `cogos/phone/store.py` — `PhoneStore.__init__` 加 `events_path` + `_next_seq = _scan_last_seq() + 1`；新增 `emit(type, **payload)` 与 `_scan_last_seq()`。record = `{**payload, "seq", "ts", "type"}`（payload 在前，seq/ts/type 权威覆盖），append ndjson 一行。
- `cogos/phone/model.py` — `Msg.read()` 落库后 `self._store.emit("read", chat_id=..., msg_seq=self._seq)`。
- `cogos/phone/phone.py` — 加 `_emit_event(type, **payload)`；`_append_msg` 返回值改为 `int`（新消息 index）；9 个事件点旁路 emit。
- `tests/phone/test_model.py` — `FakeStore` 加 `emit`（记录到 `events`）；`test_read_persists` 加 read 事件断言。

## 关键结论 / 决策

- **时间分层，不加标注**：事件 `ts` = 本地时钟 `int(time.time()*1000)`，语义"事件何时发生"，统一无歧义；飞书 `create_time` 只作 `payload.time` 原样携带（`sent.time or ""`），缺失留空、不 fallback 本地时间。排序权威靠 `seq`（单调持久化）。
- **seq 持久化**：store 初始化扫 `events.log` 末行 seq+1（O(n)，先正确后优化）。单 Phone 场景无并发问题。
- 事件 payload 字段按类型（见下）。

## 9 事件清单（payload 字段）

- `received`：`{card, chat_id, from, to, content, msg_seq, time}`（`_make_on_msg` 两分支）
- `sent`：`{card, chat_id, from_, to, content, msg_seq, time}`（`_send_p2p` / `_send_to_chat`，from_=发送卡）
- `read`：`{chat_id, msg_seq}`（`Msg.read()`；Msg 无 card 概念，卡由 chat 的 bound_card/number 推导）
- `members_changed`：`{card, chat_id, added[], removed[], members[]}`
- `group_created`：`{card, chat_id, title}`（`create_group`）
- `card_status`：`{card, status, reason}`（`add_card` 成功/失败 + `reconnect` 成功/失败）
- `disconnected`：`{card}`（`_make_on_disconnect`）
- `reconnected`：`{card}`（`reconnect` 成功）
- `error`：`{card, source, error}`（`sync_groups` 的 `list_chats` 失败；`_ensure_group_session` 的 `get_members` 失败时另带 `chat_id`）

## 验证

- 全量 `python3.11 -m pytest tests/ -q` → 642 passed。
- smoke：`PhoneStore.emit` ndjson 落盘、seq 跨重启续（1→2→3）、ts 为 int ms 单调。

## 遗留 / 坑

- 多进程 / 多 Phone 实例指向同一 `data_dir` 时 seq 会竞争（内存缓存 + 各自扫描），未处理。单 Phone 场景够用。
- `_scan_last_seq` 每次启动读全文件 O(n)，事件量大后需 offset 优化。
- read 事件无 `card` 字段（Msg 不知卡），观察者需从 chat 推导。已接受。
- 未决（与本任务无关）：get_members 首进群 30s 超时兜底排队（checkpoint-21/22）。
