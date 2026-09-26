# web 异步化实现规格（精简版）· 2026-09-19

> 替代 `spec-tools-a.md` §6.1 作为本批开工依据。删掉了 §6.1 里不可达的 cancel 闸门、本批不做的渲染缝与并发上限；只保留"用户四条"所需的最小机制。
> 权威分册：`cogos/docs/design-agent-tools.md`。代码基线：`cogos` @ `4f3c017`。

## 0. 目标与判据

- `search`／`fetch` 不再阻塞当前轮：提交即返回作业句柄，结果晚点经 Signal 回来。
- 判据（design §4）：网络是无界阻塞 → **异步类**。异步的价格只有四笔：持有 task、给作业 id、长内容落载体、结果经事件回投。
- **立场**：agent 是自主主体，不是服务；另一端只是与它独立的人或 agent。异步完成只是"它自己发起的一件事办完了"，事件**唤醒它继续想**；是否回复、回复谁、发摘要还是原始结果，全由它自己用 `send_msg` 决定。**机制不自动回投、不代它回复。**
- 定位：**过渡件**。web 不进最终形态（长期＝电脑视觉上网），对象自洽、可整体删除，不被其他契约依赖。

## 1. 对象与类型

```python
# cogos/agent/impl/web.py

@dataclass(frozen=True)
class JobAccepted:
    job_id: int
    at: float                       # epoch 秒（UTC），提交时刻

@dataclass
class JobView:
    job_id: int
    state: str                      # running | done | failed | cancelled
    at: float                       # 本次状态时刻
    result: str | None = None       # 短结果内联（正文文本）
    handle: Draft | None = None     # 长结果落草稿的句柄
    error: str | None = None

class WebService:
    def __init__(
        self,
        drafts: DraftStore,
        clock: Clock,
        sink: SignalSink,
        *,
        brave_key: str | None,
        jina_key: str | None,
        proxy: str,
        brave_url: str,
        jina_url: str,
        transport: HttpGet | None = None,   # 可注入；默认 aiohttp + proxy
        search_timeout: float = 20.0,
        fetch_timeout: float = 60.0,
        max_fetch_bytes: int = 50_000,
        inline_max_bytes: int = 2048,
        retain_terminal: int = 64,
    ) -> None: ...

    async def search(self, query, count=10) -> JobAccepted
    async def fetch(self, url, fmt="markdown") -> JobAccepted
    def cancel(self, job_id) -> JobView            # raises UnknownJob
    async def aclose(self) -> None
```

- 异常：`UnknownJob`／`WebUnavailable`（所需 key 缺，**提交时抛**）／复用 `TooLarge`。

```python
class HttpGet(Protocol):
    async def __call__(self, url: str, *, headers: dict,
                       timeout: float) -> tuple[int, str]: ...
```

- `HttpGet`：网络错／超时**抛异常**；HTTP 任意状态码**返回** `(status, text)`，4xx/5xx 由各 `body_fn` 判定，transport 不判。
- 默认实现持一个**惰性创建**的共享 `aiohttp.ClientSession`（`proxy` 显式传，aiohttp 默认 `trust_env=False`）。
- A 纪律：**不读 env／文件**；key／proxy／url／超时／阈值全由装配层注入。

## 2. 提交（不阻塞，返回句柄）

```python
async def search(self, query, count=10):
    if self._brave_key is None:
        raise WebUnavailable("brave key missing")
    job = self._new_job()
    job.task = asyncio.ensure_future(self._run_search(job, query, count))
    return JobAccepted(job.job_id, self._clock.now_epoch())
```

- `job_id` 由 `WebService` 自铸（单计数器，web 一个能力一个计数器）。
- task 存进 `self._jobs[job_id]`，**强引用**防 GC。
- worker 只做三件事：取网络 → 定型（短内联／长落草稿）→ 发 Signal。

## 3. worker 与短/长

```python
async def _run(self, job, request, *, header, body_fn):
    try:
        status, text = await request()       # 唯一 await（网络）
        body = body_fn(status, text)         # 纯同步：校验/清洗/截断
    except asyncio.CancelledError:
        job.state = "cancelled"              # cancel() 已置，幂等
        raise                                # 只清理，不吞
    except Exception as exc:
        self._fail(job, str(exc)); return

    text_out = f"{header}\n\n{body}" if header else body
    data = text_out.encode("utf-8")
    try:
        if len(data) <= self._inline_max_bytes:
            job.result = text_out            # 短：内联
        else:
            job.handle = self._drafts.put(data, ext="md")   # 长：落草稿
    except TooLarge as exc:
        self._fail(job, str(exc)); return
    job.state = "done"
    self._emit(job)
```

- **`request` 是零参工厂**（`lambda: self._http.get(url, headers=..., timeout=...)`），**不是 coroutine**：提交后立刻 cancel 时 task 可能在首行前被取消，传 coroutine 会留下 `never awaited` 警告；传工厂则无悬空对象。同理 `_new_job()` 里 `ensure_future(self._run(job, request, ...))`。
- **一律先拼正文**：`header + "\n\n" + body`。
- `header`（落草稿与内联都带）：fetch＝`[来源: <url>]`；search＝`[来源: 网页搜索: <query>]`。格式在此钉死；它是 durable 内容，后改只影响新结果。
- `body`：fetch＝清洗后的正文（按 `fmt`，超 `max_fetch_bytes` 截断，末尾附 `\n\n…（已截断）`）；search＝按 `count` 逐条，格式钉死为
  ```
  1. <title>
     <url>
     <snippet>
  ```
  空结果＝`（无结果）`。
