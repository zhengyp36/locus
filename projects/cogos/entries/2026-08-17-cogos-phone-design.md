# 2026-08-17 — Phone 抽象设计（phone 层定稿，待编码）

> 本体：`~/codex/cogos`。Phone 是 `TelecomClient` 之上的 agent 视角领域层，本次讨论定稿接口与语义，未编码。工作方式：YZ 主导、逐点讨论，AI 提看法并落草稿。

## 分层

- `TelecomClient`（已实现）= 一张卡 = 一个 provider 号码的传输通道（startup/send/listen/shutdown）。
- `Phone` = 卡池 + 通讯录 + 会话 + 本地持久化 + 消息状态机，内部持有 `{number: TelecomClient}`。
- 一张卡 = 一条独立 daemon 长连接（不同飞书 app 各自身份/心跳）。

## 配置（卡 / 联系人）

- `add_card(number: Number, pin) -> Card`：注册 TelecomClient + 记 (provider, number, pin)，建立连接。
  - 成功：卡状态 = 可用，`default_card` 默认第一张。
  - 失败：不抛异常，卡状态 = 失败，记录失败原因（可查）。
- `add_contact(name, numbers: [Number])`：联系人 name → 号码列表（可多号）。
- 联系人分两类：**主动添加**（agent 起名）与**自动添加**（陌生人，name=号码）。
- `contacts()` 返回正式联系人（主动添加），**不含陌生人**；陌生人号码从 `sessions()` 的会话项看。
- 陌生人升级：`add_contact(name, number)` 若该 number 已是陌生人，则改名并标记正式，已有 p2p 会话自动关联（title 从号码变名字）。
- `get_contact(name) -> [Number]`：查联系人号码列表，供 agent 多号时自行确认。
- `rm_card` / `rm_contact`：暂不做（见生命周期）。

## send

接口三重重载，统一签名 `send(target, msg, from_number=None)`：

- `send(name: str, msg, from_number=None)` — name 唯一号时自动解析发出；多号歧义，返回错误，让 agent 走 number。
- `send(number: Number, msg, from_number=None)` — number 必须是 `add_card` 过的自己的号，精确路由。
- `send(chat: Chat, msg)` — 群。只有 p2p 才需要选卡；群一定是聊过的、已绑定卡，细节后议。

`Number` 是值对象：`COGOS005:A0005` 从 agent 视角就是一个 Number。

- `from_number` 显式指定发信卡；缺省（None）时用 `default_card`。
- `default_card`（默认发信卡，类似主卡）需记录并持久化到本地目录。
- 选号/选卡决策交给 agent 自己算，算完用 `send(number, from_number=...)` 精确发出。

## 本地目录 vs bitable（边界）

- 两个不同概念，不混淆：本地目录是**手机自己的**，与通信层无关；通信层数据与手机无关。各管各。
- 讨论手机时**不应看见 bitable**；通信层是黑盒。
- 本地目录存什么：待定，思路是"需要什么存什么"。
- 目前能想到的：电话卡 / 联系人 / 会话（私聊、群聊，都是 Chat）。
- 数据怎么存是实现细节，实现时再讨论。

## listen（收消息）

- **落库是必须的**：无论何种模式，消息到达都先落本地目录。
- `listen(on_notify, on_msg)` 两个回调**都可选、都独立**，不做手机级 mode 状态开关：
  - 只注册 `on_notify` → 只被提醒（无内容），agent 自己去拉；
  - 只注册 `on_msg` → 直接收到内容；
  - 都注册 → 都触发。
- "agent 选模式"等价于"注册哪个回调就用哪个"，可运行中改。
- `on_notify()` **无参**，纯唤醒信号。agent 被叫醒后调 `phone.sessions(type="incoming")` 得含未读消息的会话列表，自己选看哪些。
- `on_msg(chat, contact_from, msg, contact_to)` 给完整内容。

## 会话（Session = Chat）

- 每个 session 就是一个 chat，`type` 区分 `p2p` / `group`。
- 唯一标识：内部用 `Chat.id`（provider 内 `oc_xxx`）做本地目录索引键；对外 agent 只认群名 `title`（群名可重名/改名/为空，**不能作键**）。
- p2p 会话**锚定号码（Number）**，会话相互独立：一个联系人多个号 → 多个独立 p2p 会话。
- p2p 会话 title 动态派生：号码有对应正式联系人 → 用联系人 `name`（agent 本地别名，与 provider 权威名无关，改名自动跟随）；无联系人（陌生人）→ 用号码。
- group 会话的 title = 通信层给的群名。
- 会话产生是惰性的，双向：收到新 chat 消息 → 本地无此会话则自动创建；主动 `send` 给从未聊过的联系人 → 也自动创建 p2p 会话（历史可见自己发的话）。
- 主动建群（create group）暂缺（telecom 未实现）。

## 查看消息（sessions / session / msg 状态）

- `sessions(type="all"|"incoming")` 返回会话列表，每项含 id + title + type + 未读等信息：incoming 返回含未读消息的会话；all 返回全部会话。
- `session.incoming()`：返回该会话的未读消息。
- `session.history()`：返回该会话全部消息（含未读，按时间序）。
- 去掉 `session.content()`：与 history 冗余。
- `msg.read()`：agent 显式标记已读。**不做 `renew()`**——"不 read 即保持未读"已天然覆盖"标回未读"场景，YAGNI。
- `incoming()` 只读、不自动标已读，必须显式 `msg.read()`。

## 生命周期（开机/关机）

- 不做显式开关机：`add_card` 即自动连接；agent 进程在 = 永远开机，进程退 = 关机。
- `rm_card` / `rm_contact` 先不做（暂无删除场景）。
- 备忘（将来做 rm 时遵循）：删卡不删会话，只标记卡状态。

## 待讨论（见 ISSUES.md）

- 会话项是否暴露号码（区分同名会话）
- 群聊链路（send(chat) 的绑卡机制、群会话产生、主动建群）
- 本地目录数据模型 / 对象字段（Msg/Chat/Contact/Card）
