# Tool Design Draft — body / toolbox / memory (2026-10-18)

> 承 `2026-10-17-tool-design-draft.md`，本轮把 body 收成"少量基本动作"，全集沉 toolbox。
> 面向模型的工具全英文；交流语言由场景决定（内容层 vs 机制层）。

## 设计结论（承 10-17/18 讨论）

- **body ⊂ toolbox**：body 是 toolbox 的一个小子集 + 默认绑定（`body.chat.speak` ≡ `toolbox.communication.message.send(默认号码)`）。
- **body 不出现设备身份参数**：全走默认（默认号码 / 默认电脑）。toolbox 才有指定设备 / 管理操作。
- **意识层工具仍是 body + memory 两个**，不在 schema 平铺：body 与 toolbox 同构，各带自己的 help/call + catalog，
  模型通过 help 按需拿用法（当轮可见、用完释放），不长时间占上下文。
- 分组＝大类（对象优先），不是平铺；body/toolbox 精简的是每组内容，不动分组骨架。
- 能力总览（what）在 body schema description；用法（how）走 help + 最近用法缓存（条数上限，LRU）。

## body 列表（5 组，默认对象；desktop 遗留）

```
body.file.read / write / edit               — 默认电脑：读/写/改文本
body.vision.see / mark / coord              — 看图片文件(含子图 zoom)→标→算坐标，FIG 为中心
body.chat.speak / browse                    — 发消息(默认号码) / 浏览消息流
body.terminal.run / observe / send / interrupt — 默认会话：跑命令/看输出/发键/打断（run 可选 notify；多会话走 toolbox）
body.web.search / fetch / browse / cancel / close — 搜/抓网页，浏览(带状态)，取消/关闭作业
body.desktop.act                            — [遗留] 暂不实现：操作图形界面（底层 screen/1 已有，不暴露）
```

## 关键判定

- **catalog 命名与派生**：catalog 是"工具集的分类与用法"，不是全集本身——toolbox 的目录叫 `toolbox_catalog`，body 的目录叫 `body_catalog`。
  body_catalog 由 toolbox_catalog 投影派生（取子集 + 绑定默认对象 + 简化用法），落到同一 impl 层，避免同名工具两处定义。
- **see 独立成 vision 组**：see 的输出统一是 FIG（图像空间句柄），输入三源——屏幕/图片文件/FIG(zoom 子图)。
  子图 `see(FIG:a)→FIG:b` 的 ref 是 FIG，既不以文件也不以屏幕为对象，file/desktop 二分装不下。
  FIG 是统一句柄，来源只是出身不是身份；mark/coord 也以 FIG 为对象，故随 see 归 vision。
  这推翻了早期"视觉对象只有图片/屏幕两个、screen.look 与 vision.see 不并"的结论。
  （本轮屏幕来源随 desktop 遗留暂不暴露，vision 暂只看图片文件 + FIG zoom 子图。）
- **act 归 desktop，不归 vision**：act 的对象是 GUI/屏幕，不是图；图（FIG）只能看/标/算，不能 act。
  vision 是感知链（see→mark→coord），act 是操作，靠 FIG+ANNO 从 vision 传定位到 desktop 执行。
- **desktop 标遗留、暂不实现**：底层 screen/1（look/act）已实现，但本轮不暴露给 agent。
  无 desktop 时 vision 的屏幕来源（look）也不暴露，vision 只看图片文件。
- **listen_config 归 toolbox，不进 body**：listen 通道本身不是工具（被动机制，事件进循环），
  body 不出现 listen 是对的；listen_config 是配置工具，不常用，归全集。
- **screen → desktop 改名**：`desktop.act`（操作 GUI）比 `screen.act` 准，act 的对象是图形界面不是显示屏。
- **三动词判据**：read（静态内容，读完即完）/ browse（动态增长的长内容流，滚动跟）/ observe（运行中过程的状态+输出）。
  file 用 read；chat/web 用 browse；terminal 用 observe（读输出+exit_code/state 状态）。
- **异步作业＝发起/观察/取消闭环，同进同退**：web 的 search/fetch/browse/cancel/close mirror terminal 的 run/observe/interrupt。
  观察动作是"大结果不进上下文"的拉取机制（发起不回显，拉部分进度，done 事件只通知完成、不全量 push）。
- **web 作业＝临时对象，句柄 WEB:<id>**：search/fetch 发起即返回 WEB:<id>，流式产结果，写入隐藏结果文件（agent 只认句柄，不看到文件）。
  browse(WEB:<id>) 是唯一入口：返回 running/done 状态 + 内容，可 offset/limit 拉部分；结果流式，中间态有意义，拿到足够信息可提前 cancel。
  done 事件默认发（完成通知，与 browse 提前 cancel 并存）；cancel 停继续、留已有（仍可 browse）；close 显式销毁（不可再 browse）；
  无 browse 超 2h 自动回收（TTL）。cancel ≠ close：前者停止产生、保留结果，后者销毁。
