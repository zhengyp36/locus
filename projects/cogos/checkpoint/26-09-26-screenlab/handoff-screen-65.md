# handoff｜交接给新会话 · #65 → #66（Slice 2：Android）

> 规则 / 环境不在本文件——先读 `screenlab-rules.md`。
> 本会话（#65）：Slice 1（X11 看/指/放大/点/确认闭环）**完成并自测 ALL PASS**；补 `zenity` 后端判据；把 Android 环境事实补进 `tools/env.sh`。
> **不要回读本会话 transcript**：任务态已落 `screenlab-work.md`，文件是唯一依据。

---

## 复制这段作为新会话的第一句

```
接 #65。本会话直接开工 Slice 2（Android 后端同一 look/zoom/mark/coord/act 闭环 + 修 #61 坐标链 + 传输/兜底），之后续做 Windows（换后端 + DXGI 采集），不再讨论设计。
按序读（纯文本）：1. ../checkpoint/screenlab-rules.md；2. ../checkpoint/screenlab-work.md（工作单，重点）；3. ../checkpoint/design-vision-computer-fusion.md；4. ../checkpoint/design-vision-scripting.md；5. ../checkpoint/handoff-screen-65.md。
⚠️ 文档是二手描述，动手前以代码 / 实测为准。裁决者是目标（§0.0），不是 YZ；只有目标真推不出才升级后停。
环境事实（#65 实测，已全部就绪）：Android 手机 nova 4e（MAR-TL00，Android 10/SDK29，1080×2312@480）经 USB 已开 wifi adb，adb 设备 192.168.1.175:5555 在线；assist 已装且进程在跑，InjectService 已在无障碍启用，服务 8901 在听。Windows 就绪（assist/zhengyp 可 ssh，daemon 127.0.0.1:9911 在听）。事实在 tools/env.sh（SL_ANDROID_*、adb_dev、SL_WIN_*、win_ssh/win_admin）。
下一步：Android look/mark/coord/act 闭环 + 地面真值（沿用 X11 已验证形状），修 #61 坐标链；改码不 commit，每步通知 YZ 不等回复。
```

---

## 本会话（#65）做了什么

1. **Slice 1（完成，自测 ALL PASS）**：
   - 新增 `tools/x11_selftest.py`：自起 surface（Xvfb 1280×800）→ `look→mark→coord→act`。断言 coord 像素=(726,458)=真值；zoom 子窗(0.2×0.2→256×160)内 mark 0.5,0.5 的 coord 仍回 (726,458)；`act` device=pointer=(726,458)、返回 landing FIG+整屏；zenity 1→0。exit 0。
   - `tools/x11.sh` 加 `zenity` 子命令（`xdotool search --onlyvisible --class zenity`）。
   - `tools/README.md` 记 `x11.sh`/`zenity` 与 `x11_selftest.py`；`screenlab-work.md` 记 Slice 1 结果 + Slice 2 范围。
2. **环境确认（实测）**：Windows 就绪；Android 未就绪（详见下）。

## 关键事实 / 纠正（防臆断）

- 裸 `x11.sh windows`（`--name ".*"`）会数进 openbox/GTK 内部窗口，**fresh surface = 26 不是 1**；zenity 存在性必须按 **class**（新 `zenity` 子命令）。
- `imgctx` 的 `image_size` 是**渲染后**图幅（render `max_dim=800` 降采样），1280×800 → 800×500；原图尺寸看 text 里的 `（W×H）`。坐标换算不受降采样影响。
- 手机侧：Android 10/EMUI 10 无「无线调试」UI；wifi adb 靠 USB `adb tcpip 5555` 开，**重启即失**。本机无 USB 安卓设备（`lsusb` 无），Windows 无 adb，故当前无 USB 回连通道。
- 本会话新增未 commit：`tools/x11_selftest.py`、`tools/x11.sh`、`tools/README.md`、`tools/env.sh`、`screenlab-work.md`；另有 #64 遗留 `cogos/cogos/image_ctx/domain.py`、`tools/imgctx.py`。

## 未做 / 下一会话

- **Android 已就绪**（#65 实测）：USB `adb tcpip 5555` → `adb connect 192.168.1.175:5555` 已通；assist 已装/进程在跑/InjectService 已启用；服务 8901 在听。直接做 Slice 2（同闭环 + 修 #61 + 传输/兜底）。
- **不等待原则（YZ 2026-09-26 明示）**：任一环境阻塞（如设备掉线、通道断），**直接切到另一个环境继续，不等**；Android ↔ Windows 互为回退。
- **范围含 Windows（YZ 2026-09-26 明示）**：Android 之后还需完成 Windows 侧相关工作（Slice 3，换后端 + DXGI 采集；Windows 环境已就绪）。连续范围 = Android → Windows。
- `tools/android.sh status|connect|serve` helper 未建（env.sh 已给 `SL_ANDROID_*` 与 `adb_dev`；如需可补）。
- 未 commit。

## 锚

- 工作单：`screenlab-work.md`；设计：`design-vision-computer-fusion.md`、`design-vision-scripting.md`（1–16）
- 规则：`screenlab-rules.md`；目标：`spec-screen-1.md` §0.0
- 工具：`tools/imgctx.py`、`tools/x11.sh`、`tools/x11_selftest.py`、`tools/env.sh`
