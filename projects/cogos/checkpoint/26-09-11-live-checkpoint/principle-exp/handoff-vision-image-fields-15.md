# handoff｜coord 求解原图坐标落地 + ANNO 寿命=FIG + schema 契约自明验证（09-10）

> 上游：`handoff-vision-image-fields-14.md`（图上下文 K 修复 + 六次点击『工具(T)』取证 + 「标注坐标系」正误之争）。
> 本会话：把"求解坐标"做进工具并验证模型默认走对——① 图工具用途重定位（see 看清 / mark 点候选 / coord 换回原图坐标值）；② 新增 `coord` + `anno_to_src` 单点换算；③ **ANNO 寿命=FIG**（废除 `clear_fig_block`）；④ schema 契约自明（方法写进 coord 描述）+ 端到端验证（含隔离验证）；⑤ 文档同步 + 工具命名统一。
> 新会话只读本文件可接手。

---

## 一句话状态

- **coord 已落地并验证**：`coord(fig_ref, anno_id)` 纯读，返回**原图路径 + 形状 + `@原图` 坐标**（cross→`[x,y]`；rect→`[cx,cy,w,h]`，归一化 + 像素）。换算单点 `anno_to_src`（`@原图 = win_c − win_s/2 + u×win_s`），coord 与探针评分 `record_cross` 共用。
- **模型默认走对了**：`see 全图 → see 放大 → mark(局部子图) → coord`，一次收敛、无手算、无回全图打转。两轮命中：coord_1 px `(250.3,28.9)`、coord_2 px `(251.1,33.1)` vs 真值 `(255,32)`（可点带 `225≤x≤278 且 12≤y≤38`）。
- **schema 契约自足（关键结论）**：删掉 SYSTEM 里一切 coord 提示后（coord_2），模型仍主动走对 → **方法写进 coord 的 schema description 即可，不依赖 system-prompt**。
- **ANNO 寿命 = FIG**（YZ 拍板）：摘超龄图块不再清 annos（`clear_fig_block` 废除）；anno 随 `View` 在 registry 存续，重载同 `(path,window)` **带回**既有 anno；要清走显式 `clear_annos`。
- **文档 + 命名统一**：4 份 vision 文档同步；旧设计名 `load/view/draw/move/delete_anno` → 代码名 `see/mark/adjust_mark/unmark`（`load`+`view` 合并为 `see`）。
- 提交：`1b5153c`（feat coord + ANNO 寿命）/ `4555050`（docs + 命名）/ `f12d1f0`（chore 移除 lm-service 调试日志）。

---

## ① 图工具用途重定位（本会话立意）

模型要的是**目标在原图的坐标值**（远程控制拿去点按钮），不是"图上有个十字"。据此：

| 工具 | 用途 |
|---|---|
| `see` | 看清（开图 PATH / 调视野 FIG+center+size） |
| `mark` / `adjust_mark` | 点出、校准**候选**（cross 单点 / rect 区域） |
| `unmark` | 删候选 |
| `coord` | **把候选换回原图坐标值**（纯读） |

**关键判据：值必须工具给。** mark 存的是 `@窗口` 相对坐标，模型要的是 `@原图`；换算工具手上有、模型没有。此前模型手算（`0.135+0.35×0.15=0.188`）既多余又是错误来源。

## ② 代码落点（commit 1b5153c）

- `cogos/image_ctx/tools.py`：`coord()`、`anno_to_src()`（原 `_anno_to_src` 公开）、`FigureOp.COORD`；`COORD_BASE` 拆 `COORD_BASE_FOR_FIG`（相对 ref 对象）/ `COORD_BASE_FOR_ANNO`（相对源图）；**删 `clear_fig_block`**。
- `cogos/image_ctx/schemas.py`：`coord_schema()`（承载完整方法：`see 看清 → mark 压住目标 → adjust_mark 校准 → coord 取值`，并写"换算由程序完成、直接用返回值"）；各工具 description 统一为**块式结构**（动作 → 空行 → 契约块 → 空行 → 语义；契约块内坐标基与越界分块换行）。
- `cogos/cog_ctx/manager.py`：`_age` 只 `strip`（移消息图块），不再 `clear_fig_block`。
- 测试：`tests/image_ctx/test_p2.py`（coord + anno 寿命=FIG）、`tests/cog_ctx/test_manager.py`、`test_p3.py`。相关 66 passed。

## ③ ANNO 寿命=FIG（语义变更，YZ 拍板）

