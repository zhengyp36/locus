# screen-lab（screen/1 原型）

最小 `daemon + client + CLI`，实现 `spec-screen-1.md` 的 mechanical 子集。
**代码放哪未定**（裁决 7：新仓 `screen-lab` vs cogos 子包），此处是**暂存原型**。

## 文件

- `screenlab/framing.py` — 换行分隔 JSON + 可选二进制尾巴（响应头 `bytes_len`）。
- `screenlab/backends.py` — X11 adapter：抓屏 `Pillow`（首选）/ ImageMagick `import`（兜底）；注入 `xdotool`；`xrandr` 列显示器。
- `screenlab/backends_android.py` — Android adapter：抓屏 `adb exec-out screencap -p`；注入 `adb shell input tap/swipe/text/keyevent`；`wm size/density` 列显示器。
- `screenlab/daemon.py` — `screen/1` 服务端（Unix socket、快照世代、内容寻址 blob）。
- `screenlab/client.py` — 薄传输封装（无平台逻辑）。
- `screenlab/cli.py` — CLI；`daemon` 子命令 + 各 op。

## 跑

```bash
# 起 daemon（必须在该会话内；:0 需 XAUTHORITY，:99 不需要）
python3.11 -m screenlab.cli daemon --display :0 \
  --xauth /run/user/1000/gdm/Xauthority \
  --socket /tmp/kilo/screen-lab/run/screen-0.sock \
  --blob-dir /tmp/kilo/screen-lab/blobs

# 查询
python3.11 -m screenlab.cli --socket <SOCK> ping|caps|displays|state [--frame]
python3.11 -m screenlab.cli --socket <SOCK> see [--region x,y,w,h] [--max-dim N] \
  [--since-hash H] [--wait-stable SEC] [--out PATH]
python3.11 -m screenlab.cli --socket <SOCK> blob-get --sha SHA --out PATH

# 操作（--snapshot 必须用最近一次 see/state 返回的 snapshot_id）
python3.11 -m screenlab.cli --socket <SOCK> act pointer --x N --y N [--button 1] [--clicks N] --snapshot SID
python3.11 -m screenlab.cli --socket <SOCK> act key   --key ctrl+l --snapshot SID
python3.11 -m screenlab.cli --socket <SOCK> act type  --text "..." --snapshot SID
python3.11 -m screenlab.cli --socket <SOCK> act scroll --dy -1 --snapshot SID
python3.11 -m screenlab.cli --socket <SOCK> act focus --window-id WID --snapshot SID
```

`--clicks 0` = 只移动指针不点击（唤醒屏幕用）。

## Windows

约束与做法见 `../spec-screen-1.md` §5.7。要点：

- daemon 必须跑在**目标用户的交互会话**里（Session 0 / sshd 无桌面）——用该用户的启动项拉起；
- 进程启动即开 **per-monitor DPI 感知**，否则图像坐标与 `SendInput` 空间差一个缩放比；
- 传输用 **loopback TCP**（Windows OpenSSH 不支持 AF_UNIX 转发）：

```powershell
# 目标机（交互会话内，启动项）
pythonw.exe daemon.pyw          # 内含 --tcp 127.0.0.1:9911
```
```bash
# 本机
ssh -N -L 9911:127.0.0.1:9911 screen@HOST &
python3.11 -m screenlab.cli --tcp 127.0.0.1:9911 see --out win.png
```

已实测（Surface，1920×1280 @150%）：`see → act key/type/pointer → see` 闭环，Win+R 起 notepad 并打字成功。

## Android

约束与做法见 `../spec-screen-1.md` §5.8、`../checkpoint-5.md`。要点：

- **daemon 跑宿主**（`--backend android`），设备侧只有 `adbd`；这是唯一不需要"daemon 在目标会话内"的平台。
- **坐标三方同空间**：`screencap` 像素 = `input` 坐标 = `uiautomator bounds`，无 Windows 式 DPI 偏移。
- 设备侧需开 USB 调试并授权；宿主需 `adb`（EPEL `android-tools`）+ udev 规则。

