# handoff-02 · 经历轴读侧已落地；剩真身份 e2e（交接待续）

> 交接自：10-03 执行会话（承 `handoff-01`）。上游＝`README.md`（认可口径）· `DECISIONS.md`（自决＋结果）· `experience-py-shape.md`（最小形状）· 收口件 `projects/cogos/entries/2026-10-03-cogos-experience-axis-readback.md`。

## 一句话

第二刀（`experience.py` 读侧 ＋ 回边）**已落地、机制/行为/真身份 e2e 均验、已 push**；P8 关联**机械第一刀**已续跑落码（cogos `9775293` 已 push）。当前无进行中任务，**下一刀方向未定、待 YZ**（关联读侧用法 / 模型抽取＋锚分类学）。

## 第一句话（给新会话，单列）

读 `scratch/2026-10-03-experience-axis/handoff-02.md` 并照它开工；先确认代码已在 `9775293`、收口件（第二刀＋P8）已入 memory。

## 已完成（勿重做）

- cogos `7a67fc3`（**已 push**）：`agent/experience.py`（段 schema＋读侧 `by_time/by_person/open_knots/by_thread`＋`retrieve`/`open_knots`）· `consciousness.py` 回边（`recall` 开关）· `flow.py` re-export · `app.py` 透传 · 测试 `tests/agent/test_experience.py`＋跨事件 · 探针 `scripts/exp_experience_recall.py`。
- 验证：`tests/agent tests/cog_runtime` 324 passed/3 skipped；全量 1290 passed（1 无关 image_ctx 素材缺失 fail）；真模型探针 recall on/off **分叉=True**。
- locus：`12f981a`(memory) `b052164`(scratch)。

## 剩余（按优先级）

1. ~~**真身份 e2e**（handoff-01 的验收 C 第 3 条）~~ **已完成（10-03，YZ 授权）**：真 daemon＋lm-service＋真 app `tangyu`，A0001 真发两事件；事件 2 装载读回事件 1 同来源近段（ground truth＝`calls.jsonl`），`open_knots` 稳定空、旧段兼容、公开入口未崩。证据已转存 `projects/cogos/checkpoint/26-10-03-experience-axis/e2e-readback-evidence.md`。
2. ~~（可选）push cogos `7a67fc3` 到 origin master~~ **已完成**（`91fd1de..7a67fc3`；locus 亦 push）。
3. ~~**下一刀方向＝P8 关联怎么打**（YZ 10-03 定）~~ **机械第一刀已落（10-03，自治续跑）**：`open_thread_for`/`continuation_for`＋`_land` 续线（D8 按**线**判开放，修掉段级续线漏）；cogos **`9775293`（已 push）**。决策 `DECISIONS.md`「P8 关联第一刀」；收口件 `entries/2026-10-03-cogos-p8-association-mechanical.md`。
4. **下一刀方向（未定，待 YZ）**：a) 关联**读侧用法**——装载按 `thread` 取回整线（现在关联只写不读）；b) 模型抽取关联＋**P8 锚分类学**；c) 人/关系/坐标怎么落。

## 纪律（同 handoff-01）

目标导向自决、决策当场记录、结束汇总；命令用 terminal；`start_context_watch` 20s/120K；链条上限 5 跳；提交前跑测试；红线＝secrets/不可逆/外溢。清异步源顺序见 handoff-01 §纪律。

## 遗留 / 洞

`host` 无生产者 · 权重=0 · 主题/工具索引 · 误差切点 · 后压/蒸馏 · 读时现整（均按认可口径搁置）· `主题/预测` 仍占位（`thread/refs` 已随 P8 续线升级）· 命名 `经历轴→时间轴` 未收口。
P8 洞：一人多开放线只取最近 · `open_knots()`（段级）与续线（线级）口径暂不一致 · 关联**无读侧用法**（只写）· thread 关闭无「兑现/放弃」细分。
