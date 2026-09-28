# cogos toolbox：run 语义定稿（N3 收口，2026-09-28）

> **状态**：讨论定稿（YZ 同意），**未落码**。N4 并入。前序 `entries/2026-09-28-cogos-toolbox-fix.md`（其"未决"里的 N3/N4）。

## 结论

- **N3 定性**：不是"等待时长"问题，是 **`computer.command.run` 语义错位**——它是后果型（执行命令），却声明为取值型（`returns="命令输出文本"`，catalog.py:93），于是机制用"屏稳定"（`_observe_settled`，toolbox.py:280-308）猜完成 → 静默截断。根因＝把"写世界"和"读世界"混进一个调用。
- **正解**：`run` 改"发起即返回"（exec 语义、**不取值**）；**取值收敛到读类**——`file.read`（忠实输出，走重定向）＋ `observe`（屏态，天然有界）。依据是既有 design §5.2："忠实输出不在工具里做，agent 自己重定向＋文件工具"（design-agent-tools.md:72）。**不新增机制**。
- **保留 `run` 名**（YZ）：名字本身没问题（动词、与 catalog 风格一致）；改的是语义不是名字。仅当要与 §5.1/`terminal_exec` 用词统一时才值得改名 `exec`。

## 命令结束通知：机制已有，只需暴露

- 机制层**已实现**：`OSC_PREFIX="cogos;"`（terminal.py:38）＋ OSC filter 抽 token（:111-165）＋ `_maybe_notify` emit `term.notify`（:626-638），另有 `term.done`；`events.py:10-19` 已登记 `term.notify → computer.command`。
- **不需要独立 notify 工具/开关**：设计即"随命令一次性带 token"（`exec(command, notify=...)`，terminal.py:229-233 `_once_tokens`）。只需**暴露 `run` 的可选 `notify` 参数 + help 讲 token 用法**（`cmd; printf '\033]cogos;<token>\007'`）。
- **约束**：token 由模型显式埋进命令，机制只转发、**绝不自动检测命令结束**（否则重演 N3 的"机制猜完成"）。
- **短板（属主线）**：`term.notify` 事件 emit 了、`render_event` 也有，但全仓**无消费者** → "事件 → 唤醒 agent"**未接通**（events.py 自称 wake the agent，实际未接）。
- **范围**：notify 只服务慢/长命令；短命令走 redirect + read。

## N4 并入 + cancel 命名定案（09-28，YZ 同意）

- **问题**：`web_cancel`（tools.py:380 / app.py:257）与 `phone_cancel`（tools.py:503 / app.py:261）**已实现并注册**，但 catalog 无对应 Capability → 模型能发起长任务（`computer.web.search/fetch`、`communication.file.send/receive`）却无法取消。与 N3 同源 ＝ **工具原语暴露不完整**（registry/impl 有、catalog 缺）；**非"有意不给"**（design §14 明确定义 `phone_cancel(job_id)` 同步幂等）。
- **暴露**（新增两条模型面能力）：

  | 模型语义 | 模型面 path | 机制 ToolDef |
  |---|---|---|
  | 取消网页作业（新） | `computer.web.cancel` | `web_cancel` |
  | 取消文件作业（新） | `communication.file.cancel` | `phone_cancel` |

- **命名定案**：
  - **有 job 句柄的取消统一用 `cancel`**（timer 已是 `computer.reminder.cancel`；web/phone 同）。
  - **归类按"发起面"**：在哪发起就在哪取消（web 的取消在 `computer.web`，文件作业的取消在 `communication.file`）。
  - **`interrupt` 不并入 `cancel`**（YZ 定）：`interrupt` ＝ 打断**前台命令**（向 pty 发 `^C`，无句柄）；`cancel` ＝ 撤销**已登记作业**（带 `job_id`）。语义不同，合并会丢信息。
  - **不重复**：同一作业只一条取消路径、一个词。
- **命名分层原则**（本决定引出，普适）：模型面名只描述**能力语义**、**不泄漏机制实现**（同 fix 3 删 help"绑定"行）；机制名本身干净达意（`read`/`send`/`cancel`）**可同名**，带实现气味（`terminal_cancel`/`send_msg`）**须换**；组织按**能力心智模型**（command/file/screen/web/message），非代码分包（terminal/phone/timer）。

## 落地（建议批次）

- **B1**：`run` 去取值（改 exec 语义，删 `_run_composed` / `_observe_settled`）＋ 暴露 `cancel`(N4) ＋ time_form 修正（run 现标 `async`，catalog.py:94；改语义后明确为后果型）＋ help 写 redirect 指引与 notify token 用法。
- **B2**：不新建；仅把 `term.notify` 接到模型面（随 B1 的 notify 参数）。
- **过渡**（若 B1 不即落）：`run` 返回加 `settled: true/false`，不冒充完成。

## 被否

- ❌ **run 用 OSC token 换判据**：仍要机制注入 token、等事件，多一层；B1 的通路更优，无此必要。
- ❌ **加裸 tick/心跳修 N3**：tick 属发育后期，"裸 tick 生不了念"（`entries/2026-09-13-cogos-v0-arch.md`）；命令完成是**后果事件**，不是时钟问题。
- ❌ **保留 run 取值 + 屏稳定判据**：不可靠，违 §5.2。
- ❌ **独立 notify 工具/开关**：违"随命令一次性"（§5.4）。
- ❌ **每次命令自动 notify**：§5.4 明确默认关、显式开。
- ❌ **改名 exec**：非必要（除非为与 §5.1 用词统一）。

## 锚点

- 代码：`cogos/agent/toolbox.py:256-308`（`_run_composed`/`_observe_settled`）· `cogos/agent/catalog.py:88-95`（run）· `cogos/agent/impl/terminal.py:38/111-165/229-233/626-638`（OSC/notify）· `cogos/agent/events.py:10-19`（事件映射）
- 设计：`docs/design-agent-tools.md` §5.1（exec 发起即返回／不推断完成）· §5.2（忠实输出靠重定向＋文件工具）· §5.4（notify 默认关、显式开、token 随命令）
- 行为证据：`entries/2026-09-28-cogos-toolbox-behaviour-probe.md`
