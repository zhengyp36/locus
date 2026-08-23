# ISSUES

## 遗留（待处理）

### sessions 软链接：群改名同步暂未实现

- 群改名时 group/ 下的软链接仍用首次群名，不更新/重链（规则定为「只用第一次名字」）；作为遗留，需 YZ 知悉，后续补。

### resume 重建账号与 setup 账号的字段差异

- `name`：resume 用 provider_name，setup 用 app 真实名（如 `COGOS008-ADMIN`）；是否还原 app 真实名待定。
- `patch_granted`：resume 无法从云端恢复（registry 未存），重建账号缺失；无功能风险，重走 setup 会再次引导 patch 授权。

### 账号失效机制的两处遗留（机制已实现，缺口仍在）

- **注销是最终一致、非强保证**：离线设备靠 fail-open（云端不可达不主动失效、5 分钟重试）可无限期续命，最坏失效延迟 = 12h TTL + 重试窗口。与「号码唯一性=纪律非软件保证」同类折中，需 YZ 知悉。
- **无 revoke 命令**（暂不实现，短期无失效必要）：`agent_registry.status` 目前只有 `"active"`，没有把 status 改为 inactive 的入口，失效机制真机端到端不可触发（只能 mock 单测）。

### Phone get_members 兜底在并发成员事件下的排队超时（未优化）

- 真机（checkpoint-21/22）：真人进退群连发 `user.added/deleted_v1`，每个触发 `emit_members_changed` → `resolve_group_members` → `tracker.rebuild()`（`_build_lock` 串行），叠加 phone 侧 `_ensure_group_session` 又发 get_members，多个 rebuild 锁上排队累积到 30s（REQUEST_TIMEOUT），members 更新拖慢 ~30s；正确性无碍（members_changed 帧 added 兜底）。实测单次 HTTP 快（get_members 2.73s / list_messages 0.51s / list_members 0.36s），归因是串行排队而非单次回放慢。
- 优化方向（未实施）：`_make_on_members_changed` 已有 added/removed，可跳过 `_ensure_group_session` 的 get_members 兜底（加 `skip_pull` 参数），仅收群消息路径保留兜底。

## 已解决

- Phone 是否主动拉全量成员 → 已实施（checkpoint-18）：`_ensure_group_session` members 空则拉 + `sync_groups()`（复用 daemon `list_real_groups`），`add_card` 成功分支自动 sync。
- 未登记真人/机器人消息静默丢弃 → **设计选择**：provider 登记账号代表可见范围，未登记即不可见，不做降级处理（非 bug）。
- Phone 抽象三待讨论点裁决 → 见本体 docs/phone-design.md + entries/2026-08-17-cogos-phone-design.md。
- Phase C 联调 3 bug（缺 patch 授权步 / 重试不可续 / 卡片无按钮）→ 见 entries/2026-08-14-cogos-bugfix.md。
- setup 调通中 2 bug（done 重复点击重跑建表 / finish 后卡片未拦截）→ 见 entries/2026-08-15-cogos-setup-verify.md。
