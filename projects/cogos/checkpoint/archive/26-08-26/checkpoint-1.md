# checkpoint-1 — cogos 通信收尾 + 回归整体系统设计

## 当前问题

cogos 通信层已基本可用，告一段落；回归 cogos 整体智能系统设计。三件事的推进方式正在讨论，未定。

## 已做修改（locus 记忆层）

- `projects/cogos/current.md`：2A + phone-term 真机验证标注完成，"未决"区清空移除。
- `projects/cogos/ISSUES.md`：load_bot/AccountRef.ensure 分层错位入"遗留（待处理）"；2A 真机验证标注已完成。
- `projects/cogos/CHANGELOG.md`：追加 08-24 两项真机验证收尾记录。

## 讨论内容

1. YZ 提出三件事：①整理通信记忆（最小印象摘要：agent 靠什么工具与 agent/真人交流）②转向 agent-study 加载既有内容 ③开始智能系统设计。
2. 讨论中引出：先给 agent-study 在 locus 下建索引。YZ 澄清"移入"= 同 cogos 一样，locus 内建索引和工程印象，本体不物理移动。
3. AI 独立观点：
   - 建索引是后续两步的前置依赖，应现在做，但只建骨架（README + index + active 指针）。
   - 印象层（current.md 内容）留到"重新加载"步生成，避免"索引说读了、实际没读"。
   - 关键边界：agent-study 本体是知识库（02-concepts 约 50 概念 + 03-maps + 01-recovery），locus 对它存"索引指针"而非复制内容，防双写——这点与 cogos（代码工程）不同。
   - 衔接：通信记忆与 agent-study 的 `agent-communication-protocol.md` / `perception-communication.md` / `agent-architecture-layers.md` 对应，通信层是这些概念中感知/通信层的落地，会自然导出智能系统设计主线。

## 关键锚点

- agent-study 本体：`../agent-study/`（remote git@github.com:zhengyp36/agent-study.git，已登记 workspace.json）。
- agent-study 入口：`agent-study/AGENTS.md` + `index.md` + `01-recovery/current-focus.md`。
- agent-study 旧声明：index.md 顶部"locus 自身机制待修，暂不记入 locus"（08-13），现策略转向纳入 locus。

## 关键结论/决策

- 暂无 YZ 拍板（索引是否现在建、范围几何待定）。

## 遗留

- 三件事排序与范围未定。
- agent-study 索引范围未定（骨架 now vs 印象 later）。
