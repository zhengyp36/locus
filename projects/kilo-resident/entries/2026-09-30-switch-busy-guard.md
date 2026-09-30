# 2026-09-30 · /new /pin 忙碌保护（在途回复不再静默丢）

## 结论

`/new`、`/pin` 加忙碌保护：`rt.busy || rt.inflight` 时拒绝切换，回「当前正忙，等这轮结束再切」（对齐 `/compact`）。`switchSession` 加防御性 warn：发现 live inflight 即打日志，把"静默丢"变"有声"。

本体 `../kilo-resident` 提交 `7bfcd0a`（feat/kilo-phone，已 push）；新增 `test:switch-busy-guard`（stub runtime，无 daemon 单测）。bridge 已 `bridge-restart` 部署，`kilo serve` 未动。

## 根因

`switchSession` 无条件 `rt.inflight = undefined; rt.busy = false` 并把 runtime 重键到新 session。模型还在生成时切会话 → 旧 session 完成时 `runtimes.get(oldId)` 已空，`resolveReply` 无人认领 → 回复静默丢。实证：KILO-DOCTOR 08:30:56 的 doctor 消息被 08:33:12 的 `/new` 丢弃，回复 08:33:41 才在旧会话完成。

## why（关键判断）

- **`/new` 的保护必须在 `createSession` 之前**：否则拒绝时泄漏一个空 session。
- **保护后所有 `switchSession` 调用点都在 turn boundary**：handoff 走 `pendingSwitch` 延迟到 idle；autoHandoff 在 idle 后；`/new` `/pin` 被拒。`busy=true, inflight=undefined` 窗口（无 chatId 的通知 wake、autoHandoff 进行中）同样被拒——此时 session 确在干活，拒是对的。

## 被否方案

- **补发已完成回复**（becameIdle 发现 inflight 会话已切时补发到原 chatId）：被否。保护补上后该路径不可达；为它维护孤儿 inflight 追踪 + 旧会话 resolveReply + 超时清理，复杂度换不到收益。防御性 warn 足以暴露未来回归。

## 已知 trade-off

若 idle 事件在事件流重连间隙丢失，`busy` 会卡在 true → `/new` `/pin`（及既有的 `/compact`、消息注入）永久被拒。这是**既有系统性特性**（busy 标志信任事件流），非本次回归；此前 `/new` `/pin` 能当逃生口恰恰是靠静默丢回复。逃生口 = `ctrl-kilo bridge-restart`（busy 标志随进程重建清零）。
