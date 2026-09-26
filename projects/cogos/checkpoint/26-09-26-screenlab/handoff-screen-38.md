# handoff｜交接给新会话 · 2026-09-24 #38

> 接 #37（#37 = "按怎么使用重验图形面"那一轮）。本会话（#37 续）做了**两批修复**：
> ① 「原因清楚且纯 bug」批（F1/F1b/F2/session.env/`--no-sandbox`）；
> ② F6/F9/F7「close 与 GUI 进程」（YZ 定 **温和默认 + `--force`**）。
> **均已落码 + 靶机验证，未提交。** 上下文 202k/1M（20%）→ 按纪律切会话。
>
> **规则 / 环境操作不在这里**——见 **`screenlab-rules.md`**（稳定参考，先读）。本文件只讲状态 / 待决 / 下一步。

## 给新会话的第一句话

> 先读 **`screenlab-rules.md`**（规则 + 环境操作，稳定）→ 再读**本文件**（状态 / 待决 / 下一步）→ **`spec-screen-1.md` §0.0**（目标，唯一约束）→ **`checkpoint/tmp-screen-usage-verify.md`**（本轮全部证据 / 讨论 / 实现）。
> **下一步顺序（YZ 定）**：① 等 YZ 裁决 **F8 剩余** 与 **F4**（见下）；② 跨机 `view` 验证（便宜）；③ C4「重启不自启」按静态判断；④ 收尾（并入 `issue-screen-surface-lifecycle.md`「执行中发现」、写 #39 handoff、与 YZ 讨论后删 tmp）；⑤ 代码**不提交**等 YZ。
> 靶机在跑：`surface-centos-9`，账户只剩 `sva`（`:10` 1600x900）；面当前 **inactive**（已 force close）。

## 本会话已做并靶机验证（未提交）

### 批 1「纯 bug」
- **F1** 面未起时 `surface` 挂死 → 存活预检（查 `/tmp/.X11-unix/XN`）+ xdotool `timeout`；实测 **123ms** 返回 `{"error":"surface_not_running"}` rc=1（原挂死 435s+）。
- **F1b** `alloc_display` 撞 sshd X11 转发 TCP → 新增 `display_in_use()`（unix / lock / **TCP 6000+N**）；占 6010/6011 时跳过。
- **F2** 空剪贴板 → rc=0、无 stderr；**写路径 `xclip` 泄漏 stdio 使经 ssh 永不返回** → stdio 重定向 + `-loops 1`（实测 2s 返回）。
- `session.env` 前导空格删除；`--no-sandbox` 全仓无残留；`surface --help` 改为不依赖 session.env / 面。

### 批 2「F6/F9/F7 close 与 GUI 进程」（YZ 定：温和默认 + `--force`）
- **`surface run`** → `systemd-run --user --collect --slice=screenlab-apps.slice --unit=screenlab-app-<pid>-<rnd>`（cgroup 归组、即时返回；失败 `{"event":"failed",...}`，成功 `{"event":"started","unit":...}`）。
- **`surface close <窗口>`** → `windowactivate --sync` + `xdotool key alt+F4`（**真 WM_DELETE**，非 `windowclose`=XDestroyWindow）；事件 `close_requested`。
- **`screenlab close`（温和默认）**：对所有窗口发 WM_DELETE → 有界等待（`SCREENLAB_CLOSE_GRACE`，默认 10s）→ 查 slice **cgroup 实际进程**（**不用 `is-active`**：cgroup 空后 slice 仍会短暂报 active）→ 空则停 target 报 `{"event":"closed","forced":false}`；非空则**不动会话**、报 `{"event":"close_blocked","closed":false,"survivors":["<pid>:<comm>"]}` rc=1。
- **`screenlab close --force`**：polite ask 后 `stop screenlab-apps.slice`（SIGTERM→SIGKILL）**再**停 target，报 `{"event":"closed","forced":true}`。
- `close --destroy` 内联 force。
- 另：`surface run` 启动失败现可判读（**部分解 F8**）。
- 契约 `screenlab/install/session-create.md`、`surface --help`、`screenlab` usage 已更新。

**验证（靶机）**：温和关闭后 target inactive 且无残留；`surface run sleep 300` → `close_blocked` survivors 正确且会话保留；`--force` 干净收敛；**F9** 两轮 open/run/close 后重开 chrome 抓屏**无 `Restore pages?`**（仅 update 气泡）；**F7** 循环 run 均正常起窗；`surface run /nonexistent-cmd-xyz` 报 `failed` rc=1。

## 待 YZ 裁决（飞书已发，尚未回复）

1. **F8 剩余**：**A 推荐** 启动后短暂等待判存活，报 `{started|failed,pid,alive,exit_code}` + 输出落 `STATE/run.log`；**B 最小** 只加日志；**C 现状即可**（已能报 failed + unit）。
2. **F4**：`capture` 无 `tree`、`act element` 未实现，spec §1 宣称与实现不符。建议**改 spec 承认 Goal 1 只有像素**、a11y 记候选（不现在补实现）。同意否？

## 工作树（`../cogos` @ `feat/screenlab-p2`，均未提交）

- 本会话改动：`screenlab/install/` 下 `surface`（**untracked**）、`session-start.sh`、`session-stop.sh`、`screenlab`、`session-create.md`。
- #36 遗留（非本会话）：`cogos/agent/tools.py`、`docs/design-agent-tools.md`、`screenlab/proto/protocol.py`、`screenlab/service/{cli,daemon}.py`、`tests/screenlab/e2e/tool_loop_e2e.py`。

## 入口

- **规则 + 环境（先读，稳定）**：`screenlab-rules.md`
- **本轮全部证据（含 F6/F9 讨论与实现）**：`checkpoint/tmp-screen-usage-verify.md`
- 目标（唯一约束）：`spec-screen-1.md` §0.0
- 结论/依据：`issue-screen-surface-lifecycle.md`（本轮发现待并入「执行中发现」）
- 体系：`design-screen-system.md`；契约：`../cogos/screenlab/install/session-create.md`
- 代码：`../cogos` @ `feat/screenlab-p2`
- 上一轮：#37 `handoff-screen-37.md`
