# code-map · toolbox 实现（活文档）

> **用途**：**交接 / 续接先读本文**，再按"既有相关锚"spot-read 代码——**避免重读全仓**。
> **纪律**：**每片完成即更新**。改动只影响模块 / 接口 / 锚 / 测试时才改写对应行（**重写式**，非追加）。
> **状态轴**：✅ 已实现 · 🔧 调试中 · ⏳ 未实现 · ♻️ 现有待改。
> **范围**：**只覆盖本次开发**（toolbox 呈现核心，`toolbox-walkthrough.md §2` 的 S0–S5）**实际会碰的文件**；**不做全仓地图**——与本轮无关的层（飞书通信 / phone / screenlab / cog_runtime 内部 / 视觉…）**一律不列**。
> **收口**：作为**本次开发**的 code-map 存 memory（scoped entry）；**不并**全仓 `entries/project-map.md`（那是另一件事、不本次承担）。

## 模块地图（计划 → 逐步填实）

| 模块 | 职责 | 关键符号 | 测试 | 状态 |
|---|---|---|---|---|
| `cogos/agent/catalog.py` | **模型面目录单一来源**：3 组 / 面 / 能力（`path`、一句 help、参数、绑定 impl 名或组合） | `CATALOG` / `resolve(path)` / `help_for(prefix)` | `tests/agent/test_catalog.py` | ✅ S0 |
| `cogos/agent/toolbox.py` | `toolbox` 元工具：`help` 四级 ＋ `call` 路由（含组合能力 `run`） | `make_toolbox_spec` / `_call` / `_DefaultSession` | `tests/agent/test_toolbox.py` | ✅ S1/S2 |
| `cogos/agent/app.py` | 装配：对外只暴露 `toolbox`；`system` 后注入常驻总览 | `_machine_env` / 两段 context | `tests/agent/test_app.py` | ✅ S3 |
| `cogos/agent/config.py` | 去工具清单（人设）；`render_overview` 出**机器环境 ＋ 3 组** | `render_system_prompt` / `render_overview` | `tests/agent/test_config.py` | ✅ S3 |
| `cogos/agent/consciousness.py` | 传入**单个** `toolbox` schema | `toolset_names=["toolbox"]` | `tests/agent/test_consciousness.py` | ✅ S3 |
| `cogos/agent/events.py` | 事件按**模型面前缀**渲染；term 事件 `id` → `session` 短标签 | `_EVENT_PREFIX` / `render_event` | `tests/agent/test_events.py` | ✅ S4 |
| `cogos/agent/impl/terminal.py` | 暴露 `shell` / `root`（供总览机器环境） | `shell` / `root` property | `tests/agent/test_terminal.py` | ✅ S3 |

## 既有相关锚（现在只需读这几处）

| 位置 | 作用 |
|---|---|
| `cogos/agent/app.py:228` `_build_specs` | 38 个 `ToolDef` 装配处（S3 改为只外露 `toolbox`） |
| `cogos/agent/app.py:215` | context 初始化（现只有 `system`；S3 在此后加常驻总览） |
| `cogos/agent/app.py:297` `_consume_events` | 事件 → `IncomingMessage(source=system)` → `on_message`（步 4 通道，已具备） |
| `cogos/agent/catalog.py` `CATALOG` / `help_for` | 目录单一来源：3 组 / 面 / 能力；help 四级渲染（空/组/面/能力） |
| `cogos/agent/toolbox.py` `make_toolbox_spec` | 元工具 schema（`command` / `name` / `args`）＋ help / call；`_DefaultSession` 惰性开默认会话 |
| `cogos/agent/toolbox.py` `_call` / `_run_composed` | 路由：能力 → 绑定 impl；`computer.command.run` ＝ open ＋ exec ＋ observe 组合 |
| `cogos/agent/tools.py:31` `ToolDef` | 契约层：`schema` / `fn` / `time_form` / `prompt`（catalog 绑定它的 `name`） |
| `cogos/agent/tools.py:1397` `ToolRegistry` | `names` / `schemas` / `prompt_lines` / `call` |
| `cogos/agent/config.py:132` `render_system_prompt` | 现含 `tool_lines`（S3 去掉） |
| `cogos/agent/consciousness.py:65` | `runtime.cu(material, tools=registry.schemas(names), callbacks=…)` |
| `cogos/agent/events.py` `render_event` | 事件渲染：`_EVENT_PREFIX` 映射模型面前缀；term 事件 `id`→`session` 短标签 |
| `cogos/agent/catalog.py` `session_label` | 会话对象索引（`t<id>`），run 返回与事件共用 |
| `cogos/agent/app.py` `_machine_env` | 总览机器环境（host/os/shell/home/cwd） |
| `cogos/cog_runtime/runtime.py:107` `tooling` 分支 | `tool_calls` ↔ `role:tool` 循环——**抹痕（后续）的落点** |

