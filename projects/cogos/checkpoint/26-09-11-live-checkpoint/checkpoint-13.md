# checkpoint-13 — 命名层级修正：引入 cog-object（与 cog-func 同层）

接 checkpoint-3（范式/命名）。讨论"对象"的地位，修正命名层级体系：把"对象"升为与 cog-func 同层的封装范式。定锚。

## 当前问题

现有三层 cog-unit / cog-func / cog-actor 中，"对象"（ImageObj/IntentObj）被当"数据载体"（正交维度），无独立层级。审视认为应引入 **cog-object** 作为能力封装层的一种范式。

## 关键结论 / 决策

### 1. 修正后的层级

```
cog-unit         原子动作（cu，推理最小单元）
  │
[能力封装层]  ← 两种并列范式，对应编程史"函数/类"
  cog-func      过程式：用函数组织流程（调 cu 做理解，无状态）
  cog-object    对象式：状态 + 数据 + 行为（方法）绑定成一体的主动封装
  │
cog-actor       主体（谁）：实例化/组织 func 与 object，agent = 对外实例
```

### 2. cog-object = 主动封装，非数据容器

- 弱化版（旧）：ImageObj 只是被 cog-func 操作、被 cog-actor 持有的数据载体。
- 强化版（新，定锚）：状态 + 方法绑在一起，对象自含行为（如 `ImageObj.focus()` / `.extract()` / `.summarize()`），方法是 cog-func / cog-unit 的组合，挂到对象上。
- 这就是面向对象的封装：逻辑不再靠外部函数操作对象，而是对象自己拥有方法；函数成为对象的成员。

### 3. 历史修正（checkpoint-3 呼应）

- checkpoint-3 曾把"对象"落点放 **cog-actor（未来函数式轻对象）**——modify：cog-object 承担"对象"概念，cog-actor 明确为**纯主体（谁）**，用它组织 func/object，不再让 actor 兼当"对象层"。

### 4. 实例化命名

- cog-object 是**范式**；`xxxObj`（ImageObj / IntentObj）是**具体落地类型/实例**。

### 5. 选 func 还是 object（判据 = checkpoint-7 对象化）

- 一次性无状态流程 → cog-func（纯函数）。
- 跨轮共享 / 有缓存 / 行为绑定状态 → cog-object。
- 即 checkpoint-7 对象化判据与命名体系合并成立，定锚。

## 遗留 / 未定

- cog-object 内部方法用 cog-func/cog-unit 组合的细化（如 ImageObj 的 focus/extract 方法如何复用 cog-func locate）——实现时定。
- 命名体系既已定锚，后续文档/本体语言统一用新层级。
