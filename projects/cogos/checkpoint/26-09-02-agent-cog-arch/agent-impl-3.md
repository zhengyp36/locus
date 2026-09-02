# agent 工具层扩展（第一期）—— 读写文件 + 执行命令

> 状态：待实施（方案已定，新会话照本文件做）。
> 目标：给 agent 补外设工具，让它在 `work_dir` 内读写文件、执行命令，能当编程助手用。
> 设计主文档：`agent-prototype-design.md`。前一期：`agent-impl-2.md`（身份认知 + 真实 LLM 回复）。代码认知：`codebase.md`。

## 目标与效果

- **离线（fake）**：注入一条消息 → LLM 可调用 `read_file` / `write_file` / `execute`，工具正确读写/执行并回传结构化结果。
- **真实**：与 agent 聊天时，它能读工程文件、写文件、跑命令（如 `ls`、`pytest`），结果作为 tool 返回给 LLM。

## 明确边界（不做）

- **不做上网**（search/fetch，后置；方案见 `docs/webtool-design.md`，key 已在 `~/.secrets/brave.key` / `jina.key`）。
- **不做 edit 工具**（精确替换编辑），`read_file` + `write_file` 够起步，需要再加。
- **不做记忆工具**（单独设计，后续从编程助手对话里观察出"记什么"再定）。
- **不做多目录 `work_dirs`**（先单 `work_dir`）。
- 不做场、元层时钟、群聊、通讯录转名字、主动发消息。
- 不碰 cog_runtime。

## 配置结构

`agent.json` 新增可选字段 `work_dir`，默认 `"work"`（相对 agent_dir）：

```json
{
  "memory_dir": "memory",
  "phone_dir": "phone",
  "work_dir": "work"
}
```

`work_dir` = agent 可操作目录：读写文件的根 + 执行命令的 cwd。独立于 memory/phone，避免污染 profile.md 和 phone 数据。

## 文件改动

```
cogos/agent/config.py      # 改：AgentConfig 加 work_dir: Path；load_agent_config 读 work_dir（默认 "work"，相对 agent_dir）；render_system_prompt 补工具清单
cogos/agent/tools.py       # 改：加 make_read_file_spec / make_write_file_spec / make_execute_spec 三个工厂（含路径边界 + 截断 + 超时）
cogos/agent/app.py         # 改：Agent 组装注册 4 个工具、传 work_dir、创建 work_dir 目录；_DEMO_AGENT_JSON 补 work_dir
cogos/agent/consciousness.py # 改：toolset_names 默认改为全部四个工具名
```

依赖单向保持：`tools` 的 spec 工厂只依赖传入的 `work_dir: Path`，不 import 其它 agent 层。

## 接口契约

### config.py

```python
@dataclass
class AgentConfig:
    memory_dir: Path
    phone_dir: Path
    work_dir: Path        # 新增

# load_agent_config: 读 agent.json，work_dir 字段默认 "work"，相对路径基于 agent_dir
#   work_dir = Path(data.get("work_dir", "work"))
#   if not work_dir.is_absolute(): work_dir = agent_dir / work_dir
#   （与 memory_dir/phone_dir 同样的解析方式）
```

### tools.py（三个新工厂，签名收 work_dir: Path）

```python
import asyncio
from pathlib import Path

MAX_CMD_OUTPUT = 4000      # stdout/stderr 各自截断字符数
MAX_READ_SIZE = 8000       # read_file 截断字符数
EXECUTE_TIMEOUT = 30.0     # 秒

def make_read_file_spec(work_dir: Path) -> ToolSpec
def make_write_file_spec(work_dir: Path) -> ToolSpec
def make_execute_spec(work_dir: Path) -> ToolSpec
```

**统一结果结构**（沿用 `send_msg` 的 `{"ok": bool, ...}`，`ToolRegistry.call` 已做异常兜底）：

- `read_file(path)` 成功：`{"ok": True, "path": "src/foo.py", "content": "...", "size": 1234, "truncated": false}`
- `read_file` 失败：`{"ok": False, "reason": "..."}`（路径逃逸 / 不存在 / 是目录 / 非 UTF-8 文本）
- `write_file(path, content)` 成功：`{"ok": True, "path": "...", "bytes": 456}`
- `write_file` 失败：`{"ok": False, "reason": "..."}`
- `execute(command)` 成功执行：`{"ok": True, "exit_code": 0, "stdout": "...", "stderr": "...", "duration_ms": 120}`
- `execute` 超时：`{"ok": False, "reason": "timeout after 30s", "stdout": "...", "stderr": "..."}`

### schema（给 LLM 看，description 用中文，与 send_msg 一致）

```python
# read_file
{"name": "read_file", "description": "读取工作目录内的一个文本文件",
 "parameters": {"type": "object",
   "properties": {"path": {"type": "string", "description": "工作目录内的相对路径"}},
   "required": ["path"]}}

# write_file
{"name": "write_file", "description": "写入（覆盖）工作目录内的一个文本文件，父目录不存在时自动创建",
 "parameters": {"type": "object",
   "properties": {"path": {"type": "string", "description": "工作目录内的相对路径"},
                  "content": {"type": "string", "description": "要写入的完整文件内容"}},
   "required": ["path", "content"]}}

# execute
{"name": "execute", "description": "在工作目录内执行一条 shell 命令，返回 stdout/stderr/退出码",
 "parameters": {"type": "object",
   "properties": {"command": {"type": "string", "description": "要执行的 shell 命令"}},
   "required": ["command"]}}
```

## 关键实现细节（坑，务必照做）

