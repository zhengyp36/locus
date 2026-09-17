# handoff｜kilo-phone：A0006 作为 Kilo 的「手机」与 agent 对话（09-13）

> 新会话入口。本轮把 spec 落成代码并真机验证了 cogos 侧；Kilo 侧注入待真机跑。
> spec / 实现状态：`work/A/kilo-resident/docs/design-kilo-phone.md`（§14）。

## 一句话

Kilo 以独立号码 `COGOS002:A0006` 当「另一个真人」与 agent 对话：按需开一部 cogos「手机」（helper 进程），入站唤醒 Kilo、出站只在 Kilo 显式调 `phone_send` 时发（无自动回传，防自激）。

## 代码 / 提交（已 push）

- `work/A/kilo-resident` 分支 `feat/kilo-phone` `e0f16e0`
- `work/A/cogos-kilo-phone` 分支 `feat/kilo-phone` `e2de0a3`（off `s2-selfdrive-loop`）
- `work/A/locus` master：`4c23bb1`（记忆）、`25a62bc`（workspace.json 注册 kilo-resident external）

## 已实现

- cogos：`cogos/phone/helper.py`（持 Phone、`on_msg`→POST sink、loopback `/send /status /resume /close`、每对端连续入站上限 fuse）+ `tests/phone/test_helper.py`。
- kilo-resident：`src/phone.ts`（PhoneManager 子进程 + sink）、`src/bridge.ts`（`/phone/*` 控制路由 + `deliver()` 注入）、`src/control.ts`、`src/types.ts`、`config.example.json`、`plugin/kilo-phone.ts`（`phone_open`/`phone_send`/`phone_close`）、`test/phone.ts`。

## 已验证

- cogos 全量 `1071 passed / 1 skipped`；helper 10 项测试。
- kilo-resident `npm run typecheck`、`npm run test:phone`。
- 真机（helper 层）：
  - 入站 A0001→A0006→sink（payload `{source:"agent",from,round,...}`）✅
  - 出站 `POST /send {to:"COGOS002:A0001"}` → A0001 收到 `from=COGOS002:A0006` ✅
  - helper 停 → daemon `list-bot` 中 A0006 消失（释放号码）✅
  - 无自动回传 ✅

## 未验证 / 待办（新会话）

1. **Kilo 侧 bridge 注入未真机跑**（最关键）：需常驻 bridge + 一个 Kilo 会话。起法：在 `work/A/kilo-resident` 放 `config.json`（含 `phone` 块 + `wake.mode`），`scripts/residentctl.sh start`；然后 `phone_open`，让 A0001 发 A0006，确认会话出现 `[agent来信] COGOS002:A0001 · 第 N 轮：…` 回合且无自动回传。注意端口（4097/4180）与 B 侧 bridge 冲突风险——B 侧若在跑，先停或改端口。
2. **切会话自动释放未机制化**：当前只有显式 `phone_close` / helper 崩溃释放；会话切换的自动杀未接线（spec §14 开放问题 1）。
3. **插件未挂载**：`plugin/kilo-phone.ts` 需按现有方式软链到 `~/.config/kilo/plugin/`。
4. **与唐钰 A0005 的完整 e2e**：需 唐钰 agent 在跑（当前未起）。唐钰侧需 `add_contact("Kilo", ["COGOS002:A0006"])`。
5. 合并决定：两条 `feat/kilo-phone` 是否合入 `main`/`master`。

## 环境事实

- A0006 卡 `~/.cogos/feishu/accounts/bot-COGOS002-A0006.json`，status=active，pin `3b7da434`。
- cogos feishu daemon 在跑（设备级单例）；helper 经它认领卡，断开即释放。
- 测试借用 A0001（李恪，pin `2b36a305`）当发信方；A0006 与 A0001 互发真机已通。
- 跑 cogos 一律 `python3.11` 且从 checkout 用 `-m`。

## 本轮验证（09-13 会话 #10，A 工位）

### phone 真机通了（不依赖插件、不依赖常驻 bridge）
用 cogos `phone.helper` + 自写 sink 手驱：`COGOS002:A0006`(KILO) 认领上线 → YZ 从 `COGOS002:H0002` 发信 → helper POST sink → 读到 → `POST /send` 回 → YZ 收到；`/close` 后 A0006 释放。与插件路径同一套机制，只是手动驱动。
- **发现**：helper 入站 payload 把 `source` 硬编码为 `"agent"`，真人 H0002 被误标——"通道来源"被当成"对方类型"。按"壳只给事实"，应是发送方真实身份。**待修**。

### 常驻 bridge 的两种唤醒形态（已实测配置）
- **无头**：bot → 临时目录 + 新建会话（`wake.mode:"async"`）。
- **当前会话**：bot 显式指到某 sessionID + `wake.mode:"tui"`，DM 作为一轮注入该 TUI 窗口。已配好（把 `KILO-LOCUS-A` 指向 A/locus 的当前会话），但真机审批未跑完。

### 审批增强（A/kilo-resident，未提交，typecheck 过）
- `permission.asked` 超时：由"删记录+拒绝"改为 `expirePermission`——释放工具调用但**保留记录标 `expired`**，发飞书"超时已释放，可 `/retry`"；新增 `/retry <id>`（向会话注入"请重新发起"）；`/pending` 分待审批/已超时两区；`permission.replied` 对 expired 不删。
- **真机集成测试** `test/permission-retry.ts`（`npm run test:permission-retry`）**ALL PASS**：首次 ask → 3s 超时 expired 保留 → `/retry` → 唤醒 → 模型重发新 ask（新 id）。用独立 `kilo serve :4098` 避开旧插件。
- 另加 `notifyChat` 兜底（bot 配置：人未 DM 也能推审批）——**未真机验**。
- 环境：`~/.config/kilo/plugin/permission-notify.ts` → `.disabled`（单向通知、不可批，已摘）。
- 遗留：A 侧 `config.json`（gitignored）留本会话映射 + notifyChat；A bridge 已停；B 常驻 bridge 已恢复（`:4180`）。

## 锚

- spec：`work/A/kilo-resident/docs/design-kilo-phone.md`
- 设计讨论链：`locus/projects/cogos/entries/`（09-12 ~ 09-13）
- 号码/唤醒支线：`checkpoint/handoff-kilo-number-contacts.md`
- 之前状态：`checkpoint/status.md`（cogos v0 主线，与本次并行）
