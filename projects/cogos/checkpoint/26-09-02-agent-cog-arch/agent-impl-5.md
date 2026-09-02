# agent 工具层扩展（第三期）—— scratch 草稿纸

> 状态：已完成（841 passed，含 9 个新增测试）。
> 设计：对话中与 YZ 敲定（scratch 版本化写时复制 + 去版本号用 ms 时间戳归档）。
> 前一期：`agent-impl-3.md`（读写文件 + 执行命令）。代码认知：`codebase.md`。

## 目标与效果

- 给 agent 一个私有草稿纸区，承接关键思考过程不被摘要压丢。
- 逻辑 id 恒指最新：`active/<id>.md`；改写时旧版归档 `history/<id>.<ts_ms>.md`（不丢，仅供复现问题）。
- LLM 只见 id + content，机制层逻辑（计数器/归档/时间戳）全封在工具内。

## 明确边界（不做）

- 不做上下文日志落盘（复现的"另一半"留后）。
- 不做版本号（ms 时间戳区分历史版，撞名仅影响复现，可接受）。
- 不做脚注标记 `[^1]` 那层（属 cu 循环/脉络，后做）。
- 不做目录 ID 化（DirTable 稍后反哺，本期 scratch 独立于 work_dir 纯文件实现）。
- 不引锁：ScratchStore 写操作内部无 await，单事件循环内天然原子。

## 存储结构

```
<agent_dir>/scratch/
  scratch.json      # {"next_id": 3}
  active/1.md       # 恒指最新
  history/1.<ts_ms>.md   # 旧版归档
```

## 文件改动

```
cogos/agent/tools.py       # 改：ScratchStore + make_scratch_write/read/list_spec
cogos/agent/config.py      # 改：AgentConfig 加 scratch_dir；load_agent_config 读（默认 "scratch"）；system prompt 补清单
cogos/agent/app.py         # 改：组装 ScratchStore + 注册三工具；_DEMO_AGENT_JSON 补 scratch_dir
cogos/agent/consciousness.py # 改：toolset_names 加三工具
tests/agent/test_scratch.py  # 新：9 个测试
```

## 接口契约

- `scratch_write(content, id=None)`：无 id 新建返回 `{ok, id, created:true, bytes}`；有 id 改写返回 `{created:false}`。
- `scratch_read(id)`：`{ok, id, content, size, truncated}`。
- `scratch_list()`：`{ok, drafts:[{id, size, updated_ms}]}`。
- id 校验：纯数字字符串，否则 `{ok:false, reason:"invalid id"}`。
