# phone 文件收发实现规格 · 2026-09-19

> 本批开工依据。来源：2026-09-19 与 YZ 的对话（讨论记录待并入 `checkpoint-2.md`）。
> 权威分册：`cogos/docs/design-agent-tools.md` §10 phone。代码基线：`cogos` @ `c91aee4`。
> 范围：`phone.send` / `phone.receive` 增加**文件（file/image）**；audio/media/sticker/post 不做。

## 0. 目标与立场

- **收发是基线能力，不依赖电脑**：term/fs 是可选装配的账户，"没建账户"也必须能收发文件。
- 三层职责：`cogos/phone`＝路径级通用库（**同步语义**、只拿路径与不透明引用）；`daemon`＝有凭据的执行器（解析附件、下载/上传、后台 task）；agent 侧（B／机制）＝授权与 spool。
- **文件字节不进 socket**：daemon 直接读写本机路径，socket 只跑信令（key／路径／ack）。字节 disk→disk，零进程间拷贝。
- 命名文件的正主仍是**电脑 fs**；spool 只是**在途暂存**，无检索语义，不是档案。
- agent 仍是自主主体：下载完成只发 Signal 唤醒，**机制不代它回复**（沿用 web 口径）。
- 图片"可读"依赖视觉（后续能力）；本批只保证字节到位。

## 1. 附件解析（daemon）

- `entry.py` 增加 `_extract_attachment(msg_type, content, message_id)`：
  - `image` → `{kind:"image", key:image_key, name:""}`
  - `file`  → `{kind:"file", key:file_key, name:file_name}`
  - `audio`/`media`/`sticker`/`post`：本批不解析（`content_text` 仍为空，行为同现状）。
- `route_message` 的 `message` 帧增加字段 `attachments: [{kind, key, name, ref}]`，其中 `ref = {message_id, file_key}` 是**不透明**串，仅供回程下载。
- 事件里**没有 `file_size`**：大小只能下载后知道（已知代价）。
- 资源下载 URL：`GET /open-apis/im/v1/messages/{message_id}/resources/{key}?type=image|file`（`image_key` 用 `type=image`，其余用 `type=file`）。
- **key 必须取消息 content 里的**：实测 message `file_key` ≠ 上传返回的 `file_key`，用错会 `234003`（§12.4）。

## 2. Phone 模型（`cogos/phone`）

- `Msg` 增加附件列表；每项：`{key(Phone key), name, kind, ref(不透明)}`。
- **Phone key**：不透明、**确定性**，编码 `(chat_id, msg_seq, idx)`。用途有二：
  1. `download(key)` 直接定位消息，**不建索引表**；
  2. 作为 spool 槽名，使重复下载天然覆盖。
- `ref`（`message_id` + `file_key`）只在 Phone 内部存/转；**不进 agent 可见 API**（phone-design 身份边界）。
- 不记录"是否已下载"状态（见 §3 重复下载规则）。

## 3. download（入站）

库（`cogos/phone`，通用、路径级）：

```python
async def download(self, keys, dst_dir) -> list[dict]
# 每项: {"key", "path", "name", "ok", "error"}
```

- `dst_dir` 由调用方给（B 传 spool 目录）；**库不认 spool 概念**。
- 逐 key 解析 `ref` → 让 daemon 下载到 `dst_dir/<key>[.part]`。
- `name` 回传原始文件名（元数据），磁盘名用 key。

daemon：

- 帧 `download{request_id, ref, path}` → **后台 task**（非 inline）拉资源 → 写 `<path>.part` → 原子 `rename` → `download_ack{request_id, results}`。
- **读循环必须改成"分发起 task"**（`daemon.py:276` 现为 inline，长下载会堵整条控制通道）。
- **重复下载**：同名（key）槽先删后写 → 幂等、无状态。
- **同 key 并发**：单飞；第二个请求报"下载中"。
- 失败/超限/取消：删 `.part`，**不留空条目**。

## 4. send_file（出站）

库（`cogos/phone`）：

```python
async def send_file(self, target, src_path, name) -> SendAck
# target 语义同 send（name / Number / Chat）
```

流程：agent 先把文件放进 spool（`transfer`）→ `phone.send_file(target, spool_path, name)`。

daemon：

