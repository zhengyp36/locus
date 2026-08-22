# cogos 真机验证计划（草稿 v2）

> 2026-08-22 | 全新 provider `COGOS002`，从零建，真人 + AI 共同完成
> 真群验证主体：脚本直调 `FeishuTelecomClient`，不用 term
> 本体：`~/codex/cogos` | 数据目录：`~/.cogos/feishu/default/run/sessions`

## 一、目标

在全新 provider `COGOS002` 上跑通完整链路，顺带验证"从零建 provider"的全过程：
建 provider（init + setup-bs + /setup）→ 建 agent（/add-agent）→ 真群收发/命令/区分/tracker/event。
全部用新群，不用 COGOS001 老群。

## 二、验证方式

不用 term（交互式 stdin REPL，AI 无法操作）。改用脚本直调 telecom 接口：

```python
import asyncio
from cogos.feishu.telecom import FeishuTelecomClient, Contact, ALL

c = FeishuTelecomClient(Contact("COGOS002:A0001"), pin)
c.listen(on_msg=..., on_disconnect=...)   # 先设回调再 startup（reader 在 startup 时已起）
ident = await c.startup()                  # 鉴权 + 返回权威身份
chat = await c.create_chat("verify")       # 建群，caller 成 owner（任意 agent bot 均可）
await chat.add_members([Contact("COGOS002:A0002")])   # daemon 内部编排 me_join（public 已考虑）
await chat.send("hi", to_targets=[ALL])    # 群发 @all
await chat.send("hi", to_targets=[Contact("COGOS002:A0002")])  # 指定 mentions
await chat.get_members()                   # 群成员列表
await chat.remove_members([...])           # 群主踢人
await chat.leave()                         # 自己退群
await c.shutdown()
```

关键点：
- `startup()` 内部已 `_do_listen()` 起 reader + heartbeat；`listen()` 只重设回调（`_reader` 动态读 `self._on_msg`，startup 前设回调最稳）
- 每个 bot 一个独立 client，一个脚本多 client 并发，或分脚本
- 群聊 send 是 fire-and-forget，靠对方 `on_msg` 回显验证收到

## 三、整体阶段

### 阶段 0：环境 + bs-bot（真人扫码 1 次）
- AI：`cogos-feishu init`（起 daemon + monitor）
- AI：`cogos-feishu setup-bs --provider COGOS002` → OAuth URL 给 YZ
- YZ：扫码建 bs-bot（`{provider}-BS-{device_name}`）
- 断言：bs-bot 落盘 + daemon `add-bot` WS 激活

### 阶段 1：setup provider（真人扫码 + 点链接）
- YZ：飞书给 bs-bot 发 `/setup` → 点卡片
- 流程：OAuth 建 admin-bot（扫码 1 次）→ patch 权限授权（点链接）→ 建 bitable 7 表 → 落盘 provider.json
- 断言：admin-bot + bitable + bs_registry 落盘

### 阶段 2：add-agent × 4（每个 agent 扫码 1 次）
- YZ：飞书给 bs-bot 发 `/add-agent <name>` → 点卡片
- 流程：OAuth 建 agent-bot（扫码）→ patch 授权（点链接）→ 事件订阅（点链接）→ 生成 PIN + 注册 + contact bitable
- 建 4 个：A0001/A0002/A0003/A0004（真群验证需要 1 群主 + 2 成员，tracker/event 用第 4 个）
- 断言：账号文件含 `pin`、`status=init`、`bitable_token`；agent_registry 有记录

### 阶段 3：真群验证（AI 脚本主导，见下节）

## 四、真群验证分层（依赖驱动）

### L1 建真群
- 群主 bot `create_chat("verify")` 建群
- `add_members([A0002, A0003])` 拉两个 bot
- 断言：A0002/A0003 各自 on_msg 收到进群 system 消息；chat_registry 落盘 owner=群主

### L2 收发
- 群主 `chat.send("hi", [ALL])` → A0002/A0003 on_msg 收到（sender=A0001，mentions 含 @all/全成员）
- 群主 `chat.send("hi", [A0002])` → 仅 A0002 收到、mentions 含 A0002
- A0002 回复 → 群主收到（反向）
- 断言：落地 `by_chat_id/<chat_id>/history` + group 软链；sender number 解析正确（真 group 走 `resolve_number`）

