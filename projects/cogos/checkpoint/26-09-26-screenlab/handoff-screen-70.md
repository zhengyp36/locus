# handoff｜交接给新会话 · #70 → #71（screenlab 整合 · X11 切换）

> 规则 / 环境不在本文件——先读 `screenlab-rules.md`（含纪律）。
> 本会话（#70）：把 `../checkpoint/tools` 脚本能力整合进产品 `screen/1`（客户端整合 + 脚本归位）；
> Windows + Android 地面真值回归 **ALL PASS** 并 commit+push。**X11 切换未做**，交给本后继（天亮验）。
> 交接原因：ctx 超 150K（纪律）。

---

## 复制这段作为新会话的第一句话

```
接 #70。screenlab 整合已完成 Win+Android 回归并 push（cogos c9d6ad6 + fa49a89, origin/feat/screenlab-p2）。
本会话任务 = ① X11 切换：把 tools/x11.sh 的抛式自管 Xvfb(走 checkpoint) 换到产品图形面
（screenlab/install/session-start.sh create 起的账户级 Xvfb surface，经产品 screen/1 unix socket），
imgctx --backend x11 走 ScreenChannel + ssh StreamLocal 隧道，x11_selftest.py 形状不变跑通；
② 若 X11 通，收尾更新 tools/README + work log。
动手前先按序读（纯文本）：1. ../checkpoint/screenlab-rules.md；2. ../checkpoint/screenlab-work.md §状态；
3. ../checkpoint/handoff-screen-70.md（本文件，含已完成细节与 X11 待办）。
纪律：10min 闹钟；ctx ≥150K 交接；裁决由目标（spec-screen-1.md §0.0）；阻塞→飞书通知 YZ 后做不阻塞的；
允许 commit/push（不 tag），提交前跑测试。
⚠️ 文档是二手描述，动手前以代码/实测为准。
```

---

## #70 已完成（素材）

- **客户端整合（核心）**：`screenlab/tools/imgctx.py` 的 `look/act` 改走产品 `screen/1`
  （`cogos/agent/impl/graphics.py::ScreenChannel`），不再 shell 到后端脚本；`see/mark/coord` 仍走
  `image_ctx`，作用在 `blob_get` 拉回的帧上（引擎未改）。
  - `look`：`capture(since_hash="")`（恒取新帧）→ `save_frame` 到 `<root>/frames/frame-look-<pid>-<ns>.png` → `see PATH:`。
  - `act`：新连接重抓（铸本连接 `snapshot_id`）→ `client.act("pointer", snapshot_id, x=norm,y=norm)`
    → `_capture_settled`（有界重抓确认落点帧）→ `see` 落点帧 + `mark` landing。
    另算 `change.diff_bbox(模型看的那帧, 新帧)`，**只报告** `stale`/`drift_bbox`（含目标点 = stale），**不拒**
    （设计 §16：机制给变化、模型决断；dxcam 缓存/窗口重绘会误伤硬拒）。
    ⚠️ **遗留**：真正的"act 只作用在模型看到的那一帧"需**持久连接**（跨 CLI 调用保住同一 `snapshot_id`），本会话用重抓近似；若 YZ 要硬保证，下一刀做客户端 broker。
  - 端点：`--endpoint`(unix:/tcp:) / `--key` / `--ssh`([user@]host[:port])；默认按 `--backend` + env
    （`SL_*_ENDPOINT`、`SL_AGENT_KEY`、`SL_WIN_SSH`、`SL_SSH`）。`SL_ANDROID_ENDPOINT`、`SL_ANDROID_AGENT_KEY` 已加进 `env.sh`。
- **Android 回归 ALL PASS（3/3 稳定）**：走 assist app 的 `screen/1`（`tcp:192.168.1.175:8901`，auth key
  `screenlab/tools/keys/android_agent.key`＝手机 registry 里 alias `kilocode` 的密钥；`android.sh consent-auto` 免人工同意）。
  `device=[338,2125]` = uiautomator Chrome 图标真值，Chrome 变前台。
  - **caveat（产品侧已知）**：assist app 的 MediaProjection `grabPng` 在切 app 后可能滞后数秒（`acquireLatestImage` 返回 null 时回缓存帧）。
    故 `act` 的落点帧是 best-effort（`_capture_settled` 有界重抓，命中落点即返）；selftest 的"屏幕变化/落点 bbox"改用
    **独立 adb 两帧**（`pre_adb`/`post_adb`）判定，稳定性也只看**目标区域**（launcher 顶部有常驻动画，整屏 diff 不适用）。
