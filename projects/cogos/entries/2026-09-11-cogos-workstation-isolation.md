# 2026-09-11 工位隔离缺口（COGOS_HOME + 服务单例 owner）

关联：`ISSUES.md`「工位隔离缺口」、`tasks/task-5-loop-verify-timing.md`、`current.md`。

## 现象

工位 B 真机跑时"不同会话自起 lm-service / feishu 服务有问题"。根因：cogos 没有"工位 = 隔离运行环境"这一层——路径钉死 `~/.cogos`，包安装钉死 A。

## 两类耦合（证据）

1. **代码身份**：`pip show cogos` → editable `/home/zhengyp/work/A/cogos`（装在全局 `~/.local`，非 venv）。不在 B checkout 的 cwd 下 `import cogos` 会拿到 A 的代码。task-5 靠 `cd work/B/cogos-s2` 规避（已核验 import 到 B 自己的 `loop.py`），但是**隐式契约**，忘了就静默跑 A 代码。
2. **运行状态/服务**：路径硬编码 `~/.cogos` —— `feishu/config.py:10-12`、`lm_service/config.py:9`、`phone/term.py:394`、loop 的 agent-dir 默认值。feishu daemon + agent 是**单例**，两会话同时起会抢同一 `global.json` work-dir、`accounts/`、agent 绑定（`~/.cogos/agent/tangyu`）；与 S2/S3「work-dir 被切到 `default-xxxx`」同源。lm-service 的 host/port 可 env 配（`client.py:16-17`），但 secrets/state/recorder 仍共享（`calls.jsonl` 已 523MB、无上限）。

## 危害

- **当前不阻塞**：task-5 只跑 mock，不需要任何服务。
- **阻塞**：两边同时真机跑；"常驻"（服务需稳定 owner）。

## 解法（分层）

1. **立即（零改码）**：真机要服务时，B 指向 A 的 lm-service（env `LM_SERVICE_HOST/PORT`），不自起。
2. **短期（小改，最值）**：引入 `COGOS_HOME`（默认 `~/.cogos`）统一所有路径 → A 用 `~/.cogos`、B 用 `~/.cogos-b`；顺带消掉整个"串状态"缺陷族（workdir 切换、accounts 互踩）。
3. **代码身份**：每工位一个 venv，或死守"一律从 checkout cwd 跑"并写进规范。
4. **长期（架构）**：分清"服务 vs 工位"——lm-service / feishu 是**单例资源，唯一 owner + 稳定入口**，工位只做客户端。与"常驻"是同一件事。

## 备注

自包含、改动小、可用测试自动验收 → 适合当自驱回路的真实靶子（dogfood）。等 task-5 出来后再决定是否排入。
