# handoff｜交接：M2 图形路线实验（第四轮）· 2026-09-21 #17

> ➡️ **已被 `handoff-screen-18.md`（第五轮）接续**（最新为 `handoff-screen-19.md`）：**本轮主题 = 定方案（怎么做）**。新会话从 #18 读起；本文件此后只作**目标（§十一·11.1）/ 作废清单（§十一·11.3）/ 素材（§二）**的引用源。

> **新会话读**：本文件 + `handoff-screen-16.md`（**§〇·五 已定案清单**）+ `handoff-screen-15.md`（§四 架构定案）+ `screen-exp-log.md`（逐条细节）+ `screen-verify-1.md`（假设/计划）。
> **脚本**：本地 `screen-lab-verify/`；远端 tangyu 副本在 `/tmp/` 与 `~/screenlab/`。

## 〇、工作纪律（沿用 + 本轮教训）

1. **动手前起 10–15 分钟闹钟**；到点**回看**：先把结论落 `screen-exp-log.md`，自评"是否偏离原目标 / 是否卡住"，再讨论。**闹钟是护栏不是 KPI**，没做完无压力。纯讨论轮不必起。
2. `terminal_exec` 完成会唤醒，**不要在 exec 后 sleep 轮询**；判断结果以**输出文件**为准（`terminal_observe` 可能回放大量历史）。
3. **一次只跑一条实验命令**。本轮踩坑：多 terminal 并发 → scp 覆盖正在执行的脚本（语法错误）、`pkill`/`pgrep` 自伤、探活选错显示，浪费大量时间。**并发是这次最大的时间黑洞。**
4. **`pkill -f` / `pgrep -f` 会自伤**——连 **ssh 的整条命令行**也算（`pgrep -f "[b]2.sh"` 会匹配到自己命令行里的 `bash /tmp/b2.sh` → 死循环）。用 `[x]` 写法、`-x`、PID，或**放进脚本文件**执行。
5. **sudo 用 zhengyp**（tangyu 非 sudoer）；密码只喂 stdin：`sudo -S -k ... < ~/.secrets/centos.key`。

## 一、一句话现状

M2 的**本机实验基本做完并落盘**：后端定案 **Xwayland(X11)+XTEST**；A3、分发验证、E4/F1、E6 均已有结论。~~剩两个尾巴（A11 `:2` 隐患 / B2 未收口）~~ —— **随"自持 / 自启"一并作废，见 §十一 · 11.3**。**没写任何生产代码。** 另：22:5x–23:2x 讨论由"目标才是约束"拉通**目标（`spec-screen-1.md` §0.0）+ 设计结论（§十一）**。

## 二、本轮（#16→#17）新增结论

| 项 | 结果 | 细节位置 |
|---|---|---|
| **B1 后端** | ✅ Xwayland(X11)+XTEST 三项全过（X11 起得来 / 树完整 382 / **bounds 随窗口平移=全局坐标** / **XTEST 文本逐字命中**） | exp-log §B1 |
| **A3 act element** | ✅ 重解析（窗口移动后仍点中）/ 子树 vs 全树（382节点573ms vs 1760节点2545ms）/ 200ms deadline 触发回退 | exp-log §P1·A3 |
| **P1 分发** | ✅ 1 个 `pipewiresrc`（单消费者）→ `tee` fan-out 3 个 appsink，**3/3 出帧** | exp-log §P1·分发 |
| **E4/F1 反检测（本机）** | ✅ 三配置（无 flag / 带 flag / 带 flag+a11y 客户端）**页面可见静态指纹逐字段一致** → flag 与 a11y 激活**无页面可见痕迹**；❌ 本机 `webgl=null`（无 3D，归 E1/A12） | exp-log §E4/F1 |
| **E6 humanization** | ✅ 73 点轨迹 + 非等间隔（18–298ms）+ 末端过冲回正 + 点击命中 | exp-log §E6 |
| ~~**A11 user unit / 自启**~~ | ❌ **作废**（自持 / 自启需求已撤，见 §十一·11.3）。原结论文本保留在下行历史里 | exp-log §A11 |
| ~~**A11 隐患（未解）**~~ | ❌ **作废**（是"自启"这条路的副作用；该路已弃，**无须解、无须绕**）。原记录：自启后只剩一个 auth 且只对 `:3` 有效、`:2` 连不上 | exp-log §A11 补充 |
| **B2 启动器** | 🔶 代码就位；~~mutter `:2/:3` 探活部分作废~~（§十一·11.3）；**"X11 上起 chrome"的用法保留** | exp-log §B2 |

