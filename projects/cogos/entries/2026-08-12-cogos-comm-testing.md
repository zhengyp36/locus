# CogOS 通信层（旧）

## 2026-08-12: 真实账号集成测试

已完成：
- 启动 daemon（manual 模式），陈梦瑶 bot 通过 lark_oapi 1.6.8 连上飞书 WS（`connected to wss://msg-frontier.feishu.cn`）
- `create-group` 建群 + 拉真实用户（YZ）✓
- `invite-members --id-type app_id` 拉其他 bot 入群 ✓（修复了 core.py add_members 把 member_id_type 错放在 JSON body 而非 query param 的 bug）
- `speak` 发消息 ✓
- `add-bot` / `list-bot` 管理 bot 连接 ✓
- `--help` 补齐了所有 23 个命令 DESCRIPTION

已解决：
- WS 事件路由 — 经 SDK 源码分析 + 实际验证，`register_p2_card_action_trigger` 与 `register_p2_customized_event` 互不冲突
- `TOAST_FAILED` 未定义 → 已补充 `TOAST_PROCESSING` / `TOAST_FAILED` 常量
- `session.list <bot_id>` 拿不到 session → `data.get("id")` 线上 JSON 无此字段，改为 `stem[4:]` 匹配
- 约定写入 `AGENTS.md`：bot 标识用文件名 stem，不用 JSON `name`
- `purge-bot` 移植自 agent-study/cogos-code → `cogos/feishu/purge.py`，MODE_DAEMON，清理 bot 所有群聊/Bitable

已建立的通用机制：
- `projects.md` 新增 `约定:` 字段指向工程 AGENTS.md
- 会话启动和话题切换时自动加载

关键锚点：
- bot_id 不可变（文件名 stem），name 可变（JSON 字段）
- Session 持 bot dict 取代 app_id
- WSManager 在 daemon 启动时自动恢复
- core.py `add_members`: `member_id_type` 是 query param，不是 body 字段
- SDK `_do_without_validation` 分发逻辑：先 `_callback_processor_map` 再 `_processorMap`
- `purge-bot`：新命令模块 `purge.py`
