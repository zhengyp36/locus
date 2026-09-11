# handoff-1 — 视觉定位诊断：对话式脚本实验（会话交接）

> 交接时间：2026-09-06 中午。
> 上游：`locate_issue.md`（V1 定位循环两轮实验 + 待讨论问题）。
> 本会话完成了：方法论转变 + 对话式诊断脚本 `diagnose.py`（方案A）+ 定位"图像回灌通道"根因 + 修好视觉闭环 + 三步任务跑通 + 稳定性3测 + 业界方案调研。
> 新会话读本文件即可接续，不必重读长会话。

## 一句话状态

**视觉闭环已打通**：`diagnose.py` 让 LLM 自调 `info/extract/draw`（方案A），图像经 **user 消息**回灌后模型能真正"看到"自己取出的局部，三步任务（读图→找纠缠矩形→draw 框出）可走通。但暴露一个深层问题：**LLM 自我校验是"反馈为真、却无法据此进一步决策"**（它知道"可能偏"，但算出了精确坐标又弃用、无法自洽终止"觉得偏 vs 其实准"的冲突）。下一步方向 = **机制层接管坐标校验/收敛**。

## 核心根因（已证实，最重要）

**DeepSeek 的 `role:"tool"` 消息不支持图像**。图像若塞进 tool 消息的 content，经 lm-service `_vendor_tool_message`（`cogos/lm_service/providers/base.py:166`）会 `json.dumps` 压成一整坨文本，deepseek 收到的是"这有一张 data URL"的 JSON 字符串，模型把它当纯文本读 → 产生"ASCII art/乱码"幻觉 → **看不清图就会复读打转**（此前 0/2 成功）。

实验证据（同图不同路径）：
- `user` 消息带图：✅ 准确描述渐变+网格+文字。
- `tool` 消息带 `image_url` 数组（经 lm-service）：❌ 当文本 → "ASCII art"。
- `tool` 消息带图（直达 deepseek API）：❌ 返回空 content。
- 直达 deepseek 已确认 `role:"tool"` 无视觉通道 → **改 cogos 也没用，得绕道**。

**修复**（已在 `diagnose.py`，未动 cogos）：`tool_message` 只回文本元数据；新增 `push_image_observation()`，`extract`/`draw` 产出图后**追加一条 user 带图消息**回灌给模型看。

## `diagnose.py` 现状

- 路径：`/tmp/kilo/vision/diagnose.py`
- 用法：`python3.11 diagnose.py <msg.txt> --img <图> --history <jsonl> --max-trials N --max-tokens N`
- `temperature=0.2`（已改）；`TOOLS` 含 `info/extract/draw`；含 `parse_xml_toolcalls`(html.unescape) 兜底模型把工具写成文本XML。
- 视觉闭环 = user 消息回灌图（关键）。
- 下一步未做：**机制层坐标台账 + 数值收敛判定**。

## 本会话关键观察

1. **历史残留污染**：`diagnose_history.jsonl` 累积，没清就能让模型响应旧上下文（"我一句问‘看到了什么’，它却去找纠缠矩形"）。换任务必须 `rm` 清 history。
2. **成功路径一次走通**（跑通的那次）：`info→extract→extract→draw→extract(自检)`，红框命中真值 (0.596,0.513)，模型还 crop 自查。
3. **稳定性 3 测**（各清 history）：3/3 都走到 draw 且都有自检复核，"复读打转"已消除。**坐标核验**（联合框中心 vs 真值 (0.596,0.513)）：

   | run | draw次数 | 中心 | 偏移 px | 行为 |
   |---|---|---|---|---|
   | run1 | 1 | (0.599,0.510) | **+2.4,-1.8** | 一次命中 |
   | run2 | 2 | (0.598,0.514)→(0.597,0.512) | +1.6→**+1.2** | 命中但**反复纠结** |
   | run3 | 1 | (0.585,0.505) | **-8.8,-4.8** | 框住略偏左、框(0.080正方)偏大 |

   **三次都命中，无一真正框错。** 旧判断"run3 偏左罩进 range"是**误判**（实测偏移 -8.8px，是"框住但偏左下、框偏大"，非框错目标），已修正。
