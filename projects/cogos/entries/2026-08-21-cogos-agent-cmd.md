# 群命令机制 + add-ws 引用计数

> 2026-08-21 会话。已实施，真机验证未做。已提交 `835bc3e`。

## 问题

`refresh_contact` → `_collect_meet_openids` 先 `wsm.add(self_bot_id, on_event=...)`，但 `WSManager.add` 在 bot 已 active 时抛 `WSClientError("already active")` → `/refresh-contact` 失败、`@all /MEET` 探测失效。

## 方案一：add-ws 引用计数（连接生命周期）

- `WSManager.add(bot_id, on_event, persist=True, allow_duplicate=False)`：`allow_duplicate=True` 时已存在不报错、不覆盖 on_event，只 `refcount+=1`。
- `remove(bot_id)`：递减到 0 才 `_stop_client` + 写盘。多流程配对 add/remove，try/finally 保证异常路径也释放。

## 方案二：命令机制（事件分发）

- 命令只在群聊（飞书 `chat_type=="group"`），统一 `@all /cmd`。判定：单 `/` 开头 = 命令拦截；双 `//` 开头 = 普通消息去一个 `/`；非 `/` = 普通。
- 转义纯函数 `escape_outgoing(text)`（补 `/`）/`unescape_incoming(text)`（去 `/`），telecom↔daemon 边界各调一次。
- `agent_cmd.py`（新建）：命令注册表（**多 handler**，同命令字 list 追加，各 handler 用 chat_id 自过滤）+ `is_command`/`dispatch_command`/`parse_command` + escape/unescape + `strip_at_all` 迁移。未知命令静默丢弃（不达 agent 不回提示）。
- `_collect_meet_openids` 改注册临时 `/MEET` handler + `allow_duplicate=True`，收完 try/finally 注销。

## 已知取舍（有意）

- bot → human：bot 发以 `/` 开头普通文本会补成 `//`，真人看到多一个 `/`（真人无边界删）。
- human → bot：真人发 `/xxx` 普通文本要手动发 `//xxx`。
- 对 bot 友好（无感命令字）、对真人不友好，接受该取舍，不为体验破坏 @all 广播语义。

## 实施

- `agent_cmd.py` 新建；`ws.py` `_Entry` 加 refcount；`handler.py` `handle_agent` conn 判定前插 `is_command` 分流；`agent_conn.py` `route_message` strip 后 `unescape_incoming`；`daemon.py` 发送前 `escape_outgoing`；`bs_agent.py` `/MEET` handler 化。

## 测试

全量 **509 passed**（原 486）。

## 遗留

- 真机验证点未做（真群单 `/` 拦截、`//` 还原、refresh 时 agent 在跑 `/MEET` 仍生效）。
- refcount 极端交错不做额外防护（try/finally 已保证基本配对）。