- 帧 `send_file{request_id, to|chat_id, path, name}` → 读 `path` → 分类上传 → `Lib.send(msg_type=file|image, content={...})` → 落出站消息 → `send_file_ack{request_id, ...}`。
- 分类表（daemon，按扩展名）：
  - 图片 `.jpg/.jpeg/.png/.gif/.webp/...` → `POST /im/v1/images`（`image_type=message`）→ `msg_type=image`，content `{"image_key": ...}`
  - 文件 → `POST /im/v1/files`（带 `file_type`+`file_name`）→ `msg_type=file`，content `{"file_key": ..., "file_name": ...}`
  - `file_type` 映射：`pdf/doc/xls/ppt/mp4/opus`，**未知落 `stream`**。
- 上传前 `getsize` 预检上限，超限快速失败。
- p2p 选卡 / 群 `bound_card` **复用现有路由**（`_send_p2p`/`_send_to_chat` 的解析），只换 content 为文件。
- **一条消息一个文件**；多文件＝多次调用。

## 5. cancel

- 协议：`download_cancel{request_id}` / `send_file_cancel{request_id}`；daemon 按 **`(conn, request_id)` 鉴权**取消（别让 A agent 取消 B 的），清 `.part`。
- B 作业 cancel：工具 task 被取消时 Phone 捕获 `CancelledError` → 补发对应 cancel 帧（daemon 回的 ack 无人收，无所谓）。
- daemon 断连：遍历该 `conn` 在途登记表**批量取消**。
- 竞态：下载可能刚好完成——按 **task 状态**判是否还在跑，别按文件在不在（避免删掉已完成的最终文件）。

## 6. 作业与 Signal（B 层）

- `phone_download` / `phone_send_file`：`time_form="async"`，返回 `JobAccepted`；完成/失败发
  `Signal(kind="phone.download_done" | "phone.send_file_done", payload={job_id, state, items|error})`；**取消不发**。
- `phone_cancel(job_id)`：同步、幂等，照 `web_cancel`。
- payload 只带机器事实（key/path/state/error），**不带内容**。
- 完成通知**不走 `phone.receive`**：入站附件是**感知面**，下载完成是**作业面**；两条平行，靠 `key`/`job_id` 关联。

## 7. spool（agent 侧，本地）

- 一块本地目录，机制自有，**独立于电脑与 draft**；**单层扁平**，不分 in/out。
- 命名：入站＝Phone key（确定性）；出站＝agent 给的名字；**撞名报错**（agent 自行改名或先 `list`）。
- 接口：`list`（最小元数据 `id/name/size/mtime`）、`delete`（幂等）、`clean`（清全/清过期）。
- 淘汰：**容量上限 + TTL，两者先到**；**只淘汰 idle**，在途（下载中/发送中）**pin 住**；**懒触发**（list/download/send/delete 时顺手清）。
- 与 draft 的**有意不对称**（写进 spec 说明）：draft 无 delete（淘汰覆盖删除，§7）；spool 有显式 delete——它是信箱，收到不想要的要能立刻丢。角色不同，不是概念打架。

## 8. transfer

- 保持**纯 copy**（design §9 原则不动）。
- 根集合增加 spool，寻址统一为 `scheme:path`：`draft:<id>` / `spool:<key或name>` / `machine:<相对根路径>`。
- "移出 spool" ＝ 上层组合 `transfer` + `spool.delete`（不给 transfer 加 mode）。

## 9. 接线

- `cogos/agent/impl/phone.py`：`PhoneCapability` 增加 `sink` + job 表 + `download`/`send_file`/`cancel`。
- `cogos/agent/tools.py`：`phone_download` / `phone_send_file` / `phone_cancel` + spool `list`/`delete`（包归属由装配层定）。
- `app.py`：装配 spool 目录与 Phone 配置；退出时清在途。
- **授权护栏在 B**：校验 `dst`/`src` 落在 spool 内。这是**护栏不是沙箱**——transfer 能把电脑上任意文件搬进 spool 再发，故挡手滑不挡有心（§15 遗留）。daemon 保持傻执行器。

## 10. 测试

- daemon（假 Feishu transport）：附件解析、下载 `.part`→rename、取消清 `.part`、上传分类、超限失败、断连批量取消。
- Phone：key 定位消息、重复下载覆盖、同 key 并发拒绝、附件引用不进 agent API。
- B：作业/Signal/cancel、spool `list`/`delete`/TTL/pin。

