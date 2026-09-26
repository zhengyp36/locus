# 工具实现层（A）接口规格 v1.4 · 2026-09-19（09-19 新增 §6.1 WebService · web 异步化）

> **范围**：只写 **A 实现层**（`design-agent-tools.md` §2／§13）。不含 schema／包／装配／role（B/C）。
> **依据**：权威分册 `cogos/docs/design-agent-tools.md`（工具部分唯一权威口径）；过程见 `checkpoint-1.md` §16~§19。
> **形态**：普通签名；返回普通值或抛类型化异常；异步结果走 A 自有 `Signal`。
> **本稿状态**：v1 已按 09-18 评审修订（见 §9 变更记录）。仍标 `待审` 的为编码时才需要定的实现细节。
> 下一步（编码）在本稿通过后进行：落 stub＋单测，先 `Clock`／`DraftStore`；**每个对象落成即配最薄 B 接进现有环**（§8）。

## 0. 公共约定

- A **不 import** `ToolSpec`／`AgentEvent`；只依赖 A 内类型。接线层把 `Signal` 映射成事件。
- A 对象在 agent 组装时创建；只有**有后台任务/连接**的对象才有 `start/stop`（`TimerService`、`ComputerManager`）。
- 单测判据（A 是否干净）：每个对象可**脱离 cu／registry** 直接实例化并断言。
- **时间坐标统一**：A 内部一律 **epoch 秒（float, UTC）**；时区只影响 `Clock.now()` 的渲染。产事件者共用同一 `Clock`。

```python
class ImplError(Exception):
    """A 层所有类型化异常的基类。"""


@dataclass(frozen=True)
class Signal:
    kind: str          # A 稳定标识；B 再映射成设计事件名
    payload: dict
    at: float          # epoch 秒（UTC）


class SignalSink(Protocol):
    def emit(self, signal: Signal) -> None:
        """同步、非阻塞（实现用 put_nowait）。队列满则丢弃并计数，绝不阻塞读流。"""
```

## 1. Clock　`time`

```python
class Clock:
    def __init__(self, tz: str | None = None) -> None: ...
    def set_timezone(self, tz: str) -> None: ...   # raises UnknownTimezone
    def now(self) -> datetime: ...                 # tz-aware；取值/渲染用
    def now_epoch(self) -> float: ...              # epoch 秒 UTC；Signal.at 用
```

- `[已定]` 取值型、同步、有界。
- `set_timezone` **只改显示**，不改坐标；`now_epoch()` 与时区无关。
- **A 不读配置**：初始 `tz` 由装配层注入（`Clock(tz=...)`，`None`＝系统本地）；`set_timezone` 只改**内存态**。**读/写 `agent.json` 与持久化归装配层**（v0 可不持久化）。
- **待审**：非法 `tz` 抛 `UnknownTimezone`（推荐）还是保留原值。

## 2. DraftStore　`draft`

设计依据 `design-agent-tools.md` §7。

```python
@dataclass(frozen=True)
class Draft:
    id: int
    ext: str
    size: int


@dataclass
class DraftRead:
    id: int
    text: str          # A 已按 offset/limit 切好；行号渲染属 B
    offset: int
    limit: int
    total_lines: int
    size: int          # 整份文件字节数
    truncated: bool


@dataclass(frozen=True)
class MarkedDraft:
    id: int
    summary: str


class DraftStore:
    def __init__(
        self,
        root: Path,
        *,
        quota_total: int,          # 例 30MB
        quota_draft0: int,         # 例 1MB，独立、不进总量
        marked_max_count: int,     # 例 20
        marked_max_bytes: int,     # 例 10MB
        hard_max_bytes: int = 500 * 1024 * 1024,
        evict_hot: int = 100,
    ) -> None: ...

    # ---- 工具面 ----
    def read(self, id, *, offset: int = 1, limit: int = DEFAULT_LIMIT) -> DraftRead
    def write(self, content: str, *, id=None, ext: str = "md") -> Draft
    def edit(self, id, old_string: str, new_string: str) -> Draft
    def mark(self, id, summary: str) -> None          # summary ≤ 256 字
    def unmark(self, id) -> None
    def list_marked(self) -> list[MarkedDraft]        # 只列已标

    # ---- transfer 专用入口（非 agent 工具直接调）----
    def reserve(self, ext: str) -> Draft              # 预分配 id，不落文件（v1.3）
    def get_bytes(self, id) -> bytes                  # 源端原样读（二进制安全；v1.3）
    def put(self, data: bytes, *, id=None, ext: str) -> Draft
```

