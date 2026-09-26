# handoff｜交接：从 screenlab 转向"讨论方向" · 2026-09-22 #26

> ➡️ 接续 `handoff-screen-25.md`（第十二轮）。但**本轮不继续 screenlab**，而是**往上抬一层，讨论方向**。
>
> **本轮任务（YZ 定）**：**方向不预设，讨论得出**；得出后仍是活的。新会话先读素材，然后与 YZ 一起**讨论方向**。

## 一、新会话只读这些，别多读

1. **素材（先读）**：`locus/projects/cogos/entries/2026-09-22-cogos-screen-direction-material.md`
   —— 本会话固化下来的**事实 / 假设 / 作废 / 方向候选 / 未决问题**。**方向不在这里面，待讨论。**
2. 讨论若回到**整体（L1）**：`cogos/docs/design-selfdrive-agent.md`（当前总纲 / 唯一权威口径）+ `checkpoint/handoff-cogos-theory-review.md`（理论评审入口，从骨架第一拍起）。
3. 讨论若留在**工具（L3）**：`handoff-screen-18.md §5.1`（目标）+ `spec-screen-client-api.md` + `spec-screen-ledger.md`。
4. **代码**（以代码为准）：`cogos/screenlab/` @ `0670849` / tag `screenlab-freeze-2026-09-22`。

⚠️ 别读 `handoff-screen-15/16` 的目标与架构表述；`spec-screen-element-act.md` 整份作废。

## 二、纪律

- **方向不预设**：先讨论，后落；落下的方向**仍可再议**。
- **事实 / 假设分开**：事实带出处（日期 / 命令 / 代码位置）；假设显式标注；**作废即删名**。
- **定期回到素材与方向**——别一头扎进 L3 的细节（上一轮"像什么都没做"就是这么来的）。
- 一次只跑一条实验命令；改了 `screenlab/` 必须 **account-install + 重启 daemon**。
- sudo 密码只喂 stdin（`< ~/.secrets/centos.key`）；`pkill -f/pgrep -f` 注意自伤。

## 三、状态

- cogos `0670849` + tag `screenlab-freeze-2026-09-22` 已 push；工作树干净。
- locus 素材与本文档已写；**本会话未改任何产品代码**。

## 四、给新会话的第一句话

> 先读 `locus/projects/cogos/entries/2026-09-22-cogos-screen-direction-material.md`，
> 把里面的**事实 / 假设 / 作废 / 候选 / 未决问题**复述一遍给我核，
> 然后我们**讨论方向**——不要预设方向，也不要急着动手。
