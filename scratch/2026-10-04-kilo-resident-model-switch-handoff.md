# handoff — kilo-resident 模型标注 / `/models` 切换 / per-chat 队列合并

## 状态

- 编码完成，已提交并推送：分支 `feat/kilo-phone`，commit **7f07fe6**（工程 `/home/zhengyp/work/A/kilo-resident`）。
- 验证：`npm run typecheck` 全绿；无 daemon 单测全过 —— `test:model-switch`、`test:inbound-ack`、`test:switch-busy-guard`、`test:permission-notify`、`test:session-isolation`、`test:inbound-post`。
- 未做：**未重启/部署 `kilo serve`（红线）**；未跑依赖 daemon(4097) 的集成测试（避免打扰 live 宿主）。

## 本次改动要点

1. 每条模型回复前缀 `▸ providerID/modelID`（`resolveReply`；per-bot `modelHeader` 可关）。
2. `/models` 列白名单（`config.models`，固定序）+ 当前模型（不在白名单则追加末尾），标当前。
3. `/models <N>` 设 `rt.pendingModel`，下一条 prompt 一次性带上（A'），对排队 drain 也生效；失败自动去覆盖重试一次。
4. per-chat 队列 + linger（`queue.coalesceMs`，默认 700ms）合并；回执状态机 coalescing/queued/processing，`ack` 语义上移到每批。
5. auto-handoff / session handoff 携带当前模型；`/new` 清 pending+batch，`/pin` 保留 pending。

设计与偏差记录：**`/home/zhengyp/work/A/kilo-resident/docs/model-switch-and-queue.md`**（含 TODO 勾选与 5 条偏差）。

## 下一步（新会话）

1. 对照 `docs/model-switch-and-queue.md` 逐条检视实现（重点：per-chat 队列与 `becameIdle` / auto-handoff 交互、回执去重、`pendingModel` 一次性语义）。
2. 发现问题直接修；偏差记录里"待检视确认"的条目给出结论。
3. 全部核完 → **飞书通知 YZ**（工具 `tools/feishu_notify.py`，默认 YZ）。

## 给新会话的第一句话（单列）

检视 kilo-resident（`/home/zhengyp/work/A/kilo-resident`）提交 7f07fe6：模型回复标注 + `/models` 切换 + per-chat 队列合并；对照设计文件 `docs/model-switch-and-queue.md` 逐条核对，修问题并确认偏差记录，完成后飞书通知 YZ。
