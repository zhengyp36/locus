# step-1 setup COGOS002

> 建 bs-bot + admin-bot + bitable + 5 个 agent-bot，修复 setup/add-agent/activate 三个 bug。

## 阶段进度

- 阶段 0：bs-bot 已建，WS 激活（daemon.log `ws added for COGOS002-BS (bot_type=bs)`）
- 阶段 1：/setup 建 admin-bot + bitable（含修复 bug#1）
- 阶段 2：/add-agent × 5 + /activate × 5，A0001~A0005 全部激活完成（含修复 bug#2、bug#3）

### 通信录状态（activate 后）

- 规则：新 bot 激活时已与所有 lower peers 建立通信录；已有 bot 需在新 bot 出现后手动 refresh 才补齐。无自动触发。
- A0001/A0002/A0003：contact.json 完整含 A0005，`max_active_number=A0005`（已手动 refresh）
- A0004：缺 A0005，`max_active_number=A0004`（**唯一未刷新**，留作「使用中刷新通信录」验证素材）
- A0005：完整（最后激活，collect 时天然收全 lower peers，无需刷新）

## 发现并修复的问题

### bug#1 setup 写计数器 NameError（bs_provider.py）

- 现象：daemon.log `setup provider failed`，traceback 指向 `_create_bitable_with_schema` 第 219 行 `NameError: name 'json_headers' is not defined`
- 定位：bitable app + 7 表已建成，卡在写 `COUNTER_RECORDS` 这步；`json_headers` 只在 `_create_table`（252 行）内定义，本函数作用域缺失
- 修复：`_create_bitable_with_schema` 内补 `json_headers = {"Content-Type": "application/json; charset=utf-8"}`（218 行后）

### bug#2 add-agent name 被飞书应用名覆盖（bs_agent.py）

- 现象：`bot-COGOS002-A0001.json` 的 `name` = `"李恪(A0001)"`，应为 `"李恪"`
- 定位：链路 `bs_setup.py:124` name="李恪" → `bs_agent.py:325` 初次存纯 name → `on_url`（317 行）提示把飞书应用命名「李恪(A0001)」→ `_configure_admin_bot` 读回 app_name="李恪(A0001)"（bs_provider.py:149）→ `bs_agent.py:350` `{"name": bot_name or name}` 覆盖成带号码
- 根因：`_configure_admin_bot` 返回的 `bot_name`（飞书应用名，故意带号码以便后台区分）不该覆盖账号 `name`
- 修复：删除 `bot_name` 覆盖（347、349-351 行），`name` 保留用户输入值
- 数据修正：4 个账号 json 的 name 去括号号码后缀，现为 李恪/元芳/剑平/陈留

### bug#3 activate 拉群 Chat.add 缺参数（bs_agent.py）

- 现象：`/activate A0002` 报内部错误，daemon.log `TypeError: Chat.add() missing 1 required positional argument: 'bots'`
- 定位：`groupmgr.Chat.add(humans, bots)` 需两个位置参数，`bs_agent.py:679` 写成 `await chat.add([peer_bot])` 只传了 humans；对比 `daemon.py:636`、`groupmgr.py:185` 都是 `chat.add(humans, bots)`
- 修复：`bs_agent.py:679` → `await chat.add([], [peer_bot])`

## 遗留

- agent_registry（bitable）里 name 本来就是纯 name，无需改
- 5 个账号本地 status=init（云端 agent_registry 已 active，本地靠 `refresh_agent_account` 同步）
- A0004 通信录未刷新（缺 A0005），留作阶段后续「使用中刷新通信录」验证
