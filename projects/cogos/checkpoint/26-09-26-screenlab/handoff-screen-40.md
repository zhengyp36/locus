# handoff｜交接给新会话 · 2026-09-24 #40

> 接 #39。本会话 = **Goal 1 收尾确认（YZ 已确认 push）+ Goal 2 / 关系 3a 的"使用层方案"讨论定稿**，产出 **`design-screen-assist.md`**。
> 下一步 = **按该稿做 X11 闸门实验**（用靶机真实桌面）。**本会话未动代码、未做实验。**
>
> **规则 / 环境操作不在这里**——见 **`screenlab-rules.md`**（稳定参考，先读）。

## 给新会话的第一句话

> 先读 **`screenlab-rules.md`**（规则+环境）→ 本文件（状态/下一步）→ **`design-screen-assist.md`**（§0 边界 / §2 流程 / §4 环节 / §7 靶场 / §8 规则）→ **`spec-screen-1.md` §0.0`**（唯一约束）。
> **本会话把 3a 的"使用层方案"定稿**（`design-screen-assist.md`），**下一步 = 做 X11 闸门实验**；本线**从 X11 起，Wayland 先不做**。
> 靶机 `surface-centos-9`（100.100.137.78）；宿主 VBox `ssh zhengyp@100.112.50.115`（救机 `VBoxManage controlvm centos9 reset`）。
> 代码 `../cogos` @ `feat/screenlab-p2`（tag `screenlab-goal1-2026-09-24` 已 push）。

## 本会话已做（纯讨论 + 文档，未动码/未实验）

- **Goal 1 收尾确认**：YZ 确认 3 commit + tag 已 push 到 `origin/feat/screenlab-p2`。
- **产出 `design-screen-assist.md`（Goal 2 / 关系 3a 工作稿）**，收敛如下（细节见该稿）：
  - **使用层同形**：agent 视角与"开自己电脑 / 协助另一 agent"同形；差异只有四件——临时入场 · `close`=松手 · 可被抢占 · 收回显式可查。
  - **九步流程**（§2）：真人在飞书开口 → agent 发带 nonce 请求 → 真人机按发送者号码匹配通讯录弹框 → 人点同意 → agent 报号码+签名、真人机用**通讯录公钥**验签 → tailscale 建连、同形 `ComputerSession`（默认只读）→ 真人一上手 agent 转观察 → 退场/收回 → 下次调用立即报 `revoked`。
  - **认证 = 通讯录 `{号码, 公钥}`**（飞书发来、存下即可，**不再设计机制**）；红线：**不采信连接自报的公钥**。
  - **传输 = tailscale（已定，不自建）**；WireGuard 管管道，签名管"是哪个号码"，授权仍在我们层。
  - **平台纪律 = 不依赖平台 + 最小描述**：只给 `ostype` + `info()` 能力位；行为差距靠**看/试/问**，不给"行为手册"。
  - **取消/收回 = 物理/注入分源**（§4.7）：主用**物理热键**（Windows `LLMHF_INJECTED`、X11 evdev、macOS `CGEventTap` 过滤注入）；辅为**状态灯**（click-through）；兜底系统共享指示器 + 飞书远程停。同一分源逻辑兼作抢占判定。
  - **Wayland 先不做**（不追求覆盖所有情况）。
  - **靶场 = surface 的"真实桌面"**（§7）：新建账户 + 登录（**GDM autologin** 更稳，或 `VBoxManage controlvm centos9 keyboardputscancode` 注入解锁；**别 reboot**，有 dracut 前科）。**意外好条件**：VBox 键盘注入在 guest 里=**物理设备**，`xdotool`=XTEST → 可在 VM 上**真测分源**。

## 下一步（新会话照此做实验）

**X11 闸门**（真值对照，公开入口真用；**首次实验建 `screen-assist-exp-log.md`** 逐条记判据/方法/结果/结论）：
1. **附着现有真实会话**（非新建 Xvfb）：在其上 `capture` + `act` 闭环；**退出后不破坏真人会话**（A1 崩 shell 是反面教材）。
2. **物理/注入分源**：取消热键只认"非 XTEST"事件；用 **VBox 键盘注入模拟真人**、`xdotool` 模拟 agent，验抢占判定。
3. **收回立即可见**：停会话 → agent 下次调用立刻报 `revoked`/`channel_closed`（不挂死，F1 是反面教材）。

## 入口

- **规则 + 环境（先读，稳定）**：`screenlab-rules.md`
- **本线方案（工作稿）**：`design-screen-assist.md`
- 目标（唯一约束）：`spec-screen-1.md` §0.0
- 体系：`design-screen-system.md`；生命周期/命令层：`issue-screen-surface-lifecycle.md`
- 号码体系：`../cogos/cogos/phone/`、`../cogos/cogos/feishu/telecom.py`
- 平台实测：`screen-exp-log.md`（E5/A1/A2/P1）
- 代码：`../cogos` @ `feat/screenlab-p2`
- 上一轮：#39 `handoff-screen-39.md`
