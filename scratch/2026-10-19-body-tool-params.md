# body tool params (draft, 2026-10-19)

```
body.chat.speak(to, text)
body.chat.browse(chat, before?, limit?)
body.file.read(path, offset?, limit?)
body.file.write(path, content)
body.file.edit(path, old_string, new_string, replace_all?)
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

- chat：`speak(to, text)`；`browse(chat, before?, limit?)`，`before` 缺省从最新往前读
- file：参数/命名对齐 kilo（path/old_string/new_string/replace_all）
- terminal：`run(command)` 命令是完整一行 shell 字符串（参数/引号/管道由 agent 拼），异步启动即返回；`observe` 读物理行（pyte 渲染，wrap 后每行 ≤ 列宽），`offset` 缺省看末尾；`send` 原样发字节不隐式回车；`interrupt` 发 `\x03`
- web：`search(query)` / `fetch(url)` 提交即返回 `WEB:<id>` 句柄；`browse(ref, offset?, limit?)` 唯一入口，返回状态（running/done）+ 内容（行号分页，`offset` 缺省从头）；done 默认通知 agent；`cancel` 取消在途，`close` 释放完成（TTL 2h 兜底）
- vision：`see(ref, center?, size?, remark?)` PATH 开图 / FIG 调视野；`mark(ref, kind, center, size?, remark?)` cross/rect 标注，返回 ANNO；`coord(ref, anno)` 读回原图坐标（纯读无 remark）。坐标归一化，`see`/`mark` 的 center 相对当前视野，`coord` 换算回原图

## 定位单位分道

| 对象 | 单位 | 定位 | 意图数量 |
|---|---|---|---|
| file | 逻辑行 | `offset`（行号，缺省从头） | `limit` |
| terminal | 物理行 | `offset`（行号，缺省看末尾） | `limit` |
| chat | 条 | `before`（时间戳，缺省最新） | `limit` |
| web | 逻辑行 | `offset`（行号，缺省从头） | `limit` |
| vision | 图（FIG） | 坐标（center/size 开窗） | — |

## 截断

- 机制总量上限兜底，末尾截断标 `truncated`（单位：file/web 逻辑行 / terminal 物理行 / chat 条）
- terminal 物理行天然 ≤ 列宽，无单行超长；file/web 逻辑行超长靠总量截断兜底

## 待定

- `terminal.run` 的 `notify`：cogos 用 OSC token 编进命令实现完成通知；body 是否保留待定
- `web.fetch` 的 `format`：倾向去掉（默认 markdown，html 原始结构走 toolbox）
