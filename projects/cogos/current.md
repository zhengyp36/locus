# cogos

多 agent 运行时，飞书作通信总线。通信层已收口，底层三件（lm-service + cog-runtime）完成。主线 = **自驱回路** → **agent 本体 = 动机为根** → 会话 #11 收敛出 **agent 模型（重投影/回看/事件轴）** → 会话 #12 **E0 手动探针跑通**，转向"**自我是经历长出来的**" → 会话 #14 **自我收敛**（要"能自我长的 agent"）。

## 当前：收敛——要"能自我长的 agent"（09-14 会话 #14）

- **目标**：要能**自己判断、长跑不偏、该顶就顶**的 agent。**"好用"与"自驱/有自我"是一件事**（迎合≠好用）；真正不需要自我的是**闭合域写死规则的工具**，非同类。→ `entries/2026-09-14-cogos-self-convergence.md`
- **自我**：非"装进去的根/记忆/身份"，是环里**慢变量**——既被经历改写、又慢到能稳住的一贯读法（性格不是器官）。**只能长不能装**。"自"的门槛=目的/动机来源；=**偏移的自持**（大方向＋自己撞出并守住的小分支）。
- **自驱三条件**（缺一不可）：动因是自己的 ＋ 主动与环境（含人）发生关系 ＋ 后果回来改自己；**沉默/拒绝也算"动"**。
- **探针到不了**：离线单发＋后果手喂 → 无环长不出自我；只余零件＋两条反面约束（写回不写结论）。陪聊算数，"单发手喂"才不算。
- **防偏/防定型**：偏=无慢变量＋只堆不整 → 靠"整合"（=ROADMAP 的上下文可重组）；只跟一个人相处会**定型**（=对方替它决定）→ 要多人真后果、有变化也有重复。
- **治理**：判断归它、决定权归规则；**对齐=定规则不削判断**；要定"哪些事归谁 / 谁定分配（不能它定）/ 分歧留账"。
- **要做**：**建能跑的环**——真实互动里自己动/读/写回，看偏移是否出现并自持（v0 设计早有，一直没做）。
- **09-14 倾向探针（#14）**：机制通（负向经历把 agree 从 88~95% 翻到 2~5%），但只是"照结局记账"、无解读；对"自我长出来"不构成证据 → `entries/2026-09-14-cogos-tendency-probe.md`、`work/A/checkpoint/probe-tendency/`。
- **待 YZ**：最终让它在哪活/成为什么；单 vs 多环境、从哪一步动手；判据定案。
- **#14 后半（未入 entries）**：动因讨论收敛到**饿/困/疼**（机制管机制、agent 只感知状态；饿→求助非谄媚）→ `handoff-cogos-drives.md`
- **#15（未入 entries）**：**证伪"把动因做成机制"**（机制不能想要；饿底物不对）→ 重心移到**经历**；否掉"中性机制"版，改为 **YZ 的修正版：中性的调用接口 + 非中性的模型与经历（=沉淀机制）**；诊断"无法整合"困境（垂直深化 vs 水平接线）；落到 **YZ 计划：先搭能接触外部世界的架子**。→ 交接 `work/A/checkpoint/handoff-cogos-scaffold.md`
- **#16（未入 entries）**：把 §7"架子"推进一层——**感知机制**（真实判据 / 处境快照 / perceive 拉 / event 推 / 时间与位置作坐标）；**身份锚 = signature**（host 也可变、只有 signature 不变；经历挂 signature，不感知目录）；**运行组织 = 事件驱动**（唯一主体；`loop.py` 是离线实验台，非架构，其验收第二判官/守卫/后果绑定待折回主体）；**tick = 内部事件**（生念时机，无世界内容）；**生念 = 选择器机制**（张力概率选事项 + 从事项之外选角度；张力=未闭合的环）。更正 #15 §7.6"两个它"为误读。→ 交接 `work/A/checkpoint/handoff-cogos-perception-tick.md`
- **#17（未入 entries）**：把"架子"推成**可施工的结构**——**运行框架**（状态/压力：`P整理`/`P节律`/`T` + 睡醒判决 + 生念 T1/T2）→ **流与时间线**（事件切割 / 区间树 / 三种拓扑 / 多分辨率压缩 / 权重决定谁不许压）→ **总纲**（三条不变量 + 锚/流/经历）→ 一处**悬置**（"一条新流的方向从哪来"：未闭合只提供动力）→ **最小 agent 草稿**（经历轴是骨架；取回替代常驻）→ **环落到 cu**（环＝机制三段夹一个 cu；一个环＝多个 cu；打断即重组＝存/取；`finish`＝预测器）。**更正**：①不变名"时间线可寻址"（含未来规划）②后果降为**权重**来源（什么都记、后果决定活多久）③单一归属＝**共切面**、"我"不需常驻只需来源唯一；**答了 #16 §6 的口子**（判定归有目标的流；取回＝相似度＋张力通道；生念＝T1/T2＋概率＋内容闸）。→ 交接 `work/A/checkpoint/handoff-cogos-loop.md`
- **#18**：从"最小 agent 长什么样"推起，**否掉"最小"**（循环依赖、无可删的核）→ 定**经历的表示**（段＝一弧一条；顺序不记、引用实时记；**层级后压**、不进基底；段带**路标**与**预测**；活跃度＝近因＋强度＋权重）→ **切点＝误差**（非"有没有事件"；`finish`＝切点传感器＋卡住/茫然判别器）→ **取回必须内容寻址**（链只服务**证伪**、不服务想起）→ **整理＝抽样重演**（反向重演＝后果绑定）→ 借认知科学校准（事件分割／回放／可得可及／fuzzy-trace）。**收口**：环已在转（现有 agent＝纯响应式闭环）→ 不是"搭"是**换零件**（一次一个、其余冻结），第一刀候选＝**后果**（现状只写不读）。**产物**：`design-cogos-agent-current.md`（当前总纲／唯一权威口径）＋ `design-cogos-open-items.md`（未定表；**权重构造式**为关键路径）＋ 六份旧 design 头部标注（#17 口径部分被修正，**冲突以总纲为准**）。→ `entries/2026-09-17-cogos-experience-representation.md`

