# handoff｜视觉图组织/引用 → P1 原始层 规格已定稿 + 两拍板 → 待实现（09-08 晚收尾）

> 2026-09-08 晚（本会话收口）。上游：`handoff-vision-image-fields-4.md`（设计定稿 + 坐标三套化 + 建验收清单）。**本会话完成了 P1 纸张步（实现规格）、subagent 检视修复、以及两项设计决策（YZ 拍板）**。新会话只读本文件即可接手；**接口/细节以本体 `design-vision-image-fields.md` 为准，验收以 `design-vision-image-fields-checklist.md` 为准，P1 落码以 `design-vision-image-fields-p1-spec.md` 为准**。

---

## 一句话状态

- 设计定稿协调一致（坐标三套化）。**P1 原始层实现规格已写好（含坐标换算/clamp/指纹/签名+输出形状），经 subagent 检视并修复 2 高危；两项设计决策已由 YZ 拍板**。**下一步 = 落 `cogos/image_ctx` 原始层（add_src/load/view/render，用 windows.png 验证），直接按 P1 规格实现，无需再走纸张步。**

---

## 本会话产出（新会话必须知道）

### 1. P1 规格文档（本会话核心交付）
`cogos/docs/design-vision-image-fields-p1-spec.md` 定义：
- **坐标模型**：单一真源=源图像素矩形；`@全图 Window`(存态 center/size) ↔ 像素矩形；`@窗口`(动作态)。
- **坐标换算** `view_to_window(ref_fig, center, size, shape)`：`@窗口` → 新 FIG 的 `@全图 Window`。
- **view 越界 clamp**：方案1 只取有效区、不补边/平移、标注原→生效；退化(完全出界)落到边界对称 2×2。
- **render 指纹** `(path, window, annos)`：`window_key`(=去重键) + path + annos，逐点拍平序列化 sha1。
- **add_src / load / view / render 签名 + 消息块(Block/meta_annotation) 输出形状**，以及 img_tool 对接（region 归一化差异 + max_dim 封顶 + budget 注意）。

### 2. subagent 检视 + 已修（实现时别再踩）
- **高危（已修）**：指纹对 `pts(list[list])` 直接 `:.4f` → TypeError（改逐点拍平序列化）；clamp 退化 2×2 在右/下边沿变 0 宽（改对称 2×2，恒非零）。
- 中低（已修）：元注解 `:.2f`→`:.3f`（对齐设计 `c(.188,.042)`，避免重载锚粗~7px）；`view_to_window` 签名与调用统一；`window_key` 显式定义且与指纹窗键同源。
- 核验：坐标换算公式正确（windows.png 1357×764 实例：`@窗口` center=[.188,.042] → `@全图` 精确回 center；size 数值差宽高比属预期）。

### 3. YZ 已拍板（关键，勿再当作 open 项）
- **§7-1 `load` 产新 FIG**：全图也是普通 FIG（整幅窗口），与 sub-FIG 同一 dedup——按 `(path, 全图窗口)` 恒定 FIG_ID，**首次 load 建、再次 load 复用**（恒同 `src_fig`）；与 P4「同 path 幂等」不冲突；"新"=首次不存在才建。`load` 与 `view` 对称，均走 dedup。
- **§7-2 `@窗口` size 基准 = 方案 A**：center、size **均分轴 over 参考 FIG 窗口盒**（`1,1`=整盒），**不取短边倍数**。即 size 是"当前参考窗口的比例"。接受 `@窗口≡@全图` 仅**对象级**等价（size 数值不等，不影响正确性）。理由：单一基准、贴"0~1 覆盖该窗口"、B 的"短边随 view 变"是移动基准心智负担且收益不可见。
- （此前已定，勿改）无场、无 load_many、compile 无去重、图去重仅身份层、note 瞬态。

---

## 设计要点骨架（不变式，详见本体）

