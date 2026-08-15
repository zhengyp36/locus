# ROADMAP

## 当前阶段

通信层（comm）Phase 0/1/A/C 已完成并真机调通；provider.json = 3 字段索引层已落地（`d84660d`）。`/resume` 已 cloud-first 重写（`a0e1092`）并跨设备真机验证通过，半恢复已裁决推迟（见 entries/2026-08-15-cogos-resume-verify.md）。数据管理 `/add-human` `/add-agent` `/query-agent` 已实现并真机验证通过（号码分配 + counter 接线 + PIN 生成 + agent-bot 卡片创建 + 云端查询），已提交 `c540d15` `8b690be`；`/help` 排首位并打印 bitable_url。agent-term 架子已实现（`5094ba8`，channel 协议 + daemon 长连接 + term 交互终端 + startup PIN 鉴权）；账号失效/刷新已实现（`docs/agent-account-refresh-design.md`，refresh 无返回值 + load 判定 + 12h 失效 + 心跳重校验，456 passed，`ae02c0b`）。

## 下一阶段方向（来自实验 5 的 AI 独立评估，优先级降序）

1. 调试验证（resume 跨设备已验，半恢复已裁决推迟 —— 收尾完成）
2. 可靠性 / 可观测性
3. 持久化
4. 认知树 + InferNode
5. agent 运行时
6. 权限