```bash
# 宿主起 daemon（无需 --display）
python3.11 -m screenlab.cli --backend android daemon \
  --socket /tmp/kilo/droid/run/screen.sock --blob-dir /tmp/kilo/droid/blobs

# 指定设备（多设备时）
python3.11 -m screenlab.cli --backend android --adb-serial <SERIAL> daemon --socket ...

python3.11 -m screenlab.cli --socket <SOCK> see --out droid.png
python3.11 -m screenlab.cli --socket <SOCK> act pointer --x 540 --y 2012 --snapshot SID
```

- `act key` 收 Android key 名（`home`/`back`/`enter`/... 见 `backends_android.py::_KEYMAP`）或 `KEYCODE_*`。
- `act type` 仅 ASCII，空格自动转 `%s`；中文/特殊字符不可用。
- `mode=tree` / `act element`（a11y）**未实现**，但 `uiautomator dump` 通路在 Android 上可用、坐标与像素同空间。

已实测（华为 `MAR-TL00`，Android 10 / EMUI 10，1080×2312）：时钟「秒表」闭环 `see → act pointer 开始 → see`（`00:00.00 → 00:01.24`）→ 暂停 → `00:02.55`；过期快照被拒、`since_hash` 回 `unchanged`、blob 内容寻址一致。

## 协议要点（与 spec 对应）

- **快照世代**：`see`/`state --frame`/`act` 各签发新 `snapshot_id`；`act` 校验必须是**最新**一代，否则回 `stale_snapshot`。`act` 完成后自动抓一帧、签发新世代。
- **变化感知**：`see --since-hash H` 若帧哈希相同 → `unchanged:true` 且不下发 blob。
- **blob 内容寻址**：`blobs:[sha]`，`blob_get(sha)` 取字节；同帧重复 `see` 不新增 blob（天然去重）。
- **不推事件**：靠 `frame_hash` + `wait_stable`。
- `mode=tree` / `act kind=element`（a11y）**未实现**（spec §10 裁决 8 未定，亦未做 a11y 实测）。

## 验收（2026-09-20 LLM 在环）

两环境各起 daemon，用 CLI + 读图跑"看 → 点 → 再看"：

- **`192.168.1.212:99`（Xvfb + openbox + chrome demo.html）**：完整闭环通过——
  `see`（输入框含 "hello act ok"）→ `act pointer` 点输入框 → `act key ctrl+a` → `act type "hello from screen/1 daemon"` → `see --wait-stable 2`
  确认输入框变为新文本；`frame_hash` 由 `2b03…` → `a132…`。
  另验：`see --since-hash` 回 `unchanged:true`；旧 `snapshot_id` 的 `act` 被拒（`stale_snapshot`，exit 1）；`state --frame` 拿到 `focus={window_id,title:"demo.html"}`（openbox 在，WM 前置满足）；`blob_get` 取回的 PNG 与原文件 `cmp` 一致。
- **本机 `:0`（GNOME on Xorg）**：起先处 GNOME 锁屏，用 `act type`+`Return` 输入密码解锁后跑完整闭环——
  `see` → `act pointer` 点顶栏时钟 → `see`（日历/通知面板展开）→ `act key Escape` → `see`（面板关闭，`frame_hash` 回到点击前值）。
  另验 `state --frame`、`act pointer --clicks 0`。
- **观察（值得进 spec）**：`act` 完成时抓的那一帧**可能早于 UI 渲染**（实测：`key Escape` 后 `act` 回的 `frame_hash` 仍是面板打开时的 `71f6…`，随后 `see --wait-stable` 才拿到关闭后的 `b5ea…`）。→ `act` 的返回帧只能当"提示"，**要判断稳定态必须再 `see --wait-stable`**。

后端：两机均命中 `capture_backend=pillow`（212 的 python3.9 也有 Pillow）、`act_backend=xdotool`。

- **Windows（`screen` 专用标准账户，1920×1280 @150%）**：`pythonw` 在交互会话（SessionId 1）里跑 daemon，loopback TCP + `ssh -L` 隧道；`see` 抓到桌面 → 点开始按钮（图像坐标 `618,1258`）弹出开始菜单 → `Win+R` 起 notepad → 打字 75 字符成功。DPI 修复前后对比：`displays` 由 `1280×853` 变为 `1920×1280`，点击由错位 1.5× 变为精确命中。

## 安全备注

- `act type` 的响应**只回 `text_length`、不回文本**，避免密码等经工具输出外泄。
