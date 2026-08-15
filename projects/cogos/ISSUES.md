# ISSUES

## 遗留（待处理）

### resume 重建账号与 setup 账号的字段差异

- `name`：resume 用 provider_name，setup 用 app 真实名（如 `COGOS008-ADMIN`）；是否还原 app 真实名待定。
- `patch_granted`：resume 无法从云端恢复（registry 未存），重建账号缺失；无功能风险，重走 setup 会再次引导 patch 授权。

### speak 用 user_id 发消息需额外权限

- `speak` 命令用 `user_id` 发消息需 `contact:user.employee_id:readonly` 权限；bs-bot 与管理员通信应统一用 `bot["open_id"]` + `receive_id_type="open_id"`。

## 已解决

- Phase C 联调 3 bug（缺 patch 授权步 / 重试不可续 / 卡片无按钮）→ 已修已提交 `54394c4`（2026-08-14），已联调验证通过（2026-08-15）。细节见 entries/2026-08-14-cogos-bugfix.md。
- setup 调通中发现的 2 bug：卡片 done 后重复点击重跑建表、finish 后卡片事件未拦截 → 已修已提交 `19cf32b`（2026-08-15）。
