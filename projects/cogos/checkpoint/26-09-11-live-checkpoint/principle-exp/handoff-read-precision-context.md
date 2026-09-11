# handoff｜读图精度 · 思考/注意力/提示词/模型/像素 + vf6 上下文组织（09-07 晚）

> 2026-09-07 晚。上游：`handoff-focus-scan-foveation-7.md`（第8轮，vf6 整合版落地）。本会话**换主线**：用 vf6 读体温单 p062，跟 YZ 挖「模型到底怎么读图 / 读准靠什么」，并测出 vf6 的上下文组织 bug（连续"可以"复读）。也堆了一批 vf6 改造。
> 新会话只读本文件即可接手；locus 记忆见 `projects/cogos/entries/2026-09-07-cogos-vision-thinking-attention.md`（结论+素材+vf6 改造清单，本文件是交接版）。

---

## 一句话状态

`vf6.py`（/tmp/kilo/vision）已改造：删 `pin/unpin/驻留`→视野两层（全景 current + 中央凹 fovea）、fovea 按源图分组存 `contexts[scene_id]`、`open` 已存在图=恢复上下文组图、修 P2 body 超限、加 `--no-thinking` 开关、打印 reasoning + `finish_reason=length`。读了体温单 p062，挖出「读准靠模型+像素，思考是增益器却是非单调」+ vf6 上下文串行不分区 → 复读 bug。**下一步（未动）：上下文分区/动作状态区、finish_reason 处理、关键字段交叉验证。**

---

## 二、核心结论（读图精度，已收敛，别翻案）

按权重（**模型差异 > 思考**，注意谱系偏差）：

1. **模型视觉能力 > 思考**（最重要）：同 600×800 缩略、同为无思考——网页版（强模型）几乎全对（何润珍/62/26021007/2026-02-03）；deepseek 无思考读错（名字三样、52、380…）。**主变量是模型，不是思考**。我此前把 deepseek 行为当通则＝**模型谱系偏差**，已修正。

2. **思考 = 非单调增益器**（同模型内）：
   - 用对：deepseek 上 thinking 救"打转/乱猜"（会追点、radius 逐级收紧）；网页版科室"金属→金城"、符号校正。
   - 用错：为自洽而**编造**且不自知（住院号 26021007→260021007 反而错、deepseek 读体温编 36.5~36.8）。
   - 提升幅度**与模型强弱成反比**：deepseek（弱）思考≈开/关质差；网页版（强）提升局部、可能局部退化。

3. **提示词**：能"指方向+逼诚实"（逐字读、看不清则标"疑似/看不清"→不脑补、会拒答、年龄读对62），但**不加推理深度、不补像素** → 模糊字仍单次猜错（"何润玲"、住院号"360…"）。

4. **像素/放大**：读准第一是像素（信息量）。像素够→无思考接近可用；像素不足→思考（多步去模糊，概率命中）或**放大 view（真像素，最可靠）**。

5. **单次前向永远不可全信**：任何模型单次会局部小错且不自知（金属/血压49/脉搏符号/住院号），**交叉验证兜底永远需要**——不看模型、不看思考。

**统一模型**：读准 = 模型能力 + 像素 +（思考=推理补/猜 | 提示词=定向+诚实 | 放大=真像素）。思考改变"想得深"，不改变"看得清"。

---

## 三、vf6 上下文组织 bug（本次新挖，待修）

**现象**：REPL 连续输入"可以"，agent 一字不差复读同一段（`vf6_repl_out_new/history.jsonl` 第14/16→15/17 行）。佐证：`contexts[image_1]` 只有 view_1（c0.5,0.5,r0.4），**从"你试试看"到两次"可以"都没发过任何 view 动作**。

**根因（上下文组织，不是"模型不会做"）**：
1. **上下文 = [system] + 完整文字 history + [视野图集] 串行拼接，不分区**。完整历史（含模型自己上一轮长文）被原样喂回 → 模型把"自己上轮长文"当"待延续模板"，收到短句"可以"就顺延复述（应声复读/parroting）。
2. **缺"动作/状态区"**：上下文里没有"上轮提议了什么、已执行什么、现在能做什么动作"。模型只会"说话"，没有"执行"落点；既然自己能"看/会想"却无动作痕迹，便停在提议、反复复述。
3. **视觉图集每轮相同**（无新 view）+ 与对话文字纠缠（没当作独立"观察状态"）→ 无新信息打断续写。