- 异常：`InvalidId`／`DraftNotFound`／`NotText`／`InvalidEdit`／`CapacityExceeded`／`TooLarge`。
- `id=0` 保留地址：`read` 恒成功（miss 自动建空并返回空）；`write(0, "")`＝重置；**单独配额、不进总量、永不淘汰**。
- 无 `delete`、无通用 `list`/`search`（未标记项删不掉也列不出）。
- **淘汰次序写死**：① **超大未标记优先** → ② 热区 LRU 末位 → ③ 冷区随机。热区≤`evict_hot`，**只在内存**，重启清空；禁删项不受影响。
- 命名 `scratch_<id>.<ext>`，后缀原样；注册表 `marked_list.json`（非 `scratch_` 前缀，天然排除）。
- 手动 `write`/`edit` 不允许超总量配额（`CapacityExceeded`）；**`put`（transfer 侧）允许临时超**，硬上限 `hard_max_bytes`；**豁免＝store 内部内存状态**，不进 agent 可见面（单测可观察），下一次写时清。
- **待审**：`write` 新建时 `ext` 来源（现默认 `"md"`）？`read` 到二进制（transfer 进来的）返回 `NotText` 还是元信息？`InvalidEdit` 是否拆 empty／not-found／not-unique 三种子类？

## 3. TimerService　`timer`

```python
@dataclass
class Timer:
    id: int
    title: str
    fire_at: float      # epoch 秒
    state: str          # pending | fired | cancelled


class TimerService:
    def __init__(self, path: Path, *, clock: Clock, sink: SignalSink) -> None: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def set(self, title: str, delay_seconds: float) -> Timer   # raises InvalidDelay
    def cancel(self, id) -> Timer                              # raises UnknownTimer
    def list(self) -> list[Timer]                              # 仅 pending
```

- Signal：`Signal(kind="timer.notify", payload={timer_id, title, due_at, overdue_seconds}, at=clock.now_epoch())`。
- `[已定]` 同步返回句柄；`due_at`（预定）与 `at`（送达）之差＝迟到信息。
- **待审**：只支持相对 `delay` 还是也支持绝对时刻？重启后已过期的 timer 在 `start` 时补发（"错过"）？`list` 是否含已 fired/cancelled？

## 4. PhoneCapability　`phone`

- `[已定]` 复用 `cogos.phone.Phone`（其 `send(...) -> None`），A 薄包一层生成 **v0 本地 ack**。
- `receive` 是事件（perception 侧）、非 A 工具。

```python
@dataclass(frozen=True)
class SendAck:
    at: float          # 本地时刻＝"已交给通信层"


class PhoneCapability(Protocol):
    async def send(self, target: str, content: str) -> SendAck: ...
```

- **ack 语义＝"已交给通信层"**，v0 **不承诺送达**（真回执属通信层，后置）。
- **待审**：`send` 失败（无卡/网络错）抛异常还是返回失败态。

## 5. ComputerSession（term + fs + graphics）

设计依据 `design-agent-tools.md` §5／§6。**一个会话对象、多种能力面**：`term` + `fs` 已实现；**`graphics`（看屏/操作）为第三能力面，未实现**，接口与约束见 `spec-screen-1.md`（图形服务的概念定位见其 §0.1；术语：agent 侧=图形客户端、目标侧=图形服务）。

