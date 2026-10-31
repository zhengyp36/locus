# cogos 使用收口 CLI（程序/语义分离 + 声明式 agent）

> 状态：已落码并提交，`31267e3`（入口+create/template+birth）→ `abeee16`（服务清单）→ `48708e3`（run/stream/stop name 寻址），全量 1445 passed＋6 skipped，公开入口 `cogos agent run` 真跑 assemble→shutdown 生命周期 PASS。
> 来源：把「从零创建并运行一个自驱 agent」收口成一套 CLI，主线＝程序/语义分离。

一句话：`cogos up` 起前置、`cogos agent create <name> -c agent.yaml --birth-file birth.yaml` 建实例、`cogos agent run/stream/stop <name>` 按名跑/看/停——出生上下文与 agent 属性全部配置化，调语义不改代码。

## 动机（why）

自驱 agent 已落到「骨架 + 目录 + 调试 + i18n」，但「从零建一个 agent 并跑起来」还是散的操作（起 lm-service、起 feishu、写 profile、写出生上下文、起 run……）。目标＝把这套操作收口成一条 CLI，且把**程序架子**（代码）与**模型面向文本**（texts 资源库）与**实例内容**（agent 目录文件）分开——调语义只改目录文件/texts，改代码＝调架子（决策主线）。

## 命令面

```
cogos up | down | status
cogos agent template [-o dir]
cogos agent create <name> [-c agent.yaml] [--birth-file birth.yaml] [--force]
cogos agent run <name>
cogos agent stream <name> [-f]
cogos agent stop <name>
```

- **顶层 `cogos` 编排入口**（决策 10）：现有 5 个 console script（`cogos-debug`/`cogos-feishu`/`cogos-phone`/`cogos-lm-service`/`img-cli`）保留作细粒度面。`stream`/`stop` 是转发到 `cogos-debug`（stream/session 的 debug 全套 events/cursor/pause/resume/`--json`/`--expand-schema` 保留不动）。
- **name 寻址**（决策 11）：`<name>` 是位置参数，`resolve_agent_dir` → `$COGOS_HOME/agent/<name>/`，复用 `validate_name` 防穿越（拒 `/`、`\\`、`..`）。换根用已有 `COGOS_HOME` 环境变量，**不加 `--agent-dir`**（避免 name 寻址与 path 寻址两套并存）。
- **实例名 / persona 名分离**（决策 5）：实例名＝寻址键（位置参数）；persona 名（人设名）在 `agent.yaml` 的 `profile.name`。

## 数据面

```
$COGOS_HOME/agent/<name>/    # 默认 ~/.cogos/agent/<name>/
├── agent.json      # dirs + computers + default_computer + lang + phone（JSON，程序读写）
├── profile.json    # persona：name/phone_number/contacts/pin（JSON）
├── birth.yaml      # 出生上下文（YAML，声明=运行，直接拷）
├── agent.yaml      # 声明归档（只读快照，chmod 0o444）
└── stream/ memory/ events/ work/ phone/ secrets/ machine/
```

- **声明文件 `agent.yaml`**（决策 4/14）：结构化声明（`lang`/`phone`/`profile`/`machines`）→ create 展开成 `agent.json`＋`profile.json`；`machines` 映射 `computers`（name+root，root 相对 agent 目录解析）。**归档**＝创建快照、只读、可追溯＋支撑复用；**不随运行期同步**（防与 JSON 漂移，运行期只改 JSON）。全解析先于任何文件系统变更（非法声明不落半截目录，`--force` 只有新声明合法才毁旧 agent）。缺省用 `default_agent_yaml(name)` 渲染默认声明。
- **birth.yaml 声明=运行**（决策 1/2）：独立 YAML、直接拷（零转换）；结构复用 `Message.content`（`content: str | list[{type,text}]`、type 不设白名单、`role ∈ {system,user}`）；`--birth-file` 直接拷、缺省用 texts 三段渲染默认模板（system＝persona system prompt＋capability_note、user＝birth_task）。非法 role/结构 fail-fast 报文件路径（`BirthError` 带路径），不回退默认。
- **占位符白名单**（决策 3）：`{name}`/`{phone_number}`/`{contacts}`，递归到文本叶子；`{contacts}` 多行展开（每联系人一行 `- name (number)`、后续行带占位符前导缩进、跨行对齐）。
- **phone 显式字段**（决策 6）：`agent.yaml.phone` 显式声明（默认 false，零配置离线可跑），身份与运行模式正交；不从 `phone_number` 推导（推导把两者耦合死）。
- **lang 语义**（决策 8）：lang＝模型面向文本默认语言（非对话语言）；对话语言由通信层消息内容动态决定、模型自己应对。
- **复用旧 agent**（决策 13）：砍 `--from DIR`，用归档声明文件（`-c old/agent.yaml --birth-file old/birth.yaml`）重建，不做目录拷贝（避免「拷不拷运行时状态」歧义）。

