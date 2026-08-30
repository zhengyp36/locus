# status

新会话恢复：读 locus 记忆（active → projects/cogos/current.md）+ `handoff.md`（段 2 启动提示词，自包含）。

## 当前：cog-runtime 实施 ✅ task-4 完成 + lm-service 续轮转换 ✅ 真实闭环全绿

- task-4 完成：类型 + CogUnit + CogRuntime/_advance 状态机 + 支路 A/B 闭环 + 并发 + 父子通知 + shutdown。
  - 代码落 `cogos/cogos/cog_runtime/`（`types.py`/`unit.py`/`runtime.py`），测试 `cogos/tests/cog_runtime/`（32 passed）。
  - 详见 `checkpoint-3.md`（段 1）+ `checkpoint-4.md`（段 2）。
- lm-service 续轮消息归一→厂商转换（真实测试暴露的实现遗漏，工位 A 直改）：`assemble_tool_messages` + provider 接入，测试 `test_tool_messages.py`（12 用例）。
  - 全量 pytest 777 passed 无回归（733 → 777，净增 44）。
  - 真实 deepseek 三路全绿：A 文本 / B 工具续轮 / E 401→auth。
  - 详见 `checkpoint-5.md`。
- **遗留**：细节① 告知值默认注入（设计 2.5）——YZ 拍板先遗留，属后续语义层 prompt 设计；注入点简单（构造参数 + cu() 处插 system 消息），数值待调。

## 本工位文件

- `design-cog-runtime-min.md` — cog-runtime 最小版设计（内部实现已固化，含 3.5/3.6）
- `design-cog-runtime.md` — 早期雏形（zio 映射 / 四约束等，改写时参考）
- `checkpoint-1.md` — 审核记录（意见 1~7 已收敛）
- `checkpoint-2.md` — 内部实现设计 4 问题讨论记录（已收敛，勿归档）
- `checkpoint-3.md` — 段 1（轮 1-3）记录
- `checkpoint-4.md` — 段 2（轮 4-6）记录
- `checkpoint-5.md` — lm-service 续轮消息归一→厂商转换
- `llm-capabilities.md` — LLM 调用形态静态知识

## 已归档 / 移交

- lm-service 设计/过程 → 工位 B（`design-lm-service-min.md` + task-1 + archive）
- lm-service 遗留三项 → 工位 B task-3（已完成）
- 通信层 / agent-study 复习 / 智能系统设计 → locus `projects/cogos/index.md` + `CHANGELOG.md`
