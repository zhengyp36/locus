# tools

locus 自身工作流的工具（不属于任何被记忆工程的本体）。

## feishu_notify.py

飞书发文本消息给已注册用户，用于"做完通知审核 / 遇问题通知介入"。

```bash
tools/feishu_notify.py "文本消息" [bot_name] [alias]
echo "文本消息" | tools/feishu_notify.py   # stdin 输入
```

- 默认 `bot_name=admin-cli-test`，`alias=YZ`。
- 依赖（在 repo 外，勿提交）：`~/.secrets/feishu.key`、`~/.secrets/feishu-users.json`。
- 别名注册：见飞书 MCP 的 `register_feishu_alias` / `list_feishu_aliases`。

## handoff.py

起新 Kilo session 并确认已起来（交接用）。默认 `--dir`=cwd、`--attach`=`http://127.0.0.1:4097`、账号 `kilo/kilo`、`--timeout`=120s。

```bash
tools/handoff.py "<title>" "<第一句话>"
tools/handoff.py "<title>" -f handoff-NN.md   # 首句取自文件
echo "第一句话" | tools/handoff.py "<title>"   # 或 stdin
```

## 约定

- secret 一律放 `~/.secrets/`，不进 repo。
- 若工具需带 secret 进 git，须先加 `.gitignore` 防误提交。
