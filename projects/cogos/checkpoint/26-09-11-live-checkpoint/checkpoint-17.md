# checkpoint-17 — 视觉引擎可行性实验：先人工走三接口（实验思路）

接 checkpoint-16（三接口功能明确）。三接口让 LLM 组织，但底层 img_tool 目前只有 `info`/`extract`（呈现/裁剪），缺"定位/指认"。先不写代码，用底层工具手走 `open`/`focus`/`isolate` 验证可行，把不确定性从高到低消解。

## 思路（三步）

1. **选图**：一张有清晰目标的图。
2. **纯机械手走**（img-cli `info` + `extract`，手动敲参数，无 LLM）：open/focus/isolate 各自"参数→产物（路径/尺寸/scale）"。钉死：
   - 坐标换算：`center/range` → `extract` 的 `x,y,w,h`（归一、clamp、全图↔视图映射）。
   - `max_dim` 档 / open 全景缩到多大 / extract 返回 scale 哪些算"到底（有损边界）"。
   - isolate：人凭眼睛给 target bbox → `extract` crop，顺带回答"**物理裁掉 vs 掩掉**"（crop 产物够不够，还是需 mask）。
3. **手动 LLM 走**（LmClient 视觉模型）：出摘要 / locate 语义方向 / isolate bbox → 用 `extract` 落地，验证语义闭环。
4. 两条都通 → 把 LLM 调用 + 机械封装成 cog-func / ImageObj 方法。

## 人工阶段覆盖 vs 不覆盖

- **覆盖**（纯机械）：extract/info 行为、坐标换算、"给定 region 能否正确裁图"、产物质量。
- **不覆盖**（LLM 层，人工只能"人扮演"喂坐标/bbox）：locate 语义→坐标、isolate 目标边界在哪、摘要描述。

## 验证标准

- **机械链路**：给定 region/bbox 能正确裁出图，产物尺寸/scale 符合预期。
- **LLM 闭环**：LLM 的定位/摘要能成功落地到 extract，语义与机械对上。
- **输出**：一个边想边走的记录，暴露坐标换算和 extract 的真实参数/行为。

## 遗留 / 未定

- 人工阶段 isolate 的 bbox 只能人喂（无机械指认工具）——本身即证据：机械层缺"定位/指认"，locate 必须靠 LLM。
- isolate 的"裁掉 vs 掩掉"由人工 crop 产物回答。

## 实验进展（进行中，已走完 open，2026-09-05）

### open 已打通（机械 + 摘要两层）

- **机械**：`info` + `extract --region 0,0,1,1 --max-dim 800` → 全景。`pick_scale` 是**长边 ≤ max_dim 等比缩放**（>max_dim 才降，否则原尺寸）。实测：`p062.jpg`(3468×4624) → 600×800 scale=0.173；`detail.jpg`(4000×3000) → 800×600 scale=0.2。max_dim 默认 800 取自 deepseek 官方 doc 模型能力档，**不纠结清晰度**（明确：全景就是给"整图尺度"内容，看清是 focus 的事）。
- **识图通道**：`read` 直接把图文件当附件读入即可看图（无需 gemini-vision，已从 `~/.config/kilo/kilo.jsonc` 移除；老会话工具列表残留属正常）。
- **LLM 摘要**：走 `cogos-lm-service`（`cogos/lm_service/`）。**必须用 python3.11**（`StrEnum` 是 3.11+；默认 python3.9 会 `ImportError`）。需先起 `python3.11 -m cogos.lm_service.cli server`，用内部 key `ik_REDACTED`（尾号b111 / `deepseek-v4-flash-vision-exp`，`modalities:[image]`）。router 依 message 里的 `image_url` 部件自动选 vision 模型，无需指定 model。
- **一次性 helper**：`/tmp/kilo/vision/ask_vision.py <图> "<提示词>" [system] [max_tokens]`——base64 data-URL 拼 `image_url` → LmClient → 打印文本；stderr 打 usage/finish_reason。后续所有 LLM 验证一条命令复用。

### 概念修正（YZ 纠正）

"全景不需要看清细节、抓全局语义锚"**表述不准**。正确：采样后全景在**整图尺度上已清晰**——整图可读的内容已完备，再加分辨率只是**像素变多、无新信息**。真正的信息边界=**整图尺度可辨识**（open 全覆盖）vs **区域尺度才可辨识**（小字/精确值，需 focus → **crop 那个 region 看原生/高分辨率**，非放大整图）。接 checkpoint-4（看清只能 crop 缩 range）、checkpoint-11（看不清→crop，机制层）。

### 已验证样例

- `p062.jpg` 全景 → LLM 正确识"仪陇县人民医院体温单 / 女性62岁 / 记录体征"（与肉眼真值一致）。
- `detail.jpg` 全景 → LLM 描述"渐变+细密网格线+空心框+小字(HELLO/12345/vision/range/crop)，像编辑器/可视化截图"；**精确标注值（如 (456,123)）读不出** → focus 目标。

### 定位失败实证（关键）

在 `detail.jpg` 全景上做"语义定位"验证：人眼描述"左半区 X形框+image"——错（模糊全景脑补）；LLM 定位同目标——声称找到，但 bbox 落到 "12345"（另一真实元素）。**两者都证明：从模糊全景做精准指认不可靠，内容描述必失真、坐标准确**。放大到原生可辨带（`left_mid_band.jpg`）后内容才清楚。

## 重大转折 → checkpoint-18

走通 open 后讨论反转：从"ImageTool 替主 LLM 看 + 摘要"反转为"**主 LLM 自己看 + 工具按需加载 + 痕迹擦除**"。三接口三合一（单取图工具）、摘要作废、意图=加载器。**本文件后续 focus/isolate 手走实验不再单独推进**，架构结论见 **checkpoint-18**。

## 下一步

回到 **checkpoint-16 / 18**：三接口已简化为单工具 + 主 LLM 意图决定 region（见 checkpoint-18），坐标换算（region 链）、工具集面、擦除/摘除阈值实现时定。
