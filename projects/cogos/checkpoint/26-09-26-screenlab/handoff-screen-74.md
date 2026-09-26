# handoff｜→ #75（#74 已落 v2 接入代码；剩 usage 真机验证）

> 规则 / 环境不在本文件——先读 `screenlab-rules.md`（含交接阈值 **150K**）。
> 本文件由 **#74** 写给后继 **#75**；#74 的编码任务已完成（commit+push），**未做** usage 真机验证。
> 上游：#73 与 YZ 对齐封板接口（`design-computer-v2-interface.md`）；#74 按封板稿落码。

---

## 复制这段作为后继会话的第一句

```text
接 #75。上一会话 #74 已按封板稿（../checkpoint/design-computer-v2-interface.md）落完【v2 接入】代码并 commit+push（cogos @ 8b4e685, origin/feat/screenlab-p2），全量 pytest 1231 passed；**剩 ⑤ usage 角度真机验证**（X11 fetch→act 落点、on_change=skip 生效；再 Windows；Android 动作补齐排后）。不要重新设计接口。

先按序读（纯文本）：
0. ../checkpoint/screenlab-rules.md（规则；交接阈值 150K）
1. ../checkpoint/design-computer-v2-interface.md（v2 封板接口）
2. ../checkpoint/screenlab-work.md §状态（#74 落码结论）
3. ../checkpoint/handoff-screen-74.md（本文件）

任务（按序）：
① 先跑 `tools/snapshot.sh` 看靶机状态；起 X11 surface（`screenlab open <account>`，见 rules/screenlab-work #71），以 agent 身份按**模型面入口**验证：`screen_fetch` → 真值对照（xdotool 窗几何/pointer）→ `screen_act(op="click", point=...)` 落点 == 真值；`on_change="skip"` 在目标区已变时**不注入**、返回新帧。
② 验 `screen_act` 返回帧含落点标记；验视觉面 `see/mark/coord` 在 fetch 帧上 coord 与真值吻合（放大链）。
③ 再 Windows 同形状（`tools/windows.sh` + Tk 靶，真值 center）。
④ 全过则更新 CHANGELOG/handoff；Android 动作（launch/nav/drag）按冻结动词集补齐排后。

约束：允许 commit/push（不 tag）；10min 闹钟；文档二手，动手前以代码/实测为准。
```

---

## #74 做了什么（结果）

**接口（封板稿）→ 代码，commit `8b4e685`（已 push origin/feat/screenlab-p2）**

- **`cogos/agent/impl/graphics.py::ScreenChannel` v2**：加 **current-frame 状态**（`_current`，本地原始帧路径，模型不可见）；新增
  - `fetch(max_dim, settle)`：整屏抓取、change-gated 短 settle、设 current frame，返回 `{path,size}`；
  - `act(op, region, point, on_change, text, keys, dy, to, button, clicks)`：pre-grab→本地 `change.diff_bbox` 判目标区变化→`on_change∈{act,skip}` **客户端判**→注入→有界 settle→返回 `{acted,skipped,region_changed,raw_path,size,landing,stable}`；落点 = `point`，缺省 `region` 中心；
  - `save(path=None)`：current frame 落持久文件。
  - 旧底层协议 act 更名 **`raw_act`**（`imgctx.py`/`tools/agent.py` 已跟进）；`on_change` 非 act/skip 报错；`drag` 暂报 unsupported（协议无 drag）；模型 op→协议 op：click/move→`pointer`、scroll/type/key、launch→`launch`。
- **工具注册（`cogos/agent/tools.py`）**：`make_screen_specs` 改为 **`screen_fetch`/`screen_act`/`screen_save`**；`screen_act` schema 冻结 `op∈{click,move,drag,scroll,type,key,launch}`、`on_change∈{act,skip}`、region/point 归一化字符串。
- **视觉面暴露**：新增 `make_vision_specs`（**`see`/`mark`/`coord`**，包 `cogos/image_ctx`），`app.py` 无条件注册；域根 `work_dir/vision`。`screen_act` 落点标记由工具层 `_render_landing` 用 image_ctx 叠十字（**best-effort**，失败回退原帧——注入已发生，不能因渲染失败而报错）。
- **`launch`** 进 `screenlab/proto/protocol.py::ACT_OPS`（唯一触协议处）。**daemon 未接 launch 后端** → 现调用回 `backend_error`（Android 动作补齐时补）。
- **测试**：`tests/agent/test_screen.py` 重写（channel v2 fetch/act/save + 三动词 + see/mark/coord join 链）；`tests/screenlab/e2e/tool_loop_e2e.py` 跟到新动词。全量 **`pytest` 1231 passed, 4 skipped**；提交前跑 `tests/screenlab + tests/image_ctx` = 94 passed。

## 留给 #75 的关键点

1. **未做真机验证**（#74 会话长、YZ 指示先交接）：① 面全在 coding + 单测层面；需按 rules 的 **usage 角度 + 独立地面真值**（xdotool / Windows Tk 靶 README）复验。
2. **X11 账户**：用 `zhengyp`（uid 1000，socket `unix:/run/user/1000/screenlab.sock`）——`human`(1002) 不可用（见 screenlab-work #71）。
3. **已知缺口（记录，非本任务范围）**：模型面工具结果只带图片**路径**；cogos LM 管线 `assemble_tool_messages` 把 tool content JSON 化、`router.infer_modalities` 只看 user content → **tool result 的图路径目前不会成为模型可看的附件**。"图不转文字"在产品 agent 内尚未真正接通；需另立小任务。
4. **验证脚本锚**：`screenlab/tools/{x11.sh,windows.sh,*_selftest.py,imgctx.py}`；产品面入口是 `make_screen_specs` 的 fn（可直接像 `tool_loop_e2e.py` 那样驱动）。

## 锚
- 接口：`../checkpoint/design-computer-v2-interface.md`；目标：`../checkpoint/spec-screen-1.md §0.0`
- 代码：`cogos/agent/impl/graphics.py`、`cogos/agent/tools.py`、`cogos/agent/app.py`、`screenlab/proto/protocol.py`、`cogos/image_ctx/`、`screenlab/service/change.py`
- 提交：`8b4e685`（`origin/feat/screenlab-p2`，不 tag）