### 前情（会话 #12~13：E0 → 自我是经历长出来 → 压缩探针=方法校准）

- **E0 手动探针已跑完整回合**（无代码；YZ=世界、AI=机制、lm-service 当通道）。装配模型定了：**想=`content`（私有、进记忆）/ 说=`send_message`（对外动作）/ 沉默是默认**；来源靠结构+标签；transport 不必真走飞书。→ `entries/2026-09-14-cogos-e0-root-probe.md`；产物 `work/A/checkpoint/probe-e0/`
- **行为事实**：①"说"要显式动作、**靠后果学会而非教学**；②"想"＝开口前的私下盘算，稀有、**不依赖根也不依赖教学**；③静默合法（是默认态）；④根只在"自我被触及"时显形，平时**只是着色**；⑤**C2 软冲突下根驱动了行为**（真根拒 / 无根从 / 异根从），C1 强冲突的拒绝与根无关（来自先验）；⑥它会**反推我们的意图**（=辨来源/护根）。
- **方法教训**：**temp=0 不是确定性的**（单条不可比，须聚合特征+加 reps）；**测冲突的指令不能引用根的原话**（会把根词递给所有臂）。
- **转向（YZ 提出，待讨论）**：**根可能不是必须的，自我是经历塑造的**；我们给的根 = 想让 agent 长成的样子。拆法：**机制给"位置"、经历长"根"**（"我"是位置不是内容）。→ `entries/2026-09-14-cogos-self-grown-from-experience.md`
- **下一步（09-14 会话 #13 已跑一轮压缩探针，结果为"方法校准"）**：因变量（说不说）被**世界话术 + 根在场**主导、注入记忆是弱变量 → 测不出压缩粒度；且"学会说"是 **affordance 不是 value**（素材选错）。→ `entries/2026-09-14-cogos-compress-probe.md`、报告 `work/A/checkpoint/probe-compress/REPORT.md`
- ~~新会话待讨论：换倾向型素材…~~ **已做（会话 #14 倾向探针），见上行**
- **09-13 模型链仍有效**（根=动机、v0 婴儿期、重投影/事件轴）：`entries/2026-09-13-cogos-{motive-root,v0-arch,reprojection-events}.md`
- 待 YZ：新会话讨论——提取机制提取什么 / "位置"那层最小集 / 实验设计；kilo-resident 是否 push。

## 自驱回路（09-11 起主线）

- 转向：造能自驱推进的 agent（L1→L4 阶梯），入口 = dogfood；行业评估结论 = 视觉已商品化，力气放回路。→ `entries/2026-09-11-cogos-selfdrive-pivot.md`
- S2 首跑 → S3 触发（壳自动选条）→ S4 判据源外移（agent 写红测试）+ 分层验收（真机省 ~33%，`9563fe4`）。→ `entries/2026-09-11-cogos-s3-trigger.md`、`cogos-criterion-dogfood.md`、`cogos-layered-acceptance.md`、`cogos-selfdrive-p0.md`
- 路线修正（09-12）：**自驱地基 = 上下文组织，不是调度机制**。→ `entries/2026-09-12-cogos-general-agent.md`
- 上下文组织推演链：复现实验 → 蒸馏再校正（投影≠替换、回取≠立即取、换帧要质变）→ 换帧边界（唯一触发=目的变了）→ **身份即锚/脊** → 动机为根。→ `entries/2026-09-12-cogos-{recurrence-arm-analysis,distill-retrieval-frame-swap,frame-swap-trigger,identity-anchor-frame}.md`
- 活文档：`work/A/checkpoint/ctx-*.md`、`handoff-ctx-*.md`、`ctx-swap-probe-report.md`。

