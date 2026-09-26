# handoff｜工具实现 · 批次 1（新会话入口）· 2026-09-18

> **新会话任务**：**先审核，无问题才做批次 1**（本地三件）。一批一会话；做完批次 1 写 `handoff-tools-02.md`。

## 入口

1. **`work/A/checkpoint/plan-tools-impl.md`** ← **先读**：批次划分、铁律、既定决策、会话协议。
2. 权威：`cogos/docs/design-agent-tools.md`（工具分册）；总纲 `cogos/docs/design-selfdrive-agent.md`。
3. A 接口形状：`work/A/checkpoint/spec-tools-a.md` **v1**。
4. 过程与裁决：`work/A/checkpoint/checkpoint-1.md` **§19／§20**。
5. 代码现状：`cogos/agent/{tools,terminal,timer,config,app,consciousness}.py`；测试 `cogos/tests/`。

## 第一步（必做）：重审

- 审 `spec-tools-a.md` v1 与 `design-agent-tools.md` **是否自洽、有无遗漏/矛盾**，尤其批次 1 涉及的 `Clock`／`DraftStore`／`TimerService`／`PhoneCapability`。
- 审 spec §10 的剩余待审项，批次 1 范围内的先定掉。
- **有疑义 → 报告并停，问 YZ**（不悄悄改设计；设计问题回 `checkpoint-1.md`）。
- **无问题 → 开始批次 1。**

## 批次 1 交付（审核通过后）

- **范围**：`Clock`、`DraftStore`、`TimerService`、`PhoneCapability`(本地 ack)。
- **做法**：先落 `impl/` stub＋单测（`tests/agent/`），再实现；`pytest` 绿。
- **最薄 B**：`time.now`／`set_timezone` 接进 `ToolRegistry`，删 `config.py:100` 启动定格；`scratch_*` 换 `DraftStore`（加 `mark`/`unmark`、`list` 仅已标，去 history）；`timer` 三件改绑 `Clock`/`Signal`。
- **验收**：`python3.11 -m pytest tests/ -q` 绿；`_run_fake` 冒烟；取值型同步当轮返回。
- **注意**：`tests` 里 `scratch_*` 约 27 处引用会回归，属正常；`execute` 保留到 `term` 上线再删。

## 纪律（照 plan §0）

- 三问每步走；发现设计问题回 `checkpoint-1.md`；不替 agent 决定用法；旧代码对象级一次性替换。

## 收工

- 写 `work/A/checkpoint/handoff-tools-02.md`，含 plan §4 六字段：入口／已完成／未完成／验证结果／新发现／下一批（范围、依赖、开工前待定）／待 YZ。