```python
@dataclass(frozen=True)
class SshTarget:
    host: str
    user: str | None = None
    port: int | None = None


class ComputerManager:
    def __init__(
        self,
        *,
        machine_root: Path,
        clock: Clock,
        sink: SignalSink,
        sync_reachable: bool = False,   # 机器属性（provisioning）；v0 本机
        cols: int = 80,
        rows: int = 24,
        ssh: SshTarget | None = None,   # 远端：会话顶层＝ssh -tt；None＝本机 $SHELL
        ssh_bin: str = "ssh",
        ssh_options: list[str] | None = None,
    ) -> None: ...

    def start(self) -> None: ...
    def stop(self) -> None: ...
    def open(self, *, cwd: str | None = None, notify: str | None = None) -> ComputerSession: ...
    def list(self) -> list[SessionInfo]: ...
    def get(self, id) -> ComputerSession: ...        # raises UnknownSession


@dataclass
class ScreenView:
    lines: list[str]          # VT 渲染后的屏（含滚动历史窗口）
    offset: int               # 窗口起始行号（行，非字节）
    total_lines: int          # 滚动缓冲区总行数
    state: str                # idle | exited
    exit_code: int | None


class ComputerSession:
    id: int
    state: str                # idle | exited（无 busy）
    cwd: str
    exit_code: int | None

    @property
    def fs(self) -> FsChannel | None: ...            # 通道存在性（本机/远端皆有；无传输能力时 None）
    @property
    def fs_exposed(self) -> bool: ...                # 对 agent 是否可见 = sync_reachable ∧ fs 存在

    # ---- term 面：后果型 → 发起即返回 ----
    def exec(self, command: str, *, notify: str | None = None) -> None   # 写 command+"\n"
    def write(self, data: bytes) -> None                                 # 原样送字节
    def observe(self, *, offset: int | None = None, limit: int | None = None) -> ScreenView
    def resize(self, cols: int, rows: int) -> None
    def cancel(self) -> None       # 向 pty 发 \x03，中断前台进程组；幂等
    def close(self) -> None


@dataclass
class FileRead:
    path: str
    text: str          # A 已按 offset/limit 切好；行号渲染属 B
    offset: int
    limit: int
    total_lines: int
    size: int          # 整份文件字节数
    truncated: bool


@dataclass
class FileWritten:
    path: str
    size: int          # 写入后的整份文件字节数


class FsChannel:
    # ---- fs 面：取值型 → 有界返回；A 内部 async（远端 sftp 是网络 I/O）----
    async def read(self, path, *, offset: int = 1, limit: int = DEFAULT_LIMIT) -> FileRead
    async def write(self, path, content: str) -> FileWritten
    async def edit(self, path, old_string: str, new_string: str) -> FileWritten
```

- 异常：`UnknownSession`／`SessionClosed`／`NotFound`／`NotText`／`TooLarge`／`SpecialFileUnsupported`。
- Signal：`term.done` `{session_id, exit_code, cancelled}`（**shell 顶层进程退出**，非每命令）；`term.notify` `{session_id, token}`（**默认关、显式开**）。`at=clock.now_epoch()`。
- **命令完成不发事件、不由机制推断**（`design-agent-tools.md` §5.1）：agent 靠 `observe` 看屏、显式 notify，或 `cmd; echo $?`／重定向＋`fs.read`。
- `observe` 返回**渲染屏**（pyte）；`offset`/`limit` **按行**；现 `buffer/cursor` 丢弃；忠实输出走重定向＋文件工具。
- `cancel()` **幂等**：无前台命令／已退出时 no-op 成功。
- notify：会话级（`open(notify=token)`）＋一次性（`exec(notify=token)`）；读流时**剥离 OSC 后再喂屏**。
- fs 从会话衍生：**`session.fs`＝通道存在性**（本机 FS／远端 sftp 均存在，与 `sync_reachable` 无关）；**`session.fs_exposed = manager.sync_reachable ∧ fs 存在`＝对 agent 是否可见**（C 层据此装配 `fs.*`，不新增 `get_fs`）。会话 `close` → 挂它的 fs 一并失效（不重连）。
- fs 路径基准：相对路径以**机器根**为基（本机＝`machine_root`，远端＝账户 home），绝对路径原样；`fs.read` 上限沿用 2000 行/2000 字符，另设整文件字节上限 `MAX_FILE_BYTES`（超则 `TooLarge`），本机 v0 无超时。

## 6. TransferEngine　`transfer`