## 已收尾

- **通信层（08-07~24）**：用 `cogos/phone`，见本体 `docs/phone-usage.md`；代码现状地图 `entries/project-map.md`。
- **智能系统设计（08-24~27）**：本体 `docs/cogos-concept-system.md`、`docs/cogos-plan.md`、`docs/agent-study-hooks.md`。
- **底层三件（08-29~30）**：lm-service（tier basic/advanced、thinking 默认关、契约 `LmClient.chat`）+ cog-runtime 完成；归档 `checkpoint/archive/26-08-30-*`。
- **认知图设计探索**：封存为预研（09-01），聊天 MVP 暂停。归档 `checkpoint/archive/26-09-01-cog-graph-sealed/`。
- **agent 认知架构 + 实施（09-01~03）**：覆盖式回合 / 状态对象；read 行模式；terminal + timer；agent 接 cu 多轮续轮。→ `entries/2026-09-02-cogos-{agent-cog-arch,agent-codebase}.md`、`2026-09-03-cogos-agent-cu-wired.md`
- **cog-func 范式（09-03）**：cog-actor / cog-func / cog-unit 三层；img-tool 已实现。→ `entries/2026-09-03-cogos-cogfunc-paradigm.md`
- **视觉 + image_ctx（09-03~08）**：镜筒 / 视野三层、FIG/域、坐标三套化；设计定稿、P1~P4 落码。→ `entries/2026-09-08-cogos-{vision-image-fields,image-ctx-boundary}.md`；本体 `docs/design-vision-image-fields.md`
- 完整阶段脉络 `CHANGELOG.md`；认知地图 `entries/project-map.md`。

## 锚点

