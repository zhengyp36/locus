# CogOS — setup 流程真机调通 + 3 项修复

> 2026-08-15。代码已提交（`19cf32b`），在 `~/codex/cogos`。

## setup 调通

卡片驱动 provider 创建流程真机调通：bs-bot 发 `/setup` → 卡片「开始创建」→ OAuth 建 admin-bot → patch 授权 → 配 scope → 建 bitable 7 表 → 写 admin_registry → 保存 provider，卡片逐行打勾。

`/resume` 代码完整，**未真机验证**（下一步）。

## 调通中修的 3 点

1. **卡片 done 后重复点击重跑建表**（`bs_card.py`）
   - 现象：手机 /setup 成功后，飞书端旧卡片仍可点，再点重走建表。
   - 根因：`handle_card_action` 的 `start` 分支只判 `running` 不判 `status`；done 后 running=False 无条件重跑。
   - 修复：start 先判 `status==done` → patch 回终态卡片 + toast，不再进 `_run_setup`。注意 `in_progress`+`running=False` 是正常首点，不能挡。
2. **finish_card 后卡片事件未拦截**（`session.py`）
   - 设计 G3f-card-design §3.2：finish 删 `cards/{message_id}` 索引 → 下次 card_action_trigger 报"卡片已失效"，不写 stream、不触发业务。
   - 现状：finish_card 删索引已做，但事件到达不查索引，`drain` 反而重建索引（与设计相反）。
   - 修复：新增 `Session.is_card_active()`；`on_event` 闭包在 `save_entry` 前对 `CardActionTriggered` 查活性，不活跃直接返回 toast"卡片已失效"。
3. **agent_registry 加 pin 列**（`bs_provider.py`）
   - `TABLES` 里 agent_registry 在 `status`（active/inactive）前加 `_text("pin")`。PIN 生成/鉴权逻辑仍未实现。

## 测试

- 全量 380 passed，1 failed（`test_workdir_switch` 因残留 daemon 进程干扰，与改动无关）。
