# handoff｜交接：M2 图形路线实验（第三轮）· 2026-09-21 #16

> ⚠️ **有更新版：`handoff-screen-17.md`（第四轮）**；本文件 §〇·五 已定案清单仍有效。
> ❌ **作废（2026-09-21 23:2x）：自持 / 自启整条线已撤** —— **A8、A11、`:2` 隐患、`systemd-run`/user unit/linger 装配、`ensure` 命令、"桌面生命周期"话题全部作废**。详见 `handoff-screen-17.md` §十一·11.3。本文件 §四 **P4｜自持**、§五 / §六 里相关条目**均已失效，勿再执行**。
> **目标（唯一约束）见 `spec-screen-1.md` §0.0。**
> **新会话读本文件 + `handoff-screen-15.md`（尤其第四节的架构定案）即可开工。**
> **最重要的细节文件**：`screen-exp-log.md`（实验逐条记录 + 脚本索引）；假设清单/计划：`screen-verify-1.md`；上一轮：`handoff-screen-15.md`；脚本：`screen-lab-verify/`。

## 〇、给新会话的两条工作纪律（YZ 定）

1. **动手实验前先起一个 10 分钟闹钟**；到点停下，**先把结论落 `screen-exp-log.md`，再和 YZ 讨论**；没做完就讨论后继续。**闹钟是护栏，不是 KPI——到点没做完完全没有压力。** 纯讨论/交接轮不必起。
2. **`terminal_exec` 完成会唤醒你，不要在 exec 后 `sleep`。**（想给长任务探活用的 `timeoutSec` 看门狗参数尚未实现，暂缓。）已知 `terminal_observe` 可能一次性返回大量历史输出 → 判断结果请以**输出文件**为准。

## 〇·五、✅ 已定案清单（2026-09-21，**勿再当待裁决**）

1. **浏览器后端默认 = Xwayland(X11) + XTEST**。依据 B1：三项判据全过（X11 起得来 / a11y 树完整 / 全局坐标 / XTEST 文本输入），一次解掉"文本输入 + 全局坐标"两个缺口。详见 `screen-exp-log.md` §B1。
2. **文本输入路线 = 键盘合成（XTEST）**。Chromium 不暴露可用的 a11y `EditableText`（一手实测）；GTK 等原生控件才可直接写 —— 已定，不再找 a11y 写法。
3. **坐标路线的成立前提 = 被测浏览器跑 X11**。X11 客户端 a11y bounds **即屏幕像素坐标**（窗口平移 → extents 同步平移，已实测）。原生 Wayland 客户端只给窗口局部坐标，此路已弃。
4. **注入与观看解耦**：XTEST 不占用 ScreenCast 流；Wayland 的 absolute 注入才必须挂流，而流是**单消费者独占**（A2）→ 选 X11 后"注入"与"给人看/调试口"不抢资源。
5. **架构 = 两模式 + 单操作者**（§三，全文见 `handoff-screen-15.md` 第四节）。
6. **"headless 里没有 X"是假象**：Xwayland 一直在，只是 display 没探对（见 §七）。当初被迫加的 `--ozone-platform=wayland` **应去掉**。

## 一、一句话现状

M2 的 **headless 路线全通**：无 seat 的 headless gnome-shell + chrome（`--password-store=basic` + **X11/Xwayland** + `--force-renderer-accessibility`）可正常上网；**办法二（AT-SPI `Action`）在自造页 + 真实站点（react.dev）全覆盖**；**文本输入（XTEST）与全局坐标均已验证**；ScreenCast 取帧复核通过。**架构已定案（两模式 + 单操作者）**。**没写任何生产代码。**

## 二、本轮证实 / 证伪（要点，细节见 `screen-exp-log.md`）

