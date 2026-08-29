# checkpoint-2 — 轮 2：admin CLI（api-key / internal-key）

## 当前问题

admin.py 简化：删蓝本 service/systemd 组与 api-key config/model/base-url 等旧参数，保留 api-key / internal-key 两组（calls 轮 5），写三文件 + secrets 0600。

## 已做修改

- `cogos/cogos/lm_service/admin.py`：新建（113 行）。argparse 嵌套 subparsers：`admin` → `api-key`/`internal-key` → `add`/`list`/`delete`；每级 `set_defaults(func=...)` 分发；无子命令 `print_help()` 退出。`build_parser(subparsers)` 供未来顶层 cli.py 复用，`main(argv=None)` 供 `python -m cogos.lm_service.admin` 直接跑。

## 已读代码要点

- 蓝本 `admin.py:1-218`：`_parse_argv` 手写参数解析 + `service` 组（systemd）+ `api-key add` 带 `--model/--base-url/--max-concurrent/--max-rpm`（旧单 json 语义），全部舍弃
- 本工程 `config.py:106-163`：`add_api_key(provider,account,api_key)` 三参（校验 account 存在 config.yaml）、`delete_api_key` 有 active internal key 守卫、`add_internal_key` 返回 ik_id、`delete_internal_key` 置 revoked（软删）

## 关键结论/决策

- admin 命令不碰 base_url/model/并发（这些进手写 config.yaml）；CLI 只写 secrets.yaml（api_key）+ state.yaml（internal_key）
- chmod 0600 由 `config.save_secrets()` 的 `_atomic_write(...,0o600)` 保证，admin 不重复处理
- list 输出 json（indent=2, ensure_ascii=False），机器可解析、供 AI 助手 grep

## 遗留/坑

- **环境坑**：yaml 装在 user site-packages（`~/.local/lib/python3.11/site-packages`）。`export HOME=/tmp/...` 测试时 user site 被移出 `sys.path` → `import yaml` 失败。本地验证三文件需 `PYTHONPATH=/home/zhengyp/.local/lib/python3.11/site-packages` 补回（或不用 HOME 劫持、改 `Config(base_dir=...)` 直测）。
- 蓝本 adapter 旧 `ProviderError(status, msg, raw)` 位置参数，轮 4 改 category 时同步改 deepseek/openai 调用点（承接 checkpoint-1 遗留）。
- `delete_api_key` 会拦「仍有 active internal key 引用」——测试 delete 顺序须先 revoke internal key。
