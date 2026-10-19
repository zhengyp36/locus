# 工具用法 · 全量整理（草稿）

> 讨论日期 2026-10-17。意识层工具＝`body`＋`memory`，工具＝**system block / tool schema / user 消息（用法缓存）** 三部分。此稿＝工具用法全量，未收口。
> 数据源：`cogos/agent/catalog.py`（23 个能力，已落码）＋ `memory` 工具（10-15 设计口径，未落码）。

## 0. 呈现结构（三部分）

| 部分 | 内容 | 性质 |
|---|---|---|
| system block | 能力总览（what：body 能做什么 + memory 是什么） | 常驻、叙述 |
| tool schema | body（入口＋"用 help 拿用法"）／ memory（fold/unfold 用法） | 常驻、结构化 |
| user 消息 | 最近用过工具的用法缓存（条数上限，标 `[tool usage]`） | 动态、可淘汰 |

- 调用通道唯一：schema 只注册 body/memory，模型只能调这两个；用法缓存只省 help 探索，调用仍走 `body call`。
- 缓存是主动机制（全局工作空间是树生长式、会压缩 help 结果），装配时注入为 user 消息。

## 1. tool schema

### body（三参数）

```
command: string, enum["help","call"]   # 必填
name:    string   # 能力英文路径；help 可用前缀，call 需完整路径
args:    object   # call 的参数，键名靠 help
```

### memory（设计口径，未落码）

```
fold:   name + description   # 把一段思考整理成概念
unfold: name                 # 把概念展开成详情
```

## 2. body help 四级

```
body(help)                              → 三组总览
body(help, name="computer")             → 组下 faces
body(help, name="computer.command")     → face 下 capabilities
body(help, name="computer.command.run") → 该能力详情（五段式）
```

- `body(help)` 三组总览：

```
可用能力分三组，用 body(help, name=<组>) 展开：
- computer（电脑）：你自己的机器：跑命令、读写文件、看并操作图形界面、上网查取信息；到点能提醒你。
- communication（通信）：和其他人相互交流——收发消息与文件。
- vision（视觉）：能看清一张图的细节（可放大局部），并测出图上某处的坐标。
```

- 组下 faces：

```
computer     → command / file / screen / web / reminder
communication → message / file
vision       → （无 face，直接 see / mark / coord）
```

- 五段式格式（一条工具详情）：

```
<path>
<summary 一句话做什么>
参数：
- <name>（必填/可选, <type>）：<description>
返回：<returns>
时间形态：<sync|async>
```

## 3. 能力全量（23 个，按 catalog 声明序）

### computer.command（终端）

**run**
```
跑一条命令（发起即返回，不回显输出）
参数：
- command（必填, string）：要执行的命令
- notify（可选, string）：命令完成后的通知 token；把 token 编进命令（cmd; printf '\033]cogos;<token>\007'），完成后机制发事件
返回：发起回执（不含命令输出）
时间形态：async
```

**observe**
```
回看当前会话输出
参数：
- offset（可选, number）：窗口起始行号，从 1 开始，省略则看末尾屏
- limit（可选, number）：最多返回行数，省略则一屏
返回：会话屏幕文本
时间形态：async
```

**interrupt**
```
打断当前命令
参数：
- （无）
返回：会话状态
时间形态：async
```

**send**
```
向会话原样发文本或按键（不隐式回车）
参数：
- data（必填, string）：要原样发送的内容；控制键用 ^C / ^D / <Tab> 记号
返回：会话状态
时间形态：async
```

> face 级附注（`help` 打印在能力清单下）：run 发起即返回、不回显输出；用 observe 看屏取输出（首选），输出大或要精确内容时让命令重定向到文件、再用 file.read 读。

### computer.file（文件）

**read**
```
读文件（按行，带行号）
参数：
- path（必填, string）：文件路径：相对路径以机器根为基，绝对路径原样
- offset（可选, number）：起始行号，从 1 开始，默认 1
- limit（可选, number）：最多读取行数
返回：带行号的文件内容
时间形态：sync
```

**write**
```
写文件（整份覆盖）
参数：
- path（必填, string）：文件路径；父目录不存在时自动创建
- content（必填, string）：要写入的完整内容
返回：写入字节数
时间形态：sync
```

**edit**
```
精确替换文件中的一段字符串
参数：
- path（必填, string）：文件路径
- old_string（必填, string）：要被替换的原文片段，必须唯一
- new_string（必填, string）：替换后的新片段
返回：写入字节数
时间形态：sync
```

### computer.screen（图形面）

**look**
```
取当前屏幕一帧（当前视图）
参数：
- （无）
返回：当前帧图片路径与像素尺寸
时间形态：async
```

