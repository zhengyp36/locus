# cogos

多 agent 运行时，飞书作通信总线，前身 agent-study。通信层已真机调通。

- 已完成：agent-term、账号失效/刷新、AccountRef 号码解析、Telecom 通信接口（FeishuTelecomClient 四方法）；Phone 抽象已定稿待编码。
- 群操作（`eb68ceb`）：app 拉 app bot 被封（invite 230003），唯一路径 me_join（需 public 群）：建群 private→拉真人 user_id→改 public→各 bot me_join→改回 private。修 bug（`bfae959`）：invite-members 拉真人从未真正执行——`Chat.add` 按 `h.get('type')=='human'` 过滤但 human 账号无 type 字段恒空；改显式 humans/bots + `_add_humans` 先查证再重试 + `Lib.list_members`（分页）。
- agent-bot 创建（`8ab7420`）：status 写 init + 每 agent 建 Contact bitable。
- p2p 激活（`/activate <Axxx>`）：奇偶选群主建双 bot 群 + `@all /MEET` 收 open_id + 写 Contact bitable + 置 active；bot↔bot p2p 收发已落地（1624136）。
- contact-refresh（`608ecef`）：`/refresh-contact <Axxx>` 补齐更高号新激活 agent（连续区间，读对方 contact 查 chat_id）。
- bot 命名规范（`951c32a`）：admin `{provider}-ADMIN` / bs `{provider}-BS`（name 含 device_name）/ agent `{provider}-Axxxx`；删 S 计数器；bs_registry 字段 device/app_id/app_secret/status，setup/resume 后按 app_id 自检 upsert + 回填 tenant。
- sessions 目录整改：落盘改 `SESSIONS_DIR/<app_id>/by_chat_id/<chat_id>/`，叠加 p2p/group 软链接分类视图 + `providers/<provider>/<number>` 软链接；group-p2p 由 activate/refresh 收尾转 p2p 链；`sync-session-links` 命令随时补 providers 链。新增 `session_naming.py`、`session_links.py`、`accounts.get_human_by_user_id`/`list_bot_accounts`。
- bot 间消息发送：`AgentConn.make_session`（self.account 当 bot dict，弃 load_bot）+ `resolve_target`（目标缓存 20 FIFO key provider:number；H→user_id / A→自己 contact 查 chat_id）+ daemon `_handle_agent_send_p2p` 重写；接收 `route_message` 按 chat_type 分派（p2p→human、group-p2p→meta `peer_number`）；`_resolve_human` 本地优先。修 3 bug：chat_id 传裸号、human provider 校验、发送失败不断连。
- bot p2p 真机调通 + group-p2p 迁移修复（`32a2940`/`665ddda`）：老群（08-19 激活、早于 fix_group_p2p 落地）缺 `chat_type:group-p2p` + `peer_number` 元数据 → route_message 不路由、群错在 group/。修：新增 `sync-group-p2p` 命令（`_list_contact_rows` + `sync_group_p2p_links` 从 contact bitable 补 peer_number + 转 p2p 链）+ bot p2p 去 `@_all` 前缀（`_strip_at_all`，仅 group-p2p）→ entries/2026-08-20-cogos-p2p-debug.md
- 已实施 account refactor：删 agent 账号三字段（bitable_url/open_id/patch_granted）、bitable_token 改 `_ensure_contact_token` 按需重建、term `_load_pin` 改 `AgentRef.ensure`、`_configure_admin_bot` open_id 可空；追加修 `AgentRef._refresh` 补 bot_type/type/id/provider/tenant（否则 /resume 恢复的 agent 本地文件缺 bot_type，ws.add 失败）；真机验证 token 重建命中 `A0001-Contact` + startup OK；459 测试通过 → entries/2026-08-20-cogos-account-refactor-done.md
- 讨论中（未实施，待 YZ 定方向）：load_bot 与 AccountRef.ensure 分层错位（`_peer_chat_id` 读 peer token 仍 load_bot）→ entries/2026-08-20-cogos-load-bot-vs-ensure.md
- 待接：send_chat、to_targets @、OnMsg 返回 Chat、可 import 的 Python startup() API。

细节见锚点与 entries。

## 锚点

- 本体/约定/关键文件/设计决策/前身来源: projects/cogos/README.md
- 项目认知地图（目的轴 + 概念体系 + 状态轴 + 代码分层）: projects/cogos/entries/project-map.md
- 阶段记录: projects/cogos/CHANGELOG.md
- 遗留问题: projects/cogos/ISSUES.md
- 下一阶段方向: projects/cogos/ROADMAP.md
- 历史细节: projects/cogos/index.md → projects/cogos/entries/
