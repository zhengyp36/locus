# handoff｜交接给新会话 · #69 → #70（把脚本整合进产品工具）

> 规则 / 环境不在本文件——先读 `screenlab-rules.md`。
> 本会话（#69）：与 YZ 回顾 #62c→#68；定方向 = **脚本 ↔ 工具双向补**；把产品增量 commit+push。
> **不要回读本会话 transcript**：任务态已落 `screenlab-work.md`（§状态）。
> 交接原因：YZ 要求从新会话开始做整合，避免本会话逼近 150K。

---

## 复制这段作为新会话的第一句

```
接 #69。Slice 0–3 已完成并已 commit+push（origin/feat/screenlab-p2）。本会话任务 = 把 ../checkpoint/tools 的脚本能力整合进产品工具（双向补），先在 Windows + Android 回归，X11 留到天亮再验。
先按序读（纯文本）：1. ../checkpoint/screenlab-rules.md；2. ../checkpoint/screenlab-work.md（§状态）；3. ../checkpoint/handoff-screen-69.md（任务与整合方向）。
整合方向（已与 YZ 定）：① 视觉层留客户端，不改 screen/1 协议；imgctx 的 look/act 改走 screenlab/proto/client.py（复用 snapshot_id 过期校验），see/mark/coord 接在拉回的帧上（image_ctx）；② 不丢工具已有的治理层（snapshot/generation、同意、生命周期、a11y）；③ 把需要的脚本归位到 cogos（如 screenlab/tools/，先例 screenlab/install/），排除 tools/keys/agent.key；④ 验证沿用现有地面真值 selftest 形状；Windows/Android 现在回归，X11 切换（抛式 Xvfb → 产品图形面）留到最后、天亮验。
允许 commit/push（不 tag），提交前跑测试。纪律：10min 闹钟；ctx ≥150K 或逼近就交接；裁决由目标（spec-screen-1.md §0.0）；目标推不出 → 飞书通知 YZ 后不空等，先做不阻塞的。
⚠️ 文档是二手描述，动手前以代码/实测为准。
```

---

## 为什么做这件事（#69 与 YZ 的结论，素材）

- 现状：能力已三平台跑通，但**视觉工具仍是脚本**（`tools/imgctx.py` import `image_ctx`），后端一半在脚本、一半在产品码；`image_ctx` 在 cogos 内**零引用**，agent 用的不是"电脑工具"。
- 产品工具（`screenlab`）已有的：`capture`（返回 `snapshot_id`+`changed`+`image`）、`act(snapshot_id)`（**过期即拒** `stale_snapshot`，`daemon.py:331-352`）、同意/收回/多账户/共屏/a11y。
- 这轮真正的净增益（相对 #62c 之前）：**视觉定位 see/mark/coord 首次被 agent 用上** + `#61` 坐标链修复 + Windows DXGI 后端 + image_ctx 持久化 + 分块 diff 原语。
- 缺口：视觉层没进工具、后端重复。**双向补 = 把脚本的视觉定位接进工具，别用脚本替换工具的机械/治理层。**
- 结论：整合后 agent 见到**一个工具**，兼具"视觉定位 + 帧绑定/过期校验/同意"，即收尾收益。

## 本会话（#69）改动

- cogos `feat/screenlab-p2` 已 commit+push 3 个 commit：`832e085`（image-ctx 持久化）、`23c04e8`（DXGI 后端）、`975cc60`（分块 diff）。测试：`test_change.py` 5 passed、`tests/image_ctx` 45 passed。
- 更新：`screenlab-rules.md`（纪律：≤150K 交接、阻塞则通知后先做不阻塞的、整合期允许 commit/push 不 tag）、`screenlab-work.md`（§状态）。
- **未入库（需 #70 归位）**：`checkpoint/tools/` 整个目录——它**不是 git 仓库**，故无法提交；含 `keys/agent.key`（私钥，**不得入库**）。

## #70 的具体任务

1. 客户端整合（平台无关）：`imgctx` 的 `look/act` 改走 `ScreenClient`（`screenlab/proto/client.py`），`act` 带 `snapshot_id`；see/mark/coord 走 `image_ctx` 作用在 `blob_get` 拉回的帧上。不改 `screen/1` 协议。
2. 脚本归位到 cogos（如 `screenlab/tools/`，参照 `screenlab/install/`），排除 `keys/`；测试脚本一并。
3. 回归：Windows（daemon+DXGI）、Android（assist+daemon 8901）——地面真值 selftest（`windows_selftest.py`/`android_selftest.py`）形状不变，改走工具路径。
4. X11：把抛式 Xvfb `:101` 换到产品图形面（`install/session-start.sh create`），**天亮再验**；期间别让 X11 阻塞前两者。
5. 允许 commit/push（不 tag），提交前跑测试。

## 锚

- 规则：`screenlab-rules.md`；工作单：`screenlab-work.md`；目标：`spec-screen-1.md` §0.0
- 设计：`design-vision-scripting.md`（§传输修正清单）、`design-vision-computer-fusion.md`
- 工具：`tools/{imgctx.py,x11.sh,android.sh,windows.sh,*_selftest.py,screendiff.py}`、`tools/win/`
- 产品：`cogos/screenlab/{proto/client.py,service/daemon.py,service/backends_win.py,service/change.py}`、`cogos/image_ctx/`
