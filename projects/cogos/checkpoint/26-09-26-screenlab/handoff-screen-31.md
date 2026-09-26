# handoff｜交接给新会话 · 2026-09-23 #31

> 接 #30。本会话先把**判断修正**（Goal 1 其实未完成），再做**闸门实验**证明多账户形态可行，最后把**验证工具落地并全绿**。
> **上下文 186k/1M (19%) ≥ 150k 阈值 → 按纪律切会话。**

## 给新会话的第一句话
> 先读 `screen-goal1-progress.md`（**滚动状态 = 唯一工作入口**），复述 **§3 当前指针 / §4 阻塞项** 给我核；
> 然后**停下等 YZ 的形态裁决**（§4 第一条）：Xvfb（已验、软件渲染）vs 真 Xorg+Xephyr 嵌套（未验）。
> **别重跑闸门实验**——验证工具已全绿，直接复用。
> 开工前 `set_timer` 10 分钟；到点跑 `python3 tools/ctx.py`，对照 §3 看偏离与 ≥150k。

## 本轮结论（一句话）
- **Goal 1 未完成 → 缺口 = 多账户各自独立图形面**；已证明该缺口在 **Xvfb 形态**下可打通（三关系 + 隔离 + GL/Chrome 全验），验证工具 `run_goal1_xvfb.sh` 一次跑完 **RC=0**；**卡在 YZ 形态裁决**（Xvfb vs Xephyr），tag 挂起。

## 本轮判断修正（YZ 已同意）
- 之前把「Step 2–6 全绿」当成 Goal 1 完成是**误判**：那些只验了「**同一块 `:0`** 上的多种关系」，agent2 从没有自己的桌面。spec 前提是「每 agent 一账户 / 操作**自己账户对应的桌面**」（spec-screen-1.md:12,15,29）。
- 另外证伪一条外推：**B2（GTK/GL 抓不到）不是「非真 Xorg」的通病，只是 mutter+Xwayland 特有**；Xvfb 上不重现。

## 本轮已完成（对应 progress §4）
- **闸门①**：`Xvfb :7` + 真实 `PillowCapture` 抓到 GTK/VTE 文字（`gate-xvfb.png`）。
- **闸门②**：daemon-on-Xvfb 闭环（type/key 生效，帧现回显）。
- **闸门③**：agent1 `:7` 1280x720 + agent2 `:8` 1024x768，**各自独立 Xvfb + 各自服务并存**；X 级隔离成立（互访 `No protocol specified`、对方 runtime/xauth `Permission denied`）。
- **闸门④**：Chrome 148 on Xvfb 完整可抓（`glxinfo` = llvmpipe 软件 GL，`Accelerated:no`）。
- **凭证 e2e**：两账户各 10/10；**跨账户**（agent2 经隧道 → agent1 面）10/10。
- **验证工具落地**：`../cogos/tests/screenlab/e2e/`
  - `run_goal1_xvfb.sh`：操作机驱动，一条命令跑完 7 步（部署/双账户 create+服务/幂等/账户内闭环+隔离/跨账户隧道 guest/viewer 只读），末尾汇总 **RC=0**。
  - `xvfb_goal1_e2e.py`：账户内判据（自身显示可答、对端被拒、对端 runtime 不可读、服务答对 display/几何、闭环动帧、落 PNG）。
  - `xvfb_account_prepare.sh`：**create 原型**（每账户 Xvfb + 0600 xauth + 聚焦终端 + session-start）。
  - `xvfb_tunnel.sh`：跨账户 streamlocal 隧道（放文件里避免 pkill 自匹配）。
- **证据**：本机 `/tmp/kilo/goal1/{frame,agent1-after,agent2-after}.png`。

## 本轮踩到的坑（供 create 模式）
1. 换掉包目录后**必须 restart 服务**，否则旧 daemon 的 blobs 目录消失 → `FileNotFoundError`。
2. 终端焦点会被残留浏览器抢占 → `type` 进错窗；prepare 每次都要 `windowactivate`。
3. ssh 命令行里 `pkill -f <同串>` **会自匹配杀掉自己** → pkill 模式放进脚本文件才安全。

## 下一步（等 YZ 裁决后）
1. **形态裁决**（阻塞）：Xvfb（软件渲染=指纹，与 spec「不被检测」张力） vs 真 Xorg+每账户 Xephyr 嵌套（未验） vs 多 VM/VKMS。
2. 裁决后：`session-start.sh` 加 `create` 模式（含 session-stop teardown、幂等、detach）；把 prepare 原型收编进安装脚本。
3. 文档回写：`spec-screen-1.md` §0.0/§7、`cogos/docs/design-agent-tools.md`；`spec-screen-ledger.md` §0「未使用 Xvfb」纪律要改。
4. 收尾：清理靶机（Xvfb `:7/:8`、两 daemon、临时脚本/chrome profile、agent2 一次性公钥去留、`/tmp/slrun`）；提交 + 打 tag（YZ 定）。
5. 已知不阻塞：反检测/真 GPU（目标 3）、Wayland 真人桌面（Goal 2）、授权粒度（ledger §8）。

## 工作纪律（务必执行）
1. **动手前** `set_timer` 10 分钟；到点 ① `python3 tools/ctx.py` ② 对照 progress §3 ③ ≥150k 或偏 → 更新 progress + 写 handoff + `tools/feishu_notify.py` 通知 YZ。
2. **每步完成**就地更新 `screen-goal1-progress.md` §6 记一行 + 飞书通知 YZ；无须 YZ 介入则继续。
3. **边界**：改代码/操作测试机 = 我做；**提交/推送/tag、动 zhengyp/本机、改目标 = YZ 定**；靶机 `surface-centos-9` 可随意用，但**别用 `zhengyp` 当测试账户**。
4. 自检命令在 `../locus` 跑：`python3 tools/ctx.py`。

## 入口
- **滚动状态（先读）**：`checkpoint/screen-goal1-progress.md`（§1 锚点；§4 是本轮全部结论）
- 环境细节：#28 `handoff-screen-28.md`；上一轮 #30
- 规格：#1 `spec-screen-1.md`；账本 `spec-screen-ledger.md`；客户 API `spec-screen-client-api.md`
- 验证工具：`../cogos/tests/screenlab/e2e/`（`run_goal1_xvfb.sh` 等，**未提交**）
- 代码：`../cogos/screenlab` @ `c23dab3`（分支 `feat/screenlab-p2`，已推送；本轮只加了 tests/ 下验证工具，未提交）
