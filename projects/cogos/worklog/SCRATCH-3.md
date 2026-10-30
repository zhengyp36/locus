# 2026/10/30

## 自驱agent组成

**大脑**
- 状态
- 决策
- 意识流
- 后台流

**通道**
- 事件: 输入
- 工具: 输入/输出

**持久化**

## State(状态)信息梳理

是否上电 powered_on : powered_on_ts != 0
启动时间 : power_on_ts, powered_on_ts
出生时间 birth_ts : 首次的 power_on_ts

原始意识流
意识流蒸馏: 纵向/横向

记忆:
- 纵向
- 横向

## 持久化

- 配置信息 agent.json
  - 总入口
  - 身份识别信息 (电子签名: 公钥/私钥对)

- 个人信息 profile.json
  - 姓名
  - 出生时间 (首次启动时间)
  - 身份识别信息 (电子签名: 公钥)

- 程序信息 runtime.json
  - 启动时间 power_on_ts, powered_on_ts
  - 最新状态 last_state, last_state_ts (活跃时每介入点更新, 状态变更时更新, 闲置时控制更新频率)
  - 退出时间 power_off_ts, powered_off_ts

- 记忆
  - 意识流
    - 原始意识流
    - 意识流蒸馏: 纵向
  - 记忆蒸馏
    - I型记忆-主题内容/张力源
    - II型记忆-折叠/展开
    - II型附着于I型

- 事件-目录
- 电话-目录

## 目录结构示例

tangyu/
├── agent.json
├── profile.json
├── runtime.json
├── last_runtime.json
├── stream/                    # 意识流 [新增 = CogStream store_dir]
│   ├── <YYYYMMDD>.TZ<offset>.V<version>.jsonl
│   └── meta.json              #   {date, next_version}
├── memory/                    # II型记忆 [现有，不动]
│   ├── INDEX.md
│   └── <slug>.md
├── events/
├── phone/
├── work/
├── machine/<name>/
└── secrets/

## 遗留

- 张力源与目标相关, 目标的张力有利于聚集, 不利于发散
- 好奇有利于发散
- 张力与好奇之间如何平衡