**改进方向（未做，候选）**：把上下文按角色分区——①规则区(system) ②观察状态区(当前视野图+id/坐标/属性) ③动作状态区(可执行动作+上轮提议/已执行) ④对话历史区(纯文字、按轮、可截断)。关键：**观察/动作与对话文字分开 + 加动作状态区**。需做对照验证"分区是否真减复读/提执行"。

---

## 四、deepseek 技术观察

- `thinking` 只有 `{enabled}`，**无思考预算**（budget_tokens 是 openai 专属，此处无效）。
- 思考链(reasoning_content)与 content **共享 max_tokens**；思考过长→`finish_reason=length` 硬切→content 空→vf6 只读 content→空文本+无动作。
- **token 越大越糟**（模型把额度当"还能继续想"，催其穷举思考不收尾，content 越易空）。"加大 token 防截断"是**反方向**；应约束思考长度或检测 `finish_reason=length`。
- lm-service 把 deepseek reasoning_content 归一为独立 `reasoning` 字段（base.py:265）；vf6 丢弃（只读 content）。

---

## 五、vf6 改造清单（本会话已落）

- 删 `pin/unpin/驻留`；视野改两层（全景 current + 中央凹 fovea）。
- fovea 按源图分组存 `contexts[scene_id]`（property `fovea` 返回 `contexts[current]`）；`open` 只切 current、不再清空；`open` 已存在图=恢复该图上下文组图（缓存到盘，改指针重放）。
- 修跨图 view 分组 bug：产物进 `contexts[orig_id]`（被看的那张），而非 `contexts[current]`。
- `run_step` 内循环**不再累积图 base64**（base 纯文字 + 每轮单次 `build_vision`，受 `FOVEA_MAX=4`）→ 修 P2 body 超限。
- 加 `--no-thinking`（默认 thinking 开）；打印 reasoning（前400 + 全文入 thinking.log）+ `finish_reason=length` 提示；`MAX_TOKENS` 现 8192。
- 协议 SYSTEM 改两层（全景→中央凹）+ 说明"open 已存在图恢复上下文组图"。

---

## 六、文件 / 素材 / 后端

- `vf6.py`（/tmp/kilo/vision）：主工具（一次 `msg.txt` 或 `--repl`）。
- 素材：`p062.jpg`(3468×4624 原图)、`pano_p062.jpg`(600×800 缩略)、`name_crop.jpg`(姓名放大)、`locate_exp/`。
- 脚本：`_native_intro.py`(原生无思考无工具单图)、`_compare.py`(思路开/关各3次)、`_prompt.py`(提示词版3次)、`_vf6_check.py`(状态级上下文恢复)、`_vf6_agent_check.py`(真实对话多轮)。
- 会话 out：`vf6_p062_out/_thk/_thk2/_thk3/vf6_repl_out_new/vf6_repl_out_new_1`（vs trails 轨迹图）。
- `thinking.log`：推理链全文。
- **真值**：何润珍 / 女 / 62岁 / 住院号 26021007 / 科室 金城精神专业 / 2026-02-03 起 / 身高150 / 体重58 / 血压首格 116/69。

后端：`python3.11 -m cogos.lm_service.cli server --port 11434`（会话级进程、易被回收，新会话需重开）。KEY `ik_REDACTED`（`LmClient(KEY)`）。

跑法：`cd /tmp/kilo/vision && python3.11 vf6.py msg.txt [--scene p062.jpg --pano pano_p062.jpg --out DIR]`；`--repl` 交互；`--no-thinking` 关思考。REPL 用同 `--out` 重进会 load 状态续上下文（图不进持久上下文，视区只重注入 current+末4 fovea）。

---

## 七、遗留 / 下一步（待 YZ 裁决）

1. **上下文分区/动作状态区**（新）——最值得做的方向：上下文按角色切块 + 加"动作状态区"，验证是否减复读/提执行。候选做对照原型（串行 vs 分区）。
2. **`finish_reason=length` 处理**：检测到就提示重试/换短思考/降级关 thinking。
3. **"证据引用 + 不确定出口"** 作主流程（提示词已能逼出诚实，可低成本并入）。
4. **关键字段交叉验证兜底**（读两遍一致才上报，不一致标疑）。
5. **"连续≥N轮只说话无动作/内容近似 → 注入'把提议执行成动作'"**（或"同坐标重复 view≥N 注入提示"，早记候选）。
6. vf6 细节：`map_to_pano` 跨链条、ref target 不自动进视野需用户 open。
