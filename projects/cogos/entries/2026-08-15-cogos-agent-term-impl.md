# 2026-08-15 — agent-term 架子实现 + 账号失效/刷新方案定稿

## term 架子实现（6 步，已提交 `5094ba8`）

按 agent-term-impl-plan.md 的「执行方式」工作流切分：主会话做 Step1（protocol）+ Step6（全量+复核），subagent A 做 Step2+3（daemon 长连接 + query_agent_fields），subagent B 做 Step4+5（agent_connect + term.py）。

- Step1 protocol.py：顶层 `channel` 路由 + `proto.agent` 命名空间（startup/startup-ack/hb-req/hb-ack/send/send-ack/message/shutdown + `_check_agent_type`）；`proto.ipc` 6 消息加 `channel:"cli"`、`proto.hb` 加 `channel:"monitor"`；`_check_ipc_type/_check_hb_type` 不校验 channel。
- Step2 daemon.py：`_handle_client` 按 channel 分派（cli/monitor/agent，close 责任下放）；`_agent_conns` 注册表 + `AGENT_HB_TIMEOUT=45`；`_verify_pin`（本地→云端回退）；`_handle_agent_client`（鉴权/踢旧/心跳超时/退出）；`_handle_agent_send`（裸 user_id 直发）。
- Step3 bs_agent.py：抽 `query_agent_fields(provider, number)` 纯函数，`query_agent` 改调它（对外行为不变）。
- Step4 client.py：`agent_connect()` 长连接（不 close）。
- Step5 term.py：`split_number` + `main()`（reader/heartbeat/stdin 三 task）；commands.py 注册 `term`（MODE_CLI）+ DESCRIPTION。
- 验证：全量 440 passed / 1 failed（test_workdir_switch 残留 daemon，与改动无关，已清理残留进程）。

## 鉴权方式讨论（方式1 → 方式2）

现状方式1 `_verify_pin` = 本地读 → 缺失回退云端。讨论后定方案为方式2 `ensure → verify`：`bs_agent.ensure_agent_account` 确保本地有（缺失/过期从云端拉取并刷新），返回账号 dict；`_verify_pin` 退化为纯 pin 比较。

理由：对齐 /resume 的「云端 source of truth、本地物化缓存」；物化本地账号是 agent-bot WS 激活的前置；verify 纯化。

## 失效方案定稿（docs/agent-account-refresh.md，未实现）

- 本地账号加 `expires_at`（墙钟），`AGENT_ACCOUNT_TTL = 12*3600`，`AGENT_REVALIDATE_COOLDOWN = 300`。
- refresh = merge：云端字段覆盖、本地专属字段（open_id/patch_granted/tenant/type/bot_type/id）保留；只成功才覆盖。
- 语义边界：网络错 → fail-open（不动本地、5min 重试）；云端确认 status!=active → fail-closed（落 status=inactive + 关连接）。
- 心跳重校验挂 hb-req 分支；同步拉取 30s 阻塞先接受，真机见延迟再拆 task。
- 待定：status 取值（现仅 active，补 inactive）；无 revoke 命令 → 只能 mock 单测，真机端到端缺验证路径；daemon 主动 shutdown 信号（最小=关 socket，term 收 EOF）。

## 关键字段/契约备忘

- channel 只作 daemon 顶层路由键，`_check_ipc_type/_check_hb_type` 不校验 channel。
- agent 长连接 close 责任在 `_handle_agent_client`，不进 `_handle_client` finally。
- 心跳超时用 `sock.read(timeout=AGENT_HB_TIMEOUT)` 实现，不单独起巡检 task。
- 本地账号 schema（add_agent 写）：id/name/type/bot_type/provider/tenant/app_id/app_secret/open_id/patch_granted/pin；云端 agent_registry 缺 open_id/tenant/type/bot_type。
