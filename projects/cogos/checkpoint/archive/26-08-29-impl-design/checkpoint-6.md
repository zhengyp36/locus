# checkpoint-6 — code-as-action 抛弃 + LLM 两层使用（产物型工具方向）

## 当前问题

推翻 agent-study 挂接结论 code-as-action，并确立「LLM 两层使用」的新设计方向。

## 关键结论（YZ 拍板）

### code-as-action 抛弃

- agent-study `hooks.md:4` 的 code-as-action（代码片段作 action）被抛弃。
- 理由：
  1. 越界：cogos 分界是「语义归 LLM，程序管外围」，动作执行本就是程序的活，code-as-action 把执行交回 LLM。
  2. 灵活性代价：裸代码执行 = 权限/安全失控（`hooks.md:4` 本想用受控 tool call 防的）；且代码不可折叠/检索/回链，塞不进认知树行动规则 schema（规则节点生命周期 = 试用→验证→载体→淘汰）。
  3. agent 不为写代码而设计，内部功能明确，不需 LLM 写代码实现内部功能；LLM 基本处理语义。
- 收敛：**LLM 输出 = 语义/结构化意图，执行全走受控工具 / cog-func，无代码生成**。

### LLM 两层使用（方向性，未固化本体）

- **内层**：LLM = agent 的语义器官（CogUnit → LLM-Service，机制层），「它在想」。
- **外层**：LLM = agent 造物里的组件（agent 写软件/工具，把 LLM 调用嵌进软件），「它造的东西在跑」。
- 写代码的真正定位 = **造物**（持久、可部署软件），非执行手段。code-as-action 错在把「造物」降级为「执行手段」。
- 「钻进代码里」= 存在边界延伸：agent 产物部署到哪，能力延伸到哪（递归自举，用 LLM 造含 LLM 的工具）。
- 工程落点（阶段 1 不做，schema 留位）：认知树「行动规则/工具」节点给**产物型工具**留位（工具不限于预定义 cog-func 组合，可含 agent 生成的软件）；机制层仍卡资源（产物内嵌 LLM 调用若走 lm-service 也归因同一 group/quota）。

## 遗留 / 待办（收口时）

- 本体 `../cogos/docs/agent-study-hooks.md` code-as-action 条目已改 `[暂不使用]`（08-28）。
- 「LLM 两层使用 + 产物型工具 + 自设计工具」待合流，收敛后再决定进 `cogos-concept-system.md` 还是 `cogos-plan.md`。
- 与「资源索引不做」「工具子系统（webtool-design）」的关系待理清。
