# checkpoint-1 — 轮 1：包骨架 + config 三文件 + base.py category

## 当前问题

lm-service 最小版起步：搭 `cogos.lm_service` 包骨架，config 从蓝本单 json 文件改成 yaml 三文件，ProviderError 加 category。

## 已做修改

- `cogos/pyproject.toml`：dependencies 加 `pyyaml`（三文件 yaml 所需，蓝本无）
- `cogos/cogos/lm_service/__init__.py`：新建（空，LmClient 轮 6 再挂）
- `cogos/cogos/lm_service/providers/__init__.py`：新建（空）
- `cogos/cogos/lm_service/providers/base.py`：新建 — `ErrorCategory`（StrEnum 六类）+ `ProviderError(category, message, raw, status_code)` + `ProviderBase`（原样保留接口）
- `cogos/cogos/lm_service/config.py`：新建 — yaml 三文件 Config 类

## 已读代码要点

- 蓝本 `lm_service/lm_service/config.py:1-219`：单 json 文件 `~/.agi-core/lm-service.json`，`internal_keys[ik_id] = {provider, account, model, status, created_at}`，`add_api_key` 混合写 api_key+models+并发在同一文件
- 蓝本 `providers/base.py:1-13`：`ProviderError(status_code, message, raw)` 无 category
- cogos 约定 `feishu/config.py` / `pyproject.toml`：运行时目录 `~/.cogos/<module>/`，pyproject scripts 用连字符命令名

## 关键结论/决策

- 三文件对齐：`config.yaml`(0644 手写 model 清单+并发+base_url) / `secrets.yaml`(0600 CLI 写 api_key) / `state.yaml`(0644 CLI 写 internal_key)，靠 `(provider, account)` 对齐
- internal_key 结构 `{id(字典键), group, provider, account, status, created_at}`——去 model 加 group；`resolve` 返回 `models` 清单（交 router，轮 3）+ `api_keys[0]`
- model 清单为 list of `{model, tier, modalities, logprobs, context_limit}`（capability 字段占位）
- `add_api_key` append 到 `api_keys`（一账户多 key，`resolve` 取 `[0]`），校验 account 存在 config.yaml
- 删蓝本残留：`BUILTIN_MODEL_DEFAULTS` + `global_context_limit()` + `config_api_key`（config 现手写，无 config CLI 命令组）

## 遗留/坑

- `~/.cogos/` 已有 feishu/phone，lm-service 子目录尚未创建（load 时 mkdir）
- 蓝本 adapter 调 `ProviderError(status, msg, raw)` 位置参数，轮 4 改 category 时需同步改 deepseek/openai 调用点
- pyyaml 需进 pyproject（已加）；环境用系统 python3.11 + 已 pip 装 pyyaml
