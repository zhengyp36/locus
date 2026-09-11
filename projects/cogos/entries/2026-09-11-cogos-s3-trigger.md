# 2026-09-11 cogos S3：触发（启动即跑）+ 前置三修复

关联：`checkpoint/s3-report.md`、`checkpoint/status.md`、`cogos/docs/design-selfdrive-loop-s3.md`、entry `2026-09-11-cogos-selfdrive-pivot.md`。

## 做什么

拆掉 S2 回路第一个人工格"触发"。从"人用 `--item` 指定"改为"壳自动选条"。

## 前置三修复（S2 暴露）

1. `tests/feishu/test_workdir_switch.py`：加 `COGOS_SERVICE_TESTS` 开关（外加 systemd `skipif`），默认跳过。此前全量套件会操作真实 `~/.cogos/feishu`、停 daemon。
2. `cogos/phone/phone.py`：`_connect_card` 失败只改 status（原会 `is_default=False` 并持久化 → 静默失联）；`add_card` 改为连上后才设默认；`config.init_phone` 补"有匹配 profile 卡但无默认卡则设默认"。
3. `cogos/agent/loop.py`：`_notify` 重试 3 次退避，仍失败写 `notify_outbox.jsonl` 并标 `notify_failed`（runs.jsonl + 议程 notes）；dry 模式输出结构化 `notify` 记录（原会把纯文本混进 runs.jsonl）。

## S3 机制

- `eligible_items` / `pick_next`：跳 `done`/`needs_human`/`risk:high`；`todo` 优先于中断的 `in_progress`；组内保持议程顺序。
- 无候选 → `no_work`：记 runs.jsonl 后退出，不建 Agent、不碰手机、不调模型。
- 安全件：只挑 low-risk；一次一条；壳不 commit/push。

## 真机三次（同一项，先提交红测试 `TestCreateGroupClearError`）

- run1 `done` 但**零改动** → 暴露"验收空转"：验收=既有套件全绿，模型不动手也能过。同 S2 清单第 4 条。
- run2 `needs_human/model_asked`：模型报"测试不存在"。根因=**`--work-dir` 只作用于验收，模型工具仍绑 agent.json 的空目录**。
- 修 `Agent(work_dir=)` + loop 透传后，run3 `done`：模型把 `create_group` 的 `self._clients[...]` 改成 `_client_for(card)`，红测试转绿。

## 关键结论 / 待 YZ 讨论

- 触发与安全路径（自动选条、`model_asked` 停机、done 停机、通知成功/失败可见）全跑通。
- **work_dir 必须让"模型工具"和"验收"同目录**，否则回路空转或误问。
- **验收空转**是机制性风险：对策=议程项先放红测试、验收含该测试；是否升为议程契约待定。
- 模型会把 `send_msg` 当"报告"用，`model_asked` 会误停；已记录 `question` 文本，问/报是否区分待定。
- 环境：daemon 工作目录会被切到 `default-xxxx`（历史副作用），跑前确认 `global.json=default`；`send_msg` 偶发 `not started` 由 outbox 兜底。

## 落点

- 代码：分支 `s2-selfdrive-loop`（已 push）；commit `ff15a12`/`74886d0`/`7c728ba`/`42389ce`/`14fb517`/`5c4b627`/`9eb76cf`。
- 下一步 S4 候选：常驻/定时、消费人的回复、验收契约、问/报区分。
