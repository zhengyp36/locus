# checkpoint-7 — 轮 7：lm_call CLI 改造 + 顶层 cogos-lm-service CLI

## 当前问题

`lm_call` 改造为人工 CLI 复用 `LmClient`（不重复逻辑），删 `logger.py`（记录移服务端）。同时补 checkpoint-6 遗留的顶层 `cogos-lm-service` CLI（server/call/admin 分发）。

## 已做修改

- `cogos/cogos/lm_service/cli.py`：新建。顶层 `cogos-lm-service` CLI，`build_parser()` 注册 `server`/`call`/`admin` 三子命令，`set_defaults(func=...)` 分发、无子命令 `print_help()` 退出。`call` 复用 `LmClient`：读 stdin/`--file` JSON → 校验 `messages` + `_CHAT_FIELDS` 白名单（未知字段 SystemExit）→ `asyncio.run(_run_chat)` → 打印 content（或 `--raw` 打印归一响应）。错误 `LmServiceError` 打印 `Error [category]: message` 并 exit 1。`--host/--port` 显式时拼 base_url，否则用 LmClient 默认。
- `cogos/cogos/lm_service/server.py`：`create_app` 改同步（原 `async def` 无 await，`main()` 传 coroutine 给 `web.run_app` 是 latent bug）；抽 `run(config, host, port)`，`server.main()` 与 cli `_cmd_server` 共用。
- `pyproject.toml`：`[project.scripts]` 新增 `cogos-lm-service = "cogos.lm_service.cli:main"`。

## 已读代码要点

- 蓝本 `lm_call/cli.py`：`cmd_send` 用 urllib 拼 http + 手写错误解析 + 本地 `logger.py` 落盘；另有 `build`（文本文件拼 request JSON）/`list`/`show`（读本地 logger 日志）。三者均不搬：`list`/`show` 由 `admin calls` 取代（记录移服务端），`build` 超最小版范围舍弃。
- 蓝本 `lm_call/logger.py`：本地日志目录 `~/.agi-core/lm-calls/logs`，记录 request/response——被服务端 recorder（calls.jsonl）取代，弃用不搬。
- `server.py` 原 `main()`：`app = create_app(args.config)` 未 await（coroutine 直接进 `run_app`），且 `create_app` 内无任何 await → 同步化安全（AccountScheduler 的 Semaphore/Queue 在首次 `submit` 时于运行 loop 内惰性创建）。

## 关键结论/决策

- **`lm_call` 合并为 `cogos-lm-service call` 子命令**（spec 1.1「call = 人工调用（原 lm_call）」），不再设独立 `lm_call` 包/script。
- **`build`/`list`/`show` 不搬**：list/show 由 `admin calls` 取代，build 属便利工具超最小版，减法可追溯。
- **`call` 白名单 `_CHAT_FIELDS`**（temperature/max_tokens/top_p/thinking/tier/must/trace_id）对齐 handler `ALLOWED_REQUEST_FIELDS`，未知字段本地报错（比静默丢弃更能暴露用户笔误）。
- **`create_app` async→sync**：契约变更，外部旧 `await create_app()` 调用（如 round3 gate）需改；round 8-10 的 pytest mock 测试按 sync 写。

## 遗留/坑

- **gate 通过**：round7_gate.py 全绿 + 668 passed 无回归。
- **gate 技术坑**：fake server 与 subprocess CLI 同进程时，`asyncio.run(main())` 里 `subprocess.run` 会阻塞事件循环导致 server 无法响应 → fake server 必须放独立 daemon 线程（各自 event loop）。
- 蓝本 `logger.py` 物理文件仍在 `agent-study` 蓝本目录（未动，因本体不在 cogos 仓库），「删」指不搬入 cogos。
- 下一轮轮 8 起进入 pytest mock 测试（路由/错误归类/归一+调试记录），规格 6.1。
