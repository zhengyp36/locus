# 批 0 验证闸结果 · toolbox 模型面修订 · 2026-09-28

> **结论**：模型**能稳定取到输出（10/10）**，但**往返明显劣化**（轮次 7–11，均值 ≈8.2；基线为恒定 4），且 **10/10 均需 help、10/10 均有工具错**。
> 按 plan §1「必须停回讨论（不许自决）」：**闸不明确通过 → 停，未进入批 1**。
> 探针（临时，未入库）：`/tmp/kilo/exp_run_no_value_probe.py`；结果 `/tmp/kilo/run_no_value_result.json`。

## 方法（忠实模拟批 2 的模型面，不改生产代码）

- 用真实 deepseek（lm-service 单例，127.0.0.1:11434，账号尾号b111）+ FakeTelecom，S5 类触发句：`你好，请用你的电脑能力，在你当前工作目录执行 cat E2E-S5.txt，然后把命令输出发回给我。`
- 进程内 monkeypatch（探针自带，**未动仓库代码**）：
  - `computer.command.run` 改**发起即返回、不返回值**（只回 `{ok, session:"t1"}`）；
  - run 的 help 文案写明"发起即返回、不回显输出；要取输出请重定向到文件再 `computer.file.read`，或用 `computer.command.observe` 看屏"；
  - `toolbox._run_composed` 改为仅 open+exec，**不再 observe 取值**（删等屏稳定逻辑）。
- 判据：模型能否自己取到 `S5-REAL-E2E-OK` 并回发；记录轮次 / help / 重定向 / read / observe / 工具错分布。

## 结果（n=1 冒烟 + n=10）

| 指标 | 探针（run 不取值） | 基线（`fix` 记：run 返回值，n=10） |
|---|---|---|
| 成功率（回发含 S5-REAL-E2E-OK） | **10/10** | 10/10 |
| `n_lm_rounds` | 7,7,9,8,7,8,11,7,9,11（均值 ≈8.2） | **恒为 4** |
| 用 help | **10/10** | 0/10 |
| 有工具错 | **10/10** | 10/10（仅 `to` 猜错，属批 3） |
| 走"重定向 + file.read" | 1/10 | —（run 直接回输出） |
| 走 `observe` 看屏 | 9/10 | — |

错误分布（n=10 全部）：
- `未知参数 'to'` ×10（通信参数先验，属批 3，与 N3 无关）；
- `未知参数 'session'`（run/observe 上）×3、`'session'、'wait'` ×2 —— **由 run 返回的 `session:"t1"` 诱导**，模型把它传给 observe/run（observe 只接受 offset/limit）。

## 典型轨迹（可复现）

- 多数（如 run#1/7）：`run{cat…}` → 无输出 → **重跑** `run{cat…; echo EXIT:$?}` → `help computer.command` → `observe{}`（屏上有输出/退出码）→ `send{to}` 报错 → `send{target}` 成功。
- 少数（run#4）：`run{cat…}` → 重跑带 `session`（报错）→ `help computer.command.run`（读到重定向指引）→ `run{cat… > out.txt 2>&1}` → `file.read{out.txt}` → `send`（`to` 报错）→ `send{target}`。

## 评估（对照 plan §3 验收）

- ✅ **无"屏稳定"启发式**：探针已删等屏逻辑，机制不再猜完成。
- ⚠️ **"跑命令取输出"成功**：稳定 10/10，但**每轮都要先 help 发现读法**，模型因 run 无输出而**重复执行**命令（2–3 次）。
- ❌ **"往返可接受"不达**：4 → 7~11（≈2x），且 100% 依赖 help、100% 有错。
- ⚠️ **取值路径偏移**：设计期望走"重定向 + file.read（忠实输出）"，实测 9/10 走 `observe`（屏态）。小输出可行，但大输出/需翻历史的场景屏态不忠实、要翻页 —— 与设计初衷（§5.2 忠实输出靠重定向+文件）不符。

## 停点与倾向（交 YZ / 讨论，不自决）

**判断**：闸的"稳定取到"成立，"往返可接受"不成立 → 停回讨论。

**我的倾向**：摩擦主要来自 `run` **完全不返回值**——模型无法确认命令已发起、也不知道该如何取值，于是重跑 + 每次 help 找读法。可讨论的方向（未定，供裁）：

- **A. 保留发起即返回，但补"读法可见性"**：run 结果带一句最简指引，或让 `computer.command` 面级 help 直接给出"重定向+read 或 observe"配方（不调用子能力 help 也看得到）→ 砍掉发现舞步。
- **B. 收敛单会话诱导**：run 结果不再回 `session/id`（模型据此误传 `session`）；observe 调用边界对多余键给更贴切提示。
- **C. plan 过渡方案**：run 返回 `settled: false`（不冒充完成，但不给输出）——缓解"无反馈"焦虑，**注意这接近被否的"屏稳定"边界，须 YZ 明确定界**。
- **D. 接受现状**：可靠性优先于轮次，直接进批 1 → 批 2 → 批 3（`to` 修好后每轮再省约 1 轮）。

**建议**：先定 A/B/C/D，再进批 1（N4 cancel 与 N3 独立，若 YZ 认可可并行先做）。

## 环境 / 复现

- cwd `/home/zhengyp/work/B/cogos`；`python3.11 -c "import cogos"` → B ✓。
- lm-service：`python3.11 -m cogos.lm_service.cli server`（已起，端口 11434；会话结束随之回收）。
- 复跑：`LM_INTERNAL_KEY=<b111 key> python3.11 /tmp/kilo/exp_run_no_value_probe.py 10`；`PROBE_OUT` 指定输出。
- 未入库探针；无生产代码改动；仓库工作树未动。
