# cogos

多 agent 运行时。飞书作为通信总线和人-agent 交互面。

- remote: https://github.com/zhengyp36/cogos-dev
- 本体路径: `~/codex/cogos`
- 语言: Python 3.11（`.python-version` + `pyproject.toml` `requires-python = ">=3.11"`）
- 测试: `python3.11 -m pytest tests/ -q`
- 入口: `cogos-feishu <command>`（`python3.11 -m cogos.feishu.cli`）
- AI 开发由 locus 接管（cogos 仓库 AGENTS.md 已改为接管声明）

## 前身 / 来源

cogos 的前身是 `~/codex/agent-study/` 下的代码。agent-study 是"先学 agent 后开发 agent"的工程，cogos 是其中"开发 agent"的落点。

- `~/codex/agent-study/agent-study/agi-core/agi_body/feishu_gateway` — 飞书网关，用于 agent 通信（未完整实现）
- `~/codex/agent-study/agent-study/cogos/` — 前身工程（含旧设计文档 `comm/`）
- `~/codex/agent-study/cogos-code/` — 前身代码

## 关键文件

- `cogos/feishu/cli.py` — CLI 入口
- `cogos/feishu/session.py` — Session（持 bot dict）
- `cogos/feishu/daemon.py` — 后台进程
- `cogos/feishu/ws.py` — WebSocket 管理
- `cogos/feishu/config.py` — 配置
- 通信层/Provider: `bs_cmd.py` `bs_setup.py` `bs_provider.py` `bs_card.py` `bs_workspace.py` `bot_manifest.py` `bitable_helper.py` `provider.py` `accounts.py` `handler.py` `env.py` `purge.py`

## 关键设计决策

- bot_id 不可变（文件名 stem），name 可变（JSON 字段）
- Session 持 bot dict 取代 app_id
- WSManager 在 daemon 启动时自动恢复
- 信号处理支持异步 graceful shutdown
- bot/human JSON 增加可选 `provider` 字段，bs-bot 必填
- `core.py` `add_members`: `member_id_type` 是 query param（`params=`），不是 body（`json=`）
- 新增命令在 `cogos/feishu/commands.py` 的 `DESCRIPTION` 中补齐 help 文本（`@define` 注册后应出现在 `--help`）

## 外部文档

- 通信层完整设计: `~/codex/cogos/docs/comm-full-design.md`
- agent 账号失效/刷新: `docs/agent-account-refresh.md`（方案）+ `docs/agent-account-refresh-design.md`（详细设计）
- 实施计划: `~/codex/cogos/docs/comm-impl-plan.md`
- 进度树 / 完整 TODO: `~/codex/agent-study/discussions/project-tree.md`
- 早期卡片/Session 设计（08-10，疑被 comm 线取代）: `docs/G3f-card-design.md` `docs/ws-session-design.md` `docs/G3f-todo.md`
