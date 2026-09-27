# toolbox-design · 工具层统一形状（2026-09-28）

> **一句话**：工具层只有一个 `toolbox`；能力用 `组.面.能力` 路径寻址；机器是路径的**隐含上下文**；人 / agent 的差别只表现为**事件**。
> 性质：讨论定稿（呈现形状）；命名待定；不落码。入口见 `ENTRY.md`，分组见 `toolset-decisions.md`。

## 1. 唯一工具

```
toolbox(command="help", name=?)         # 展开；省略 name = 总览
toolbox(command="call", name, args={})  # 执行
```

- tool-schema 恒定（不随视角变）→ 命中缓存。

## 2. 命名空间（`name` 的取值）

```
computer.command.*     run / observe / interrupt / answer_auth
computer.file.*        read / write / edit
computer.screen.*      look / act / save
computer.web.*         search / fetch
computer.reminder.*    set / cancel / list
communication.message.send  communication.file.send / receive
vision.*               see / mark / coord
```

- 组：`computer` / `communication` / `vision`；**无独立控制面**——换机＝换视角（§4）。

## 3. 电脑的面

- **面**：command · file · screen · web · reminder。
- **`reminder` 必须走事件**（命令 `sleep` 唤不醒）；时区与取时间归环境描述 / `command`（`date`）。

## 4. 机器＝路径的隐含上下文

- `computer.*` 读作"**当前这台机器**"，**不**读作"我的机器"；当前是哪台由**视角总览**承载，模型不查询、不记忆。
- 默认 = `self`（无名）；**换机＝机制追加一份视角总览**（该机身份／环境描述 ＋ 面清单），模型不调 switch。
- **每台机器声明自己的面**；如 `surface` 只有 `screen`，则 `computer.command.*` 在它上面**不存在**、`help` 里不出现。
- 名字 ＝ 机器自己的身份（host / 账户 / 别名）；**不在名字里区分人 / agent**（那是关系与在场，走事件）。

## 5. 事件＝第二条通道（不进 toolbox）

- 命令完成、提醒到点、来信 / 文件，以及机器的 **同意 / 被抢(observer) / 收回** → 消息。

## 6. 协助（screenlab）接入

- ＝ `screen` 面的**一个后端**（远端 / 协助），与 X11 本地后端并列；`screen/1` ＋ `auth/1` **不改**。
- 那台机器成为**另一个视角**（只声明 `screen`）；切换＝机制追加总览。
- 同意 / 被抢 / 收回 → 事件消息；**无专属工具、无专属动词**。
- config：单 `computer` ＋ `graphics_endpoint` → **机制侧机器表**（每机 faces ＋ endpoint / key）。
- 权威口径：`design-agent-tools.md` §17；目标 `spec-screen-1.md` §0.0。

## 7. 已否（why）

- **`human-desktop` 命名** → 把"宿主是人"焊进机器名，破坏 3a/3b 对称；机器按身份命名。
- **给 assist 做专属动词** → 协助 ＝ 切到"只有 screen 面的机器"，与自操作同形状。
- **每个调用传机器名** → 机器是视角上下文；换机要换环境描述，正合"视角＝用法契约"。

## 8. 未定

- 命名：**模型面标识已定＝英文路径**（§2 / §9）；机制面命名分层见 **A5（§11）**；余 `toolbox` 参数名待定。
- `toolbox help` 展开：**已定＝精确路径前缀**（空 / 组 / 面 / 能力四级，见 `ENTRY.md`）；`help` 空去留见 **B3**。
- 跨机单步动作（A→B）与"当前视角"的张力。
- 用法保温 / 淘汰策略：**A4 已定**（§11）。

## 9. 工具清单（模型面 → 实现）

> 依据 §1–§6。把现有 **38 个实现工具**收敛为 **~21 个模型面能力**；实现名保留、模型面另立（名分离）。
> 唯一工具：`toolbox(help / call)`。

### computer（当前机器）· 15

| 路径 | 干什么 | 实现（旧名） |
|---|---|---|
| `computer.command.run` | 跑一条命令，拿输出 | `terminal_open`＋`terminal_exec`＋`terminal_observe`（合并） |
| `computer.command.observe` | 回看当前会话输出 | `terminal_observe` |
| `computer.command.interrupt` | 打断当前命令 | `terminal_cancel` |
| `computer.command.answer_auth` | 回应登录 / 密码提示（用我的凭据，**无值、不选槽**） | `terminal_write_key`（值留在机制） |
| `computer.file.read` / `write` / `edit` | 读写改文件 | `read_file` / `write_file` / `edit_file` |
| `computer.screen.look` | 取当前屏幕一帧（当前视图） | `screen_fetch` |
| `computer.screen.act` | 在刚看到的帧上动作 → 回新帧＋落点 | `screen_act` |
| `computer.screen.save` | 把当前帧存成文件 | `screen_save` |
| `computer.web.search` | 搜网页 → 结果 | `search`（**去 `job_id`**） |
| `computer.web.fetch` | 抓网页正文 → 结果 | `fetch`（**去 `job_id`**） |
| `computer.reminder.set` / `cancel` / `list` | 提醒 | `set_timer` / `cancel_timer` / `list_timers` |
| **机制** | 会话生命周期 / 原始字节 | `terminal_open`(裸) / `close` / `list` / `write` |
| **机制** | web 取消 | `web_cancel` |