## 服务清单（决策 12）

`cogos up/down/status` 遍历 `SERVICES: list[Service]`，每项 = 启动 + 就绪判据 + running 判据 + 停止：

| 服务 | 启动 | 就绪判据 | running |
|---|---|---|---|
| lm-service | `python -m cogos.lm_service.cli server`（编排层后台拉起） | 端口 11434 可连 **且** `state.yaml` 有 active key | 端口可连 |
| feishu | 复用 `cogos.feishu.service.Service`（systemd/manual） | `daemon_running()` | 同左 |

- **编排层、服务各自适配**：lm-service 编排层轻量 PID 自管（写 `server.pid`＋SIGTERM＋优雅停），feishu 复用现有 `Service`；不强制全 systemd/全 PID。`up` 幂等（已起不重起）＋就绪探测（默认 30s 超时），`down` 优雅停。未来新增前置＝加一条清单项，零编排代码改动。

## run 属性派生（决策 7）

`cogos agent run <name>` 不携带属性参数：`with_phone`/`lang`/`store_dir` 全在 create 固定进 `agent.json`（`AgentConfig` 补 `phone`/`lang` 字段），run 时 `load_agent_config(agent_dir)` 派生（`with_phone=config.phone`、`lang=config.lang`、`store_dir=config.stream_dir`）。细粒度 `python -m cogos.agent.run` 仍保留 `--no-phone`/`--lang`/`--store-dir`（作细粒度面）。

## 落码要点

- `cogos/cli.py`：顶层 parser + `resolve_agent_dir`（name 寻址，复用 `validate_name`）；stream/stop 转发 `debug.main([...])`。
- `cogos/services.py`：`Service` dataclass + `SERVICES` 清单 + `up/down/status`（`_lm_start/_lm_ready/_lm_running/_lm_stop` PID 自管）。
- `cogos/agent/create.py`：`validate_name`/`load_agent_yaml`/`expand_agent_config`/`expand_profile`/`create_agent`/`template_outputs`。
- `cogos/agent/birth.py`：`load_birth`（`BirthError` 带路径）/`interpolate_birth`/`interpolate_text`（contacts 缩进对齐）/`render_default_birth`/`dump_birth`（`|` 块标量）。
- `cogos/agent/config.py`：`AgentConfig` 补 `lang`/`phone` 字段，`load_agent_config` 读之。
- `cogos/agent/run.py`：抽 `run_agent` 供 CLI 复用（`main` 细粒度保留参数）。

## 被否 / 未采用

- **birth 用 key+value 放 texts** → 否：出生是实例上下文，不是通用文案。
- **birth 内嵌声明文件** → 否：性质不同＋YAML 缩进过深＋非「声明=运行」。
- **birth 转 JSON 统一目录** → 否：引入一处转换。
- **birth 用 jsonl 照搬意识流持久化** → 否：jsonl 的 state 控制行是运行时语义，出生是静态声明。
- **run 带 `--no-phone`/`--lang`/`--store-dir`** → 否：属性在 create 固定、run 不该再决定「怎么跑」。
- **phone 从 `phone_number` 推导** → 否：身份与运行模式正交，推导耦合死。
- **无 version/kind 元数据** → 否（YAGNI 无消费方；将来结构演进再引入，且只对程序生成模板有意义）。
- **`--from DIR` 目录拷贝复用旧 agent** → 否：归档声明文件重建即可，避免「拷不拷运行时状态」歧义。
- **`--agent-dir` path 寻址** → 否：与 name 寻址两套并存，换根用 `COGOS_HOME`。
- **前置进程全 systemd / 全 PID 统一** → 否：各服务已有一半现成适配，统一=重写。

## 遗留

- `up` 拆最小版 `up/status/down`，不做自动重启守护（长驻进程生命周期：拉起/探活/优雅停/日志已覆盖）。
- `resolve_agent_dir` 防穿越靠 `validate_name`（拒 `/`、`..`），`stream/stop` 转发给 debug 的 `--agent-dir` 是绝对路径（name 已校验，安全）。
- 三段落码无 handoff 尾巴；使用收口 CLI 待 YZ 核验（结构说明 + 关键文件 + 验收结果）。
