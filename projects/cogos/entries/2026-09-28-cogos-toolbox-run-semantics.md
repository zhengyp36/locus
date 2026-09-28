# cogos toolbox：run 语义定稿（N3 收口，2026-09-28）

> **状态**：**已落码并验证**（cogos `ab46a5b`，A 工位执行，09-28）。N4／`to` 一并。前序 `entries/2026-09-28-cogos-toolbox-fix.md`（其"未决"里的 N3/N4）。

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

## 落地（已执行，09-28）

- **run**：catalog 改 `impl=terminal_exec`（去 `steps` 组合机制，删 `_run_composed`／`_observe_settled`）；结果＝中性发起回执（去 `id`/`session`，带一句读法 note）；`computer.command` 面级 help 给取值配方（`catalog.FACE_NOTES`：observe 看屏／大输出重定向＋`file.read`）；暴露可选 `notify` token 参数。time_form 仍 `async`（后果型）。
- **N4**：新增 `computer.web.cancel`(`web_cancel`)、`communication.file.cancel`(`phone_cancel`) catalog 条目（参数 `job_id`）。
- **`to`**：`communication.message.send`／`communication.file.send` 模型面改 `to`，catalog `arg_map={"to":"target"}` 映射到 impl，impl 不动。
- 提交 `ab46a5b`（push origin master）＋ doc `ea2812c`。测试：`tests/agent` 277 passed／3 skipped；全量 1281 passed／5 skipped（唯一 fail `tests/image_ctx/test_p2.py::test_mark_pixel_lands_on_tool` 系缺外部 `/tmp/kilo/vision/...` 素材，与本改无关）。

## 批 0 复评（n=10，真实 deepseek + FakeTelecom，harness `scripts/exp_agent_behaviour_probe.py`）

- **判据（重设后）全过**：成功 10/10、**help 0/10**、工具错 **0/10**、往返 **5**（基线 4）。
- **实测轨迹**（10/10 一致）：`run{cat}` → `run{cat … > out.txt 2>&1; echo done}` → `file.read{out.txt}` → `send{to}`。取值**全走重定向＋file.read**（设计期望路径），非 observe。
- **why（取向）**：批 0 首轮的"往返不达"＝**不公平基准**（4 轮是"猜完成"换来的）＋三个正交摩擦（`to` 猜错 ×10、`session` 回显诱导 ×5、run 无回执→重跑/help）。A（读法可见性）＋B（去 session）＋`to` 落地后摩擦尽消，往返 5 可接受 → **保留 N3 健全语义**。
- **被否**：**C `settled` 过渡**——既不取值也非真完成信号，模型无从行动，且近"猜完成"边界；要真信号只能是 `observe`（真屏）或 OSC `term.notify`（真事件）。**D 原样接受 8.2**——漏掉已识别的确定性摩擦，不采（取其"可靠优先"排序，不取其内容）。
- **遗留观察**：模型先跑一次裸 `cat`、再重跑带重定向（多 1 轮）；可在描述里更明确引导"一开始就重定向"，或接受（不阻塞）。

## 复查修复（09-28，cogos `8bb00b3`）

- **工具结果泄漏 numeric `id`**：`observe`/`interrupt`/`send`（及 `run`）的结果带内部会话号 `id=<n>`；N3 后 observe 成主路径，此泄漏＝给模型一个"无法合法回传"的句柄（B 要消除的 session 诱导）。修：需注入 session 的能力结果统一去掉 `id`。
- **事件键不匹配**：terminal 事件 payload 用 `session_id`，`render_event` 只认 `id` → `term.done`/`term.notify` 实际渲染成 `session_id=…`（泄漏内部名、S4 对象标签从未生效）。修：term 事件把 `session_id`→`session="tN"`；测试改真实 payload 键。
- 修复后 `tests/agent` 278 passed；复跑 n=10 无回归（10/10、help 0、错 0、往返 5）。证据 `checkpoint/26-09-28-toolbox-model-face/`。
- **遗留（未改，属设计判断）**：单会话期事件仍带 `session="tN"` 标签，但 `open`/`list` 已撤、模型无法定向会话 → 该标签暂时是"inert handle"，长期可能重引 session 诱导；是否在单会话期也从事件里去掉，待 YZ 定。

## 过渡（未采用）

- ~~`run` 返回加 `settled: true/false`~~（见上"被否 C"）。

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
