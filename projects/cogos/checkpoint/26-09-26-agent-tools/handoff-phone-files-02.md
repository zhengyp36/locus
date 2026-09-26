# handoff｜phone 文件收发 · 已实现 + 真机部分验证 · 2026-09-20

> **新会话入口**：先读 **`work/A/checkpoint/spec-phone-files.md`**（§12 实验、§13 `/FILE`、§14 落点）
> 与 `cogos/docs/design-agent-tools.md` §10（已追平）。本批已落码并 commit，**不是从零讨论**。
> **本批已收束**（真机 ①②③ 全过、已 push）。下一会话转工具现状讨论：读 `handoff-tools-09.md`。
> 代码基线：`cogos` @ **`5c5e1b4`**（本地 `master`，**未 push**，工作区干净）。
> 测试：`python3.11 -m pytest`（系统 `python` 是 3.9，缺依赖）。真机 daemon：`systemctl --user restart cogos-feishu-daemon`。

## 本批做了什么

- 实现 phone **file/image 收发**全链路（daemon 执行器 + `cogos/phone` 库 + B 层 spool/作业/Signal + 工具装配）。
- 实现 bot↔bot 的 **`/FILE` 内置命令**中继（spec §13）。
- 补齐**感知面**：`IncomingMessage.attachments` + perception 透传 + consciousness 渲染（本批审出的缺口）。
- 真机验证 bot↔bot 收发（A0001→A0002，file+image，字节一致）。
- 35 files, +3440；一次 commit `5c5e1b4`。全量 pytest **1181 passed / 4 skipped**。

## 关键结论（勿翻案）

- **字节不进 socket**：daemon 读写本机路径，socket 只跑信令。路径级库 `cogos/phone`；护栏在 B（限 spool）。
- **Phone key 确定性**：`f"{chat_id}#{msg_seq}#{idx}"`；既定位消息又作 spool 槽名（重复下载覆盖）。
- **消息 content 的 key ≠ 上传返回的 key**（文件）；下载/`/FILE` 都必须用**消息里的 key**（§12.4）。
- **限额**：文件 ≤30 MiB、图片 ≤10 MiB；未知扩展名 `file_type=stream`（§12.2/12.3）。
- **bot↔bot**：飞书不把 bot 媒体推给对端 bot；出站文件消息后由 daemon 补发 `@all /FILE <message_id> <key> [name]`，对端 daemon 把它**合成一条带 `attachments` 的入站 `message` 帧**（phone 侧与真人发文件一致）；命令被消费、按 `message_id` 幂等（§13）。
- **伴随 `/FILE` 只在目标解析为 `chat_id` 时发**（bot p2p / 群 / 混合群）；真人 p2p（`user_id`）不发，真人靠真实事件。
- **真人→bot 感知**：飞书按 scope 推用户消息（实测 file/image 事件都到，无需 @）；文件事件 content 带 `file_key`+`file_name`，无 size。
- **读循环**：仅 `download`/`send_file` 分发起 task（其余保持 inline，控制回归面）；`SockFile.write` 加写锁。
- **on_msg sink 契约未改**：attachments 走持久化的 `Msg.attachments`，perception 从 `chat.history()` 末条读公开附件（`ref` 不外泄）。

## 已验证（真机，2026-09-20 全过）

- ✅ **bot↔bot（新 API）**：`scripts/exp_verify_phone_files_e2e2.py` ALL PASS —
  `Phone.send_file(A2, src)` → `/FILE` 伴随 → 对端合成入站附件 → `Phone.download([key])` 字节一致（file+image）。
- ✅ **接口/解析**：unit tests（daemon/phone/spool/transfer/perception）。
- ✅ **真人→bot**：重开监听（`/tmp/kilo/verify_human_in.py`）后 YZ 现场发 3 文件 + 1 图片，
  **全部无 @ 就推到 bot**（4 事件 `event_seen=True`），按消息 key 下载字节一致；
  事件 content = file 的 `file_key`+`file_name` / image 的 `image_key`，无 size（坐实 §12.4）。
- ✅ **bot→真人渲染**：YZ 手机确认可打开预览。
- ✅ **mixed group 对端 bot**：手动群（A0001+A0002+H0002，群 `oc_56e69ba9...`）`/tmp/kilo/verify_mixed_group.py` ALL PASS —
  对端合成附件、sender 解析成 `COGOS002:A0001`、按 key 下载字节一致（file+image）；薄弱点未复现。
- 观察：真人入站图片 15.1 MB（≈14.4 MiB）可收可下，超「图片 ≤10 MiB」——该限额只约束 bot 上传/发送，真人入站不受限。

## 遗留 / 开口（交新会话或 YZ 裁决）

- **mixed group**：真机已过（见上）；但 `_resolve_group_sender` 依赖 contact/tracker，仍属薄弱点。
- **`/FILE` 投递失败**：已补 warn（`file_cmd.py:83`，`45ab216`），但 `_mark_seen` 在 deliver **前**标记 → 失败不重试（待 YZ 裁决是否回滚 seen）。
- **`/FILE` 幂等**是内存态（上限 512，daemon 重启即失）。
- **transfer 寻址**：当前用结构化 `kind`+`entry`（draft/machine/spool），**未**落 spec §8 的 `scheme:path` 字符串形式；语义（纯 copy、撞名报错）已实现。
- **spool 元数据**：`list` 的 `name` = 磁盘 id（Phone key / agent 名），**原始文件名未持久化**为 spool 元数据。
- **批量/并发**：一消息多附件批量、并发上限、秘密 denylist/审批 仍 §11 遗留。
- **前提**：daemon 只在「该 bot 的 agent 进程在线」时订阅其飞书事件；离线时命令/真人消息都不会到 daemon。
- 实验脚本已随本批提交（`scripts/exp_verify_phone_files*.py`），可作真机复验的骨架。

## 风险提示

- 读循环分发起 task 是全体命令共用路径，已收窄为仅新帧；若后续扩展需一并审写串行化。
- `/FILE` 依赖对端 daemon 把 `entry.sender` 解析成号码；群场景的号码解析是薄弱点。

## 收工

- commit：`5c5e1b4`（本批）+ `45ab216`（/FILE 失败补 warn）；本地 `master`，**未 push**。
- 本批真机复验脚本（未入 git，可复用）：`/tmp/kilo/verify_human_in.py`（真人→bot）、`/tmp/kilo/verify_mixed_group.py`（mixed group）。
- 交接单与 spec 落在 `work/A/checkpoint/`（该目录非 git 仓库）。
- 记得：真机复验前 `systemctl --user restart cogos-feishu-daemon`。
