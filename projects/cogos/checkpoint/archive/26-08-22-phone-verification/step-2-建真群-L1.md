# step-2 建真群 L1

> 阶段 3 真群验证之 L1：任意 agent 建真群 + 拉 bot 进群 + 进群感知落盘。
> 群主 A0001，成员 A0002/A0003。chat_id=`oc_8a18f62411072e504dd56cb675c5b63c`。

## 结果（通过）

1. **create_chat 成 owner** — A0001 `create_chat("verify")` 返回 chat_id，chat_registry bitable 落盘 `owner=COGOS002:A0001`（必测点 #1 全过）
2. **add_members 拉 bot 进群** — `add_members([A0002, A0003])` ack ok（必测点 #2 过）
3. **进群感知落盘** — A0002/A0003 各自 members.json 生成，agent 区含 enter 记录
4. **startup 自建 tracker** — A0001 重启后 `_build_group_trackers` 自动 build，members.json 完整含 A0001/A0002/A0003

## 关键发现（计划偏差 + 代码认知）

1. **进群感知不走 on_msg**：MemberAdded/MemberRemoved 走 `handler.py:41` → `feed_member_event` → tracker，不产生 agent message。计划 L1 "on_msg 收到进群 system 消息"断言**不成立**，正确断言是 members.json 落盘。
2. **get_members 纯 bot 群返回空**：`_handle_agent_get_members` 只回 human（`_resolve_human`），bot 成员注释"block 6"未实现。bot 成员观测点 = tracker 的 members.json。
3. **members.json 时序不一致**：A0002 build 时 A0003 尚未进群，故 A0002 缺 A0003；A0003 最后进群故完整。收敛靠后续 `/ENTER` 公告 rebuild（L4 话题）。

## 操作踩坑

1. **本地账号 status=init 拒 startup**：daemon `startup` 校验 `status=="init"` 拒绝。step-1 遗留"本地靠 refresh_agent_account 同步"在真机验证前必须先做：`refresh_agent_account("COGOS002", n)` 把 5 个账号同步成 active。
2. **daemon 内存缓存**：`AccountRef._cache` 进程级 15min TTL，改本地账号文件后 daemon 未过期仍读旧值，报"account not active"。解法：重启 daemon（`systemctl --user restart cogos-feishu-daemon`）。
3. **daemon 重启方式**：DAEMON_MODE=systemd，`systemctl --user restart cogos-feishu-daemon`；monitor 周期 120s 太慢，手动 restart 更快。

## 遗留

- 群 `oc_8a18f62411072e504dd56cb675c5b63c`（A0001/A0002/A0003 在群）留作 L2 收发验证现成群，无需再建。
- A0004 通信录未刷新（缺 A0005）继续留作 L4 素材。
- 延后项（真人进群/发言/`/REMOVE`）不涉及。
