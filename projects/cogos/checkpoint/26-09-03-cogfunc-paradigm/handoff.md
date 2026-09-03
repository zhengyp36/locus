# Handoff — cog-func 范式 + cog-actor 命名（会话交接）

> 日期：2026-09-03。新会话加载本文 + `entries/2026-09-03-cogos-cogfunc-paradigm.md`（完整结论）+ 本体 `docs/cogos-concept-system.md` §二/§九 即可恢复。当前处于「范式讨论收敛、命名拍板，下一步 = 以视觉为例实现四层」。

## 本会话产出（勿翻案）

从「视觉方案看似收敛但仍有疑虑」出发，换角度从三件套（LLM/cog-unit/cog-func）审视，发现只实现了 lm-service + cog-unit，缺 cog-func。讨论一路推到范式层，产出三层结论 + 命名。

## 核心结论

1. **cog-func 本质**：封装「理解」而非「过程」。原语层（预枚举封闭，决定可以怎么做）+ 功能层（组合开放，决定要做什么，种子+生长）。
2. **视觉 = cog-func 而非子系统**：img-tool 原语 + look_at 种子功能 + 生长功能（zoom_in/verify_readable）。「工具 vs 子系统」分叉已化解。
3. **命名（YZ 拍板）**：cog-actor（谁）/ cog-func（什么能力）/ cog-unit（什么动作）三层；agent = 对外的 cog-actor 实例，总结模块 = 内部 cog-actor。
4. **成长机制**：经验绑定 cog-func（程序性记忆，调用即生效），不进认知树；raw trace 攒批 → 量变总结 → 保底滚动替换；记录规则自长。

## 下一步任务（新会话）

**以视觉功能为例，做一次四层实现：lm-service → cog-unit → cog-func → cog-actor。**

- lm-service：✅ 已有（chat 支持 content[] 含 image，vision 归 basic 档）
- cog-unit / cog-runtime：✅ 已有（CogUnit + CogRuntime 状态机 + cu 多轮续轮）
- img-tool 原语：❌ 待实现（info / extract，短命子进程，句柄 = path，无状态无 close）
- cog-func（look_at）：❌ 待实现（契约 + 能力集 + 缓存句柄，复用主 cu 循环，不新建引擎）
- cog-actor：❌ 待设计（agent 如何作为对外的 cog-actor 组织上述 func）

## look_at 剖面（设计已收敛，供实现参考）

- 输入：意图（看什么/为什么看）+ 图索引(path) + 缓存句柄(可空)
- 输出：结论 + 更新后的缓存句柄
- 能力集：info(path) / extract(path, region)（注入主 LLM 上下文 = tool registry 注册两个工具）
- 状态（缓存句柄，机制层维护，LLM 不直接感知 how）：`{ path, full:{w,h}, seen:[{region,scale,conclusion}], calibration, budget }`
- 契约（prompt）：看清 = 缩 region 凑近（非放大）；看不清 → extract 更小 region；能力不足 → 转述「看不了」
- 内部：复用主 LLM cu 循环，不新建进程/服务/循环（img-tool 独立进程仅因性能，非架构独立子系统）

## 关键文件

- 完整结论 + 三层 + 成长机制 + 命名：`entries/2026-09-03-cogos-cogfunc-paradigm.md`
- 视觉实测 + img-tool 原语设计：`entries/2026-09-03-cogos-vision-scheme.md`
- 视觉本体：`docs/vision-system-design.md`（§4/§6/§14）
- 概念体系（已同步 cog-actor）：`docs/cogos-concept-system.md` §二/§九
- lm-service + cog-unit 现状：`docs/design-lm-service-min.md`、归档 `checkpoint/archive/26-08-30-cog-runtime-impl/design-cog-runtime-min.md`
- 代码：本体仓库 `/home/zhengyp/work/A/cogos/`（包 `cogos/`，含 lm-service、cog-runtime、agent 雏形、tests）

## 留白（无实验数据，先不定）

- 资源约束量：先跑满就停（共享大上限）
- 记录规则种子：尽量全记，后续由总结模块收缩
- 保底替换置信度：外部结果信号（任务完成/用户采纳/未重试），非 LLM 自评
- 总结触发阈值：机制层攒够 N 条触发
