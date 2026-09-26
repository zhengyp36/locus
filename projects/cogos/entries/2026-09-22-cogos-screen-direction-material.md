# 素材｜图形工具（screenlab）现状与方向讨论材料 · 2026-09-22

> **性质**：本文件是**素材**，**不含方向结论**。方向由新会话讨论得出，且得出后仍是活的。
> **纪律**：事实带出处；假设显式标注；候选方向**不排序、不结论**。

## 0 位置图（结构，非判断）

- **L1 cogos 主线**：自驱 agent 本体（动机 / 自我 / 经历 / 运行框架）→ 总纲 `cogos/docs/design-selfdrive-agent.md`（当前唯一权威口径）。
- **L2 能力 / 工具层**：`term / fs / graphics / web / phone-files / comm` → `cogos/docs/design-agent-tools.md`。
- **L3 screenlab**：L2 中 **graphics** 那一格的实现 → `cogos/screenlab/`。

本会话（09-22 第十二轮）绝大部分时间在 **L3**。

## 1 事实（已验，带出处）

- **目标（7 条）**：`handoff-screen-18.md §5.1`；旧目标表述一律作废。
- **方案稿**：`spec-screen-client-api.md`（动词面）、`spec-screen-ledger.md`（账本）。
- **冻结点**：cogos `0670849`（分支 `feat/screenlab-p2`）+ annotated tag `screenlab-freeze-2026-09-22`，已 push；locus `4fb5bf9`。
- **动词面已实现**：`screenlab/proto/client.py` = `open / close / state / capture / act / yield / grant / revoke / blob_get`（另有 `info / displays`）。
- **授权语义 e2e 13/13 通过**（owner 抢占、revoke 立即断通道、ttl、一次性、not_owner）：`handoff-screen-18.md §7.3`。
- **人侧 viewer 真机验证**（页面 / 四端点 / 取帧 / 操作 / status / revoke / owner `yield` 让位与自动取回）：`handoff-screen-25.md §二 A1–A7`。
- **本机（VM）真实桌面 = GNOME/X11**：`loginctl` session 175 `Type=x11`；`/proc/41459/environ` 有 `XDG_SESSION_TYPE=x11`、`DISPLAY=:8`、`XDG_CURRENT_DESKTOP=GNOME`（2026-09-22 实测）。
- **agent1 会话 = headless Wayland + Xwayland**：`screenlab/install/session-start.sh:137`（`gnome-shell --headless`）。
- **取帧后端 `x11-windows`**：`screenlab/service/backends.py:187` —— 枚举 root **直接子窗口**、逐窗 `gst ximagesrc` 合成；代码注释说明合成 WM 下 root 窗口无客户端像素。
- **B2 现象**（在 agent1 的 Wayland+Xwayland 上实测）：`xfce4-terminal` 内容全黑、`zenity`（GTK3）文字缺失；单独 `gst ximagesrc xid=<该窗口>` 亦为黑；递归遍历窗口树未改善（改动已回退）→ `handoff-screen-25.md §三`。
- **"启动应用"无客户端动词**：动词面无 `launch / exec`；此前用账户 shell（`runuser`）起进程 → `handoff-screen-24/25`。
- **本机工具包可见性现状**：Chrome（软件渲染、客户端自绘外框）可见；`zenity` / `xfce4-terminal`（GTK）不可见。
- **本会话失败观察**：私有 Xvfb `:99` 上 `xdotool search` 返回空、`gst ximagesrc` 产出 0 字节 PNG（2026-09-22，未解释）。
- **环境可用件**：`Xorg` / `Xvfb` / `Xwayland` / `gnome-shell 40.10` / `mutter` / `gst-launch-1.0` / `xdotool` 在；无 `Xephyr/Xnest/xorg-x11-drv-dummy`；GTK 应用仅 `zenity` / `xfce4-terminal`，无 Qt 应用、无 `gtk3-demo`。

## 2 假设（未验，别当事实）

- B2 根因 = EGL/GL 渲染面不在 X 可读 pixmap —— **未验**（`handoff-25 §三` 只是"怀疑"）。
- B2 是 Wayland/Xwayland **专属** —— **未验**（本机 zhengyp 会话是 X11，可直接测）。
- X11 下 GTK/GL 窗口**可抓** —— **未验**。
- Wayland 下 XTEST 对**原生窗口**有效 —— **未验**。
- 私有 Xvfb spike 失败的含义 —— **未知**（疑环境 / gst 配置，非结论）。

## 3 作废名单

- `人一动手即夺回输入`（仅 ③a 成立；已由 `yield` 取代）。
- `热订阅`、`关闭重开`、`Xvfb 作起步形态`、`网络/NAT/打洞`、`a11y`、`元素表`、`act element`。
- `spec-screen-element-act.md` 整份。
- **本会话否决**：`runuser 封装一条命令提供给 agent`、**单独的 `exec` 动词**（讨论结论：跑东西走"桌面终端 + 输入位"）。
- **降格（非事实）**：`三通路`（跑东西 / 出画面 / 收操作）= `handoff-18 §5.2·B` 的 `[方案]`，**不是事实**；本会话我一度把它当事实用。

## 4 方向候选（并列，不排序、不结论）

- **A 继续做完 L3**：把 graphics 工具做到"真机可用"（形态 / 取帧 / 输入 / 装配 / 覆盖面）。
- **B 回上层**：暂停 L3，回 L1 / L2 讨论整体方向与优先级。
- **C 只补到够用**：L3 补到"浏览器能看能操作"即停，把力气放回主线。

（仅列候选，供讨论；不推荐、不排序。）

## 5 未决问题（待讨论）

- L3（graphics）在整体里**现在该占多大权重**？
- 形态：X11 优先 vs 必须覆盖 Wayland（取决于目标机与反检）。
- "人与 agent 双向"的形态：接入真人**真实桌面** vs 给账户**另开一块桌面**。
- 反检靶（"不被检测"对谁隐蔽）。
- 必须覆盖哪些应用。
- 目标本身：L1"能自我长的 agent"与这条工具线的关系。

## 6 入口

- 目标：`handoff-screen-18.md §5.1`、`spec-screen-1.md §0.0`
- 方案：`spec-screen-client-api.md`、`spec-screen-ledger.md`
- 总纲：`cogos/docs/design-selfdrive-agent.md`
- 理论评审入口：`../checkpoint/26-09-26-theory-residual/handoff-cogos-theory-review.md`
- 代码：`cogos/screenlab/` @ `0670849` / tag `screenlab-freeze-2026-09-22`
- 交接：`../checkpoint/26-09-26-screenlab/handoff-screen-26.md`
