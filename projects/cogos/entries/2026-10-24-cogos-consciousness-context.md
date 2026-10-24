# 意识上下文（数据层 + 接口层）落码（2026-10-24）

## 结论（活跃）

意识上下文 = **被动持久化服务（积木）**，已落码 ② 数据层 + ③ 接口层，**不含上层编排**（归一化/醒/睡/IDLE 唤醒属更上层，另议）。

- 三 commit：退役 v2.2 flow 子系统 `2f0c34c`、数据层 `3d20dce`、接口层 `f76da56`。
- 全量 1350 passed（退役删 30 测，新增 21 测）。
- 载体 `cogos/agent/consciousness.py`：`FileState`（盘上七态）+ `State`（对外五态）+ 序列化 + `ConsciousnessStore`（数据层）+ `Consciousness`（接口层）。

## 数据层（persistence.md 落地）

- 文件 `<wake>.<context>.jsonl`，append-only JSON Lines，`type=message`/`type=state` 分派，**行序权威**。
- 盘上七态 `FileState`：loading/loaded/continuing/continued/unloading/unloaded/**idle**。
- 版本号 wake/context 均从 1；`meta.json` = 无意识文件时权威（`{"wake_version","context_version"}`）；`archive/` 归档。
- ts：内存 float epoch ↔ 盘上 ISO 本地偏移（`format_ts`/`parse_ts`，`astimezone().isoformat()` / `fromisoformat()`）。

## 接口层（interface.md 落地）

- 对外五态 `State`：ASLEEP/WAKING_UP/AWAKE/IDLE/FALLING_ASLEEP。
- 原语：`start_load`/`append`/`load_done`/`request_sleep`/`start_unload`/`unload_done`/`revoke`/`reset`。
- 介入点：`on_tool_done`/`on_done` → `_on_intervening`（判成败 → 检查点 → `InterveneContext` → 决策 → 第二件事(换cu/置None) → 第一件事(interrupt)）。
- 决策 tagged union：`Resume`/`Switch(new_context)`/`Sleep`。
- `do_switch` 换 cu 统一动作（Switch + revoke 共用）；`revoke` = 无 cu 的 Switch。

## 自决（10-24 已核对：第 1~3、5~6 条通过，第 4 条经讨论修订）

1. **构造补 `make_cu`**：原 spec `Consciousness(path, on_intervening)` 缺 cu 创建入口（起 cu 需 runtime/tools/registry，属上层）；`make_cu=None` = 纯持久化模式。
2. **`continued` → AWAKE**：§1.2 未列 `continued`，但逻辑 = 承接就绪、cu 在跑，归 AWAKE。
3. **interrupt 顺序**：按 §2.6 流程 + §9 已定-7「结束时 interrupt」（§2.7「在 do_switch 之前」判为措辞误差）。
4. **介入点重入（修订）**：`_do_interrupt(cu, reason)` 记录被中断 cu 的 `(id, 首次 reason)`（首次对齐 `interrupt()` first-wins），`_verify_interrupt(cu, result)` 校验——**tool 点重入恒 bug**；**finish 点 `cu is not self._cu` 或 `result is CuResultInterrupted` 均进 `_verify_interrupt`**（id 在记录 ＋ reason 匹配＝合法跳过、否则 bug，均 log+raise）。当前 cu 无记录却 settle Interrupted 也是 bug（堵 `CogRuntime.shutdown()` 绕开直调 `cu.interrupt` 的隐患）。记录保留最近 8 条不 pop（更稳、不依赖 settle 恰一次）、`start_load` 清空。
5. **is_first_wake = (wake_version == 1)**：出生/首醒为 1，首睡后 +1。
6. **meta.json keys**：`{"wake_version","context_version"}`。

## 被否方案

- 新模块名 `ConsciousnessContext`（避撞旧 flow 版 `consciousness.py`）→ **否**，先退役旧版、直接叫 `Consciousness`。
- 数据层塞进 `Consciousness` 类、不拆 store → **否**，拆 `ConsciousnessStore`（数据层可独立测试）。
- 内存态用 persistence §2 的 4 态（empty/loading/loaded/unloading）→ **否**，用 interface §1.2 对外 5 态（§2 的 4 态是旧模型，未在「待同步」清单里全改，遗留）。
- 介入点重入按「`cu is not self._cu` 静默 return」→ **否**（10-24），改 `_do_interrupt`/`_verify_interrupt` 显式校验（静默 return 会漏掉真 bug）。

## 遗留

- 上层编排（归一化/醒/睡/IDLE 唤醒）未做。
- 装载机制（记忆→2 条起点）、整理/重定向执行机制、目录名已定 `consciousness/`、掉电恢复未全覆盖。
- 介入「具体形态」（审视措辞/清理时机/留痕形式）仍待实验。