| 项 | 结果 |
|---|---|
| **A4 真实站点**（react.dev，React SPA） | ✅ 树 1376 节点 / 227 个可动作节点（button 106、link 71、entry/slider/combo 各 3…） |
| **A4 懒开** | ❌ 不带 `--force-renderer-accessibility` 时树**只有 1 个 `frame` 节点** → **flag 目前必需**（与 F1 指纹冲突） |
| **A1 复核 + A2** | ✅ `RecordMonitor` 出 1920×1080；❌ mutter ScreenCast 流**单消费者独占**（并发第二路无帧），但"不新开显示/不改分辨率"成立 |
| **值类控件** | ✅ range（`Value.set_current_value`）、✅ select（`open` + 子项 `select`）真触发页面 `onchange`；❌ text/textarea |
| **文本输入根因** | **Chromium 不暴露可用的 `EditableText`**（`get_editable_text_iface=None`、`set_text_contents=False`）；**GTK `GtkEntry` 对照正常**（写入成功）→ **Chromium 特有**，非 AT-SPI 缺陷 |
| **ScreenCast `Session creation inhibited`** | 真因是 headless shell **自己进了屏保/锁定** → 关 `idle-delay`/`lock-enabled` |
| **B1 后端（Xwayland）** | ✅ 三项全过：X11 起得来 / 树完整（382 节点）/ a11y bounds 随窗口平移=**全局坐标** / **XTEST 文本输入逐字命中**（详见 `screen-exp-log.md` §B1） |
| **E4/F1 反检测（本机）** | ✅ 三配置（无 flag / 带 flag / 带 flag+a11y 客户端）页面可见静态指纹**逐字段一致** → flag 与 a11y 激活**无页面可见痕迹**；❌ 本机 `webgl=null`（无 3D，归 E1/A12）；性能侧信道噪声大未量化 |

## 三、架构定案（**必读**，全文见 `handoff-screen-15.md` 第四节）

- ~~**出发点**：agent 自己没有用屏需求 → 给 agent 的电脑**默认不占屏**~~ ❌ **此条错，已作废**：**反馈必须有**；占屏是方案。正确口径见 `spec-screen-1.md` §0.0。
- **统一抽象**：endpoint（**像素 + a11y + 输入**）↔ client（真人或 agent）。三场景只是"endpoint 在哪台机器 + 谁是 client"；**场景2（agent 间）与场景3（agent 给人看）同构**；场景1（人机协助）唯一有本地主体。
- **只有两种模式**：
  - **模式 A（机器上没真人）**：agent 自用；owner agent 持操作权，可授权给别的 agent，**可随时拿回**。
  - **模式 B（机器上有真人）**：真人最高优先级，**可随时拿回**；agent 接入协助（不用屏）。
  - "agent 在用、真人想看" = **模式 A 的只读调试口**；要介入则切模式 B。
- **不变量**：**任一时刻至多一个"有效操作者"**；只留一个极薄的**撤销/抢占**原语，**不做排队或仲裁**；语言只做高层协调，不负责防冲突。
- **观看向两处退化**：模式 A 的看 = 调试口（只读、分发便宜）；模式 B 的看 = **人本机物理屏**。
- **agent 的推理/状态放在图形会话之外**（图形会话只是"随时可换的一双手"），使模式切换便宜。

## 四、待做实验

**P1｜补完 M2 的"操作"** —— ✅ **已完成**（详见 `screen-exp-log.md` §P1）
- ✅ **A3**：重解析（窗口移动后仍点中）、子树 vs 全树（1760 节点/2545ms vs 382 节点/573ms）、200ms deadline 触发回退 → 三项全过。设计含义：≈**1.5ms/节点**，全树遍历不可用，须"**按 id 缓存路径 + point query + per-op budget + 回退**"。
- ✅ **分发验证**：1 个 `pipewiresrc`（单消费者）→ `tee` fan-out 给 3 个 appsink，**3/3 都出帧** → "能分发"成立（模式 A 调试口 / 场景3 底座）。
- 坑：D-Bus 信号 `PipeWireStreamAdded` **必须迭代 `GLib.MainContext`** 才送达（否则 `NODE=None`）。

**P2｜像素 / 键盘注入**（文本输入已定案 = XTEST/X11；以下为余项 / 兜底）
- ✅ **文本输入**：**已定案走 Xwayland + XTEST**（B1 实测逐字命中）。落地项：生产启动器**去掉** `--ozone-platform=wayland`，加 **DISPLAY/XAUTHORITY 探活**（见 §七）。
- **兜底（非必需）**：Mutter `RemoteDesktop.NotifyKeyboardKeycode` / `ydotool` —— 仅在"非 mutter / 无 Xwayland"环境才考虑。
- **E5 余项**：Wayland `NotifyPointerMotionAbsolute(stream,x,y)` —— 降级为"若要支持原生 Wayland 后端时的注入实现"，**不再是默认路径**。

