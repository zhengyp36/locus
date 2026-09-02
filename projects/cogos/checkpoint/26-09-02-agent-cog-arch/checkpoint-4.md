# checkpoint-4 — agent 加真实入口并用真实账号联调

> 补 `app.py --real` 真实入口，用唐钰 `COGOS002:A0005` 联调，等 YP（`COGOS002:H0002`）发消息验证收发闭环。

## 当前问题

agent 架子只有 fake 入口，无法用真实账号跑「收到→回复」闭环。

## 已做修改

- `cogos/agent/app.py` — `main()` 支持 `--real [config_path]`；`_run_real` 用默认 `Phone`（`FeishuTelecomClient`）→ `phone.startup()` 恢复卡 → `Agent.start()` 挂 listen → `asyncio.Event().wait()` 挂住；`_default_config_path` 缺省 `~/.cogos/phone/default/phone.json`。默认（无参）仍走 `_run_fake`。

## 已读代码要点

- `docs/phone-usage.md:13-21` — 真实开机 `Phone()` + `add_card(number, pin)`，失败不抛异常查 `card.status`。
- `cogos/phone/term.py:374-382` — 真实入口范式：`Phone(config_path)` → `phone.startup()` 恢复卡 → `phone.listen(...)` → 挂住。
- `cogos/feishu/client.py:85-93` — `agent_connect()` 连 daemon unix socket；daemon 不在则 `startup` 失败。
- `cogos/feishu/cli.py:1-7` — `cogos-feishu init` 启动 daemon + monitor（systemctl）。

## 关键结论 / 决策

- 真实账号已就绪：卡 `COGOS002:A0005`（pin 已存，`status=ok`，default），daemon 启动后 ws `ws added for COGOS002-A0005 (bot_type=agent)`，说明 `FeishuTelecomClient.startup()` 连上。
- 回复仍是 echo 假回复（`consciousness._reply`），联调只验证收发闭环。

## 验证

- `python3.11 -m pytest tests/agent/ -q` → 9 passed（fake 路径未破坏）。
- 后台启动 `python3.11 -m cogos.agent.app --real`，卡 status=ok，daemon.log 出现 agent ws 连接。
- **闭环验证成功**：YP（`COGOS002:H0002`）发「你好」→ agent 收到（`in`，time 1788250347921）→ 约 1s 后 echo 回复「echo: 你好」（`out`，time 1788250348892），见 `phone-data/chats/COGOS002:H0002.json`。

## 遗留 / 坑

- 回复内容仍是假回复（echo），接 lm_service 是下一步。
- 进程 stdout 被块缓冲，`print` 诊断在非 tty 下不实时刷出（不影响功能）。
