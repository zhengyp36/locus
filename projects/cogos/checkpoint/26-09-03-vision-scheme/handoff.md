# Handoff — cogos 视觉系统方案（会话交接）

> 日期：2026-09-03（三轮讨论收敛）。新会话加载本文 + `entries/2026-09-03-cogos-vision-scheme.md`（细节）+ 本体 `docs/vision-system-design.md` §14 即可恢复。当前处于「视觉方案架构收敛完毕，剩少量待定点，继续讨论」。

## 当前状态

视觉子系统方案经三轮讨论收敛出架构骨架（三层），已固化本体 `docs/vision-system-design.md` §14（新增「架构收敛」「精确给 + resize 鲁棒 + 定标」两小节）。剩几个待定点（region 表达细节、纸载体、显著检测、f(W,H) 标定），下一步在新会话继续讨论这些待定点。

> **后续推进（09-03 续）**：视觉定位已被 cog-func 范式讨论推进——视觉既非工具也非子系统，是 cog-func（img-tool 原语 + look_at 种子功能 + 生长功能），"工具 vs 子系统"分叉已化解。见 `entries/2026-09-03-cogos-cogfunc-paradigm.md`。

## 架构（最终收敛，勿再翻案）

三层，唯一智能主体 = 主 LLM（agent / 主 cu）：

1. **img-tool（底层原语，纯程序，无决策）**
   - `info(path)`：尺寸 / 格式 / 大小 / 能力探测（ok、max_block）
   - `extract(path, region)`：region 归一化坐标(0~1)，scale 自动推到「≤封顶内最高分辨率」，返回图 + 元数据（scale / region_echo / has_more_detail / grid 网格→坐标映射）
   - 短命子进程（grep 式），非服务，不用 asyncio；句柄退化为 path，无 close，无状态
   - 命名：组件 `img-tool` / CLI `img-cli` / Python 包 `imgtool`

2. **视觉子系统 = 主 LLM 看图时的手眼（机制 + 能力，无独立智能）**
   - 网格 4×4 定位 + grid 元数据（编号 → 原图坐标映射），LLM 报离散格子编号定位
   - scale 自动推 = 渐进离散聚焦（全图 → 中间态 → 原生局部是连续轴）
   - 定标（自校验探针）、resize 鲁棒、能力探测（块大小 ≤ min(内存, LLM封顶)）

3. **主 LLM（唯一智能）**：注入自己的上下文进入视觉子系统，图进 cu 上下文 → lm-service 路由 vision 模型 → 主 LLM 自己看图、自己决策（看哪/凑近/多局部组合）。图是临时介质，看完出结论，图不留在上下文。

## 核心结论

1. **目的 = 看清楚**（省 token 是副产品，不是独立策略）。
2. **理论根基**：厂商 vision LLM 把图 resize 到封顶再切 patch（文档 ~800×800，实测 443 token），大图细节进模型前丢失，厂商无解 → 自建「分块递进看清」。
3. **精确给**：必须自己把图缩到封顶内，不甩厂商 resize——省 token + 网格标注不被 resize 糊掉（定位才可靠）。resize 静默，必须主动告知元数据。
4. **方案2 胜出**：图进主 LLM 上下文自己看，不是「工具返回文字结论」（方案1 = 盲人听转述，图→文字降维，已否）。
5. **无「第二个主体」**：取景器 LLM / 内部 LLM 都被否——看图需要背景知识，背景只在主 LLM 那里，看的主体始终唯一。
6. **resize 鲁棒**：厂商无运行时接口，只有会漂移的文档声明（实测 443 vs 文档 384），usage 是真正锚；保守给图 + usage 校准 + 相对定位三手段。
7. **定标**：LLM 自报网格编号做自校验；全景最危险、定标一次够（局部分辨率更高必可读）；分步做避免分心。

## 待定点（新会话继续）

1. **region 表达**：网格编号 vs 归一化坐标入参（已倾向归一化坐标 + 网格辅助，未拍板）。
2. **「纸」的载体**：大图多局部组合的中转（§10/§11 已埋，复用认知树骨架 vs 独立视觉工作记忆）。
3. **大图「先看哪」**：自下而上显著检测（缩略看不清时的起点，后置）。
4. **f(W,H) 标定**：图像 token 是否纯尺寸函数、图内文字是否额外计 token（需实测，决定 usage 判断 resize 的可靠性）。

## 关键文件

- 细节 + 实测 + 三轮收敛：`entries/2026-09-03-cogos-vision-scheme.md`
- 本体锚点：`docs/vision-system-design.md`（§14 实施收敛 / 架构收敛 / 待拍板清单）
- lm-service 视觉接口已支持：content[] 含 image，vision LLM 归 basic 档（`design-lm-service-min.md`）
- agent 现状：工具层 read/write/edit/execute/search/fetch，cu 多轮续轮已通（`entries/2026-09-03-cogos-agent-cu-wired.md`）
