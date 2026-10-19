# Tool Design Draft — body / memory (2026-10-17)

> 面向模型的工具全英文（名称 / 参数 / 描述 / help）。
> 交流语言由场景决定，与工具语言无关（内容层 vs 机制层）。
> 本文件为 markdown 草稿，编码时再转 function-calling JSON schema。

## 设计结论（承 10-17 讨论）

- 工具只写 tool schema，不在 system prompt 重复。
- 能力总览（what）写进 body 的 schema description；用法（how）走 `body help` ＋ 最近用法缓存（条数上限，LRU 淘汰）。
- 能力总览＝3 组 ＋ 面级列举；叶子级用法走 help drill-down。
- 分组：communication / vision / computer（computer 下面 terminal / file / screen / web；reminder 待定，暂不列入）。
- 意识层统一"组 → 面"两级；机制层 face 中间层与叶子藏进 help。
- 模型面 path 统一用 terminal（原 catalog `computer.command` 改名），与机制层 impl `terminal_*` 对齐；编码时改 path，不设映射层。

## body

### tool schema（markdown 呈现）

```
name: body

description: >
  Act on the world and sense it. Capabilities:
  communication (send messages, send files, receive files);
  vision (look at images, mark, read coordinates);
  computer — terminal (run commands, observe), file (read, write, edit),
  screen (look, act), web (search, fetch).
  Use `help` to get the exact usage of a capability, then `call` to execute it.

parameters:
  command: string, one of ["help", "call"]
           help = discover usage; call = execute
  name:    string, capability path
           help accepts a group/face prefix; call needs the full leaf path
  args:    object, arguments for the capability
           call only; keys and meanings come from help
```

### 调用示例

```
1. body(help)                          → 三组 + 面级列举（即 description 里的能力总览）
2. body(help, "computer")              → terminal / file / screen / web
3. body(help, "computer.terminal")     → run / observe / interrupt / send 的参数与用法
4. body(call, "communication.message.send", {to: ..., content: ...})
```

### 最近用法缓存（机制层行为，不写进 schema）

- 最近用过的工具用法以 user 消息注入上下文，条数上限 + LRU 淘汰。
- 模型靠它跳过重复 help；缓存是机制自动做的，模型无需知道其存在。
- 与"工具结果走 user role、标注为工具结果"同一纪律，注入时加轻标注区分。

## 模型面命令清单（23 条，body 能力背后的真实路径）

### communication
- communication.message.send
- communication.file.send
- communication.file.receive
- communication.file.cancel

### vision
- vision.see
- vision.mark
- vision.coord

### computer — terminal
- computer.terminal.run
- computer.terminal.observe
- computer.terminal.interrupt
- computer.terminal.send

### computer — file
- computer.file.read
- computer.file.write
- computer.file.edit

### computer — screen
- computer.screen.look
- computer.screen.act
- computer.screen.save

### computer — web
- computer.web.search
- computer.web.fetch
- computer.web.cancel

### computer — reminder（待定，暂不列入 body）
- computer.reminder.set
- computer.reminder.cancel
- computer.reminder.list

注：computer.terminal 由 catalog 现名 computer.command 改来——模型面 path 统一用 terminal，与机制层 impl（terminal_exec / terminal_observe / terminal_cancel / terminal_write）对齐，不再有"意识层面名 vs 机制层路径"两层。编码时同步改 help 渲染、_NEEDS_SESSION、测试断言。

## memory（待写）

- 对内整理：fold / unfold 两个原子操作，schema 直接给用法（当前简单）。
- 与 body 并列，同为意识层唯一两个工具。
- 本次暂不展开。
