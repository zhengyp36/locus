# handoff｜phone 文件收发 · spec 已定 · 待实验 · 2026-09-19

> **新会话任务**：这是**讨论续讨论**，不是直接开发。先做 **§12 实验（真机）**，按结果修 spec，再把开口项讨论清楚；**不要在实验前落码**。
> **交接语**：读 `work/A/checkpoint/spec-phone-files.md`（本批唯一依据）与 `work/A/checkpoint/handoff-tools-08.md`（web 批次，纪律同源）。
> 代码基线：`cogos` @ `c91aee4`（已推 `origin/master`，工作区干净）。测试用 `python3.11 -m pytest`（系统 `python` 是 3.9，缺 `pyte`）。

## 入口

- 本批 spec：**`work/A/checkpoint/spec-phone-files.md`**（12 节，唯一依据）。
- 权威分册：`cogos/docs/design-agent-tools.md` §10 phone（**尚未更新，仍是旧口径**，待 spec 定案后追平）。
- 讨论记录：尚未并入 `checkpoint-2.md`（**遗留**）；本轮结论全在 spec。
- 既有 phone 代码：`cogos/cogos/phone/{phone,model,store}.py`、`cogos/cogos/feishu/telecom.py`、`cogos/cogos/feishu/daemon.py`、`cogos/cogos/agent/impl/phone.py`。
- 既有实验脚本范式：`cogos/scripts/exp_verify_phone_{send,recv,members,human,e2e}.py`。

## 本批做了什么

- **仅讨论＋定案＋写 spec**，未落任何代码。
- 定下 phone 文件收发（file/image）的整体方案，见 spec。

## 关键结论（勿翻案）

- **phone 不依赖电脑**：term/fs 是可选装配账户；没建账户也要能收发。
- **字节不进 socket**：daemon 直接读写本机路径，socket 只跑信令。路径当**不透明 sink**，不算耦合；daemon 是傻执行器。
- **spool 独立于电脑与 draft**，单层扁平；`list`/`delete`/`clean` + 容量/TTL、只淘汰 idle、在途 pin、懒触发。它是**在途暂存、不是档案**（无检索/分类语义）；命名文件正主仍是电脑 fs。
- **`cogos/phone` 是路径级通用库**（同步语义），"路径限在 spool 内"是 **B 层**约束。
- **授权是护栏不是沙箱**：B 收口，daemon 不管；transfer 能把电脑任意文件搬进 spool 再发，故挡手滑不挡有心（§15 遗留）。
- **完成走作业 Signal，不走 `phone.receive`**：入站附件＝感知面，下载完成＝作业面，两平行，靠 key/job_id 关联。
- 出站**撞名报错**（agent 自行处理）；Phone key **确定性编码 `(chat_id, msg_seq, idx)`**；**重复下载覆盖**（不记状态）；daemon 清 `.part`、spool 自清，两层各管各的。
- `transfer` 保持**纯 copy**；根集合加 spool，寻址 `scheme:path`。

## 下一步（按序）

1. **先做 §12 实验（真机，优先）**，验三条：
   - bot 是否有**读消息资源**（`/im/v1/messages/{id}/resources/{key}`）与**上传**（`/im/v1/files`、`/im/v1/images`）的权限/scope；
   - **bot↔bot（group-p2p）文件消息能否收/发**（此前只验过文本，全新面）；
   - 文件/图片实际大小上限与 `file_type` 枚举取值。
   - 建议按 `exp_verify_phone_*.py` 范式写一次性脚本；结果回填 spec。
2. **按实验结果修 spec**（若 bot↔bot 不支持文件，方案要重估）。
3. **讨论并钉死 spec 开口项**（见下"待裁"）。
4. 定案后更新权威分册 §10，再落码。

## 待裁 / spec 开口项

- 接口形状未钉死：`download` 返回项字段、`SendAck` 形状、**key 编码格式**、路径绝对/相对、附件在 `message` 帧里**与现有 `entry` 并存还是替换**（现 `entry=asdict(entry)` 已带 content dict，易双份）。
- 出站细节比入站薄：群路由、ack 载荷、上传分类边角。
- 文件名注入：agent 给的名字既当 spool 磁盘名又当飞书 `file_name`，需 basename 校验。
- 工具命名、包归属、**spool 配置落点**（卡在 4b 装配未定义处）。

## 风险提示（交给新会话）

- **爆炸半径**：daemon 读循环改"分发起 task"是全体命令共用路径（`daemon.py:276`），回归面远大于手机文件；写串行化不变量一并落。
- **跨消费者**：`cogos/phone` 是通用库，kilo-phone helper 的 `on_msg` sink 契约（`{from,to,content,ts,seq}`）会被 attachments 新字段影响。
- **重叠**：`send_msg` 真异步、渲染缝、4b 装配未完成，注意别混批。

## 明确不做（记债）

audio/media/sticker/post 附件；出站批量；§15 秘密 denylist/审批；vision 接入；并发上限；transfer 的 spool 寻址细节（随 transfer 规格）。

## 纪律

- **先做实验、先讨论清楚，再写码**。
- 结论先落 spec / `checkpoint-2.md`，定案再更新权威分册。
- 一批一会话；开工前重审 spec。

## 收工

- 本批无代码提交。交接单与 spec 落在 `work/A/checkpoint/`。
