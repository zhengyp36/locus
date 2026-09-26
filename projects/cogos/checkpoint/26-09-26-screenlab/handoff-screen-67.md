# handoff｜交接给新会话 · #67 → #68（Slice 3：Windows）

> 规则 / 环境不在本文件——先读 `screenlab-rules.md`。
> 本会话（#67）：**Android Slice 2 完成 + #61 坐标链修复 + 通用分块 diff 兜底**（均自测 ALL PASS，X11 回归 ALL PASS）。
> **不要回读本会话 transcript**：任务态已落 `screenlab-work.md`（§Slice 2 结果），文件是唯一依据。
> 交接原因：10min 闹钟到点，`ctx.py` 报 15%（绝对 153K）——按规则交接。

---

## 复制这段作为新会话的第一句

```
接 #67。本会话直接开工 Windows（Slice 3：换后端 + DXGI 采集），Android 已全部完成，不再讨论设计。
按序读（纯文本）：1. ../checkpoint/screenlab-rules.md；2. ../checkpoint/screenlab-work.md（重点 §Slice 2 结果 + §Slice 2 范围）；3. ../checkpoint/handoff-screen-67.md；4. ../checkpoint/design-vision-scripting.md（§传输修正清单 + 已定 15）。
⚠️ 文档是二手描述，动手前以代码 / 实测为准。裁决者是目标（spec-screen-1.md §0.0），不是 YZ；只有目标真推不出才升级后停。
环境事实（#67 实测）：Android 已验收通过可不管；Windows 机 tablet-bbt8eqb4（Win11，100.112.50.115）——assist/zhengyp 均可 ssh，但 **daemon 当前没在跑**（status.ps1 只见表头：无 pythonw、无 991[12] 监听、daemon.log 停在 9/25 23:14）。assist 前缀 C:\Users\assist\AppData\Local\screenlab 有 venv（Python3.11.5，含 PIL/numpy/comtypes/dxcam）/已部署 screenlab/shot.py/daemon.log；有 csc.exe。Win 采集/注入必须落在 assist 的**交互式会话**（ssh 落在 Session 0 看不到桌面）——harness：admin ssh 跑 tools/win/launch_daemon.ps1 / launch_tray.ps1 / shot_task.ps1，62c 版 tools/win/62c/launch_probe.ps1、launch_cmd.ps1（可跑任意命令到 C:\Users\assist\screenlab-62c\*.out）。部署单文件用 tools/win/push_file.sh <path-relative-to-screenlab>。
下一步：①（先）确认/拉起 Windows daemon 与 assist 交互式会话；② 实现产品 DXGI 采集后端（backends_win.py 加 DxcamCapture，GDI 回退；dxcam 已装 = 真 DXGI Desktop Duplication，IDXGIOutput5）；③ 用 62c/launch_probe.ps1 在交互式会话里跑一次产品 backend 抓帧自证；④ 再考虑 tools/windows.sh + windows_selftest.py（同 look/mark/coord/act 闭环，换后端）。改码不 commit，每步通知 YZ 不等回复。
```

---

## 本会话（#67）做了什么（详情见 screenlab-work.md §Slice 2 结果）

1. **Android 闭环**：新增 `tools/android.sh`（screencap + InjectService 注入 + foreground + ui-bounds + consent-auto）、`tools/android_selftest.py`（**ALL PASS**）。`imgctx.py` 加 `--backend {x11,android}`。
2. **#61 坐标链修法**：`act` 用 `FIG.orig_w/orig_h`（模型看到的那帧的像素尺寸）算设备坐标，不再另查 geometry。实测 #61 根因 = 模型按渲染图目测归一坐标不准（不是映射错）。
3. **通用分块 diff 兜底**：产品层 `cogos/screenlab/service/change.py`（x8 指纹 + 分块 bbox）+ 单测（5 passed）+ `tools/screendiff.py`；接入 Android 验收（稳定=false 用 bbox；act 前后 changed bbox 含落点）。
4. **实测结论（重要）**：Android 经 adb 取 raw RGBA 一帧 15.0s/10MB vs PNG 4.9s/1.6MB → "去 PNG 改传 raw" 在 adb 链路**不划算**；真要改需 app 内 MediaProjection raw + 协议改造（设计稿"待 YZ 定"），**未动**。
5. **Windows 只做了侦察**：ssh 通、daemon 未跑；拉了 dxcam 源码到 `/tmp/kilo/dxcam/`（含 `_libs_d3d11.py`/`_libs_dxgi.py`/`core_stagesurf.py`）——里面有 DXGI/D3D11 的 comtypes 接口定义（含精确 vtable 槽位：ID3D11DeviceContext Map=槽10、Unmap=11、CopyResource=43；ID3D11Device CreateTexture2D=槽5），实现 DXGI 采集可直接照抄。62c 的 `probe_dxgi.py`（纯 ctypes，DuplicateOutput 见 IDXGIOutput1 槽22）与 `probe_dxcam.py` 亦可用。

## 关键纠正 / 防臆断

- `handoff-screen-65.md` 说 "daemon 127.0.0.1:9911 在听" **已过期**：`status.ps1` 现在没有任何 daemon/监听。
- Windows `query session` 在 ssh 的 PATH 里没有（CommandNotFound）；用 `qwinsta` 或 Get-Process 的 SessionId。
- `timeout` 不能直接跑 bash 函数（`win_ssh`）；要么 `timeout bash -c`，要么直接用 `ssh "$SL_WIN_SSH"`。
- `screendiff` 的全局指纹对状态栏秒级噪声敏感；判"有无意义变化"用 **bbox**（分块 diff），不要用指纹相等。

## 未 commit（都别 commit）

`tools/android.sh`、`tools/android_selftest.py`、`tools/screendiff.py`、`tools/imgctx.py`、`tools/README.md`、`cogos/screenlab/service/change.py`、`cogos/tests/screenlab/test_change.py`、`screenlab-work.md`；另有 #64/#65 遗留（`cogos/cogos/image_ctx/domain.py`、`tools/x11.sh`、`tools/x11_selftest.py`、`tools/env.sh`）。

## 锚

- 工作单：`screenlab-work.md`；设计：`design-vision-scripting.md`（15/16、传输修正清单）、`design-vision-computer-fusion.md`
- 规则：`screenlab-rules.md`；目标：`spec-screen-1.md` §0.0；屏变实验：`screen-change-detect.md`（Windows/DXGI §）
- Windows 工具：`tools/win/{README.md,status.ps1,launch_daemon.ps1,launch_tray.ps1,shot_task.ps1,push_file.sh,push_pkg.sh,shot.py}`、`tools/win/62c/{launch_probe.ps1,launch_cmd.ps1,probe_dxgi.py,probe_dxcam.py,changer_tk.py}`
