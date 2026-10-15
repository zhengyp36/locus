# 2026-10-04 · 模型标注 / `/models` 切换 / per-chat 队列合并

## 结论

三件咬合在 bridge 入站→排队→注入→回复主链路上的事，落地 feat/kilo-phone（`7f07fe6`，已 push）：

1. **模型回复标注**：`resolveReply` 拼 body 处前缀一行 `▸ providerID/modelID`（取自 assistant 消息实际作答模型，最后一条完成消息）。只加在模型回复上；ack/审批/timer/terminal/context 通知不加；仅飞书侧渲染，不进 session 上下文。per-bot `modelHeader`（默认 true）可关。
2. **`/models` 查看**：列表＝白名单固定顺序 + 当前模型（不在白名单才追加末尾），标当前；label 从 `provider.list.name` 取，取不到回退 id。
3. **`/models <N>` 切换**：N 按规范列表解析（跨重启稳，不依赖上次快照）。机制 **A'＝一次性 `rt.pendingModel`**：只设 pending，下一条 prompt（含排队 drain）带上一次、成功后清，之后靠 session 记住。**在构建 prompt 时解析模型**，故对排队 drain 也立即生效，正在跑的那轮不受影响。纯内存动作，**忙碌也允许**。
4. **per-chat 队列 + linger 合并**：队列从 per-runtime 单队列改 **per-chat**；入站进该 chat 的 batch 并重置 linger 定时器（`queue.coalesceMs`，默认 700ms），静默到才 drain，整批合并成**一个 prompt** → 一次 `resolveReply` → 一条回复。
5. **回执状态机上移**：coalescing（连发中，静默）/ queued（静默到但正忙，回一次「已排队」）/ processing（drain，回一次「开始处理」）；`ack: always|delayed|off` 粒度上移到**每批**，绝不逐条 ack。系统消息不带模型头部。
6. **交互修正**：auto-handoff / session handoff 携带「当前模型」（`rt.pendingModel ?? sessionModel`）；`switchSession` 队列清理、`tryDispatch`/`requestAutoHandoff` 的「队列非空」判定改为「任一 chat batch 非空」。

设计/施工/偏差/检视全记录在**本体** `docs/model-switch-and-queue.md`（§1–10 + 偏差记录 + 检视结论 + 后续变更）。

## 检视（10-04 后续会话核对 7f07fe6，修复见 `13ed24a`）

- **真 bug：turn-boundary drain 永久短路**。`becameIdle` 先置 `rt.resolving = true`，再用含 `!resolving` 的 `canStartTurn` 作 drain 门 → 门恒 false。「在忙时静默、已 ready」的批在其后 idle 永不 drain（多 chat 卡死）。修法：抽出 `turnFree`（只含 `!busy/!inflight/!handoffRunning`），`becameIdle`/`drainChat` 改用它，`onQuiet` 仍用 `canStartTurn`。回归测试 `test/inbound-ack.ts` "batch drains at the turn boundary"。
- `/new` 未清 `pendingModel`（违反 §8）→ 切会话前补清，吃新会话默认。
- processing 单条措辞对齐 §7；白名单非法项补 `warn`（§2 要求「跳过并 warn」）。

## 后续变更（`9c174fe`）

- `/new` 默认模型：由「吃新会话默认」改为**设 pending＝白名单首个模型**（成功回执追加一行 `模型：providerID/modelID`）；白名单空则回退 `undefined`。仅飞书 `/new`，启动/pin 失效新建/显式 handoff/auto-handoff 均不变。

## why（关键判断）

- **A' 一次性 pending 而非改 config.model**：切换只影响「其后消息」，不污染全局、不重启；pending 一次性消费，之后靠 session 自身记住模型。
- **per-chat 队列**：同 chat 连发（尤其复制粘贴/自动编号多段）应合成一次调用，避免逐条触发多轮；linger 静默窗口即合并时机。
- **ack 上移到每批**：逐条 ack 会被合并后语义错位；每批最多两条信号（排队 + 开始处理）各自去重。回执核心价值＝区分「收到 / 没收到」。
- **失败重试一次兜底**：`pendingModel` 致 prompt 失败时，自动清覆盖、用会话当前模型重试一次再回执，比设计「清 pending + 报错」更不易丢消息。
- **切换不强制校验 connected**：白名单本就是人工策展，只校验目标属白名单；connected 仅在 `/models` 列表以「不可用」提示，不阻断。

## 偏差（均确认成立）

1. 合并用单个 text（`join("\n\n")`）而非多个 text part（管线单文本签名；同消息内多段文本语义等价）。
2. 模型失败多一层兜底重试（见 why）。
3. 切换未强制校验 connected。
4. `providerCatalog.available`：`provider.list` 读失败时不再把全部模型误标「不可用」。
5. `config.json` 为 gitignore → `models` 落提交的 `config.example.json`，同步到本地 config.json（不提交）。

## 被否 / 保留边界

- **「先发 /models 再按快照切换」**被否：改用规范列表解析，跨重启稳、少一步。
- **`/compact` 跟随新机制**被否：仍用固定 `config.model`，本次不动。
- **通知类 wake 消费 `pendingModel`** 被否（保留）：`pendingModel` 只被下一条**用户入站** prompt（含排队批）消费；timer/terminal/context 通知走 `dispatchBatch`，不带也不消费——否则可能抢在用户消息前清掉 pending。设计 §5「其后消息」指用户消息。

## 验证

- `npm run typecheck` 全绿；无 daemon 单测全过：`test:model-switch`、`inbound-ack`（按新 batch 语义重写）、`switch-busy-guard`、`permission-notify`、`session-isolation`、`inbound-post`。
- **未做**：未重启/部署 `kilo serve`（红线）；未跑依赖 daemon(4097) 的集成测试（避免打扰 live 宿主）。
