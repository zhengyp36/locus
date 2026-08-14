# cogos 项目认知地图

> 更新：2026-08-15（新方法：目的优先 + 状态轴）| 本体：`~/codex/cogos`
> 入口：`cogos-feishu <command>`（`python3.11 -m cogos.feishu.cli`）| 测试：`python3.11 -m pytest tests/ -q`
> 用法：读「一~五」建整体理解 → grep 目标模块标题 → read 对应小节。写时同步：改动改变不变量/易错点/调用关系/入口/测试命令才重写对应小节（重写式，非追加）。
> 状态轴标记：✅ 已实现 · 🔧 调试中（代码完整、待真机）· ⏳ 未实现/预留 · ⚠️ 折中/待核（留人判，不擅断）

## 一、项目目的（认知层）

- 起源 `~/agent-study`：先学 agent → 开发 agent → 追求 AGI。
- 最初构想 AGI 是**独立认知个体**；后转向：搭**平台**（cogos，认知操作系统），从平台生成 AGI agent。
- 通信工具 = 独立个体的**嘴和耳朵**，接**感知层**而非意识层（外部消息不能直接注入 LLM 上下文）；身份靠号码识别。

## 二、概念体系（项目自己的语言）

- **设备（device）**：实体设备（一台电脑），`init` 生成设备信息。一台设备可加入多个 provider。⚠️ bs-bot 账号暂未绑定 device（account 无 device 字段；device 现仅用于 /resume 写 devices/instances 表）。
- **provider（运营商）**：一个飞书租户下的号码域，可命名（`COGOS001`）；= **唯一 admin-bot + 若干 bs-bot**，维护 `Axxxx`/`Hxxxx`。支持多运营商；**不互通是折中而非设计**。
- **bs-bot（基站）**：一个 **(provider, device)** 对应一个飞书 bot 账号，`setup-bs --provider X` 由真人授权创建。每 bs-bot 一个**真人管理员**（谁扫码创建谁管理），只响应管理员消息。
- **admin-bot**：provider 唯一，有一个 **bitable**；账号**只读写 bitable、不监听 WS**（收发是 bs-bot 的职责）；所有 bs-bot 共用同一 admin-bot 账号读写 bitable，无权限问题。
- **多设备**：换设备再 `setup-bs` → `/resume <admin-bot-app-id> <admin-bot-app-secret>` 用 admin-bot 账号读 bitable 恢复。
- **号码**：真人 `Hxxxx`（手动填、无 counter）、agent `Axxxx`（自动 counter）、bs-bot `Sxxxx`（预留、当前不分配）。**H/A 有 name 字段**。号码在**单 provider 内**唯一（不并发创建保证，使用者纪律，⚠️非软件保证）。
- **agent-bot vs agent**：agent-bot = 飞书 app（app-id/app-secret），一个 agent-bot 对应一个 `Axxxx`；agent = **独立认知个体**，一个 agent **可持多个 agent 号码**（像人多手机号）。
- **群成员视觉一致**：真人 nickname=`Hxxxx`（`张三(H1284)`），bot 名=`name(Axxxx)`（`李四(A2736)`）。
- **PIN**：add-agent 生成（随机串），startup 鉴权。⏳ 代码暂无。
- **bot↔bot 私聊**：飞书不支持 bot 互通 → 建**双 bot 群 + @all**，不解散、写 bitable。⏳
- **号码全名只在接口层**：`运营商前缀+号码`（`COGOS001:A1328`）；内部定位 provider 后只用裸号码，代码 key 一律裸号码。
- **消息落地**：本地文件 `SESSIONS_DIR/<app_id>/<chat_id>/stream|history|cards`；收发都先落 stream，处理后进 history（`pick` 改名 `.doing` → `done` 移到 history）；文件名 `{ts}_{rand4}_{type}.json`。

## 三、Python 接口（agent 侧，设计目标，⏳ 未实现）

```python
inst = startup("COGOS001:A1328", on_msg, PIN)
inst.send("COGOS001:H2049", msg)
inst.send("COGOS001:A0053", msg)
inst.shutdown()
```

