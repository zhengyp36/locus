# handoff｜交接给新会话 · #64 → #65（Slice 1 X11 闭环）

> 规则 / 环境不在本文件——先读 `screenlab-rules.md`。
> 本会话（#64）：Slice 0（image_ctx state 持久化 + 薄 CLI）**完成**；Slice 1（X11 看/指/点闭环）**已跑通手工与 CLI 闭环**，自测脚本未写。
> **不要回读本会话 transcript**：任务态已落 `screenlab-work.md`，文件是唯一依据。

---

## 复制这段作为新会话的第一句

```
接 #64。本会话直接开工 Slice 1（X11 看/指/放大/点/确认闭环），不再讨论设计。
按序读（纯文本）：1. ../checkpoint/screenlab-rules.md；2. ../checkpoint/screenlab-work.md（工作单，重点，含 Slice 0/1 进度与待办）；3. ../checkpoint/design-vision-computer-fusion.md；4. ../checkpoint/design-vision-scripting.md；5. ../checkpoint/handoff-screen-64.md。
⚠️ 文档是二手描述，动手前以代码 / 实测为准。裁决者是目标（§0.0），不是 YZ；只有目标真推不出才升级后停。
环境事实：目标机 surface-centos-9 默认离线，用 `ssh zhengyp@100.112.50.115 '"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" startvm centos9 --type headless'` 拉起；开机后无图形会话，用 `tools/x11.sh start` 起自管 Xvfb :101 + openbox + zenity 靶。
下一步：写 Slice 1 自测（look→mark→coord→act，已知真值见工作单）、README 已记 x11.sh、确认 Slice 1 通过后依目标定 Slice 2；改码不 commit，每步通知 YZ 不等回复。
```

---

## 本会话（#64）做了什么

1. **Slice 0（完成）**：
   - `cogos/cogos/image_ctx/domain.py`：加 `Domain.open(root, state=None)` + `save/load`（JSON 原子写；state=None 保持原内存行为）；load 重建 `registry`/`figs` 去重表并把 `_id_gen` 重置到 `max(fig_id)+1`（已定 3–8）。
   - 新增 `tools/imgctx.py`（see/mark/adjust-mark/unmark/coord，flock state，单行 JSON）；`tools/imgctx_selftest.py`（已知真值验收，**ALL PASS**）。
2. **Slice 1（X11 闭环，基本完成）**：
   - 新增 `tools/x11.sh`：目标机上自管 Xvfb `:101` + openbox + zenity 点击靶，启动走 systemd-run 瞬态单元 `sl1-*`。子命令 `start/stop/geometry/capture/click/pointer/windows/status`。
   - `imgctx.py` 加 `look`（capture→image_ctx 新 FIG）/ `act`（anno 归一 →×屏幕=设备像素 → xdotool 点击 → 重抓 → 整屏 + 落点 mark）。
   - **闭环实测**：`look` FIG:1000 → mark OK (0.567,0.572) → `coord` px (726,458) → `act` device [726,458]、`pointer` 正好 X=726 Y=458、落点 FIG:1001、zenity 窗口 1→0。

## 关键事实 / 纠正（防臆断）

- image_ctx 真实 API：`see/mark/adjust_mark/unmark/coord` + `Block(text, image=PNG绝对路径, image_size)`。原 `Domain` **无 save/load**（纯内存）；fig id 计数器模块级全局 `view._id_gen`；去重表 `Source.figs[window_key]`。
- `add_src` **按 path 字符串**去重 → 每次 capture 必须用**唯一帧路径**（`x11.sh capture` 已按 `frame-<ts>.png`）。
- 目标机开机后**无图形会话**（human :0 不在）；`status.sh` 报 unreachable/attach inactive。用 `x11.sh` 自管 Xvfb 绕开。
- 本机 `python3.11`+PIL 12.3.0；目标 `python3`=3.9+PIL 10.0.1；本机 Xvfb `:77` 仅供后端试验（会话结束已停）。

## 未做 / 下一会话

- Slice 1 **自测脚本**（已知真值：1280×800 openbox 居中 zenity 的 OK ≈ (0.567,0.572)）；README 已补 `x11.sh` 条目与用法。
- 判断 Slice 1 是否达标：以目标 §0.0 为准（"能操作 + 有反馈" 的看/点闭环已成）。达标后依目标定 Slice 2（Android 换后端 + 修 #61），**不问 YZ**。
- 未 commit（`domain.py` 有改动；tools 新增文件）。

## 锚

- 工作单：`screenlab-work.md`；设计：`design-vision-computer-fusion.md`、`design-vision-scripting.md`（1–16）
- 规则：`screenlab-rules.md`；目标：`spec-screen-1.md` §0.0
- 工具：`tools/imgctx.py`、`tools/imgctx_selftest.py`、`tools/x11.sh`、`tools/README.md`
