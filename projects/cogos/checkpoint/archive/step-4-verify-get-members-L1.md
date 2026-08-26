# step-4 verify get_members (L1-3/4)

> 验证 L1 的 get_members 收发群成员 + add_members 后再次 get_members。
> 发现并修复问题4：get_members 的 bot 段读缓存 tracker，add_members 后滞后。

## 验证结果

- 验证3（get_members 返回群成员）：**通过**。A0001 建群后 `get_members` 返回 `[A0001]`（自己）。
- 验证4（add_members 后 get_members 看到新成员）：**初始失败**，修复后通过。
  - 失败现象：`add_members([A0002])` ack ok，A0002 确已进群（`list_chats` 证实），但再次 `get_members` 仍只返回 `[A0001]`。
  - 修复后：建新群走完整 3-4 链路，`get_members` 立即返回 `[A0001, A0002]`，无需重启。

## 问题4 定位

- 链路：`_handle_agent_get_members`（daemon.py:665）bot 段读 `conn.get_tracker(chat_id).agent_numbers()`，即 A0001 的 members.json `agent` 区。
- 根因：A0001 建群时 `get_tracker` build 一次（agent 区只有 A0001）。`add_members` 拉 A0002 走 `Chat.add` → `lib.join_chat`（me_join，groupmgr.py:90），飞书 `im.chat.member.bot.added_v1` 事件只发给被拉 bot（A0002）自己的 app；`feed_member_event`（agent_conn.py:296）对 `is_bot` 只 `add_event(self.ref.number)` 更新 A0002 自己的 tracker。A0001 的 tracker 无任何 rebuild 触发，members.json 停留在 `['A0001']`。
- 佐证：重新 startup A0001 触发 `_build_group_trackers` rebuild（history replay 解析 "{from_user} invited" 补上 A0002）后，`get_members` 才返回 A0001+A0002。证实是 tracker 滞后，非 add_members 未生效。

## 修复

- `daemon.py:706` `_handle_agent_get_members` bot 段：`get_tracker` 后加 `await tracker.rebuild()`，再读 `agent_numbers()`。rebuild 内部有 `_build_lock` 防并发，异常 fail-open 返回空 bot 列表（原有 try 包裹不变）。

## 验证

- `py_compile` syntax OK。
- 现有群（A0002 已进群）`get_members` → `[A0001, A0002]`。
- 新建群完整链路：`get_members` → `[A0001]`；`add_members` → `get_members` → `[A0001, A0002]`。
- `test_daemon.py` 37 passed、`test_tracker.py` 15 passed；全量 548 passed, 1 failed（`test_bs_agent.py::TestAddAgent::test_full_flow`，step-1 遗留，与本次无关）。

## 遗留

- 测试群残留：`oc_31f0ed1d342265e38860efedab154b65`（verify-3-4）、`oc_58f9ec300adefc3ce254ef6dac005492`（verify-3-4b），均 A0001+A0002 在群，可留作 L2 素材或解散。
- `test_bs_agent.py::test_full_flow` 断言 `name` 旧行为（step-1 bug#2 删 bot_name 覆盖后未同步），待修正。
- 本地账号状态：A0001 active，A0002~A0005 init（A0002 add_members 时已云刷新回 active 本地文件，需复核实际 status）。
