# cogos 工具呈现（toolbox）实现 + 分层验收（2026-09-28 收口）

> 结论：**工具呈现设计已实现并全阶段验收通过**（S0–S4 代码 + 阶段 I/II/III 真实探针；S5 真实飞书身份 e2e 本次跑通）。工作树干净，任务收口。
> 过程材料（scratch，收口后删）：`ENTRY.md` / `code-map.md` / `toolbox-walkthrough.md` / `toolbox-design.md` / `toolset-decisions.md` / `handoff-08..10.md` / `discussion-discipline.md`。

## 做了什么（why）

- 目的函数＝**感知清晰度**（低认知负荷 → 推理质量），token 次要。总目的：把模型的工具从"散"变"可用"。
- 工具呈现最终形态：模型只见 **3 组用法总览（常驻 `system-reminder` 消息）＋ 单一元工具 `toolbox`**；`tool-schema` 恒定（只有 `toolbox`）→ 命中前缀缓存；用法按需求 `toolbox help` 逐级精确路径展开（`help` 空＝三组 / 组 / 面 / 能力）；执行 `toolbox call <path> {args}`。
- "可用"判据：①3 组总览＋单 `toolbox`；②不查文档能选到能力并调起来（help/call）；③一次真实操作端到端跑通。

## 代码（cogos master，已提交，工作树干净）

- S0 `f8ef94a` catalog（模型面目录单一来源，新 `cogos/agent/catalog.py`）
- S1 `67011d0` toolbox 元工具 + help 四级（新 `cogos/agent/toolbox.py`）
- S2 `fd2752b` call 路由（含组合能力 `computer.command.run` = open+exec+observe）
- S2 修复 `8a5cdf1` run 等 shell readiness（否则丢输出）
- S3 `42f09aa` 对外只暴露 `toolbox` + `system` 后注入常驻总览
- S4 `9183508` 事件按模型面前缀渲染 + 会话短标签 `t<id>`
- 测试：`python3.11 -m pytest tests/agent tests/cog_runtime` → **300 passed, 3 skipped**（系统 `python` 是 3.9，必须用 `python3.11`）。

## 验收（agent 视角，硬纪律：无真实对照不算完成）

- 阶段 I/II（真实 deepseek 探针）：模型只挂总览＋单 `toolbox`，自行 `help` 逐级 → `call run/web`；判据 1、2 成立。
- 阶段 III（主路径，真实模型 + FakeTelecom）：`Agent` 装配 → 投递消息 → `help` 发现 → `call run cat hello.txt` → 拿 `MAINPATH-OK` → 经通信回消息。
- **S5（本次，真实身份 + 公开入口）**：起 feishu daemon（systemd user）+ LM service + `python3.11 -m cogos.agent.app --agent ~/.cogos/agent/tangyu`（唐钰 = COGOS002:A0005）；真实飞书消息从 李恪(A0001) 经真实 P2P 群 `oc_6ab7…` 发入。地面真值（LM `calls.jsonl`，2026-09-28T11:21:55~11:22:05）：
  - 模型上下文 = 人设（无工具清单）＋ 常驻总览（3 组）＋ 来源消息；
  - `toolbox(call, computer.command.run, {command:"cat E2E-S5.txt"})` → `S5-REAL-E2E-OK`（session `t1`）；
  - `toolbox(call, communication.message.send, {to:…})` **报错**（错参名）→ `toolbox(help, communication.message.send)` 拿参数说明 → 改 `target` 发出；
  - 飞书 `events.log`：`received` 11:21:54 → `sent` 11:22:05 回 A0001。
  - 判据 3 全中；判据 2 的 help 自纠同时出现。

## 关键决策 / 偏离（详见收口前 `code-map.md §阶段 I 决策`）

- catalog 纳入 `open/list/send`（原 §9 记为机制，按 walkthrough 步 2 目标纳入模型面）。
- `run` 内建**两处有界等待**（shell readiness + output settle，≤~6s，非模型参数）：不加会丢 pty 首条输出 → 判据 3 跑不通。**若视为新增机制格须回讨论。**
- `answer_auth` 仅声明（机制选槽未接）；S4 只做单会话短标签；事件前缀映射 `term.*→computer.command`、`timer.*→computer.reminder`、`web.*→computer.web`、`phone.*→communication.file`、`transfer.done→computer`。
- **已否（why 见 `ENTRY.md`）**：完全按需（连名字都藏）→ 负荷从"选择"移到"发现"，违清晰；组描述写使用建议/排除句；按工具实现列清单（切碎跨面用途）；用意图翻译藏工具 / 独立意图匹配器（执行须精确）；用 `[来源:]` 承载视角（`[来源:]` 是世界数据专属）；缓存不作约束。Kimi 消息级动态工具（保前缀缓存）**参考不采用**（schema 走顶层）。

## 残留 / 后续（不在本次范围）

- 换视角细化（步 5）、错误渲染（步 6）、抹痕（`role:tool` 结果改走追加消息）、工具命令化、`wait` 参数化、多会话标签（A2 第二步）。
- 未定：用法加载后的淘汰/保温策略；机制工具面的命名与形状。

## 过程教训（与 YZ 更正）

- 上一会话把 S5 判为"外部阻塞"（本机无 telecom daemon、`~/.cogos/agent/tangyu` 无 `profile.md`、需指认账号）。实际 **daemon 可自起、profile 已存在、账号 A0001–A0005 真实可用** → 属**误判阻塞**，且未按规则（`rules/task.md`：YZ 在场带倾向求助 / 不在场升级）求助。规则校准：**判"阻塞"前先穷举本地可自解项并动手验证**，只有真不可逆/外溢才停。

## 交接 / 环境事实（复现用）

- LM service：`python3.11 -m cogos.lm_service.cli server`（127.0.0.1:11434），internal key `ik_c47WkfAw7E5v6Ck8idMHgg`（real deepseek，account 尾号b111）。
- feishu daemon：`cogos-feishu init`（systemd user：`cogos-feishu-daemon/monitor`）；账号在 `~/.cogos/feishu/accounts/`；唐钰 profile `~/.cogos/agent/tangyu/memory/profile.md`（联系人 YZ=COGOS002:H0002）。
- agent：`LM_INTERNAL_KEY=… python3.11 -m cogos.agent.app --agent ~/.cogos/agent/tangyu`。
- S5 探针文件 `E2E-S5.txt`（内容 `S5-REAL-E2E-OK`）在 agent work_dir。
