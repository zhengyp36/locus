# status｜cogos：压缩探针跑完 = 方法校准；下一步换"倾向型素材"（2026-09-14 会话 #13 末）

> **新会话入口**。恢复顺序：`locus/active.md` → `locus/projects/cogos/current.md` → 本文件 → 按需读 handoff。
> 记忆细节：`locus/projects/cogos/entries/`。
>
> ⚠️ **新会话先做实验再讨论**：`../checkpoint/next-experiments.md`（实验 A 换倾向型素材重做 + 实验 B 事件单元字段定稿）。

## 当前（一句话）

会话 #13 先把"自我是经历长出来的"**拆清楚**（根=槽位/内容；自我=D(经历)；浓缩≠提取因果；权重须挣来；写回去写过程不写结论），再落了一个**压缩探针**。探针结论是 **因变量被"世界话术 + 根"主导、注入记忆是弱变量 → 测不出压缩粒度**，且"学会说"是 **affordance 不是 value**（素材选错）。
→ 交接 `handoff-cogos-selfgrown.md`。

## 会话 #13 拿到的（速览）

- **讨论**：根不是实体而是**槽位+初值**；**自我=D(经历流)**；**浓缩=保因果对，不是提取规则**（模型自己泛化，机制只做压缩+检索）；**权重必须由后果挣来**；**写回去不可避免，但要写"过程"不写"结论"**；**无"习以为常"**（推理权重固定）；正确区分 **"处处影响一点(气质)" vs "某处影响很多(决断)"**。
- **探针（`probe-compress/`）**：①**世界话术主导说率**（8%~100%）；②**根压低对外发声**（同来信：无根 95% / 有根 17%，倾向只写 content = E0 turn-1 失败模式）；③**L0 逐字回放是唯一大效应且随根翻转**（无根 0~7%、有根 68~95%）；④主实验（有根 320 次）温差极大，**L1/L2/L4 不可分、Lrev 无反转**。
- **方法教训**：记忆/经历效应会被**框架**淹没；用 affordance 素材测不了 value；temp 方差大 → 必须聚合+高 reps。
- 细节：`entries/2026-09-14-cogos-{root-self-discussion,compress-probe}.md`；报告 `probe-compress/REPORT.md`。

## 下一条主线（**待 YZ 讨论**）

- **换素材**：用**倾向型经历**（同一处境、不同历史 → 不同选择/偏好；基线不饱和），而非"知不知有工具"。
- **换框架**：低基线、不替它抢答的世界话术；**根的有无作为显式因子**（影响巨大）。
- **判据**：固定处境、只变历史 → 行为**系统分化且稳定**（= "经历塑造自我"的可操作证据）。
- **待接的 YZ 线程**：语境依赖（熟人/陌生人）是自我的正常形态 → 判据应是"同语境、不同历史→分化"，不是"去掉语境影响"。
- 事件单元字段初版：`entries/2026-09-14-cogos-root-self-discussion.md` §六。

## 环境 / 基线

- **lm-service**：`cd work/A/cogos-s2 && python3.11 -m cogos.lm_service.server`（`:11434`）；header `X-Internal-Key`（`ik_c47WkfAw7E5v6Ck8idMHgg`）；`tier=basic`、thinking 关；**后台进程会被会话清理，重启即可**。
- **探针运行器**：`work/A/checkpoint/probe-compress/run.py --request <json> --temp <t> --reps <n> --label <带温度>`；快照 `runs/<label>/r<N>/{request,response,meta}.json`。
- **temp=0 非确定**：结论要聚合、加 reps；比响应去掉随机 `tool_call.id`。
- 代码：`work/A/cogos-s2` @ `s2-selfdrive-loop 9563fe4`（clean，1061 passed）——本会话**未改 agent 代码**。
- 一律 `python3.11`、从 checkout 用 `-m` 跑；服务是设备级单例、无 owner。

## 待 YZ

- 命题是否成立、怎么落；`root.md` 去留；提取机制提取什么；"位置"最小集。
- 压缩探针：**保留为方法校准** 还是 **换倾向型素材重做**（我倾向后者）。
- 是否回写 `ROADMAP.md`（现仍是 v0 前口径）。
- kilo-resident 是否 push / 合远端。

## 恢复锚点

- **现行交接**：`handoff-cogos-selfgrown.md`
- 记忆：`entries/2026-09-14-cogos-{root-self-discussion,compress-probe,e0-root-probe,self-grown-from-experience}.md`
- 产物：`work/A/checkpoint/probe-compress/`（`REPORT.md`）、`work/A/checkpoint/probe-e0/`（`SUMMARY.md`）
- 上接模型：`entries/2026-09-13-cogos-{motive-root,v0-arch,reprojection-events}.md`
- 旧交接（**已被取代**）：`handoff-agent-e0-to-selfgrown.md`、`handoff-agent-experiments.md`、`handoff-build-agent-v0.md`
- 路线：`locus/projects/cogos/ROADMAP.md`