## 三、已定案（**勿再重开**）

1. **浏览器后端默认 = Xwayland(X11) + XTEST**（§B1）。
2. **文本输入路线 = 键盘合成**（Chromium 不暴露可用 `EditableText`）。
3. **坐标前提 = 被测浏览器跑 X11**（a11y bounds 即屏幕像素坐标）。
4. **注入与观看解耦**：XTEST 不占 ScreenCast 流（流单消费者独占，A2）。
5. **架构 = 两模式 + 单操作者**（`handoff-screen-15.md` §四）。
6. **E4/F1 本机**：flag / a11y 在**页面可见面**上不露痕迹。
7. **E6**：humanization 可行（初步模型够用）。
8. ~~**A11**：用户管理器级自启成立~~ → ❌ **已作废**（"自持 / 自启"需求撤销，见 §十一·11.3）。

## 四、待做

**本机（我自主可做）**
- **B2 启动器**：**保留"X11 上起 chrome"**；**去掉 mutter `:2/:3` 探活**（那段随自启路作废，§十一·11.3），直接用自己会话的环境变量。
- 可选补测：反检测**性能侧信道量化**（多轮中位数）；E3 虚拟显示器**定制性**（早期遗留"待查"）。

**需 YZ**
- **A7**：图形登录 / VT 路径（需切 VT）—— ~~随 ssh + 按需模型作废~~；仅在要做"人机同屏"时才有意义。
- **旧 system 服务** `screenlab.service` / `screenlab-xvfb.service`（active+enabled，未动）——退役还是保留，待裁决（不阻塞）。

**需硬件**
- **E1/A12**：真 GPU 指纹（本 VM 无 3D，`webgl=null`）→ 换 3D 机器。**注：反检测已入目标（`spec-screen-1.md` §0.0），这条在范围内、不是可选。**

**设计讨论（等有数据/YZ）**
- "a11y 腿是否进 endpoint 接口"。
- 反检测目标强度（决定**是否值得换机**）。
- 撤销/抢占原语（可先做**无真实输入源的桩**）。

> **2026-09-21 22:5x–23:2x 讨论**：A11 `:2` 已完成第一轮定位（`screen-exp-log.md` §A11 隐患定位），但**随"自持 / 自启"整体作废**（§十一·11.3）；并由"目标才是约束"拉通目标（`spec-screen-1.md` §0.0）。**B2 保留起 chrome 的用法，去掉探活。**

## 五、环境现状（2026-09-21 21:46 只读确认）

> ❌ **本节的 `screenlab-shell.service`（persistent user unit）+ linger 路径已作废**（见 §十一·11.3）。下列相关条目**保留仅作历史，待清理**：
> `systemctl --user disable --now screenlab-shell`、`loginctl disable-linger tangyu`。

- **桌面**：~~`screenlab-shell.service`（**user, persistent**，`active` + `enabled`）+ `default.target Wants=screenlab-shell.service`~~ ❌作废；~~`MainPID=20907`…~~（历史）。
- **Xwayland（异常）**：日志 `Using public X11 display :2, (using :3 for managed services)`；**但只有一个 auth 文件且只对 `:3` 有效、`:2` 连不上**。→ X11 客户端目前只能用 `:3`。
- **chrome**：无残留（已清）。
- **旧 system 服务**：`screenlab.service` / `screenlab-xvfb.service` = active + enabled，占 `/run/screen/screen.sock`；**未动**。
- `loginctl`：tangyu `Linger=yes`；无 seat 会话 id 100。
- tangyu gsettings：`idle-delay=0`、`screensaver lock-enabled=false`、`toolkit-accessibility=true`。
- 临时 ACL `setfacl -m u:tangyu:rw /dev/dri/card0`（**重启失效**）。
- VBox 主机侧 3D 加速已开（YZ 改）。
- **临时**：`~/screenlab/` 已装 `screenlab-x11.sh` / `screenlab-chrome.sh`（+x）。

## 六、入口与命令

