# task-7 设计决议（2026-09-11，YZ 逐条拍板）

来源：工位 B `../checkpoint/task-7-design.md`（原始细节 + 实测依据）。本文件为 locus 记忆层的决议快照。

## 决议 9 条

1. **上下文**：所有输入共享一条脉络（单会话），串台接受。
2. **飞书信任边界**：配置文件化账号白名单；列表内允许进入（YZ=superuser 全权，其余按条目分级），**列表外无响应**（静默丢弃、不回）；身份在桥接层判定，不交给模型。
3. **工程绑定**：**不绑目录**；每目录一枚飞书 bot，桥接按「消息来自哪个 bot」映射 `bot→目录/session`；daemon 中性起、插件全局。
4. **常驻宿主**：`kilo daemon`；不开机自启，人工手动 `start`/`restart`。
5. **窗口默认**：裸 `kilo` 为普通会话；连常驻显式 `kilo attach <url>`，不加别名。
6. **回复路由**：严格按 `messageID/parentID` 归属——注入时带可控 `messageID`，助手 `parentID` 回指它，只把飞书触发的回合推回飞书。✅ 已实测（`exp12`）。
7. **忙时注入**：**B 排队等 idle**（桥接订阅 `session.status`/`session.idle`，FIFO，idle 再注入）；队列上限/超时兜底待定。
8. **飞书入站**：**桥内独立直连 WS**（`lark_oapi`），用 Kilo 自己的 bot 凭据 `~/.secrets/feishu.key`；**不走 cogos daemon socket**。首个 bot＝`KILO-LOCUS-A`（`cli_aa2949ffb4789bfb`，凭据已验证）。
9. **飞书出站**：**桥内直连 open API，文本与文件都支持**（`im/v1/messages` `msg_type=text|file`；文件先 `im/v1/files` 上传）。
10. **转实现时机**：**先补验证再转**（见下）。

## 三项待验证（实现前）

1. TUI `attach` 后窗口输入是否落同一 session（真终端手测）。
2. 飞书入站 → Kilo → 回飞书 真机往返（bot `KILO-LOCUS-A`）。
3. 多窗口/窗口+飞书并发顺序与串台表现。

## 关键坑（写代码必读，摘自 report）

- 插件按 `event.id` 去重（事件投递 2 次）。
- 插件内回执审批必须自建 `createKiloClient({baseUrl:serverUrl})`，别用 `PluginInput.client`。
- 事件名以运行时为准（`session.idle`/`session.status`/`message.part.delta`/`permission.asked`/`pty.exited`），SDK 类型滞后。
- 内置 bash 无完成事件；后台完成唤醒需自建 `run_bg`。
- 模型每次 prompt 显式传；改 `kilo.json` 默认模型运行时不生效。

## 上下文轮换（2026-09-11 补充决议）

长脉络涨上下文时的三种手段（`exp13_summarize.mjs` 实测）：

1. **原地压缩（默认）**：`session.summarize {providerID, modelID}`（TUI `/compact`）。同 session id，追加 `summary=true` 摘要 + 打 `summary` 标记 + 发 `session.compacted`；桥接无需改 pin。
2. **新 session（`/new`）**：`session.create` + **重 pin**（桥接订阅 `session.created` 按 directory 更新 `bot→session`）；否则窗口/飞书分叉。
3. **fork/裁剪**：`session.fork({messageID})` 保留前缀丢尾部；`session.abort`/`session.delete`。

决议：默认「原地 summarize + 阈值触发」（插件监听 `session.idle`，估 token 超阈则 summarize）；`/new` 仅作彻底重开、须配套重 pin。自动压缩有无未确认。

## 命令执行与定时器（2026-09-11 补充决议）

借鉴 cogos `agent/terminal.py` + `docs/design-terminal-timer.md`，拆成两个**相互独立、由模型编排**的能力：

- **terminal**（非阻塞命令会话）：`open`/`exec`/`observe`（cursor 增量）/`cancel`（killpg）/`list`/`close`；正常退出发一次完成事件；**不自带周期通知**。阶段1 subprocess、不上 pty。底座二选一：复用内置 `background_process`（需复核其事件）或自建移植 cogos terminal。
- **timer**（通用自唤醒/提醒）：`set_timer`/`cancel_timer`/`list_timers`，到点发 `timer_fired`。**与命令解耦**、周期由模型定，可用于自唤醒（peek/再等/停命令）或**定时提醒用户**。
- **约束**：timer **用户可见可控**（窗口 + 飞书命令列表/取消），**不做后台常驻轮询**（无 timer 时休眠，事件驱动），落盘持久，设上限/最小间隔。
- 原理：完成事件负责"提前结束"，timer 负责"自唤醒/提醒"，命令本身不承担等待策略。
