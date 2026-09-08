# 读图精度 · 思考/注意力/提示词/模型/像素 关系（09-07，principle-exp）

> 交接：`/home/zhengyp/work/A/checkpoint/principle-exp/handoff-read-precision-context.md`（新会话先读它）。

> 场景：`vf6.py`（/tmp/kilo/vision）读体温单 p062（姓名/年龄/住院号/科室/单位符号）。跟 YZ 一轮轮用「无思考 / 有思考 / 提示词 / 不同模型 / 不同像素」做对照，挖"模型到底怎么读图"的机制层。聚焦**读准到底靠什么**。

## 收敛结论（按权重）

1. **模型视觉能力 > 思考**（谱系差，最重要）
   - 同一张 600×800 缩略、同为无思考：网页版（强视觉模型）几乎全对（何润珍/62/26021007/2026-02-03）；deepseek 无思考读错（名字三样、52、380…）。→ **主变量是模型，不是思考**。
   - 我此前把 deepseek 的行为当"通用规律"，这是**模型谱系偏差**，已修正。

2. **思考 = 非单调增益器**（同模型内比）
   - 用对：deepseek 上 thinking 救"打转/乱猜"（会追点、radius 逐级收紧）；网页版科室"金属→金城"、符号校正。
   - 用错：为自洽而**编造**（住院号 26021007→260021007（反而错）、deepseek 读体温编 36.5~36.8），且**不自知**。
   - 提升幅度**与模型强弱成反比**：deepseek（弱）思考≈开/关质差；网页版（强）提升局部且可能局部退化。

3. **提示词**：能"指方向 + 逼诚实出口"（逐字读、看不清则标"疑似/看不清"→ 不再脑补、会拒答、年龄读对 62），但**不加推理深度、不补像素** → 模糊字仍单次猜错（"何润玲"、住院号"360…"）。

4. **像素/放大**：读准第一是像素（信息量）。像素够→无思考接近可用；像素不足→思考（多步去模糊，概率命中）或**放大 view（真像素，最可靠）**。

## 统一模型

- 读准 = **模型视觉能力 + 像素量 +（思考=推理补/猜 | 提示词=定向+诚实 | 放大=真像素）**。
- 思考改变的是"想得深、会自检"，**不改变"看得清"**；它用得好纠偏、用不好为自洽编造。
- **单次前向永远不可全信**：任何模型单次都会局部小错且不自知（金属/血压49/脉搏符号/住院号），**交叉验证兜底永远需要**，不看模型、不看思考。

## 技术观察（deepseek）

- `thinking` 只有 `{enabled}`，**无思考预算**（budget_tokens 是 openai 专属，此处无效）。
- 思考链（reasoning_content）与 content **共享 max_tokens**；思考过长 → `finish_reason=length` 硬切 → content 空 → vf6 只读 content → 拿空文本+无动作。
- **token 越大越糟**：模型把"还有额度"当"还能继续想"，穷举思考不收尾，content 越易空。所以"加大 token 防截断"是**反方向**；应约束思考长度或检测 `finish_reason=length`。
- lm-service 把 deepseek reasoning_content 归一为独立 `reasoning` 字段；vf6 丢弃。

## vf6 改造（本会话）

- 删 `pin/unpin/驻留`；视野改两层（全景 current + 中央凹 fovea）。
- fovea 改为**按源图分组**存 `contexts[scene_id]`；`open` 只切 current、不再清空；`open` 已存在图 = **恢复它的上下文组图**（缓存到盘，改指针重放）。
- 修跨图 view 分组 bug（产物进 `contexts[orig_id]`）。
- `run_step` 内循环**不再累积图 base64**（每轮重建纯文字 messages + 单次 `build_vision`，受 FOVEA_MAX=4 约束）→ 修 P2 body 超限。
- 加 `--no-thinking` 开关；打印 reasoning（前400 + 全文入 thinking.log）+ `finish_reason=length` 提示。
- 待办（未落）：`finish_reason=length` 触发重试/换策略；提示词"证据引用+不确定出口"作为主流程；关键字段交叉验证兜底。

## 素材

- `/tmp/kilo/vision/`：vf6.py、pano_p062.jpg（600×800 缩略）、p062.jpg（3468×4624 原图）、thinking.log（推理链、69KB）、_compare.py / _prompt.py / _native_intro.py、vf6_p062_out*/（会话状态）、name_crop.jpg。
- 真实姓名：**何润珍**、女、62岁、住院号 **26021007**、科室 **金城精神专业**、日期 2026-02-03 起、身高150、体重58、血压首格 116/69。
- 后端：`python3.11 -m cogos.lm_service.cli server --port 11434`（会话级进程，易被回收需重开）。KEY `ik_c47WkfAw7E5v6Ck8idMHgg`。
