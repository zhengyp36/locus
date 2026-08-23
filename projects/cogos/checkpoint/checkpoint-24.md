# Checkpoint 24 — phone 可观测性设计（讨论结论）

## 当前问题

phone 提供给 agent 使用时，三方需同时观察：agent（唯一使用者）、真人（终端）、AI 助手（非终端）。要求实时、只读、对 agent 无感。

## 关键结论 / 决策

1. **观测与使用解耦，观测 = 读盘**。store 落库（cards/contacts/chats 含 messages+read+members）已是天然观测面；观察者不 import Phone、不占连接，天然跨进程+只读+无感。
2. **实时性 = append-only 事件流 + fs 通知**（`events.log` ndjson + `tail -f`/inotify），**不做轮询**（实时/开销跷跷板），**不上 socket server 广播**（复杂度高、收益零）。业界对照：Kafka/WAL/CQRS/CDC。轮询退居最终兜底。ndjson 按行天然断点续读、多消费者各自 offset 互不干扰。
3. **观察对象 = agent 视角，非 phone 通信层**。开发关心 agent 行为时间线 `received → read → sent`，不是 telecom 帧。**已读 `read` 是 agent 行为**（`Msg.read()` model.py:99 落库），非观察者私有 offset——两个概念须拆开：agent 的 read（被观测）vs 观察者"已看到"游标（私有 offset）。
4. **分层**：phone 事件流 = 通信事实层，独立成立；agent 侧观察 = 行为语义层，待 agent 设计后再定。
5. **统一只读观察接口**：`snapshot()`（全量状态）+ `tail(since_seq)`（增量）。真人终端 = 常驻订阅（tmux/weechat/mutt 模型，会话切换+未读角标+只读导航命令），AI = 按需拉取（seq 断点）。

## phone 事件清单（9 个，从使用者视角）

- A 对话流：`received`（_make_on_msg phone.py:325）、`sent`（_send_p2p:253/_send_to_chat:282）、`read`（Msg.read() model.py:99）
- B 群结构：`members_changed`（phone.py:350）、`group_created`（create_group:413）
- C 连接健康：`card_status`（add_card:89/reconnect:426）、`disconnected`（phone.py:368）、`reconnected`（reconnect:426 成功）
- D 异常：`error`（sync_groups:299/_ensure_group_session:209）

每条事件字段：`seq`（单调递增）、`ts`、`type`，按类型带 `card`/`chat_id`/`from`/`to`/`content`/`msg_seq`。`connected` 不单列，由 `card_status(ok)` 表达。

## 下一步动手（/undo 后）

- Phone 加 `_emit_event(type, payload)`，在现有落库点旁路 append `data_dir/events.log`（ndjson）。
- 事件 writer 挂 `PhoneStore`（store 是 Phone 与 Msg 共享单例、落库收敛点）；`Msg.read()` 经 `self._store.emit(...)` 发事件；Phone `__init__` 注入 writer。
- 只读观察接口 `snapshot()` + `tail(since_seq)`。

## 遗留 / 坑

- 未决：get_members 首次进群同步拉成员 + 30s 超时兜底排队（checkpoint-21/22），与本任务无关。
- agent 侧行为事件（决策/状态机）待 agent 设计落地后再定。
