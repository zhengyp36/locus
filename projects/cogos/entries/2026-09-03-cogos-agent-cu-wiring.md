# agent 接 cu 讨论（09-03，收敛、未实施）

> 起因：terminal+timer e2e（真实 deepseek）暴露 agent 层 oneshot 无续轮——LLM 收到「执行长命令」只调 `terminal_open` 就停，open 结果没回传，没机会调 `terminal_exec`。

## 现状（代码锚点）

- agent 收到 phone 消息**没起 cu**，直接 `Consciousness.on_message`（`consciousness.py:32`）里 `self._lm_client.chat`：一次 chat + 逐个 `await` 工具调用，结果只 `logger.info`（`:46`），不续轮。
- `cogos/agent/` 全仓**零引用** `CogRuntime`/`CogUnit`——cog-runtime 只被自己的测试用。两层是独立、未接通的子系统。
- `CogRuntime._advance`（`runtime.py:55`）已支持多轮工具闭环：`tooling` 态把结果组装 assistant+tool 消息 append material（`runtime.py:114-131`）→ 回 `running` 再 chat → 无 tool_calls 才 `_finish(CuResultOk)`（`runtime.py:97-100`）。

## 收敛方案（待实施，YZ 已认可方向）

```
Agent 持有 self._context（init 写入 system 身份）
单 consumer 串行：
  on_msg/事件 → self._context.append(user 消息)
  → cu = runtime.cu(material=self._context, callbacks={on_tool_call, on_done})
  → await cu.wait()   # 串行，一个 cu 结束才下一个
  → cu 结束，context 已含完整历史，agent 继续持有
```

关键结论：

- **共享 context 是 agent 的对象，不是 cu 的**。cu 设计理念用完就丢：`runtime.cu(material=...)` 只是存引用（`unit.py:12`），`_finish` 后 `pop unit`（`runtime.py:163`）只丢句柄，material 留 agent 手里。
- **串行 + `await cu.wait()`**：同一时刻只有一个 cu 写 context，不交织；runtime 同步 append 块天然保证配对。不需要锁、不需要「隔离拷贝 + 合并」（那会错误地让 cu 拥有 context）。
- **tier 显式 basic**：`select_model` 里 None 取 candidates[0]（依赖 config 顺序、脆弱），basic 精确匹配 + 降级标记。当前两者都选 flash，但 basic 语义更稳。
- **工具超限不补工具结果**：在 `on_tool_call` 里计数，超限调 `cu.interrupt("max_tool_rounds")`（`unit.py:39` 只设 interrupt_reason）→ `_advance` 回循环开头检查（`runtime.py:57-60`）→ `_finish(Interrupted)` 结束。因为不再 chat，deepseek 不会报「tool_calls 无结果」；且 append 在 interrupt 检查之后，失败轮消息不进 context（干净，无孤儿 tool_calls）。
  - 唯一会报错的情况：超限后**还想继续 chat** 让 LLM 自己停，那才必须补 tool 结果。

## 信息回 agent 的两条通道

| 内容 | 进 context 时机 | 机制 |
|---|---|---|
| user 消息 | 起 cu 前 | agent 手动 append |
| 每轮 assistant(tool_calls)+tool 结果 | cu 循环中 append 那一刻 | material 同一引用，实时 |
| 最终 assistant 回复（CuResultOk.content） | on_done 里 | **agent 手动补**（runtime 不 append） |
| 失败轮消息 | 不 append | 随 cu 丢弃 |
| 成功/失败/中断结果 | on_done(result) | agent 据此决策 |

`on_done(result, material)` 分派：`CuResultOk` 补最终 assistant 回复 + 需回复则 send_msg；`CuResultError` 补错误说明 / send_msg 告知 / 重试；`CuResultInterrupted` log。

## 已定/待定

- 已定：context 是 agent 对象、material 传引用、串行 + wait、超限 interrupt 不补结果、tier basic。
- 待定（新会话继续）：事件以什么角色 append（倾向 user）；上下文无限增长的压缩/截断；`on_tool_call` 抛异常会导致 cu 悬挂（`_advance` 无 try/except，需补）。
