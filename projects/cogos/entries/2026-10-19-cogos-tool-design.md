# 工具设计线 · body / toolbox / memory（2026-10-19）

> **状态：进行中（候选结论、未落码）**。承 scratch 草稿 10-17~19（备份 `7ad3127`），本轮收口为"已定 vs 待定"两栏，步骤 3 继续定案。
> 术语权威锚：glossary `body` / `toolbox` / `body_catalog`/`toolbox_catalog` / `keep`/`forget` / `附件投影` / `句柄`。
> 面向模型的工具全英文；交流语言由场景决定（内容层 vs 机制层）。

## §0 定位

- 意识层工具＝**body（对外）＋ memory（对内）**。10-15 的"intent（对外）"**改名为 body**；「意图＝无声动作指令」概念仍活（glossary「意图」），只是不再作为工具名。
- 对外工具 3 条思想：**简单 / 全面 / 手艺**。自驱 agent 真正价值＝思维能力＋造工具能力，对外工具只要不制约"造工具"即可；**图形界面操作是唯一需要手艺处**（GUI 为人类设计，LLM 对图形的理解与响应跟不上，故显笨拙）。
- 工具 3 态 IO：**被动感知**（源+内容，内容可空）/ **主动获取**（源+内容）/ **主动行动**（对象+内容）。行动闭环＝观察影响→主动获取→形成认知。

## §body（5 组，默认对象）

- **body ⊂ toolbox**：body 是 toolbox 的子集＋默认绑定（`body.chat.speak` ≡ `toolbox.communication.message.send(默认号码)`）。
- **不带设备身份参数**：全走默认（默认号码/默认电脑）；toolbox 才有指定设备/管理操作。
- 分组＝大类（对象优先），非平铺；精简的是每组内容，不动分组骨架。
- 能力总览（what）在 body schema description；用法（how）走 help＋最近用法缓存（条数上限，LRU）。
- 5 组：`file`（read/write/edit，命名对齐 kilo）· `vision`（see/mark/coord，FIG 为中心）· `chat`（speak/browse）· `terminal`（run/observe/send/interrupt）· `web`（search/fetch/browse/cancel/close）。`desktop.act` 遗留、暂不实现（底层 screen/1 已有，本轮不暴露）。

### body 参数（10-19 定稿）

```
body.chat.speak(to, text)
body.chat.browse(chat, before?, limit?)
body.file.read(path, offset?, limit?)
body.file.write(path, content)
body.file.edit(path, old_string, new_string)
body.terminal.run(command)
body.terminal.observe(offset?, limit?)
body.terminal.send(data)
body.terminal.interrupt()
body.web.search(query)
body.web.fetch(url)
body.web.browse(ref, offset?, limit?)
body.web.cancel(ref)
body.web.close(ref)
body.vision.see(ref, center?, size?, remark?)
body.vision.mark(ref, kind, center, size?, remark?)
body.vision.coord(ref, anno)
```

- chat：`speak(to, text)`；`browse(chat, before?, limit?)`，`before` 缺省从最新往前读。
- file：命名/参数对齐 kilo（path/old_string/new_string）；`replace_all` 去掉（impl `fs.edit` 无此参数，暴露即陷阱）。
- terminal：`run(command)` 命令＝完整一行 shell 字符串，异步发起即返回；`observe` 读物理行（pyte 渲染），缺省看末尾；`send` 原样发字节不隐式回车；`interrupt` 发 `\x03`。
- web：`search(query)`/`fetch(url)` 提交即返回 `WEB:<id>`；`browse(ref, offset?, limit?)` 唯一入口，返回 running/done＋内容（行号分页，缺省从头）；`cancel` 取消在途、`close` 释放完成（TTL 2h 兜底）。
- vision：`see(ref, center?, size?, remark?)` PATH 开图 / FIG 调视野；`mark` cross/rect 标注返回 ANNO；`coord` 读回原图坐标（纯读无 remark）；坐标归一化，`see`/`mark` 的 center 相对当前视野，`coord` 换算回原图。

### 定位单位分道

| 对象 | 单位 | 定位 | 意图数量 |
|---|---|---|---|
| file | 逻辑行 | `offset`（行号，缺省从头） | `limit` |
| terminal | 物理行 | `offset`（行号，缺省看末尾） | `limit` |
| chat | 条 | `before`（时间戳，缺省最新） | `limit` |
| web | 逻辑行 | `offset`（行号，缺省从头） | `limit` |
| vision | 图（FIG） | 坐标（center/size 开窗） | — |

### 截断

机制总量上限兜底，末尾截断标 `truncated`（单位：file/web 逻辑行 / terminal 物理行 / chat 条）。

## §toolbox（全集，可整层延后）

- body 的每个功能都能在 toolbox 找到（全集＋默认视角）；低频全沉 toolbox（phone.*、vision 的 adjust-mark/unmark/save、desktop.save、reminder、listen_config 等）。
- 多会话（A2）：`terminal.open`/`list`/`close` 暴露会话句柄 `TERM:<id>`（并发挂多个前台交互式程序）。
- 访问＝自己的 help 探索＋call 调用（内部走 toolbox_catalog），不在 schema 平铺。
- **MVP 可整层延后**：body 5 组＋memory 已覆盖"感知-思考-行动"核心闭环（造工具＝terminal＋file.write/edit）。先做 `body_catalog`＋body.help/call＋memory；`toolbox_catalog` 延后，body_catalog 先直接定义、将来重构为派生。

