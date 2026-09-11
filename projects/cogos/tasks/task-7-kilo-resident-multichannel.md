# task-7 — Kilo 常驻 + 多通道（飞书/窗口）spike

> 状态：待执行。**工位 B owner（设计 + 实现同一人）**。工位 A 只在结束时做独立复核；开放决策由 YZ 裁决。
> 性质：**spike（可行性 + 设计）**，不是实现任务。目标是把"常驻 Kilo + 事件唤醒 + 飞书/窗口双通道"的技术路走通并产出设计，**不要**一上来做产品。
> 归属：Kilo harness 支线（由 cogos 自驱主线引出）。实现落在 Kilo 侧，**不碰 cogos 代码**；若后续转实现，再另立 locus 工程。

## 目标

证明并设计：一个**常驻的 Kilo**，能同时接受两类输入——窗口（TUI）与飞书消息——任一都能唤醒它，且回复能回到来源通道。回路机制复用 cogos 已验证的思路（统一事件队列 + 多输入适配器 + 输出路由）。

## 已确认事实（工位 A 已查，直接可用）

**Kilo 能常驻（server 模式）**
- `@kilocode/sdk`：`createKiloServer(options?)` → `{ url, close }`；`createKiloClient(config?)` → `KiloClient`；还有 `createKiloTui(options?)`。本机包在 `~/.config/kilo/node_modules/@kilocode/sdk`。
- `KiloClient` 有 `session.prompt` / `session.promptAsync` / `session.abort` / `session.command` / `session.shell`。

**插件 = 事件回调入口**
- 包：`~/.config/kilo/node_modules/@kilocode/plugin`（v7.3.21）。
- `Plugin = (input, options?) => Promise<Hooks>`；`PluginInput = { client, project, directory, worktree, serverUrl, $, experimental_workspace }` —— **`client` 就是 `createKiloClient` 的返回，可用于注入 prompt**。
- Hooks：`event({event})`（收**所有总线事件**）、`chat.message`、`tool.execute.before/after`、`tool.definition`、`tool: { <name>: ToolDefinition }`（自定义工具）、`experimental.compaction.autocontinue`、`permission.ask`。
- 加载：`kilo.json` 的 `plugin` 数组，或配置目录下 `{plugin,plugins}/*.{ts,js}` 自动发现。

**总线事件名（`@kilocode/sdk` 的 Event 联合）**
- `session.idle`、`session.status`、`session.created/updated/deleted/error`、`message.updated`、`message.part.updated/removed`、`permission.updated/replied`、`command.executed`、`file.edited`、`todo.updated`、`pty.created/updated/exited/deleted`。
- **`pty.exited` = 命令完成的天然事件**（terminal_done 的等价物）。

**飞书侧已有件**
- 出站：本机 global `kilo.jsonc` 已配 MCP `feishu` → `~/.config/kilo/tool/feishu_server.py`（发文件 + 用户别名；走 `~/.secrets/feishu.key`）。
- 入站：复用 cogos 的 `cogos/feishu`（daemon/ws）长连接，把消息桥成 Kilo 事件（B 已有 cogos worktree）。
- cogos 的 `terminal.py` 语义（busy/idle + buffer/cursor + killpg + 完成事件）是**设计已验证**，不是可搬代码。

## 待验证清单（spike 的核心产出）

1. **常驻**：`createKiloServer` 能否起 headless server；CLI 是否有 `kilo serve`；server 生命周期内 session 是否持久、能否重连。
2. **多前端共用一个 session**：TUI 窗口 + 另一个 client（飞书桥）能否同时 attach / 驱动同一 session；消息顺序、并发 prompt 的行为（排队 / 报错 / 打断）。
3. **事件唤醒**：插件 `event` 能否收到 `session.idle` / `pty.exited`；收到后调 `client.session.prompt` 注入是否能唤醒空闲会话；**忙时注入**的行为。
4. **回复回灌/路由**：用 `event` + `message.part.updated` 能否捕获 assistant 回复，并按来源通道转发（窗口来的回窗口、飞书来的回飞书）。
5. **后台命令完成事件**：内置 `background_process` / pty 是否会发 `pty.exited`；若不发，需自定义 `tool` 包一层来发事件。
6. **上下文策略**：共享一条脉络 vs per-channel context；串台风险。
7. **安全边界**：飞书是外部不可信输入，驱动一个能跑 bash 的 agent = 提示注入 + 越权；需要信任分级（如飞书侧默认只读/只提案，危险动作回窗口确认）。

## 建议实验步骤（最小、递进）

1. 起 headless server（`createKiloServer` 或 CLI serve），用 SDK client 发一条 prompt 给一个 session，确认能跑且能收到 `session.idle`。
2. 写最小插件：`event` 里打印事件；确认能看到 `session.idle`、`pty.exited`、`message.part.updated`。
3. 插件在收到 `session.idle` 后调 `client.session.prompt` 注入一条 → 验证"事件唤醒"。
4. 忙时注入一次，记录行为（排队/打断/报错）。
5. 自定义一个 terminal 风格 `tool`（包 pty），完成后确认 `pty.exited` 上总线；对照 `terminal.py` 语义。
6. 飞书入站桥接：用 cogos `feishu` daemon 把一条真人消息注入 session；回复经 `event` 观察后转回飞书。
7. 窗口 + 飞书同时打，观察串台与顺序。

## 交付物

- `work/B/checkpoint/task-7-report.md`：上述 7 项逐条结论（可复现命令 / 观察），标"确定 / 推测 / 未验证"。
- 最小原型：`work/B/kilo-spike/.kilo/plugin/*.ts`（唤醒 + 注入；后台完成事件）。
- 设计草案：常驻形态（headless server vs in-TUI 插件）、通道模型、回复路由、上下文策略、安全分级。
- YZ 决策清单：上下文共享 vs 分通道；飞书信任边界；是否转实现、转哪条路。

## 停下点

spike 跑完、报告 + 原型 + 设计草案齐，飞书通知 YZ。**不实现完整产品**；等 YZ 裁决再决定是否转实现。

## 前置 / 环境（B 开工前先确认）

- `kilo --version` 可用（A 侧是 7.3.45，node v24）。
- `~/.config/kilo/node_modules/@kilocode/{plugin,sdk}` 存在。**若 B 机器没有 Kilo 或这些包 → 先装/报阻塞，别硬做。**
- `~/.secrets/feishu.key`、`~/.secrets/feishu-users.json` 可用（飞书）。
- `python3.11` + cogos 仓库（飞书入站桥）。
- 网络可达飞书 open API。

## 工程规范

- 只做 spike 原型，不改 cogos、不改 Kilo 本体（默认插件路径；若确认必须改本体 → 停下，通知 YZ）。
- 密钥不落仓库、不进日志。
- 可复现：每个结论附命令/代码锚点。
- 所有权：本任务 B 自有；A 不参与过程，只在结束时复核；开放决策上报 YZ。

## checkpoint 工作法

- 每阶段写 `work/B/checkpoint/`：`status.md` + `checkpoint-N.md`（锚点 `文件:行` 优先、凝练可恢复）。
- 结构：当前问题 / 已做修改 / 关键结论 / 遗留坑；每阶段 `status.md` 写"下一步读什么锚点"。
- 阶段结束飞书通知 YZ。
