# handoff｜交接给新会话 · 2026-09-24 #47

> 接 #46。本会话 = 从目标定出 3a 路线 + 建活文档/codebase + 落 **E1（agent 侧 auth 接线）**、真机复验 **E2（3a 机制链端到端）**。
> 全部代码改动**未 commit**（YZ 未定）。**下一会话从 E4（YZ 下场体验验收）起**。
> **规则/环境不在本文件**——先读 `screenlab-rules.md`。

---

## 复制这段作为新会话的第一句

```
先按序读三个文件，再动手：
1. ../checkpoint/screenlab-rules.md（规则，先读）
2. ../checkpoint/screen-assist-status.md —— 先做 §0「切会话须知」里的核实：
   那些"不是我写的"痕迹（/tmp/kilo/e2_agent.py、e2b_agent.py、§4 的 E2 记录、timer）
   大概率是本会话早前轮次（上下文被压缩）自己写的；别当成外部第二个会话、别去找不存在的冲突。
3. ../checkpoint/codebase.md（代码认知基线，别重读代码）

状态：Goal 2 / 关系 3a —— E1 + E2 已过。真机 surface 的 human@:0 上，
"agent 侧公钥握手 → 真人 consent → capture/act → 物理键抢占(role→observer,下次 act no_input_bit)
 → consent --cancel 收回(channel_closed)" 已端到端实跑通。

代码：../cogos @ feat/screenlab-p2，全部改动未 commit（11 文件，见 codebase.md 版本戳）；先别 commit。
靶机：surface 100.100.137.78，human@:0 attached，daemon 带 --presence --tcp 100.100.137.78:8911 --auth --consent event。

下一步：
- E4 体验验收（需 YZ 下场）：YZ 在宿主 Windows(100.112.50.115) 打开 centos9 的 VBox 控制台窗口 → 得到真鼠标；
  我发起一次连接，YZ 用真鼠标动一下，验"拿回"是否即时 + 同意入口体感是否顺手。
- E5 提交 / tag / 回写分册（待 YZ 定）。

纪律：目标裁决（spec-screen-1.md §0.0）；能推的自决并记进 status；命令走 terminal（非阻塞）；
不 commit；验收用公开入口 + 地面真值（import -window root / xdotool getmouselocation），不用自写 e2e 自证。
```

---

## 本会话做了什么（给人类的摘要，不必复制）

- **路线**（从 §0.0 3a 导出）写进 `screen-assist-status.md`：段 A 功能打通（AI 主导）/ 段 B 体验验收（YZ）；
  明确不做：SETTLE/IDLE/物理热键、弹窗(v1 CLI 够)、Wayland。
- **E1**（代码，未 commit）：`cogos/agent/impl/graphics.py` 加 `key_path` → `AuthClient.attach()` 握手 + `ScreenClient.from_channel()`；
  `config.py`/`app.py`/`terminal.py` 透传 `computer.graphics.key`。缺省 = 旧路。`pytest tests/agent/test_screen.py tests/screenlab` = 33 passed。
- **E2**（真机验证）：`/tmp/kilo/e2_agent.py` + `e2b_agent.py`（用 `ScreenChannel(key_path=…)`，即 `computer` 工具同一实现）
  在 `human@:0` 跑通全链，地面真值命中（`xdotool` 落点 `960,546`；`import` 尺寸 1920×1093）。
- **认知/文档**：新建 `../checkpoint/screen-assist-status.md`（活文档=路线+进展）；重写 `../checkpoint/codebase.md`（版本戳 0697c27 + 3a 新代码锚点）。
- **插曲**：一度把上述痕迹误判为"第二会话"，经 YZ 提醒，判定为**本会话自己的早前轮次**（幻觉），已在 status §0 记为待核实。

## 锚

- 活文档/路线：`screen-assist-status.md`
- 代码认知：`codebase.md`
- 设计：`design-screen-assist.md`（§3.2 已定）
- 实验：`screen-assist-exp-log.md`（§5/§6/§7）
- 目标：`spec-screen-1.md` §0.0
- 上一轮：#46 `handoff-screen-46.md`