```python
@dataclass(frozen=True)
class DraftRef:
    id: int


@dataclass(frozen=True)
class MachineRef:
    session_id: int      # v0；将来指向 machine 对象
    path: str


@dataclass(frozen=True)
class TransferAccepted:
    handle_id: int
    dest: DraftRef | MachineRef      # 发起时即定；新草稿 id 在此分配


class TransferEngine:
    def __init__(
        self,
        drafts: DraftStore,
        computers: ComputerManager,
        clock: Clock,
        sink: SignalSink,
    ) -> None: ...

    async def transfer(self, src, dst) -> TransferAccepted: ...   # 发起即返回
```

- 异常：`UnknownEndpoint`／`TooLarge`（>`hard_max_bytes`）／`CapacityExceeded`／`TransferFailed`。
- Signal：`Signal(kind="transfer.done", payload={handle_id, dest, bytes, error}, at=clock.now_epoch())`；成功 `error=None`，失败 `bytes=0`＋`error` 文案。
- `[已定]` 只 **copy**、整文件、无 offset、无 mode；端点 草稿 ↔ 机器根；**纯事件、不可等**（`transfer()` 仅返回 `TransferAccepted`）。
- v0 **不引入 `Machine` 对象**：`MachineRef{session_id, path}`（§9.2 的 `SshTarget` 已是机器级目标）。机器端相对路径以机器根为基（本机 `machine_root`，远端账户 home）。
- 草稿端去程走 `DraftStore.get_bytes`、回程 `reserve(ext)`＋`put`（临时超＋本轮豁免）；机器端走 `session.fs`（**不受 `sync_reachable` 暴露闸门影响**）。
- **不附来源戳**（来源只在入口标注，机制不跟踪；design §9/§11）。

## 6.1 WebService　`web`（过渡件 · 可拔除）

> **已过期（2026-09-19）**：本批 web 异步化已按 **`spec-tools-web.md`** 实现并落地；此节仅存历史，勿据此编码。差异见该文件 §10。

设计依据：`checkpoint-2.md` §二／§三／§四／§7（类重划：web 从 sync 移入 async）。**定位＝过渡件**：`search`／`fetch` 不进 agent 最终形态，长期由"电脑视觉上网"取代（design §14）；因此本对象自洽、可整体删除，**不得被其他契约依赖**，也不为其单开命名空间。

```python
@dataclass(frozen=True)
class JobAccepted:
    job_id: int
    at: float                        # epoch 秒；提交时刻


@dataclass
class JobView:
    job_id: int
    state: str                       # running | done | failed | cancelled
    at: float                        # 本次状态时刻
    result: object | None = None     # 短结果内联（原样值）；长结果 None
    handle: Draft | None = None      # 长结果落草稿的句柄
    error: str | None = None
    source: str = ""                 # 发起时的入站来源（回落用，§R15）


class WebService:
    def __init__(
        self,
        drafts: DraftStore,
        clock: Clock,
        sink: SignalSink,
        *,
        brave_key: str | None,          # 装配注入；A 不读 env/文件
        jina_key: str | None,
        proxy: str,
        brave_url: str = "...",         # 默认可留装配层
        jina_url: str = "...",
        search_timeout: float = 20.0,
        fetch_timeout: float = 60.0,
        max_fetch_bytes: int = 50_000,
        inline_max_bytes: int = 2048,
        max_inflight_jobs: int = 4,
        max_concurrent_requests: int = 2,
    ) -> None: ...

    async def search(self, query, count=10, *, source: str = "") -> JobAccepted
    async def fetch(self, url, fmt="markdown", *, source: str = "") -> JobAccepted
    def cancel(self, job_id) -> JobView          # raises UnknownJob
    async def aclose(self) -> None
```