> **密码如何输入（`write_key` 归机制的落法）**：归机制收走的是**值与槽位选择**，不是"输入"这件事。
> ① 凭据在**装配时按会话 / 目标绑定**，pty 遇登录提示（`sudo` / `ssh` …）**自动注入**，模型只 `command.run`；
> ② 自动识别不准时，用 `command.answer_auth` **无值应答**——模型只指"时机"，不见值、不选槽；
> ③ 多目标（ssh 到不同 host）→ 凭据按**目标**绑定，不是"每会话一条"；
> ④ 无绑定却遇提示 → 事件报机制层，不逼模型现造；
> ⑤ 模型自建密码本（§15）是另一件事，仍挂。

### communication · 3

| 路径 | 干什么 | 实现（旧名） |
|---|---|---|
| `communication.message.send` | 给联系人或号码发消息 | `send_msg` |
| `communication.file.send` | 把一个文件发给对方 | `phone_send_file`（**去 job / spool**） |
| `communication.file.receive` | 取回收到的文件 | `phone_download`（**去 job / spool**） |
| **机制** | 取消 / 暂存区管理 | `phone_cancel` / `phone_spool_list` / `phone_spool_delete` |

### vision · 3

| 路径 | 干什么 | 实现（旧名） |
|---|---|---|
| `vision.see` | 打开一张图、或放大局部（放大＝开窗） | `see` |
| `vision.mark` | 在图上标注 | `mark` |
| `vision.coord` | 读标注的源图坐标 | `coord` |

> `screen` 与 `vision` 的分界：`screen` ＝ 当前机器屏幕的**取帧与动作**；`vision` ＝ 对**任意一张图**（含 look 出的帧）的看 / 标 / 读；放大＝`vision.see` 开窗。

### 一并归机制（不进模型面）

- `scratch_*` 六个 → 私域＝`file` 面下的策略，或纯机制。
- `transfer` → 通信文件收发的内部搬运（家 ↔ spool）。
- **作业句柄**：`job_id` / `handle_id` 全归机制，模型面只呈现"提交 → 结果 / 事件"。

### 事件的统一形状（第二条通道）

- `[computer.command] …` · `[computer.reminder] …` · `[computer.web] …`
- `[communication.message] …` · `[communication.file] …`
- `[machine <name>] 同意 / 被抢(observer) / 收回`

## 10. 归机制的漏项审计（2026-09-28）

> 规则：归机制只收 **值 / 句柄 / 槽位选择**，**不收"动作本身"**。凡模型必须能表达"时机"的，保留一个**无值**动作。

| 归机制项 | 丢了什么 | 补法 |
|---|---|---|
| `terminal_write` | **非行输入**：Tab 补全 / 方向键 / `^D` / `^Z`、TUI 菜单、非回车即时响应 | 值无关的 `command.send`（发一段文本或按键，**不隐式回车**）；或明确"只支持行式交互" |
| `terminal_open` / `list` | **多会话并发**、指定 `cwd`、看"在跑什么" | **A2 已定**：支持多会话；会话＝对象索引；`open(cwd?)` 开新会话；`list` 倾向保留（§11） |
| `notify` token | 何时被叫醒 | **§12.3**：通知是**模型可选的原语**（订阅 / `term.done` / timer）；完成判定不由机制推断 |
| `job_id` / `handle_id` | 异步结果的**配对**（哪条结果对应哪个请求） | **对象索引**（§12.7）：世界对象的可见短标签，事件 / 结果 / `read` 统一用它 |
| `phone_spool_*` | 收到的文件**落在哪**、`file.send` 的源路径 | 收到的文件**落地到家电脑**（`file` 面可达），`file.receive` 直接给路径；spool 只在机制内。附件下载默认自动 / 事件带路径 |
| `scratch_*` | 有界私域 / 禁删 / `id=0` 信箱 | 私域＝（家）电脑上的目录，经 `file` 面读写；有界 / 禁删 / `id=0` 信箱作**机制策略** |
| `web_cancel` / `phone_cancel` | 喊停 | 机制超时兜底；或接受"不可取消" |
| `transfer` | —— | **无新增**；跨机单步动作仍挂（§8） |

**三处要紧**：`terminal_write`（→ A1 已定）、`terminal_open/list`（→ A2 已定）、`phone_spool`（收到文件落哪，留实现）。其余作机制策略或接受。

