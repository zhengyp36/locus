# 轻机制、信任 LLM（案例）

> 本文先给出 Claude Code 记忆机制的原样描述，附简短点评。是参考，不是要遵守的规则。
> 来源：Phistory 抓包的 Claude Code 2.1.296 system prompt（https://phistory.cc/ ，仓库 https://github.com/WEIFENG2333/phistory）。

## 一、Claude Code 的记忆机制

**存储形态**：纯文件系统。目录 `~/.claude/projects/<project>/memory/`。一个记忆一个文件，一个文件只记一个事实。

**每个文件**（frontmatter + 正文）：

```
---
name: <短 kebab-case slug>
description: <一行摘要，召回时用来判断相关性>
metadata:
  type: user | feedback | project | reference
---

<事实正文>
```

正文里用 `[[other-name]]` 链接相关记忆。

**四类内容**（`type` 字段）：

- `user`：用户是谁（角色、专长、偏好）
- `feedback`：用户给的「该怎么工作」的指导（纠正＋确认过的方法），须含 **Why** 和 **How to apply** 两行
- `project`：进行中的工作/目标/约束（代码或 git 历史推不出的）；相对日期转成绝对日期
- `reference`：外部资源指针（URL、dashboard、ticket）

**索引**：单独的 `MEMORY.md`，每行一条指针 `- [Title](file.md) — hook`，每次会话整份加载进上下文。

**双链**：正文里用 `[[name]]`（name＝另一条记忆的 slug）把相关记忆连起来；**允许指向还不存在的 name，表示「以后值得写」，不是错误**（原文：「Link liberally」）。

**写入规则**：

- 写前先查重：已有文件覆盖的就更新，不建重复；发现记错的删掉。
- 不记 repo 已记录的（代码结构、过往修复、git 历史、CLAUDE.md），也不记只对本次对话重要的；被要求记这类时，反问「其中什么是不显然的」，只记那部分。

**召回方式**：靠 frontmatter 的 `description` 判断相关性；召回到的记忆通过 `<system-reminder>` 块注入，当作背景上下文（不是用户指令，反映「写下时」的事实）。

## 二、点评

这套机制几乎没有「精确规则」：`name` 和文件名怎么对应没写死，`hook` 字段没有定义，指向不存在的 `[[name]]` 不算错误。它仍能用，而且 LLM 用得顺——靠的是语义理解，不是规则。

可参考的只有一点：**机制可以留白**。留白能成立，前提是「最自然的填法恰好就是设计者要的填法」——LLM 的语义理解正好用来填这些空白。

我们自己的一个反例（出生走查里）：对象指称（「张三」「那个陌生人」「刚开的电脑」）本来一句话就是 fold 的应用、机制零新增，却一度被做成「兜底命名、触发条件、代词/锚切换规则」的设计——替 LLM 操心它本来就会的事。
