# Checkpoint 21 — 会话5 真人进退群 + 收尾清理：全绿

> 本体 `~/codex/cogos`。checkpoint-8 最后一个批次。脚本
> `scripts/exp_verify_phone_human.py`（新跟踪）。

## 环境

- daemon 重启 active（`systemctl --user start cogos-feishu-daemon`，PID 36329）。
- 真人号：H0001=SL（user_id `5969bedf`）、H0002=YZ（user_id `125cf5a4`），均 active。
- 观察者 A0001（Phone 装卡），操作者 A0002（bot owner）。

## 场景17 结果（真人进退群，user 事件路径）

```
17-pre 观察者群会话落库   members=[]（初始空，见下「观察点」）
17a    真人进群 members 增 members=[A0001,A0002,H0001,H0002] ✅
17b    真人退群 members 减 members=[A0001,A0002,H0001]（H0002 消失）✅
```

- **进群**：bot `add_members` 拉真人 → 飞书 `user.added_v1` → members 增，验证通过。
- **退群**：YZ 在飞书 App 用 H0002 主动退群 → `user.deleted_v1` → members 减 H0002，验证通过。
- 群 `oc_2bcdf3231fbd5dea711bdfde7de77d8b` 已 disband。
- **summary: ALL PASS**。

## 关键结论

- 真人进退群与 bot 路径同源（`feed_member_event` → `emit_members_changed`），
  真机首次验证 `user.added_v1`/`user.deleted_v1` 正确驱动 members 增减。
- 飞书私群真人无法主动加入（无二维码/邀请 API），故「真人进群」用 bot 拉、
  「真人退群」用真人主动操作，两条都覆盖 user 事件路径。

## 观察点：get_members 兜底 RPC 真机超时（30s）

- 日志出现 `ensure_group_session pull members for '...' failed: request timed out: get_members`。
- 时序：`_make_on_members_changed` 先 `await _ensure_group_session`，后者见 members 空
  同步 `tchat.get_members()` RPC；daemon `resolve_group_members` 里 `tracker.rebuild()`
  历史回放（HTTP）在真机 >30s（REQUEST_TIMEOUT）→ 超时。之后 members_changed 帧的
  added 才被写入，members 最终正确。
- 影响：members 更新被拖慢 ~30s；正确性无碍（added 帧兜底）。属 checkpoint-18 已知
  「先正确后优化」的 get_members 兜底 + tracker.rebuild 开销，本次真机坐实。
- 优化方向（未实施）：`_make_on_members_changed` 已有 added/removed，可跳过
  `_ensure_group_session` 的 get_members 兜底（如加 `skip_pull` 参数），仅收群消息
  路径保留兜底。

## 收尾清理

- 残留群 disband：`oc_0bfa0de9221b695eceb0fec17f6d1d22` ✅、
  `oc_6ec8092dac297a9d5efbbdbcbd4f8aa7` ✅（owner=A0001 disband，其余 bot 报
  232009 已解散，预期）。
- phone 临时数据 `/tmp/kilo/e2e_phone*`（5 个目录）已清理。

## 遗留

- 会话 4 异常边界（21/23/25）真机可挑验，非必需（checkpoint-20 已代码层实施）。
- 全部 8 个批次（会话1~5）完成；未 commit 的代码改动累积到 checkpoint-18/20（list_chats
  RPC + 群 sync、异常感知/重连）。
