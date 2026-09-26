# handoff｜交接：人侧 viewer 验收（第十二轮）· 2026-09-22 #25

> ➡️ 接续 `handoff-screen-24.md`（第十一轮）。新会话从 #25 读起。
>
> **本轮任务（YZ 指定）**：**代码已提交，先不写码**。与 YZ 一起**验收已实现的功能**——
> 逐条对照"真正实现 / 只是骨架 / 没做"，把要补的排出来。讨论清楚前别动手实现。
>
> **新会话只读四样，别多读**：
> 1. **目标（唯一约束）**：`handoff-screen-18.md` **§5.1**。
> 2. **本路线方案**：`handoff-screen-18.md` **§5.2 / §5.3 / 六 / 七**；两个 spec：`spec-screen-client-api.md`（动词面，含 `yield` 与 §4·15）、`spec-screen-ledger.md`。
> 3. **读法纪律**：`handoff-screen-18.md` **§5.0**（双栏 + 反证句 + 作废即删名）。
> 4. **代码**：`cogos/screenlab/`（分支 `feat/screenlab-p2`，**本轮已提交 `0670849`**）。
>
> ⚠️ `spec-screen-element-act.md` **整份作废**；别读 `handoff-15/16` 的目标与架构表述；别用 `screenlab/install/{install.sh,*.service,xvfb-start.sh}`（旧 Xvfb/systemd 路线，已废）。
> ⚠️ a11y 已在 #23 整体剥离；#22 §三/§四/§五·1·3·4 的"树 = 可选语义索引"口径**已推翻，别沿用**。

## 一、本轮（第十一轮）交付了什么

**人侧 viewer**：YZ 在浏览器里**看** agent 操作 agent1 的屏，并能自己**操作**（关系③b + 介入）。实现见 `screenlab/viewer/`：

- `bridge.py` — stdlib `http.server` 桥。**持一条** `screen/1` 连接（世代是连接级的，看与操作必须同连接），把页面的 HTTP 请求翻译成：
  - `GET /` 页面；`GET /frame?since=` → `capture`（变了回 PNG，没变回 JSON；响应头带 `X-Snapshot-Id/X-Frame-Hash/X-Changed/X-Dead`）；
  - `GET /status` → 输入持有者 / 本通道位 / 指针 / 焦点；
  - `POST /act` → `act`（pointer/key/type/scroll），世代过期**自动补一次 capture 再重试一次**。
  - 桥以 **guest** 身份 `open(credential=token)`；`revoke` 后每次调用失败 → 标 `dead`，页面显示"已断开"。
- `page.html` — 暗色页面，0.4s 轮询渲染；点击=左键、中/右键、滚轮、键盘（Enter/Backspace/方向键、Ctrl+组合已映射；可打印字符缓冲后走 `type`）。左上角显示 `权限 / 输入：我·空·agent 持有`。
- **传输不入方案**（§5.2·E）：桥只 bind 本地，由外部（隧道 / tailscale）暴露。

**同时把上一轮未提交的东西一起提交了**（`0670849`）：`yield` 动词（`daemon.op_yield` + `client.yield_input`）、`x11-windows` 取帧后端、`tests/screenlab/e2e/guest_intervention_e2e.py`、`test_ledger.py` 的让位用例、`install.ps1`（上轮遗留）、`ClientError` 带 `error/detail` 属性。

## 二、验收清单（**供本轮与 YZ 逐条对**）

### A. 已实现且真机验证过（可直接验收）

| # | 功能 | 证据 |
|---|---|---|
| A1 | 页面 + 桥四个端点 | 单测 `tests/screenlab/test_viewer.py`（9 项）；curl 实测 |
| A2 | guest 凭证接入（`open(credential)`，subject=YZ） | 桥启动日志 `bits{capture,input}`、`subject=YZ` |
| A3 | 取帧：1920×1080 PNG；`since_hash` 命中则不传图 | 实测 129KB→未变 246B JSON |
| A4 | 操作：`pointer`(click/move)、`scroll`、`type`、`key` | YZ 页面里实测（滚动 Chrome、点链接、指针移动可见） |
| A5 | `status` 输入归属 / 权限位（页面对应显示） | 实测 holder 变化 |
| A6 | `revoke` 本地立即失效 | 实测：`/status`→`no_channel`、`/frame` `X-Dead:1` |
| A7 | owner `yield` / guest 接 / owner 下次 `act` 自动取回 | `guest_intervention_e2e.py` 10/10；并实跑 hold→yield→(free)→reclaim |

