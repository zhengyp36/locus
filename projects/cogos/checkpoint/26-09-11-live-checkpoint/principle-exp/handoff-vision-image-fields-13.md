# handoff｜对话式图工具落地（see+mark 族接模型）+ 点击『工具(T)』真实命中与非命中取证（09-09 晚）

> 2026-09-09 晚。上游：`handoff-vision-image-fields-10.md`（点击命中标准 + 我评审闭环，命中率 62.5%）→ `-11.md`（图说明自注解定案）→ `-12-tools.md`（图工具重构 see+mark 族实施清单）。
> 本会话：① 落地 handoff-12 遗留的"schema 接入并暴露给模型 + 验证契约自明"；② 搭**对话式图工具** `image_field_chat.py`；③ 用真实模型点击『工具(T)』取证——**命中样本（<10px）与非命中样本（test_2 偏右 78px）并存**，并精确定位非命中的根因。
> 新会话只读本文件可接手。

---

## 一句话状态

- **对话工具已落地并自验**：`image_field_chat.py`（非仓库，`/tmp/kilo/vision/`），REPL 对话式，模型直调 cogos `see/mark/adjust_mark/unmark`（走 `figure_tool_schemas()` 契约自明），K=4 图上下文本地保留（`FigContextManager`）。
- **真实模型点击『工具(T)』取证**：
  - 命中样本（ifc_t3/t4）：模型 `see 放大菜单栏 → mark 十字 → 自评 → adjust_mark 微调 → 命中`，最终十字源图 px 稳定 <10px（如 262,33）。
  - **非命中样本（test_2）**：模型标 `@窗口(0.245,0.055)`（ref=FIG:1000 全图）→ 源图 px(332,42)，**偏右 78px，落在『窗口(W)』→ 未命中**。
- **根因精确锁定（本会话价值）**：非命中不是"基准乱"，是**模型目测本身偏了**——它在子图 FIG:1013 里把『工具(T)』看成子图横向 49%（真实 38%），**目测向右偏 ~11% 子图宽 ≈ 77px**，且**标完没自证（没再 see 核对）就收口**。

---

## 对话工具：`image_field_chat.py`（落地 handoff-12 遗留）

形态（对应 handoff-12 的"schema 接入 + 契约自明验证"）：
- **REPL / --msg 单轮**，`--repl` 交互、`--resume` 重开会话（回放历史）；`--out` 落盘；`--thinking` 默认关。
- 模型用 cogos `figure_tool_schemas()`（4 工具 schema），框架自拼 schema 传给 `LmClient.chat(tools=...)`，走**结构化 tool_calls**（非文本 JSON）。
- 工具执行用 `image_ctx` 的 `see/mark/adjust_mark/unmark`，返回 `Block{text,image,image_size}`；tool 消息回灌元信息文字（`fm.text`）、图经 user 消息回灌。
- **K=4 图上下文**：用 `FigContextManager`（老化/摘图块/清 annos），不自己拼消息。
- **每步产物图落盘** `--out/{domain/cache, shots}`；**十字落点记录** `--out/crosses.jsonl`（fig/window/cross_rel/src_norm/src_px）。
- 消息持久化 `--out/raw.jsonl`（发给模型的完整消息序列），`--resume` 重放。

### 关键修复（本会话踩的坑，别回退）
1. **多 tool_calls 时 tool 必须连续**：OpenAI/DeepSeek 协议要求 `assistant(tool_calls)` 之后所有 `tool` 消息**相邻**，中间不可插 user 观察图。之前把"观察图 user"插在 tool 之间 → `invalid_request: insufficient tool messages following tool_calls`。修复：**先执行收集所有 tc → 连推所有 tool → 再推各观察图 user**。
2. **重放协议安全**：`to_lm_messages` 对历史做重排（把被 user 穿插的 tool 归拢、observe 移到 tool 之后），旧的不平衡会话也能合规重放。
3. **打印不截断**：模型回复、工具元信息全文打印（去掉了 `[:400]/[:140]`）。

---

## 点击『工具(T)』取证

观测基准（沿用 handoff-10 的点击命中标准）：
- 真值『工具(T)』`@全图=[0.188,0.042]` → 像素靶 `(255.1,32.1)`（windows.png 1357×764）。
- 可点归属带（不偏邻居）：`225≤x≤278 且 12≤y≤38` 命中；文字块带 `234≤x≤270`。
- **运行时程序不喂命中/反馈给模型**（模型视觉自证收口）；crosses.jsonl 供事后评分。

### 命中样本（ifc_t3 / ifc_t4）
模型走 `see(开全图) → see(放大菜单) → mark → 自评 → adjust_mark → see(核对) → 收口`。最终十字稳定命中，源图 px ~(262,33)/(265,34)，距靶 <10px，落在文字块内。模型自述能反推 `原图x = 视野中心 + (读-0.5)*视野宽`。

### 非命中样本（test_2）—— 根因分析（重点）

模型轨迹：**先花十几轮乱看 Xftp 细节（文件列表/传输队列/任务栏）**，最后几轮才看菜单：
```
see FIG:1000(全图)
  → ...探索 Xftp 其余区域(14+ 次 see, 与任务无关)...
  → see FIG:1013 窗口中心(0.250,0.055) size(0.500,0.039)   ← 放大菜单左半
  → mark ref=FIG:1000(全图) center=(0.245,0.055)            ← 标【全图】ref
  → 收口(只文字复述"位于命令(C)与窗口(W)之间", 没再 see 核对)
```

