# checkpoint-6 — 轮 6：抽 LmClient async 接口

## 当前问题

cog-runtime 只 import 客户端接口，不拼 http、不碰厂商 api_key / model。抽 `LmClient` async 接口封装 http 传输（socket 后置换传输只改本模块），`chat(messages, tier, must)` → 归一响应，失败抛 `LmServiceError(category, message)`。

## 已做修改

- `cogos/cogos/lm_service/client.py`：新建。`LmServiceError(category, message)`（category 存字符串枚举）+ `LmClient(internal_key, base_url=None)`。`chat(messages, *, temperature=0, max_tokens=1000, top_p=None, thinking=None, tier=None, must=False, trace_id=None)`：组装 body（optional 字段 None/False 时不发）→ POST `/v1/chat/completions` + `X-Internal-Key` header → 非 200 解析 `{"error":{"category","message"}}` 抛 `LmServiceError`；传输错误/空 body/非 json → `LmServiceError(retryable)`；2xx 返回归一响应原样。
- `cogos/cogos/lm_service/__init__.py`：导出 `LmClient, LmServiceError`（`from cogos.lm_service import LmClient` 生效）。

## 已读代码要点

- `server.py:11434`：服务端默认 `127.0.0.1:11434`，`--config` = base dir。
- `handler.py:88`：路由 `POST /v1/chat/completions`，错误响应 `{"error":{"category","message"}}`（`_error_response` 组装）。
- 蓝本 `lm_call/cli.py:143-234`：`cmd_send` 用 urllib 拼 http + 手写错误解析 + 本地 `logger.py` 落盘——这些下轮（轮 7）改造为复用 `LmClient`、删 logger.py。

## 关键结论/决策

- **`LmClient` 构造参数 `internal_key`，`base_url` 默认 `http://127.0.0.1:11434`**（支持 `LM_SERVICE_HOST/PORT` 环境变量覆盖，沿用蓝本 cli.py:13-14）。
- **`chat` 契约参数用 keyword-only**（`*` 分隔），`temperature=0` / `max_tokens=1000` 给默认值，使冻结契约 `chat(messages, tier, must)` 简写可直接调用。
- **2xx 直接返回归一响应**（`{content, finish_reason, usage, reasoning, raw, routed}` 由服务端已归一，客户端不重复归一）。
- **传输错误分类 retryable**，与 `providers/base.py:post_json` 语义一致（"响应不符合协议"非厂商拒绝）。
- `LmServiceError` 与 `ProviderError` 分离：前者客户端契约异常（服务端 error.category 字符串 / 本地 retryable），后者服务端内部 adapter 异常。

## 遗留/坑

- **gate 通过**：round6_gate.py 全绿（成功路径归一响应 / 401→LmServiceError(auth) / 关端口→LmServiceError(retryable)）+ 全量 pytest 668 passed 无回归。
- **环境坑**：`pip show cogos` editable 指向 `work/A/cogos`（工位 A 的 checkout，无 lm_service）。gate 脚本 / pytest 必须 `cd work/B/cogos` + `PYTHONPATH=work/B/cogos` 或 `python3.11 -m pytest`（cwd 进 sys.path）才 import 到工位 B 的 cogos。
- **无顶层 `cogos-lm-service` CLI**：`lm_service/` 内无 `cli.py`，pyproject 无 `cogos-lm-service` script。`admin.py` docstring 提到 `cogos.lm_service.cli` 但尚未建。轮 7（lm_call CLI 改造）需一并补顶层 CLI（server/call/admin 分发），或确认其归属轮次。
