# toolbox 改进建议（工作稿，2026-09-28）

> 来源：S5 e2e + 16 次无外溢复跑暴露的问题。总判断：不是"模型笨"，是**调用边界缺契约校验**——catalog 声明了参数、help 也讲了，但 `call` 把 args 当 kwargs 直透实现层，猜错参数名必然以 Python 内部异常炸出来。目标不是"别猜"，而是**让猜错代价低、反馈清晰**。
>
> 关联：`../projects/cogos/entries/2026-09-28-cogos-toolbox-behaviour-probe.md` · `../projects/cogos/ISSUES.md`。

## 建议清单（按优先级）

1. **`call` 边界按 catalog 校验参数**（强倾向，改动小）
   - `toolbox._call` 进实现层前用 `cap.params` 查：未知键 / 缺必填 / 类型不符 → 回结构化错误。
   - why：错误现在来自实现层，泄漏 `make_send_msg_spec.<locals>.fn()`；契约就在 catalog，在哪声明就在哪校验；未知键可回"该能力参数：target/content"，模型一次改对，省一次 help 往返；实现层不必各自防御。

2. **错误形状统一为"可读、可行动"**（倾向）
   - 如 `未知参数 to；本能力参数为 target(必填) / content(必填)`。
   - 边界：只"列出合法参数"，**不做**模糊匹配 / 自动纠错 / 意图匹配（执行须精确；独立意图匹配器、意图翻译藏工具已否）。

3. **help 去掉/改写"绑定"行**（倾向，顺手）
   - `绑定：send_msg` / `绑定：terminal_open + terminal_exec + terminal_observe` 是机制实现细节，模型用不到，还诱导它"理解实现"而非"用能力"。
   - `时间形态 sync/async` 保留（关系到要不要等）；绑定改面向模型的话，或删。

4. **不消灭"先猜"，把自纠链做便宜**（方向判断，不急）
   - 不往总览加能力清单防猜（退回"散"）；不引入意图层。正确形态 = "猜错→可读报错→一次自纠"。
   - why：机制给位置、错误给反馈。

5. **按误差=切点记账**（先记不做）
   - "猜错参数→help 自纠"是真实误差事件，按理论 #18（切点=误差）值得在机制层留痕，供将来"经历表示"。
   - why：契合当前主线，属大方向。

6. **修"重复外发"**（新增，明确回归 bug）
   - `cogos/agent/consciousness.py:52` 去重判断写死 `call["name"] == "send_msg"`，S3 暴露 `toolbox` 后恒假 → `_handle_done` 兜底每次补发最终文本。真实模型 16/16 复现；S5 真身份亦 2 条。
   - 倾向：按 `toolbox` 内层 `name` 判，或在 registry 层记"是否发生过 send"，而非在 consciousness 解析名字。

## 排序

先 **1 + 2**（同一处改动，收益最大）→ 顺手 **3** → **6**（bug）→ **4 + 5** 记账、留讨论。

## 被否 / 不采用

- 模糊参数纠错、自动改写参数名；独立意图匹配器；用意图翻译藏工具；往常驻总览加逐工具清单。理由统一：执行必须精确，清晰 ≠ 替模型决定。

## 评估补充（09-28：评估这批建议时发现，待议）

- **N1｜catalog 暴露但用不起来的能力**：`computer.command.open`/`list` 已进 catalog，但 `toolbox._call` 对 `observe/send/read/write/edit` 等强制注入**单一默认会话** id → 模型无法操作自己刚 `open` 的会话；`answer_auth` 亦仅声明、机制选槽未接。→ 模型面出现"看起来能用其实不能用"的陷阱。建议：撤下 `open/list`（及未接的 `answer_auth`），或补 id 传参（= A2 多会话）。
- **N2｜catalog 与 registry 无一致性自检**：catalog 声明的 `impl/steps` 若与 `_build_specs` 漂移，只在运行时炸。建议加**启动期断言**：catalog 每个能力绑定的 ToolDef 必须都在 registry。
- **N3｜`run` 固定 ~6s 有界等待**：`toolbox._observe_settled` 固定轮询 ≤~6s；慢命令可能被截断且模型不知情（无 `wait` 参数）。待评估是否把等待变为可感知/可参数化。
- **N4（待确认）**：`web_cancel`/`phone_cancel` 等 impl 未进 catalog → 模型无法取消长任务，是否有意？
