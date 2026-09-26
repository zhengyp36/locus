# handoff｜web 异步化已落地 · 2026-09-19

> **新会话任务**：web 异步化**已实现并推送**。下一步先做 **① 更新权威分册 `cogos/docs/design-agent-tools.md` §4／§14**（见下"下一步"），再按 YZ 意图推进 ② 渲染缝／§十五、③ `send_msg`。
> **交接语**：读 `work/A/checkpoint/handoff-tools-08.md`，先读 `spec-tools-web.md`（本批权威 spec）与 `checkpoint-2.md` §二十。

## 入口

- 本批权威 spec：**`work/A/checkpoint/spec-tools-web.md`**（精简版，替代 `spec-tools-a.md` §6.1 作为 web 依据）。
- 讨论记录：`checkpoint-2.md` §二十（web 异步化收束；§一～§十九为前会话）。
- A 层总 spec：`spec-tools-a.md` v1.4（§6.1 已过期，仅历史）。
- 权威分册：`cogos/docs/design-agent-tools.md`（**本轮只提交了前会话的"工具／机制／事件面"订正，§4／§14 仍未更新**）。
- 代码：`cogos` @ **`c91aee4`**（已推 `origin/master`，工作区干净）。
  - `c73630d feat(agent): run web search/fetch as async jobs`
  - `c91aee4 docs: treat events as a tool's push face`（前会话所留改动的提交）

## 本批做了什么

- 新增 `cogos/agent/impl/web.py`：`WebService`（+ `HttpGet`／`AiohttpGet` 可注入传输、`JobAccepted`／`JobView`／`UnknownJob`／`WebUnavailable`）。
- `cogos/agent/tools.py`：`search`／`fetch` 改走 `WebService`、`time_form="async"`；新增 `web_cancel`（sync）。
- `cogos/agent/app.py`：装配 key／proxy／url（env 优先、回退 `~/.secrets/*.key` 与默认 proxy）；`Agent.stop()` 顶部 `aclose`。
- 删除 `cogos/agent/webtools.py`、`tests/agent/test_webtools.py`、`research/misc/verify_webtools.py`（旧同步形态，已失效）。
- 新增 `tests/agent/test_impl_web.py`（18 例，假 transport）。
- 全量 pytest：**1126 passed, 4 skipped**。

## 本批关键结论（勿再翻案）

- **`source` 已删除、不做回投**：agent 是自主主体，不是服务；异步完成只发 Signal 唤醒它继续想，**是否回复／回复谁由它自己 `send_msg` 决定**，机制不自动回投。`_consume_events` 未改（事件仍 `source="system"`）。
  - 关联靠 **`job_id`**（工具返回 + 事件 payload），不靠 source。
- **cancel 无闸门**：`DraftStore.put` 同步、worker 在 HTTP await 后无 await，`task.cancel()` 只在网络 await 处生效；"取消不发完成事件"由 `CancelledError` 保证。
- 草稿正文**来源头**是**内容出处**（fetch URL／"网页搜索: query"），与"谁触发"无关；格式已在 spec 钉死（durable）。
- 短/长阈值 `inline_max_bytes=2048`，超出落草稿；`result` 固定为正文文本。

## 下一步（按序）

1. **更新 `design-agent-tools.md`**（代码已落地，权威分册该追平）：
   - §4：判据改写为"**类 = 能否无界阻塞**"；规则①重写（`checkpoint-2.md` §二／§七）。
   - §14：解除 `search`／`fetch` 的 freeze，写明 **web 是过渡件**、长期＝电脑视觉上网。
2. **渲染缝／§十五**（YZ 待裁）：是否立 `observation.py`（默认 `str`）、模型可见文案定稿（`checkpoint-2.md` §十五／§十六）。
3. **`send_msg` 真异步**（YZ 待裁）：现状标 async 却阻塞。

## 本批明确不做（记债，勿混入）

渲染缝 `observation.py`、并发上限（`max_inflight_jobs`／`Semaphore`）、模型可见文案定稿、统一事件信封、`transfer` 对齐作业形状、作业可观测列表、上下文压缩／丢弃（§十八）、同 URL 在途去重、草稿淘汰保护。

## 遗留（不在本批范围）

- **4b 装配**：`assemble`／分包／按需／`agent.json`「电脑」接线。
- **标注规范（§十五）／`tool` 命名／模型可见面最小词汇** 三项仍待 YZ 裁（`handoff-tools-06.md`）。
- `transfer` 尚无 cancel；`term.*` 整族一刀切 async（`observe`/`list`/`cancel` 实为取值）。
- `time_form` 仍是**无人消费的死元数据**（已 grep），"异步不阻塞"无机制保证，靠 B 自觉 + 测试兜底。
- `experiment/selfdrive/loop.py:TASK_TOOLSET` 旧 `read_file` 语义。
- 批次 2.5 旧遗留：armed/一次性 token、槽位列举、密钥/`ControlMaster`。
- 通信工具**历史回读面**（§十八）；统一"在途调用"可观测面。
- 草稿 id 复用坑（淘汰最大号＋重启，`DraftStore._scan_next_id`）——归"草稿 id 语义"。

## 纪律（照 plan §0）

- 结论先落 `checkpoint-2.md`／spec，定案再更新权威分册 `design-agent-tools.md`。
- 一批一会话；开工前重审 spec／权威分册。
- 跑测试用 `python3.11 -m pytest`（系统 `python` 是 3.9，缺 `pyte`）。

## 收工

- 本批已提交＋推送（`c91aee4`）。下一批从"更新 design §4／§14"起，另起 handoff。
