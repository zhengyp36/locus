# ISSUES

## 遗留（待处理）

### load_bot 与 AccountRef.ensure 分层错位

- 多处 `load_bot` 读 agent 账号，文件删了直接报错，应从云端兜底；但两者层次不同，不能一刀切替换。
- `load_bot`：本地文件读取，同步，文件丢失抛错，无云端兜底/TTL；`AccountRef.ensure`：memory→local→cloud→hard fail，云端兜底 + TTL，入参 `provider:number`。
- 该改的调用点（读 agent 账号，registry 有权威源）：`term.py:79` `_load_pin`、`bs_agent.py:511/770/888`；该留的（非 registry，云端无权威源）：admin/bs/test bot。
- 根修法：本地文件退化为纯缓存（字段全可云端重建），agent 账号读取全走 ensure，load_bot 只服务 admin/bs/test。→ entries/2026-08-20-cogos-load-bot-vs-ensure.md

### sessions 软链接：群改名同步暂未实现

- 群改名时 group/ 下的软链接仍用首次群名，不更新/重链（规则定为「只用第一次名字」）；作为遗留，需 YZ 知悉，后续补。

### resume 重建账号与 setup 账号的字段差异

- `name`：resume 用 provider_name，setup 用 app 真实名（如 `COGOS008-ADMIN`）；是否还原 app 真实名待定。
- `patch_granted`：resume 无法从云端恢复（registry 未存），重建账号缺失；无功能风险，重走 setup 会再次引导 patch 授权。

### 账号失效机制的两处遗留（机制已实现，缺口仍在）

- **注销是最终一致、非强保证**：离线设备靠 fail-open（云端不可达不主动失效、5 分钟重试）可无限期续命，最坏失效延迟 = 12h TTL + 重试窗口。与「号码唯一性=纪律非软件保证」同类折中，需 YZ 知悉。
- **无 revoke 命令**（暂不实现，短期无失效必要）：`agent_registry.status` 目前只有 `"active"`，没有把 status 改为 inactive 的入口，失效机制真机端到端不可触发（只能 mock 单测）。

### 坐标规则注入：静态前置 → 应随图动态注入（设计讨论已定方向，暂缓）

- 现状：坐标规则是**静态 system 前置**（`FigContext.system_prompt()` / `SYSTEM_HINT`），任何上下文都带。
- 后续想改成：**有图才注入、只放一条 system、位置在首次/当前图块前、随最近一张图移动、图全消失则规则删、整套只说一次**；上下文无图不谈坐标（省 token、不误导，且与图块 K 轮老化/摘除天然对齐）。
- 附带硬约束：图全消失后模型"重定位已摘窗口"时为**无规则、纯锚**状态 → 锚必须真正自含（正是 checklist §139 / 任务 B 的判据）。若任务 B 过不了，则规则需与"锚文字"共存亡，而不是与"图"共存亡。
- 已定：先简单做（静态前置照旧），动态注入后面再考虑（YZ 已确认）。
- 09-08 深夜更新：**任务 B 已实证**该硬约束（真实 `FigContextManager` 老化 → 图超龄被摘 → 纯锚无规则重定位 delta 0），即锚自含成立。故「无图则规则删」的可行性有据；但**坐标教学必要性仍未定**——那要靠"衍生推理档"（用锚做新相对窗口）检验，若彼时模型混淆才推动态注入。

## 封存 / 暂停

### 认知图设计 + 4K 聊天机器人 MVP（08-30 晚 ~ 09-01 凌晨）

- 认知图设计探索期（checkpoint-1 ~ 13）已封存为预研：底层原语=节点+类型化关系、四通道/图无决策/情绪还原等结论是「图长出来该长什么样」的预研，非必须实现。
- 关键转折（checkpoint-12/13）：图必要性不在「抽象需要记忆」，而在上下文局限；方向改为「cu 跑起来后从痛点长出」。
- 4K 聊天机器人 MVP 暂停（记忆用文件组织 / 软预算+冗余 / 预算外包取舍自学，结论已定稿，暂不实施）。
- 归档：`checkpoint/archive/26-09-01-cog-graph-sealed/`（checkpoint-1~13 + handoff + status + interface-design-plan）。后续再看从 `handoff.md` 恢复。

## 已解决

- lm-service 三项遗留（internal_key 自带 base_url / tool call 内部化 / content 归一 content[]）→ **task-3 完成**（08-30，工位 B）：5 轮 mock 全绿 + 全量 733 passed + deepseek 真实验证全绿（tool call 同构 openai、arguments 真实 parse、strict 忽略不补）。过程 `work/B/checkpoint/`，任务 `tasks/task-3-lm-service-fixes.md`。
- get_members 30s 超时 → **根因自阻塞**（checkpoint-27 坐实，非此前「串行排队」）：phone 侧 telecom `_reader` 单协程 `await` 回调里同步 get_members 等 ack，而 ack 须同一 reader 读回 → 自阻塞 30s。已用 2A 修复（checkpoint-28，`3976401`）：reader 回调改 `asyncio.create_task` 异步分发，ack 仍同步读。只做 2A、不做 skip_pull（接受 first-message+members 空时双拉）。真机验证已完成（真人进退群驱动 members_changed，30s 消失确认）。
- Phone 是否主动拉全量成员 → 已实施（checkpoint-18）：`_ensure_group_session` members 空则拉 + `sync_groups()`（复用 daemon `list_real_groups`），`add_card` 成功分支自动 sync。
- 未登记真人/机器人消息静默丢弃 → **设计选择**：provider 登记账号代表可见范围，未登记即不可见，不做降级处理（非 bug）。
- Phone 抽象三待讨论点裁决 → 见本体 docs/phone-design.md + entries/2026-08-17-cogos-phone-design.md。
- Phase C 联调 3 bug（缺 patch 授权步 / 重试不可续 / 卡片无按钮）→ 见 entries/2026-08-14-cogos-bugfix.md。
- setup 调通中 2 bug（done 重复点击重跑建表 / finish 后卡片未拦截）→ 见 entries/2026-08-15-cogos-setup-verify.md。
