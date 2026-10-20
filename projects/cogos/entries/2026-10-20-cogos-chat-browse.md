# chat.browse 落码 · 消息浏览（2026-10-20）

> 状态：**已落码**（`dfd07a5`）。承 tool-design §body（`body.chat.browse(chat, before?, limit?)` 已定口径）+ directory-roots（解除「phone 消息缓存落点」悬置）。

## 口径（落码后）

- chat 参数 = **会话**（联系人名字/号码、群名/群ID），内部 **id 精确匹配 → title（名字/群名）匹配**；title 多匹配报 `AmbiguousChat`（重名兜底，不给内容）。
- **双向（in/out）**：browse 同时看到收到的 + 自己发的，`direction` 字段区分。
- **48h 读时窗口**：只返回 `time >= now-48h`；`before`（毫秒时间戳）翻页读更旧，`limit` 截断标 `truncated`。
- browse 只读 Phone 已有历史，**不拉飞书服务器**（服务器拉取归 toolbox.communication，延后）。

## 关键发现（推翻草稿两点）

- **Phone 层已有双向消息历史**：`Phone._append_msg` 收 `in` + 发 `out` 都写 PhoneStore（json），服务器时间已用（`sent.time` / `message.time`）。→ chat.browse **复用** `Phone.sessions()` + `Chat.history()`，**无需新建缓存**（草稿「新建缓存落 agent_root/work_dir/chat」作废）。
- **SendAck 无需改**：发送消息的服务器时间已由 Phone 层写进 store，browse 不依赖 `PhoneCapability.send` 的返回（草稿「SendAck 带回服务器时间」作废）。
- **群消息天然支持**：`Phone._make_on_msg` 对群消息也 `_append_msg "in"`（perception 只过滤「通知」、不影响 store 落盘），故 browse 群会话（群ID/群名）读得到收发历史，无需改 perception。

## 落码

- `impl/phone.py`：`ChatBrowseView` + `PhoneCapability.browse/_resolve_chat` + `UnknownChat`/`AmbiguousChat`。
- `tools.py`：`make_chat_browse_spec`（`chat_browse`）。
- `body_catalog.py`：`chat.browse` 能力 + chat 组描述更新。
- `app.py`：注册 `chat_browse`。commit `dfd07a5`。

## 被否

- 新建独立消息缓存（落 agent_root）：Phone store 已有双向历史，新建＝双写。
- SendAck 带回服务器时间：browse 不依赖它。
- 复用 store「直接给 browse」但无 48h 过滤：正确做法＝复用 store + 读时窗口过滤（store 不被淘汰污染）。
