# 2026-10-04 · 飞书富文本入站丢失 + 入站必有回执

## 结论

- **根因**：用户用飞书"自动编号"（有序列表）发消息时，消息以 `msg_type=post`（富文本）到达；`src/feishu.ts` 只读 `content.text`，post 无此字段 → text 为空 → `src/bridge.ts` 判 `ignore empty or non-text message` 静默丢弃。重发时复制粘贴丢了列表格式、退回 `text`，才被处理 —— 表现为"消息丢失、重发才好"。
- **实证**：用 KILO-DOCTOR app 凭据拉 `im/v1/messages` 历史，当天三次"无响应"消息 `msg_type` 均为 `post`，与日志三次 `ignore empty or non-text message` 逐一对应；桥接无 warn、无事件流重连、无排队。**排除**飞书丢推送、busy 卡死、WS 缺口。
- **修复**（commit `88c8ac4` + review 修正 `fcb4bf8`，feat/kilo-phone，已 push；已 `bridge-restart` 部署）：
  - 解析 `post`：渲染 `text/a/at/emotion/hr/code_block`，优先 `content_v2` 的 `md`（保留原始 markdown）；`img` 内嵌图片下载并复用附件通道。
  - 不支持类型（`audio/media/sticker/merge_forward/interactive/...`）→ 回执"暂不支持 X，请发文字或图片"，不再静默丢。
  - **入站必有回执**：`ack: always | delayed | off`（per-bot，默认 always）；直发回"收到，处理中…"，排队回"前面还有 N 条"；投递失败与"完成但无文字回复"也各补一条信号。
  - 忽略/入站日志带 `message_type`，未来可诊断。

## why（关键判断）

- **回执默认 always**：核心价值是区分"收到 / 没收到"，这正是本次事故最伤人处。`delayed`（默认 5s 后才出声）留给怕吵的 bot 当逃生配置。
- **不下载音频/视频喂模型**：模型用不上，回执提示更合适；图片可下载故支持。
- **空回复补完成信号**：否则"回执"之后又静默。

## 被否方案

- **只认 `text`、post 归为"不支持"**：编号列表是常见用户输入，且解析零额外 API，是真需求，必须真解析。
- **让用户别用自动编号**：客户端行为，改不了用户，治标不治本。

## 验证

- 单测 `npm run test:inbound-post`、`test:inbound-ack`；`typecheck` + 既有 `test:inbound-attachment` / `test:switch-busy-guard` / `test:auto-handoff` 全过。
- **真实验收通过**（2026-10-04 14:58 CST，真实身份 + 飞书公开入口）：
  - 06:58:32 自动编号 `post`（1./2./3. 三条）到达 → 06:58:33 收到「收到，处理中…」→ 06:58:45 正式答复，内容确认三条完整。原静默丢 bug 消除。
  - 06:59:49 语音 → 06:59:50「收到，处理中…」→ 06:59:58 答复。
- **语音实测**：飞书自动转写，入站即 `text` 类型，走正常文本通道；`audio` 分支保留为"未转写真音频"的兜底（日常不触发）。
