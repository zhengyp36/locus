# report｜ctx-seed 判别实验 E1/E2（真机）

> 2026-09-12。承接 `ctx-seed-probe-report.md`（首跑）与 `locus/projects/cogos/entries/2026-09-12-cogos-ctx-seed-diagnosis.md`（诊断）。
> 探针已扩：`--arm {current,axes,narrative}`、`--b-mode {neutral,loose,strict}`、`--hops N`。

## 设置

- 靶：`research/target`（埋雷取证靶），每臂跑在**干净副本**上（`/tmp/ctx-seed-e1|e2/<arm>`），跑后 diff 源文件。
- 契约固定为**中性**（`--b-mode neutral`，不注入"已核实/别重验"也不授权取指针）——测组织方式本身。
- 模型 temperature=0（近确定性），但 provider 仍有轻微抖动（见下）。
- E1：三臂，单跳。E2：`current` vs `axes`，`--hops 3`（逐跳重新蒸馏，测链退化）。

## E1 结果（组织方式，单跳，中性契约）

| 臂 | 帧 A 调用 | **帧 B 工具调用** | 帧 B 轮次 | 靶被改 | 答对 |
|---|---|---|---|---|---|
| current（现状 schema） | 15 | **6** | 3 | 否 | 是 |
| axes（正交轴） | 15 | **0** | 0 | 否 | 是 |
| narrative（第一人称） | 15 | **0** | 0 | 否 | 是 |

- `current` 的 seed：`open_questions` = 3 条**下游动作**（"`load` 重复读盘要不要报告？""`_CACHE` 全局要不要提示？""要不要给补丁？"），无一条是阻塞未知。
- `current` 帧 B 随即用 6 条 `execute` **重做**：cat 全部源码、重跑 report/selfcheck、反向顺序验证、rounding 边界、独立复算。
- `axes` 的 seed：`open: []`、`next: [修复建议]`；`narrative` 首人称叙述。两者帧 B **零调用**，直接作答（且回答了 next，但没执行）。
- → **信息被当待办的直接机制坐实**：`open_questions` 没地方放"下一步"，只能塞动作；帧 B 见桶就执行。给 `next` 一条轴后，动作不再落进 `open`。

## E2 结果（多跳链，hops=3，中性契约）

| 指标 | current | axes |
|---|---|---|
| seed 字符（hop0→1→2） | 2269 → 2971 → 3641（**逐跳膨胀**） | 2575 → 2748 → 2748（**收敛**） |
| 帧 B 工具调用（B1/B2/B3） | 14 / 8 / 8（**持续重做**） | 11 / 0 / 0（**停下**） |
| 是否改动靶源码 | **是**：B1 用 execute 改写 `cache.py` 为双键（`selfcheck` 转 0 failure） | 否（`selfcheck` 仍 2 failure） |
| B2/B3 看到的真相 | 已被 B1 改过（污染） | 原状 |
| 末尾答案 | 转向"修复已确认" | 原问题，正确 |

- `current`：链**既重做又越权动作**，把世界改了，后续跳继承了被改过的状态 → **链漂移**，末跳在回答一个已非原题的问题。
- `axes`：链收敛（seed 尺寸稳、调用归零、不动世界）。
- **但 axes 的 B1 仍有 11 次调用**：因为该次 hop0 的 `open` 被填了一条"非阻塞项"（原文以"无阻塞性未知"开头，却仍列了一条）。对照 E1 axes（`open` 真为空）→ 0 调用。故：
  - **重做与 `open` 是否为空强相关**；
  - **正交 schema 不能保证 `open` 不被填**——"桶会被填满"在 `open` 上仍会发生（只是比 `open_questions` 轻）。

## 关键结论

1. **组织方式确实决定行为**：同样的内容，`current` 触发重做、`axes`/`narrative` 消除重做（E1）。
2. **主机制是维度分离**（`open` vs `next`），不是"主体叙事"：`axes`（无第一人称）已足够消除重做——我原先"必须第一人称"的下注**未被支持**（至少本靶不必要）。
3. **仅换 schema 不充分**：蒸馏器仍会把非阻塞项塞进 `open`（E2 axes），此时又重做。还需约束 `open` 语义（只放阻塞未知，没有就留空），或由续接侧只认"阻塞"。
4. **旧 schema 的危害不止重做**：它诱导**越权动作**（B1 改源码），进而**污染后续跳的真相**、seed 逐跳膨胀、末跳跑偏——多跳下从"重做"升级为"链漂移"。
5. **帧职权的空档暴露**：`current` 帧 B 直接改了代码；`axes` 只验证不修。`next` 到底"我做 / 交下一帧 / parked"未定，行为随机——必须先裁。

## 坑 / 方法学

- **n=1/臂、单靶、且是"问题已答完"的任务**：不能外推。`axes` 两次跑结果不同（`open` 空 vs 非空），既是发现也是噪声来源，需重复 + 换靶。
- **execute 是任意 shell**：帧能改文件、写 `/tmp`（E2 current 又留了 `/tmp/cache.py.bak`）。每臂必须用独立副本并 diff。
- 待补：**第二类靶**（真有剩余工作的任务）+ 每臂重复若干次。

## 下一步（待 YZ）

- 先裁**帧职权**（陈述 / 行动 / parked），它决定 `next` 语义与后续所有对照。
- 加第二类靶 + 重复，确认 3/4 的普适性。
- 再定 seed v2 形态：`axes` 起步，强化 `open` 语义；`narrative` 作为可选臂。
- 之后再落 `consciousness.py`（并行路径，旧 append 保留 A/B）。

## 现场

- 探针：`work/A/cogos-ctx/research/ctx_seed_probe.py`
- raw：`/tmp/ctx-seed-e1/{current,axes,narrative}-log/raw.jsonl`、`/tmp/ctx-seed-e2/{current,axes}-log/raw.jsonl`
- 靶副本：`/tmp/ctx-seed-e1|e2/<arm>`（`current` 副本已被改，作污染证据保留）
- 靶原始：`work/A/cogos-ctx/research/target/`（未动，selfcheck 2 FAIL）