- 短/长按 `len(text_out.encode("utf-8"))` 度量，阈值 `inline_max_bytes`。
- 失败（网络错、HTTP ≥400、`TooLarge`）→ `state=failed`、`error=...`，**照发 Signal**，不静默。

## 4. cancel（同步、幂等）

| cancel 时状态 | 行为 |
|---|---|
| `running` | 置 `state=cancelled`，`job.task.cancel()`；**不发 Signal**；返回 `cancelled` |
| `done`／`failed` | 原样返回终态，不改、不撤回 |
| `cancelled` | 幂等返回 |
| 未知／已修剪 | `UnknownJob` |

- **不设"算出后检查 state"的闸门**：`DraftStore.put` 同步、worker 在 HTTP await 之后无 await，单线程下 `task.cancel()` 只在网络 await 处生效；"取消后不冒完成事件"由 `CancelledError` 天然保证。
- worker 的 `except CancelledError` 只置状态 + 重新抛，不吞。

## 5. Signal

```python
Signal(kind="web.search_done" | "web.fetch_done",
       payload={
           "job_id": ..., "state": ..., "result": ..., "handle": ...,
           "error": ...,
       },
       at=self._clock.now_epoch())
```

- 成功／失败都发；取消不发。
- payload 只含机器事实：**不含工具名、不含中文标签**。工具名由 kind 承载。
- **关联靠 `job_id`**：事件唤醒 agent，它用自己的上下文（job_id 对应的那次调用）认领结果。**不带 source、不做路由**——机制不代它回复。

## 6. 生命周期

- 共享 `ClientSession` 在首次请求时惰性创建（需 running loop）。
- `aclose()`：取消全部在途 task（`gather(return_exceptions=True)`），关闭共享 session（若已创建）。
- 终态作业保留 `retain_terminal` 条，超出按序修剪（修剪后 cancel 得 `UnknownJob`；信息无损失，事件已发过）。

## 7. 接线（非 A 层）

- `cogos/agent/tools.py`：
  - `search`／`fetch` 的 `fn` 改为调 `WebService`，`time_form="async"`；返回显式 dict，如 `{"ok": True, "job_id": ..., "at": ...}`（不要落进 `Registry.call` 的 `{"ok": True, "result": ...}` 兜底）。
  - 新增 `web_cancel`：`async def fn(job_id)` 包 `service.cancel`，`time_form="sync"`，返回 `{"ok": True, "job_id", "state", "result"|"handle"|"error"}`。
  - 旧 `webtools.py` 的 HTTP 实现迁入 `impl/web.py`；key/env 读取上移到装配层，`webtools.py` 删除。
- `cogos/agent/app.py`：
  - 读 key／proxy：**保持现行为**——env（`BRAVE_API_KEY`／`JINA_API_KEY`／`KILO_PROXY`）优先，回退 `~/.secrets/*.key` 与 `http://127.0.0.1:10809`；`brave_url`／`jina_url` 常量一并落此。
  - 构造 `WebService` 注入（`make_search_spec(web)`／`make_fetch_spec(web)`／`make_web_cancel_spec(web)`）；`Agent.stop()` **开头**调 `await web.aclose()`（早于 consumer 取消）。
- 通知落点：走既有 `_QueueSink.emit`（app.py:74）→ `_consume_events`（app.py:202），与 `transfer.done`／`timer.notify` 同一条路，**web 不特殊处理，`_consume_events` 不改**。

## 8. 测试（`tests/agent/`，注入假 transport）

- 成功（短→`result` 内联；长→`handle` 落草稿，正文含来源头）。
- 超时／网络错／HTTP ≥400 → `failed` + Signal。
- cancel：running→`cancelled` 且**不发 Signal**；done→原样返回；重复 cancel 幂等；未知→`UnknownJob`。
- 无 key → 提交时 `WebUnavailable`。
- `retain_terminal` 修剪后 cancel 得 `UnknownJob`。
- 假 transport 断言请求 URL／headers／proxy 传递。

## 9. 本批不做（记债）

模型可见文案定稿、渲染缝 `observation.py`、`max_inflight_jobs`／`Semaphore` 并发上限、同 URL 去重、草稿淘汰保护、统一事件信封、`transfer` 对齐作业形状、`send_msg` 真异步。

## 10. 与 `spec-tools-a.md` §6.1 的差异

1. **删 cancel 闸门**（不可达，纯增复杂度）。
2. **删渲染缝**（本批不做，默认仍走 `render_event`）。
3. **删两道上限**（并发交给后续批次）。
4. 明确 `result`／`handle` 二选一、`result` 为**正文文本**（避免 2048 度量口径与存储形态不一致）。
5. 明确来源头格式（钉死，durable）：这是**内容出处**，供 agent 日后读草稿自判，与"谁触发"无关。
6. **删 `JobView.source` 与 source 路由**：异步完成只唤醒 agent，不自动回投；关联靠 `job_id`。
