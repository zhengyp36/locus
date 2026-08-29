# Checkpoint 14 — 会话2 主动发送+建群+多卡：真机全绿

> 本体 `~/codex/cogos`。checkpoint-8 会话2 执行结果，脚本
> `scripts/exp_verify_phone_send.py`（新跟踪）。

## 环境

- daemon 在跑（systemd，pid 33240），COGOS002 5 bot 均 active。
- 装卡：COGOS002:A0001（李恪，default）+ A0002（元芳，第二卡）。
- 发送 target 用 A0001 而非 A0003 的原因（见下）。

## 结果（`scripts/exp_verify_phone_send.py`）

```
场景 12 phone.create_group  12a 落库 type=group ✅ / 12b title=send-group ✅ / 12c bound_card=A0001 ✅
场景 3  群发               3a 落 out ✅ / 3b from_=A0001 ✅
场景 5  多卡 from_number    5a 落 out ✅ / 5b from_=A0002(指定卡) ✅ / 5c to=A0001 ✅
```

- 新群 `oc_6c8fb7...` 已 disband 清理。
- **summary: ALL PASS**。

## 关键结论

- 场景 5 的 `from_number` 语义验证：`_send_p2p` 用 `_resolve_send_card(from_number)`
  选卡，落库 `from_=card.number` = 指定卡 A0002（而非 default A0001），`to`=target。
- 场景 12 `create_group` 落库 `bound_card`=default 卡、`type=group`、title=传入名。

## 场景 5 target 为何用 A0001（重要约束）

- `_activate_agent_setup_p2p_group`（`bs_agent.py:622`）只为**编号更低**的 agent
  建 dual-bot p2p group（`if idx >= self_idx: continue`）。
- 因此 A0002 的 contact 里只有 A0001，没有 A0003~A0005；A0002→A0003 发 p2p 会
  `resolve_target` 抛 "target has no reachable address"。
- 故多卡验证 target 用 A0001（A0002 唯一可达 peer），仍充分证明 from_number
  覆盖 default 卡。

## 遗留 / 后续

- checkpoint-8 剩会话 3/4/5：
  - 会话3 成员变化非常规路径（`exp_verify_phone_members.py`，场景 16/18）。
  - 会话4 异常/边界（场景 21/23/22/24/25）。
  - 会话5 人工（真人进退群 场景17 + 收尾清理残留群）。
