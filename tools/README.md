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

## 交接（handoff）

交接用 Kilo 的 `handoff` 工具（由 kilo-resident 的 resident 桥接提供），**不在本目录**：起新 session 并确认已起来，默认同目录、默认继承本会话模型，可用 `model: "providerID/modelID"` 覆盖。用法见 `../rules/task.md` 的「交接」。

## 约定

- secret 一律放 `~/.secrets/`，不进 repo。
- 若工具需带 secret 进 git，须先加 `.gitignore` 防误提交。
