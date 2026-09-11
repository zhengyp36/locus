# 2026-09-10 cogos：coord 求解原图坐标 + ANNO 寿命=FIG

上承 `handoff-vision-image-fields-14.md`（图工具对话探针 `image_field_chat.py` + 点击『工具(T)』取证；根因=模型目测偏+没换算+没自证）。

## 命题与结论主线

模型要的是**目标在原图的坐标值**（远程控制要拿去点按钮），不是"图上有个十字"。因此把图工具重新定位为：

- `see` = 看清（开图 / 调视野）；
- `mark` / `adjust_mark` = 点出并校准候选（`cross` 单点 / `rect` 区域）；
- `unmark` = 删；
- **`coord` = 把候选换回原图坐标值**（纯读）。

关键判断：**坐标值必须由工具给**——mark 存的是 `@窗口` 相对坐标（相对所属 FIG 窗口），模型要的 `@原图` 值需要 `win_c − win_s/2 + u×win_s` 换算，这个换算工具手上有、模型没有。之前模型自己手算（`0.135+0.35×0.15=0.188`）既是多余又是错误来源。

## 实现（commit 1b5153c）

- `image_ctx/tools.py`：
  - 新增 `coord(domain, fig_ref, anno_id, *, remark="")`：纯读、不渲染、不产图块。返回**原图路径（全局稳定身份）+ 形状 + `@原图` 坐标**（cross→`[x,y]`；rect→`[cx,cy,w,h]`，归一化 + 像素）。
  - `anno_to_src(fig, a)`（原 `_anno_to_src` 提公开）：`@窗口→@原图` 换算单点，`coord` 与探针评分 `record_cross` 共用，消除双份逻辑漂移。
  - `FigureOp.COORD`；`COORD_BASE` 拆 `COORD_BASE_FOR_FIG`（相对 ref 对象）/ `COORD_BASE_FOR_ANNO`（相对源图）。
  - **移除 `clear_fig_block`**：`cog_ctx/manager.py` 摘超龄图块只 `strip`（移消息图块），**不再清 annos**。
- `image_ctx/schemas.py`：新增 `coord_schema()`，并把各工具 description 统一为**见式块结构**（动作 → 空行 → 契约块 → 空行 → 语义）。coord 描述承载完整方法（`see 看清 → mark 压住 → adjust_mark 校准 → coord 取值`，并说明"换算由程序完成、直接用返回值"）。
- 测试：`test_p2.py`（coord + anno 寿命=FIG）、`test_manager.py`、`test_p3.py` 更新；全量相关 66 passed。

## ANNO 寿命 = FIG（关键语义变更）

- 原设计：anno 生命 = 所属 FIG 图块在 K 轮窗口内，超龄即 `clear_fig_block` 清空。
- 问题：FIG 对象本就持久存在（挂 `Source.registry`，K 轮只决定"prompt 带不带图块"），anno 却被人为提前清——不一致，且造成"标完搁置几轮再读坐标就读不到"。
- 定案（YZ）：**ANNO 寿命 = FIG 寿命**；摘超龄图块只移消息图块、不动 annos；要清走显式 `clear_annos`。副作用（正向）：重载同 `(path,window)` 的 FIG **带回**既有 anno。
- 未做：ANNO id 全局计数（撤回——定位键是 `(FIG, ANNO)` 组合，局部编号已够）。

## 验证（端到端，2 轮均命中）

- `coord_1`（SYSTEM 含 coord 提示）：`see 全图 → see 放大(FIG:1001) → mark(局部图) → coord`；13 msgs / 2 图 / 1 十字 / 4 调用；落点 `@原图 (0.1845,0.0378)` = px `(250.3,28.9)` vs 真值 `(255,32)` → **命中**（偏差 ~5.8px，可点带 `225≤x≤278 且 12≤y≤38`）。
- `coord_2`（**删掉 SYSTEM 一切 coord 提示**做隔离）：同样路径，px `(251.1,33.1)` → **命中**（偏差 ~4.1px）。
- **结论**：把方法写进 coord 的 schema description 即可让模型默认走对，**不依赖 SYSTEM 提示**（契约自明成立）；无手算、无"回全图自我怀疑"打转。对照 handoff-14：new_2 绕 91 条、new_1 非命中，本次与最佳单次样本 new_4(后) 同级且无需人提示。

## 文档同步 + 命名统一（commit 4555050）

- `design-vision-image-fields.md` / `-checklist.md` / `-p1-spec.md` / `-p3-spec.md`：ANNO 寿命=FIG、`clear_fig_block` 废除、coord 落点（§9-9）、接口面更正。
- **工具命名统一**：文档旧设计名 `load`/`view`/`draw`/`move`/`delete_anno` → 代码名 `see`/`mark`/`adjust_mark`/`unmark`（`load`+`view` 合并为 `see`；p1-spec §5.3+§5.4 合并、小节重排）。保留概念 `view`（`FIG≜(path,view)`、`view.py`）与禁用历史名（`load_many` 等）。

## 提交

- `1b5153c` feat(image-ctx): coord + ANNO lifetime=FIG
- `4555050` docs(vision): sync + unify naming
- `f12d1f0` chore(lm-service): 移除调试图数日志（YZ 清）

## 锚点

- 探针：`/tmp/kilo/vision/image_field_chat.py`（已接 coord，SYSTEM 为隔离版无 coord 提示）
- 验证目录：`/home/zhengyp/work/A/workspace/{coord_1,coord_2}`（raw.jsonl + crosses.jsonl + shots/）
- 交接：`checkpoint/principle-exp/handoff-vision-image-fields-15.md`
