# ENTRY · cogos toolbox FIX（交接 + 本会话恢复入口）

**一句话**：本会话已讨论完 toolbox 的 6 条改进建议（含评估，新增 N1~N4），并发出新会话执行修复；**本会话不封笔**，留作继续讨论。用户 `/undo` 回退消息后，**重读本文件即可恢复讨论上下文**。

## 本会话讨论情况（恢复用）

- **对象**：`scratch/2026-09-28-cogos-toolbox-improvements.md`（6 条建议 + N1~N4）。
- **证据**：`../projects/cogos/entries/2026-09-28-cogos-toolbox-behaviour-probe.md` —— 16 次真实模型 + FakeTelecom 复跑：16/16 首调用前不 help、先猜错 `to`→撞裸 Python 异常→靠 help 自纠；16/16 外发 2 条（重复外发 bug）。
- **逐条讨论**：第 1~4 条已逐条讨论（好处 / 做法 / 取舍）；第 5 条搁置；第 6 条为必修 bug（未单列讨论）。
- **评估结论**：整体成立；主线 = 机制面退出模型面 + 错误便宜化。
- **评估新增 N1~N4**（见 improvements 文件 §评估补充）：
  - **N1** 暴露但用不起来（`open`/`list`/`answer_auth`）——**方向岔路，需 YZ 裁**；
  - **N2** catalog↔registry 缺一致性自检；
  - **N3** `run` 固定 ~6s 等待可能截断输出；
  - **N4** `cancel` 能力未进 catalog（是否有意）。
- **待 YZ 拍**：N1 方向（撤下 vs 补齐 id 传参）；是否纳入 N3/N4。

## 交接给新会话（执行）

- **标题**：`26-09-28-cogos-toolbox-fix`
  - 原拟 `26/09/28-cogos 工具呈现-FIX-12`：斜杠不符库内惯例（`26-09-28`），且 `FIX-12` 只指 1、2 条、与实际范围（6/1+2/3/N2）不符 → 已改。
- **首句**：见文件 `/tmp/kilo/handoff-first-line.txt`（内容同下"首句原文"）。
- **修复范围 / 顺序**：`6`（必修 bug）→ `1+2`（同批）→ `3` → `N2`；`4` 在 1+2 后用 harness 度量；`N3/N4` 待确认；`5` 搁置。
- **待裁**：N1 方向 → 带倾向求助 YZ，不得自决。
- **纪律**：先加载 `rules/task.md` 并复述；不得 `--auto`；提交前跑 `python3.11 -m pytest tests/agent`。
- **起会话结果**：见文末"交接执行记录"。

### 首句原文

```
执行：先加载并复述 rules/task.md；再读 scratch/ENTRY.md（滚动状态）→ scratch/2026-09-28-cogos-toolbox-improvements.md（6 条建议+N1~N4）→ projects/cogos/entries/2026-09-28-cogos-toolbox-behaviour-probe.md（证据）。修复顺序：6（必修 bug：cogos/agent/consciousness.py:52 去重判断写死 send_msg，改为在 registry 层记"是否已 send"并覆盖 message/file）→ 1+2（toolbox 调用边界按 catalog 校验参数 + 结构化可读错误，同批）→ 3（help 删除"绑定"行）→ N2（catalog↔registry 启动期一致性断言）；4 在 1+2 后用 scripts/exp_agent_behaviour_probe.py 跑 reps 度量往返数。N1（撤下 open/list+answer_auth vs 补齐 id 传参=多会话）是方向岔路，须带倾向求助 YZ、不得自决；N3/N4 待确认；建议 5 搁置。提交前跑 python3.11 -m pytest tests/agent；不得 --auto。
```

## 交接执行记录

- （待填）handoff.py 起会话时间 / 新会话是否确认已起。

## 下一步

- 用户 `/undo` → 本文件即恢复入口；新会话并行自行修复；本会话可继续讨论（尤其 N1 方向裁断）。
