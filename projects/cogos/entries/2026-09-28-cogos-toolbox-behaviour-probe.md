# cogos 工具呈现行为观察：真实模型多跑（2026-09-28）

> 结论：无外溢 harness（真实 deepseek + FakeTelecom）复跑 S5 类触发，**16 次干净样本行为高度一致**；同时发现两个问题——**裸异常回给模型**、**每次重复外发一条**。

## 做了什么（why）

- 起因：S5 真身份 e2e 里模型"参数名错 → help 自纠"只见过一次，想确认是否每次都这样、有无其他行为 → 属**行为分布采样**（温度非确定，须 reps，见 `2026-09-14-cogos-compress-probe.md` 的方法教训）。
- 选**无外溢 harness**（而非重复 S5 真身份）：真实模型 + FakeTelecom，不发真实飞书消息、可脚本化、可跑 reps。
- harness：`../cogos/scripts/exp_agent_behaviour_probe.py`（已入库 `66bf679`，已 push）；用法 `LM_INTERNAL_KEY=… python3.11 scripts/exp_agent_behaviour_probe.py N`；触发句 = S5 原句「执行 cat E2E-S5.txt 并回复」。

## 观察结果（干净样本 n=16：batch1=3 / batch2 前 3 / batch3=10）

- **16/16 首调用前不 help**，直接 `call computer.command.run`（正确，从不猜错、从不需要 help）。
- **16/16 紧接着猜 `communication.message.send` 的参数用 `to`**（应为 `target`）→ 撞裸 Python TypeError → 靠 `help` 自纠 → 改对重发成功。
- **16/16 每跑恰好 1 次工具错**；错误文本 = `make_send_msg_spec.<locals>.fn() got an unexpected keyword argument 'to'`（Python 内部函数名泄漏）。
- help 深度两种，均出现：**直达叶子 6/16**（`help communication.message.send`）／**逐级下钻 10/16**（`help communication` → `.message` → `.message.send`，多 2 轮）。
- **16/16 外发 2 条**（模型自己 1 条 + 自动补发 1 条），见下"根因"。

## 两个问题（待 YZ 裁，未在本轮修）

1. **去重判断失效 → 每次重复外发**（bug）：`../cogos/cogos/agent/consciousness.py:52` 的 `if call["name"] == "send_msg": sent = True` 在 S3 暴露 `toolbox` 后恒假——模型实际调用 `toolbox`，`sent` 永远 False → `_handle_done` 的"模型未回复"兜底又补发一条最终文本。S5 真值也是 2 条（`~/.cogos/feishu/.../by_chat_id/oc_6ab7…/stream/20260928_112205_*message_sent` 与 `20260928_112206_*message_sent`）。
   - 倾向修法：按 `toolbox` 调用里 `name == "communication.message.send"` 判，或在 registry 层记"是否发生过 send"，而非在 consciousness 里解析名字。
2. **裸异常泄漏给模型**（体验/清晰度）：`_call` 把 args 当 kwargs 直透实现层，未知键 → Python TypeError 原文。倾向：调用边界按 `catalog.params` 校验，回结构化、模型面向的错误（"未知参数 to；本能力参数为 target/content"）。

## 建议（与 S5 讨论一致，待裁）

- 强倾向：调用边界按 catalog 校验参数 + 结构化错误（修 2，顺带省掉一次 help 往返）。
- 修 1（去重判断）是明确回归，应修。
- **不采用**：模糊参数纠错 / 意图匹配 / 往总览加能力清单来"防猜"——执行须精确；"猜错→可读报错→一次自纠"就是正确形态，目标是让这条链便宜。

## 环境坑（复现注意）

- LM service（`python3.11 -m cogos.lm_service.cli server`，`~/.cogos/lm-service`，真 deepseek，key `ik_c47WkfAw7E5v6Ck8idMHgg`，账号尾号b111）**会自行挂掉且无日志**（`server.py` `print=lambda _:None`）；中途挂掉时 agent 行为 = `cu failed retryable` → 自动回 `[出错] retryable`（0 次模型调用、1 条外发）。跑 reps 前先确认端口、挂了重启。
- 结论只在 `communication.message.send` 这一能力上采样；`computer.command.run`/`file`/`web` 等未跑多次。

## 证据

- harness（已入库）+ 结果 JSON（临时）`/tmp/kilo/probe-result*.json`（batch1/2/3）。
- LM `calls.jsonl`；S5 真值 `~/.cogos/feishu/default/run/sessions/cli_aa038cadbd38dcff/by_chat_id/oc_6ab7d61a4fbcd5595aa408a4b463121a/stream/20260928_*`。
- 回归：`python3.11 -m pytest tests/agent` → 263 passed / 3 skipped。