**P3｜反检测** —— E4/F1 **本机部分已完成**（见 `screen-exp-log.md` §E4/F1）
- ✅ **E4/F1（本机）**：三配置静态指纹逐字段一致 → **a11y / flag 无页面可见痕迹**（证伪 F1 担忧）；性能侧信道噪声大，待更干净测量。
- ✅ **E6 humanization**：已验可行（73 点轨迹 + 非等间隔 + 末端过冲回正 + 点击命中；见 `screen-exp-log.md` §E6）。
- ❌ **剩余**：`E1/A12`（**需真 3D 机器**；`webgl=null` 是当前家具缺口）。

**P4｜自持** —— ❌ **整条作废**（见文件头 + `handoff-screen-17.md` §十一·11.3）：~~`A8`（linger + user unit 重启自持，需 YZ reboot）；`A11`（user unit 集群收尾）~~。

**随定案新出**：撤销/抢占原语原型（可先做无真实输入源的桩）；"a11y 腿是否进 endpoint 接口"（设计决策）。

**本机判"不可满足/需换机"**：E1/A12（硬件）；场景1 非 Linux 人机的 a11y 腿。（~~Wayland 全局坐标~~ **已绕：改走 X11，不再是缺口**。）

## 五、环境现状与改动

> ❌ **本节 `linger` / tangyu gsettings / ACL 等条目随自持·自启作废，待清理**（见文件头）。保留仅作历史。

- 目标账号 `tangyu(1001)`；`gdm` active（greeter 占 seat0/tty1）；tangyu 用 linger 起 headless shell。
- **headless shell 现在 running**（`screenlab-shell`，1920×1080）；现场残留的 chrome / `a4-serve` **已清**。
- `alice(1002)`：YZ 建，正常桌面会话（seat0/tty2）。
- **持久/临时改动**：
  - `loginctl enable-linger tangyu`（可逆）
  - 临时 ACL `setfacl -m u:tangyu:rw /dev/dri/card0`（**重启失效，当前已设**）
  - tangyu gsettings：`idle-delay=0`、`screensaver lock-enabled=false`（**否则 ScreenCast 被拒**）、`toolkit-accessibility=true`（alice 也设过 true）
  - VBox 主机侧 3D 加速已开（YZ 改）

## 六、入口与纪律

> ❌ **本节 `systemd-run` / linger / `terminate-user` 相关命令全部失效**（见文件头），**勿再执行**。

```bash
# tangyu
ssh tangyu@localhost
export XDG_RUNTIME_DIR=/run/user/1001 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
# 起 headless 桌面（单元名统一 screenlab-*）
systemd-run --user --unit=screenlab-shell --collect --setenv=NO_AT_BRIDGE=0 \
  --property=StandardError=file:/tmp/screenlab-shell.err \
  -- gnome-shell --headless --virtual-monitor 1920x1080 --wayland-display=screenlab-0
# chrome（默认后端 = X11/Xwayland；**不要**再加 --ozone-platform=wayland）
# 先探活 Xwayland（多实例：:2/:3 常通，:0/:1 是别的会话，:4/:5 坏）
for d in :2 :3 :1 :0; do for f in $(ls -t /run/user/1001/.mutter-Xwaylandauth.*); do
  DISPLAY=$d XAUTHORITY=$f timeout 4 xdotool getdisplaygeometry >/dev/null 2>&1 && { export DISPLAY=$d XAUTHORITY=$f; break 2; }
done; done
google-chrome --password-store=basic --force-renderer-accessibility <url>
# headless shell 必须先关空闲锁定，否则 ScreenCast 被拒
gsettings set org.gnome.desktop.session idle-delay 0
gsettings set org.gnome.desktop.screensaver lock-enabled false
# alice（正常会话，从本机以 sudo 操作）
sudo -S -k -u alice -H bash /tmp/<script>.sh < ~/.secrets/centos.key
```
- **sudo**：`sudo -S ... < ~/.secrets/centos.key`（密码只喂 stdin）。
- **每条结论先落 `screen-exp-log.md`**。
- **`pkill -f <pattern>` 会自伤**（匹配到自己命令行 → 命令被切断；**ssh 的整条命令行也算**）→ 用 `-x`、PID、**或把 pkill 放进脚本文件**、或用 `[b]racket` 写法。