## 11. 不做 / 遗留

- audio/media/sticker/post 附件；一消息多附件下载的批量语义细化；出站批量；秘密 denylist/审批（§15）；vision 接入；并发上限。
- transfer 的 spool 寻址细节随 transfer 规格落。

## 12. 前置验证（真机结果，2026-09-19 已完成）

脚本：`cogos/scripts/exp_verify_phone_files.py`（自包含 API 探针）、
`..._human.py`（真人 H0002↔A0001）、`..._send.py`（出站 + bot↔bot）。
账号：A0001-A0005；真人 H0002=YZ。daemon 用 `systemctl --user start cogos-feishu-daemon`。

**1. scope：全部通过。** A0001 可 `POST /im/v1/files`、`POST /im/v1/images`、
`GET /im/v1/messages/{id}/resources/{key}?type=file|image`；上传→发送→下载回字节一致。

**2. 大小上限（实测，含边界）：**
- 文件：≤ **30 MiB**（31,457,280 B 通过，+1 失败，`code=234006` "file size exceed"）。
- 图片：≤ **10 MiB**（10,485,760 B 通过，10,490,000 失败，同样 234006）。

**3. `file_type` 枚举：** 接受 `doc/xls/ppt/pdf/mp4/opus/stream`；
`image`/`bogus`/空 → `234001` invalid param。注意**没有** `image` 这个 file_type；
图片走 `/im/v1/images`（`image_type=message`）。未知类型落 `stream` 的策略成立。

**4. 关键坑：message file_key ≠ upload file_key。**
`/im/v1/files` 返回的 `file_key` 与消息 content 里的 `file_key` **不同**；
下载消息资源必须用**消息 content 里的 key**（用上传返回的 key 会 `234003 File not in msg.`）。
图片两处 `image_key` 相同。→ §1 的 `ref.file_key` 取**消息 content** 的 key；§4 用上传 key 发送。

**5. 入站事件（感知面）：真人→bot 全部通过。**
- 真人 H0002 在普通群（无 @）发图片：A0001 收到事件（`type=image, content={image_key}`），
  回捞 + 下载成功（实测 15MB 图）。
- 真人 H0002 在普通群（无 @）发**文件**：A0001 收到事件
  （`type=file, content={file_key, file_name}`），回捞 + 下载成功（800B，`event_seen=True`）。
- 即：**人类发的 file/image 事件能到 bot，无需 @**；事件里**没有 size**（符合 §1）。

**6. bot↔bot：发 OK、读/下载 OK、事件不保证。**
- A0001 可上传并发送 file/image 到 bot 群与 group-p2p（`code=0`）。
- 接收方 A0002 能 `list_messages` 回捞并用**自己的凭据**下载，字节一致（file/image 均验证）。
- 但**对端 bot 收不到事件**：A1（普通群/group-p2p）监听时，A2 用原始 API 发的
  text/file/image 均无事件；A2 侧同理。经 daemon `send` 的文本能到（本地投递，非飞书推送）。
- 推断：飞书只把**用户**消息按 scope 推给 bot，**bot 发的消息不推给对端 bot**（除非 @，而文件无法 @）。
  → bot↔bot 文件的"感知面"不能依赖事件，须回捞历史或另设计（**遗留，待裁**）。

**结论**：方案主体成立——真人→agent 的 file/image 感知面（事件）、回捞、下载全验证；
上传/下载/限流/枚举都验证。需按第 4 条修 `ref` 取键口径，并把第 6 条的
bot↔bot 入站感知方式列入待裁。真人↔agent 的出站方向由 YZ 手机端确认渲染。

## 13. bot↔bot 文件：新增 `/FILE` 内置命令（2026-09-19 定，待抠细节）

背景：飞书只把**用户**消息按 scope 推给 bot，**bot 发的消息不推给对端 bot**（除非 @）。
现有 bot↔bot 文本靠 daemon 注入 `@_all`（`daemon.py:352`）走通；file/image 的 content
没有 @ 槽 → 对端收不到事件（§12.6）。真人→bot 不受影响。

