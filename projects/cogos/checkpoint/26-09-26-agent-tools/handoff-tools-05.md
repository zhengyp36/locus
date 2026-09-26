# handoff｜工具现状过目 · web 工具异步化（新会话入口）· 2026-09-19

> **新会话任务**：**暂不推进实现**。先过目当前工具现状，再讨论 **web 工具（`search`／`fetch`）是否异步化**。
> **交接语**：读 `work/A/checkpoint/handoff-tools-05.md`，先过目工具现状，讨论 web 工具异步化。

## 入口

> `cogos` @ **`4f3c017`**（`docs: reconcile agent-tools design with batch decisions`）；前一个 `ac1ef13`（批次 4a 代码）。工作区干净。

1. **`work/A/checkpoint/plan-tools-impl.md`** ← 批次划分与铁律；批 4 已拆 4a（已做）／4b（缓）。
2. 权威：`cogos/docs/design-agent-tools.md`（§2 三层、§3 清单、§4 时间形态、§12 分包、§14 范围）。
3. A 接口形状：`work/A/checkpoint/spec-tools-a.md` v1.3。
4. 过程与裁决：`checkpoint-1.md` **§19~§28**（批次 4a 见 §28；审核对账见 §27）。
5. 代码：
   - A：`cogos/agent/impl/{base,clock,draft,timer,phone,terminal,secret,fs,transfer}.py`。
   - B 契约表：`cogos/agent/tools.py`（`ToolDef(schema, fn, time_form, prompt)`＋各 `make_*` 工厂＋`ToolRegistry`）。
   - 装配（临时）：`cogos/agent/app.py:_build_specs()`；system prompt 由 `ToolRegistry.prompt_lines()` 派生（`config.py:render_system_prompt(profile, tool_lines)`）。
   - web 实现：`cogos/agent/webtools.py`（aiohttp＋代理；`SEARCH_TIMEOUT=20`／`FETCH_TIMEOUT=60`／`MAX_FETCH_SIZE=50000`）。
6. 测试：`tests/agent/`（web 见 `test_webtools.py`；契约/单一来源见 `test_app.py::test_toolset_single_source`、`test_tools.py`）。

## 现状（批次 4a 后）

- **A 层（能力）已完成**：`Clock`／`DraftStore`／`TimerService`／`PhoneCapability`／`ComputerManager`(term+fs)／`TransferEngine`；含远端 term、`SecretStore`/askpass、远端 sftp。
- **B 层（契约）已单一来源**：`ToolDef` 表同时派生 registry／白名单／system prompt；`time_form`／`prompt` 必填并校验；registry 校验 `key == ToolDef.name`。**扁平名保留**。
- **C 层（装配）未做（4b，缓）**：`assemble(role/context)`／分包／按需装配／`agent.json`「电脑」配置接线均未做。`sync_reachable` 仍是 `app.py` 单点条件。
- **时间形态现状**（`ToolDef.time_form`，元数据）：`sync`＝time／draft／timer set-cancel-list／fs／**search／fetch**；`async`＝term／transfer／send_msg。

## focus：web 工具异步化

- 现状：`search`／`fetch` 标 `time_form="sync"`，当轮返回长内容（搜索结果列表／网页 markdown，`fetch` 可到 50KB）。
- 纠结点（design §4 判据＝**取值型 vs 后果型**，不按 target 位置）：
  - 若视为**取值型** → 保持同步（有界）现状；网络/超时靠 `SEARCH_TIMEOUT`／`FETCH_TIMEOUT` 兜。
  - 若视为**后果型** → 发起即返回＋结果走事件；但 design §4 明说「**事件只做短通知、不带长内容**」，而 web 的价值恰是长内容 → 需要配套通道（结果落草稿／机器文件，事件只带 handle／id；agent 再 `draft`/`fs` 取）。
- 相关既有边界：design §11「来源只在入口标注」；§14「`search`/`fetch` 冻结现状」；§15「组装 cu（单弧预算／可打断／续弧落账）整体遗留」；§18.3「异步非免费，结果成事件 ⇒ 续弧与落账归组装层」。
- 建议讨论项：① web 归取值型还是后果型；② 若异步，长内容走哪条通道（draft／machine file）；③ 是否需要 `web.done` 之类事件名与 payload；④ 与「组装 cu 层遗留」的依赖顺序（没有续弧机制时异步化是否只是把值挪走）。
- 不替 agent 决定用法；只保证能力完整、可控、可观测（plan §0）。

## 遗留（不在本会话范围）

- **4b 装配**：`assemble(role/context)`／分包／按需装配／`agent.json`「电脑」配置接线（`checkpoint-1.md` §25.2／§28.4）。
- design §11「来源＝具体标识」是否给内部事件更细来源（§15.4.1）——入口／事件 schema 话题。
- `experiment/selfdrive/loop.py:TASK_TOOLSET` 仍是旧无 `id` 的 `read_file` 语义（实验脚本）。
- 批次 2.5 旧遗留：armed/一次性 token、槽位列举、密钥/`ControlMaster`。

## 纪律（照 plan §0）

- 本会话**只过目与讨论**，不动代码；发现设计问题回 `checkpoint-1.md`。
- 一批一会话；开工前重审 spec／权威分册。

## 收工

- 讨论若形成结论 → 回记 `checkpoint-1.md`；需要动手再另起 handoff。