### B. 有实现但**没真机验证 / 只是骨架**（重点讨论）

| # | 项 | 现状 |
|---|---|---|
| B1 | **拖动**（pointer move/press/release） | **没做**。`act pointer` 只有 `button+clicks`（`clicks=0` 可当 move 用），没有 press/release ⇒ 选字、拖窗、拖滑块做不了。handoff-24 §五·4 的待裁决项 |
| B2 | **非 Chrome 窗口看不见** | **实测确认**（见 §三）。GTK/VTE 窗口内容抓不到：`xfce4-terminal` 全黑；`zenity` 对话框只有图标/按钮、**文字缺失**。Chrome（软件渲染、客户端自绘外框）正常 |
| B3 | **只读 `{看}` 通道** | 代码支持（无 input 位即拒 `act`），**没单独验** |
| B4 | **中途到期 / 被 revoke 的页面行为** | revoke 验过；**ttl 到期**在页面上的表现没验 |
| B5 | **远程接入**（隧道 / 非本机浏览器） | YZ 这次是**本机 Chrome 经 127.0.0.1** 接的；跨机隧道路径没走过 |
| B6 | **性能** | `x11-windows` 每个窗口 spawn 一个 `gst-launch` 取帧，页面 0.4s 轮询 ⇒ 窗口一多、负载飙到 load 10+，还出现过 gst 卡住。轮询频率 / 合成开销要重新定 |

### C. 完全没碰（对着目标）

| # | 项 |
|---|---|
| C1 | **目标 3 加固**（真 GPU 渲染、时序拟真）——Linux 上最大缺口 |
| C2 | **③a 真人在自己机器装服务、agent 接入**——没验 |
| C3 | 目标 4 的后半（不抢物理屏已有一半）与"人能介入"以外的形态 |
| C4 | 工程收尾：blob 无 GC、`_geometry` 缓存不失效、授权只到账户级、冷启动 ~1 分钟（handoff-24 §五·7·8） |

## 三、`x11-windows` 的实测边界（本轮新发现，B2 的依据）

现象 + 排查：

- `xfce4-terminal` 起来了（X11 窗口存在，标题 `agent1@10:~`），但页面里**全黑**（只有外框和滚动条）。
- 我一度以为是"WM 把客户端 reparent 进外框、后端只抓 root 直接子窗口"⇒ 改成**递归遍历窗口树**再合成——**没有改善**（终端仍黑），**该改动已回退**（不在 `0670849` 里）。
- 用 `gst-launch ximagesrc xid=<终端窗口>` 单独抓该窗口：**成功返回但内容是黑的**（2851B PNG）。⇒ **不是 reparent 的锅，是这些窗口的像素本身就取不到**。
- 对照 `zenity`（GTK3）：**外框、图标、按钮出来了，文字没出来**。⇒ 不是 VTE 独有，是**一类 GTK/GL 渲染窗口**在本机 mutter+Xwayland 下取帧不全（怀疑 EGL/GL 面不在 X 合成器可读的 pixmap 里；`gpu-process --use-gl` / `--ozone-platform=x11` 等线索）。
- 结论：**"在 viewer 里看到一个终端"目前被取帧后端挡住**，不是 viewer 的问题。候选方向（**待 YZ 定，不要直接做**）：换用 XComposite `NameWindowPixmap` 取窗口像素；或让目标 app 走软件渲染（关 GL）；或换一个用核心 X 绘制的终端。

## 四、本轮踩到、值得记的坑

