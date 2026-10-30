# 自驱 agent 可视化调试工具（看 + 控制）

> 状态：已落码（cogos commit `bb7a489` debug tooling ＋ `c97a468` console script `cogos-debug`），全量 1363 passed。界面（TUI）仍暂缓。
> 来源：调试自驱 agent 的**推理过程**（非程序 bug）需要两个效果——「看」（假设我是模型，看到了什么）和「控制」（运行中暂停/恢复）。讨论共识在 `scratch/2026-10-30-cogos-debug-visualization.md`，收口后删除。

## 核心：流 = 模型视角（没有第二落点）

- context 是 append 的消息流，unit 调 LLM 时 `material=self._context` 原样传 → **意识流 jsonl 本身就是「模型看到了什么」的完整记录**，天然聊天历史。
- 调试 = 读流 + 切上下文标记 + 控制信号，不另建数据面。
- 已有什么（不用新写）：流落盘（StreamStore，行含 role/content/tool_calls/tool_call_id/reasoning/round/ts）、system prompt 在流里（birth 第一行 `role=system`）、Switch 切上下文标记（`CONTINUING`/`CONTINUED` builtin state + next/prev 交叉链接）、因果挂点（`CogStream.note(state, **extra)`）、事件落盘（EventStore）。

## 唯一新增：schema 落盘 + hash 版本引用

- schema 是代码静态常量（body/memory `_SCHEMA` 写死），随代码演进变。启动时算内容 hash，与 `<agent_dir>/schemas/` 已落最新版比：一样复用旧 ID，不一样落 `<id>.json` 并在流写 `note("schema_ref", id=...)`。
- **ID = sha256(canonical JSON) 前 8 位**：一个值同时回答「变没变」（新 ID=变了）和「哪个版本」（稳定标识）；相同内容复用同一文件、只写一次。
- 好处：调试工具读文件展开 schema，与代码解耦，跨代码版本回看旧流也对得上。

## 流里记什么 / 因果 = 介入点挂 note

- 消息 + 控制标记 + schema 引用（`note("schema_ref", id=...)`）。
- 事件收到不插，介入点判断处理时才插（现状正是 `Relay(events)` 进流）；State 注入同事件，作为消息进流。
- 「有关联才插入」= 插入时机即建立关系时机，不需要跨源对齐。事件文件与流内 user 消息**先不做显式 id 关联**，两个视角按时间近似对齐即可。

## 接口层 + CLI + cursor + 控制

- `stream_reader.py`：`StreamReader` 把 stream 目录按 next/prev 串成跨 Switch 的虚拟连续序列（`entries()`/`tail(n)`/`since(ts)`/`follow`），加 `EventReader`（事件视角）。
- `debug.py`：`python -m cogos.debug <子命令> --agent-dir`（默认 `~/.cogos/agent/tangyu`）；子命令 `stream`/`events`/`cursor set|next|prev|reset`/`pause`/`resume`/`shutdown`；`--json` 出结构化。
- **cursor（阅读进度，过渡方案）**：存 `/tmp/cogos-debug-cursor-<name>`，内容 `{"ts":...}`（**ts 非行号**：行号跨 Switch/归档会漂）。`COGOS_DEBUG_CURSOR` 环境变量 + `cursor next/prev` 翻页；TUI 做前过渡，TUI 进程内记位置可省。
- **控制**：`CogStream.pause()/resume()`（`asyncio.Event`，挂点 = `_handle_intervene` 里 checkpoint 之后、`_decide` 之前 `await pause_event.wait()`）；语义＝当前 LLM 调用已完成、结果已落盘，await 期间 idle loop 卡住不推进，resume 走正常决策。`run.py` 起 `<agent_dir>/control.sock`（收 `{"cmd": pause|resume|shutdown}`），`AssembledAgent` 透传。

## 范围边界（暂不做）

- 多流 / 后台流 / 元层 LLM 流：等遇到再实现，现在拍表达是空想。
- 界面（TUI）：薄壳后做，交互翻页/游标归 TUI。

## 被否方案（why）

- **trace span 六部件观测点 / 多源对齐框架**：过度设计，因果靠「介入点挂 note + 有关联才插入」已自足。
- **单独 io.jsonl + step id 关联**：伪问题，「模型看到 = context = 已落盘流」。
- **实时真推送**：假实时（周期查时间戳）够用。
- **`--file <名>` 文件定位**：文件名对人无意义，改 `--since` 时间定位。
- **「schema 静态、流里不记、import 常量表」**：诉求改为「落盘 + 版本回溯 + 与代码解耦」后不成立，改「落盘 + hash 版本引用」。
- **行号游标**：行号跨 Switch/归档漂移，改 ts。

## 实现偏离（相对讨论稿）

- 无实质偏离。仅 CLI `--agent-dir` 用 `argparse.SUPPRESS` 支持「选项在子命令后」；接口层方法名 `entries()` 代 `iter`（避免遮蔽内置 `iter`）。
