# system prompt 调研：Claude Code vs Kilo 对照（10-09）

## 目的与定位

理解"system prompt 究竟产生什么效果"，为 cogos **控制系统**（glossary：事件→工作空间的机制层，决定"此刻工作空间放什么"）里"给模型的那层指令怎么写"提供配方。属控制系统子话题，**调研素材/参考锚，非机制定论**。

## 样本与来源

| 样本 | 版本 | 来源 | 可靠性 |
|---|---|---|---|
| Claude Code 官方正文 | 2.1.295 | phistory.cc（claude-tap 抓 HTTP 请求体） | 较可靠＝实际 payload；但混动态注入层 |
| Kilo 主 agent | 7.8.8 | 本地二进制 `@kilocode/cli` bin/.kilo 明文提取 | 最干净（开源，无需抓包） |

证据 `checkpoint/26-10-09-system-prompt-study/`（claude-code 原文 157KB / kilo 主 agent 8.5KB / sources.md 含可复现方法）。

## 核心结论：控制配方三构件

两样本对照后，有效"控制"不靠风格（命令式 vs 陈述式都可），靠三个构件：

1. **few-shot 锚格式**：用 `<example>` 问答例子直接示范"答多长/什么语气"，比抽象规则（"keep it short"）可靠。Kilo 有、Claude Code 无——Kilo 最值得借鉴点。
2. **边界＋可判定例外**：禁止写成"默认 X，除非可判定例外"，而非"永远 X"或模糊平衡。Claude Code `confirm unless durably authorized` 可判定；Kilo Proactiveness 是"平衡"（模糊、不可判定）。
3. **注入防护成段**：定义"什么可信/不可信"（pasted_content / system-reminder / hook output / recalled memory）。Claude Code 有 4 处专门设计；Kilo 仅 1 条。

## 对照要点

- **命令式（Kilo）通病**＝靠重复强调稀释权重（"concise/<4行"≥3 次）；**陈述式（Claude Code）**一事说一次，靠"默认+例外"保证。
- 身份锚定两者都有；环境声明（Harness）Claude Code 有、Kilo 主 prompt 无（分散在别处）。
- 工具"策略层"（When to use / 别重复跑 / 别编造结果）＝行为指令藏于 schema，不亚于正文，两样本都有。

## 对控制系统的启示

我们跑在 Kilo 上，继承**命令式＋few-shot**（few-shot 是优点）。要补 Claude Code 两个强项：
- **边界＋例外结构**：替换"模糊平衡"，如"默认自决，除非 X/Y/Z 才问"。
- **注入防护成段**：agent 接大量工具输出/文件/MCP 数据，"reminder 非用户输入"一条不够。

## 被否 / 澄清

- 收口 ≠ 定论（记忆层是活层，就地改）。
- "Claude Code 无官方公开"属实；来源＝抓包快照，"基础层重构版"措辞已纠正为"抓包 payload＋动态注入层"（工具 schema/环境快照/CLAUDE.md 非官方正文、须剥离）。
- 未钉新术语进 glossary（"控制系统"已有；三构件是结论摘要，待落地写 prompt 时再议是否钉）。
