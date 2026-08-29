# checkpoint-3 — 轮 3：主链路 router + handler + scheduler 接 router

## 当前问题

搭 lm-service 主链路：router 选 model（模态>tier>must），handler 鉴权简化 + tier/must/trace_id + 错误响应 `{"error":{"category","message"}}`，scheduler 接 router 选 model 而非蓝本的 `resolved["model"]`。

## 已做修改

- `cogos/cogos/lm_service/router.py`：新建。`select_model(models, messages, tier=None, must=False)` → `{model, tier, degraded}`；`infer_modalities` 只推断非 text 模态（当前 image）；tier 用 `_TIER_RANK`（cheap=0/expensive=1），`degraded = rank(actual) < rank(requested)`（"实际低于请求"）；不满足模态/ must=true 无匹配 tier 抛 `ProviderError(invalid_request)`。
- `cogos/cogos/lm_service/handler.py`：新建。`ALLOWED_REQUEST_FIELDS` 增 `tier/must/trace_id`；`_validate_internal_key` 只查存在+active（无鉴权语义）；必填 messages/temperature/max_tokens + unknown fields → invalid_request；`_error_response` 按 category 映射 HTTP 状态（auth 401/quota 402/invalid_request 400/content 400/semantic 502/retryable 503）；删 `/v1/context-limit` 端点。
- `cogos/cogos/lm_service/scheduler.py`：新建。蓝本 AccountScheduler(semaphore+RPM)+Scheduler 池化原样，改：`PROVIDER_REGISTRY = {}`（轮 4 装 deepseek/openai）；`ProviderError(category, msg)` 换位置参数；`Scheduler.submit` 调 `select_model` 选 model 后拼进 resolved，结果加 `routed={tier, degraded}`。
- `cogos/cogos/lm_service/server.py`：新建（原样 port，改 import 路径 + `create_app(base_dir=None)` + `--config` 语义为 base dir）。

## 已读代码要点

- 蓝本 `handler.py:6` `ALLOWED_REQUEST_FIELDS` 无 tier/must/trace_id；`handler.py:70-73` context-limit 端点 + `config.py:78-86` `global_context_limit`（已删）。
- 蓝本 `scheduler.py:41-52` `_process_request` 用 `resolved["model"]`（旧绑 model）；`scheduler.py:110-120` `submit` 只 resolve 不选 model。
- 本工程 `config.py:165-193` `resolve_internal_key` 已返回 `models` 清单（轮 1 改），router 的原料。

## 关键结论/决策

- **router 独立组件**不塞 config，纯函数选 model；tie-break = 注册顺序取第一个（`candidates[0]` / `tier_candidates[0]`）。
- **degraded 语义**：`实际 tier 低于请求 tier`（cheap<expensive）。image 请求 tier=cheap 落到 expensive vision 是"升级"，degraded=False（spec 2.3 "低于"）。
- **text 为默认能力**：`modalities=["image"]` 的 vision model 同样满足纯文本请求，text+tier=expensive 会路由到 vision。
- **handler 不 catch 后吞异常**：scheduler 抛 `ProviderError` → handler 转 `{"error":{"category","message"}}`，HTTP 状态按 category 映射（category 权威）。
- **server.py 本轮一并 port**：主链路"跑通"需 app 组装，原样搬运低成本。

## 遗留/坑

- **`PROVIDER_REGISTRY` 空**：mock 验证须先注入 FakeProvider（`scheduler.PROVIDER_REGISTRY["deepseek"] = Fake`）。轮 4 装真 adapter 并 populate。
- **`PYTHONPATH` 坑**：跑 `/tmp/kilo/*.py` 脚本时 sys.path[0] 是脚本目录非 cwd，须 `PYTHONPATH=/home/zhengyp/work/B/cogos` 才能 import 本地 `cogos`（否则撞 site-packages 的旧 cogos，无 lm_service）。
- **gate 通过**：8 项 mock 检查全绿（路由 cheap/expensive/image/degrade/must、错误 auth/invalid_request、缺字段）。
- 蓝本 adapter 旧 `ProviderError(status, msg, raw)` 位置参数未动，轮 4 同步改 deepseek/openai（承接 checkpoint-1/2 遗留）。
