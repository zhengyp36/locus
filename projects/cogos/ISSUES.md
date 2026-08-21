# ISSUES

## 遗留（待处理）

### sessions 软链接：群改名同步暂未实现

- 群改名时 group/ 下的软链接仍用首次群名，不更新/重链（规则定为「只用第一次名字」）；作为遗留，需 YZ 知悉，后续补。

### Phone 抽象待讨论点（设计定稿，见 entries/2026-08-17-cogos-phone-design.md）

- 会话项是否暴露号码：一个联系人两个号 → 两个同名 p2p 会话，光看 title 分不清；是否在会话项额外暴露 `number` 字段待定。
- 群聊链路：`send(chat)` 依赖通信层群发，而通信层「群聊 send / to_targets @ / 群内 bot 消息 app_id 反查」仍留空；群会话「已绑定卡」机制未定；主动建群（create group）暂缺。
- 本地目录数据模型 + 对象字段（Msg/Chat/Contact/Card）：实现时再讨论。

### 未登记真人消息被静默丢弃

- 群聊里真人 sender 经 `_resolve_human` 解析 `user_id`→number（本地 human-*.json → 云端 human bitable），三级都查不到就返回 `None`，`route_message` 直接丢消息；未登记的群内真人发消息，agent 收不到且无日志/提示。是否对未知真人降级处理（如用 user_id 兜底、记录告警）待定。

### resume 重建账号与 setup 账号的字段差异

- `name`：resume 用 provider_name，setup 用 app 真实名（如 `COGOS008-ADMIN`）；是否还原 app 真实名待定。
- `patch_granted`：resume 无法从云端恢复（registry 未存），重建账号缺失；无功能风险，重走 setup 会再次引导 patch 授权。

### 账号失效机制的两处遗留（机制已实现，缺口仍在）

- **注销是最终一致、非强保证**：离线设备靠 fail-open（云端不可达不主动失效、5 分钟重试）可无限期续命，最坏失效延迟 = 12h TTL + 重试窗口。与「号码唯一性=纪律非软件保证」同类折中，需 YZ 知悉。
- **无 revoke 命令**（暂不实现，短期无失效必要）：`agent_registry.status` 目前只有 `"active"`，没有把 status 改为 inactive 的入口，失效机制真机端到端不可触发（只能 mock 单测）。

## 已解决

- Phase C 联调 3 bug（缺 patch 授权步 / 重试不可续 / 卡片无按钮）→ 见 entries/2026-08-14-cogos-bugfix.md。
- setup 调通中 2 bug（done 重复点击重跑建表 / finish 后卡片未拦截）→ 见 entries/2026-08-15-cogos-setup-verify.md。
