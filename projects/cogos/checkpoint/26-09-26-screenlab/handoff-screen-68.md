# handoff｜交接给新会话 · #68 → #69（Slice 0–3 完成；回顾开发/交接情况）

> 规则 / 环境不在本文件——先读 `screenlab-rules.md`。
> 本会话（#68）：**Slice 3（Windows：换后端 + DXGI 采集）完成，自测 ALL PASS**。至此 Slice 0–3 全完成。
> **不要回读本会话 transcript**：任务态已落 `screenlab-work.md`（§Slice 3 结果 + §状态），文件是唯一依据。
> 交接原因：YZ 要求交接并回顾几次交接的开发情况（非 10min 到点）。

---

## 复制这段作为新会话的第一句

```
接 #68。Slice 0–3（X11 / Android / Windows 三平台的 看/指/放大/点/确认 闭环 + Windows DXGI 采集 + 通用分块 diff 兜底）已全部完成，各自自测 ALL PASS，仓库一律未 commit。
本会话任务 = 先按序读下列文件加载上下文，**然后等 YZ**；等 YZ 到位后，与 YZ **一起**回顾 #62c→#68 的交接与开发情况（素材见 ../checkpoint/handoff-screen-68.md 的「回顾」段，仅作素材，**不要自己单方面回顾或下结论**）。下一步方向只在 YZ 在对话中提出后才跟进。
按序读（纯文本）：1. ../checkpoint/screenlab-rules.md；2. ../checkpoint/screenlab-work.md（重点 §状态 + §Slice 3 结果）；3. ../checkpoint/handoff-screen-68.md（含回顾素材与本会话改动）；4. ../checkpoint/design-vision-scripting.md（§传输修正清单 = 待 YZ 定的候选）。
⚠️ 文档是二手描述，动手前以代码 / 实测为准。裁决者是目标（spec-screen-1.md §0.0），不是 YZ。
加载完用 /home/zhengyp/work/A/locus/tools/feishu_notify.py 通知 YZ「已就绪、等 YZ 一起回顾」，然后停下等 YZ。
```

---

## 回顾：几次交接的开发情况（#62c → #68）

| 交接 | 阶段 | 做了什么 | 验收 / 结果 | 关键纠正 |
|---|---|---|---|---|
| #62a/b/c | 设计 + 实验 | 三平台屏变感知原语实验（`screen-change-detect.md`）；定「传输与看屏分离」（已定 15） | 实验归档，无码入库 | Windows DXGI/X11 XDamage/Android damage 差异 |
| #62c→#63 | 融合设计 | usage-first 重做融合（`design-vision-computer-fusion.md`）；锁平台顺序 X11→Android→Windows；建开工工作单 `screenlab-work.md` | 未改码 | 推翻中间版机制汇总 |
| #63→#64 | **Slice 0** | `image_ctx/domain.py` 加 `open/save/load`（state 持久化 + `_id_gen` 重置 + figs 重建）；新增 `tools/imgctx.py`（薄 CLI，flock state） | `imgctx_selftest.py` **ALL PASS**（静态 PNG see/mark/coord + 缩放链 + 去重） | API 以代码为准：`Block=(text,image 路径,size)`；`add_src` 按 path 去重 → 每帧唯一路径 |
| #64→#65 | **Slice 1** | 新增 `tools/x11.sh`（自管 Xvfb `:101`+openbox+zenity，systemd-run）；imgctx 加 `look/act` | 手工+CLI 闭环跑通（coord/pointer=(726,458)、zenity 1→0）；自测未写 | 目标机默认离线、无图形会话 → 自管 Xvfb；裸 `windows` 数进内部窗口，存在性按 class |
| #65→#66 | Slice 1 收尾 | 新增 `tools/x11_selftest.py`；`x11.sh zenity` 子命令；env.sh 补 Android 事实 | `x11_selftest.py` **ALL PASS** | `image_size` 是**渲染后**图幅（max_dim=800），原图尺寸看 text |
| (#66 回收) →#67 | **Slice 2** | 新增 `tools/android.sh`（screencap + InjectService tap + uiautomator 真值）+ `android_selftest.py`；imgctx 加 `--backend`；**修 #61**（act 用 FIG 自身 `orig_w/h`）；通用分块 diff：`service/change.py` + 单测 + `tools/screendiff.py` | Android 闭环 **ALL PASS**；X11 回归 ALL PASS | #61 根因=模型按渲染图目测归一不准；Android raw 比 PNG 慢（15s vs 4.9s），"去 PNG"在 adb 不划算 |
| #67→#68 | **Slice 3** | 纠正"daemon 没跑"；`backends_win.py` 加 `DxcamCapture`（DXGI，懒 import）+ `pick_capture()`（GDI 回退）；`platform_backends` 用它；新增 `tools/windows.sh` + `windows_selftest.py`；imgctx 加 `--backend win` | Windows 闭环 **ALL PASS**（真值 Tk 靶 click=(900,550)、README→HIT）；daemon `capture_backend=dxcam` | daemon 实测在 assist **session 7** 在跑；`import dxcam` 在 Session 0 直接失败（无桌面）→ 懒 import；采集/注入必须交互式会话 |

**共性**：验收形状三平台一致 = 地面真值元素 → `look→mark→coord→see(zoom)→act`，断言 coord/device 命中真值 + `act` 后画面变 + 自算 diff 定位变化。机制层只做 mechanical I/O、无同意握手、无人值守；唯一智能在 agent 侧、图不转文字。

## 本会话（#68）改动

- 产品码：`cogos/screenlab/service/backends_win.py`（DxcamCapture + pick_capture）、`platform_backends.py`（win32 用 pick_capture）。
- 工具：`tools/windows.sh`、`tools/windows_selftest.py`、`tools/win/62c/{win_io.py,target_tk.py,probe_backend_dxcam.py}`；`tools/imgctx.py` 加 `--backend win`；`tools/README.md` 记 Slice 3。
- 运行态：Windows daemon 已重启载入新码（`capture_backend=dxcam`，assist session 7，9911/9912）；安装副本已 push，**仓库未 commit**。

## 未 commit（累计，都别 commit）

- cogos：`screenlab/service/{change.py,backends_win.py,platform_backends.py}`、`tests/screenlab/test_change.py`、`cogos/image_ctx/domain.py`（#64）。
- tools：`imgctx.py`、`imgctx_selftest.py`、`x11.sh`、`x11_selftest.py`、`android.sh`、`android_selftest.py`、`screendiff.py`、`windows.sh`、`windows_selftest.py`、`env.sh`、`README.md`、`win/62c/{win_io.py,target_tk.py,probe_backend_dxcam.py}`。
- checkpoint：`screenlab-work.md`。

## 待 YZ 定的候选（非待办，等 YZ 提出）

- 传输修正清单（`design-vision-scripting.md`）：`daemon.py:296` 每帧 PNG 编码 → 原生 damage / 分块 diff；`backends_android.py:78` → MediaProjection raw；`backends.py:120` 开 XDamage。
- 接进真正的 `computer` 工具（v2）；Slice 0–3 的 commit/tag。

## 锚

- 工作单：`screenlab-work.md`；设计：`design-vision-scripting.md`、`design-vision-computer-fusion.md`
- 规则：`screenlab-rules.md`；目标：`spec-screen-1.md` §0.0；屏变实验：`screen-change-detect.md`
- 工具：`tools/{imgctx.py,x11.sh,android.sh,windows.sh,*_selftest.py,screendiff.py}`、`tools/win/`
```
