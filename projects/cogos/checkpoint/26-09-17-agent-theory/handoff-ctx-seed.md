# handoff｜cogos 通用 agent：上下文组织（ctx-seed 实验）

> 2026-09-12。新会话入口 = `status.md`；本文件是详细交接。
> 关联记忆：`locus/projects/cogos/entries/2026-09-12-cogos-general-agent.md`（完整讨论）。

## 一句话

从"自驱回路是为工程任务设计的吗 / 通用 agent 能否做纯思考"推出**路线修正：自驱的地基是上下文组织，不是调度机制**。
第一刀 = 意识上下文实现"**帧 → 蒸馏 → 冷启动重启**"，探针已写、`--fake` 通、**真机待环境**。

## 为什么（背景链，已定论）

- **通用性 = 判据谱系**（机器可判 ←→ 判断），不是"工程 agent + 思考 agent"两种。工程是"判据可廉价机器判定"的硬端。
- **回路三缺口**：机器二值判据 / 无"半成品"线程状态 / 单条一枪到底。
- **"该放放"由 agent 自己决定**（调度判断，非认知判断，故不自欺）；壳只当记账员+护栏。
- **症结**：`consciousness.py` 意识上下文裸 append、从不重组 → 帧=日志 → agent 出不来自己 → 不能自评 → 只能靠人或另一 agent。
- **精化模型**：换帧三时刻（蒸馏 / 存储**原地不搬** / 新帧按需拉）；**有损发生在取出**（reconsolidation）；**连续=蒸馏链非 transcript**；两节拍——在线（串行+按需拉）+ **离线睡眠**（批量重放/抽象/裁剪；抽象必须批量，按需替代不了）；**检索=解引用非搜索**（seed 自含、指针不载正确性）；**记忆组织=写时付、读时省**。

## 三刀（顺序）

1. **seed + 冷启动重启**（当前，优先）——判据 = 冷启动只凭 seed 能否续下去。
2. **线程单位 + parked/resume**——"放放/换线"。
3. **判据接口抽象**——硬/软判据都接（后置，别预造）。

## 实验现场（已做）

- worktree `/home/zhengyp/work/A/cogos-ctx`，分支 `ctx-seed`，基于 `s2-selfdrive-loop` `9563fe4`。
- 探针 `research/ctx_seed_probe.py`：帧 A（工具续轮展开）→ 蒸馏（seed JSON，字段 `intent/current_question/progress/open_questions/pointers/dropped`）→ 帧 B（**冷启动，只给 seed**）；打印 seed + 终答；raw.jsonl 落 `/tmp/ctx-seed-probe/<ts>/`。
- `--fake`（脚本化 client）**已跑通整条流程**：帧A 工具续轮 → seed 解析 → 帧B 解指针出终答。`--goal/--question` 可换靶。
- 默认靶 = cogos 自身工具续轮机制（答案可在本仓库核实）。
- **未 commit**；`consciousness.py` 未动。

## 下一步动作

1. **真机跑探针**（先起环境）：
   ```
   cd /home/zhengyp/work/A/cogos-ctx
   python3.11 -m cogos.lm_service.server        # 另开：lm-service
   LM_INTERNAL_KEY=<key> python3.11 -m research.ctx_seed_probe.py
   ```
   看：seed 是否自含、帧 B 是否续得上、**帧 B 有没有"重做/困惑"**（诊断蒸馏漏了什么）。
2. 据结果决定：换更"思考型"且有客观答案的靶 / 调 seed 字段 / 是否落 `consciousness.py` 并行路径（旧 append 保留 A/B）。
3. 再上第二刀（parked/resume）。

## 环境 / 坑

- 真机要 **lm-service**（`python3.11 -m cogos.lm_service.server`）+ 模型后端（deepseek `127.0.0.1:11434`）+ `LM_INTERNAL_KEY`。**当前三者均未起**（status.md 记录过 key）。
- **必须从 checkout 目录用 `-m` 跑**（`cd <worktree> && python3.11 -m research.ctx_seed_probe ...`）：editable 的 `cogos` 钉在 `work/A/cogos`（master），直接用脚本路径 import 会**静默跑错代码**。已验证 `python3.11 -m` 从 `cogos-ctx` 下解析到本地包。
- `cogos-ctx` 基于 `s2-selfdrive-loop`，含 loop 工作，但本实验只碰 consciousness/上下文层，与 loop 解耦。

## 待 YZ 决策点

- 真机靶选哪个（默认用仓库机制问题；也可给一个更"纯思考"、你能判真值的题）。
- 判据是"续得上"就够，还是要加"帧B 不重做"的更强约束。
- 分工：探索型单 owner（设计+实现同一人），另一工位末端复核。

## 锚点

- 完整讨论：`locus/projects/cogos/entries/2026-09-12-cogos-general-agent.md`
- 路线修正：`locus/projects/cogos/ROADMAP.md`（09-12 修正节）
- 代码：`work/A/cogos-ctx` @ `ctx-seed` → `research/ctx_seed_probe.py`；意识层现状 `cogos-s2/cogos/agent/consciousness.py`
- 上一阶段（P0/L1，已完成）：`handoff-layered-acceptance.md`；`cogos-s2` @ `9563fe4`（已 push `s2-selfdrive-loop`）
