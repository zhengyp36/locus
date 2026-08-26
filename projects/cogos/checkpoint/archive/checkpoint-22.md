# Checkpoint 22 — 30s get_members 超时归因修正

> 本体 `~/codex/cogos`。YZ 质疑 checkpoint-21 的「tracker.rebuild 历史回放 >30s」结论,
> 实测推翻之,重新归因。

## 实测数据（真机 daemon active，观察者 A0001）

- `get_members` RPC 全程 **2.73s**（1 member），非 30s。
- `list_messages` 全量回放（不带 start_time） **0.51s / 2 条**。
- `list_members` **0.36s / 0 items**。
- `fetch_token` 单次 0.23s；连打 10 次共 1.61s，**无限流**。

## 结论

- checkpoint-21 的「tracker.rebuild 历史回放（HTTP）在真机 >30s」是**错误归因**。
- HTTP 本身快、历史也少，单次 rebuild 不构成 30s。

## 重新归因（推测，未再实测复现）

30s = REQUEST_TIMEOUT，超时的根源更可能是**串行排队**而非单次回放慢：

1. daemon agent socket 读循环是单协程逐个 `await` 处理（`daemon.py:286-311`），
   `_handle_agent_get_members` 阻塞期间同连接后续请求全部排队。
2. `resolve_group_members` → `tracker.rebuild()` 内部 `_build_lock` 串行（tracker.py:139）。
3. 真人进退群会连发 `user.added_v1`/`user.deleted_v1`，每个都触发
   `emit_members_changed` → `resolve_group_members` → `rebuild()`；叠加 phone 侧
   `_ensure_group_session` 又发一次 get_members，多个 rebuild 在锁上排队，
   才可能累积到 30s。

## 待 YZ 裁决

- 是否要在真机复现并发成员事件下的 get_members 延迟（加计时代码/日志）。
- 优化方向不变（checkpoint-21 已记）：`_make_on_members_changed` 已有 added/removed，
  可跳过 `_ensure_group_session` 的 get_members 兜底。
