# cogos

多 agent 运行时，飞书作通信总线，前身 agent-study。通信层已真机调通。

- 已完成：agent-term、账号失效/刷新、AccountRef 号码解析、Telecom 通信接口（FeishuTelecomClient 四方法）；Phone 抽象已定稿待编码。
- 群操作（`eb68ceb`）：app 拉 app bot 被封（invite 230003），唯一路径 me_join（需 public 群）：建群 private→拉真人 user_id→改 public→各 bot me_join→改回 private。
- agent-bot 创建（`8ab7420`）：status 写 init + 每 agent 建 Contact bitable。
- p2p 激活（`/activate <Axxx>`）：奇偶选群主建双 bot 群 + `@all /MEET` 收 open_id + 写 Contact bitable + 置 active；bot↔bot p2p 收发已落地（1624136）。
- contact-refresh（`608ecef`）：`/refresh-contact <Axxx>` 补齐更高号新激活 agent（连续区间，读对方 contact 查 chat_id）。
- bot 命名规范（`951c32a`）：admin `{provider}-ADMIN` / bs `{provider}-BS`（name 含 device_name）/ agent `{provider}-Axxxx`；删 S 计数器；bs_registry 字段 device/app_id/app_secret/status，setup/resume 后按 app_id 自检 upsert + 回填 tenant。
- sessions 目录整改：落盘改 `SESSIONS_DIR/<app_id>/by_chat_id/<chat_id>/`，叠加 p2p/group 软链接分类视图 + `providers/<provider>/<number>` 软链接；group-p2p 由 activate/refresh 收尾转 p2p 链；`sync-session-links` 命令随时补 providers 链。新增 `session_naming.py`、`session_links.py`、`accounts.get_human_by_user_id`/`list_bot_accounts`。
- 待接：agent 目标 open_id、OnMsg 返回 Chat、send_chat、to_targets @。

细节见锚点与 entries。

## 锚点

- 本体/约定/关键文件/设计决策/前身来源: projects/cogos/README.md
- 项目认知地图（目的轴 + 概念体系 + 状态轴 + 代码分层）: projects/cogos/entries/project-map.md
- 阶段记录: projects/cogos/CHANGELOG.md
- 遗留问题: projects/cogos/ISSUES.md
- 下一阶段方向: projects/cogos/ROADMAP.md
- 历史细节: projects/cogos/index.md → projects/cogos/entries/