## 不变量（改动若碰这些必须回看 walkthrough / toolbox-design）

1. **tool-schema 恒定**：对外只有 `toolbox` 一个 schema → 命中前缀缓存。
2. **结果 / 异步结果 / 事件各自独立消息**（本轮`call` 结果走厂商 `role:tool`；抹痕后续）。
3. **常驻总览**在 `system` 之后；`help` 用**英文路径标识**寻址。
4. **对象索引**＝世界对象（会话 / 图 / 文件 / job）的短标签，非收件箱。

## 阶段 I 决策 / 偏差（待 YZ 知悉）

1. **catalog 含 `open` / `list` / `send`**：§9 表把三者记为机制；但 walkthrough §2 步 2 目标列出，A1（`send`）/ A2（`open`/`list` 倾向保留）已定 → 纳入模型面。多会话标签实现（A2 第二步）未做，`_DefaultSession` 单会话惰性复用。
2. **`run` 内建两处有界等待**（readiness ＋ settle，共约 ≤6s 上限）：非模型参数（`wait` 仍推后）。理由：pty 首条命令会撞 shell 启动（tty 先回显命令行、shell 尚未执行），不加会丢掉输出 → 判据 3 跑不通。`_wait_ready` 等 shell 起来；`_observe_settled` 等输出变化后稳定。**若视为"新增机制格"，回讨论。**
3. **`answer_auth` 仅声明**：绑定 `terminal_write_key`，但模型面无 `key`（机制选槽）尚未接；调用会因缺参报错，本轮不测。
4. **S4 会话短标签（`t<id>`）只做单会话**：`run` 返回与 term 事件共用；多会话标签仍属 A2 第二步。
5. **S4 事件前缀**：`term.*→computer.command`、`timer.*→computer.reminder`、`web.*→computer.web`、`phone.*→communication.file`、`transfer.done→computer`。`[machine …]` 同意/被抢/收回未实现。

## 阶段 II / III 状态（2026-09-28）

- **阶段 II 真实探针过**：真实 deepseek 模型只挂总览 ＋ 单 `toolbox`，自行 `help` 空→三组→各面→能力，再 `call run/web` 等；判据 1、2 成立。
- **阶段 III 主路径 e2e 过（真实模型）**：`Agent` 装配（总览 ＋ 单 `toolbox`，schema 只 `toolbox`）→ fake telecom 投递消息 → 模型 `help` 发现 → `call run cat hello.txt` → 拿 `MAINPATH-OK` → 经通信回消息。
- **残留**：真实**飞书身份 / 公开入口**那一版验收未做（需 YZ 的活账号，涉及外部消息外溢）→ 主路径已用真实模型 ＋ fake transport 覆盖判据 3 的机制；飞书版待 YZ。

## 更新纪律

- 每片结束：更新上表**状态** ＋ 新增**锚**；接口 / 不变量变了才改写对应行。
- 行锚写 `文件:行`，便于续接直接 `read`。