### L3 命令/区分
- 发 `/x`（未知命令）→ 被 `is_command` 拦截，不达 agent（on_msg 收不到）
- 发 `//hello` → agent 收到 `content == "/hello"`（双斜杠还原）
- 发已有命令（如 `/help`）→ 走命令 handler
- 区分：真群 sender 是 A 号（非 group-p2p 的 peer_number 路径）

### L4 tracker
- 建群后各 bot `members.json` 生成，agent 区含 A0001/A0002/A0003，`history_available=true`
- A0004 进群 → `/ENTER` 公告触发其它 bot `rebuild()` → members.json 补 A0004
- startup 遍历：重启某 bot，`_build_group_trackers` 自动建 tracker
- member 事件喂入：bot 进/退群事件 add_event 生效

### L5 event
- 新 bot 进群 → `/ENTER Axxxx` 公告 + 各 bot members.json 收敛
- 退群四路径：
  1. `chat.leave()`（自己退）→ `/LEAVE` 公告 + 真正退群
  2. `chat.remove_members([A000x])`（群主踢）→ `/LEAVE` + 退群
  3. `/REMOVE`（真人校验）→ 需真人，延后
  4. `/LEAVE` 接收方 rebuild 收敛
- 断言：退群后各 bot members.json 移除该 bot

## 五、真人 / AI 分工

| 环节 | AI | 真人（YZ） |
|---|---|---|
| init / setup-bs CLI | 执行、观察日志、转达 URL | 扫码建 bs-bot |
| /setup | 观察日志 | 发命令 + 点卡片 + 扫码 admin-bot + patch 授权 |
| /add-agent × 4 | 观察日志 | 发命令 + 点卡片 + 扫码 + patch + 事件订阅 |
| 真群验证 | 脚本驱动、断言、定位修复 | 无需（除非飞书需手动确认） |
| 延后项 | 脚本 + 断言 | 真人进群/发言/发 /REMOVE |

## 六、必测点（失败即定位并修复代码，不视为"风险"）

1. 任意 agent bot 都能 `create_chat` 成为 owner（不依赖 BS/admin）
2. `add_members` 拉 bot 进群（daemon 内部 public/me_join 编排正确）
3. `add_members` 传 A 号 vs H 号，daemon 正确区分 human/bot 路径
4. 真群 sender/mentions 解析（open_id 双向 + 三缓存）
5. 真群与 group-p2p 判定不串（新群全是真 group）
6. `/ENTER` `/LEAVE` 公告 + rebuild 收敛，各 bot members.json 最终一致

## 七、观测手段（AI 不用 term 观察）

- 脚本内 on_msg 回调直接 print → 断言收发结果
- 落地目录 `~/.cogos/feishu/default/run/sessions/<app_id>/by_chat_id/<chat_id>/`：`members.json` / `history` / `contact.json`
- daemon 日志看 WS 收发、三缓存命中、路由分派

## 八、真人边界（延后，需真人主动）

1. 真人进/退群 → tracker 的 human 分区事件
2. `/REMOVE` 真人校验（真人发命令踢 bot）
3. human 的 `user_open_id` 解析（需真人在群）
4. 真人发普通消息 → bot 收到（sender 解析为 H 号）

## 九、工作流（checkpoint 约定）

采用 `locus/scratch/checkpoint-rule.md` 规则（凝练可恢复、锚点优先），checkpoint 落 `/tmp/kilo/locus/checkpoint/`（locus 工程之外，`/undo` 不回退）。

三个文件职责：
- `cogos-live-verification-plan.md`：验证计划（目标/阶段/分层/分工/必测点/工作流），相对稳定，只改计划本身
- `codebase.md`：代码认知基线 + 每步对代码的新认知（append 式，跨步骤持续累积）
- `step-N-<主题>.md`：每步过程记录（当前问题/已做修改/已读代码要点/关键结论/遗留坑）

会话节奏：
1. 新会话加载本 plan + `codebase.md`，恢复上下文
2. 按阶段执行；过程中重要信息记 `step-N-<主题>.md`，新代码认知 append 到 `codebase.md`
3. 一步完成后停下，提示 YZ `/undo` 回退清理讨论干扰
4. 下一步：加载 `codebase.md`（+ 本 plan）恢复，继续

文件命名：
- `step-1-setup-COGOS002.md`（建 provider + agent）
- 后续：`step-2-群聊收发命令.md`、`step-3-tracker-event.md` 等（按实际拆）
