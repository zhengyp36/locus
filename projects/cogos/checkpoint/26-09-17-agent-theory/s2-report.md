# S2 报告｜自驱回路首跑（最小可验靶子）

> 2026-09-11。计划 `plan.md`，状态面 `state.md`，spec `cogos/docs/design-selfdrive-loop-s1.md`。
> 结论：**壳跑通了**（一个真实增量 + verdict=done），并暴露出 7 条"人在哪被需要"与 3 个真实缺陷。

## 一、靶子与壳

- **靶子**（最小可验，不取候选 1）：`ensure-cloud-fallback-test`
  — 给 `AccountRef.ensure` 的"本地缺失 → 云端兜底"路径补单测，不改生产逻辑。
- **验收**（壳跑，不信模型自证）：`pytest tests/feishu -q` + `pytest -q`，全绿才算 done。
- **壳**：新增 `cogos/agent/loop.py`（薄壳）+ `Agent` 三个只读访问器；执行复用 `CogRuntime.cu` + `ToolRegistry`。分支/worktree：`s2-selfdrive-loop` @ `/home/zhengyp/work/A/cogos-s2`。
- **环境**：真实 deepseek（lm-service 本地）+ 真实飞书（agent `COGOS002:A0005` → YZ `COGOS002:H0002`）。

## 二、结果

- **verdict = done**（第 2 次重跑，第 1 步验收即全绿 `[0,0]`）。
- **真实增量**：agent 给 `tests/feishu/test_accounts.py` 新增 `TestEnsureCloudFallback`（2 用例）：
  - 本地文件缺失 → mock 云端 → 返回 active 账号；
  - 云端返回空 → ensure 返回 `{}`。
  未改生产代码，符合约束。`tests/feishu` 562 passed。
- **过程数据**：`cogos-s2/runs.jsonl`（4 条：首跑 step1/2 未过 → 重跑 step1 过 → done）。
- **通知**：真发了飞书（"开始…"已送达，YZ 实际收到并回复）。

## 三、"人在哪被需要"清单（S2 核心产出）

1. **触发**：本次靠人（我在命令行跑）。回路自己不会启动/续跑 → S3 首要拆除项。
2. **人的回复无法让回路继续**：模型若用 `send_msg` 问人，回路停下；且 S2 未启动 perception，人的回复根本没被消费 → L1 无"等待/续跑"。
3. **通知不可靠且失败被吞**：完成通知报 `not started`（见缺陷①）——壳只 log，不重试、不换通道；人可能永远收不到"卡住/完成"。
4. **验收质量壳管不了**：验收只看 pytest 退出码；模型写个空测试也能过。本次测试内容合理，但**判"测试有没有意义"仍需要人**。
5. **最终把关在人**：壳判 done ≠ 可合入。diff 未提交，需人 review（本报告第三节即为此）。
6. **环境依赖靠人**：真实通知要 lm-service + 飞书 daemon + card default 三者齐备；任一缺失，无人会自愈。
7. **风险项未触发**：`risk: high` 会在执行前停下等人批准，本次 low 未验证该分支。

## 四、意外发现（真实缺陷，均非壳引入）

- **① 全量 pytest 会操作真实运行环境**：`tests/feishu/test_workdir_switch.py` 直接用真实 `~/.cogos/feishu`（未隔离），全量验收运行时会改写 `global.json`、生成 `default-xxxx` 目录，并**把运行中的 feishu daemon 停掉** → agent 中途掉线（`no default card`/`not started`）。这正是首跑"神秘中断"与 daemon 两次掉线的根因。
- **② phone 失败会清 `is_default` 并持久化**：第一次连不上 daemon 时 `_connect_card` 把 `is_default=False` 写盘；之后 `init_phone` 因 `has_card` 为真不再设默认 → 后续发送一直 `no default card`。
- **③ 壳的 notify 失败仅吞掉**：`_notify` 捕获异常只打印，不影响 verdict → 自主运行时"失联"是静默的。

## 五、结论与下一步

- **壳（机制）成立**：议程 → 执行 → 验证 → 写回 → 通知 → 停/问 闭环跑通，且"模型不自证、壳跑判据"有效。
- **S2 达标**：跑通 + 清单完整（其中"人在哪被需要"7 条）。
- **代码已提交**（未 push）：分支 `s2-selfdrive-loop`，`91ff8dc`（壳）+ `c74f47e`（测试增量）。spec 随分支入库。
- **S3 前置修复（YZ 已认可，未实施）**：
  1. `test_workdir_switch.py` 默认不跑（显式 env 开关 `COGOS_SERVICE_TESTS` / `integration` 标记），不硬注释——保留按需可跑。
  2. `phone._connect_card` 失败只改 status、不动 `is_default`；`init_phone` 补设默认卡。
  3. `loop._notify` 失败不吞：重试退避 + 本地 outbox + `runs.jsonl`/status 标 `notify_failed`。
  三条做完再进 S3 拆"触发"。
