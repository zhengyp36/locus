## cogos

- 路径: `~/codex/cogos`
- 描述: 多 agent 运行时。飞书作为通信总线和人-agent 交互面。
- 语言: Python 3.11
- 测试: `python3.11 -m pytest tests/ -q`（330 pass）
- 入口: `cogos-feishu <command>`

关键文件:
- `cogos/feishu/cli.py` — CLI 入口
- `cogos/feishu/session.py` — Session（持 bot dict）
- `cogos/feishu/daemon.py` — 后台进程
- `cogos/feishu/ws.py` — WebSocket 管理
- `cogos/feishu/config.py` — 配置

外部笔记:
- `~/codex/agent-study/discussions/project-tree.md` — 进度树
- `~/codex/agent-study/agent-study/cogos/comm/` — 设计文档

## agent-study

- 路径: `~/codex/agent-study`
- 描述: agent 设计学习工程
