# 2026-08-20 — load_bot vs AccountRef.ensure 分层

与 YZ 讨论：多处 `load_bot` 读 agent 账号，文件删了直接报错，应从云端兜底。结论是两者层次不同，不能一刀切替换。

## 两个 API 定位

- `load_bot(name_or_id)`：本地文件读取，同步，入参文件 id（`foo-A001` / `foo-ADMIN`），文件丢失抛 `FileNotFoundError`，无云端兜底、无 TTL。
- `AccountRef.ensure()`：账号解析，异步，memory→local→cloud→hard fail，入参 `provider:number`，云端兜底 + TTL，返回可用账号或 `{}`。

`AccountRef` 依赖 provider（要 `_load_admin` 拿 admin bitable_token 查云端），所以只能解析「有 provider + 在 registry 的 A/H 账号」。

## load_bot 调用点分类

该留（非 registry，云端无权威源）：
- `bs_agent.py:77` `_load_admin` → admin 账号
- `groupmgr.py`、`accounts.py:547` speak、`ws.py:264` — 通用 bot id / test bot
- bs bot（`{provider}-BS`）

该改（读 agent 账号，registry 有权威源）：
- `term.py:79` `_load_pin`（最典型，拿 pin）
- `bs_agent.py:511/770/888` `load_bot(agent_account_id(...))`

## 关键结论

- ensure 兜不了「本地特有字段」不是 ensure 缺陷，是设计债——本地不该有特有字段（见 account-refactor 篇）。
- 不能把 `bot-{id}` 反推 AccountRef：ADMIN 首字母 A 会被 `from_number` 误判 AgentRef。
- 根修法：本地文件退化为纯缓存（字段全可云端重建），则 agent 账号读取全走 ensure，load_bot 只服务 admin/bs/test。
