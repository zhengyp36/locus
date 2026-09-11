# checkpoint-14 — ImageObj 实现定稿：cog-object 方法集（含摘要内嵌修正）

接 checkpoint-12/13。基于"ImageTool 收敛为 ImageObj（cog-object）"给出实现定稿，并修正"摘要是独立方法"。

## 当前问题

ImageObj（cog-object）暴露哪些方法；摘要是否独立方法。

## 关键结论 / 决策

### 1. ImageObj = cog-object（接 checkpoint-13）

- 动作 = 对象**自带方法**，不是外面 an cog-func 操作数据对象。
- 方法：`open` / `focus` / `取子图`（+ 内部定位 locate 子 cog-func）。

### 2. 摘要内嵌，非独立方法（本轮修正）

- **摘要是"输出图的伴随产物"**：任何产生输出图的动作（open/focus/取子图）都**自动完成摘要**，内嵌在动作里，作固有副作用，不作可单独调用的方法。
- 摘要 = 内部一次**描述性 cu**（定位那步已看 region，零边际成本，checkpoint-8）。
- 同一对象再次引用时摘要不变（走缓存/印象），不重生成。
- 因此不会出现"图 + 另一次独立摘要动作"的割裂——主 LLM 拿到的永远是**图+摘要一体结果包**（checkpoint-12）。

### 3. 实现布局

```
主 LLM ──意图工具(唯一入口)──▶ ImageObj（cog-object）
│                              ├─ 方法: open / focus / 取子图
│                              ├─ 状态: 图链(内容图+视野+关系) 摘要 印象+旁注 依据信号 生命周期
│                              └─ 内部: img_tool 原语 + cog_runtime.cu(定位/摘要)
信息隔离：主 LLM 只收结果包(图+摘要+依据)，定位过程不可见
```

### 4. 方法动作

- `open`：img-tool `info`(全图) → 建根（全景锚 + 首视野），自动带全景摘要。
- `focus`：语义方向 → 内部 lombok子 locate 落全图 region → `extract` → 建子视图，自动带该视图摘要。
- `取子图`：某 region 固化为可复用/加旁注的独立节点（挂 children），自动带摘要。

## 遗留 / 未定

- 关系树 vs 全图坐标呈现（checkpoint-12）——待拍板。
- locate 是否抽成共用 cog-func 模板（checkpoint-2；先特化后抽象）。
- annotate/画线是否保留（关系树方案下弱化）。
- 图池/缓存/生命周期（checkpoint-7/8）——后置。
- 落地顺序/验收：①ImageObj 状态模型 → ②方法（FakeLmClient + Pillow 造图单测）→ ③接意图工具 → ④后置缓存；`python3.11 -m pytest`，真实 deepseek 看图 e2e 闭环。
