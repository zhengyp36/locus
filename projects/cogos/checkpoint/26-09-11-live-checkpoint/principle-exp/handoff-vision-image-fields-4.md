# handoff｜视觉图组织/引用 设计改坐标三套化 + 建验收清单 → 待 P1 实现（09-08 晚续）

> 2026-09-08 晚（续轮）。上游：`handoff-vision-image-fields-3.md`（设计定稿 + 全文审核自洽，尚未实现）。本轮在审阅协调过程中**修正设计坐标体系**并**新建验收清单**。新会话只读本文件即可接手；**接口/细节以本体文档 `cogos/docs/design-vision-image-fields.md` 为准，验收以 `design-vision-image-fields-checklist.md` 为准**。

---

## 一句话状态

- **设计定稿且协调一致**（坐标改为**三套化**：`@窗口`/`@全图`/像素；已建**验收清单**），**尚未实现**。下一步落 `cogos/image_ctx` 原始层（P1：add_src/load/view/render，用 windows.png 验证）。

---

## 本轮改了什么（新会话必须知道）

### 1. 坐标体系重做：从"相对全图全局系"→「三套化」（这是最大变更，§5/§9-3 重写）
- **动作坐标 = `@窗口`**（窗口相对归一化）：`view`/`draw`/`move` 的 `center/size/pts` 相对**参考 FIG 的窗口框**，`0~1` 覆盖该窗口，`<0`/`>1`=窗口外偏移（即平移）。参考框由动作**显式**给定（`view` 用 `ref=FIG:<id>`、`draw`/`move` 用所属 FIG），多 FIG 并存无歧义。
- **地图 = `@全图`**（信息性）：元注解报告每 FIG 的窗口在全图的位置（`c/s` 相对全图 `orig_w×orig_h` 归一化）。模型读它做**内心地图**（我在全图哪/覆盖多大/是否到边），**不进动作接口**。
- **像素 = 内部/校验 + 尺寸报告**：`orig_w×orig_h`、实际下发位图 `w×h`；渲染、跨 FIG 计算、ground-truth 校验（如 P2 判工具是否落 `[0.188,0.042]`）用像素；模型只在元注解读尺寸。
- **为何无"全图绝对动作坐标"**：看全图 = load/view 全图（此窗口=整体 ⇒ `@窗口 ≡ @全图`），模型只在 `@窗口` 上动作，绝对化只在该处退化出现。
- 参考系**标签明文**：`@全图`（地图）/`@窗口`（动作与 anno 同帧）；措辞统一，`mark_pt` 记号改用 `m(.188,.042)`（避免 `@` 歧义）。

### 2. 新建验收清单（新会话用它自检）
- `cogos/docs/design-vision-image-fields-checklist.md`：分 P1~P4，每组【行为 MUST HAVE + 禁区 MUST NOT】，每条回指设计 § 条款 + 可验证手段（单测 / `windows.png`+vf6 探针 / A-B）。**检查两项**：① 功能完整 ② 是否偏离设计（禁区项最易被顺手加回）。

---

## 设计要点骨架（详见本体，此处只列验收时对上的不变式）

- 图 ≜ `(path, view)`；引用 = 单一 tagged token `FIG:`/`PATH:`/`ANNO:`，只抄不造。
- 无场：图散落历史、活 K 轮（默认 4 可配）、单轮恒 1 图块、无 `load_many`；`earliest_fig_turn` 单指针摘超龄；K 改大不回生、改小立即生效。
- 存储三层：`images/`（资产）/`desc/`（canonical 视图+anno，不含 note）/`cache/`（可清，指纹 `(path,window,annos)`）。
- 去重仅身份层（Source 图根）：同 path 幂等、同 `(path,window)` 同 FIG_ID；跨 path 像素相同不合并；**compile 不去重**。
- 像素一致性：下发展 `render(fig)` 窗口位图（crop+主动降采样封顶）、`detail=original`、元注解 `w×h`=实际下发；越界 view/anno 均 clamp 取有效区、不补边/平移、文字标「原→生效」+ `⚠️` 高亮（anno clamp 不报错）。
- `note` 瞬态：只在生成那轮经 `compose_figure_text` 消费、随即丢弃，不写回图/desc/缓存/域状态；回显第二人称 `你的备注:`；元信息字段短+固定序+不分隔对齐。

---

## 下一步（P1 原始层）

1. **前置（纸面，先定地基）**：定 P1 坐标换算 + clamp + 指纹公式/签名——`@窗口 → @全图` 换算（动作@窗口 + 参考 FIG 的@全图 window → 新 FIG 的@全图 Window）、view 越界 clamp 取有效区、render 指纹 `(path,window,annos)`、`add_src`/`load`/`view` 输出形状。顺带把 checklist P1 的"对照项"变"可实现规格"。
2. **落代码** `cogos/image_ctx/`：`domain.py`（Source 图根+去重表）/`view.py`（Window+换算+clamp）/`render.py`（封装 img-tool 取像素）/`tools.py`（load/view 原语）。独立模块，避与 `img_tool` 冲突。
3. **跑 P1 验收**：`windows.png`(1357×764) + vf6 复现，勾 checklist P1（行为全过 + 禁区不踩）。

---

## 运行

- 后端：`cd /home/zhengyp/work/A/cogos && python3.11 -m cogos.lm_service.cli server --port 11434`（**会话级，每新会话要重开**）。KEY `ik_REDACTED`。
- 跑 vf6：`cd /tmp/kilo/vision && python3.11 vf6.py <msg.txt> --scene windows.png --out DIR [--no-thinking]`。
- 测试需 python3.11。
- **飞书通知**：`cd /home/zhengyp/work/A/locus && python3.11 tools/feishu_notify.py "<文本>"`（依赖 python3.11 + httpx，默认 YZ）。

---

## 关键文件

- 本体（最终定稿）：`/home/zhengyp/work/A/cogos/docs/design-vision-image-fields.md`（坐标三套化已写入）
- **验收清单**：`/home/zhengyp/work/A/cogos/docs/design-vision-image-fields-checklist.md`（本轮新建）
- 上游设计：`/home/zhengyp/work/A/cogos/docs/vision-system-design.md` §4/§6/§14（原语与分辨率）
- 工具/原型：`/tmp/kilo/vision/{vf6.py, vf_tool.py, vf_box_proto.py}`、`vf6_repl_out_new/windows.png`
- 前置交接：`handoff-vision-image-fields-3.md`（设计定稿版）、`-2.md`（含 FIG/域/Source 骨架）、`handoff-vf6-rect-marker-context.md`