## 四、关键不变量（兑现状态）

1. 每 provider 唯一 admin-bot；admin 只读写 bitable、不监听 WS。✅（daemon 不激活 admin、handler 无 admin 注册）
2. 每 (provider, device) 一个独立 bs-bot；bs-bot 有真人管理员。⚠️（device 维度未绑定）
3. `/resume` 用 admin-bot 账号读 bitable 恢复多设备。✅
4. bot 间私聊 = 双 bot 群 + @all；群不解散、写 bitable。⏳
5. add-agent 生成 PIN；一 agent-bot 一 Axxxx；一 agent 可持多 Axxxx。⏳
6. H/A 号码单 provider 内唯一（不并发保证）。⏳（H 手动、A 自动 counter、S 预留）
7. 一人/agent 可持多 provider 号码；运营商不互通是折中。⚠️（结构预留、号码分配未实现）
8. 接口层带前缀、内部裸号码。⚠️（前缀解析随 startup 一起未实现）
9. 消息落地 = 本地文件目录模型。✅

## 五、状态轴总览

- ✅ 已实现：飞书通信基础 = ws / send / 监听收消息（7 类事件落盘）/ 收发卡片；命令框架（CLI + 消息命令）；环境/设备/账号/清理。
- 🔧 调试中：setup 流程（OAuth 建 admin-bot → 配 scope → 建 bitable 7 表 → 写 admin_registry）+ /resume。
- ⏳ 未实现：号码分配（三张号码注册表已建、无命令无写入、counter 未接线）、PIN、`startup/send/shutdown` 接口、双 bot 群自动建立、@all、`/add-human` `/add-agent`。
- 预留未接线：bot_type `agent`/`admin` 已枚举，EventHandler 只注册 `test`/`bs`。

## 六、代码分层

### G1 框架核心（进程 + 命令 + IPC）
- config.py — 全局配置（延迟加载，路径从 BASE_DIR 派生）。✅ 不变量：所有路径从 `BASE_DIR` 派生。测试 `test_config.py`。
- commands.py — 命令注册框架（`@define`/`@on_done` + DESCRIPTION）。✅ 易错：新增命令须补 DESCRIPTION。测试 `test_commands.py`。
- cli.py — CLI 入口（argparse + CLI/DAEMON 路由）。✅
- client.py — Unix socket 客户端（CLI→daemon）。✅
- daemon.py — daemon 进程（flock 防脑裂；启动自动激活 bs-bot，**不激活 admin**）。✅ 测试 `test_daemon.py`。
- monitor.py — monitor 守护（心跳 + 重启）。✅ 待补：`monitor on/off` 命令。测试 `test_monitor.py`。
- protocol.py — IPC/心跳协议（JSON-lines）。✅ 测试 `test_protocol.py`。
- service.py — 进程管理（systemd/manual 统一）。✅ 测试 `test_service.py`。
- entry.py — 消息/事件**数据模型**（`Entry` + 7 子类，frozen dataclass；`from_event` 覆盖 8 类事件）。✅（旧 map 误猜为「入口」）测试 `test_entry.py`。

### G2 飞书 API / 连接 / 会话
- core.py — 飞书 API 积木（url + Lib）。✅ 易错：OAuth `PersonalAgent` 建的 bot 无 patch 自管理权限（PATCH scope 前须先 `url.auth(app_id, BOT_PATCH_PERMISSIONS)` 引导授权）；`add_members` 的 `member_id_type` 是 query param。
- ws.py — WebSocket 管理（WSClient + WSManager，daemon 启动自动恢复）。✅
- session.py — Session（持 bot dict）；**消息落地兑现者**（`save_entry`/`pick`/`done`/`drain`，`SESSIONS_DIR/<app_id>/<chat_id>/stream|history|cards`）。✅ 不变量：bot_id 不可变（文件名 stem）、name 可变。