## 11. A 项定稿（2026-09-28）

> A ＝ 文档已列「未定 / 审计」，本轮裁决。尺子：**上下文即记忆**（`ENTRY.md` 尺子2）。

- **A1 · 非行输入**：保留无值动作 `computer.command.send`——原样发文本 / 按键（**不隐式回车**），控制键用记号（`^C` / `^D` / `<Tab>`）由机制翻译；与 `run` 并列。理由：真实命令多 TUI，只支持行式跑不通"真实操作"；按键不是值，符合"归机制只收值 / 句柄 / 槽位，保留无值动作"。
- **A2 · 多会话**：**支持多会话**（长跑 dev / build、快命令、TUI 各一条）。会话 ＝ 对象引用（B1）；`run` / `observe` / `interrupt` / `send` 带 `session`，省略 ＝ 默认会话；开新会话倾向 `computer.command.open(cwd?) → 标签`；`list` 倾向保留作保险。连带：`run` ＝ open ＋ exec ＋ observe 的**合并须拆**——合并是单会话假设的产物。
- **A3 · 句柄配对**：并入 **B1**「对象引用」，统一短标签。
- **A4 · 保温 / 淘汰**：本步**不做物理淘汰**，保温即默认；唯一"作废" ＝ 视角切换的就近追加，以最近为准。理由：淘汰 ＝ 真遗忘、永久丢失，代价高；token 次要。
- **A5 · 命名分层**：**实现名自由**（仅服务代码 / 调试）；**机制装配词汇 ＝ 模型面路径词汇**（同源，免映射）；"机制工具面"不是需要命名的一层——归机制者是实现细节。实现名 ↔ 模型路径的映射落 B 适配器（`ToolDef`）。

## 12. 消息化与送达（2026-09-28）

> 承接：调用级时间形态 ＋ 结果消息化 ＋ 送达不可靠。尺子：**上下文即记忆**（`ENTRY.md` 尺子2）。

1. **sync / async ＝ 调用级，agent 定**（不是工具属性，也不是"取值 / 后果"）：**内部有界操作同步**（记忆整理、文件读写、取值），**外部调用可打断、默认异步**。判据由 `design-agent-tools §4` 的"取值型 / 后果型"改为"**内部 vs 外部**"。
2. **无搭车**：每个调用一条结果；**异步的实结果、事件各自是独立消息**。同步只是"调用方选择等这一条"。
3. **完成判定归模型，机制不推断**：机制只给原语——**结果重定向（落文件）**、**事后读**（`fs.read` / `observe` / `see`）、**通知**（term 的 `notify` token / `term.done` / timer）。模型自选：同步等 / 轮询 / 订阅。`run` 不做完成推断。
4. **工具实现落 term**：工具 ＝ 在会话里跑的程序，白拿通知 / 重定向 / `observe`；**呈现层仍保 3 组 ＋ toolbox**；**感知类**（`vision.*`、`screen.look/act`）走**带附件的结果消息**，不命令化。
5. **抹痕**：发起走厂商 `tool_calls`，回程**不走厂商格式**，渲染成自家消息——**每轮一个 cu**（结束请求 → 渲染 → 重发）；**渲染模板 ＝ 机制默认 ＋ 工具覆盖**（落 `ToolDef`）；归属头 `[<path>] …`（与事件同形）；渲染消息必须**写明"是模型自己调用的"**（`tool_call` 已抹，否则模型不记得）。
6. **送达尽力而为，世界是真相源**：结果**丢得起 ⟺ 可重新获得**——① 世界还记得（痕迹：图 / 文件 / 屏 / 会话 / spool）；② 操作可重做（`search` / `fetch` / `time` / `list` / `observe`）。→ **不设收件箱、不做送达去重、不要求模型记得**；`search` / `fetch` **可选落文件**稳定化。**后果型**（`send_msg` / 发文件）不得靠重做，查证走回执 / spool。
7. **对象索引**：需跨调用指认的世界对象（会话 / 图 / 文件 / job…）由机制发**短标签**，即**对象索引**——它是**世界对象的引用**（用于指认与重新获得），**不是收件箱**。事件 / 结果 / `read` 统一用它。

**待定**：抹痕循环形状（每轮一个 cu）确认；渲染**角色 / 归属头**；`help`(空) 去留（倾向取消）；`computer.command.open` 与否；`toolbox` 参数名。

## 锚

- 入口 `ENTRY.md`；分组 `toolset-decisions.md`
- 本体 `../cogos/docs/design-agent-tools.md`（§12 分包 / §17 协助）；`../cogos/docs/design-selfdrive-agent.md`
- 视觉 × 电脑 fusion：#63 `design-vision-computer-fusion.md`（模型面 look / act / save ＋ `vision.see` 开窗）