```bash
ssh tangyu@localhost
export XDG_RUNTIME_DIR=/run/user/1001 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus

# 桌面（持久 unit）—— ❌ 作废，勿再用（§十一·11.3）；清理：
#   systemctl --user disable --now screenlab-shell
#   loginctl disable-linger tangyu        # 需 zhengyp sudo

# 起 chrome（B2 保留部分；探活已作废）
~/screenlab/screenlab-chrome.sh "http://127.0.0.1:8765/"
```

## 七、已知坑（本轮新增，其余沿用 #16 §七）

- **显示选择**：Xwayland 有 **public（`:2`）** 与 **managed services（`:3`）** 两套；探活**不要盲扫**，优先解析日志里的 public display；**`:3` 上 chrome 会起来后退出**。
- **`/tmp` 下的脚本不能"原地 exec"**（`setsid /tmp/x.sh` → `权限不够`）→ 装到家目录，或 `bash <file>`。
- **`pkill -f` / `pgrep -f` 自伤**（含 ssh 整条命令行）→ `[x]` 写法 / `-x` / PID / 放进脚本文件。
- **D-Bus 信号需迭代 `GLib.MainContext`**（`PipeWireStreamAdded` 纯 sleep 收不到 → `NODE=None`）。
- 沿用：关闭 ScreenCast session 会崩 shell；headless 必须先关空闲锁定否则 ScreenCast 被拒；不带 `--force-renderer-accessibility` 就是空树；跨用户 `/tmp` 属主；ScreenCast `RecordMonitor`；`Introspect` 被封。

## 八、脚本索引（`screen-lab-verify/`）

| 文件 | 用途 |
|---|---|
| `a4-x11.sh` / `a4-extents.py` / `a4-keytest.py` / `a4-xtest.sh` | **B1**：Xwayland 后端验证（X11 起 chrome / extents 全局坐标 / XTEST 键盘） |
| `p1-start.sh` / `p1-a3.py` / `p1-a3.sh` | **P1·A3**（重解析 / 子树 / deadline） |
| `p1-fanout.py` / `p1-fanout.sh` | **P1·分发**（1 pipewiresrc → tee → N appsink） |
| `e4-fp.html` / `e4-serve.py` / `e4-fp.sh` | **E4/F1**（指纹页 + 三配置采集） |
| `e6-page.html` / `e6-serve.py` / `e6-move.py` / `e6.sh` | **E6**（轨迹页 + 缓动/抖动/过冲注入） |
| ~~`a11-setup.sh`~~ | ❌ **作废**（A11 自启，见 §十一·11.3） |
| `screenlab-x11.sh` / `screenlab-chrome.sh` / `b2.sh` / `b2-diag.sh` | **B2**：探活 + X11 chrome 启动器 + 验证/诊断 |
| `a4-page.html` / `a4-serve.py` / `a4-serve-t.py` / `a4-atspi.py` / `a4-values*.py` / `a4-iface*.py` / `gtk-entry.py` / `gtk-run.sh` | 早前 A4/值类控件/`EditableText` 实验 |
| `a2.sh` / `a2b.sh` / `screencast-mon.py` | ScreenCast 流复用（单消费者/并发） |
| `cleanup.sh` | 清残留 chrome / a4-serve / gtk-entry |

## 九、建议的首次动作

1. 读本文件 + `handoff-screen-16.md`（§〇·五）+ `handoff-screen-15.md`（§四）+ `screen-exp-log.md` 的 **B1 / P1 / E4-F1 / E6** 段；**目标读 `spec-screen-1.md` §0.0**。
2. **先看 §十一·11.3 作废清单**——A8 / A11 / `:2` 隐患 / systemd 装配 / `ensure` 命令 / "生命周期"话题**全部作废，勿再实验、勿再讨论**。
3. 然后进**设计讨论**（§四末三条）。

## 十、设计讨论清单（等 YZ，不阻塞实验）

- **a11y 腿是否进 endpoint 接口**（现抽象是"像素 + a11y + 输入"，a11y 是否作为接口的一等公民）。
- **反检测目标强度**（"像真人"要到什么程度 → 决定是否值得为 E1/A12 找 3D 机器）。
- **撤销/抢占原语**（可先做无真实输入源的桩）。

## 十一、设计结论（2026-09-21 22:5x–23:2x 讨论，YZ × AI）