4. **run2 = "反馈为真、无法进一步决策"实证**（新会话重点素材，在 `run2.log`，**注意不是"假反馈"**——用坐标数据核实过）：
   - 它说"框偏了/没完全框住"（line 51 起多次自我质疑）→ 却**没给偏差方向/量**。
   - 算出更准坐标（line 121-122）→ 又弃用，回头说"当前已基本准确"。
   - 最终"虽然偏大但可接受" + 自评置信度 90%。
   - **关键数据**：两次 draw 联合框中心 = (0.598,0.514) / (0.597,0.512)，相对真值偏移仅 **+1.6/+1.2px**——**早就命中了**。draw#2 还把框从 (0.040,0.072) 收窄到 (0.035,0.060)，是有效贴合。
   - 所以它不是"乱说/没改准"，而是**两种认知来源打架**：视觉直觉"感觉没贴准" vs 几何计算"偏移1px"。它无法裁决"信直觉还是信数字、要不要重画"，**停在质疑、做不出确定性决策**。
   - → 这正是把"确认够不够好"的裁决策**必须交给机制层**（用几何收敛阈值一刀切）的原因。与 V1"明知 single rectangle 也不修正"同构，但归因修正为"反馈为真、缺裁决规则"。
5. **LLM 能"记住"坐标吗**：坐标值在上下文里（机制上能引用），但模型只做**语言级印象记忆**（"偏上/偏大"），**不建数值台账做中心比对**。这正是机制层该补的。
6. **判别原则（YZ 澄清，重要）**：区分"假反馈"（乱说）与"反馈为真、无法进一步决策"（知道错但上下文无法推动改进）。run2 属**后者**——判据是**核坐标数据**：两次 draw 都命中真值、且 draw#2 收窄尺寸，说明它并非乱画，而是"有直觉偏差但缺裁决规则"。"假反馈"应表现为给出与实测不符的坐标；"反馈为真"则是坐标确实好、只是它口头犹豫。**下结论前要拿客观坐标比对，不能只看文本声称。**

## 待讨论/待做（新会话）

1. **机制层坐标台账 + 数值收敛判定**：每次 draw 记录框中心，计算到目标的偏移差，|Δ|<阈值才接受——把"确认够不够好"的裁决策从 LLM 手里拿走，断掉"既觉得偏又觉得准、无法自洽终止"的悬置。
2. **失败回退路径只部分演示**：run2 有"质疑→重画 v2"，但没见"reject→恢复全屏→换区域→精确命中"的完整闭环；可造更难的图逼它真失败。
3. **多视图投票的适用边界**（讨论产物）：位置未知时投票是病态的——coarse(搜索) 与 fine(精化) 两段制，投票只属 fine；coarse 需机制层兜底（网格/检测器枚举候选/多候选校验），不能只给 LLM 一个模糊方向。
4. **点击 vs 包围**：点击=区域命中(cheap)，包围=边界回归(hard)；两段式：先定位目标所在区域，再在小区域内精化边界。
5. **业界方案已确认**（详见 locate_exp.md）：GUI-Lens(coarse-to-fine cropping+coordinate priming+visual verification)、GUI-RC(spatial voting)、UI-Zoomer(uncertainty-gated zoom)、Zoom Consistency。三组件跟我们 checkpoints 逐条对应。

## 业界对照（GUI-Lens, arxiv 2608.03270）

| GUI-Lens | 我们 checkpoints | 状态 |
|---|---|---|
| 粗到细裁剪，模型自选 region/scale | checkpoint-15 focus(center/range) | 印证 |
| 坐标参考(OCR+组件检测) | checkpoint-2 region链/网格定位 | 印证 |
| visual verification(reject→恢复全屏重启) | checkpoint-17 不能听声称 | 印证且补上"校验"这一环 |
| 局部位映射回原图 | checkpoint-2 region链换算 | 印证 |
| 最多8轮，95%样本4轮内停 | focus循环停的条件 | 借鉴 |
实证：Cropping 是主增益；Verification 提升可靠性；coordinate priming 帮弱后端(flash属这档)。

## 关键文件 / 命令

- 脚本：`/tmp/kilo/vision/diagnose.py`
- 图：`/tmp/kilo/vision/locate_exp/detail.jpg`(4000×3000) / `pano_800.png`(800×600)
- 产物：`/tmp/kilo/vision/locate_exp/`（run1-3.log 稳定性3测、annotated*.png/entangled*.png 各次框出图、center_right*.png crop、msg.txt=三步任务、diagnose_history.jsonl=最近一批跑完后的历史）
  - run2.log 是"反馈为真无法决策"实证的关键素材（含两次 draw 坐标）。
- 实验说明：`/home/zhengyp/work/A/checkpoint/locate_exp.md`（方法+工具+本次素材）
- 需求文档：`/home/zhengyp/work/A/checkpoint/locate_issue.md`
- 后端：lm-service 在后台跑（`python3.11 -m cogos.lm_service.cli server`，端口 11434，用 python3.11 不是 3.9）
- 复跑三步任务：
  ```
  rm -f /tmp/kilo/vision/locate_exp/diagnose_history.jsonl
  python3.11 /tmp/kilo/vision/diagnose.py /tmp/kilo/vision/locate_exp/msg.txt --max-trials 10 --max-tokens 3072
  ```