1. **路径边界（唯一安全机制）**：读写只接受相对路径。实现一个内部 `_resolve(work_dir, rel)`：
   ```python
   def _resolve(work_dir: Path, rel: str) -> Path:
       p = (work_dir / rel).resolve()
       if not p.is_relative_to(work_dir.resolve()):
           raise ValueError("path outside work_dir")
       return p
   ```
   绝对路径、`..` 逃逸都判 `is_relative_to` 拒绝（Python 3.11 支持 `Path.is_relative_to`）。`ValueError` 会被 `ToolRegistry.call` 捕获转 `{"ok": False, "reason": ...}`，但更建议在 fn 内显式 try/except 返回 `{"ok": False, "reason": str(e)}`，保证不抛断。

2. **read_file 二进制检测**：`p.read_bytes()` 后 `decode("utf-8")`，`UnicodeDecodeError` → `{"ok": False, "reason": "not utf-8 text"}`；`p.is_dir()` → `{"ok": False, "reason": "is a directory"}`。成功再按 `MAX_READ_SIZE` 截断：`content[:MAX_READ_SIZE]`，`truncated = len(text) > MAX_READ_SIZE`。

3. **write_file 自动建父目录 + 覆盖写**：`p.parent.mkdir(parents=True, exist_ok=True)`，`p.write_text(content, encoding="utf-8")`，返回 `bytes = len(content.encode("utf-8"))`。

4. **execute 用 shell + 超时 + kill**：
   ```python
   proc = await asyncio.create_subprocess_shell(
       command, cwd=str(work_dir),
       stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
   try:
       out, err = await asyncio.wait_for(proc.communicate(), timeout=EXECUTE_TIMEOUT)
   except asyncio.TimeoutError:
       proc.kill()
       await proc.wait()
       return {"ok": False, "reason": f"timeout after {EXECUTE_TIMEOUT}s", "stdout": "", "stderr": ""}
   ```
   超时时 stdout/stderr 已在 communicate 里拿不到（wait_for 抛异常即丢），可简化为空串；要拿部分输出需额外处理，本期不必。

5. **exit_code 语义**：命令返回非零仍 `{"ok": True, "exit_code": n, "stderr": ...}`，`ok` 只表示"工具执行成功（没超时/没异常）"，让 LLM 自己看 exit_code/stderr 判断命令成败。

6. **输出截断**：stdout/stderr 各自 `s[:MAX_CMD_OUTPUT]` 截断（`decode("utf-8", errors="replace")` 防非 UTF-8 输出炸掉）；`duration_ms = int((t1 - t0) * 1000)`，用 `time.monotonic()`。

7. **app.py 组装**：`ToolRegistry` 注册 4 个工具；`Agent.__init__` 里 `config.work_dir.mkdir(parents=True, exist_ok=True)`（在 `load_agent_config` 之后、组装工具之前）。`_DEMO_AGENT_JSON` 补 `"work_dir": "work"`（fake 临时目录下自动建）。

8. **consciousness 默认工具集**：`toolset_names` 默认改为 `["send_msg", "read_file", "write_file", "execute"]`（构造时仍可注入覆盖，保留口子）。

9. **render_system_prompt 补工具清单**：现有末尾那句"收到消息后，请用 send_msg 工具回复对方一句话"改为列出可用工具，例如：
   ```
   你可用以下工具：
   - send_msg：给联系人或号码发消息
   - read_file：读 work_dir 内文件
   - write_file：写 work_dir 内文件
   - execute：在 work_dir 内执行 shell 命令
   收到消息后，先判断该做什么，用对应工具完成，需要回复时用 send_msg。
   ```

## 测试

照 `tests/agent/` 现有范式（`FakeLmClient` + `make_response`，见 `tests/agent/conftest.py`），新增：

1. `test_config.py` 补：`work_dir` 默认值（`<agent_dir>/work`）、相对解析、绝对路径保留。
2. `test_tools.py` 补：
   - `read_file`：正常读 + `size`/`truncated`；超长截断（写 >8000 字符文件断言 truncated=true）；路径逃逸（`../x`、绝对路径）→ `ok:false`；不存在 / 目录 → `ok:false`。
   - `write_file`：写 + `bytes`；父目录不存在自动建；路径逃逸 → `ok:false`。
   - `execute`：`echo hello` → stdout 含 hello、exit_code 0；`exit 3` → `ok:true` 且 exit_code 3；`sleep 60` → 超时 `ok:false`（测试里把 `EXECUTE_TIMEOUT` monkeypatch 成 0.2s 或注入短超时，避免真等 30s）。
   - 长输出截断：`python -c "print('x'*10000)"` → stdout 长度 == 4000。
3. 全量回归 `python3.11 -m pytest tests/ -q` 无退化（基线 798 passed）。

测试里 `make_execute_spec` 若把超时常量写死，需支持 monkeypatch 或让超时成为可注入参数（建议工厂签名 `make_execute_spec(work_dir, timeout=EXECUTE_TIMEOUT)`，测试传 `timeout=0.2`）。

## 完成标准

`Agent(agent_dir)`（fake）deliver 一条消息 → LLM 能收到含 4 个工具 schema 的 `chat(tools=...)` → 调 `read_file`/`write_file`/`execute` 得到结构化结果。pytest 通过 + 全量无回归。

## 风险评估（结论：可进入开发）

| 风险 | 级别 | 对策 |
|---|---|---|
| 路径逃逸导致误读写 work_dir 外文件 | 中 | `_resolve` + `is_relative_to` 强制校验 |
| execute 卡死 / 输出过大撑爆上下文 | 中 | 30s 超时 kill + 输出各截断 4000 字符 |
| 非 UTF-8 输出 / 二进制文件 | 低 | `errors="replace"` + 二进制检测 |
| 工具集默认改动影响既有测试 | 低 | 集中改 `app.py` + `consciousness` 默认值，测试随契约更新 |

无阻塞性风险；坑均已列明，可直接进入开发。