**缘起**：① 由 A11 `:2` 隐患引出"为什么非要开机自启"；② 由 **"目标才是约束，实验与方案都不是"** 这条原则重新拉通目标。

### 11.1 目标层（唯一约束 · 全文见 `spec-screen-1.md` §0.0）
- 若干 agent，**各配一个电脑账户**、ssh 登录；**一个账户 = 一个图形界面**（多出来的是连进来的 client，不是界面）。
- agent **能操作图形界面且有反馈**；**像真人、不被检测**（这是前提，不是选项）；默认**不抢屏**，必要时与人共屏。
- 三种关系：**自操作 / 授权他 agent（显式、可收回）/ 与真人之间**。

### 11.2 已定结论
1. **单位 = 一个账号一个桌面（per-user endpoint）**。`tangyu` 只是**第一个样板，不是设计**。每个 agent 用自己的账号、以**自己的身份**起自己的界面。
   - 白送：X 显示 / a11y 总线 / `XAUTHORITY` / `WAYLAND_DISPLAY` 天然按 `/run/user/<uid>/` 隔离；**单操作者不变量自动成立**（XTEST 只作用自己的显示）；每 agent 独立浏览器 profile。
   - **不需要跨用户放权**；`tangyu` 也不再是必需。
2. **图形界面就是"开一个程序"**（terminal 模型）：需要时开、不用了关。**不引入"生命周期"这个设计层**。
   - 要延续的状态放**磁盘**（浏览器 profile 按账户固定复用），**不靠会话常驻** → "像真人"所需的稳定身份由此满足。**开 → 关 → 再开，状态不丢。**
   - "跟 ssh 同生灭"还是"断开可续" = **使用偏好**（要不要一个 `tmux` 等价物），不是设计决策。
3. **systemd / linger 退出架构**（作废清单见 11.3）。
4. **一账户一界面**；同一时刻可有**多观察者、至多一个操作者**（client 侧的事）。
5. **特例**：跨 agent 协助 = **显式交出该界面凭证**（`XAUTHORITY` + a11y 总线地址）；人看某 agent 的屏 = 对**那个界面**开只读调试口。
   - 量级警示：`XAUTHORITY` = 该屏**全权**（读屏 + 全键鼠 + 窗口数据），属"**endpoint 凭证交接**"。

### 11.3 ❌ 作废清单（**勿再重开、勿再实验、勿再讨论**）

| 作废项 | 原因 |
|---|---|
| **A8（reboot 自持）** | "自持"不是需求。**勿再提 reboot**。 |
| **A11（user unit 自启收尾）** | 同上，自启需求撤销。 |
| **A11 `:2` 隐患的全部排查** | 是"自启"这条路的副作用；该路已弃 → **无须解、无须绕**。 |
| **"`ensure` 命令"（跨用户授权 + 幂等 + 健康检查 + `flock`）** | 跨用户动机消失（11.2·1）。 |
| **`systemd-run --user` / user unit / `WantedBy=default.target` 作为装配形态** | 只在"要自启 / 要活过 ssh"时才需要；两条都撤。 |
| **`loginctl enable-linger tangyu`** | 同上，**待清理**：`loginctl disable-linger tangyu`。 |
| **`screenlab-shell.service`（persistent user unit）** | 同上，**待清理**：`systemctl --user disable --now screenlab-shell`。 |
| **"不做不用就销毁"** | 那是"状态在会话里"的假设下才成立；profile 落盘后**关了再开不丢**，可以随用随关。 |
| **"桌面生命周期"这个话题本身** | 过度设计；按 11.2·2 处理即可。 |
| **`screenlab.service` / `screenlab-xvfb.service`（旧 system 服务）** | 属早期 Xvfb 原型，与现路线无关（是否退役仍待 YZ，但不阻塞）。 |

### 11.4 仍然有效（勿误伤）
- per-account 隔离；按需开 / 关；**浏览器 profile 落盘**；单操作者不变量；凭证交接的量级警示。
- **反检测已入目标**（`spec-screen-1.md` §0.0）→ **E1/A12（真 GPU / 真显示器）在范围内**，不是可选。

**未证 / 待议**：① per-account 界面用哪种**轻形态**（`Xvfb + openbox` 原型 vs mutter）——同时权衡**反检测痕迹**；② 跨 agent 授权是否需配合"撤销 / 抢占"原语；③ 反检测**强度**（对谁、到什么程度）。