1. **owner 之间不互相抢占**：两个 owner 通道同时操作会 `input_taken`（`ledger.take_input` 里 owner 抢占只对 guest 生效）。演示时我用一个长驻 owner 控制器持输入，导致 YZ 点了没反应——**页面对非持有者的输入是直接忽略、不回服务端**，看着像坏了。要不要改成"照样发 `act` 并把 `input_taken` 显式提示"，是个 UX 待裁项。
2. **占位现象**：页面轮询 + 每窗一个 gst，会让机器负载飙高，甚至 gst 卡住、拖慢整个测试套件。收尾前我已停掉桥/控制器/终端。
3. 本机 `/home/zhengyp` 是 700，agent1 读不到 repo ⇒ 直接跑后端测试要用 `env PYTHONPATH=<repo> /usr/bin/python3`（root，带 PIL），或部署后再测。

## 五、环境 & 常用命令（沿用 #24 §六，daemon pid/display 以现测为准）

```bash
# 部署（改了 screenlab/ 才需要；否则 daemon 跑旧包）
pkill -u agent1 -f "screenlab.service.cli daemon"; sleep 2
sudo bash cogos/screenlab/install/account-install.sh agent1
sudo bash cogos/screenlab/install/session-start.sh agent1     # 需要时 --restart

# 现测环境（本轮实测）：socket /run/user/1003/screenlab.sock，display :6，
#   xauth /run/user/1003/.mutter-Xwaylandauth.N9TAW3，account agent1，
#   capture_backend x11-windows，act_backend xdotool，pid 42298（以现测为准）

# 跑 viewer（host 侧，能连到 socket 的地方；局域网/隧道由外部提供）
sudo env PYTHONPATH=/home/zhengyp/work/A/cogos /usr/bin/python3 \
  -m screenlab.viewer.bridge --sock /run/user/1003/screenlab.sock \
  --credential <token> --host 0.0.0.0 --port 8800
# 凭证：owner 侧发一次性 {看,操作}
sudo env PYTHONPATH=/home/zhengyp/work/A/cogos /usr/bin/python3 \
  -m screenlab.service.cli --socket /run/user/1003/screenlab.sock \
  grant --bits capture,input --ttl 3600 --once

# 单测（必须 3.11）
python3.11 -m pytest tests/screenlab/test_viewer.py -q     # 9 passed
python3.11 -m pytest tests/screenlab -q
python3.11 -m pytest tests -q                              # 之前 1218 passed（本轮因机器负载没跑完全量，见 §四·2）

# e2e（见 tests/screenlab/e2e/README.md）
sudo env PYTHONPATH=/home/zhengyp/work/A/cogos \
  /usr/bin/python3.11 tests/screenlab/e2e/guest_intervention_e2e.py --sock /run/user/1003/screenlab.sock
```

**防火墙**：`firewalld` 只放行 22/4096；直连 8800 不通 ⇒ 用 SSH 隧道（`ssh -L 8800:127.0.0.1:8800 zhengyp@<host>` 后开 `http://127.0.0.1:8800/`），或临时开端口（本轮没开）。

## 六、纪律（沿用 #22 §九 / #24 §七）

- **双栏**：`[目标]` / `[方案]`；只有 `[目标]` 有否决权。
- **反证句自检**：说"因为已验 / 已定案 / 以前这么做"就暂停。
- **机制不代判**：不代判动作生效，也不代判"看什么"。
- **作废即删名**：`热订阅` / `关闭重开` / `Xvfb 作起步形态` / `网络/NAT/打洞` / `a11y` / `元素表` / `act element` / `人一动手即夺回输入`（仅 ③a 成立）。
- 一次只跑一条实验命令；`sudo` 密码只喂 stdin（`< ~/.secrets/centos.key`），**注意重定向位置**。
- 改了 `screenlab/` 的代码必须**重新 account-install + 重启 daemon**。

## 七、给新会话的第一句话

代码在 `0670849`，工作树干净。**先别写码**：拿 §二 的清单跟 YZ 逐条过，确认 A 里哪些他真正验收了、B 里哪些要补、C 里哪些要议；把"要补什么、补到什么程度"谈定，再决定动哪块。
