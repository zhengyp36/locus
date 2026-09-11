# task-7 实现进展（2026-09-11，YZ 交接新会话前）

来源：工位 B `../checkpoint/task-7-handoff-2.md`（新会话入口）。本文件为 locus 记忆快照。

## 本体

- 仓库：`work/B/kilo-resident`，remote `git@github.com:zhengyp36/kilo-resident.git`（public），HEAD `895c765`。
- 栈：Node/TS（Node≥24 直接跑 `.ts`，strip-only，不能参数属性/枚举）。
- 桥接独立进程 + Kilo server 宿主；插件全局（`~/.config/kilo/plugin/`）。

## 已实测

- 飞书文本往返（`hi` → session → 回飞书）。
- `/new` 新建 + 重 pin；`/compact` 接线。
- timer：`/timer 1 …` 秒级准点触发、投递飞书 + 唤醒 session；`/timers` `/cancel`；控制 API；模型工具 `set_timer`/`cancel_timer`/`list_timers` 已加载。
- 桥接实现：入站 WS、白名单（按 open_id）、按 `messageID/parentID` 回路由、忙时 FIFO 等 idle、墙上时间 timer 落盘。

## 关键坑

- `event.subscribe` 必须带 `query.directory`，否则只收 heartbeat。
- 飞书 sender 只有 open_id（缺 user_id 权限）。
- `KILO-LOCUS-A` 不能按 user_id 发 DM；通知用 admin-cli-test。
- `kilo daemon start` 本机 10s 硬超时、子进程 ~11–14s 就绪 → 暂用 `kilo serve`（前置 `-u KILO_PROCESS_ROLE/RUN_ID/PID/KILO/KILOCODE_FEATURE`、设 `KILO_SERVER_USERNAME/PASSWORD`）。

## 遗留（优先级）

1. 常驻宿主非真常驻（随 TUI 停止）；修 daemon 或 systemd。
2. §9.1 terminal（底座 a/b 未定）+ `run_bg` 完成唤醒未移植。
3. §6 权限闭环（superuser 自动回执 / guest 转飞书审批）未做，只有通知插件。
4. §8 自动压缩阈值触发未做。
5. 验证① TUI attach、③ 多窗口并发未做。
6. 飞书入站文件/图片未处理；出站文件未实测；多 bot 未测；guest 无差异化。
7. timer 重启补投、队列超时丢弃：写了未实测。

## 环境副作用（本机，非本体）

- `~/.config/kilo/kilo.jsonc`：`external_directory` 改递归 `**`。
- `~/.config/kilo/plugin/permission-notify.ts`：权限询问时飞书通知 YZ。
- `~/.config/kilo/plugin/kilo-resident-timer.ts` → 软链到本体 `plugin/`。