- **评审中（新会话入口）**: 陪 YZ 从头过整体理论，顺序＝骨架→矛盾→未定项，**只讲不推进** → `work/A/checkpoint/handoff-cogos-theory-review.md`（从骨架第一拍起）
- **方向讨论入口（09-22 #26）**：screenlab 告一段落，转「**讨论方向**」（**方向不预设**，讨论得出）。**入口（唯一）** `work/A/checkpoint/handoff-screen-26.md` → 素材 `entries/2026-09-22-cogos-screen-direction-material.md`
- **讨论（09-23 #26 内）**：从"ToDesk 解锁模型不碰密码"展开——**can≠know**、**agent=意图层非权限层**、敏感是**关系属性**靠**围堵**不靠识别、**致命三元组**；对 cogos = ledger 已有围堵，缺 **HITL+egress 限域**，敏感分类只当分诊不当闸门 → `entries/2026-09-23-cogos-sensitive-info-boundary.md`
- 当前口径: 本体 `../cogos/docs/design-selfdrive-agent.md`（**当前总纲／唯一权威口径**，09-17 由 #18 总纲整体化）。过程与依据已归入 `checkpoint/26-09-17-agent-theory/`（原 `work/A/checkpoint` 已并入并清理，含 #15~#18 handoff、六份旧 design、probe/ctx 旁证）；索引 `checkpoint/ARCHIVE-INDEX.md`，迁移映射 `MIGRATION-MAP.md`／`MIGRATION-COVERAGE.md`。六份旧 design 头部标注仍有效，**冲突以整体文档为准**
- agent 工具实现（A 层分批，09-18 起）：依据/产物在 `work/A/checkpoint/`（plan／spec-tools-a v1.4／spec-tools-web／spec-phone-files／checkpoint-1·2／handoff-tools-01~09／handoff-phone-files-01·02）；**批次 1／2（本机 term）／2.5（远端 term+凭证注入）／3（FsChannel+TransferEngine）／4a（ToolDef 单一来源）已提交；4b 装配缓**（待第二消费者）；web 异步化已落地（`impl/web.py`）。**phone 文件收发已实现并真机全过**（① 真人→bot 无 @ 事件直达+按 key 下载；② bot→真人手机可预览；③ bot↔bot；④ mixed group 合成附件；`5c5e1b4`+`45ab216`，已 push）。临时测试账号 `tangyu`/`cog-ty-0005`（本地+远端 localhost）→ `entries/2026-09-19-cogos-agent-tools-impl.md`
- 图形面（看屏/操作，09-20）：see/act 在**四台机器**跑通（本机 `:0`、212 `Xvfb:99`、Windows Surface `192.168.1.112` 标准账户交互会话、Android `MAR-TL00`/EMUI10 走 adb）；设计级约束（`snapshot_id`、WM 前置、服务必须在会话内、Pillow+xdotool、Windows DPI 感知、Android 坐标同空间）；设计稿 `work/A/checkpoint/spec-screen-1.md`（**§0.1 术语与形态**）；原型 `work/A/checkpoint/screen-lab/`；实测 `checkpoint-3.md`/`checkpoint-4.md`/`checkpoint-5.md`；**术语定案**=`computer` 工具三能力面 term/fs/**graphics**，agent 侧=图形客户端、目标侧=**图形服务**（目标侧不叫 agent；sshd/sftp 保留、只自建图形服务；统一在 agent 侧）；交接 `handoff-screen-04.md`（**下一步=Phase 2 形态讨论**：可安装/自启/远程/**鉴权**、四平台顺序、Android 设备内 app）。**多裁决未定**（图 lineage／自建 vs E2B／客户端厚度／**代码放哪**／Wayland／a11y tree）→ `entries/2026-09-20-cogos-screen-face.md`
  - **P1 已落码 + 双机验收**（`screenlab/` 进 cogos 仓库根；分支 `feat/screenlab-p1`，**未合并 master、未建 PR**；协议 `screen/1` 冻结；验收 1–7 过、pytest 1198）→ `handoff-screen-06.md`
  - **多账户模型定**：给 agent 一个账户 = 给它一个**独立会话/桌面**（不是抢人的）；`owned`（agent 自占）vs `granted`（人的桌面让出）
  - **发现并修复「无头外壳缺 X 鉴权」**：`Xvfb :99` 无 `-auth` → 同机任意账户可抓屏/注入；修 3 文件（**未提交**），双机验证；212 **真 reboot** 后无人工自启 + 闭环 OK
  - **下一步 = P4 Windows 外壳讨论**（登录前/安全桌面：A 自动登录 / B UIAccess / C 凭据提供程序 / RDP，建议不做）→ `handoff-screen-08.md`
  - **大图慢的根因 = VBox 7.2.x 桥接收包 bug**（非 screenlab/协议：下载 ~64KB/s 且卡死、`rx_errors` 随传输涨、NAT 口正常）；**改用 Tailscale 绕行**——实测同走 enp0s8 仍 4MB/s（原始 TCP 同条件 16.4s/1MB vs tailnet 0.74s），故无需宿主关 RSC → `entries/2026-09-20-cogos-screen-net-vbox-bridge.md`
   - **目标重置（YZ，09-20 #11）**：先做 **Linux、非无头、真人使用场景**；**agent = 一个普通用户**（同账户/同 PAM 登录/同图形栈/真 GPU/同输入路径），删掉一切"agent 专用"机制（Xvfb、专用通道）；**a11y（AT-SPI）优先、像素兜底**；"能被 YZ 看见"用 xpra/Xvnc over ssh、默认关+readonly。AT-SPI 本来就是一条 systemd **user unit**（`at-spi-dbus-bus.service`），故 a11y 侧几乎不用新造。**核心架构已被 spike 验证**：非 seat 用户 + headless mutter + Xwayland + AT-SPI（GI `Atspi`）读到元素树、按 a11y bounds 用 xdotool 点击成功；`card0` 开不了但不需要（`renderD128` 0666）。待裁决：登录模型（linger vs PAM）/ 看屏方案 / granted 档 → **`work/A/checkpoint/handoff-screen-11.md`（新会话入口）**
   - **#9 轮（09-22，接手 #21）**：工具层真机闭环打通——`ScreenChannel` **从不发 `open`**（agent 侧每次 capture/act 都 `no_channel`，是硬 bug，已修 `1dfbdb5`）；**口径修正（推翻 #21 的"树为主路径"）：图 = 主干**（感知 + 落点，唯一能加固的腿）、**a11y 树 = 可选语义索引**（按名精确找/批量列），**不做增量 a11y**（真工程、三平台、下注条件未满足）；**机制不代判"看什么"**（`KEEP_ROLES`/骨架/大纲都属代判，待回退）。第九轮代码已提交 `800e5a9`+`1dfbdb5`（全仓 1248 passed；`tests/screenlab/e2e/tool_loop_e2e.py` 全过）→ 交接 **`work/A/checkpoint/handoff-screen-22.md`（新会话入口）**

- 并行支线: `../kilo-resident/checkpoint/26-09-17-phone-number-contacts/`（kilo-resident，别混 v0）
- 工程管理: `README.md`（remote/本体/关键文件）、`CHANGELOG.md`、`ISSUES.md`、`ROADMAP.md`、`tasks/`
- 旧活文档归档: `checkpoint/26-09-11-live-checkpoint/`