- 图 ≜ `(path, view)`；引用 = 单一 tagged token `FIG:`/`PATH:`/`ANNO:`，只抄不造。
- 无场：图块散落历史、活 K 轮（默认 4 可配）、单轮恒 1 图块、无 load_many；`earliest_fig_turn` 单指针摘超龄；K 改大不回生、改小立即生效。
- 存储三层：`images/`(资产)/`desc/`(canonical，不含 note)/`cache/`(可清，指纹 `(path,window,annos)`)。
- 去重仅身份层（Source 图根）：同 path 幂等、同 `(path,window)` 同 FIG_ID；跨 path 像素相同不合并；compile 不去重。
- 像素一致性：下发 `render(fig)` 窗口位图（crop+主动降采样封顶）、`detail=original`、元注解 `w×h`=实际下发；越界 view/anno 均可 clamp 取有效区、不补边/平移、文字标原→生效 + `> ⚠️`。
- `note` 瞬态：生成那轮经 `compose_figure_text` 消费随即丢弃；回显第二人称 `你的备注:`；元信息短+固定序+不分隔对齐。

---

## 下一步（落代码）

1. 落 `cogos/image_ctx/`：`domain.py`(域+Source 图根/去重表) / `view.py`(Window+换算+clamp) / `render.py`(薄封装 img_tool 取像素+缓存) / `tools.py`(load/view 原语)。**按 `design-vision-image-fields-p1-spec.md` 实现**，独立模块、避与 img_tool 冲突。
2. 跑 P1 验收：`windows.png`(1357×764) + vf6 复现，勾 `design-vision-image-fields-checklist.md` P1（行为全过 + 禁区不踩）；用真值 `[0.188,0.042]` 标定 `@窗口≡@全图` 换算（§8 残留探针）。
3. 落地时把 checklist P1 的"对照项"逐条勾，重点：坐标换算/clamp/指纹/像素一致性。

---

## 运行

- 后端：`cd /home/zhengyp/work/A/cogos && python3.11 -m cogos.lm_service.cli server --port 11434`（**会话级，每新会话要重开**）。KEY `ik_REDACTED`。
- 跑 vf6：`cd /tmp/kilo/vision && python3.11 vf6.py <msg.txt> --scene windows.png --out DIR [--no-thinking]`。
- 测试需 python3.11。
- 飞书通知：`cd /home/zhengyp/work/A/locus && python3.11 tools/feishu_notify.py "<文本>"`（默认 YZ）。

---

## 遗留 / 待办（非阻塞实现，落地后或随手处理）

- **设计本体 doc §6 示例 `@全图 c(.50,.50) s(1.0,1.0)` 与 §2/§9-3「size 按短边」冲突**：按短边归一全图应 `s(1.78,1.0)`（1357×764）。规格 §5.2 已用正确短边口径，建议后续把设计 §6 例值改成短边口径，避免实现混淆。
- §7-3 `detail=original`（禁厂商二次 resize）落点：P1 靠**主动降采样**保像素一致性，detail 项归 P2+/请求构造层；P1 不接请求编排。
- §7-4 封顶 `max_dim`：可配置，默认 `IMGTOOL_DEFAULT_MAX_DIM=800`（`img_tool.DEFAULT_MAX_DIM`）。
- §7-5 换算精度/指纹精度/`estimate_peak`(全幅预算对小口大图是否误拒)——落地时实测，见 checklist §8。
- cocos `image_ctx` 尚未创建（将从零建）。

---

## 关键文件

- 本体（最终定稿）：`/home/zhengyp/work/A/cogos/docs/design-vision-image-fields.md`
- 验收清单：`/home/zhengyp/work/A/cogos/docs/design-vision-image-fields-checklist.md`
- **P1 实现规格（本会话交付，落码依据）**：`/home/zhengyp/work/A/cogos/docs/design-vision-image-fields-p1-spec.md`
- 上游设计：`/home/zhengyp/work/A/cogos/docs/vision-system-design.md` §4/§6/§14
- 工具/原型：`/tmp/kilo/vision/{vf6.py, vf_tool.py, vf_box_proto.py}`、`vf6_repl_out_new/windows.png`
- 前置交接：`handoff-vision-image-fields-4.md`（设计定稿版）、`-3.md`、`-2.md`