- **提交＝不阻塞**：`search`／`fetch` 立即返回 `JobAccepted`（铸 `job_id`、起 worker task）；**不返回结果**。结果延迟 ⇒ 必有作业；当轮在线取值者不产生作业。
- **作业记录＝机器事实**：只有 `state`（机器枚举）／`result|handle`／`error`／`source`／`at`；**不含工具名、不含标签、不含中文**——工具名由 kind（`web.search_done`／`web.fetch_done`）承载，标签/文案归渲染层。
- **短/长分流**：结果序列化为文本后度量字节。≤ `inline_max_bytes` → `result` 内联；否则 `DraftStore.put` 落草稿、`handle` 指向它、`result=None`。`put` 失败（`CapacityExceeded`／`TooLarge`）→ `failed`。
  - 落草稿的正文**顶部加一行来源头**（fetch＝URL，search＝"网页搜索"）：草稿读回来没有来源通道，来源必须随内容落（design §11 缺口；§R19）。
- **Signal**：`kind ∈ {web.search_done, web.fetch_done}`，`payload = JobView 字段`（`at` 用 `Signal.at`）。成功/失败都发；**取消不发**（见下）。
- **cancel＝同步、幂等、尽力而为**：

  | cancel 时状态 | 行为 |
  |---|---|
  | `running` | `task.cancel()`；丢弃中间物、不落草稿、**不发 Signal**；返回 `state=cancelled` |
  | `done`／`failed` | 返回该终态，不改、不撤回（已完成者不可回收） |
  | `cancelled` | 幂等返回 |
  | 未知/已修剪 | `UnknownJob` |

  - **取消闸门**＝worker 在"结果算出"与"落载体＋发 Signal"之间检查 `state==cancelled`。事件循环单线程，只有 `await` 处可被打断；窗口即落草稿那次 `await`。**契约只保证"取消后不再冒出完成事件"，不保证撤销已送达的事件。**
- **并发控制**（两道上限，皆注入）：
  - `max_inflight_jobs`：`running` 作业数达上限，`search`／`fetch` **立即抛 `WebBusy`**（不排队）；
  - `max_concurrent_requests`：worker 内 `Semaphore` 限 HTTP 在途数（挡 429／额度）。
- **结果可达＝可重做**：web 属"只读、可重做"类（`checkpoint-2.md` §十八），草稿**允许被淘汰、不做保护**；工具说明须写明"长结果落草稿、草稿可能被淘汰、需要时重抓"。`read` 命中缺失草稿只回"不存在"（不区分未写／在途／已淘汰）。
- **异常**：`UnknownJob`／`WebBusy`／`WebUnavailable`（所需 key 缺，提交时抛）／复用 `TooLarge`、`CapacityExceeded`。
- **生命周期**：持后台 task ⇒ 有 `aclose()`（取消全部在途、关共享 `ClientSession`）。共享 session **惰性创建**（需 running loop，构造时可能没有）；`aclose` 前所有 worker 已 try/except 收敛，`CancelledError` 只做清理、不吞。
- **A 纪律**：不读 env／文件／常量默认值（key／proxy／url／超时／阈值全注入，§13）；HTTP 层可注入，便于假 transport 单测。
- **B/C 侧（非本稿范围，仅记落点）**：`search`／`fetch` 保留旧扁平名、`time_form` 转 `async`，fn 薄封装并注入**当前 turn 的 `source`**；新增 `web_cancel`（同步）。模型可见文案（§十五）归渲染层；渲染缝与事件渲染暂不统一。

## 7. A 信号一览

| kind | 来源 | payload |
|---|---|---|
| `timer.notify` | TimerService | `timer_id, title, due_at, overdue_seconds` |
| `term.done` | ComputerSession | `session_id, exit_code, cancelled` |
| `term.notify` | ComputerSession | `session_id, token` |
| `transfer.done` | TransferEngine | `handle_id, dest, bytes, error` |
| `web.search_done` | WebService | `job_id, state, result, handle, error, source` |
| `web.fetch_done` | WebService | `job_id, state, result, handle, error, source` |

- `phone.receive`（perception 侧）不在此表；A 不产。
- kind 用 A 稳定标识，**映射成设计事件名由 B 做**。

## 8. 落点与集成