## 七、已知坑（新增，其余沿用 #15）

- ~~**headless 里 chrome 必须 `--ozone-platform=wayland`**~~ **已推翻（B1）**：真因是 Xwayland 有**多实例、没探对 display**。正确做法：探活选通的 `DISPLAY/XAUTHORITY`（`:2/:3` 通、`:0/:1` 是别的会话、`:4/:5` 坏），chrome 走默认 X11 后端。
- **`CreateSession` 报 `Session creation inhibited`** → 查 `org.gnome.ScreenSaver.GetActive`，是 headless shell 自己屏保/锁定了 → 关 idle/lock。
- **不带 `--force-renderer-accessibility` 就是空树** → flag 必需。
- **跨用户 `/tmp` 属主**会挡住写入（alice 的 `a4-*.log`）→ 各用各的路径（已改 `/tmp/a4t-*.log` + `a4-serve-t.py`）。
- **文本输入**：对 **Chromium** 必须键盘合成（a11y 的 `EditableText` 不可用）；GTK 等原生控件 a11y 可直接写。
- 沿用：ScreenCast `RecordMonitor`、`Introspect` 被封、RemoteDesktop session 只对同连接暴露、关闭 ScreenCast session 会崩 shell、journal 读不到要靠 `StandardError=file:`。

## 八、脚本（`screen-lab-verify/`）

| 文件 | 用途 |
|---|---|
| `a4-page.html` / `a4-serve.py` / `a4-serve-t.py` | A4 可控测试页（14 控件）/ 回执服务 / tangyu 路径版（`/tmp/a4t-*.log`） |
| `a4-atspi.py` / `a4-real-probe.py` | 遍历 chrome a11y 树 + `doAction`；真实站点树统计 |
| `a4-real.sh` / `a4-values.sh` / `a4-values.py` / `a4-values2.py` | 真实站点启动 / 值类控件实验 / 接口探测 / 键盘事件 + select |
| `a4-iface-probe.py` / `a4-iface2.py` / `gtk-entry.py` / `gtk-run.sh` | Chromium `EditableText` 缺失的证据 + GTK 对照 |
| `a2.sh` / `a2b.sh` / `screencast-mon.py` | 流复用（单消费者/并发）、持 session 拿 node id |
| `a4-x11.sh` / `a4-extents.py` / `a4-keytest.py` / `a4-xtest.sh` | **B1：Xwayland 后端验证**（X11 起 chrome / extents 全局坐标 / XTEST 键盘输入） |
| `p1-start.sh` / `p1-a3.py` / `p1-a3.sh` | **P1·A3**（X11 起 chrome + 测试页 / 重解析·子树·deadline） |
| `p1-fanout.py` / `p1-fanout.sh` | **P1·分发**（1 pipewiresrc → `tee` → N appsink） |
| `e4-fp.html` / `e4-serve.py` / `e4-fp.sh` | **E4/F1 反检测**（指纹页 + 服务 + 三配置采集） |
| `e6-page.html` / `e6-serve.py` / `e6-move.py` / `e6.sh` | **E6 humanization**（轨迹页 + 缓动/抖动/过冲注入 + 点击） |
| `cleanup.sh` | 清残留 chrome / a4-serve / gtk-entry |

## 九、建议的首次动作

1. ~~先和 YZ 定浏览器后端默认~~ **已定案（§〇·五）：Xwayland(X11) + XTEST，无需再议。**
2. ~~**P1**：A3 → 分发验证~~ ✅ **已完成（§四 + `screen-exp-log.md` §P1）。**
3. **下一步候选**：① 把 X11 探活封成 chrome 启动器（去掉 `--ozone-platform=wayland`，用 §六 片段）；② P3 反检测（E4 / F1 / E6）；~~③ P4 自持（A8 需 reboot、A11 收尾）~~ ❌ **作废**。
