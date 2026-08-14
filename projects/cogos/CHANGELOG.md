# CHANGELOG

- 2026-08-14 — Phase C 联调 3 bug 修复（`54394c4`）：补 patch 授权确认步 + admin-bot 幂等落盘可续 + 卡片 awaiting_patch 按钮。全量 377 passed 1 failed（残留 daemon 进程干扰，与改动无关）。
- 2026-08-13 — Phase A+C：卡片驱动 provider setup（A 阶段卡片模拟 + Phase C 卡片创建合一），bot-by-app-id 缓存自愈（`6e514fe`）。全量 372 tests。联调暴露 3 问题待修（缺 patch 授权 / 重试不可续 / 卡片无按钮），见 ISSUES.md。
- 2026-08-12 — provider 字段改造（`402ddf1`）：bot/human JSON 增加可选 `provider` 字段，bs-bot 必填；`/setup` 从 session.bot 读 provider。
- 2026-08-12 — Phase 1 Provider 搭建（`7b67561`）：`setup_provider`/`resume_provider` 编排（OAuth → scope → Bitable 7 表 → 注册）。
- 2026-08-12 — Phase 0 bs-bot 命令机制（`71abae9`）：`@msg_command` 框架 + `/setup` `/resume` `/help` 消息命令，daemon 自动扫描 bs-bot 激活 WS。
- 2026-08-12 — 通信层完整设计定稿（`656bcbd`）：`comm-full-design.md` + `comm-impl-plan.md`。
- 2026-08-12 — 通信层工具补齐：`purge-bot`（`0a2f4a6`）、toast 常量 + CLI 集成测试（`2eb5971`）、session.list stem 匹配修复（`afb3bf8`）、add_members member_id_type 修复 + 完整 `--help`（`04fa1db`）。
- 2026-08-11 — 通信层 Step 1-5（`9581082`/`2afeae0`/`8769f2b`）：bot 身份模型 + Session 持 bot dict + WSManager 集成 daemon + 群聊命令 + speak 增强（330 tests）。
- 2026-08-10~11 — G3f 卡片/Session 元数据：session meta + 撤回关联（`3ebd274`）+ 卡片消息 steps 1-9（send_card/send_patch/finish_card + cards/ 目录，326 tests）。
- 2026-08-09~10 — G3c/G3d/G3e：WS/Session 设计 + EventHandler 注册 + FileLock + listen.py + Entry dataclass + history/ 目录。
- 2026-08-07~08 — G1/G2/G3a/G3b：初始提交、环境管理（init/stop/reset/status/show-device-info）、commands 拆分、core.Lib（URL 命名空间 / OAuth create_bot / send）、secrets 类型系统（bot/human）、provider。