- 原：anno 生命 = 所属 FIG 图块在 K 轮窗口内，超龄即清。
- 问题：`View` 本就挂 `Source.registry` 持久存在（K 轮只决定 prompt 带不带图块），anno 却提前清——不一致，且"标完搁置几轮再读坐标"会读不到。
- 定案：**anno 寿命 = FIG**；摘图块不动 annos；显式 `clear_annos` 才清。正向副作用：重载带回 anno。
- 撤回：ANNO id 全局计数（定位键是 `(FIG,ANNO)` 组合，局部编号已够）。

## ④ 验证（端到端，2 轮）

| run | 路径 | 结果 px | 偏差 | 备注 |
|---|---|---|---|---|
| coord_1 | see→see→mark→coord | (250.3,28.9) | ~5.8px | SYSTEM 含 coord 提示 |
| coord_2 | see→see→mark→coord | (251.1,33.1) | ~4.1px | **SYSTEM 删净 coord 提示**（隔离） |

- 两轮均 13 msgs / 2 图 / 1 十字 / 4 调用；真值 `(255,32)`。
- **隔离结论**：schema 自明即可，无需 SYSTEM 提示。
- 视觉核验：十字压在『工具(T)』文字区（`coord_1/shots/view_002.png`）。

---

## 下一会话可讨论/待办

1. **rect 路径未端到端验**：coord 的 rect（中心+尺寸）只有单测，未跑真实模型"圈定区域 → coord 取 `[cx,cy,w,h]`"。
2. **coord 后的收敛/自证**：现状靠 mark 后看一眼 + coord。是否需要"标后把视野对准十字再确认"的约定？handoff-14 的 new_2 打转问题在本会话未复现（默认走对），但未系统压测。
3. **命名统一的副作用**：`load`/`view` 在文档里合并为 `see`，但 `view` 作为概念（`FIG≜(path,view)`、`view.py`、View 类）仍在——语义上"视野"与"看"是两回事，是否要在术语层进一步区分？
4. **硬不变量 vs 自学习的落点**（本会话讨论沉淀）：能写进接口/契约的不变量（坐标系、映射、ID 规则）就别让模型学；只有判断类（何时放大、窗口多大）才值得"学了再总结"，且总结要绑方法、留迹、可复验。coord 是"不变量进 schema"的一个范例。
5. **探针 SYSTEM 为隔离版**（已删 coord 提示）——保留作"schema 自足"的验证基线；若要恢复提示可加回。
6. **lm-service**：调试日志（`_count_images`/`messages=N images=M`）已由 YZ 移除并提交；后台跑 server 仍需 `python3.11 -u`。

---

## 运行

- **LM server（会话级，需重开；`-u` 看日志）**：`cd /home/zhengyp/work/A/cogos && python3.11 -u -m cogos.lm_service.cli server --port 11434`；KEY `ik_REDACTED`；鉴权头 `X-Internal-Key`。
- **对话工具**：`cd /tmp/kilo/vision && python3.11 image_field_chat.py --msg '<任务>' --out <dir>`（或 `--repl` / `--resume`）。
- 测试：`cd /home/zhengyp/work/A/cogos && python3.11 -m pytest -q`（改动用例：`tests/image_ctx tests/cog_ctx`）。

---

## 关键文件

- 探针：`/tmp/kilo/vision/image_field_chat.py`（已接 coord；SYSTEM 为隔离版无 coord 提示）。验证目录 `/home/zhengyp/work/A/workspace/{coord_1,coord_2}`（raw.jsonl + crosses.jsonl + shots/）；源图 `/home/zhengyp/work/A/workspace/windows.png`（1357×764）。
- 图工具本体：`cogos/cogos/image_ctx/{tools,schemas,view,domain,render}.py`；上下文 `cogos/cogos/cog_ctx/{context,manager}.py`。
- 设计/清单：`cogos/docs/design-vision-image-fields{,-checklist,-p1-spec,-p3-spec}.md`（已同步 coord + ANNO 寿命 + 命名统一）。
- 目标真值：『工具(T)』`@全图=[0.188,0.042]`→px `(255,32)`；可点带 `225≤x≤278 且 12≤y≤38`。
- 上游取证：`handoff-vision-image-fields-14.md`；工具用法整理：`checkpoint/principle-exp/tools-usage-models.md`。
- 记忆：`locus/projects/cogos/entries/2026-09-10-cogos-coord-anno-lifetime.md`。
