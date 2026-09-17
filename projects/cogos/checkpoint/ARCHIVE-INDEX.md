# ARCHIVE-INDEX｜../checkpoint 归置结果（2026-09-17）

源 `work/A/checkpoint` 已归入：本目录 `26-09-17-agent-theory/`（cogos）＋ `locus/projects/kilo-resident/checkpoint/26-09-17-phone-number-contacts/`（kilo）。
整体权威口径已抽出为 **本体 `cogos/docs/design-selfdrive-agent.md`**。

状态义：**吸收**＝结论已进整体；**过程**＝保留依据；**取代**＝仅存历史；**旁证**＝只提供方法教训／判据。

## design

| 文件 | 状态 | 备注 |
|---|---|---|
| `design-cogos-agent-current.md` | 吸收 | 整体文档取代它 |
| `design-cogos-open-items.md` | 吸收 | 并入整体 §11／§12 |
| `design-cogos-agent-form.md` | 过程 | 三不变量／机制边界仍有效；结构三样已被改 |
| `design-cogos-loop-invariants.md` | 过程 | 环＝机制三段夹 cu 仍有效；`finish` 定位已被改 |
| `design-cogos-runtime-states.md` | 过程 | 全文仍有效，未接线 |
| `design-cogos-runtime-flows.md` | 过程 | 压缩／权重导出仍有效；切点／整理口径已被改 |
| `design-cogos-flow-direction.md` | 过程 | §6 悬置已解（方向＝对位） |
| `design-cogos-minimal-agent.md` | 取代 | "最小核"作废；保留"经历轴是骨架""取回替代常驻" |

## handoff

| 文件 | 状态 |
|---|---|
| `handoff-cogos-experience.md` | 过程（#18 主要依据） |
| `handoff-cogos-loop.md` | 过程（#17） |
| `handoff-cogos-perception-tick.md` | 取代（#16） |
| `handoff-cogos-scaffold.md` | 取代（#15） |
| `handoff-cogos-drives.md` | 取代（#14后半~#15） |
| `handoff-cogos-selfgrown.md` | 取代（#13~#14） |
| `handoff-agent-e0-to-selfgrown.md` | 取代（#12~#13） |
| `handoff-agent-experiments.md` | 取代（#11~#12） |
| `handoff-build-agent-v0.md` | 取代（#8~#9） |
| `handoff-identity-anchor-frame.md` | 过程（#12 支线） |
| `handoff-ctx-*.md`（4） | 旁证（上下文组织支线） |
| `handoff-criterion-dogfood.md` / `handoff-layered-acceptance.md` / `handoff-s4-next.md` | 旁证（自驱阶段） |

## 报告与阶段

| 文件 | 状态 |
|---|---|
| `probe-e0/`（10 md ＋ runs.tar.gz） | 旁证（E0 手动探针） |
| `probe-tendency/`（2 md ＋ runs.tar.gz） | 旁证（倾向探针） |
| `probe-compress/`（1 md ＋ runs.tar.gz） | 旁证（压缩探针，结论＝方法校准） |
| `ctx-*`（6） | 旁证（上下文组织） |
| `s2-report.md` / `s3-report.md` / `checkpoint-1..5.md` / `plan.md` / `state.md` / `status.md` / `next-experiments.md` | 过程（自驱阶段） |
| `dogfood/` / `dogfood-timer/` / `s4-target/` | 旁证（dogfood） |
| `README.md`（源目录说明） | 过程 |

## kilo 支线

| 文件 | 位置 |
|---|---|
| `handoff-kilo-phone.md` | `locus/projects/kilo-resident/checkpoint/26-09-17-phone-number-contacts/` |
| `handoff-kilo-number-contacts.md` | 同上 |

## 迁移元数据

- `MIGRATION-MAP.md`：源→目标映射。
- `MIGRATION-COVERAGE.md`：覆盖实测（5143 ＝ 迁入 5134 ＋ 缓存排除 9）。
