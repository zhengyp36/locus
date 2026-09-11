# codebase — cogos 代码认知基线

> 本体仓库 `/home/zhengyp/work/A/cogos/`，包 `cogos/`。就地改：认知变了就修正，过时结论去掉。

## 包结构

```
cogos/
  feishu/       # 通信层（飞书总线，已收口）
  phone/        # 通信抽象 phone（feishu 之上，agent 通信用）
  lm_service/   # LLM 服务封装（client + providers + server + cli）
  cog_runtime/  # CogUnit + CogRuntime 状态机
  img_tool/     # 视觉取图原语（core 纯逻辑 / cli flock 子进程 / stub async 封装）
  agent/        # agent 雏形（consciousness/tools/terminal/timer/events/app）
```

组件/CLI 短横线（cogos-lm-service 等），Python 包下划线（lm_service/cog_runtime）。

## lm_service（冻结契约）

- `client.py`：`LmClient(internal_key)`，`async chat(messages, *, temperature=0, max_tokens=1000, top_p=None, thinking=None, tier=None, must=False, trace_id=None, tools=None)` → 归一响应 dict。
  - `messages` 是 `[{role, content[]}]`（content 是 list，text 项 `{type:"text", text}`）。
  - 响应含 `content`（list）、`tool_calls`（`[{id,name,args}]`）、`usage`、`reasoning`、`routed`。
  - 异常 `LmServiceError(category)`，category ∈ ErrorCategory（retryable/semantic/auth...）。
  - 不暴露 base_url（走环境变量 `LM_SERVICE_HOST/PORT`）。
- `providers/base.py`：`assemble_tool_messages` 把续轮 tool 消息转厂商格式（含 reasoning_content）。
- `__init__.py` 导出 `LmClient, LmServiceError`。

## cog_runtime（CogUnit + CogRuntime）

- `types.py`：`Tier = "basic"|"advanced"`；`CuResultOk(content, reasoning)` / `CuResultError(category)` / `CuResultInterrupted(reason)`。
- `unit.py`：`CogUnit` 被动数据 + 句柄，状态机 created→pending→queued→running→tooling→done；`wait()`/`no_wait()`/`interrupt(reason)`；parent/children append-only。
- `runtime.py`：`CogRuntime(internal_key, max_concurrent=4, client=None)`；`cu(material, tier, tools=None, callbacks=None, parent=None, thinking=None)` → CogUnit。
  - `material` 是**可变 list**，续轮消息直接 append 进去，`on_done` 拿到完整上下文。
  - callbacks：`on_ready(cu, material)` / `on_tool_call(cu, calls)->results` / `on_done(result, material)`。
  - 推进集中在 `_advance`；工具循环：tool_calls → on_tool_call → 回填 assistant/tool 消息 → pending 再跑。
  - `on_tool_call` 缺省 → `CuResultError("invalid_request")`。
  - 并发 `asyncio.Semaphore`；`shutdown()` 打断所有未定 cu。

## agent（雏形）

- `consciousness.py`：`Consciousness` 持 context + `asyncio.Lock`，`on_message` append user → `runtime.cu(tier="basic", tools=schemas)` → `await cu.wait()`。`on_tool_call` 计数超 `MAX_TOOL_ROUNDS=10` 则 `cu.interrupt("max_tool_rounds")`。`on_done` 补 assistant + 兜底 send_msg。
- `tools.py`：`ToolSpec(schema, fn)` + `ToolRegistry(schemas(names)->list, call(name, args)->dict)`。工具 fn 返回 dict（`ok`/`reason`/...）。内置 read/write/edit/execute/search/fetch + scratch + `drain_stream`。
- `terminal.py`/`timer.py`/`events.py`：终端会话管理、定时器、事件。
- `app.py`：`Agent` 组装 phone + registry + runtime + consciousness + perception；`CogRuntime(os.environ.get("LM_INTERNAL_KEY", ""))` 或注入 `lm_client`。

## img_tool（视觉取图原语）

- `core.py`：同步纯逻辑。`estimate_peak(w,h,file_size)` / `check_budget` / `budget_from_available(mem_available_kb, fraction)` / `parse_meminfo` / `read_mem_available` / `parse_region(x,y,w,h,W,H)`（归一化→像素，clamp）/ `pick_scale(long_side, max_dim)`（≤max_dim 恒 1.0 永不放大）/ `infer_format(out)`（.jpg/.jpeg→JPEG，.png→PNG，缺省 JPEG）/ `do_info(path)` / `do_extract(path, region, max_dim, out)`。常量 `EST_PEAK_CONST=48MB`、`MEM_FRACTION`（env `IMGTOOL_MEM_FRACTION` 默认 0.6）、`DEFAULT_MAX_DIM=800`。
- `cli.py`：`img-cli` 入口。子命令 `info <path>` / `extract <path> --out ...`。先 `acquire_slot`（flock 计数信号量，lockdir `/tmp/imgtool-locks-{uid}/`，N=`IMGTOOL_CONCURRENCY` 默认 1，jitter 50~200ms，`--wait-timeout` 默认 30）再干活。stdout 单行 JSON；退出码：文件不存在/参数错→1+stderr，业务错误态（图太大/空 region）→0+ok:false。
- `stub.py`：async 封装 `info`/`extract`。`extract` 建 tempfile 作 `--out`→起子进程→读 bytes→unlink 清理，返回 `{ok, data, width, height, scale, format}`。找 img-cli：`sys.executable -m cogos.img_tool.cli`（`IMGTOOL_CLI` 可覆盖）。
- 本步不注册进 agent registry，未接 look_at/cog-func。

## 测试

- `tests/` 按包分目录（`tests/cog_runtime/`, `tests/agent/`, `tests/lm_service/`, `tests/feishu/`, `tests/phone/`, `tests/img_tool/`）。
- `pyproject.toml`：`testpaths=["tests"]`, `asyncio_mode="auto"`。
- conftest 风格：`FakeLmClient` + `monkeypatch.setattr(runtime_mod, "LmClient", lambda ik: fake)`；img_tool 用 Pillow 造小图 fixture `make_image`。
- 全量基线 915 passed；跑法 `python3.11 -m pytest`（**需 python3.11**，feishu 用 `X | None` 语法，3.9 会 import 报错）。

## 依赖 / 打包

- `pyproject.toml`：name=cogos，deps `aiohttp/prompt-toolkit/pyyaml/qrcode/Pillow`。
- scripts：`cogos-feishu`/`cogos-phone`/`cogos-lm-service`/`img-cli`。
