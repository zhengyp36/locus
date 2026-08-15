# CogOS — agent-term 方案定稿（term 脚手架 + agent 通信通道）

> 2026-08-15 会话。纯方案讨论，无代码。产出正式设计文档 `~/codex/cogos/docs/agent-term-design.md` + 函数级实施计划 `~/codex/cogos/docs/agent-term-impl-plan.md`（6 步：protocol → daemon → bs_agent 抽纯函数 → client → term.py → 全量测试）。

## 结论

- 新增 `cogos-feishu term <provider:number> <PIN>`，模拟 agent 用号码通信，是 agent 运行时的最小脚手架。
- **核心定位：daemon = agent 通信代理**。agent 进程（term 现在、真 agent 以后）只持号码 + PIN，经 unix socket 长连接接入 daemon；daemon 负责鉴权、激活 agent-bot WS、收发飞书消息、路由。这是整个方案成立的前提，决定后面 agent 运行时全走 daemon 中转、不自己直连飞书 WS。
- 兑现不变量 8（前缀 `COGOS001:A0003` → 内部裸号码）+ 不变量 5 的 startup PIN 鉴权。

## 协议：channel + type

- 顶层加 `channel`（cli / monitor / agent）作路由键，`type` 变通道内短命令字（连字符）。理由：daemon `_handle_client` 现在靠平铺 type 字符串分派，agent 进来会膨胀成 if-else 树；且三通道连接生命周期不同（cli/monitor 短连接、agent 长连接），channel 正好区分。
- JSON 键 snake_case，字段名对齐 bitable 列名（`number`/`pin`，不用 `No`/`PIN`）。
- 现有 cli/monitor 的 type 值不动，只加 channel，改动最小。

## 拍板

1. **PIN 鉴权**：本地 `bot-{number}.json` 命中即过，缺失回退云端 `agent_registry`（复用 `query_agent` 路径）。二者都实现，跨设备可通。
2. **单号码多连接**：新连接鉴权通过后踢旧连新（PIN 通过 = agent 自身行为）。
3. **send 用 user_id**：已验证 `speak --bot A0001 --human YZ` 成功，agent-bot 权限够，解除了 ISSUES 里"speak 用 user_id 需额外权限"的疑虑（至少对 agent-bot）。
4. **channel 拆分**：见上。

## 架子范围 vs 后置

- 本次：protocol（channel + agent 命名空间）、daemon（channel 分派 + `AgentConnections` 注册表 + `_handle_agent_client`）、client（`agent_connect`）、term.py + cli 注册、鉴权（本地→云端回退）。
- 后置留桩：agent-bot WS 激活 + `EventHandler.register("agent")`、`agent:message` 路由推送、`agent:send` 的 H 目标解析（`/add-human` 只写云端 human_registry，无本地 human 账号，H→user_id 解析天然依赖云端）。

## 易错点（实现时注意）

- `daemon._handle_client` 现有 `finally: sock.close()` 对 agent 长连接不适用，须把 close 责任下放到各 handler。
- `agent:send` 目标 `COGOS001:H2049` 的前缀解析：term 入口拆 provider:number，daemon 内部只用裸 number 定位账号。

## 新会话启动要求

开发放新会话（本会话仅讨论）。执行顺序：① 恢复记忆 → ② 读 project-map → ③ 读 `~/codex/cogos/docs/agent-term-design.md`（设计）→ ④ 读 `~/codex/cogos/docs/agent-term-impl-plan.md`（函数级实施计划）→ ⑤ 按 impl-plan 6 步开发。
