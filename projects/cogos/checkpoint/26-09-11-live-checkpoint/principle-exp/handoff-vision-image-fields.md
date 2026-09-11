# handoff｜视觉图的视图/域/场设计定稿 → 落地 vf6（09-08 中午）

> 2026-09-08。上游：`handoff-vf6-rect-marker-context.md`（GUI 点击/矩形十字/上下文重设计）。本会话把「图如何落到上下文」收敛成**设计定稿**并写入本体 `cogos/docs/design-vision-image-fields.md`。
> 新会话只读本文件即可接手；locus 记忆见 `projects/cogos/entries/2026-09-08-cogos-vision-image-fields.md`（含完整论证脉络）。

---

## 一句话状态

- **设计已定稿**（视图/域/场三元组），**尚未实现**。下一步 = 把这套接口落进 vf6 的 `run_step` 下一版。
- 核心跃迁：**主图/子图边界对模型不存在**（图为自足视图：窗口+全局范围）；坐标系**统一根源图归一化**（模型无换算）；上下文 **文字永续含重载锚 + 图瞬时**。

---

## 一、设计要点（详见本体文档）

### 三元组
- **图 = 视图（View）**：对模型 = `{窗口图 + 全局范围(W,H)}`，自足；主/子只是程序内锚（源图+parent+window）。
- **域（Domain）**：图资源容器（images持久/cache可清/desc canonical）；归属+共享/隔离边界。
- **场（Field）**：视图容器。`load_xxx` 是**唯一切场入口**。
  - 观察场 = 视图**轨迹序列**（view 追加，无在场主图，首项即打开那张）。
  - 比较场 = 视图**并列集合**（view 替换某位；≤3，超截断标注前3）。

### 坐标系（模型无换算关键）
- 所有视图共用**根源图归一化坐标系**（`global_w/global_h`）；`view`/`draw` 的 center/size 恒相对它。
- 坐标**可负/可 >1**（移到图外任意方向）；越界 → 返回边界窗口图 + 标注「原坐标→实际生效坐标」。

### 上下文注入
- 图只挂产生它的那轮（图瞬时）；历史消息**天然文字**（**砍掉"降级文字"——冗余**）。
- **文字 = 语义描述 + 重载锚**（fig_ref+全局范围+窗口）；模型丢图可从文字锚 `load_xxx`/`view` 拿回。
- 观察场轨迹 = 历史消息序列本身；窗口（历史条数/摘要化）控上下文长度，与图无关；摘要**保留含锚一句**。
- 每轮顶部**薄状态行**标「当前场+当前视图+最新窗口」（防 load 被裁丢场信息）。

### 图消息规范
- 图操作返回 = 成对 text/image；text 拆**程序事实 + 模型批注(note)**。
- 程序事实含：fig_ref(重载锚)/全局尺寸/窗口参数/越界标注/继承关系/场级(比较场几张+截断未加载)。
- **场只 load 那轮完整声明**；view/draw 不重复场类型（靠薄状态行常驻）。
- 模型批注：无坐标→`figure.text`；有坐标(draw)→`figure.annos`。互补不破坏图。

### 接口（模型可调哑原语；域为隐式上下文，不进协议）
```
load_view_field(ref, *, note="") -> 消息块
load_compare_field([{ref,note},...]) -> 消息块      # ≤3,超截断
view(ref, center, size, shape="rect", *, mark=True, mark_pt=None, note="") -> 消息块
draw(fig_ref, kind, pts, *, id=None, label=None, color=None, note="") -> anno
move(fig_ref, anno_id, pts) -> anno
```

### 去重
- 源图不去重（即使像素相同）；子视图按 `(parent,center,shape)` 去重（建议含 size），命中=防复读信号 `dup_from`。

---

## 二、下一步落地（按优先序）

1. **原始层**：`add_src` / `load_view_field` / `view` / `render`(+cache) —— 让图能组织、复现当前 vf6 能力（用 windows.png 验证）。
2. **定位**：`draw` / `move` / `clear_annos` —— GUI 点击坐标刚需（目标「工具(T)」真值 [0.188,0.042]）。
3. **上下文**：`compile`（文字永续 + 图瞬时 + 薄状态行 + 重载锚）—— 替代 build_vision。
4. `load_compare_field` / 去重 / 历史条数窗口 —— 后置。

### 落地时的关键实现点
- **统一坐标系**：`view`/`draw` 的 center/size 相对根源图归一化；越界/负值 clamp + 返回「原坐标→实际坐标」文字。
- **render 是唯一碰位图/缓存点**；缓存键 = `(parent+window+annos+源码md5)`；annos 变即失效。
- **程序事实文字要含重载锚**（fig_ref+全局+窗口），否则"丢图拿不回"。
- **薄状态行**常驻当前场，如 `当前场: 观察场 · 视图 image_1 (1357×764) · 最新 view#13`。
- 不带"降级文字"、不重复罗列旧视图文字（历史消息已在承载）。

### 后端/运行（沿用）
- 后端：`cd /home/zhengyp/work/A/cogos && python3.11 -m cogos.lm_service.cli server --port 11434`（**会话级，每新会话要重开**）。KEY `ik_REDACTED`。
- 跑 vf6：`cd /tmp/kilo/vision && python3.11 vf6.py <msg.txt> --scene windows.png --out DIR [--no-thinking]`。
- 跑测试需 python3.11。

---

## 三、关键文件

- 本体（设计定稿）：`/home/zhengyp/work/A/cogos/docs/design-vision-image-fields.md`
- 上游设计：`/home/zhengyp/work/A/cogos/docs/vision-system-design.md`（§4/§6/§14）
- 工具/原型：`/tmp/kilo/vision/{vf6.py, vf_tool.py, vf_box_proto.py}`、`vf6_repl_out_new/windows.png`（1357×764）
- 前置交接：`handoff-vf6-rect-marker-context.md`、`handoff-read-precision-context.md`
- locus 记忆：`projects/cogos/entries/2026-09-08-cogos-vision-image-fields.md`

---

## 四、待确认（可后定）

① `size` 是否入子视图去重键（建议含）；② 观察场历史条数窗口默认 K（可配，摘要保留含锚一句）。这两项拍板即可开跑；不影响原始层落地。
