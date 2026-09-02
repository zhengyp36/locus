# Agent 代码认知 + 实施状态

> 原文 codebase.md + status.md：`checkpoint/26-09-02-agent-cog-arch/`。本文是交接凝练版。

## 已实施（6 期，全量回归 856 passed，已推 origin/master）

1. 意识层第一期：身份认知（agent.json + profile.md + pin）→ 幂等装卡/建联系人 → ToolRegistry + send_msg → 接 LmClient 真实回复（oneshot 不续轮）→ 时间补齐。
2. 工具层第一期：work_dir 边界 + read_file/write_file/execute（路径逃逸/二进制/超时进程组 kill/截断）。
3. 工具层第二期：search(Brave)+fetch(Jina)，aiohttp 显式代理。
4. 工具层第三期：scratch 草稿纸（ScratchStore + scratch_write/read/list；写时复制：active/<id>.md 恒指最新，改写归档 history/<id>.<ts_ms>.md，scratch.json 计数器分配 id）。
5. edit_file + scratch_edit：精确字符串替换（old_string 唯一匹配，0/多/空串均报错），scratch_edit 同样走归档。
6. read 改行模式：read_file/scratch_read 加 offset(1起)/limit(默认500上限2000)，返回行号前缀 + total_lines + truncated(=还有后续行)，单行超 2000 截断。

## 包结构锚点

- `cogos/agent/`：message / config / perception / consciousness / tools / webtools / app。
- `consciousness.py` 当前 oneshot：组 system+user 调 chat，有 tool_calls 逐个执行仅日志，无则兜底 send_msg。
- `config.py`：load_agent_config / load_profile / init_phone（幂等）/ render_system_prompt。
- `tools.py`：ToolSpec + ToolRegistry；send_msg / read_file / write_file / edit_file / execute / search / fetch / scratch_write / scratch_read / scratch_edit / scratch_list。共享 `_apply_edit`（唯一替换）+ `_render_lines`（行渲染）。

## 关键坑

- add_card 不幂等（init_phone 显式判断）；消息 time 可能空（兜底「未知时间」）；LLM 可能不调工具（prompt 强制 + 兜底直发）；续轮需按消息隔离否则 tool_call id 对不上。

## 真实部署

- `~/.cogos/agent/tangyu/`（agent.json + memory/profile.md）。
- 启动：`cogos-feishu init` → lm-service server(127.0.0.1:11434) → `LM_INTERNAL_KEY=ik_... python3.11 -m cogos.agent.app --agent <dir>`。
- 唐钰 COGOS002:A0005，pin 967b6fa7；internal_key ik_c47WkfAw7E5v6Ck8idMHgg。

## 遗留（待讨论，不随手改）

- 无取消/抢占；并发共享状态无锁；oneshot 结果不回填（v2 解决）；同 sender 乱序；无并发节流。

## 下一步（terminal + timer 实施）

- 方案已定稿 `../cogos/docs/design-terminal-timer.md`：terminal（busy/idle + 游标读 buffer + killpg 中止 + 完成事件）+ timer（绝对时间戳 + 单调度循环 + timers.json 持久化）+ 事件回执通路（queue + consumer）。阶段 A terminal 先行、B timer 随后。
