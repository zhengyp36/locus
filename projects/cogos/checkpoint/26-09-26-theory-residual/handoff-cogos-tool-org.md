# handoff｜工具（实现）给新会话 · 2026-09-18

> **新会话任务**：讨论**工具的实现**（设计已收口，本轮进入落地：落点/接口/顺序/差距）。
> **性质**：设计阶段（只讲不推进）**已结束**；本轮谈实现。设计若有漏洞 → 回 `checkpoint-1.md` 记一笔，**不悄悄改设计**。
> **当前焦点**：按 §16.5 清单与 §16.2／§16.3 收敛形态，定**从哪一枪动手**（§四 三问：落点／接口／差别）。

## 入口

1. **`work/A/checkpoint/checkpoint-1.md`** ← **设计与决策主入口**。相关：**§13（目录/草稿）、§15（安全，多数已遗留）、§16（工具，核心）、§17（简化与草稿）、§18（分包与时间形态）**；§十四 是**代码现状事实层**。
2. `locus/active.md` → `projects/cogos/current.md`
3. 权威口径：`cogos/docs/design-selfdrive-agent.md`（**冲突以它为准**；checkpoint 是非权威讨论记录）。

## 已定设计（实现依据）

### 工具清单（§16.5 定稿）
- **agent 面向·工具**
  - `time.*`：`now`、`set_timezone` —— 同步（取值）
  - `draft.*`：`read`、`write`、`edit`、`mark`、`unmark`、`list`(仅已标) —— 同步（机制侧、保证快）；`write` 无 id→生成、带 id→覆盖；**无 `new`／`delete`／通用 `search`**
  - `timer`：`set`(→句柄)、`cancel`、`list` —— 同步返回；到点/错过走事件
  - `transfer`：`transfer(src,dst)` —— 异步；**只 copy、整文件**；端点 草稿↔机器根
  - `phone.*`：`send` —— 异步（ack；后果走事件）。**`receive` 是事件、非工具**
  - `term.*`：`open`、`exec`、`write`、`observe`、`cancel`、`close`、`list` —— 异步
  - `fs.*`：`read`、`write`、`edit` —— 同步有界；**以 `term` 会话句柄为目标**
- **事件（推，非工具）**：`phone.receive`、`timer.notify`（到点/错过）、`term` 退出/屏变通知、事件自带的**时刻**（机制注入）。
- **机制面向（同步、不可见）**：`load/retrieve`、`record_segment/promote`、`consolidate/replay`、`read_segment/write_segment`、`mech_scratch_*` —— **整体遗留，本轮不做**。

### 关键形态
- **包＝可一起授予/撤销的工具组**，**包名即命名空间前缀**；装配归机制、不向模型宣示（§18.1）。
- **时间形态判据＝取值型 vs 后果型**（**不按位置分**）：取值型（`now`/`set_timezone`/`draft.*`/`timer.set`/`fs.*`）同步；后果型（`term.*`/`transfer`/`phone.send`）异步。**事件只做短通知、不带长内容**（§18.2／§16.3）。
- **终端**（§16.2）：**pty 单形态、pipe 废弃**；`write` 送字节（含密码/控制字符）；**`observe`＝看屏**（VT 模拟器渲染＋滚动历史，不给 raw）；忠实输出走**重定向＋文件工具**；**显式 winsize**；非阻塞（poll/event）；远程 ssh 跑在 pty 里。notify（§16.8）：默认关、显式开，带内走 pty 流，保留 OSC 外壳＋随机 token，真相以 `observe` 为准。
- **文件／电脑**（§16.3）：`term` 与 `fs` **同 account/target**（fs 走同一 ssh 的 sftp）；**权限＝OS 账户权限**（无根沙箱、无 symlink 逃逸概念）；机器带**"可同步可达"属性** —— 装则有 `fs.*`（同步有界、普通文件、无 list/search/delete），不装（远端）**无 fs**、走 `term`＋`transfer`；**fs 从 term 衍生，`term.open` 的会话句柄即 fs 参数，不新增 `get_fs`**，会话关则 fs 失效；大文件/部分内容**在源处切片（终端）后 transfer**，`transfer` 不加 offset。
- **草稿**（§17.3）：`id` 平铺＋`id=0` 保留地址（始终可读、miss 自动建空、**覆写为空**即重置、无 delete）；`mark` 附 ≤256 字摘要、`list` 仅已标；**默认可删、标记禁删**（例：0# 单独配额 1MB／禁删 20 条 & 10MB／总量 30MB）；**淘汰＝最近访问列表·只在内存**；mark 注册＝独立 `marked_list.json`；文件名 `scratch_<id>.<ext>`（后缀原样）；超容＝手动写即失败、仅 `transfer` 可临时超（≤500MB）、写后查容量**超大优先**淘汰（刚 transfer 的豁免到下次写）。
- **目录归属**（§13.1）：**机制根／草稿根／机器根**（档案已删）；机器根用真实绝对路径，OS 权限定边界。
- **来源戳／信任**（§15.4.1）：**工具只提供"来源标注"**；来源＝具体标识、非分类；来源判断/信任不在工具层。