- A 模块：`cogos/agent/impl/`（一对象一文件，`__init__` 汇总）。
- **集成策略**：**每落一个 A 对象，即配最薄的 B**（name→fn 映射）接进现有 `ToolRegistry`／`Consciousness`，**沿用旧扁平工具名**；C（分包/装配）后置。目的：每刀都能在真环里被证伪（"发起即返回＋事件续弧"的衔接单测盖不住）。
- 旧代码处理（A 接上时切）：
  - `ScratchStore` → `DraftStore`（去掉 history 归档；加 mark／配额／淘汰）。
  - `TerminalManager` → `ComputerManager`/`ComputerSession`（pipe→pty；`buffer/cursor`→VT 屏；busy→无）。
  - `read_file`/`write_file`/`edit_file` → 会话 `FsChannel`。
  - `execute` → **随 term 上线删除**（批次 2 收尾已删，09-19）。
- **待审**：A 若新目录并存，需明确旧模块删除时点（建议对象级一次性替换，不长期并存）。

## 9. 变更记录（v0 → v1，09-18 评审）

1. **term 语义定死为持久 shell**：`exec`＝发命令行、`term.done`＝shell 退出、去掉 busy、`cancel`＝`\x03` 幂等。（依据 `design-agent-tools.md` §5.1）
2. **时间坐标统一 epoch 秒**；`Clock` 增 `now_epoch()`；产事件者注入 `Clock`。
3. **`DraftStore` 配额补全**（`marked_max_count`/`marked_max_bytes`/`hard_max_bytes`）；淘汰次序写死；`put` 豁免改内部状态。
4. **`transfer` 发起即返回 `dest`**，新草稿 id 在发起时分配；`transfer.done` 带 `dest`。
5. **phone ack 降级为 v0 本地 ack**（"已交给通信层"，不承诺送达）。
6. 依据改为权威分册 `design-agent-tools.md`。
7. `sync_reachable` 从 `open()` 移到 `ComputerManager` 构造（机器属性）。
8. 集成策略：**每对象配最薄 B 进环**，不一次性切。
9. 包名去掉点号（`timer`/`term`/`fs`）。
10. `observe`/`ScreenView` 单位＝**行**。
11. `SignalSink.emit` 定义＝**同步非阻塞**（`put_nowait`）。
12. 删 `DraftStore.close()`（无后台任务者不设生命周期动词）。
13. `cancel()` **幂等**。

## 9.1 变更记录（v1 → v1.1，批次 2 编码时定 · 2026-09-19）

14. **`term.done` 恒发**（shell 退出即发）；`term.notify` 才是默认关、显式开。design §3 原措辞已改为分列。
15. **`observe` 默认＝末尾屏**：`offset=None` 返回末尾 `limit` 行（`limit` 默认＝屏行数）；`offset` **按行、1-based**；`total_lines`＝滚动历史＋可视屏。返回类型仍 `ScreenView`。
16. **`close()`＝唯一销毁动作**（终止 shell）；`term.done.cancelled` **仅当 close()／`manager.stop()` 主动拆除时为 True**；`cancel()`（`\x03`）不影响该标志。exited 后 `exec`/`write`/`resize` 抛 `SessionClosed`，`cancel`/`close` no-op。
17. **会话信息 `SessionInfo{id, state, cwd, exit_code, notify}`**；`open()`/`exec()` 的 `notify` token 命中即发 `term.notify`（`exec` 的一次性 token 命中后丢弃）。
18. **实现细节定案**：pty＝stdlib `pty.fork()`（控制终端＋`\x03` 前台组）；winsize 初值＝构造 `cols=80,rows=24`，`resize` 走 `TIOCSWINSZ`；`observe` 渲染用 **pyte `HistoryScreen`**（新依赖 `pyte`）。`write` 过 B 层按 **utf-8** 编码（A 仍收 `bytes`）。

## 9.2 变更记录（v1.1 → v1.2，远端 term · 2026-09-19）

19. **机器级远端目标**：`SshTarget{host, user?, port?}`；`ComputerManager(..., ssh=...)`。`ssh=None`＝本机 `$SHELL`；否则会话顶层进程＝`ssh -tt <user@host>`（端口 `-p`）。"本地/远端"由 manager 构造决定（一台电脑一个 manager）。
20. **密码不入 A**：agent 在 ssh 提示后经 `session.write` 送入；默认 ssh 选项 `StrictHostKeyChecking=accept-new`、`ConnectTimeout=15`。**密码路径不加 `BatchMode`**（与提示互斥）。
21. 远端 `open(cwd=...)` 暂不生效（v0，落远端 home），`session.cwd=""`；`term.done`＝ssh 退出。依据 `checkpoint-1.md` §23。

