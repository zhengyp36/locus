# 260818 — 飞书群相关操作调研与结论（供新会话续接）

> 会话时间：2026-08-18。主题：cogos 里「建群 + 拉 bot 进群」这条落地路径，最终确认飞书平台新规封死了「bot 互拉建群」。
> 读这一个文件即可恢复全部上下文。

## 背景：为什么关心"群"

- cogos = 多 agent 运行时，飞书作通信总线 + 人-agent 交互面。
- 项目地图「不变量 4」：bot↔bot 私聊飞书不支持 → 用 **双 bot 群 + @all** 实现，不解散、写 bitable（当前 ⏳ 未实现）。
- 本会话围绕「建群 + 把 bot 拉进群」的可行性做调研，发现这条路径有平台侧障碍。

## 一、cogos 现有建群能力（`~/codex/cogos`）

- `cogos/feishu/groupmgr.py`：CLI 命令 `create-group` / `invite-members` / `leave-group` / `destroy-group`（均手动）。
- `create-group` 流程：`load_bot(args.bot)` 按文件名 stem 取 bot → `lib.create_chat(app_id, app_secret, name, user_ids, user_id_type)` 建群（bot 成为群主）→ 打印 `chat_id`。
- `cogos/feishu/core.py`：
  - `create_chat`（:295）：body 带 `chat_type:"group"`，可选 `user_ids`+`user_id_type` 建群时顺带拉人。
  - `add_members`（:316）：`id_list` 支持**批量**，`member_id_type` 走 query param；`invite-members` 默认 `open_id`。
- 特性：非 0 直接抛 `RuntimeError`，**不幂等**（`232010` 已在群 会被当失败）。

## 二、与 bot_group_test.py 的对比（前身已验证脚本）

- 路径：`~/codex/agent-study/agent-study/agi-core/feishu/scripts/bot_group_test.py`。
- 建群：`create_chat` 只传 `{"name": name}`，不带 `chat_type`、不带成员；群建好后再**逐个** `add_member` 拉人。
- 拉人：**逐个**调 `add_member(token, chat_id, id, id_type)`：
  - 拉 bot 用 `member_id_type="app_id"`，传 bot 的 `app_id`；
  - 拉真人用 `member_id_type="open_id"`；
  - 用**第一个 bot（建群者/群主）的 token** 统一拉所有人。
- 幂等：`232010`（已在群）当成功处理。
- 权限引导：建机器人后打印授权 URL（含 `im:chat:create` 提示）。

## 三、拉 bot 失败的第一层原因：member_id_type

- 飞书规定：**拉 bot 进群必须 `member_id_type="app_id"`，`id_list` 填 bot 的 app_id**（不能用 open_id）。
- cogos `invite-members` 默认 `open_id`，一个 `--id-type` 套用全体成员，无法在一个命令里混用两种 id 类型 → 拉 bot 时把 app_id 当 open_id 传，直接报错。
- 权限不是问题：`bot_manifest.py` 的 `BOT_SCOPES` 已含 `im:chat.members:write_only` 和 `im:chat:create`。

## 四、第二层（更根本）：飞书新规 "Bot is not allowed to be invited by other app"

- 报错字面：**应用（app）不能再把「另一个应用的 bot」拉进群**。
- 关键：`bot_group_test.py` 和 cogos 拉 bot 时用的都是 **`tenant_access_token`（应用身份）**（前者 `TOKEN_URL = auth/v3/tenant_access_token/internal`；后者 `Lib.fetch_token` 同理）→ 两者现在都会命中这条限制。
- 时间线：早期飞书允许「app 拉 app bot」，**2025 年收紧**：
  - 官方文档 "Add users or bots to a group" 最后更新 2025-03-13，新增 "Usage restrictions"；
  - 2025-03-31 生效「将用户或机器人拉入群聊 API 补充沟通权限管控」公告（沟通协作权限 / 对外沟通权限 / 屏蔽校验，涉及 `232024`、`succeed_type` 入参）。
- 该句报错文案**尚未收录进官方错误码表**（较新变更，文档未同步），已核对 apifox 镜像的完整错误码列表（232001/232010/232014/232024/232025/232027/232028/232033/232034/232043/232044/99992351… 均无此句）。

## 五、可行替代方案（待选）

1. **真人手动拉**：客户端把 bot 加进群。最省事，但不可编程、违背自动化。
2. **用户身份拉**：改用 `user_access_token`（真人 user 的 OAuth token）调拉人接口——用户身份仍可拉 bot。依赖真人授权，token 需刷新。
3. **bot 主动加入**：`PATCH /im/v1/chats/:chat_id/members/me_join`（"用户或机器人主动加入群聊"接口），让 bot 自己加群而非被别的 app 邀请。前提待核（是否需群开放、bot 是否需知道 chat_id 等）。

## 六、对 cogos 的影响

- 不变量 4 的落地路径「bot 互拉建双 bot 群」被飞书平台封死，需重新决策。
- 待讨论的对策方向（本会话末尾引出，未定）：
  - A. 走方案 2/3 把 bot 拉进群，继续坚持「飞书群内 bot↔bot」；
  - B. 重新审视设计：bot↔bot 通信不通过飞书群，改走 cogos 自身的通信层（Telecom / Phone 抽象已存在，agent↔daemon 已通），飞书仅作 agent↔human 交互面。

## 参考资料

- 官方文档 "Add users or bots to a group"（Usage restrictions）：https://open.feishu.cn/document/server-docs/group/chat-member/create
- 拉人进群 API 补充沟通权限管控公告：https://open.feishu.cn/document/platform-notices/breaking-change/additional-communication-controls-for-add-to-group-api
- apifox 镜像（含完整错误码表 + me_join 接口）：https://feishu.apifox.cn/api-9020974
- 实战 gist（多 Agent 群、拉 bot 用 app_id、飞书智能体拉不进群 232024）：https://gist.github.com/huyufeng700-png/52b1e3e3e99bd7207b0ddcc240cffc06
