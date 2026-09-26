# plan｜agent 工具实现（A 层分批）· 2026-09-18

> **状态**：设计已收口、spec v1 已通过；**待新会话审核后开工**。一批一会话，逐批交接。
> **依据**：`cogos/docs/design-agent-tools.md`（工具权威分册）、`cogos/docs/design-selfdrive-agent.md`（总纲）、`spec-tools-a.md` v1（A 接口形状）、`checkpoint-1.md` §19／§20（过程与裁决）。
> **交付**：4 批；每批完成后写下一批 handoff。

## 0. 铁律

- **一批一会话**；每会话开工前**重审** spec／权威分册，无问题才动手。
- 每步走**三问**（落点／接口／差别）；**发现设计问题回 `checkpoint-1.md` 记，不悄悄改设计**。
- **每落一个 A 对象即配最薄 B**（name→fn 接进现有 `ToolRegistry`，**沿用旧扁平工具名**）；C（分包/装配）后置。
- 旧代码**对象级一次性替换**，不长期两套并存。
- 不替 agent 决定用法；工具只保证能力完整、可控、可观测。

## 1. 既定决策（开工即用，勿再议）

- `Clock`：**不读配置**；初值由装配层注入（`Clock(tz=...)`，`None`＝系统本地）；`set_timezone` 只改内存态；非法 tz 抛 `UnknownTimezone`。
- `DraftStore`：`write` 新建 `ext` 默认 `"md"`；`read` 二进制抛 `NotText`；`InvalidEdit` 拆 empty／not-found／not-unique 三个子类。
- **时间坐标＝epoch 秒（UTC）**；产事件者注入同一 `Clock`。
- `transfer` **发起时即定 `dest`**；`phone` ack v0＝本地 ack（不承诺送达）；`sync_reachable` 归机器属性；`observe` 单位＝行；`SignalSink.emit` 同步非阻塞；`cancel()` 幂等。
- **`execute` 不实现**（`term` 上线后已删，09-19）；**`search`/`fetch` 冻结**，不改动。
- A 落点 `cogos/agent/impl/`；测试 `tests/agent/`。

## 2. 批次

### 批次 1 — 本地三件（先做）
- **范围**：`Clock`、`DraftStore`、`TimerService`、`PhoneCapability`(本地 ack)。
- **文件**：`impl/clock.py`、`impl/draft.py`、`impl/timer.py`、`impl/phone.py`；`tests/agent/test_impl_*.py`。
- **最薄 B**：`time.now`／`set_timezone` 接进 registry，删 `config.py:100` 启动定格；`scratch_*` 换 `DraftStore`（加 `mark`/`unmark`、`list` 仅已标，去 history 归档）；`timer` 三件改绑 `Clock`/`Signal`。
- **验收**：`pytest` 绿；`_run_fake` 冒烟；取值型同步当轮返回。
- **预期回归**：`tests` 里 `scratch_*` 约 27 处引用。
- **产出**：`handoff-tools-02.md`。

### 批次 2 — term 核心（最难）
- **范围**：`ComputerManager`/`ComputerSession`（pty、`exec`/`write`/`observe`(VT)/`resize`/`cancel`/`close`/`list`、`term.done`、notify）。
- **语义（已定）**：会话＝持久 pty 顶层进程；`exec`＝写命令行；`write`＝原样送字节；**命令完成不由机制推断**；`term.done`＝shell 退出；**无 busy**；`cancel`＝`\x03` 幂等；`observe`＝VT 渲染屏（pyte，按行）。
- **开工前待定**：pty 库选型（`pty.openpty`+asyncio / `ptyprocess`）、winsize 初值、notify matcher 细节。
- **验收**：单测＋冒烟（发命令／看屏／发键／notify token）。
- **产出**：`handoff-tools-03.md`。

### 批次 2.5 — 远端 term + 凭证注入（09-19 插入）
- **范围**：远端 term（会话顶层＝`ssh -tt`，密码走 `write`）；`SecretStore`＋`SSH_ASKPASS` 自动登录（agent 不见密码）＋`write_secret`/`terminal_write_key` 受控出口。
- **产物**：`checkpoint-1.md` §23／§24；方案 `design-secrets.md`（草案）。
- **结果**：已实现并验证（`pytest tests/ -q` 1096 passed）；真机 `tangyu@localhost` 验证。

### 批次 3 — 会话衍生
- **范围**：`FsChannel`（本机）、`TransferEngine`。
- **依赖**：批次 2。
- **开工前待定**：fs 路径基准（会话 `cwd` vs 机器根）、`fs.read` 有界上限/超时、transfer 机器端定位。
- **验收**：`fs` read/write/edit；`transfer` 草稿↔机器根 copy（含二进制/大文件走 `put`）。
- **产出**：`handoff-tools-04.md`。

### 批次 4a — 工具层收尾（B 契约表 · 2026-09-19 定 · 本轮范围）
- **范围**：`ToolDef` 声明表（name／schema／time_form／prompt／fn）作**单一来源**；registry／白名单／system prompt 由它派生；保留扁平名。
- **不做**：`assemble`／分包／role／context／机器配置（归 4b）。
- **验收**：工具集单一来源（不再手工同步三份列表）；`pytest` 绿；`_run_fake` 冒烟。
- **结果**：见 `checkpoint-1.md` §28。

### 批次 4b — 装配（C · 缓，待单独讨论）
- **范围**：`assemble(role/context)`、分包（授权单位）、按需装配、`agent.json`「电脑」配置接线（§25.2）。
- **触发**：出现第二个消费者（机制面向工具，或需按机器/会话裁剪）后再议；不预先造抽象（design §18.1）。
- **产出**：收尾；`work/A/checkpoint/` 归位 `locus/projects/cogos/checkpoint/`。

## 3. 会话协议

**开工**：读本 plan ＋ 上一批 handoff ＋ 重审 `spec-tools-a.md`／`design-agent-tools.md`（先报告有无问题）。
**疑义** → 停下问 YZ，不带疑开工。
**收工** → 写 `handoff-tools-0(N+1).md`，字段见 §4；必要时更新 `checkpoint-1.md`。
**全部完成** → 归档归位。

## 4. handoff 必含字段

- 入口（本 plan、权威分册、spec、上一批 handoff、相关代码）
- 本批**已完成**／**未完成**
- **验证结果**（命令＋结论）
- **新发现**（设计问题→已回记 `checkpoint-1.md`；其余记此）
- **下一批**：范围、依赖、开工前待定项
- **待 YZ**