- **Windows 回归 ALL PASS**：走 session 内产品 daemon 的**测试实例**（loopback TCP `127.0.0.1:19911`、`--consent auto`、
  同一 registry），经 ssh 隧道（`--ssh assist@100.112.50.115`）。`windows.sh it-daemon start|stop`
  （新增 `win/62c/it_daemon.ps1`，Task Scheduler COM 在 session 7 起 `python -m screenlab.service.cli --tcp … daemon`）。
  未动真 daemon（`127.0.0.1:9911`，`config.json` consent=event，保持原样）。`device=(900,550)`=Tk 靶真值，READY→HIT。
- **脚本归位**：整个 `../checkpoint/tools/` → `cogos/screenlab/tools/`（排除 `keys/`、`blobs/`、`.imgctx/`、`__pycache__`、
  `.pytest_cache`、`state.json`、`android-probe/{build,runs}`；新增 `screenlab/tools/.gitignore` 忽略 keys/blobs 等）。
  `keys/{agent.key,android_agent.key}` 仍在本地（未入库）。
- **提交**：`c9d6ad6 feat(screenlab): drive the vision loop through the product screen/1 service`
  + `fa49a89 fix(screenlab): settle the act confirmation; report drift instead of refusing`
  均已 push（`origin/feat/screenlab-p2`）。产品测试 `tests/screenlab + tests/image_ctx` **71 passed**；
  `imgctx_selftest.py` ALL PASS（新位置）；Android selftest 3/3 ALL PASS；Windows selftest ALL PASS（新位置）。
- **注意**：`windows.sh` 的 `SL_WIN_ENDPOINT` 默认（`imgctx`）仍是 `tcp:127.0.0.1:9911`；selftest 显式用 19911。
  真 daemon 9911 需人工同意（consent=event），不用于无人值守回归。

## #70 未做 → #71 的 X11 切换

- 现状：`tools/x11.sh` 在目标机自管抛式 Xvfb `:101` + openbox + zenity（`sl1-*` systemd-run 瞬态单元），
  `x11_selftest.py` 通过它做 look→mark→coord→act。**未接产品图形面**。
- 目标：改用产品 `screenlab/install/session-start.sh create <account>` 起的账户级 Xvfb surface
  （systemd user unit 组；socket 在账户 `XDG_RUNTIME_DIR/screenlab.sock`），`imgctx --backend x11` 用
  `ScreenChannel` + `--ssh zhengyp@100.100.137.78`（StreamLocal 隧道）连 `unix:/run/user/<uid>/screenlab.sock`。
  账户用 `human`（uid 1002）：`SL_X11_ENDPOINT=unix:/run/user/1002/screenlab.sock`，`SL_SSH` 已指 `zhengyp@100.100.137.78`。
  - 先 `sl_root`/`sl_remote_vars` 以 human 身份跑 `install/session-start.sh create`（或 root 带账号名）；
    确认 `screenlab.sock` 在听、`imgctx look` 出 1280×800（或 session.env 记的分辨率）。
  - `x11_selftest.py`：把 surface 启停从 `x11.sh start` 换到产品 session；zenity 点击靶仍在（真值 (726,458) 视分辨率而定，重算真值）。
  - 地面真值/z 判据形状不变（coord px==真值 / act device==coord / zenity 1→0）。
- 若 X11 通 → 收尾：README 的 Slice 1 示例改产品路径；work log §状态补 X11。

## 锚

- 规则：`../checkpoint/screenlab-rules.md`；工作单：`../checkpoint/screenlab-work.md`；目标：`../checkpoint/spec-screen-1.md` §0.0
- 代码：`cogos/screenlab/tools/{imgctx.py,*_selftest.py,env.sh,windows.sh,win/62c/it_daemon.ps1}`、
  `cogos/screenlab/{proto/client.py,service/daemon.py,install/session-start.sh}`、`cogos/agent/impl/graphics.py`
- 环境事实：`screenlab/tools/env.sh`（`SL_*`）；Android `192.168.1.175:5555`；Windows `100.112.50.115`（assist/zhengyp）；CentOS `100.100.137.78`
