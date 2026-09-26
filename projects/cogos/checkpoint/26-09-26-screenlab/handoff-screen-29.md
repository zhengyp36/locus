# handoff｜交接给新会话 · 2026-09-23 #29

> 接 #28。上一会话：把测试环境弄干净、**验证了形态**（Step 0/1 完成），并建起"跨会话连续"的机制。

## 给新会话的第一句话
> 先读 `screen-goal1-progress.md`（**滚动状态 = 唯一工作入口**），把它的 **§2 步骤表 / §3 当前指针 / §4 待 YZ** 复述一遍给我核；
> 然后**按步骤做 Step 2**——但先跟我确认「X11 单形态」。
> **开工前先 `set_timer` 10 分钟**；到点跑 `python3 tools/ctx.py`，对照 §3 看是否偏离、会话是否过长。
> 别重新发现环境——锚点都在 progress §1。

## 本轮结论（一句话）
- **形态验证通过**：X11（XFCE/Xorg，合成 ON）下 root 抓与单窗抓都看清 `xfce4-terminal` 文字、`zenity` 文字、GTK3 对话框 —— **B2（Wayland 下 GTK 窗全黑/缺字）不重现**。证据 `/tmp/kilo/cap1-{root,term,zen,gst}.png`。
- 单形态推荐 = **VM 内普通 X11 桌面**（XFCE/Xorg），人只用 viewer 看；Wayland/Xwayland/headless/Xvfb 降为延后或备选。**待 YZ 正式确认。**

## 本轮已完成
- **Step 0**：靶机 `surface-centos-9` 定靶并清空旧 screenlab；两机清理；靶机 machine-id 换新、hostname `surface-centos`；靶机建 **agent1** 账户，`:0` 归 agent1 的 XFCE/X11 会话。
- **Step 1**：见上"结论"。
- **连续性机制**：`../locus/tools/ctx.py`（自检命令）+ `screen-goal1-progress.md`（滚动状态）+ 10 分钟闹钟纪律。

## 工作纪律（务必执行）
1. **每个动作前** `set_timer` 10 分钟；到点三件事：① `python3 tools/ctx.py`；② 对照 progress §3 当前指针判断是否偏离；③ **上下文 ≥150k（≈15%）或路径偏 → 就地更新 progress + 写新 handoff + `tools/feishu_notify.py` 通知 YZ 切会话**。
2. **每完成一步**就地更新 `screen-goal1-progress.md`，并在 §6 记一行（时间 · 指针 · token）。
3. **边界**：改代码/操作测试机 = 我做；**提交/推送、动 zhengyp/本机、改目标** = YZ 定；判据失败 → 停下报结论。
4. 自检命令在 `../locus` 目录跑：`python3 tools/ctx.py`。

## 入口
- **滚动状态（先读）**：`checkpoint/screen-goal1-progress.md`
- 环境细节：#28 `checkpoint/handoff-screen-28.md`
- 代码：`../cogos/screenlab` @ `0670849`（分支 `feat/screenlab-p2` / tag `screenlab-freeze-2026-09-22`）
