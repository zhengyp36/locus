# body tool params (draft, 2026-10-18)

> `?` = 可选，其余必填。句柄值形式：web/terminal 用 `WEB:<id>`，vision 用 `PATH:<path>` / `FIG:<id>`。

```
body.file.read(path, offset?, limit?)
body.file.write(path, content)
body.file.edit(path, old_string, new_string)
body.vision.see(ref, center?, size?, remark?)
body.vision.mark(ref, kind, center, size?, remark?)
body.vision.coord(ref, anno)
body.chat.speak(to, content)
body.chat.browse(to, offset?, limit?)
body.terminal.run(command, notify?)
body.terminal.observe(offset?, limit?)
body.terminal.send(data)
body.terminal.interrupt()
body.web.search(query)
body.web.fetch(url, format?)
body.web.browse(ref, offset?, limit?)
body.web.cancel(ref)
body.web.close(ref)
```

## 决策点（本列表里已做的取舍，待你确认）

- `body.chat.speak` 保留 `to`（接收者＝联系人名/号码）：`to` 是消息对象，不是设备身份参数；body 默认的是"发送方设备/号码"而非接收者。
- `body.web.cancel/close/browse` 用 `ref`（值 `WEB:<id>`），替代原 toolbox 的数字 `job_id`。
- `body.web.browse` 是唯一入口：返回 running/done 状态 + 内容，可 offset/limit 拉部分；cancel ≠ close。
- `body.vision.coord` 去掉 `remark`：纯读、无持久语义（现有 impl 只是把 remark 拼回返回文本，无意义）；`see`/`mark` 的 remark 保留（note 落 FIG/ANNO 对象）。
- `body.chat.browse` 加 `to`（必填）：chat 的对象是联系人/群，browse 浏览的就是"和某个对象的历史对话"，offset/limit 分页翻历史。
- vision 三动作 `see/mark/coord` 的 `remark` 倾向去掉：对象引用靠 FIG/ANNO 句柄，文字备注是 agent 记忆职责，不该由工具参数承载。
- `web.fetch` 的 `format` 倾向去掉：默认 markdown，html 原始结构是罕见需求，走 toolbox。
- `search` 去 `count`：返回量由机制统一截断（内容分流），超上限走 browse 拉；发起类一律不带返回量参数。
- 拉取类（read/observe/browse）的 `limit` 倾向一并去掉：只留 `offset` 游标定位，返回量统一截断；待确认。
- desktop 组（`body.desktop.act`）遗留，不在本列表。
