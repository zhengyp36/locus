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

### 智能系统设计缺口（复习 agent-study 后确认，待补设计）

- **缺「过程元控制」**：有内容审视（显意识把关），无过程元控制（监控调度智能过程本身）。补法=预装三种子（自我状态可读 / 元动作可执行 / 反思回路），元策略自长。元动作已列继续/换路/求助/放弃，缺切换方法/扩大观察/折叠。
- **缺「诊断/调试观察」**：事件流 / 可观测性接口设计。阶段 1 认知树与执行器需要，否则调试盲区。已补进 cogos-plan.md 待定项。

## 已解决

- get_members 30s 超时 → **根因自阻塞**（checkpoint-27 坐实，非此前「串行排队」）：phone 侧 telecom `_reader` 单协程 `await` 回调里同步 get_members 等 ack，而 ack 须同一 reader 读回 → 自阻塞 30s。已用 2A 修复（checkpoint-28，`3976401`）：reader 回调改 `asyncio.create_task` 异步分发，ack 仍同步读。只做 2A、不做 skip_pull（接受 first-message+members 空时双拉）。真机验证已完成（真人进退群驱动 members_changed，30s 消失确认）。
- Phone 是否主动拉全量成员 → 已实施（checkpoint-18）：`_ensure_group_session` members 空则拉 + `sync_groups()`（复用 daemon `list_real_groups`），`add_card` 成功分支自动 sync。
- 未登记真人/机器人消息静默丢弃 → **设计选择**：provider 登记账号代表可见范围，未登记即不可见，不做降级处理（非 bug）。
- Phone 抽象三待讨论点裁决 → 见本体 docs/phone-design.md + entries/2026-08-17-cogos-phone-design.md。
- Phase C 联调 3 bug（缺 patch 授权步 / 重试不可续 / 卡片无按钮）→ 见 entries/2026-08-14-cogos-bugfix.md。
- setup 调通中 2 bug（done 重复点击重跑建表 / finish 后卡片未拦截）→ 见 entries/2026-08-15-cogos-setup-verify.md。
