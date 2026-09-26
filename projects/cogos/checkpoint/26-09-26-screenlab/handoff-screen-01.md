# handoff｜图形电脑（看屏 / 适配服务 / 协议 / 客户端）讨论 · 2026-09-20

> **新会话任务**：继续讨论"图形化看电脑"——适配服务与协议的形态、客户端怎么用、以及怎么起步验收。**纯讨论**，未拍不动码。
> **交接语**：读 `work/A/checkpoint/handoff-screen-01.md`，承接"已收敛结论"，从"待 YZ 裁决"往下谈。
> **前序**：`handoff-tools-09.md`（工具现状盘点 / 分域 / 按需加载）→ 本会话（图形面，本批讨论为主）。

## 本会话性质

**纯讨论，未改任何代码。** 代码基线仍 `cogos` @ `45ab216`（同 `handoff-tools-09`，工作区干净）。

## 讨论主线（一条链）

1. **工具分域**：32 工具 → 4 域（私记 / 电脑 / 对外 / 时间）+ 图通用原语；降负荷六机制（命名自定位、域少而稳、簇内默认、看屏二分、图是原语、time_form 上浮）。
2. **模型怎么看到工具**：两通道全量平铺（system prompt `config.py:99` + schemas `consciousness.py:68`）；`toolset_names` 管道已埋未接线（`app.py:185`）。
3. **按需加载三档**：装配期静态裁（=4b，设计内）/ 情境动态增删（设计内）/ 模型自助 `load`（与 §12「装配归机制」冲突，需裁决）。
4. **视觉定位**：图**不做第五域**。单张看图也**工具在前**（自缩放，厂商 resize 静默丢细节，§168–170）；`image_ctx` 自带目录（`images/` 资产 + `cache/`），`add_src` = load（异步候选）、`see` = 看（同步）；与 `vision-system-design` 的无状态 `img-tool` 口径**冲突未并**。
5. **图形化看电脑整类缺失**：全仓无 display / X11 / 截屏 / 注入实现。
6. **抽象与适配服务**：一个屏幕面协议 + 平台 daemon；OS 差异下沉 adapter。**Android 翻案**：`scrcpy` 现成（adb 上完整看/动），反而是最便宜的 adapter 验证场。
7. **协议设计（screen/1）**：caps 握手 → `displays` / `state` / `see(mode=auto|pixels|tree, region, max_dim, since_hash, wait_stable)` / `act(element|pointer|key|type|paste|scroll, snapshot_id)` / `blob_get(sha)`；**快照世代**防"拿旧图点新界面"；blob 内容寻址去重；**不推事件**（帧哈希 + wait_stable）。
8. **客户端形态**：一套动词 `connect / displays / state / see / act`。**a11y 不是另一族工具**，是 `see` 的一条数据通道（`mode`）和 `act` 的一种宾语（`element`）；像素/元素只是同一动作的两种寻址，路由在服务端。
9. **行业现状**：树默认 + 视觉兜底、**按次路由**（Terminator `click_element` 五档 `vision_type`，树 ~95% / 视觉清 5%）；Playwright MCP / Windows-MCP / macOS AX-MCP；**MCP 2026-07 spec 成协议事实标准**；但 MCP 之下"屏幕原语协议"**无标准**，变化感知仍轮询；OSWorld 已饱和（OSWorld 2.0 最强模型掉回 20.6%）。
10. **实施困难分两串**：工具侧（跨平台 adapter / 无头 a11y / 输入时序 / 抓屏成本）vs 接入侧（图进 context 的运行时 / 装配 / 上下文成本）。
11. **阶段划分修正**：先做**自洽工具**（daemon + client + CLI）→ B 层契约 → 最后接入。**验收由 LLM 在环**（用 CLI + 读图跑"看→点→再看"），不必等运行时改造。图进 context 属接入阶段，不是 Phase 1 拦路虎。
12. **机器评估**：本机 = CentOS Stream 9 VM（VirtualBox）**2 vCPU / 3.6G（可用 1.07G）——正是 `vision-system-design` 里那台弱机**；X11 栈 / Xorg / libXtst / chrome148 / at-spi2-core / dbus / Python3.11+Pillow **都在**；缺 `Xvfb`/`xdotool`/`scrot`/`adb`/`pyatspi`；**sudo 要密码**；默认 Wayland（gdm greeter）+ 无用户桌面。