- **time 不进 body**：now（机制层注入当前时间到上下文）/ wait（"停 = 等"，机制层睡/醒）/ remind（闹钟，低频归 toolbox）都不是对外工具。
  等待/唤醒是循环控制面，不是 agent 的 body 工具；body 精简到 5 组。
- **terminal 会话＝临时对象，需模型可见句柄；多会话暴露（A2）**：并发（多个前台交互式程序同时挂着）必要。
  机制层 manager 已支持多会话（dict + 每次 open 新 id），限制在 toolbox 的 `_DefaultSession` 单例；A2 把 session id
  从机器内部句柄翻成模型可见句柄（与 FIG/WEB:<id> 同类，加 `TERM:<id>` 前缀区分数字 id）。
  body 的 terminal 组走默认会话不变，多会话是 toolbox 层显式能力：`terminal.open` 返回句柄，
  run/observe/cancel 按 `TERM:<id>` 指定目标会话。
   与 `COMPUTER:<id>` 不冲突：设备（computer）稳定可寻址直寻址 host，会话（terminal 实例）临时对象才要句柄。
- **附件投影 = 内容分流的答案**：内容呈现三档——内联（小内容进文本，持久）／附件（当轮可见可浏览，跨轮消失）／指针（只给句柄，内容在外部）。
  主动拉取（read/see/help）→ 附件投影进当轮；被动推送（消息/job done/提醒）→ 短通知+指针，按需拉取（拉取即附件）。
  持久化只有句柄 + assistant 消息（模型自己的加工/总结）；附件跨轮消失后模型只看见自己的加工，不记原始刺激。
  记住大段原文→记索引（内容在哪，可反复重读），不抄原文：输出 token 贵、外部介质通常稳定、变了通常也不要紧；
  原文仅在"要紧且会变"时固化（时点值，如报价/约定）。
  消解"阈值待定"：附件跨轮消失，大小只影响当轮 token，不影响长期上下文；"记什么"交给 assistant 总结，可重读兜底。
  呼应机制层 D1 未闭合项（图引用→模型附件，assemble_tool_messages/provider 组装）。

## toolbox（全集，可整层延后）

- body 的每个功能都能在 toolbox 找到（全集 + 默认视角）。
- 低频全部沉 toolbox：phone.*（card/contact/file.cancel）、vision 的 adjust-mark/unmark/save、
  desktop.save、reminder、listen_config 等。
- 多会话（A2）：`terminal.open` / `terminal.list` / `terminal.close` 暴露会话句柄 `TERM:<id>`，
  并发挂多个前台交互式程序（ssh 远程 + 本地测试 + vim 同时）。
- 访问方式：toolbox 自己的 `help` 探索 + `call` 调用（内部走 `toolbox_catalog`），不在 schema 平铺。
- **先不做 toolbox 也足够**：body 5 组 + memory 已覆盖"感知-思考-行动"核心闭环（造工具 = terminal + file.write/edit）。
  MVP 只做 `body_catalog` + body.help/call + memory；`toolbox_catalog` 延后，body_catalog 先直接定义、将来重构为派生。

## memory

- **本质**：信息组织方式（把一段信息折成概念），不是"长期记忆"；长期记忆是 fold 的副产品。
- **四操作 = 两组正交**：
  - `fold / unfold` — 组织轴（形态）：折成概念 / 展开，服务于"想"（chunking，释放工作空间）。
  - `keep / forget` — 记忆轴（存续）：记 / 忘，服务于"存"。
  - 正交：fold+keep（概念入长期记忆）、fold+forget（临时折叠、不留）、unfold+keep（原文直记）、unfold+forget（不记）。
- **位置即强度**（keep/forget 的实现）：索引有序，keep 推到最前、forget 推到最后（简化的强化/淡忘）。
  浮现集取前 N（工作集窗口）；容量满尾部淘汰 = 遗忘。forget = 淡出、非删除（可翻回）。
- **不模拟人的局限**：模拟认知结构（该记什么、怎么组织），不模拟生物局限（反复强化、不能主动忘）。
  keep 一次即持久（agent 有持久化，不需反复回忆）；forget 是超越（人想忘忘不了）。
- **规模演化**：单维位置（记忆少）→ 经历挂钩（索引大：fold 挂到产生它的经历，相关经历优先加载相关记忆）
  → 主题簇（更深：按相关性聚簇，簇＝主题＝维度，从相关性涌现）。
- 与 body 并列，同为意识层唯一两个工具。

## 待定 / 未决

- toolbox 的完整组织（分组、命名、与机制层 catalog 的关系——已定名 toolbox_catalog / body_catalog，派生关系见关键判定）。
- 缓存参数（条数上限具体值）。
- **内容分流（已定附件投影，见关键判定）**：剩装配细节——phone 消息落 inbox、search/fetch done 事件带指针、
  大文件只回 id 不经 context（design-agent-tools.md 既有原则），统一成"拉取即附件投影"。
- phone 异步作业（file.send/receive + cancel）是否补 observe / 是否同模式，待 web 定后再对齐。
