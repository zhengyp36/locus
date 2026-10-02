# handoff-02 · 经历轴读侧已落地；剩真身份 e2e（交接待续）

> 交接自：10-03 执行会话（承 `handoff-01`）。上游＝`README.md`（认可口径）· `DECISIONS.md`（自决＋结果）· `experience-py-shape.md`（最小形状）· 收口件 `projects/cogos/entries/2026-10-03-cogos-experience-axis-readback.md`。

## 一句话

第二刀（`experience.py` 读侧 ＋ 回边）**已落地、机制/行为均验、已提交**；剩余只有**真身份 e2e**（需真发飞书＝外溢＋第二账号编排，须 YZ 在真机确认），其余为下一刀（P7/P8）。

## 第一句话（给新会话，单列）

读 `scratch/2026-10-03-experience-axis/handoff-02.md` 并照它开工；先确认代码已在 `7a67fc3`、收口件已入 memory。

## 已完成（勿重做）

- cogos `7a67fc3`（**未 push**）：`agent/experience.py`（段 schema＋读侧 `by_time/by_person/open_knots/by_thread`＋`retrieve`/`open_knots`）· `consciousness.py` 回边（`recall` 开关）· `flow.py` re-export · `app.py` 透传 · 测试 `tests/agent/test_experience.py`＋跨事件 · 探针 `scripts/exp_experience_recall.py`。
- 验证：`tests/agent tests/cog_runtime` 324 passed/3 skipped；全量 1290 passed（1 无关 image_ctx 素材缺失 fail）；真模型探针 recall on/off **分叉=True**。
- locus：`12f981a`(memory) `b052164`(scratch)。

## 剩余（按优先级）

1. **真身份 e2e**（handoff-01 的验收 C 第 3 条）：真 daemon＋真 app `~/.cogos/agent/tangyu`，真发飞书 `A0001→A0005` 两事件，确认跨事件 `open_knots` 稳定、公开入口在新代码下不崩。**须 YZ 知悉/配合**（外溢＋第二账号）。方法见 `current.md` 09-28 S5 与第一刀 entry §3；`scripts/send_msg.py` / `scripts/exp_verify_phone_e2e.py` 可参考。
2. （可选）push cogos `7a67fc3` 到 origin master。
3. 下一刀方向：**P7 判结主体**（谁写 `结`）· **P8 关联怎么打**（装载直取入口）——本刀只做了机械退化解。

## 纪律（同 handoff-01）

目标导向自决、决策当场记录、结束汇总；命令用 terminal；`start_context_watch` 20s/120K；链条上限 5 跳；提交前跑测试；红线＝secrets/不可逆/外溢。清异步源顺序见 handoff-01 §纪律。

## 遗留 / 洞

`host` 无生产者 · 权重=0 · 主题/工具索引 · 误差切点 · 后压/蒸馏 · 读时现整（均按认可口径搁置）· `thread=id/refs=[]/主题/预测` 占位待升级 · 命名 `经历轴→时间轴` 未收口。