## §memory（四操作正交）

- **本质＝信息组织方式**（把一段信息折成概念），不是"长期记忆"——长期记忆是 fold 的副产品。
- **四操作＝两组正交**：
  - `fold / unfold` — 组织轴（形态）：折成概念 / 展开，服务于"想"（chunking，释放工作空间）。
  - `keep / forget` — 记忆轴（存续）：记 / 忘，服务于"存"。
  - 正交：fold+keep（概念入长期）、fold+forget（临时折叠不留）、unfold+keep（原文直记）、unfold+forget（不记）。
- **位置即强度**：索引有序，keep 推到最前、forget 推到最后；浮现集取前 N、容量满尾部淘汰＝遗忘；forget＝淡出非删除（可翻回）。
- **不模拟生物局限**：模拟认知结构（该记什么、怎么组织），不模拟生物局限（反复强化、不能主动忘）；keep 一次即持久（agent 有持久化，不需反复回忆），forget 是超越。
- **规模演化**：单维位置（记忆少）→ 经历挂钩（索引大，fold 挂到产生它的经历，相关经历优先加载相关记忆）→ 主题簇（按相关性聚簇，簇＝主题＝维度，从相关性涌现）。

## §关键判定（why）

- **see 独立成 vision 组**：see 输出统一是 FIG（图像空间句柄），输入三源＝屏幕/图片文件/FIG(zoom 子图)。子图 `see(FIG:a)→FIG:b` 的 ref 是 FIG，不以文件也不以屏幕为对象，file/desktop 二分装不下。FIG 是统一句柄，来源只是出身不是身份；mark/coord 也以 FIG 为对象，故随 see 归 vision。**推翻早期"视觉对象只有图片/屏幕两个、screen.look 与 vision.see 不并"**。
- **act 归 desktop 不归 vision**：act 的对象是 GUI/屏幕，不是图；图（FIG）只能看/标/算，不能 act。vision 是感知链（see→mark→coord），act 是操作，靠 FIG+ANNO 从 vision 传定位到 desktop 执行。
- **三动词判据**：read（静态内容，读完即完）/ browse（动态增长的长内容流，滚动跟）/ observe（运行中过程的状态+输出）。file 用 read；chat/web 用 browse；terminal 用 observe。
- **异步作业＝发起/观察/取消闭环，同进同退**：web 的 search/fetch/browse/cancel/close mirror terminal 的 run/observe/interrupt。观察＝"大结果不进上下文"的拉取机制（发起不回显，拉部分进度，done 只通知完成不全量 push）。cancel ≠ close（前者停止产生、保留结果，后者销毁）。
- **附件投影＝内容分流的答案**：内联（小内容持久）/ 附件（当轮可见，跨轮消失）/ 指针（只给句柄）。主动拉取→附件投影进当轮；被动推送→短通知+指针，按需拉取。持久化只有句柄＋assistant 自己的加工；记大段原文→记索引不抄原文。消解"阈值待定"——附件跨轮消失，大小只影响当轮 token。
- **catalog 改名与派生**：catalog 是工具集的分类与用法、非全集本身；body_catalog 由 toolbox_catalog 投影派生，落到同一 impl 层避免同名工具两处定义。
- **time/now/wait/remind 不进 body**：now（机制注入当前时间）、wait（停=等，机制层睡/醒）、remind（闹钟）都是循环控制面或低频工具，不是 body 工具。

## §已定 vs 待定

**已定（候选结论）**：body⊂toolbox；body 5 组不带设备身份；四操作正交（fold/unfold × keep/forget）；位置即强度；附件投影三档；句柄 FIG/WEB/TERM；工具 3 态 IO；对外工具 3 条思想（简单/全面/手艺）；catalog 改名派生；三动词判据（read/browse/observe）；异步作业闭环；see 归 vision、act 归 desktop；desktop 遗留不实现。

**待定（悬置，步骤 3 裁）**：
- `body` 是否含 `time`：10-18 已裁"time 不进 body"（now 机制注入 / wait 循环控制面 / remind 低频归 toolbox）；YZ 10-19 构想里 body＝chat/file/terminal/vision/web/**time**，冲突待裁。
- `terminal.run` 的 `notify`：cogos 用 OSC token 编进命令实现完成通知，body 是否保留。
- `web.fetch` 的 `format`：倾向去掉（默认 markdown，html 原始结构走 toolbox）。
- toolbox 完整组织（分组/命名/与机制层 catalog 关系）。
- 缓存参数（条数上限具体值）。
- 内容分流装配细节（phone 消息落 inbox、search/fetch done 事件带指针、大文件只回 id）——统一成"拉取即附件投影"。
- phone 异步作业（file.send/receive + cancel）是否补 observe、是否同 web 模式。
- 拉取类（read/observe/browse）的 `limit` 参数去留（10-18 曾倾向一并去掉，只留 offset 游标）。

## §被否

- 视觉对象只有图片/屏幕两个（FIG 子图 ref 装不下 → 归 vision）。
- act 归 vision（图不能 act → 归 desktop）。
- 记忆＝"长期记忆"本体（本质是信息组织方式，长期记忆是 fold 副产品）。
- 模拟生物局限（反复强化、不能主动忘 → 不模拟，keep 一次即持久、forget 是超越）。
- 内容分流靠"阈值待定"（→ 附件投影消解）。
- 对象指称做成兜底命名规则（本是 fold 应用，替 LLM 操心它本来就会的——承「轻机制」）。
