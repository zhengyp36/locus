# cogos 模型面命名：模型先验准则（2026-09-28）

> **状态**：讨论定稿（YZ 同意）。准则已落设计 `../cogos/docs/design-agent-tools.md` §19；案例 `target→to` **待验、未落码**。
> 来源：toolbox 行为复跑稳定猜错参数（`entries/2026-09-28-cogos-toolbox-behaviour-probe.md`）。

## 结论：一条命名准则

**模型面命名以「模型好理解」为唯一判据**（不是机制名好看）。模型面名与机制实现名**解耦**（catalog 层，§2 契约层）；同/异名只是结果。

- **元工具事实**：`toolbox` 是单一元工具，能力参数名**不在 tool schema 里**（`args` 自由 object，toolbox.py:59-62）→ 模型**看不到**参数名、只能凭先验猜。故"猜"是**结构性必然**，不是模型笨。
- **先验准则**：**当模型对同一处稳定地猜成同一个合理值**，应把**模型面名**对齐该先验——让首猜即中（省一次往返）。
- **三闸**（全满足才改，否则补 help/描述而非改名）：① **一致性**＝稳定猜同一个（非随机错、可 reps 复现）；② **合理性**＝该值领域通用、不引入歧义、不破坏跨能力一致；③ **证据**＝reps 采样确认分布（n≥10）。
- **整族一致 > 单点迎合**：同族能力要改一起改（只改一处 = 制造新的不一致）。
- **别名映射**：模型面用先验名、映射到 impl（模型面 `to` → impl `target`），**impl 不改**。

## 案例：`target` → `to`（待验）

- 依据：真实模型 **16/16 + 10/10** 稳定猜 `to`（应 `target`）。
- `target` 是通信族统一用词：`communication.message.send`（catalog.py:257）/ `communication.file.send`（:268），impl `send_msg`/`send_file` 亦用。
- 落地：**整族**改模型面为 `to`；impl 不动；catalog 映射；改后 harness 复跑验（首猜命中率↑、往返↓）。
- 注意：`to` 在本 catalog 别处另指 drag 终点（`computer.screen.act`，catalog §18），**同名不同义**须权衡。

## 边界 / 被否

- ❌ **无底线迎合模型**：模型猜的值若不领域通用/不跨能力一致（闸二），不采纳。
- ❌ **随机错当先验**：每次猜不同词 → 是描述不清/无先验，该补 help，不是改名。
- ❌ **被单一模型绑架**：先验随模型换代而变（`to` 极通用、风险低，但应记"当前模型先验"非永恒真理）。
- ❌ **拿改名掩盖描述不足**：先确认不是 schema/help 描述欠清。
- ❌ **`interrupt` 并入 `cancel`**（YZ 定）：打断前台命令 ≠ 撤销作业，语义不同。

## 命名分层原则（普适，引出）

- 模型面名**只描述能力语义、不泄漏机制实现**（同 fix 3 删 help"绑定"行）。
- 机制名干净达意可同名（`read`/`send`/`cancel`），带实现气味须换（`terminal_cancel`/`send_msg`）。
- 组织按**能力心智模型**（command/file/screen/web/message），非代码分包（terminal/phone/timer）。
- 有 job 句柄的取消统一 `cancel`；归类按发起面。

## 锚点

- 设计：`../cogos/docs/design-agent-tools.md` §19（新增）· §2 契约层
- 行为证据：`entries/2026-09-28-cogos-toolbox-behaviour-probe.md`
- 修复（可读错误，使猜错便宜）：`entries/2026-09-28-cogos-toolbox-fix.md`
