# 2026/10/30

关于自驱agent骨架的构想:
1. 有一条 CogStream, 这是自驱 agent 的意识流
2. 有一个元层，在意识流(CogStream)的介入点出现
3. 意识流的状态: 活跃(元层出现在TOOL/REASONING两个介入点)，闲置(元层出现的STOPPED介入点)

出生过程:
1. 触发出生的条件: CogStream.rounds = 0, CogStream.context 没有内容
2. 出生的触发点在 STOPPED 介入点发生
3. 通过 Relay 加载第一份上下文

上电恢复过程:
1. 读取上一次的下电前的状态
2. 基于上一次状态恢复恢复 CogStream, 如果中间间隔时间过长, 应该考虑上下文的衔接问题(这是元层的任务)

上电过程:
1. 上电前: started=False
2. 上电发生在: STOPPED 介入点
3. 根据情况选择走: 1) 出生过程; 2) 上电恢复过程

元层是什么？元层是自驱agent的代表。
- 一组状态信息
- 程序逻辑：给出准入条件，组织元层信息
- LLM语义逻辑：判断介入策略

如何维护agent的状态:
- 在每个介入点进入时发现状态变更并更新状态
  - 状态信息:
    - active + ts
    - idle + ts
    - 只在状态变更时更新ts
- 策略信息
  - 在每个策略结束时记录
  - 只在真正介入时才记录, 如果没有达到准入条件的不记录

介入点-STOPPED:
- 如果没有上电, 走上电逻辑
- 如果已经上电, 只在有事件时介入

介入点-TOOL:
- 有事件时才介入

介入点-REASONING:
- 必须介入
  - 有事件走事件介入
  - 张力是否清除, 若未清除, ...

流程:
- 上电流程
- 事件介入流程
- 张力源检测流程

张力源:
- 外部消息
- 内部任务

元层信息/agent信息
- 出生时间
- 系统启动时间
- 当前介入点类型
- 是否完成上电
- ...
- !信息区分: 可编辑; 不可编辑!

元层:
- 元层与程序层的交互
- 元层与意识层的交互

# 2026/10/29

介入的准入条件
- TOOL
  - 事件
  - tool_waiting_util
- REASONING
  - 事件
- STOPPED
  - 事件
  - tool_waiting_util and done

要达到的效果：
- 有事件时可以响应
- 工具调用结果清除(暂缓)
- waiting工具/意识打盹(暂缓)
- 上下文过长整理(暂缓)
- 意识层与元层的分离(暂缓)

过程:
- 出生，熟悉工具
- 基于事件的响应

body:
- file（3） — read / write / edit（逻辑行定位，命名对齐 kilo）
- vision（3） — see / mark / coord（FIG 为中心）
- chat（2） — speak / browse
- terminal（4） — run / observe / send / interrupt
- web（5） — search / fetch / browse / cancel / close
- time（3） — now / wait / remind
