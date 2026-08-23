# Checkpoint 15 — 会话3 成员变化：/LEAVE 竞态定位 + 修复落地（待真机重验）

> 本体 `~/codex/cogos`。会话3 脚本 `scripts/exp_verify_phone_members.py`（新跟踪）。
> 结论：场景18（members 增）真机通过；场景16（bot 退群 members 减）暴露 /LEAVE 竞态，
> 已按「发送者即事实」方案修复，单测绿，**待重启 daemon 后重跑脚本验证场景16**。

## 真机结果（改动前）

```
场景 18  A0002 建群 add A0001 → members=['A0001','A0002'] ✅（add A0003 后 = 3 人 ✅）
场景 16  A0002(owner) leave → 群解散，A0001 也被移出，members 不变 ❌
场景 16  A0003(非owner) leave → 群还在，但 members 仍含 A0003 ❌（timeout）
```

- 第一次：owner A0002 leave → 飞书解散整个群（cleanup 报 `232011 Operator can NOT
  be out of the chat`，A0001 已不在群）。故「owner leave」≠「成员减一」。
- 第二次：改用 A0003（非 owner）leave，群仍在，但 A0001 的 members 不减。

## 根因（/LEAVE 竞态）

`_do_leave`（`group_event.py:30`）顺序：**先 `send_text("/LEAVE X")` 公告，再
`leave_chat` API**。其他 bot 收到公告 → `_handle_leave` → `emit_members_changed`
立刻重拉权威列表，此时 X 还没真正退 → diff 为空 no-op；随后 X 真退，飞书只给 X
自己推 `bot.deleted_v1`，不给群内其他 bot 推事件，无二次触发。

日志佐证（`run/daemon.log`）：场景16 期间只有 A0003 自己 resolve 失败
（`232011 Operator can NOT be out of the chat`），A0001 无再次 resolve 记录。

## 方案（YZ 拍板：都修改，不记 ISSUE）

1. **收到 /LEAVE 即认为发送者 bot 退群（事件即事实）**，不再重拉。
   - 判断 `sender.type == "app"`（bot）才处理，真人（user）忽略。
   - 依据：真群 agent 发送会把 `/` 转义成 `//`，其他 bot 无法伪造单 `/` 命令；
     `/LEAVE` 后跟的 Axxx 仅可读性，不解析。
   - 风险（接受，不记 ISSUE）：公告后进程挂导致退群失败 → 误判；以及本地/服务器
     时钟倒挂时历史回放可能把错误 leave 态覆盖不回 enter。
2. **顺手修 group-p2p 发送侧不转义的不对称**：`_handle_agent_send_p2p` 对 AgentRef
   target 补 `escape_outgoing`（真群发送侧本来就有，group-p2p 走 send_p2p 漏了）。

## 代码改动

- `cogos/feishu/group_event.py` — `_handle_leave`：sender 非 app 直接 return；否则
  `_resolve_group_sender` 拿退群 bot 号码 → `conn.emit_member_leave(ref.key, chat_id)`。
- `cogos/feishu/agent_conn.py` — 新增 `emit_member_leave(number, chat_id)`：
  `tracker.add_event(short, "leave", now_ms)` + 快照剔除该 number + push
  `members_changed(removed=[该bot])`；快照里没有该 number 时只记 tracker 不 push。
- `cogos/feishu/daemon.py` — `_handle_agent_send_p2p` AgentRef 分支加
  `escape_outgoing`。
- 测试：
  - `tests/feishu/test_group_event.py` — leave 标记 sender / 真人忽略。
  - `tests/feishu/test_agent_conn.py` — 新增 `TestEmitMemberLeave`（2 用例）。
  - `tests/feishu/test_daemon.py` — send_p2p bot 转义 / 真人不转义（2 用例）。

## 验证

- 相关单测 `tests/feishu/{test_group_event,test_agent_conn,test_daemon}.py`
  **60 passed**。
- 全量单测未重跑（改动后仅跑了相关 3 文件）。

## 下一步（YZ 回退后继续）

1. 重启 daemon 加载新代码（当前 daemon/monitor 均 failed/stopped，见下）。
2. 重跑 `python3.11 scripts/exp_verify_phone_members.py` 验证场景16 真机通过。
3. 全量单测 `python3.11 -m pytest tests/`。

## 环境注意

- daemon/monitor 当前**都没在跑**：旧 daemon 33240 于 02:52:45 停；monitor 34113
  短暂起后 SIGTERM 停；daemon 34111 启动 8s 后因 SIGTERM 触发 `server.close()` →
  `serve_forever` 抛 `RuntimeError: server is closed`（daemon.py:92 未捕获该异常，
  属既有缺陷，非本次改动引入）。重启时注意别在启动瞬间再发 SIGTERM。
- 残留：`run/daemon.sock`、`daemon.pid`、`daemon.lock` 文件待清理。
- 飞书残留群：会话3 两次跑脚本各留/清了群；`oc_8550...` 已 disband。历史残留
  `oc_0bfa...`、`oc_6ec...` 仍在（会话5 收尾）。
