# 2026-08-22 COGOS002 真机验证（从零建 provider + L1 群）

全新 provider COGOS002，脚本直调 `FeishuTelecomClient` 真机验证（不用 term）。checkpoint 移入 `projects/cogos/checkpoint/`。

## 进展

- 阶段 0-2：bs-bot + admin-bot + bitable + A0001~A0005 全激活（/add-agent ×5 + /activate ×5）
- 阶段 3 L1：A0001 建真群成 owner（chat_registry 落盘 owner），拉 A0002/A0003，members.json 落盘，startup 自建 tracker

## 修复（8 处，均真机暴露）

1. setup 写 bitable 计数器 `NameError: json_headers`（`bs_provider.py:219` 作用域缺失）→ 补定义
2. add-agent `name` 被飞书应用名覆盖（`bs_agent.py:347` `bot_name or name`）→ 删覆盖，保留用户输入 name
3. activate 拉群 `TypeError: Chat.add() missing 'bots'`（`bs_agent.py:679`）→ `chat.add([], [peer_bot])`
4. 本地 `status=init` 卡死 startup（`accounts.py:418 ensure` 本地命中 init 特判，主动 `_refresh()` 云同步，失败 fail-open）
5. get_members 只返回真人（`daemon.py:665`）→ bot 段走 tracker `agent_numbers()`
6. add_members 后 get_members 滞后（`daemon.py:706`）→ bot 段读前 `await tracker.rebuild()`
7. 已退群成员仍被返回（`tracker.py:286`）→ `agent_numbers()` 过滤 `last_event=="leave"`
8. /ENTER 公告缺失 → 新增 `_do_enter`（对称 `_do_leave`），add_members 成功后 `@all /ENTER <n>`

## 关键认知

- 进/退群事件走 `handler.py:41` → `feed_member_event` → tracker，不进 route_message（agent on_msg 收不到 system 消息）
- `im.chat.member.bot.added_v1` 只发给被拉 bot 自己的 app；owner 的 members.json 收敛唯一靠 rebuild history replay（`"{from_user} invited"`）
- `/LEAVE` 发送端在 `_do_leave`（退群者自公告）；`/ENTER` 本轮补上；`/REMOVE` 需真人校验（`get_human_by_user_id`）
- rebuild 权威来源 = history replay（system 消息 enter/leave）+ human snapshot（`list_members`），命令字参数只作信号/校验，不用于增删
- get_members 双源：human 走 API（`list_members` user_id → `_resolve_human`），bot 走 tracker；纯 bot 群 `list_members` 只含真人

## 遗留

- `test_bs_agent.py::test_full_flow` 断言 name 旧行为未同步（bug#2 删覆盖后）
- A0004 通信录未刷新（缺 A0005），留作 L4「使用中刷新通信录」素材
- 延后（需真人）：真人进/退群、真人发普通消息、`/REMOVE` 校验
