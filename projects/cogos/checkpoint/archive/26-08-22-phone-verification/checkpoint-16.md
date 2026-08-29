# Checkpoint 16 — 会话3 真机重验通过，收尾

> 本体 `~/codex/cogos`。会话3 脚本 `scripts/exp_verify_phone_members.py`。

## 结果

- 重启 daemon 加载 checkpoint-15 新代码（`systemctl --user start cogos-feishu-daemon`，active）。
- 重跑脚本 **ALL PASS**：
  - 场景18 本 bot 被拉进群 → members 增到含 A0002/A0003 ✅
  - 场景16 非 owner A0003 退群 → members 减 A0003，A0002(owner) 保留 ✅
- 群 `oc_dd285aa25d346f05807e1e89d238e567` 已 disband。
- 全量单测 **620 passed**（615 → 620，新增 leave/escape 用例）。

## 结论

checkpoint-15 的「发送者即事实」修复（`emit_member_leave`）真机验证正确，
/LEAVE 竞态已闭环。会话3 收尾。

## 环境

- daemon active（PID 34316），残留 `daemon.sock/pid/lock`、`monitor.pid/lock` 已清理。
- 历史残留群 `oc_0bfa...`、`oc_6ec...` 仍在（会话5 收尾）。