**act**
```
在刚看到的帧上动作 → 回新帧＋落点
参数：
- op（可选, string）：click / move / drag / scroll / type / key / launch（默认 click）
- region（可选, string）：目标区域 "x,y,w,h" 归一化（相对当前帧）
- point（可选, string）：落点 "x,y" 归一化
- on_change（可选, string）：act / skip
- text（可选, string）：type / launch：文本或 app / URL
- keys（可选, string）：key：键名或组合，如 "ctrl+l"
- dy（可选, number）：scroll：滚动量（正上负下）
- to（可选, string）：drag：终点 "x,y" 归一化
- button（可选, number）：鼠标键，默认 1
- clicks（可选, number）：点击次数，默认 1
返回：新帧图片路径＋落点
时间形态：async
```

**save**
```
把当前帧存成文件
参数：
- path（可选, string）：目标路径，省略则用时间戳名
返回：持久文件路径
时间形态：async
```

### computer.web（上网）

**search**
```
搜网页 → 结果
参数：
- query（必填, string）：搜索关键词，中英文均可
- count（可选, number）：返回结果条数，默认 10，最大 20
返回：搜索结果
时间形态：async
```

**fetch**
```
抓网页正文 → 结果
参数：
- url（必填, string）：要抓取的网页完整 URL
- format（可选, string）：markdown（默认）/ text / html
返回：网页正文
时间形态：async
```

**cancel**
```
取消一个在途的网页作业
参数：
- job_id（必填, number）：作业 id（来自 search / fetch 的返回）
返回：作业状态
时间形态：sync
```

### computer.reminder（提醒）

**set**
```
设一个到点提醒
参数：
- title（必填, string）：提醒事项，触发时带回
- delay_seconds（必填, number）：多少秒后触发
返回：提醒 id 与触发时刻
时间形态：sync
```

**cancel**
```
取消一个提醒
参数：
- id（必填, number）：提醒 id
返回：提醒状态
时间形态：sync
```

**list**
```
列出未触发的提醒
参数：
- （无）
返回：提醒列表（含剩余秒数）
时间形态：sync
```

### communication（通信）

**message.send**
```
给联系人或号码发消息
参数：
- to（必填, string）：接收者：联系人名字或号码
- content（必填, string）：要发送的消息内容
返回：发送结果
时间形态：async
```

**file.send**
```
把一个文件发给对方
参数：
- to（必填, string）：接收者：联系人名字、号码或群 id
- src（必填, string）：文件路径或暂存区条目 id
- name（可选, string）：发送时使用的文件名，省略用原名
返回：发送结果
时间形态：async
```

**file.receive**
```
取回收到的文件
参数：
- keys（必填, array）：附件 key（来自收到文件的事件）
- dst（可选, string）：落地目录，省略则用默认
返回：文件落地路径
时间形态：async
```

**file.cancel**
```
取消一个在途的文件收发作业
参数：
- job_id（必填, number）：作业 id（来自 file.send / file.receive 的返回）
返回：作业状态
时间形态：sync
```

### vision（视觉）

**see**
```
打开一张图、或放大局部
参数：
- ref（必填, string）：PATH:<路径> 开图 | FIG:<id> 调视野
- center（可选, string）：窗口中心 "x,y"（0~1）
- size（可选, string）：窗口尺寸 "w,h"（0~1）
- remark（可选, string）：备注（可选）
返回：图与元信息行（含 FIG id）
时间形态：async
```

**mark**
```
在图上标注
参数：
- ref（必填, string）：FIG:<id>
- kind（必填, string）：cross（单点）/ rect（区域）
- center（必填, string）：标注中心 "x,y"（0~1）
- size（可选, string）：rect 尺寸 "w,h"（0~1）
- remark（可选, string）：备注（可选）
返回：图与标注 id（ANNO:n）
时间形态：async
```

**coord**
```
读标注的源图坐标
参数：
- ref（必填, string）：FIG:<id>
- anno（必填, string）：ANNO:<n>
- remark（可选, string）：备注（可选）
返回：源图归一化坐标＋像素
时间形态：async
```

## 4. 备注（收口前待对齐）

- **分组口径**：body 讨论里"能力总览"说 5 组（通信/看图/读写/上网/终端），catalog 实际是 3 组（computer/communication/vision）——`terminal`/`file`/`screen`/`web`/`reminder` 都收在 `computer` 组下。总览文案与 help 需对齐到同一套分组。
- **模型面名解耦**：`communication.message.send` 的 `to` 经 `arg_map` 映射到实现 `target`；模型只见 `to`，实现名不可见。
- **time_form**：`sync`（同步取值）／`async`（发起即返回，结果走 user 消息）；与"外部工具不占住 / 自身工具有界"的历史口径相关，未在本稿展开。
- 未暴露的能力：`computer.command.open/list/answer_auth`（N1-A 撤下，单会话 toolbox 无法定向会话；A2 多会话再议）。
