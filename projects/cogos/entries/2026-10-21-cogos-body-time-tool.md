# body time 组落码 · now / wait / remind（2026-10-21）

> **状态：已落码**（cogos `e44fd0c`）。术语权威见 glossary「wait / remind（时间工具）」「body」。

## 结论

- body 加第 6 组 **time**：`time.now` / `time.wait` / `time.remind` 三个 Capability，落进 `body_catalog`。
- 三个都不是新底层：`now` 绑定已有 `time_now`（Clock.now）；`remind` 绑定已有 `set_timer`（TimerService，与 toolbox 的 `computer.reminder.set` 镜像）；`wait` 是唯一新增 impl `time_wait`（`await asyncio.sleep`，cap 60s）。
- **wait vs remind 的定位分道**：
  - `wait`＝**同轮阻塞暂停**：blocking sleep，轮不断、上下文连续；补「模型无法主动让时间流逝」的缺口（tool call 之间墙钟几乎不前进，模型没法"等 5 秒再看 terminal 结果"）。短等待用。
  - `remind`＝**跨轮唤醒**：TimerService set → 到点 `timer.notify` 事件 → 新轮 `on_message` 醒来。重（持久化 timers.json＋新事件新 flow＋上下文要跨轮带）。自我唤醒用（无元层调度时，是 agent 自己"活着"的手段）。
- 推翻 10-18「time/now/wait/remind 不进 body」裁定，改判为「time 进 body」。

## why

- **wait 曾被想复杂**：初判把它当"同轮挂起-恢复"（=元层上下文管理的能力），倾向缓做。澄清后它只是"这一轮里让墙钟时间多走一小会儿"的阻塞 sleep，同轮上下文天然连续，**恰恰是它的价值、不碰元层**。
- **remind 已现成**：底层 TimerService + 唤醒链路（`timer.notify → sink → event_queue → on_message`）已跑通，toolbox 里 `computer.reminder.set/cancel/list` 已暴露；本次只是把 `set_timer` 镜像进 body。
- **now 是补暴露**：`time_now` 工具早已注册，但模型只拿到 toolbox（`toolset_names=["toolbox"]`），toolbox_catalog 无 time 组 → 模型此前访问不到 now。
- 实现约束：wait 加 **60s 上限**（防模型把自己挂死、阻塞串行事件处理）；描述显式写「等待期间不响应其他事件」，把"可被打断"语义排除，防模型误用。

## 被否 / 修正

- wait 做成「同轮挂起-恢复 + 可被打断」的重语义 → 否（那是元层能力，当前 `on_message` 串行 + 一次性 flow 无载体）。
- wait 缓做、等元层 → 否（定位澄清为纯阻塞 sleep 后，简单、可先落地）。
- remind 只留 toolbox 不搬 body → 否（YZ 坚持 body.time 三件都进；无元层时自我唤醒是常驻刚需）。

## 检视发现（本次顺带）

- `_wait` 初用 `raise`，改为与其余工具一致的 `return _ok_error(...)`（不经 registry 直接调用时不冒泡）。
- **body/memory 均未接进 consciousness 工具集**：`app.py` 硬编码 `toolset_names=["toolbox"]`，模型当前只看到 toolbox meta-tool，body/memory 的 catalog 能力（含本次 time 组）落码但暂不可见。属装配层职责（同「索引进上下文＝装配层职责」），非本次范围，留待装配接入。
