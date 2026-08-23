# phone-term（Phone 交互终端 TUI）

待 YZ 讨论的下一个方向。给 agent 使用者的真人一个交互式终端，直接操作 Phone 的卡片与会话、收发消息。挂在 Phone 抽象（`cogos.phone.phone.Phone`）之上，与现有 agent-term（`cogos/feishu/term.py`，daemon 长连接终端）区分。

## 界面四区

- **状态栏**：card 列表和状态
- **会话区**：当前会话的消息历史
- **命令区**：命令与消息发送
- **输出区**：非消息输出（帮助信息、错误提示）

## 启动

```
cogos.phone.term <phone.json>
```

（`phone.json` 为 Phone 配置路径，等价现有 `Phone(config_path=...)`。）

## 支持命令

- `/help`
- `/add_card`
- `/rm_card`
- `/set_default_card`
- `/list_session`
- `/switch_session`

## 消息发送

直接输入的文字 = 以默认 card 发送到当前会话。

## 备注 / 待澄清

- 命令参数形态未定（如 `/add_card <number> <pin>`、`/switch_session <id>`）。
- 读消息历史可复用可观测性（checkpoint-24/25）的落盘面（store 已落 cards/contacts/chats 含 messages+read+members）；`snapshot()`/`tail()` 观察接口当时缓做（YAGNI），若 TUI 需要读盘可能重新评估。