### G3 通信线 / Provider（bs_*）
- provider.py — provider 管理命令 `setup-bs`/`switch-provider`。✅（OAuth 创建 bs-bot 待真机）测试 `test_provider.py`。
- bs_provider.py — provider 设置流程 `setup_provider`/`resume_provider`（OAuth → scope → bitable 7 表 → 落盘）。🔧 易错（一条因果链）：patch 授权步须在 `_configure_admin_bot` 前；OAuth 后立即 `_save_admin_account` 落盘（重试不泄漏）；`bot-{bot_id}.json` 前缀勿漏。测试 `test_bs_provider.py`。
- bs_card.py — 设置卡片交互（`awaiting_patch` 态 + `on_patch_permission` Event）。🔧 测试 `test_bs_card.py`。
- bs_setup.py — bs 消息命令 `/setup` `/resume` `/help`（`admin_only`）。✅ 测试 `test_bs_cmd.py`。
- bs_cmd.py — 消息命令框架（`@msg_command` + `dispatch`）。✅
- bs_workspace.py — setup 持久化工作区（`SESSIONS_DIR/<app_id>/workspace/setup-*.json`，原子写）。✅
- bot_manifest.py — bot 清单/权限常量（`BOT_PATCH_PERMISSIONS` 已被调用）。✅
- bitable_helper.py — Bitable 助手（建表/读写；`read_counter`/`increment_counter` 定义但**无调用**）。✅

### G4 账号 / bot / 事件
- accounts.py — 账号管理（create_bot/save_account/Speaker/get_bot_by_app_id）。✅ 测试 `test_accounts.py`。
- botmgr.py — bot 生命周期 `add-bot`/`remove-bot`/`list-bot`（daemon 内）。✅
- handler.py — 事件回调注册（仅 `test`/`bs`；`_handle_card_action` 返回 TOAST 回执）。✅（admin/agent 未注册，兑现不变量 1）
- groupmgr.py — 群管理 `create-group`/`invite-members`/`leave-group`/`destroy-group`（仅手动）。✅ 易错：`add_members` query param。测试 `test_groupmgr.py`。

### G5 环境 / 设备 / 调试 / 工具
- env.py — 环境命令 `init`/`stop`/`reset`/`status`/`update-config`。✅
- device.py — 设备信息（instance_id + device.json）。✅ 测试 `test_device.py`。
- debug.py — 调试 `echo`/`simulate-dead`/`watch-bot`。✅ 测试 `test_echo.py`。
- purge.py — `purge-bot` 清理（退群 + 删 Bitable，dry_run/force/forget）。✅
- utils.py — 通用工具（`TmpFilePair` 原子写、`FileLock` 非阻塞 flock、`Dot`）。✅ 测试 `test_utils.py`。

## 七、模块 ↔ 不变量映射

| 不变量 | 兑现模块 | 状态 |
|---|---|---|
| 1 admin 唯一 + 不监听 WS | bs_provider / handler / daemon / ws | 兑现 |
| 2 (provider,device) 一 bs-bot | accounts / bs_cmd / provider | 部分（device 未绑定）|
| 3 /resume 读 bitable | bs_setup / bs_provider | 兑现 |
| 4 双 bot 群 + @all | groupmgr（仅手动）/ core（无 @all）| 未实现 |
| 5 PIN + 一 agent-bot 一 Axxxx | bs_provider（表建）/ bitable_helper（counter 未接）| 未实现 |
| 6 H/A 唯一 | counters / bitable_helper | 未实现 |
| 7 多 provider 号码 | config / accounts / provider | 部分 |
| 8 前缀→裸号码 | accounts / session / bs_workspace | 部分 |
| 9 消息落地目录 | session / config | 兑现 |

## 八、已裁决 / 折中 / 待核

- **已裁决（2026-08-14）**：agent-bot 由 bs-bot 触发创建（编排），bitable 读写全程走 admin-bot 账号（数据）；管理员数量不限制；号码前缀 H/A/S 三类（H 手动、A 自动 counter、S 预留不分配）。
- **折中（⚠️ 留人判）**：号码唯一性 = 使用者纪律保证，非软件保证（InstanceLock 无法跨设备）；运营商不互通是折中非设计。
- **待核**：device 与 bs-bot 的绑定（当前 account 无 device 字段）；`S` 号码是否真的永不分配。