**根因（精确）**：它在子图 FIG:1013（覆盖全图 x∈[0,0.5], y∈[0.0355,0.0745]，实际位图 678×30 菜单横条）里目测『工具(T)』：
- 该子图内『工具(T)』真实 @窗口 = **(0.376, 0.167)**。
- 模型报的 `(0.245,0.055)` 反推回"它眼里的子图坐标" = **(0.490, 0.500)**。
- 即：它把『工具(T)』看成子图**横向 49%、纵向 50%（正中）**，真实是 **38%、17%** → **目测向右偏 ~11% 子图宽 ≈ 77px**（子图宽 678 → 0.114×678=77px；换算全图即 0.057 归一化）。

**为什么判定为"目测偏"而非"基准乱"**：
- 模型 mark 的 ref 明确是 `FIG:1000`（全图），它报的 `(0.245,0.055)` 也是"全图量级"（y≈顶部菜单、x≈左中）——**基准其实没乱，ref=全图、与值自洽**。
- 但它**没把子图里的目测换算到全图**，直接把子图目测印象当全图值转手输出；且这个印象本身就偏了（0.245 vs 真 0.188）。
- 换一种说法：就算它 ref 指向当前子图（FIG:1013），用它给的 `(0.245,0.055)` 也会得到源图 px(166,29)——**同样偏 89px，只是方向反（偏左『命令/查看』）**。所以问题不在 ref 指向，在**坐标值本身不准 + 没换算 + 没自证**。

**根因归纳**：
1. 模型在密集菜单横条（每个菜单项仅十几像素宽）目测单项位置，**误差可达 ~11% 子图宽**——密集小目标视觉估读天然差。
2. 模型**没做"子图@窗口 → 全图"换算**，把子图目测印象直接当全图坐标输出（ref 指全图但值是从子图抄的）。
3. 模型**标完没 see 放大核对就收口**（只文字复述），缺"自证贴没贴住"。

**对照命中样本为何准**：命中样本标后会 `see(放大核对) + adjust_mark(微调)`，把估读误差压到 <10px；且其 mark 的 ref/值换算自洽。→ **关键差异不在模型能力，在"是否做了换算 + 是否自证收口"**。

---

## 下一个攻坚点（点击『工具(T)』100%）

方向（对应 handoff-10 的攻坚点 + 本会话实证）：
1. **治"密集项目测偏"**：模型对密集菜单横条的视觉估读天然差（~11% 宽）。需靠**放大到单项目可辨 + 换算**，而非指望它一次估准。
2. **强制"子图内定位 + 程序换算"**：目前模型 mark 时 ref 由它选（可用全图也可用子图）。链路关键在：模型在看到子图后，mark 的 `center` 必须**明确是相对哪个 ref**，且**自己算换算**。可选：约束"mark 前先 see 把目标放大到清晰，mark 时 ref 指向当前子图"。
3. **强制标后自证**：命中样本的有效动作是"标完再 see 放大核对，偏则 adjust_mark"。可考虑逐步把"标后必须 see 核对一次"变为约定（目前靠 SYSTEM 简述 + 模型自觉，不强制）。

> 注意：**评审策略本轮没上**。停点 = 模型视觉自证收口（它自认"标到了"就停），正确性靠模型自证 + 事后 crosses.jsonl 评分，运行时程序不喂命中反馈。若后续要 100%，再评估是否需要轻量强制核对。

---

## 运行

- **LM server（会话级，新会话需重开）**：`cd /home/zhengyp/work/A/cogos && python3.11 -m cogos.lm_service.cli server --port 11434`；KEY `ik_REDACTED`。
- **对话工具**：`cd /tmp/kilo/vision && python3.11 image_field_chat.py --repl --out <dir>`（或 `--msg "..."` 单轮 / `--resume` 重开）。
- 测试：`cd /home/zhengyp/work/A/cogos && python3.11 -m pytest -q`（1002 passed 基线）。

---

## 关键文件

- 本会话探针：`/tmp/kilo/vision/image_field_chat.py`（NEW，非仓库）；验证目录 `/tmp/kilo/vision/{ifc_t2,ifc_t3,ifc_t4}`、`/home/zhengyp/work/A/workspace/test_1`、`test_2`（含 raw.jsonl + crosses.jsonl）。
- 图工具本体（重构后）：`cogos/cogos/image_ctx/{tools,view,schemas,render,domain}.py`；上下文：`cogos/cogos/cog_ctx/{context,manager}.py`；schema：`image_ctx/schemas.py::figure_tool_schemas()`。
- LM client：`cogos/cogos/lm_service/client.py`、`providers/base.py`（`assemble_tools`/`assemble_tool_messages`/`parse_response`，内部形式 tool_calls）。
- 工具用法整理（各探针对比）：`checkpoint/principle-exp/tools-usage-models.md`。
- 目标真值：『工具(T)』`@全图=[0.188,0.042]` → 像素靶 `(255.1,32.1)`（windows.png 1357×764）。
