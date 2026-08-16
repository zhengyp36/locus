# 2026-08-16 — Telecom 通信接口抽象（面向对象重构，接口已定稿，编码待开始）

与 YZ 讨论后定稿，接口代码落在 `cogos/feishu/telecom.py`（已重写为 ABC + 占位实现，未接 daemon/term）。核心：把 agent↔daemon 通信从过程式（term.py 直接拼 proto JSON）重构为面向对象接口。

## 设计决策

- **Contact**（frozen）：`number` + `name`。`number` 只允许 provider 封闭域号码 `COGOS001:H0002 | COGOS001:A0001`（H=人 A=agent）；`name` 是代号，agent 可任意填，通信层回传时填权威真名。
- **Chat**（frozen）：`id` + `title`。P2P 和群都是会话；`id` opaque（群 `oc_xxx` | P2P 的 chat_id，飞书发送成功后返回且不变），agent 不 parse；`title` 群名，P2P 空。
- 关键坑：入站消息 sender 实际是 open_id（`ou_xxx`），不是 H 号。**open_id→H/A 号反查在通信层内部做**（`FeishuTelecomClient`/daemon 侧），接口出去的一定是 H/A 号；`@all`/@bot 解析不出的项在 `contact_to` 里跳过。
- 名字双层：出站时 number 权威、name 可忽略；入站 name 由通信层填，agent 自行转换。

## 接口（TelecomClient ABC）

- `startup() -> Contact`：连 daemon、验证号码+pin；成功返回核实后身份（name 权威），失败抛 `StartupError`。
- `send(target, msg, to_targets=None) -> None`：**非阻塞 fire-and-forget**，不返回 message_id；私聊 target=Contact、群聊 target=Chat；`to_targets` 群里 @ 的人。自己的消息靠回显回到消息流。
- `listen(on_msg, on_disconnect=None) -> None`：起 reader+heartbeat 后台 task 立即返回。
- `shutdown() -> None`：幂等。

## 回调

- `on_msg(chat, contact_from, msg, contact_to)`：async，逐条 await；**回显也走 on_msg**，agent 按 contact_from 判断是否自己（会话流连续显示）。
- `on_disconnect()`：连接断开时回调（对应现在 `sock.read() is None`）。

## 异常层次

`TelecomError` → `StartupError` / `SendError(reason, code)` / `ConnectionLost`。原则：错误抛异常，正常路径返回有意义值。`SendError` 只覆盖同步可检测错误（参数非法、目标无法解析）；异步投递失败靠回显状态体现，不再抛。

## 待编码（新会话）

- `FeishuTelecomClient` 实现四个方法，接现有 agent channel 协议。
- daemon 端发送路径同步支持 chat_id 目标（现在 `_handle_agent_send` 只收 H 号 p2p，群发不出去）。
- term.py 迁移到新接口，删掉手写 proto 拼装。
