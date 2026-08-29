# checkpoint-8 — 轮 8：mock 测试（路由）

## 当前问题

规格 6.1 mock 验证·路由：零账号全自动，monkeypatch `scheduler.PROVIDER_REGISTRY` 返回可编程响应，验证模态>tier 路由 + 降级留痕。

## 已做修改

- `tests/lm_service/__init__.py`：新建（空，对齐 tests/feishu、tests/phone 的包结构）。
- `tests/lm_service/test_router.py`：新建，163 行。`env` fixture（tmp base_dir 建三 yaml + Config.load + add_api_key/add_internal_key + `monkeypatch.setitem(PROVIDER_REGISTRY, "deepseek", MockProvider)` + Scheduler）。`MockProvider` 记录 `(model, body, api_key)` 并返回归一响应。`make_body` 默认带 temperature/max_tokens。7 用例：
  - tier=cheap 选 m-cheap、tier=expensive 选 m-exp，`routed={tier, degraded:false}`
  - 带图自动选 m-vision（tier 缺省，degraded=false）
  - 传图无 vision model → `ProviderError(invalid_request)`，mock 未被调用
  - must=false + 仅 cheap → 降级 `routed.tier=cheap, degraded=true`，选 m-cheap
  - must=true + 无 expensive → `ProviderError(invalid_request)`
  - 非法 tier → `ProviderError(invalid_request)`

## 关键结论/决策

- **mock 入口选 `PROVIDER_REGISTRY`**（spec 6.1 两个选项之一），经 `Scheduler.submit` 走全链路（resolve→select_model→AccountScheduler→provider），比单测 `select_model` 更贴近验收；同时断言 `routed` 与 provider 收到的 `model`。
- **降级用例模型清单只留 cheap**（`models=[TEXT_CHEAP]`）构造「请求 expensive 无匹配」，比用完整清单（有 expensive 就不降级）更可控。
- **ProviderError 断言 `exc.value.category`**，非 message 字符串（规格 4.2 原则）。

## 遗留/坑

- 全量 pytest 675 passed（668 旧 + 7 新），无回归。
- 轮 9 起进入错误归类 mock（规格 6.1 错误归类）：patch provider 抛 401/402/429/400/空body/非json/choices空/content_filter/insufficient_system_resource，断言 `LmServiceError.category`。
