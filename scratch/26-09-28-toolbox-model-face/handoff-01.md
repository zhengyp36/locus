# handoff｜toolbox 模型面修订 · 新会话入口 · 2026-09-28

> **新会话任务**：先做 **批 0 验证闸**；通过后依批 1（N4）→ 批 2（N3）→ 批 3（`to`）。工作单目录同此。

## 入口（按序）

1. **本目录 `plan-toolbox-model-face.md`** ← 先读（目标/三界/批次/验收/被否/纪律）。
2. **`/home/zhengyp/work/B/locus/rules/task.md`** ← 加载并**复述确认**。
3. 权威设计：`/home/zhengyp/work/B/cogos/docs/design-agent-tools.md` §5.1／§5.2／§5.4／§19。
4. 记忆依据：`/home/zhengyp/work/B/locus/projects/cogos/entries/2026-09-28-cogos-toolbox-run-semantics.md`、`...-model-prior-naming.md`、`...-behaviour-probe.md`、`...-fix.md`。

## 环境（B 工位）

- cwd = `/home/zhengyp/work/B/cogos`；**先验** `python3.11 -c "import cogos; print(cogos.__file__)"` → 必须 `/home/zhengyp/work/B/cogos/...`。
- 测试：`python3.11 -m pytest tests/agent`（＋全量）。
- harness：`scripts/exp_agent_behaviour_probe.py`（用真实模型，**连现有 lm-service，不自起**）。

## 第一步：批 0 验证闸（必做，先于任何代码改动）

- 目标：验证「`run` 发起即返回 + `read`/`observe` 取值」这条路，模型**走得通**、往返可接受。
- 方法：可先用 harness 改造/新增一个探针，给模型"发起即返回的 run + observe/read"，看它能否**自己**用重定向+读文件取到命令输出；跑 reps（n≥10）看分布。
- 判据：能稳定取到、往返可接受 → 进入批 1；**否则停回讨论**（不硬推，可能改走过渡方案：run 返回加 `settled`）。

## 纪律

- 不得 `--auto`；提交前跑测试；默认自主提交/推送。
- 发现设计问题记 checkpoint，不悄悄改；三界见 plan §1。
- 一批一会话；每批收工写 `handoff-0N.md`（入口/已完成/未完成/验证/新发现/下一批/待 YZ）。

## 通知 YZ

- 完成或遇问题 → `/home/zhengyp/work/B/locus/tools/feishu_notify.py "..."`。
