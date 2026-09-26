# handoff｜交接给新会话 · 2026-09-25 #48

> 接 #47。本会话 = 与 YZ 定 **E3 真人端入口最终形态**，并落 **E3-a（无窗口托盘入口 + 装配）** 与 **E3-c（物理热键收回，分源）**。
> 全部代码改动**未 commit**（YZ 未定）。**下一会话：补完 E3-b（地址显示）+ 把入口收进 install-machine；再做 E4（YZ 体验验收）**。
> **规则/环境不在本文件**——先读 `screenlab-rules.md`。

---

## 复制这段作为新会话的第一句

```
先按序读三个文件，再动手：
1. ../checkpoint/screenlab-rules.md（规则，先读）
2. ../checkpoint/screen-assist-status.md —— 看 §0「切会话须知」+ §2 路线 + §3 阶段表 + §4 进展
   （本会话的 E3 定稿与 E3-a/E3-c 都记在里面）
3. ../checkpoint/codebase.md（代码认知基线；本会话新增了 screenlab/service/consent_app.py、
   presence.py 的热键解析、daemon._physical_takeback——见版本戳"未 commit"清单）

状态：Goal 2 / 关系 3a。E1/E2 过。E3 入口形态已与 YZ 定稿并落地 E3-a + E3-c；
只差 E3-b（协助地址显示）+ 把 launcher 收进 install-machine。之后 E4（YZ 下场）+ E5（提交）。

代码：../cogos @ feat/screenlab-p2，全部改动未 commit（见 codebase.md 版本戳）；先别 commit。
靶机：surface 100.100.137.78，human@:0（桌面是 **XFCE**，不是 GNOME）；
      daemon 由 `screenlab open`（裸调，复用 ~/.config/screenlab/session.env）起，
      带 --presence --tcp 100.100.137.78:8911 --auth <registry> --consent event；
      真人同意入口 = 托盘 helper（screenlab-assist）。

E3 最终形态（**已定，勿再重议**；依据 §0.0 + 易用性 + design §4.7）：
- 启动：桌面「启动协助」双击（或登录自启）→ 起 = 守护 + 托盘，一起；退出 = 停整套（= 不可被协助）。
- 状态：托盘**状态灯**（未协助 / 有请求 / 协助中）；无窗口。
- 同意：请求 → 桌面**弹窗**。
- 拿回：**物理热键 Ctrl+Alt+Shift+Escape**（主，分源；env SCREENLAB_TAKEBACK_KEYS 可覆盖）+ 托盘菜单（辅）。
- 管理（起停/看地址/看状态）走 **ssh**；桌面不放命令式入口。

下一步（按此，别发散）：
- E3-b：真人侧显示"协助地址"（读 session.env 的 SCREENLAB_TCP）；给默认端口，减少人工对齐。
- 把入口收进仓库：launcher（/usr/local/bin/screenlab-assist-app + ~/Desktop/screenlab-assist.desktop）
  现在是我在靶机上临时放的，应进 `screenlab/install/` 并由 install-machine 生成。
- 然后 E4（YZ 下场：真鼠标拿回 + 体感）+ E5（提交/tag/回写，待 YZ）。

纪律：目标裁决（spec-screen-1.md §0.0）；能推的自决并记进 status；命令走 terminal（非阻塞）；
     不 commit；验收用公开入口 + 地面真值（import -window root / xdotool），不用自写 e2e 自证。
     靶机屏幕会 DPMS 熄灭 → 先 `xset dpms force on` 再用一次 XTEST 键（xdotool，不会触发分源）唤醒后抓屏。
```

---

## 本会话做了什么（给人类的摘要，不必复制）

- **E3 定稿**（与 YZ 对齐，写进 status §2/§4）：桌面只留状态灯；操作入口 = 弹窗 + 物理热键；管理走 ssh；
  启动支持"双击/登录自启"，退出 = 停整套。理由含 `design §4.7`（点图标收回与 agent 注入共用输入流，不可靠）。
- **E3-a**：新增 `cogos/screenlab/service/consent_app.py`——无窗口 Gtk 托盘入口：状态灯 + 弹窗同意 +
  右键"收回协助/退出"；`--manage-daemon` 启动时 `screenlab open`、退出时 `screenlab close`（SIGTERM 也走退出）。
  `cli.py` 加 `consent --popup`（zenity）；`install/screenlab` 透传 `--popup`。
- **E3-c**：`screenlab/service/presence.py` 在 `xinput test-xi2` 流里解析物理按键（`EVENT type` + `detail`=keycode，
  维护按下集合），命中约定组合回调；daemon 接 `on_takeback → revoke_all()`（同 `consent --cancel`）。
  默认键 `Ctrl+Alt+Shift+Escape`（keysym，经 `xmodmap -pke` 解析）。**分源**：只认非 XTEST 源。
- **靶机 ad-hoc（待收进仓库）**：`/usr/local/bin/screenlab-assist-app`（wrapper）、
  `~/Desktop/screenlab-assist.desktop`（Name=启动协助）。
- **验证（真机）**：托盘图标随进程出现/消失（面板托盘区 on/off 差分命中 `(1494,0,1707,26)`）；
  启动 → `screenlab-assist`+`screenlab-attach` active；退出 → attach inactive；
  物理热键（宿主 `VBoxManage keyboardputscancode 1d 38 2a 01 81 2a b8 9d`）→ 连接中 agent 立即 `channel_closed`。
- **插曲/坑**：桌面是 **XFCE**（非 GNOME，`xfdesktop` 原生显示桌面图标）；`xinput test-xi2 --root` 同一时刻
  只能一个客户端（daemon 的 PresenceMonitor 已占），所以热键必须并进该 monitor，不能另起一个 test-xi2。

## 锚

- 活文档/路线：`screen-assist-status.md`（§0/§2/§3/§4）
- 代码认知：`codebase.md`
- 设计：`design-screen-assist.md`（§3.2 consent hook；§4.7 收回分源）
- 实验：`screen-assist-exp-log.md`（§5/§6/§7）
- 目标：`spec-screen-1.md` §0.0
- 上一轮：#47 `handoff-screen-47.md`
