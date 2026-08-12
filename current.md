# CogOS

继续 CogOS 工作。上次结论：交接完成，待进入 CLI 测试和下一阶段设计。

关键锚点：
- bot_id 不可变（文件名 stem），name 可变（JSON 字段）
- Session 持 bot dict 取代 app_id
- WSManager 在 daemon 启动时自动恢复
