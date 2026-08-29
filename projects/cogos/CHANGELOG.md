# CHANGELOG

> 只记阶段级里程碑（成果 + 时间 + 锚点）。每日变更流水、commit、测试数在 git log 与 entries/ 里。

## 阶段 1 · 通信层基建（08-07 ~ 08-14）

从零搭起飞书通信底座：环境/设备/账号、WS/Session、收发卡片、命令机制、provider 搭建与 setup 真机调通。

- 初始提交 + 环境管理 + secrets 类型系统（bot/human）+ core.Lib
- WS/Session 设计 + 卡片消息 + FileLock + history 落地
- 命令机制（`@msg_command`）+ provider 编排（OAuth → scope → Bitable 7 表 → 注册）
- 卡片驱动 provider setup 真机调通 + Phase C 联调修复

→ 细节：entries/（08-12 ~ 08-14 系列，含 setup / comm-testing / bugfix）
→ 设计：docs/comm-full-design.md

## 阶段 2 · agent 接入 + 群聊（08-15 ~ 08-21）

agent 长连接与账号体系落地，打通群聊：agent-term、账号失效/刷新、Telecom 接口抽象、群操作、bot 间 p2p。

- agent-term 长连接（鉴权/心跳）+ 账号失效/刷新 + resume cloud-first
- Telecom 接口抽象 + 真机通信接口实现
- 群操作（me_join 唯一路径）+ bot 间 p2p（双 bot 群 + @all）+ 群聊收发/命令/区分

→ 细节：entries/（08-15 ~ 08-21 系列）
→ 设计：docs/agent-account-refresh-design.md + docs/agent-term-design.md

## 阶段 3 · phone 收口（08-22 ~ 08-24）

Phone 抽象落地（agent 侧 API），真机验证全绿，通信层收口。

- Phone 四件（model/store/fake/phone）+ 接真机 + TUI 交互终端
- 真机验证全绿（668 passed）+ get_members 30s 自阻塞根治

→ 细节：entries/2026-08-22-cogos-phone-stage-a-done.md + checkpoint/archive/26-08-24/
→ 用法：docs/phone-usage.md

## 阶段 4 · 智能系统设计（08-24 ~ 08-26）

智能系统方向收敛为概念体系 + 开发计划，进入实施。无代码变更。

- 概念体系 → docs/cogos-concept-system.md
- 开发计划 → docs/cogos-plan.md（底层三件 → 子系统 → 整系统）
- 理论摘要 → docs/cogos-design-theory-summary.md
- agent-study 已确认结论复习 → 挂接点固化 docs/agent-study-hooks.md；元控制二分（资源级/认知级）；缺口进 ISSUES

→ 过程：checkpoint/archive/26-08-26/ + checkpoint/archive/26-08-27-agent-study-review/

## 阶段 5 · 底层三件设计收敛 + 进入并行实施（08-27 ~ 08-29）

lm-service 最小版设计收敛为 v1，cog-runtime 雏形已出，进入「工位 B 实施 lm-service / 工位 A 讨论 cog-runtime」并行。

- lm-service 设计 → docs/design-lm-service-min.md（LmClient 冻结契约 / category 六类 / 三文件分离 / router 模态>tier / 调试记录）
- cog-runtime 雏形 → 活文档 design-cog-runtime.md（继续讨论）
- 任务清单 → tasks/（task-1 lm-service 工位 B + task-2 cog-runtime 工位 A）

→ 过程：checkpoint/archive/26-08-29-impl-design/
