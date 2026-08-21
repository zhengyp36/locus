# 群实时事件公告（/ENTER /LEAVE /REMOVE + remove/leave 链路）

> 2026-08-22 会话。已实施（545 passed），真机未验证。已提交 `835bc3e`。依赖 tracker。

## 目的

让 agent-bot 及时感知群成员变化。飞书 bot 只能收到**自己**的进/退群事件，收不到其他 bot 的，需公告命令补盲；真人进/退直接从事件解析。

## 信息源（事件类型已区分）

- `im.chat.member.user.added/deleted_v1`：agent-bot 收到，affected_users=真人列表。
- `im.chat.member.bot.added/deleted_v1`：仅该 bot 自己收到，affected_users 空（= 自己）。

## 三条内部命令

| 命令 | 语义 | 发送者 |
|---|---|---|
| `/ENTER Axxxx` | bot 进群公告 | 刚进群的 bot 自己 |
| `/LEAVE Axxxx` | bot 离群公告 | 退群 bot 或真人移除后补发 |
| `/REMOVE Axxxx` | 真人移除 bot 请求 | 真人 |

- `/REMOVE`：所有 bot 收到不达 agent，目标 bot（number 匹配）发 `@all /LEAVE` + leave API 主动退群，其余静默等 /LEAVE。真人校验：`entry.sender` 是 user + `get_human_by_user_id` 命中，未注册静默丢弃。
- `/LEAVE` 发送者 ≠ 离群者，参数 Axxxx 是唯一锚点，接收方不看 sender。

## 核心架构决策

1. **members.json 写入收敛到 build**：/ENTER /LEAVE 接收方**不直接 add_event**，改触发 `tracker.rebuild()`（历史权威）；真人进/退事件保持 add_event 直写；bot 自己进/退事件 add_event 自己。
2. **退群四路径统一 `_do_leave`**：发 `@all /LEAVE <number>` 公告（单 `/` 不 escape）+ `Lib.leave_chat` 真正退群。
   - `Chat.leave`（自己退，不查身份）/ `Chat.remove_members`（群主，`get_chat_owner == self.key` 逐个）/ `/REMOVE`（真人校验 + 目标匹配）/ `/LEAVE`（接收方 rebuild）。

## 实施

- `group_event.py`（新建）：`register_group_event_commands()`（注册 ENTER/LEAVE/REMOVE，模块 import 时调用）+ `_do_leave(provider, number, chat_id)`（ensure account → `Session.send_text(f"/LEAVE {number}", at_users=["all"])` → `Lib.leave_chat`）+ `_parse_number`。只 import agent_cmd/accounts/session/core，无环。
- `protocol.py`：`remove_members`/`remove_members_ack`/`leave`/`leave_ack` 帧。
- `telecom.py`：`Chat.remove_members`/`Chat.leave` + `TelecomClient._remove_members`/`_leave` 抽象 + Feishu 实现 + `_ACK_TYPES` 加两 ack。
- `tracker.py`：`rebuild()`（asyncio.Lock 串行 + 复用 build）+ build 开头重置 `_last_create_time` + `last_updated` 只前进不倒退。
- `agent_cmd.py`：`dispatch_command(entry, conn=None)`，handler 签名 `(entry, conn=None)`。
- `daemon.py`：`_handle_agent_remove_members`（群主校验）/`_handle_agent_leave`（不查身份）+ 主循环分发 + import group_event。
- `handler.py`：命令分流传 `conn=manager.get_by_app_id(...)` + import group_event。

## 前提（真机已验证）

主动退群（`DELETE /im/v1/chats/{chat_id}/members`）产 `removed ... from this chat` system 消息（自己 removed 自己），任何进/退事件都在历史体现 → **build 是权威更新机制，公告/事件只是触发信号**。

## 测试

新增 `test_group_event.py`（_do_leave 发公告+leave / /REMOVE 真人校验 / /ENTER /LEAVE 触发 rebuild / Chat.remove_members 群主检查）+ protocol/telecom 帧断言。全量 **545 passed**。

## 遗留

- `/REMOVE` 目标 bot 离线 → 静默不保证成功；真人兜底 = 手动移出后发 `/LEAVE`。
- members.json per-bot 各自独立维护，事件+公告+build 最终收敛，不加权威源。
- 真机未验证、已提交 `835bc3e`。