## 9.3 变更记录（v1.2 → v1.3，批次 3 会话衍生 · 2026-09-19）

22. **fs 通道 ≠ 工具暴露**：`session.fs`＝通道存在性（本机/远端皆有）；`session.fs_exposed = manager.sync_reachable ∧ fs 存在`＝对 agent 是否可见；`sync_reachable` 与本地/远端正交、纯配置决定（`checkpoint-1.md` §25.1/§25.2）。
23. **fs 接口**：`FileRead`/`FileWritten` 定形；`read_file`/`write_file`/`edit_file` 即 fs 包旧扁平名，**以会话句柄 `id` 为目标**（须先 `terminal_open`）；路径相对机器根、绝对原样；整文件上限 `MAX_FILE_BYTES`。
24. **`DraftStore` 增 `reserve(ext)`／`get_bytes(id)`**（transfer 专用）：发起时预留 id、源端原样读。
25. **`TransferEngine`**：纯事件不可等、v0 无 `Machine` 对象、机器端不受暴露闸门影响；`transfer.done` payload 增 `error`。
26. **撤销来源戳**：`transfer` 与草稿均不附 source（来源只在入口标注，机制不跟踪；design §9/§11）。sftp 载体＝`asyncssh`（新依赖）。

## 9.4 变更记录（v1.3 → v1.4，web 异步化 · 2026-09-19）

27. **新增 `WebService`（§6.1）**，落 `cogos/agent/impl/web.py`；`search`／`fetch` 从 sync 移入 async，提交即返回作业、结果走 Signal。
28. **作业＝每能力独立的延迟 correlator**：`job_id` 由 `WebService` 自铸，不建全局作业层；A 作业记录**不含工具名**（工具名由 kind 承载）。
29. **cancel 语义**：同步、幂等、尽力而为；闸门在"算出 → 落载体＋发 Signal"之间；取消不发 Signal。
30. **短/长分流**：`inline_max_bytes`（默认 2048）内联，超出落草稿并附来源头；web 结果属可重做类，草稿**不做淘汰保护**。
31. **并发两道上限**：`max_inflight_jobs`（超限抛 `WebBusy`）＋ `max_concurrent_requests`（Semaphore）；全部装配注入。
32. **过渡件口径**：web 不进最终形态（长期＝电脑视觉上网），对象自洽可拔除、不得被其他契约依赖。
33. **依赖**：HTTP 层沿用 `aiohttp`；key／proxy／url／超时／阈值全注入（A 不读 env／文件）。

## 10. 剩余待审（编码时定）

1. `Clock` 非法 tz 行为（初值注入／持久化归装配层，A 不涉）。
2. `DraftStore.write` 新建 `ext` 来源；`read` 二进制返回；`InvalidEdit` 子类拆分。
3. `TimerService` 绝对时刻、错过补发、`list` 范围。
4. `PhoneCapability.send` 失败语义。
5. `ComputerSession`：pty 库、winsize 初值 → **批次 2 已定（§9.1 第 18 条）**；远端 ssh 目标 → **09-19 已定（§9.2）**；fs 路径基准／`fs.read` 上限 → **批次 3 已定（§9.3 第 23 条）**。
6. `TransferEngine` → **批次 3 已定（§9.3 第 25 条）**。
7. `WebService`（§6.1）：`source` 如何从当前 turn 注入 B（显式参数 vs contextvar）；结果内联形态（search 用 JSON 文本还是原样 dict）；终态作业保留条数（建议 64，供 cancel 查终态）；`aclose` 是否需要并行 `start`；共享 session 超时/重连策略。
8. **本批明确不做**（记债，勿混入）：模型可见文案定稿（`checkpoint-2.md` §十五）、统一事件信封、`transfer` 对齐作业形状、作业可观测列表、上下文压缩／丢弃（§十八）、同 URL 在途去重、草稿淘汰保护。