方案：复用 `@all` 通道 + 新增内置命令（同 `/ENTER` 机制，`agent_cmd` 注册）：
- 命令形状：`/FILE <message_id> <file_key>`（group-only 文本；`is_command` 已限定）。
- 出站（daemon `send_file`，目标为 **bot**）：上传 → `Lib.send(msg_type=file|image)` 落消息，
  得 `message_id` + 消息 content 的 `file_key` → 紧接发一条 `@all /FILE <message_id> <file_key>`。
- 入站（对端 daemon 的 `/FILE` handler，注册方式同 `group_event`）：解析 →
  **合成一条带 `attachments` 的入站 `message` 帧**交给本 bot（见"已定"第 2 条），
  命令被 `dispatch_command` 消费，**不再作为普通文本转给 agent**；下载由 agent 走
  `phone_download` → `phone.download_done` Signal。
- 幂等：按 `message_id`/key 去重；命令后于文件消息落，读不到就短暂重试。
- 与 §6 一致：命令＝感知触发面，下载完成＝作业面 Signal。

已定（YZ，2026-09-19）：
1. payload **带** key：`/FILE <message_id> <key> [name]`（kind 由 key 前缀判定：
   `img_` → image，否则 file；name 取余下整行，可省）。
2. **对端 daemon 把 `/FILE` 转成一条 attach 消息**：合成入站 `message` 帧
   （`from=<对端 bot>`，`attachments=[{kind, key, name, ref:{message_id,file_key}}]`），
   使 phone 收到的效果与**真人发文件/图片一致**；命令本身仍被消费、不进 agent 文本流。
   agent 照常 `phone_download` → `phone.download_done` Signal（感知面/作业面与真人对称）。
3. **混合群同样补发** `/FILE`（接受 `@all` 打扰群里真人）。

**实测（2026-09-19/20，原型已验）**：daemon 加临时 `/FILE` handler（`cogos/feishu/file_cmd.py`）。
- 前提：对端 bot 的 **agent 在线**时 daemon 才订阅其飞书事件；离线时命令到不了 daemon。
- 结果：group-p2p 双向、混合群，file+image 均收到命令 →
  daemon 按 `{message_id,key}` 下载成功（`[FILE-CMD] OK ... bytes=...`，字节一致）；
  命令被 `dispatch_command` 消费，未作为文本转给 agent。
- 结论：`@all /FILE` 机制成立，可据此实现（合成 attach 消息 + spool + Signal）。

**真机复验（2026-09-20，本实现全过）**：
- 真人→bot：无 @ 事件直达（file/image 4 条 `event_seen=True`），按消息 key 下载字节一致；事件 content 无 size（坐实 §12.4）。
- bot→真人：YZ 手机可打开预览。
- mixed group：手动群（A0001+A0002+H0002）对端合成附件、sender→`COGOS002:A0001`、下载字节一致。
- `/FILE` 投递失败原先静默丢弃，已补 warn（`file_cmd.py`，commit `45ab216`）。

## 14. 实现落点（2026-09-20）

- `cogos/phone`：`Msg.attachments` + `phone_key`；`Phone.download(keys, dst_dir)` / `Phone.send_file(target, src_path, name)`；`ref` 不外泄（`Msg.attachments_public`）。
- `cogos/feishu/telecom.py`：`Message.attachments`、`download(ref, path)`、`send_file`/`_send_chat_file`（daemon 帧）。
- `cogos/agent/impl/spool.py`：`Spool`（list/delete/clean、容量+TTL、pin、collision、contains 护栏）。
- `cogos/agent/impl/phone.py`：`download`/`send_file` 异步作业 + `phone.download_done`/`phone.send_file_done` Signal + `cancel`（同步幂等、取消不发）。
- `cogos/agent/impl/transfer.py`：`SpoolRef`，draft/machine/spool 任意向纯 copy。
- `cogos/agent/tools.py`：`phone_download`/`phone_send_file`/`phone_cancel`/`phone_spool_list`/`phone_spool_delete`；`app.py` 装配 spool。
- `cogos/feishu/file_cmd.py`：真 `/FILE` handler（合成 attach 消息、按 message_id 幂等）；`daemon._send_file_companion` 在 bot/群目标后补发 `@all /FILE <message_id> <key> <name>`。
- 未覆盖：mixed group 里对端 bot 的 sender 解析依赖 tracker（**2026-09-20 真机已过**，仍属薄弱点）；批量/并发上限仍为遗留（§11）。

