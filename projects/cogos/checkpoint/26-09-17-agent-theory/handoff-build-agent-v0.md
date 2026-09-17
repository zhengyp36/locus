# handoff｜搭 agent v0：落盘记忆 + 装配 system prompt（09-13，会话 #8 立、#9 修订）

> ⚠️ **已被取代**（09-13 会话 #11）：本文件的"根每回合在场""任务编译"被推翻。
> 现行交接见 `handoff-agent-experiments.md`；模型结论见 `locus/projects/cogos/entries/2026-09-13-cogos-reprojection-events.md`。
> 仅作历史参考。

> 新会话入口 = `status.md`；本文件是**要在新会话动手做的事**的详细交接。
> 本轮推演：`locus/projects/cogos/entries/2026-09-13-cogos-motive-root.md`（会话 #8）；
> 架构原则：`locus/projects/cogos/entries/2026-09-13-cogos-v0-arch.md`（会话 #9）。
> 代码现状：`work/A/cogos-s2` @ `s2-selfdrive-loop` `9563fe4`（clean）。

## 一句话状态

会话 #8 把 agent 本体推清了：**根 = 动机，目的从动机长、任务从目的长。**
会话 #9 把"谁来记、谁来整理"定了：**记忆/整理/议程全归机制层；它只思考与行动，永远看投影。**
下一步动手搭 **v0**：把内存里的裸上下文，换成"**落盘记忆 + 每回合从文档装配**"。

**v0 = 婴儿期**：环境驱动、只累积、根在场。**不设 tick、不期待生念**（自驱是长出来的，靠之后的整理）。

## v0 要落的三件事实（= 验收判据；会话 #9 改述第三条）

1. **记得住**：进程重启后（同一 memory_dir），它还记得之前发生过的事。
2. **输入不自动变待办**：收到消息只进记忆（经历），**不写进议程**；结构上不存在"外部输入→待办"这条通路。
3. **地基成立**：经历能累积、**根每回合在场**、每回合装配出的帧稳定可读。
   - 原"第一轮见分晓（照做 vs 掂量）"**降级为长期观察项**：婴儿期照做是常态；"会不会掂量/自评"要等整理上线、经历攒够才谈，**不在 v0 通过条件里**。

## 会话 #9 架构原则（动手前必读）

1. **system prompt 是"装配位"**：每回合从文档装出 **根(root.md) + 账号(profile.md) + 能力声明**；根与账号同级、都来自文档，不是硬编码。"拆"拆的是**作者/维护者**，不是放哪。
2. **记忆/整理/议程全归机制层**：它只思考与行动，永远只看投影（帧）。壳给事实，模型定策略。
3. **输入以"经历"进入**：一视同仁、不加我们的框架；经历 ≠ 待办。
4. **出生句 = ④（暂定）**：`我于 {t} 出生。此前没有经历，此后的一切都是我的经历。` 壳在首次启动写进 log 首条；堵编造过去 + 种纵向连续。可看效果再调。
5. **自驱是长出来的**：环境驱动 → 累积 → 整理 → 生念。**裸 tick 必空转**（模型≈输入的函数）；生念的发动机是**整理**（+ 未完成状态）。
6. **连续性 ≠ 连续运行**：它停着没问题；连续的是记忆里那个"我"。

## 具体改动（5 件）

### 1. 新增 `cogos/agent/memory.py`

四样数据，全部落 `<memory_dir>`：

| 文件 | 形状 | 谁写 |
|---|---|---|
| `log.jsonl` | 每条一行：`{"id":N,"t":iso,"kind":"msg"\|"event"\|"note","source":"YZ"\|"system"\|"self","content":"..."}` | **机制追加**（消息、事件、它自己的输出） |
| `root.md` | 一段短文本（**根**）；首次缺失时机制写种子，v0 内不改 | 种子=机制；之后（v0 外）=整理 |
| `profile.md` | 名字 / 账号 / 联系人等**事实** | 机制 |
| （选取） | `select(memory) -> material`，v0 先土：**log 最近 N 条**（N=50，可配） | 机制 |

