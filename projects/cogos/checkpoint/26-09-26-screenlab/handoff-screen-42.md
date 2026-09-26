# handoff｜交接给新会话 · 2026-09-24 #42

> 接 #41。本会话 = **从目标裁决 G1/G3/G4 + 厘清 3a 的身份/授权/收回模型 + 修订 `design-screen-assist.md` 至自洽**；唯一改动 = `design-screen-assist.md`（未 commit）。
> **规则 / 环境操作不在本文件**——见 **`screenlab-rules.md`**（稳定参考，先读）。

## 给新会话的第一句话

> 先读 **`screenlab-rules.md`**（规则+环境）→ 本文件（状态/下一步）→ **`design-screen-assist.md`**（§0 边界 / §2 流程 / §3 分层 / §4 环节 / §7 靶场 / §8 规则）→ **`spec-screen-1.md` §0.0**（唯一约束）→ **`screen-assist-exp-log.md`**（#41 三闸门实验 + G1–G4）。
> 本会话**没做实验**，做的是**从目标裁决 + 改文档**：
> - **裁决三缺口**（判据只取 §0.0；"差异表"等均是素材，非约束）。
> - **把 `design-screen-assist.md` 改为自洽**：流程"**先连接/握手、后同意**"；**无会话凭证**（授权 = 一条连接，连接 + nonce 定界，不做短票）；**身份 = 密钥对（面孔）、号码 = 别名（可多个）**；收回粒度 = **连接**（三层：面孔 / 通讯录 / 连接）。
> 下一步候选：**落 G1**（attach 现有 `:N` 的公开入口）或 **实现 3a 连接/握手/收回闭环**。
> 靶机 `surface-centos-9`（100.100.137.78）；宿主 VBox（Windows）`zhengyp@100.112.50.115`。
> 代码 `../cogos` @ `feat/screenlab-p2`（`90afbeb`）。⚠️ 工作区有**未提交改动**：`screenlab/install/surface`（G2 修复，`--onlyvisible`）。

## 本会话已做

- **裁决三缺口（从目标，非人裁）**：
  - **G1｜attach 现有 display 无公开入口 → 必做（阻断 3a）**：3a 定义即"附着真人当前会话"（`design §4.1`）；`screenlab open` 写死 Xvfb 是 Goal 1 遗留。实现 = 给 `open` 加 attach 模式（读 session.env / `--display --xauth`），不起 Xvfb/WM。
  - **G3｜收回信号非语义化 → 必做（目标导出）**：(i) 立即不挂死已达标（115ms）；(ii) 需可归因（收回 vs 故障）——`design §4.5` 要求 agent 察觉被收回即停注入，通用 `connect_failed` 做不到。最小版：正常 stop 时 daemon 干净 unlink socket；客户端把"socket 消失/拒绝"映射为 `channel_closed`。
  - **G2｜`surface close` 选错窗口 → 实现 bug，直接提交**（已修未 commit）。
  - **G4｜`surface clip` 写入不持久 → 方案层，非目标阻塞**（§0.0 无剪贴板；"报成功却读空"违反可观测）。若做，正解 = daemon 内做常驻 CLIPBOARD owner，与 G3 生命周期一起规整；否则先把写路径标为不可用。
- **厘清 3a 身份/授权/收回模型（从目标）**：
  - **面 hosted by 账户**是进程事实（`spec §5.1`）；**授权 ≠ 绑账户**，3a 明写"不交出账户"。
  - **身份 = 一个密钥对（面孔）**；**号码 = 别名**，一个 agent 可有多个号码、共一把密钥；通讯录 = `{号码 → 公钥}`。
  - 握手：agent 连通道 → 报号码 → 服务端发 nonce → 私钥签回 → 服务端用通讯录公钥验 → 真人点同意。
  - **收回粒度 = 连接**：改状态即时失效；重连须重走握手 + 真人再点；**无离线凭证可吊销**。
  - **两侧存什么**：服务端 = 通讯录 + 连接记录 `{号码,通道,建时,能力位,state}`；客户端 = 通道 + 建时 + 自身私钥；都不存会话票。

## 关键坐标 / 当前状态

- **唯一改动**：`../checkpoint/design-screen-assist.md`（**未 commit**）。改了：状态行、§0 差异表「凭证」、§1 差异①、§2 流程（改序 + 服务端发 nonce + 补 step9 重连）、§3（表 + 新增"两侧存什么"）、§4.2（飞书退为发起+通道交换）、§4.3（会话票据→会话与收回感知）、§4.6/§6（去票据）。
- **代码** `../cogos` @ `feat/screenlab-p2` `90afbeb`；工作区 `screenlab/install/surface` 有未提交的 G2 修复。
- **靶机状态**（承接 #41）：`human@:0` 真实 XFCE 桌面在跑；`/usr/bin/surface` 已是修好版本；`/opt/screenlab` 与 repo 一致。
- **纪律（本会话被 YZ 强调）**：**由目标裁决，不是人裁**；`§0.0` 是唯一约束，"差异表"等是素材、可改；目标说不清才讨论。

## 一处目标没规定、本会话裁了的（可再议）

- **nonce 在连接上发**（而非"发到号码 / 飞书"）。目标未规定；选连接上发 = 更直接证明"此刻持有私钥"、少依赖飞书。若要额外绑"控制飞书号码"这层，改回飞书发。

## 下一步（新会话照此）

1. **落 G1**：`screenlab open` 加"附着已有 `:N`"路径（attach ≠ create）——3a 入场券。
2. **实现 3a 最早闭环**：连接 + nonce 握手 → 真人同意 → 会话 → 收回（断连接）+ 语义化 `channel_closed`（含 G3）。
3. **提交 G2**（若 YZ 同意）：`screenlab/install/surface` 的 `--onlyvisible`。
4. （可选）G4 clip 写路径修在 daemon 内；或标记为不可用。

## 入口

- **规则 + 环境（先读，稳定）**：`screenlab-rules.md`
- **本线方案（本会话已改）**：`design-screen-assist.md`
- **#41 实验全记录**：`screen-assist-exp-log.md`（三闸门 + G1–G4）
- 目标（唯一约束）：`spec-screen-1.md` §0.0
- 体系：`design-screen-system.md`；生命周期/命令层：`issue-screen-surface-lifecycle.md`
- 号码体系：`../cogos/cogos/phone/`、`../cogos/cogos/feishu/telecom.py`
- 代码：`../cogos` @ `feat/screenlab-p2`
- 上一轮：#41 `handoff-screen-41.md`
