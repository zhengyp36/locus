# screen-android-issues.md · Android 端能力缺口清单（#60 后）

> 由 #60/#61 会话整理。M5 真机演示暴露的**通用控制能力缺口**，逐个解决。
> 场景 = agent 经 `screenlab-auth` 控制 Android 设备（当前 `nova 4e` / API 29）。
> **注意**：目标不是"打开 Chrome 到 bing.com"（那只是一次简单测试），而是把通用控制能力补齐。
> 相关：`screen-assist-status.md` §0/§4、`handoff-screen-60.md`、`screenlab-rules.md`。

## 0. 问题总览

| # | 问题 | 状态 |
|---|---|---|
| 1 | 启动应用 / 打开网址（App 内 Intent 注入） | 待解决 |
| 2a | 坐标映射校准（归一坐标→实际落点） | 待解决 |
| 2b | 元素定位（该点哪里，视觉/mark） | 待讨论 |
| 3 | 打字（文本输入 + 提交） | 待解决 |
| 4 | 导航与手势（HOME/BACK/滑动/长按） | 待解决 |
| 5 | 一次性权限/初始化（SAW、IME 启用） | 横切前置 |

## 1. 启动应用 / 打开网址

- **现状**：只能靠 tap 找图标，受坐标限制；launch 能力缺失。
- **方案**：App 内构造 Intent——`ACTION_VIEW` + URL（指定 Chrome 包名），或 `getLaunchIntentForPackage(pkg)` 启动任意 App。
- **前置（5）**：Android 10 **后台启动 Activity 受限**（assist 是后台前台服务）→ 需其一：① 一次性 SAW「显示在其他应用上层」；② 走通知 PendingIntent 由真人点一次。
- **优点**：无需打字、无需坐标、无需读 UI 树。

## 2a. 坐标映射校准

- **现象**（#61 真机）：
  - `tap(0.125, 0.599)`（按截图估为微信）→ 实际打开**支付宝**；
  - `tap(0.260, 0.770)`（Chrome，两次）→ **无反应**（落进图标与 dock 间空档）。
  - 注入本身生效（有 App 被拉起），故是**落点不准**。
- **假设**：`capture` 帧 `1080×2312`（MediaProjection）与 `dispatchGesture` 的输入坐标空间不一致（原点/是否含状态栏、导航栏/缩放）。
- **待做**：标定 offset/scale（沿一条竖线打已知归一坐标，观察命中，反推线性映射）。
- 锚：`AssistServer.java:462-501`（`act`，`px=round(x*w)`、`py=round(y*h)`）。

## 2b. 元素定位（视觉 / mark）

- **问题**：即使映射准了，"该点哪里"仍需定位手段。
- **候选**：agent **视觉**"看图 mark 读坐标"——适用于**所有图形界面**（Linux/Windows/Android 通用）。**需专门讨论**（架构级，宜早定型）。
- 与原则的关系：视觉定位可**替代无障碍语义树**，保住 App 端"只做手势、不读树"的轻量定位。

## 3. 打字（文本输入 + 提交）

- **现状**：`act` 只支持 `pointer`（tap）。
- **路径 1｜无障碍 `ACTION_SET_TEXT` / `ACTION_PASTE`**
  - 需开 `canRetrieveWindowContent` + `getRootInActiveWindow().findFocus(FOCUS_INPUT)` 拿可编辑节点。
  - 限制：整串写入/粘贴，**不能逐键**；**API 29 无 `ACTION_IME_ENTER`**（回车另想）；部分 WebView/自绘框不吃；**必须读节点树**（与"不做语义树"冲突）。
  - 成本：低。
- **路径 2｜自带极简 IME（`InputMethodService`）**
  - 真人**一次性**启用并选中 → `commitText()` / `sendKeyEvent(KEYCODE_ENTER/BACKSPACE)` / `performEditorAction()`。
  - 优点：真·打字，逐键/回车/退格/Unicode；全 App 通用；**不读树**。
  - 代价：多一个组件 + 一次性设置；需处理"用完切回真人输入法"。
  - 成本：中。
- 两者可共存（IME 兜底 SET_TEXT 不支持的场景）。

## 4. 导航与手势

- **现状**：只有单点 tap；**无 HOME / BACK / RECENTS、无滑动/滚动、无长按**。连"回桌面"都做不到（#61 卡在支付宝前台）。
- **方案**：`InjectService.performGlobalAction`（`InjectService.java:86-90` 已有）+ `swipe`（`:79-84` 已有）暴露到协议 `act`；长按/拖拽按需。
- 归属：与 2a 互为地面基础——不先能自由导航，后续每步都难验证。

## 5. 一次性权限 / 初始化（横切前置）

- **SAW**「显示在其他应用上层」→ 服务 1（后台启动 Activity）。
- **IME 启用并选中** → 服务 3（路径 2）。
- 不是独立功能，但要显式列出、各归其问题。

## 6. 已知但别漏（非新功能）

- **时序/稳定性**：等界面稳定、`stale_snapshot`、注入自抑制窗口（`InjectService.INJECT_WINDOW_MS`）。
- **连接/授权**：一条连接一次同意（#61 已澄清；`AssistServer.java:320`）。

## 7. 建议顺序（待 YZ 裁决）

```
2a 映射校准 → 2b 视觉定型（贯穿所有 GUI，宜早定） → 4 导航手势 → 3 打字 → 1 Intent 启动
```

- 理由：2a/4 是其余能力的地面基础；2b 是横切方法、影响定位范式，宜在实现 3/1 前定型。
- 备选：**1（Intent）最小、无依赖，可提到最前做小验证**。
