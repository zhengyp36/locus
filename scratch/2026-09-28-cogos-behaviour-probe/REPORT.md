# 本轮任务执行报告：cogos 工具呈现行为观察（无外溢 harness）

- **日期**：2026-09-28
- **任务**：确认"模型参数名错 → help 自纠"是否每次都如此、有无其他行为（起于 S5 真身份 e2e 只见过一次）。
- **性质**：行为分布采样（非验收）。温度非确定 → 须 reps 聚合（方法教训见 `projects/cogos/entries/2026-09-14-cogos-compress-probe.md`）。
- **状态**：已收口。

## 1. 方法与理由

- 选**无外溢 harness**（真实模型 + `FakeTelecomClient`），不重复 S5 真身份：不发真实飞书消息、可脚本化、可跑 reps。
  - 对比被否方案：重复 S5 真身份 e2e——有真实外溢（会发消息给李恪）与计费，且组装繁琐。
- 触发句 = S5 原句：「你好，请用你的电脑能力，在你当前工作目录执行 cat E2E-S5.txt，然后把命令输出发回给我。」（发送者 `COGOS002:A0001`）。
- 每次运行建全新 agent 目录（fresh context），`work/E2E-S5.txt` 内容 `S5-REAL-E2E-OK`。
- 记录方式：包裹真实 `LmClient`，逐轮记录 chat 的 in/out（含模型 tool_calls、tool 结果、最终文本）；另收 FakeTelecom 的 `send` 调用。
- 装配直接复用 `Agent(agent_dir, client_factory=FakeTelecomClient, lm_client=..., work_dir=...)`；`on_message` 会 await 整轮结束，故 `deliver()` 返回即完成。

## 2. 执行过程

| 批次 | N | 结果 |
|---|---|---|
| batch1 | 3 | 全部干净 |
| batch2 | 10 | run 1–3 干净；run 4 半途（LM 挂）；run 5–10 全失败（LM 已挂） |
| batch3 | 10 | 全部干净 |

- **干净样本合计 n = 16**。
- **中途事故**：第一次起的 LM service 进程在 batch2 run4 前后**自行退出且无日志**（`server.py` 用 `print=lambda _: None`，无文件日志）。batch3 前重启后稳定跑完。
- LM 挂掉时的 agent 行为（非本次目标，但记录下来）：`cu failed: retryable` → consciousness 兜底自动回 `[出错] retryable`（0 次模型调用、1 条外发）。

## 3. 结果（干净样本 n=16）

| 指标 | 分布 |
|---|---|
| 首个工具调用 | `computer.command.run` 16/16（相对正确，无需 help） |
| 首调用前是否 help | 否 16/16 |
| 工具错次数 | 恰好 1 次 16/16 |
| 猜错的参数键 | `to` 16/16（应为 `target`） |
| help 深度 | 直达叶子 6/16；逐级下钻（group→face→leaf）10/16 |
| 外发消息条数 | 2 条 16/16 |

典型序列（每次必现）：

```
call computer.command.run {command: "cat E2E-S5.txt"}          # 正确
call communication.message.send {to: A0001, content: ...}      # 猜错 → 工具报错
help communication.message.send                                # 或先 help communication / communication.message
call communication.message.send {target: A0001, content: ...}  # 改对 → 成功
# 之后 consciousness 兜底又补发一条最终文本 → 共 2 条外发
```

工具错误原文（泄漏 Python 内部函数名）：

```
{"ok": false, "reason": "make_send_msg_spec.<locals>.fn() got an unexpected keyword argument 'to'"}
```

## 4. 发现的问题（未在本轮修，新增范围，待 YZ 裁）

1. **去重判断失效 → 每次重复外发**（bug）
   - 根因：`cogos/agent/consciousness.py:52` `if call["name"] == "send_msg": sent = True`。S3 起模型只调 `toolbox`，该判断恒假 → `sent` 永远 False → `_handle_done` 的"模型未回复"兜底补发最终文本。
   - 真身份佐证：S5 也是 2 条（`.../by_chat_id/oc_6ab7.../stream/20260928_112205_*message_sent` 与 `20260928_112206_*message_sent`）。
   - 倾向修法：按 `toolbox` 调用内层 `name == "communication.message.send"` 判，或在 registry 层记"是否发生过 send"。
2. **裸异常泄漏给模型**（体验/清晰度）
   - 根因：`toolbox._call` 把 args 当 kwargs 直透实现层，未知键 → Python `TypeError` 原文。
   - 倾向修法：调用边界按 `catalog.params` 校验，回结构化、模型面向的错误（"未知参数 to；本能力参数为 target/content"），顺带省掉一次 help 往返。

## 5. 建议与取向（待裁）

- 强倾向：调用边界按 catalog 校验参数 + 结构化错误（修问题 2）。
- 问题 1（去重判断）是明确回归，应修。
- **不采用**：模糊参数纠错 / 意图匹配 / 往总览加能力清单来"防猜"。执行须精确；"猜错 → 可读报错 → 一次自纠"就是正确形态，目标是让这条链便宜，而非消灭猜错。

## 6. 产物与提交

- harness：`/home/zhengyp/work/A/cogos/scripts/exp_agent_behaviour_probe.py`
  - cogos master `66bf679`（已 push `9183508..66bf679`）。
  - 用法：`LM_INTERNAL_KEY=<key> PROBE_OUT=<path> python3.11 scripts/exp_agent_behaviour_probe.py N`。
- 记忆层：`projects/cogos/entries/2026-09-28-cogos-toolbox-behaviour-probe.md`，并更新 `current.md` / `index.md` / `ISSUES.md`。
  - locus master `d267c47`（已 push `d0837d3..d267c47`）。
- 回归：`python3.11 -m pytest tests/agent` → **263 passed / 3 skipped**。

## 7. 证据与复现

- 结果数据（临时）：`/tmp/kilo/probe-result.json`（batch1）· `/tmp/kilo/probe-result-10.json`（batch2）· `/tmp/kilo/probe-result-10b.json`（batch3）。
- LM 真值：`/home/zhengyp/.cogos/lm-service/calls.jsonl`。
- S5 真值：`~/.cogos/feishu/default/run/sessions/cli_aa038cadbd38dcff/by_chat_id/oc_6ab7d61a4fbcd5595aa408a4b463121a/stream/20260928_*`。
- 复现步骤：
  1. 起服务：`cd /home/zhengyp/work/A/cogos && python3.11 -m cogos.lm_service.cli server`（127.0.0.1:11434，真 deepseek，key `ik_c47WkfAw7E5v6Ck8idMHgg`，账号尾号b111）。
  2. 跑 harness（见 §6 用法）。
  3. 若中途服务挂掉：重启后重跑；结果 JSON 会保留已完成的 run。

## 8. 遗留 / 边界

- 两个问题只记录未修（新增范围，停回讨论）。
- 只在 `communication.message.send` 上采样；`computer.command.run` / `file` / `web` 等未多跑，行为分布未知。
- 环境坑：LM service 会自行挂掉且无日志，跑 reps 前先确认端口。
- scratch 里旧的 `ENTRY.md` 已随收口移出（备份在 `/tmp/kilo/locus-scratch-removed-20260928/`）；本报告为该轮的正式过程记录。
