# 工具与记忆组织（10-13，草稿）

> 状态：讨论中，未收口。记录工具讨论的重要结论，不含过程与命名细节。入口 `scratch/ENTRY.md`。

## 一、结构

**意识层工具视图（就两个）**
- `intent`：对外，表达意图；外部能力分几类（computer / communication / vision 等）藏在其背后，意识不可见。
- `memory`：对内，整理上下文、组织记忆。

**锚的表示**
- 索引区条目＝`name + description`。
- 正文引用＝`[[name]]`。

**记忆存储**
- 藏在 agent 不可见的目录，agent 只能经 `memory` 工具间接访问。
- 链/索引只在记忆内部，不外溢到外部文件。

## 二、机制

**memory 的两个原子操作**
- fold：把一段思考整理成一个概念（name + description）。
- unfold：把一个概念展开成详情。

**折叠＝意识命名 ＋ 机制收拢（两面）**
- 意识层折叠只贴名/抽象，不收起内容。
- 机制层看到 name，装载时把其背后内容不装、只留锚（收拢）。
- 一次折叠同时完成"压缩"与"索引构造"。

**展开 ↔ 折叠互逆，长成概念树**
- 注意力所在的展开，退到背景的折叠成 name，两者动态平衡。
- 多次折叠长出概念树（树生长式，非 append）。

## 三、记忆组织的归属

- `memory` 只提供 fold/unfold 两个操作；存、索引、蒸馏、收拢由**机制层**完成。
- 记忆＝意识层命名（fold）的副产品，机制层落地。

## 四、来源

- "链＋索引"双链借鉴自 Claude Code（`[[name]]`）。
- 原文出处：Phistory（https://phistory.cc/），仓库 https://github.com/WEIFENG2333/phistory；Memory 段具体见 `captures/claude-code/2.1.296/variants/default/prompt.md`（https://github.com/WEIFENG2333/phistory/blob/main/captures/claude-code/2.1.296/variants/default/prompt.md）。
- 关键差异：Claude Code 记忆是 agent 可读写的文件；我们藏进机制层、按需装载、不外溢。
