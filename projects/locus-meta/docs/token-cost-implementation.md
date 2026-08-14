# Token 消耗方案实施计划

> 2026-08-14。来源：projects/locus-meta/docs/token-cost-analysis.md（四方案定稿，101K 样本归因）。
> 三阶段：阶段 1 完成、阶段 2 已定稿待执行、阶段 3 待办。

## 总判断

四方案分两类，只打 ~80K 变动部分，够不到 ~20K 固定开销：

- **行为约束**（C 最小锚点 edit、D 清单式总结、语言）：改 AI 习惯，零基础设施，立竿见影。
- **资产建设**（A 代码地图、B subagent 记忆提取）：建"代码认知地图"资产，见效大（40K 那个大头）但复利依赖摘要质量，需验证。

## 人机分工

人定规则、判边界、验收质量；AI 执行、探索、生成。

三件事不自动化：① 定规则（省 token 协议本身）② 判边界（什么值得落盘/地图放哪/选哪个试点）③ 验收质量（摘要是否敷衍——复利兑现的前提，整套方案最大失效点）。

## 阶段

- 阶段 1 —— **完成**：C + D 清单式 + 语言写进 AGENTS.md "省 token 行为"一节。
- 阶段 2 —— **已定稿，待执行**：cogos 试点 A+B（结论见下）。
- 阶段 3 —— **待办**：复盘推广（复利跑通 → 固化通用约定推广；跑不通 → 查摘要质量不硬推）。

## 阶段 1 细则

- C 最小锚点 edit：oldString 只贴"改动行 + 前后各一行上下文"，够唯一即可；大改动拆多个内聚小步。
- D 清单式总结：改的文件（各一行）、验证结果（一行）、遗留（一行），不复述 diff。
- 语言：机器向产物用英文（代码/提交信息/变量名/日志/路径/结构化摘要）；思考语言 = 输出语言，不刻意切。

## 阶段 2 定稿（cogos 试点 A+B）

### 关键发现

cogos `~/codex/cogos/docs/code-structure.md`（08-09，G3c 基线）本质就是方案 A 的"代码认知地图"，但已过时：缺整个 comm/bs_* 线（101K 的主题），session.py 标"待编码"实已实现，目录布局是旧 `frame/` 子包。实物验证方案 A 最大失效点——地图写了没人维护就废。

### 已定结论

1. **试点 = cogos**。
2. **地图 = AI 对代码库的认知/记忆**，不是工程文档；维护地图 = 维护 AI 的认知。
3. **地图落点 = locus `projects/cogos/entries/`**（AI 认知统一入 locus 记忆，本体留人读文档）；current.md 放指针。
4. **树型 + 按需加载**：单文件分节模拟树（markdown 标题做节点）。读取流程 = ① read 顶层索引节（模块清单 + 一句话职责）→ ② grep 标题拿行号 → ③ read 目标小节。定位靠标题锚，不硬编码行号（写时同步重写会漂移）。粒度 = 模块级（小节 <100 行整读可接受）；顶层索引 <50 行。
5. **写时同步**：改代码后即时重写对应小节。触发边界 = 改动是否改变模块的不变量/易错点/调用关系/入口/测试命令，没变不动。重写式（记忆式）非追加式。
6. **读时对照**：读代码发现与地图矛盾 → 更新。可能性小（自己改会同步，只有别人改才不一致）→ 矛盾是强信号，值得停下来核。
7. **载体分离 / AI 认知归属**：AI 对 cogos 的开发约定 + 代码认知统一收进 locus `projects/cogos/`（管理层 README 放确定的锚；记忆层 entries/ 放会变的地图/易错点）。cogos 本体只留代码 + 人读文档。
8. **cogos/AGENTS.md = 接管声明**：本工程由 locus AI 接管开发，约定与代码认知见 locus；暂不支持其他 AI 直接开发，以免信息理解不全。
9. **记忆契约修正（已改 AGENTS.md）**：除 CHANGELOG（历史，追加不重写）外，管理层（README 等）也允许重写，但需慎重、与人讨论后重写，避免追加变流水账。

### 冷启动（下一步执行动作）

**方案 b**：零新增源码读取，纯搬运已有材料 + 缺失标"待补"。

执行步骤：

1. 新建 `projects/cogos/entries/code-map.md`（单文件树型：顶层索引节 + 每模块小节）。
2. 搬运来源：
   - 框架模块（config/commands/cli/client/daemon/monitor/protocol/service/device/echo/ws/session）→ 从 `~/codex/cogos/docs/code-structure.md` 搬职责/函数/不变量/入口/测试。
   - bs_provider/bs_card 不变量 → 从 `projects/cogos/entries/2026-08-14-cogos-bugfix.md` 搬（patch 授权、幂等 merge、`bot-` 前缀 bug）。
   - 模块清单 → `projects/cogos/README.md` 关键文件。
3. 缺失标"待补"：session/accounts/handler/daemon/bs_cmd/bs_setup/bs_workspace/bot_manifest/bitable_helper/purge 等（职责一句话从文件名/README 推断，不变量标"待补"）。
4. `~/codex/cogos/docs/code-structure.md` 改一句指针（人想了解结构问 locus AI）。
5. `projects/cogos/current.md` 加地图指针。
6. 建完收尾列"待验收：code-map.md 条目"（AI 主动提醒，见验收判据）。

### 验收判据

- 合格 = 职责一句话 + ≥1 条不变量/易错点（入口/测试命令加分）。
- 红线 = 只有文件清单 / 只列函数名 / 有职责零不变量。
- 时点 = 冷启动建完 + 每次联调写时同步后。
- **由 AI 主动提醒**：写时同步收尾固定列"待验收：code-map.md 的 X 条目"（漏列=失职）；跨会话待验收项写进 cogos 记忆"下一步"锚。
- 返工 = 人点出缺什么，AI 补读补全。

### 遗留 / 推迟

- 探索丢 subagent 细则 → 下次联调前定（projects/locus-meta/ISSUES.md）。
- 传播方式（通用行为约束是否上探全局 config）→ 阶段 3 复盘再判断。
- 方案 E（模型路由/便宜模型委派）→ 减单价正交轴，已记 projects/locus-meta/docs/token-cost-analysis.md 方案 E，落地推迟（候选模型价格比待查）。
