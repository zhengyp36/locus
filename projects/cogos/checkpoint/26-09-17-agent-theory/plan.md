# plan｜cogos 自驱回路（L1 → L4）

> 2026-09-11 起。转向：从"视觉/机制细节"回到主线——造出能**自主驱动**的 cogos agent。
> 本文件是活计划（`../checkpoint/`，locus 外，`/undo` 不回退）。活文档规则见 `locus/CHECKPOINT.md`。
> 旧活文档 87 文件已归档：`locus/projects/cogos/checkpoint/26-09-11-live-checkpoint/`。

## 一、目标

agent = 模型 + 内化自省回路。要的是：**人不在场时 agent 自己思考并推进，人在场时一起裁决**。
把它拆成自主度阶梯，逐阶抬升，每阶可交付、可回退：

| 阶 | 能力 | 状态 |
|---|---|---|
| L0 | 给定任务，执行 | 基本有（cog-runtime 多轮） |
| L1 | 做完能自己验 | 半有；缺口 = 触发 + 通道 |
| L2 | 无人时自己启动/续跑下一步 | 无 |
| L3 | 自己决定"什么值得做"并排序 | 无 |
| L4 | 与人异步共驱、接管/交还 | 无（目标） |

**不押"实现 L4"**，押"把回路建起来、并逐阶抬升自主度"。每一阶都有可验证价值。

## 二、纪律（防止重蹈旧路）

1. **模型驱动、环境哑**：环境只提供可观测/渲染，不判对错、不替模型规划。
2. **过程式只用于机制**（回路怎么接、状态存哪、何时停）；**不用来设计 agent 的策略**（做什么、选哪条）——那是已作废的"把规划外包给程序"。
3. 每阶配**安全件**：验证 / 停止 / 不确定就问。
4. **验收换轴**：任务级成功率 + 自纠能力；不用 px 等代理指标。
5. **单次前向不可信**，关键结论要重复。

## 三、落点

| 内容 | 归处 |
|---|---|
| 计划/方向 | 本文 +（收口后）`locus/projects/cogos/ROADMAP.md` |
| 状态面（组件盘点 + 回路角色） | 本文目录草稿 → 收口进 `locus/projects/cogos/current.md` + `entries/` |
| 正式回路设计（契约/接口） | cogos 本体 `docs/` |
| 过程记录 | `../checkpoint/` |
| 协作规则变更 | `locus/projects/locus-meta/` |

## 四、阶段

### S0 收状态（先做）
- **产出**：组件状态面。每个组件一行：`名称 / 位置 / 状态(完成·半成·封存·阻塞) / 回路角色(议程源·触发·执行·验证·记忆)`。
- **验收**：一眼看出"回路还缺哪一格"。
- 备注：保命收编已完成——`/tmp/kilo` → `cogos/research/`；旧活文档归档 → locus 快照（均已 push）。

### S1 写最小回路 spec（L1）
- 链：`议程项 → 推进一小步 → 验证 → 写回 → 通知 → 停/问`。
- 每格用**已有件**填；填不出的格 = 缺口。
- **验收**：spec 不需要新建组件。

### S2 手工跑一遍
- 靶子：**最小可验**——小、可自动验收、无需决策（可为 `ISSUES.md` 某条的最小子切片，或临时造一条）；**不取候选 1**（通信层已收口、跨调用点重构、验收偏虚）。
- 以"YZ 不在"为约束走完回路。
- **产出**：一个真实增量 + **"人在哪被需要"清单**。
- **验收**：跑通 + 清单完整。
- ✅ 完成（2026-09-11）：verdict=done；产出见 `s2-report.md`（增量 = agent 补 `TestEnsureCloudFallback`；清单 7 条 + 3 个真实缺陷）。

### S3 拆第一个人工依赖（升 L2）
- **前置修复（S2 暴露，已定方案，未实施）**——无人触发前必须可靠可观测：
  1. `test_workdir_switch.py` 默认不跑（显式 env 开关 / `integration` 标记），消除全量验收的真实环境副作用。
  2. `phone._connect_card` 失败别清 `is_default`（只改 status）；`init_phone` 补设默认卡 → 防静默失联。
  3. `loop._notify` 失败不吞：重试 + 本地 outbox + `runs.jsonl`/status 标 `notify_failed`。
- 大概率是"触发"：会话开始/定时自动从议程拉一条并推进，人只事后复核。
- **验收**：无人触发下能推进一条且不自毁（含"不做"判据）。

### S4 逐阶抬升
- 每次只拆一个人工环节；每升一阶配一个安全件（验证件 → 停止件 → 提案机制 → 自主预算+交接）。
- **一阶一交付、可回退。**

## 五、进度

- [x] 保命：`/tmp/kilo` 收编进 `cogos/research/`；`../checkpoint` 归档进 locus 快照；旧活文档清理。
- [x] S0 收状态（`state.md`，YZ 已验收 2026-09-11）
- [x] S1 最小回路 spec（`cogos/docs/design-selfdrive-loop-s1.md`）
- [x] S2 手工跑一遍（`s2-report.md`；verdict=done + 人在哪被需要 7 条 + 3 缺陷）
- [x] S3 拆第一人工依赖（触发：启动即跑）——`s3-report.md`；自动选条 + `no_work` + 真机跑出并修 `create_group` 增量；分支 `s2-selfdrive-loop` 已 push
  - 前置三修复已实施（workdir 测试 opt-in / phone 默认卡 / notify 可靠化），全量 1018 passed
  - 真机另暴露并修复 "work_dir 未透传给模型工具"；遗留待讨论：验收空转、`send_msg` 问/报不分
- [ ] S4 逐阶抬升
  - 前置/时间线：**task-5（回路省时两件：验收遇错即止 + phase 计时）交工位 B**（`tasks/task-5-loop-verify-timing.md`，已 push）；讨论收敛"自驱 = 议程更新函数 f / ΔA"与"时间按信息增量分配"（见 `checkpoint-2.md`）。
  - 支点候选：**3（判据源 → agent）= 自驱缝 + 最大省人时**；1（常驻）/2（异步续跑）有"时间/服务 owner"理由；4（问/报）保人低频，放后。
  - ✅ 第一阶（判据源外移，红→绿两相）：`d417332`（已 push）；真靶 dogfood（COGOS_HOME 切片，`cogos-dogfood`）跑通运行 3 真 done；首跑暴露「零改动假 done」（flaky 验收 + `cu max_tokens=1000` 截断），最小修复 `4cf0f31`（变更绑定守卫 + cu error message，未 push）；报告 `dogfood/report.md`。
  - ✅ 真靶 #2（`list_timers`，worktree `cogos-dogfood-timer`）干净跑通（baseline 绿→criterion 红→implement 绿，无异常状态）；两笔产出（COGOS_HOME + list_timers）已 cherry-pick 合入 `s2-selfdrive-loop`（本地领先 origin 2，未 push，全量 1052 passed）。报告 `dogfood-timer/report.md`；**新会话入口 `status.md`**。