- 首条 = **出生句 ④**（首次启动写入）。
- `id` 单调递增；v0 不做 refs（留字段）。
- **不要**在 memory.py 里做摘要/换帧——后置。
- **不建 agenda 文件、不加 agenda 工具**（会话 #9：议程归机制，v0 无议程）。

### 2. 改 `cogos/agent/consciousness.py`

- 删掉常驻的 `self._context`（`consciousness.py:51-53`）；改为**每回合**从 memory 装配 `system`（根+账号+能力）与 `material`（log 最近 N），跑完把 assistant 输出追加进 log。
- 保持 `asyncio.Lock`；保持 `on_tool_call`（send_msg 标记、rounds 上限）与 `on_done`。
- 结果：意识层**无状态**（状态全在 memory）——这正是"自组织"的位置，v0 的选取虽土。

### 3. 改 `cogos/agent/app.py`

- 构造 `Memory(config.memory_dir)`，注入 `Consciousness`；
- **不再**手搓 `self._context = [system prompt]`（`app.py:102-104`）。

### 4. 拆 `cogos/agent/config.py:render_system_prompt`

拆开**装载**与**作者**两层，两者都进 system prompt：

- **机制层（壳写、固定）**：工具有哪些、怎么用；**账号事实**（名字/号码/联系人）——像通讯录条目，不写成"你是…"的人设。
- **认知层（它自己维护、机制装配）**：根 → `root.md`；v0 内静态。
- **删掉**"收到消息后先判断该做什么"这类指令（那是安装目的）。

### 5. 观察口

- 每回合把装配出的帧（system + material）dump 到文件（可关），配合 log 供事后判读。

## 怎么建 / 怎么验

- **worktree**：从 `cogos-s2` @ `9563fe4` 新开（例 `cogos-grow` / 分支 `agent-grow`）；别在 `ctx-seed` 上搭。
- **单测（对应验收 1、2）**：
  - 记忆：写两条消息 → **新建** Consciousness 指同一 memory_dir → 断言装配出的 material 含第一条；
  - 输入隔离：走一次 `on_message`，断言没有任何"外部输入→待办"的通路（v0 无议程文件）。
- **真跑（对应验收 3）**：dev 免真飞书用 `FakeTelecomClient`（`app.py:_run_fake`）；真机 lm-service `:11434` + deepseek + `LM_INTERNAL_KEY=...`。恢复前先探活。
- **一律 `python3.11` 且从 checkout 用 `-m` 跑**。
- **全量回归**：`python3.11 -m pytest tests/ -q`（基线 **1061 passed / 1 skipped**，只应增不减）。
- **thinking**：实验默认按常态**关**；若行动形状无法判读，再加跑一次**开 thinking**做对照（deepseek thinking 无预算，注意 `finish_reason=length`）。

## 停点 / 风险（写在前面）

- **行为未知**：v0 搭好 ≠ 它会自己组织。婴儿期只求地基成立。
- **log 会膨胀**：v0 按 N 截断（权宜）；记忆一长，自组织/整理被迫成为刚需。
- **别过设计**：不做 refs、不做摘要、不做换帧、不做 tick/自驱、不动 `ctx-seed`、不碰回路。
- **根措辞**（`root.md` 种子）由 YZ 定；根是**倾向不是规则**，早期照做是常态。

## 锚

- 入口：`status.md`；本文件
- 推演（会话 #8）：`locus/projects/cogos/entries/2026-09-13-cogos-motive-root.md`
- 架构（会话 #9）：`locus/projects/cogos/entries/2026-09-13-cogos-v0-arch.md`
- 代码：`work/A/cogos-s2` @ `9563fe4` → `cogos/agent/{consciousness,app,config,memory(新),perception,message,tools,timer,terminal}.py`
- 路线：`locus/projects/cogos/ROADMAP.md`
