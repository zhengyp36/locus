# 26-09-26-screenlab · screenlab 线归档（2026-09-26）

源：`work/A/checkpoint/`（09-20~09-26）。分支 `feat/screenlab-p2`（tip `837b51d`）。
**收口件（权威/当前）**：cogos 本体 `docs/screenlab-freeze.md`、`docs/screenlab-env.md`、`docs/design-agent-tools.md §16/§18`。
**独立验收结论**：v2 图形面**接口层通过**（X11/Windows usage 真值全过；回归 1235 passed / 4 skipped）。

## 目录内容
- **工作单/规则/验收**：`screenlab-work.md`（任务态总档）· `screenlab-rules.md`（规则）· `screenlab-tools-review.md`（#72 盘点）· `acceptance-screen-78.md`（独立验收，修订版）
- **handoff**：`handoff-screen-01..77.md`（**77 份**；**无 -78**，#78 证据见上条）
- **设计**：`design-computer-v2-interface.md`（封板 #73）· `design-vision-computer-fusion.md`（#63）· `design-vision-scripting.md` · `design-screen-system.md` · `design-screen-assist.md` · `design-screen-antidetect.md`
- **规格**：`spec-screen-1.md`（目标唯一约束 §0.0）· `spec-screen-client-api.md` · `spec-screen-element-act.md`（作废）· `spec-screen-ledger.md`（作废）
- **实测/结论**：`screen-{exp-log,assist-exp-log,assist-status,goal1-progress,verify-1,verify-usage-1,change-detect,android-issues}.md` · `issue-screen-surface-lifecycle.md` · `rationale-screen-a11y-drop.md` · `win-assist-setup.md`
- **图形面阶段档**：`checkpoint-3.md` ~ `checkpoint-6.md`
- **原型**：`screen-lab/`（旧包）· `screen-lab-verify/`（验证脚本）· `disable-rsc.ps1`
- **dev/ops 工具**：`tools/`（**已排除** `keys/ blobs/ .imgctx/ __pycache__/ android-probe/{build,runs}/ state.json`）

## 状态义
同 `ARCHIVE-INDEX.md` 约定；本线整体状态 = **接口层收口，实现细节待办（D2/D1/gap C）**。
