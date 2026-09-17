# S3 报告｜拆第一人工依赖：触发（启动即跑）

> 2026-09-11。计划 `plan.md`，状态面 `state.md`，S2 `s2-report.md`，spec `cogos/docs/design-selfdrive-loop-s3.md`。
> 结论：**S3 达标**——壳可无人选一条并推进到 done；同时真机跑出 2 个新缺陷（work_dir 透传、验收空转），已修 / 已暴露。

## 一、范围与机制

- 触发从"人选（`--item`）"改为"壳选"：`pick_next` 挑第一条可无人推进的项（跳过 `done`/`needs_human`/`high-risk`；`todo` 优先于中断的 `in_progress`）。
- 无可推进项 → `no_work`：写 `runs.jsonl` 后直接退出，不建 Agent、不碰手机、不调模型（"不做"判据）。
- 安全件：只挑 low-risk；一次启动最多一条；work_dir 隔离；壳不 commit/push。

## 二、前置修复（S2 三缺陷，已实施）

1. `test_workdir_switch` 默认不跑：加 `COGOS_SERVICE_TESTS` 开关（保留 systemd `skipif`）。全量套件表现为 `1 skipped`，不再操作真实 `~/.cogos/feishu`。
2. `phone` 失败不再清 `is_default`：`_connect_card` 失败只改 status；新卡连上后才设默认；`init_phone` 补"有匹配 profile 卡但无默认卡则设默认"。
3. `loop._notify` 不再吞失败：重试 3 次退避，仍失败写本地 `notify_outbox.jsonl` 并标 `notify_failed`（runs.jsonl + 议程 notes）；dry 模式改输出结构化 notify 记录（原会把纯文本混进 runs.jsonl）。

三条各配回归测试；全量 1018 passed / 1 skipped。

## 三、真机三次运行（同一 agenda 项）

靶子 = `create_group-clear-error`：先提交一个**红的**回归测试 `TestCreateGroupClearError`（`create_group` 当前抛 `KeyError`），验收 = 该测试 + 全量套件。

| 次 | 结果 | 说明 |
|---|---|---|
| 1 | `done`（空转） | 验收就是"既有套件全绿"，模型**未改任何代码**也 done → 暴露"验收空转"（同 S2 清单第 4 条）。notify 因 daemon 短暂掉线失败 → 由缺陷③的 outbox/`notify_failed` 捕获（修复生效）。 |
| 2 | `needs_human / model_asked` | 模型报"测试不存在"并来问。根因=**work_dir 透传缺陷**：`--work-dir` 只作用于验收；模型工具仍绑 agent.json 的空目录，看不到仓库。 |
| 3 | **`done`（真增量）** | 修好 work_dir 后，模型自动把 `create_group` 的 `self._clients[...]` 改成 `_client_for(card)`，红测试转绿；notify 送达（`notify_failed: false`）。 |

- 三次都验证了触发/安全路径：自动选条、`model_asked` 停机、`done` 停机、通知成功/失败可见。
- 真机坐标无关；用的真实 deepseek（lm-service）+ 真实飞书（agent `COGOS002:A0005` → YZ `COGOS002:H0002`）。

## 四、新发现（真实缺陷 / 教训）

- **① work_dir 透传缺陷（已修）**：`Agent` 现接受 `work_dir` 覆盖，`loop` 透传，使模型工具与验收同目录。（`cogos/agent/app.py` + `loop.py`，`5c4b627`）
- **② 验收空转（未修，机制性）**：壳只认退出码，验收太弱就会"不改代码也 done"。对策已用上：**议程项先放红测试，验收 = 该测试 + 全量**，把"要做的事"编码进判据。是否把"红测试"提升为议程契约的一部分，待 YZ 讨论。
- **③ 环境偶发**：daemon 在工作目录/重启窗口内 `send_msg` 返回 `not started`；现由缺陷③机制兜底（可见 + 入 outbox）。daemon 工作目录被切到 `default-xxxx` 的历史副作用仍在（本会话已恢复 `default`）。
- **④ 模型会把 `send_msg` 用作"报告"而非"求助"**：`model_asked` 停机对"问"有效，但若模型只是发进度也会误停；已记录 `question` 文本便于事后判读（`5c4b627`）。是否区分"问/报"待讨论。

## 五、产出

- 代码（分支 `s2-selfdrive-loop`，已 push）：
  - `ff15a12` workdir 测试 opt-in；`74886d0` phone 默认卡；`7c728ba` S3 触发 + notify 可靠化；`42389ce`/`14fb517` 议程项 + 红测试；`5c4b627` work_dir 透传 + 问题记录；`9eb76cf` 无人跑出的 `create_group` 增量。
  - spec `cogos/docs/design-selfdrive-loop-s3.md`。
- 运行数据：`cogos-s2/runs.jsonl`；首次 outbox 证据 `/tmp/kilo/s3-first-run-outbox.jsonl`。

## 六、下一步（S4 候选，待 YZ 开题）

1. 常驻/定时（agent 自己醒来）——S3 只做"人启动一次"。
2. 消费人的回复 / 等待-续跑（S2 清单第 2 条）。
3. 议程契约是否强制"先红测试"（针对验收空转）。
4. 区分 `send_msg` 的"问"与"报"。
