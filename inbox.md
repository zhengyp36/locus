# 交接：CogOS 工程当前状态（✅ 已处理 2026-08-12）

## 是什么

CogOS 是多 agent 运行时。飞书模块 = agent 间通信总线，提供：
- 持久化 bot 身份（daemon 持 bot 列表，独立于会话生命周期）
- 群聊作为通信信道
- speak 作为 agent 输出接口
- 命令式 CLI 管理

## 已完成（2026-08-11）

3 个 commit，330 tests pass（HEAD: `8769f2b`）。

| Step | 内容 | Commit |
|------|------|--------|
| 1+2 | bot 身份模型 + Session 重构 | `9581082` |
| 3+4 | WSManager 集成进 daemon + bot 命令 | `2afeae0` |
| 5 | 群聊命令 + speak 增强 | `8769f2b` |

可用命令：
```
init / stop / reset / status               # daemon
add-bot / remove-bot / list-bot            # bot 管理
watch-bot <id> [--chat-id <id>]            # 事件监听
speak --bot <id> (--msg | --card)          # 消息发送
create-group / invite-members / leave-group / destroy-group
```

### 关键设计决策

- bot_id 不可变（文件名 stem），name 可变（JSON 字段）
- Session 持 bot dict 取代 app_id
- WSManager 在 daemon 启动时自动恢复
- 信号处理支持异步 graceful shutdown

## 下一步（待讨论推进）

`~/codex/agent-study/discussions/project-tree.md` 中有完整 TODO。

优先级（来自实验 5 的 AI 独立评估）：
1. 调试验证（最小闭环跑通）
2. 可靠性 / 可观测性
3. 持久化
4. 认知树 + InferNode
5. agent 运行时
6. 权限

## 如何运行

```bash
cd ~/codex/cogos
python3.11 -m pytest tests/ -q              # 330 pass
python3.11 -m cogos.feishu.cli init         # 启动 daemon
python3.11 -m cogos.feishu.cli add-bot <id> # 添加 bot
```

## 外部笔记

- 进度树：`~/codex/agent-study/discussions/project-tree.md`
- 设计文档：`~/codex/agent-study/agent-study/cogos/comm/`
