# agent 目录结构规范化（profile.json + runtime 运行事实）

> 状态：已落码并推送，commit `ce7ac7a`，全量 1351 passed＋6 skipped。
> 来源：YZ 提出目录整理初稿 → 讨论钉 runtime 语义 → 方案 A（意识流与记忆平级）落地。

一句话：agent 目录从「配置/状态/内容混在 memory 下」规范为三层——配置（`agent.json`＋`profile.json`）、运行事实（`runtime.json`/`last_runtime.json`）、内容（`stream/` 意识流＋`memory/` II型＋`events/`＋`phone/`＋`work/`＋`machine/`＋`secrets/`）。

## 动机（why）

目录演进过程积累了几处脏东西：`profile.md` 塞在 `memory/state/`（配置混进记忆目录）、`segments.jsonl`/`scratch/`/`spool/` 是旧模型/旧流程遗留、`State.facts`（boot_ts/birth_ts/powered_on）纯内存导致「出生」每次重启重来、意识流默认纯内存无处落盘。目标＝先把目录/状态规范化，再进下一步（续推→张力源→蒸馏）。

## 目录结论（方案 A）

```
~/.cogos/agent/<name>/
├── agent.json              # 总入口：memory_dir/phone_dir/work_dir/stream_dir/computers/default_computer
├── profile.json            # 纯人设（name/phone_number/contacts/pin）[迁移自 memory/state/profile.md，md→json]
├── runtime.json            # 本次运行实时态
├── last_runtime.json       # 上次运行快照（boot 时由旧 runtime.json 归档，单槽）
├── stream/                 # 意识流落点（CogStream store_dir）
├── memory/                 # II型（fold/unfold/mark，INDEX.md + <slug>.md）
├── events/  phone/  work/  machine/<name>/  secrets/
```

- **意识流与记忆平级**（方案 B「memory 总类下挂 stream/concepts」被否）：意识流是过程痕迹/蒸馏上游，记忆是蒸馏产物，性质不同；且 memory/ 已是 II型，平级加 stream/ 改动最小，不为未落码的蒸馏/I型预建假层级。

## runtime.json 机制

- 字段：`birth_ts`（首启，继承）/`boot_ts`（本次启动）/`last_state`（active|idle）/`last_intervene`（tool|reasoning|stopped）/`last_state_ts`/`shutdown`（clean|null）/`shutdown_ts`。
- **boot 归档**：启动时旧 `runtime.json` rename 成 `last_runtime.json`（单槽覆盖），`birth_ts` 继承（首启＝boot_ts）→ 出生只一次（修掉 State.facts 内存态每次重启重设的 bug）。
- **shutdown 靠缺失推断**：只在干净退出 `stop()` 写 `shutdown="clean"`；crash/kill 写不了文件，`shutdown` 留 null，恢复方读 last_runtime 判 null＝上次非正常下电。
- **状态写入**：Decider `on_state` 回调，`last_state` 由 Action 推（Proceed/Relay/Switch=active、Stop=idle）、`last_intervene`=介入点类型；状态变迁即写＋统一 5s 节流（活跃/闲置都节流，避免长跑活跃时 last_state_ts 陈旧）。

## 落码要点

- `runtime_state.py`（新增）：`boot`（归档＋继承）、`update`（读改写）、`mark_shutdown`、`read_last`。
- `config.py`：`load_profile(agent_dir)` 读 `profile.json`（JSON，去 yaml）；`AgentConfig` 去 `state_dir` 加 `stream_dir`（默认 agent_dir/stream）。
- `decide.py`：`on_state` 回调＋`_track_state`（删 birth_ts 运行时重设）。
- `assemble.py`：boot_runtime→State.facts、`store_dir=config.stream_dir`（默认持久化）、stop 时 mark_shutdown。
- `skeleton_loop.py`：`_make_agent_dir` 改写 `profile.json`（否则 load_profile 会 FileNotFoundError，检视时发现并修）。

## 被否 / 未采用

- **单文件混合**（runtime.json 里同时塞「本次实时态」和「上次退出方式」）→ 否：改「boot 归档成 last_runtime」，本次文件只记实时态更干净。
- **`shutdown: "crash"` 作为文件里存的枚举值** → 否（YZ 指出 crash 写不了文件）：crash 靠缺失推断，文件里只存 `clean` 或 `null`。
- **出生时间放 profile.json** → 否：出生是运行时事实不是配置，放 runtime.json 继承。
- **方案 B（memory 总类下挂 stream/concepts/I型）** → 否：II型要挪进 memory/concepts/（动 MemoryStore），且蒸馏未落码前 distill/ 只能空着（假层级）。

## 遗留

- 恢复消费：读 last_runtime 判上次退出方式/状态的恢复流程未实现（本次只做记录）。
- 签名身份：预留 `secrets/` 空位、用途未定（唯一确定 agent 身份，暂用不到）。
- I型/II型 附着关系：fold 平铺 vs 按主题分组降条数，先平铺。
- `machine/` 与 `work/` 并存（machines 引入后的遗留）未合并。