### 已遗留（不在本轮）
- **外发防护／秘密清单**（§15.2／§15.7.1）整体遗留；一致性：默认秘密**明文外发**，"草稿 mark 禁删"只是存放位置非防护。
- **机制面向工具**；**组装 cu**（单弧预算／可打断／安全点／未完成弧落账／会话跨重启）。
- 更外圈 §二／§八（权重通道／从哪步动手／通道落点／分类框架 v2）。

## 实现现状与差距（§十四 事实层）

| 事实 | 位置 |
|---|---|
| 群聊被过滤（只听 p2p） | `perception.py:17` |
| 事件进 cu 来源被抹平（统一 `source="system"`）——**来源判断的前置 bug** | `app.py:147` |
| 时间在 prompt 里**启动即定格**（不更新） | `config.py:100` |
| `send_msg` 无回执／无沉默（`{"ok": true}`） | `tools.py:125` |
| 视觉（`img_tool`／`image_ctx`）**有码、未接入** | — |
| 终端是**管道**实现（无 stdin、无 pty、每命令一进程） | `terminal.py:66` |
| 终端已是非阻塞范式（发起即返回，结果走事件） | `terminal.py`／`tools.py` |
| 已有超时：execute 30s／search 20s／fetch 60s／lm 120s | `tools.py:20`／`webtools.py:23` |
| 草稿空间已有（`ScratchStore`，机制三供给之一） | `tools.py:376` |

**设计↔现状主要缺口**：pty（现为 pipe）；`observe` 看屏（现无 VT 模拟器）；`fs`（现 `read_file/write_file/edit_file` 本地、无 sftp、无会话绑定）；`transfer`（无）；`draft.*` 的 `mark/unmark/list`（无）；`timer.cancel/list`（无）；"可同步可达"属性与按需装配（无）；来源标注（被抹平）。

## 纪律

- **动手纪律**（§四）：每步动手前三问——**落点**（哪一段／哪根箭／哪个字段）、**接口**（读谁写给谁）、**差别**（环上哪处从"不转/空转"变"转"）。
- **设计已收口**：实现中发现设计问题，先回 `checkpoint-1.md` 记，**不改设计悄悄落地**。
- **别替 agent 决定**：工具只保证**能力完整、可控、可观测**，不规定"它该怎么用"。
- `work/A/checkpoint/` 是临时工作区；**收尾要归位**到 `locus/projects/cogos/checkpoint/`。
- 注意：**主入口文件常被就地更新**；进入讨论前先重读当前版本。
- 设计收口后，`checkpoint-1.md` 汇总写回 `design-selfdrive-agent.md`（**待 YZ**）。
