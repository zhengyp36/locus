# CogOS — /help 调整 + /query-agent（号码查询）

> 2026-08-15 会话。数据管理收尾：/help 排序 + bitable_url，新增 /query-agent。真机验证通过，提交 `8b690be`；add-human/add-agent 同步提交 `c540d15`。

## 决策

- /query-agent 数据源 = 云端 agent_registry 表（非本地 accounts），与 resume cloud-first 一致：单一权威源、5 字段一次拿全、换设备可查、status 准确（本地账号文件无 status 字段）。
- /query-agent admin_only=True（app_secret/pin 敏感；虽 bs-bot 只响应管理员，仍显式标注）。
- 号码输入支持剥前缀（`COGOS008:A0001` → `A0001`）。
- "admin-bot 已创建"判据 = `_load_admin(provider)` 成功（provider.json 有 admin-bot 指针 + 账号有 bitable_token）；cmd_help 里 try/except 静默跳过。
- /help 排序在 cmd_help 层实现（pop 提前），不改框架 list_commands。

## 实现

- `bs_setup.py` cmd_help：/help 排首位（pop 提前）+ provider 存在时打印 `bitable_url or bitable_token`。
- `bs_setup.py` cmd_query_agent：校验参数、剥前缀、调 query_agent、RuntimeError 转文本。
- `bs_agent.py` query_agent：`_load_admin` → `bh.query_records(agent_registry, filter='CurrentValue.[number]="Axxxx"')` → 取首条 fields → 5 字段摘要。`_cell_value` 归一化 str/list/dict 三种 Bitable 字段返回格式。

## 测试

- test_bs_agent.py 新增 TestCmdHelp（排序 + bitable_url 有无）、TestQueryAgent（found/not_found）、TestCmdQueryAgent（缺参/剥前缀/RuntimeError）。全量 416 passed +1 failed（test_workdir_switch 残留 daemon 干扰，无关）。

## 真机

- 用户确认验证通过。

## 遗留

- 无新遗留。agent 运行时（startup/send/shutdown + PIN 鉴权 + WS 激活 agent-bot）仍 ⏳，见 ROADMAP。
