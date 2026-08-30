# checkpoint-1 — 轮 1：删 LmClient base_url 参数

## 当前问题

契约 ①：`LmClient` 只持 `internal_key` 句柄，不感知 lm-service 地址。删 `__init__` 的 `base_url` 参数，地址恒走环境变量/默认。

## 已做修改

- `cogos/lm_service/client.py:29-31`：`__init__(self, internal_key)`，删 `base_url` 参数；`_base_url` 恒 = `f"http://{DEFAULT_HOST}:{DEFAULT_PORT}"`（DEFAULT_HOST/PORT 已从 `LM_SERVICE_HOST`/`LM_SERVICE_PORT` 读，模块导入时求值）
- `cogos/lm_service/cli.py:55`：`_run_chat` 删 `base_url` 参数，直接 `LmClient(internal_key)`
- `cogos/lm_service/cli.py:72`：`_cmd_call` 删 base_url 构造逻辑（原 `--host`/`--port` → base_url）
- `cogos/lm_service/cli.py:108`：`call` 子命令删 `--host`/`--port` 参数
- `cogos/lm_service/cli.py:6`：docstring 用法更新

## 关键结论/决策

- `call` 命令的 `--host`/`--port` 一并删掉：人工 CLI 也属上层，不感知地址，连服务端走环境变量 `LM_SERVICE_HOST`/`LM_SERVICE_PORT`（server 用 11435 时需 `LM_SERVICE_PORT=11435`）。
- `server` 命令的 `--host`/`--port` 保留（那是服务端监听地址，非客户端）。
- 服务端侧 base_url 逻辑（`config.py:193` + `scheduler.py:55`）不动，符合契约「服务端已实现」。

## 验证

- `python3.11 -m pytest tests/lm_service/` → 51 passed 绿。
- `LmClient` 构造签名已无 `base_url`（`client.py:30`）。
- 测试 `test_errors.py` 本就 `LmClient("ik_x")` 不带 base_url，mock aiohttp，零改动。

## 遗留/坑

- 测试环境须用 python3.11（`.python-version`=3.11）；系统默认 python3.9 缺 pyyaml 会 collection error。
- `DEFAULT_HOST`/`DEFAULT_PORT` 在模块导入时求值——测试如需运行时改地址须在 import 前设环境变量（现有测试走 mock aiohttp，不受影响）。
- 全量 pytest 不跑（feishu/phone tests 耗时且不受本轮影响），留轮 5。
