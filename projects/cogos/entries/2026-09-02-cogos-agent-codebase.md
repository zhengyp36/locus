# Agent 代码认知 + 实施状态

> 原文 codebase.md + status.md：`checkpoint/26-09-02-agent-cog-arch/`。本文是交接凝练版。

## 已实施（3 期，全量回归 832 passed，已推 origin/master）

1. 意识层第一期：身份认知（agent.json + profile.md + pin）→ 幂等装卡/建联系人 → ToolRegistry + send_msg → 接 LmClient 真实回复（oneshot 不续轮）→ 时间补齐。
2. 工具层第一期：work_dir 边界 + read_file/write_file/execute（路径逃逸/二进制/超时进程组 kill/截断）。
3. 工具层第二期：search(Brave)+fetch(Jina)，aiohttp 显式代理。

## 包结构锚点

- `cogos/agent/`：message / config / perception / consciousness / tools / webtools / app。
- `consciousness.py` 当前 oneshot：组 system+user 调 chat，有 tool_calls 逐个执行仅日志，无则兜底 send_msg。
- `config.py`：load_agent_config / load_profile / init_phone（幂等）/ render_system_prompt。
- `tools.py`：ToolSpec + ToolRegistry；make_send_msg / read_file / write_file / execute / search / fetch。

## 关键坑

- add_card 不幂等（init_phone 显式判断）；消息 time 可能空（兜底「未知时间」）；LLM 可能不调工具（prompt 强制 + 兜底直发）；续轮需按消息隔离否则 tool_call id 对不上。

## 真实部署

- `~/.cogos/agent/tangyu/`（agent.json + memory/profile.md）。
- 启动：`cogos-feishu init` → lm-service server(127.0.0.1:11434) → `LM_INTERNAL_KEY=ik_... python3.11 -m cogos.agent.app --agent <dir>`。
- 唐钰 COGOS002:A0005，pin 967b6fa7；internal_key ik_c47WkfAw7E5v6Ck8idMHgg。

## 遗留（待讨论，不随手改）

- 无取消/抢占；并发共享状态无锁；oneshot 结果不回填（v2 解决）；同 sender 乱序；无并发节流。

## 下一步（模拟 kilo code 实验）

- 先做能实现的部分；模拟 kilo code = 检验 v2 理论的实验（cu 循环/状态对象/脉络），不追求一次实现全部理论。
