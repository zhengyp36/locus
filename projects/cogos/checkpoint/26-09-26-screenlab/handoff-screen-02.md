# handoff｜图形电脑（看屏 / 适配服务 / 协议 / 客户端）讨论 · 2026-09-20 #2

> **新会话任务**：继续"图形化看电脑"。本会话已把 see/act 在**两台真机**上跑通，下一步是选：固化环境 / 写最小 daemon+CLI / 做 Wayland 或 Android 适配。**纯讨论 + 实测**，未动 cogos 代码。
> **交接语**：读 `work/A/checkpoint/handoff-screen-02.md`，细节读 `work/A/checkpoint/checkpoint-3.md`，从"待 YZ 裁决"往下谈。
> **前序**：`handoff-screen-01.md`（图形面讨论 + 阶段划分）→ `checkpoint-3.md`（本会话实测）→ 本文件。

## 本会话性质

**讨论 + 系统实测。** cogos 代码基线仍 `45ab216`、工作区干净；但**改了两台机的系统配置**（详见 `checkpoint-3.md` §八，可回退）。

## 本会话成果（一句话）

**see/act 从纸面变成两台机器上的实物**：我在本机（locus 所在 VM）隔 SSH 操作真实 X11 桌面，YZ 在 VBox 窗口同步看到界面被操作（点对话框 → `Alt+F2` 起终端 → 打字 → 抓屏确认输出）。

## 已收敛结论（可当既定）

- **本机 X11 能跑**（handoff-screen-01 说"默认 Wayland + 无用户桌面"已过时）：三段根因 = ① modesetting 拒绝在 llvmpipe 上跑 glamor → 装 `xorg-x11-drv-vmware`；② `/dev/dri/card0` 权限 → `usermod -aG video`；③ Xfce XSMP 残留 → 改用 `gnome-xorg`。
- **daemon 必须活在目标会话内部**：GNOME Shell 的 D-Bus 抓屏对外部会话 `AccessDenied`；Xwayland（rootless）根窗口 `XGetImage` 直接 `BadMatch`。外部进程抓不了 Wayland 会话。
- **`snapshot_id` 是必需的**：加窗口装饰后坐标漂移（y 158→185），按旧坐标点空——`act(pointer)` 必须绑定当次快照。
- **WM 是 `act` 可靠性的前置**：无 WM 时 `_NET_ACTIVE_WINDOW` 缺失、焦点不可控（实测键盘跑到别处）。
- **工具选型定案**：抓屏用 Pillow（`ImageGrab(xdisplay=...)`，自带 xcb）；注入用 **`xdotool`**（手写 python-xlib 因 RandR 错误处理 bug 不可靠）。
- **212 是最便宜的弱机验证场**：1 vCPU / 1.7G 跑 `Xvfb :99` + openbox + chrome，内存余 1.2G。
- Wayland 原生通道存在（`org.gnome.Mutter.RemoteDesktop` 可 `CreateSession`），但看屏要叠 ScreenCast + PipeWire，重，暂缓。

## 待 YZ 裁决

1. 图 = 持久资产（`image_ctx` 有根）还是临时介质（`img-tool` 无根）——两条 lineage 未并。
2. 自建电脑 vs E2B 类云桌面。
3. 客户端薄到哪（纯管道 vs 带薄语义层）。
4. 先做哪个平台（Linux/X11 已通、Android 未试、Windows 暂停）。
5. 是否给 212 sudo（本机已给）。
6. 旧遗留 4b 装配 / 按需加载与本线的关系。
7. **代码放哪**：新仓 `screen-lab` vs cogos 子包。
8. **是否做 Wayland 适配**（YZ 日常是 Wayland）。
9. Xfce 会话 XSMP 残留：根修还是弃用 Xfce。
10. 密码轮换 / 关 SSH 密码登录 / 收紧 firewalld（见 `checkpoint-3.md` §七）。
11. Windows 线何时重启（需 YZ 在宿主 `192.168.1.112` 上执行那条 PowerShell，装 OpenSSH Server；YZ 反馈"太慢"，已暂停）。

## 下一步建议（候选，供 YZ 选）

1. **回写设计**：把 `checkpoint-3.md` §五 的实测结论收敛进 spec（`snapshot_id` 依据、WM 前置、daemon 在会话内）。
2. **环境固化脚本**：212 的 `Xvfb + openbox + 应用` 收成一条 bootstrap；本机直接用 `:0`。
3. **最小 daemon + client + CLI**（Phase 1 自洽工具）：mechanical 子集 `displays / state / see / act / blob_get`，Unix socket，Pillow 抓屏 + xdotool 注入 + 内容寻址 blob + 快照世代；在 `:0` 与 `:99` 两环境跑 LLM 在环验收。**不被裁决 1–3 阻塞。**
4. **Wayland 适配**（Mutter RemoteDesktop + PipeWire）。
5. Android/scrcpy 场（未动）。

## 环境与命令速查

- **本机**：`DISPLAY=:0`，`XAUTHORITY=/run/user/1000/gdm/Xauthority`；Xorg 在 vt2、gnome-xorg、GDM 自动登录 zhengyp。
  抓屏：`python3.11 -c "from PIL import ImageGrab; ImageGrab.grab(xdisplay=':0').save('/tmp/kilo/s.png')"`；注入：`xdotool key/type/click/mousemove`。
  sudo：`cat ~/.secrets/centos.key | sudo -S -p '' <cmd>`（**绝不要把 `< file` 放在管道末尾**，见 §七泄露事故）。
- **212**：`ssh zhengyp@192.168.1.212` 免密；`xvfb99.service` + openbox 在跑；`DISPLAY=:99`；sudo 需密码。
- **Windows 宿主**：`192.168.1.112`，Win11 Home，VBox 宿主；`135/139/445` 开、`22` 关。

## 关键引用

- 本会话实测细节：`checkpoint-3.md`（含命令备忘 §九、系统改动 §八、安全 §七）。
- 前序讨论：`handoff-screen-01.md`（工具分域 / 协议 screen/1 / 客户端形态 / 行业现状 / 阶段划分）。
- 代码面：`app.py:192` `_build_specs`；`tools.py:1131` `ToolRegistry`；`config.py:99` `render_system_prompt`；`consciousness.py:65-70`、`:68` `schemas`；`image_ctx/domain.py:36-56`、`image_ctx/tools.py:122` `see`。
- 设计口径：`cogos/docs/design-agent-tools.md` §5.4 / §6 / §12；`cogos/docs/vision-system-design.md` §14 / §168–170。

## 纪律

- 跑测试用 `python3.11 -m pytest`（系统 `python` 是 3.9）。
- 结论先落 `checkpoint-3.md` / spec，定案再更新权威分册 `design-agent-tools.md`。
- 不替 agent 决定用法；发现设计问题回 checkpoint 记，不悄悄改设计。
