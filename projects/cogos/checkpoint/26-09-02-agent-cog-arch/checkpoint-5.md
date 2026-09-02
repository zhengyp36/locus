# checkpoint-5 — 意识层细化第一期实施 + 真实账号联调

> 按 `agent-impl-2.md` 完成身份认知 + 真实 LLM 回复，并用真实账号（唐钰 ↔ YZ）验证闭环。

## 已做修改

- `cogos/agent/config.py`（新增）— `ContactInfo`/`Profile`（含 `pin`）/`AgentConfig`；`load_agent_config`/`load_profile`/`init_phone`（幂等）/`render_system_prompt`。
- `cogos/agent/tools.py`（重构）— `ToolSpec` + `ToolRegistry` + `make_send_msg_spec`；`call` 捕获异常回 `{"ok":False,"reason"}`。
- `cogos/agent/consciousness.py`（改）— `Consciousness(registry, lm_client, profile, toolset_names)`，组 system+user 调 `chat`，执行 `tool_calls`，无 tool_calls 有 content 兜底直发 source。
- `cogos/agent/perception.py`（改）— `chat.history()[-1].time` 补消息时间。
- `cogos/agent/app.py`（改）— `Agent(agent_dir, client_factory=None, *, lm_client=None)` + `init()`/`start()`；`__main__` `--agent <dir>`。
- 测试：`tests/agent/conftest.py`（FakeLmClient + make_response）、`test_config.py`（新增）、`test_tools.py`/`test_consciousness.py`/`test_app.py`（重写）、`test_perception.py`（改）。

## 关键结论 / 坑

- **pin 缺口**：`agent-impl-2.md` 没提 pin，真实装卡需要 pin。补 `Profile.pin` 字段，`init_phone` 用 `profile.pin or "pin"`（fake 缺省 `"pin"`）。真实 pin 从 `~/.cogos/feishu/accounts/bot-COGOS002-A0005.json` 的 `pin` 取（`967b6fa7`）。
- **agent 目录独立**：agent 配置放 `~/.cogos/agent/tangyu/`（agent.json + memory/profile.md），phone.json 及 phone-data 自动生成在 `<phone_dir>/`，不混入 `~/.cogos/phone`。
- **daemon systemd unit 之前 failed**：`cogos-feishu init` 重跑后 daemon+monitor 恢复（systemctl 模式），ws 连接正常。
- **lm-service**：`python3.11 -m cogos.lm_service.cli server`（127.0.0.1:11434）；internal_key 用 `ik_c47WkfAw7E5v6Ck8idMHgg`（deepseek/尾号b111，真实 api_key）。

## 验证

- 全量回归 `python3.11 -m pytest tests/ -q` → 798 passed（无退化）。
- 真实联调：唐钰 `COGOS002:A0005` 卡 status=ok，ws `bot_type=agent` 连接；YZ（`COGOS002:H0002`）发「你好啊 / 你知道我是谁吗 / 介绍一下你自己」三轮，唐钰均以 `send_msg` 真实回复；另用 A0001 发「你好唐钰，测试一下」也回复成功。`calls.jsonl` 记录每次 `tool_calls=[send_msg]`，target 按来源回填。

## 遗留 / 坑

- 意识层 `on_message` 对工具结果只记日志，不整理/不续轮（oneshot 保持，符合本期边界）。
- 真实 agent 进程 stdout 块缓冲，诊断 print 非 tty 下不实时刷出（不影响功能）。
- 下一步：场、元层时钟、群聊、通讯录转名字展示。
