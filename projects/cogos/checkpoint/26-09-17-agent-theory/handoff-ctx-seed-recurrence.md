# handoff｜ctx-seed 探针：从"维度塌缩"到"关系/身份层"

> 2026-09-12 末。新会话入口 = `status.md`；本文件是详细交接。
> 关联记忆：`locus/projects/cogos/entries/2026-09-12-cogos-ctx-seed-diagnosis.md`（本会话完整讨论 + 实验）。
> 前置：`handoff-ctx-seed.md`（本会话开始时的状态）。

## 一句话

真机跑通了 ctx-seed 探针的**判别实验 E1/E2**：证实"**维度塌缩**（认知轴⊕历史/议程轴）会让帧 B 把信息当待办、重做整个调查"，修法是**给 `next` 一条独立轴**（非第一人称）。末轮 YZ 用真人复现类比把问题又推深一层：**缺的是"关系/身份"层**（任务身份/来源/前次记录）——重做可能是"慎重"而非缺陷。**下一会话从这里继续讨论，先别落码。**

## 本会话做了什么

1. **首跑真机**（埋雷取证靶）：seed 内容自含（严格帧 B 零调用答对）；默认帧 B 重做 → 直接病因=`open_questions` 混入下游动作 + 宽松续接词授权重取。
2. **扩探针** `research/ctx_seed_probe.py`：`--arm {current,axes,narrative}`、`--b-mode {neutral,loose,strict}`、`--hops N`。
3. **E1（单跳，三臂，中性契约，n=1，temp=0）**：帧 B 工具调用 `current`=6（重做）/ `axes`=0 / `narrative`=0，均答对、均未改靶。
4. **E2（`current` vs `axes`，hops=3）**：`current` seed 逐跳膨胀 2269→2971→3641、调用 14/8/8，且 B1 用 `execute` **真改了源码**（`cache.py`→双键，selfcheck 转 0 failure）→ 后续跳继承被改状态、末跳跑偏（**链漂移**）；`axes` seed 收敛 2748、调用 11/0/0、靶未动、答案对。
5. **生成"蒸馏前后"文本**：`research/dump_seed_trace.py` → `checkpoint/ctx-seed-trace-dump.md`（含原始 seed、帧 A 终答、帧 B 输入/工具/终答），已发 YZ。

## 已得的结论 / 修正

- **成立**：信息被当待办、维度塌缩是**主机制**；拆开 `open`（未知）/`next`（待做）即可消除重做。
- **修正 1**：第一人称（`narrative`）**未**优于 `axes` → "必须主体叙事"未被支持（当前靶）。
- **修正 2**：仅换 schema **不充分**——`axes` 的 `open` 仍会被填"非阻塞项"，此时又重做；需约束 `open` 语义。
- **修正 3（末轮）**：E1 的"axes 修好了"说早了——帧 B 停下可能只是"**没有待办可做**"，不等于"**认出并信任记录**"。重做可能是**慎重**：seed 无身份/出处时，重新看是理性默认。
- **新暴露**：**帧职权未定**（`current` 直接改码 / `axes` 只验证不修）；`next` 是"我做/交下一帧/parked"无规矩。

## 待 YZ 讨论（下一会话，按序）

1. **关系/身份层**：任务身份（是什么/哪次实例）、来源/权威（谁派/为何现在/渠道）、前次记录（指针 + 等价判断 + 置信）、记录可用性（找到/没找到）——该不该进 seed、以什么形状。
2. **帧职权**：续接帧只陈述/思考，还是允许行动？`next` 是我做 / 交下一帧 / parked？（不裁此点，后续对照无法解释。）
3. **复现实验设计**：场合一做并记录 → 场合二新会话同题、记录**可达**（测信任 vs 重做）／对照记录**不可达**（应重验）。这是区分"信任"与"偷懒"的唯一办法。
4. **联想召回代价**：设计"第一版不做联想召回"→ 真人复现第一步"眼熟"无对应物；是否至少留**显式任务身份键**。
5. 方法学：n=1/臂、单靶、且是"问题已答完"任务 → 需补**第二类靶（真有剩余工作）** + 重复。

## 现场 / 文件

- 代码：`work/A/cogos-ctx` @ `ctx-seed`（未 commit）：`research/ctx_seed_probe.py`、`research/dump_seed_trace.py`、`research/target/`（埋雷靶，自包含）。
- 报告：`checkpoint/ctx-seed-probe-report.md`（首跑）、`checkpoint/ctx-seed-experiments-e1-e2.md`（E1/E2）、`checkpoint/ctx-seed-trace-dump.md`（原始文本）。
- raw：`/tmp/ctx-seed-probe/*/raw.jsonl`、`/tmp/ctx-seed-e1/{current,axes,narrative}-log/raw.jsonl`、`/tmp/ctx-seed-e2/{current,axes}-log/raw.jsonl`。
- 干净靶副本：`/tmp/ctx-seed-e1|e2/<arm>`（`current` 副本已被改，作污染证据）。

## 环境 / 坑

- 真机：lm-service（`python3.11 -m cogos.lm_service.server`，`:11434`，header `X-Internal-Key`，body 需 `tier`/`temperature`/`max_tokens`）+ 真 deepseek 后端。key `LM_INTERNAL_KEY=ik_c47WkfAw7E5v6Ck8idMHgg`。
- **必须从 checkout 用 `-m` 跑**（`cd /home/zhengyp/work/A/cogos-ctx && python3.11 -m research.ctx_seed_probe ...`）：editable 的 `cogos` 钉在 `work/A/cogos`（master），用脚本路径 import 会**静默跑错代码**。
- **探针无写文件工具，但 `execute` 是任意 shell** → 帧能改文件/写 `/tmp`；A/B 必须每臂独立副本并 diff。
- 跑测试/脚本用 `python3.11`。

## 锚

- 完整讨论：`locus/projects/cogos/entries/2026-09-12-cogos-ctx-seed-diagnosis.md`
- 入口：`status.md`
- 上一阶段（P0/L1，已完成）：`handoff-layered-acceptance.md`；`cogos-s2` @ `9563fe4`（已 push `s2-selfdrive-loop`）
- 意识层现状：`cogos-s2/cogos/agent/consciousness.py`（append 上下文，未动）