## 已收敛的结论（可当既定）

- 图形面是**电脑的第二个面**，与 `term` 并列（会话 / 驱动 / 看屏 / 文件），不是图域的一部分；图域是它的第一个消费者。
- a11y 与截图**不是两条能力**：同一 `see`/`act` 的两条 grounding（数据 / 宾语），路由在服务端。
- 客户端**薄 = 不含平台逻辑，但含 agent 语义**；分界线是 **mechanical vs semantic**，不是 client/server。
- 服务端只做 mechanical；**理解 / 决断 / 记忆 / 装配**留 agent 侧（唯一智能主体、图不转文字）。
- **不发屏幕变化事件**；靠 `frame_hash` + `wait_stable`。
- 协议 wire **照 MCP 形状**（不自造标准），自己只加语义（世代 / 静默 / 去重）。

## 待 YZ 裁决

1. **图 = 持久资产（`image_ctx` 有根）还是临时介质（`img-tool` 无根）**——两条 lineage 必须先并，否则图域有没有目录都不定。
2. **自建电脑 vs E2B 类云桌面**（后者开箱，但租用、流形态未必容得下 blob 去重 / 快照世代）。
3. **客户端薄到哪**（纯管道 vs 带薄语义层）。
4. **先做哪个平台**（建议 Linux/X11 或 Android/scrcpy 二选一）。
5. **是否给 sudo**（决定能否在这台机器起步：装 `xorg-x11-server-Xvfb` + `xdotool`）。
6. 旧遗留 **4b 装配 / 按需加载** 与本线的关系。

## 下一步建议（窄切口）

- 路线 A（推荐）：本机 `Xvfb :99` + `xdotool`（需 sudo）→ 起 daemon + client + CLI → **我做 LLM 在环验收**（`see` 出图 → 我读图 → `act` → `see` 确认）。
- Xvfb 用软件渲染，绕开 `/dev/dri/card0` 无权限（当前用户不在 `video` 组）。
- 顺带实测**无头 a11y 是否可用**（`dbus-run-session` + at-spi + 一个 GTK 应用）。
- 一切后置：事件推送、window 级抓屏、多显示器、云桌面、term/fs 收编。

## 关键引用（file:line）

- 工具面：`app.py:192` `_build_specs`；`tools.py:1131` `ToolRegistry`、`:1156` `call`；`config.py:99` `render_system_prompt`；`consciousness.py:65-70`（tools 建 cu 时固定）、`:68` `schemas`。
- 图：`image_ctx/domain.py:36-49`（`images/` + `cache/`）、`:56` `add_src`；`image_ctx/tools.py:71` `parse_ref`(PATH/FIG/ANNO)、`:122` `see`、`:163` `Block{text,image}`。
- 视觉预研：`cogos/docs/vision-system-design.md` §14（img-tool `info`/`extract`、无状态）、§168–170（自缩放 / resize 鲁棒）。
- 设计口径：`cogos/docs/design-agent-tools.md` §5.4（不做通用事件）、§6（不做本地远端分叉）、§12（装配归机制）。
- 遗留：`spec-phone-files §8` `scheme:path`（`draft:` / `spool:` / `machine:`）未落（`handoff-phone-files-02:47`）。
- 封存：`checkpoint-1.md` §87 / §392（`image_ctx`/`img_tool` 有码未接入）。

## 纪律

- 跑测试用 `python3.11 -m pytest`（系统 `python` 是 3.9）。
- 结论先落 `checkpoint-2.md` / spec，定案再更新权威分册 `design-agent-tools.md`。
- 不替 agent 决定用法；发现设计问题回 checkpoint 记，不悄悄改设计。
