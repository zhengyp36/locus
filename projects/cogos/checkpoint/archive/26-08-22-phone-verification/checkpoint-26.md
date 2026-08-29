# Checkpoint 26 — 事件流真机验证 + get_members 30s 超时待定位

## 当前问题

事件流真机验证通过（8 类事件全落盘）；但顺带复现 get_members RPC 30s 超时，30s 花在哪未定位，需专门分析。

## 已做修改

- 无代码改动（纯验证 + 分析）。
- 新建 `/tmp/kilo/verify_events.py`：observer=`COGOS002:A0002`（Phone 装卡），mover=`COGOS002:A0001`（独立 FeishuTelecomClient）。动作序列：add_card → create_group → add_members(A0001) → mover 群发言 → observer 群发 → observer p2p 发 → mover p2p 发 → read 一条 in 消息 → remove_members(A0001)。
- 启动 daemon（`systemctl --user start cogos-feishu-daemon`，原为 stopped，PID 38073）。

## 已读代码要点

- 超时链路：`_make_on_members_changed`（phone.py:380）/ `_make_on_msg`（phone.py:353）→ `_ensure_group_session`（phone.py:202）→ members 空时 `tchat.get_members()` → `_request(proto.agent.get_members)`（telecom.py:355-356）→ `wait_for(REQUEST_TIMEOUT=30.0)`（telecom.py:396）→ `TelecomError("request timed out: get_members")`（telecom.py:398）→ `_ensure_group_session` except 落 `members_error` + emit `error`（phone.py:219-229）。
- daemon 侧：agent socket 读循环单协程逐个 `await` handler（daemon.py:286-311）→ `_handle_agent_get_members`（daemon.py:659）→ `resolve_group_members`（agent_conn.py:291）= `list_members`（真人 HTTP）+ `tracker.rebuild()`（`_build_lock` 串行，tracker.py:139/146）+ `load_bot` name。
- tracker rebuild：`build()` → `_replay_history`（`list_messages` 历史回放 system 消息）+ `_snapshot_humans`（`list_members`）+ `_gc` + `_save`（tracker.py:115-147）。

## 关键结论 / 决策

- 事件流 8 类全落盘，字段符合 checkpoint-25 清单：card_status(1)/group_created(1)/error(1)/members_changed(2)/received(2)/sent(2)/read(1)。seq 单调连续 1→10，ts 全 int ms，重启后 `_next_seq=11` 续接正确。data_dir=`/tmp/kilo/evt_flow_phone/phone-data/events.log`。
- received/sent 的 p2p 与 group 两分支都测到；disconnected/reconnected 未测（需断 daemon）。

## 现象时间线（events.log ts，本地墙钟 ms；payload.time 为飞书 create_time）

| 时刻 | 事件 |
|---|---|
| 1787463987311 | group_created seq2 |
| 1787463999938 | mover 群发言 `payload.time`（飞书服务器） |
| 1787464027821 | error seq3 `get_members` 超时（比发言晚 ~28s） |
| 1787464027822 | members_changed seq4 `added=[A0001,A0002]` |
| 1787464027825 | received seq5 |
| 1787464027830 | sent seq6 |

- 消息帧被卡 ~28s；30s 硬超时；超时后 seq3/4/5/6 密集在 7821~830（9ms）批量释放。
- 自洽还原：add_members → members_changed 帧 → `_make_on_members_changed` → get_members #1 阻塞 30s → 超时 error → added 兜底写对 → 排队消息帧处理 → `_make_on_msg` 的 get_members #2 被 members 非空短路（故仅 1 个 error）。

## 遗留 / 坑（下一步专门分析）

- **核心待解：30s 花在哪**。候选阻塞点（从过程推测，未证实）：
  1. daemon agent socket 读循环单协程，get_members 请求排队等待前面 handler 完成。
  2. `resolve_group_members` → `tracker.rebuild()` 的 `_build_lock` 串行；若多个成员事件并发触发 rebuild，锁上排队累积。
  3. 单次 rebuild 实测 0.5s（checkpoint-22），单发不构成 30s → 需查是否有锁竞争或 HTTP 卡顿。
- 日志线索（13:47:29，非 observer）：`agent 'A0001' resolve members for 'oc_b150...' failed: list members failed: 232011 Operator can NOT be out of the chat` —— 这是 mover A0001 被 remove 出群后自己收到 bot.deleted_v1 → emit_members_changed → resolve 失败，与 A0002 超时无直接因果，但同属成员事件链路，分析时留意区分。
- A0002（observer）无 resolve failed 日志 → 其 resolve 是"卡住"而非"报错"，需加计时或对照日志确认卡在 list_members 还是 rebuild。
- 未决背景：checkpoint-21 归因「rebuild 回放>30s」被 checkpoint-22 推翻改「串行排队」，但本次更简单场景（单群+单 add+单消息）也稳定复现，根因仍未坐实。
