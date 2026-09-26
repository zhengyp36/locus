# handoff｜交接给新会话 · 2026-09-25 #61

> 接 #60。本会话：**Android M5 真机演示 → 暴露通用控制能力缺口**；已记录到 `screen-android-issues.md`。
> **规则/环境不在本文件**——先读 `screenlab-rules.md`。
> **硬性要求：新会话读完即停，不做任何操作（不抓屏 / 不跑命令 / 不读图片），等 YZ 讨论视觉。**
> 未提交、未 tag；cogos 工作树 DIRTY。

---

## 复制这段作为新会话的第一句

```
接 #61。本会话只做一件事：读文档，然后停下等 YZ，不要动手。
按序读（纯文本，勿读任何图片）：1. ../checkpoint/screenlab-rules.md；2. ../checkpoint/screen-assist-status.md §0；3. ../checkpoint/screen-android-issues.md（全部）；4. ../checkpoint/handoff-screen-61.md。
硬性约束：读完不要执行任何命令（不要 terminal / bash / glob / grep），不要 capture，不要把任何图片读进上下文；只用文字回复一句「已读完，待命」，然后停下等 YZ。接下来与 YZ 讨论「视觉」问题。
```

---

## 本会话做了什么（#61）

1. 按 YZ 要求连真机跑了一次简单测试（打开 Chrome 到 bing.com）——**只是测试，不是目标**。
2. 测试暴露的缺口（详见 `screen-android-issues.md`）：
   - **坐标不准**：`tap(0.125,0.599)`（估微信）命中支付宝；`tap(0.26,0.77)`（Chrome）两次无反应。注入本身生效。
   - **`act` 只有 tap**：无 HOME/BACK/滑动/长按，连回桌面都做不到（卡在支付宝前台）。
   - **无打字**：访问 URL 需文本输入，当前不支持。
   - **无 launch**：打开应用/网址只能靠找图标。
3. **授权澄清**（YZ 追问）：一次会话弹 3 次 = 我开了 3 条连接（一次性脚本 + 重启），**不是 App 重复问**。App 每条连接只问一次（`AssistServer.java:320`），真实 agent `ScreenChannel` 一条长连接 → 一次会话一次同意；短暂网络抖动/空闲不会断（认证后 `SoTimeout=0`）。`§0.0`：授权 = 一条连接。
4. 新建 `screen-android-issues.md`：问题 1 launch / 2a 坐标映射 / 2b 视觉定位 / 3 打字 / 4 导航手势 / 5 一次性权限，含锚点与建议顺序。

## 下一步 / 待 YZ

- **讨论「视觉」**（适用于所有 GUI，架构级）：
  - 在哪儿做（倾向 **agent 端**：截图本就在 agent 手里，可能只是工作流+坐标约定）；
  - 是否 overlay/mark（倾向 host 侧，可选增强）；
  - 如何回到设备坐标（依赖 2a 映射）；
  - 精度闭环（capture→act→capture 比对 `frame_hash`）；
  - 跨平台统一抽象 `capture →(可选 overlay)→ 模型产出归一坐标 → act`；
  - 成本/时延/离线。
- 建议顺序（待定）：`2a 映射校准 → 2b 视觉定型 → 4 导航 → 3 打字 → 1 launch`（1 最小可提前）。
- **M5 验收/提交/tag/回写分册仍待 YZ**（未提交、未 tag）。

## 锚

- 缺口清单：`screen-android-issues.md`
- 活文档：`screen-assist-status.md` §0/§4
- 代码认知：`codebase.md`（版本戳 `b3cc333`；`screenlab/android/` 为新增未提交目录）
- 上轮：`handoff-screen-60.md`
