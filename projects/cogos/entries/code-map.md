# cogos 代码认知地图

> 更新：2026-08-14（冷启动·方案 b：纯搬运 + 待补）| 本体：`~/codex/cogos`
> 入口：`cogos-feishu <command>`（`python3.11 -m cogos.feishu.cli`）| 测试：`python3.11 -m pytest tests/ -q`
> 用法：读「索引」→ grep 目标模块标题行号 → read 对应小节。写时同步：改动改变不变量/易错点/调用关系/入口/测试命令才重写对应小节（重写式，非追加）。

## 索引

### G1 框架核心（进程 + 命令 + IPC）
- config.py — 全局配置（路径从 BASE_DIR 派生，延迟加载）
- commands.py — 命令注册框架（@define/@on_done + DESCRIPTION）
- cli.py — CLI 入口（argparse + CLI/DAEMON 路由）
- client.py — Unix socket 客户端（CLI→daemon）
- daemon.py — daemon 进程（socket server + flock 防脑裂）
- monitor.py — monitor 守护（心跳 + 自动重启）
- protocol.py — IPC/心跳协议（JSON-lines）
- service.py — 进程管理（systemd/manual 统一接口）
- entry.py — 入口（待补）

### G2 飞书 API / 连接 / 会话
- core.py — 飞书 API 积木（url + Lib）
- ws.py — WebSocket 连接管理（WSClient + WSManager）
- session.py — Session（持 bot dict）

### G3 通信线 / Provider（bs_*）
- provider.py — provider 管理（setup-bs/switch-provider，待补）
- bs_provider.py — bs provider 设置流程（OAuth + patch 授权 + 落盘）
- bs_card.py — 设置卡片交互（awaiting_patch 态）
- bs_setup.py — bs 安装（待补）
- bs_cmd.py — bs 命令（待补）
- bs_workspace.py — 工作区（待补）
- bot_manifest.py — bot 清单/权限常量
- bitable_helper.py — Bitable 维格表助手

### G4 账号 / bot / 事件
- accounts.py — 账号管理（Speaker/create_bot/save_account 等）
- botmgr.py — bot 管理（待补）
- handler.py — 事件处理（待补）
- groupmgr.py — 群管理（待补）

### G5 环境 / 设备 / 调试 / 工具
- env.py — 环境命令（init/stop/reset/status，待补）
- device.py — 设备信息（instance_id + device.json）
- debug.py — 调试命令（echo/simulate-dead）
- purge.py — 清理（待补）
- utils.py — 通用工具（TmpFilePair，待补）

## 模块详解

### config.py — 全局配置
- 职责：延迟加载 + 类属性模式；所有路径经 `_PATH_TABLE` 从 `BASE_DIR` 派生。
- 成员：`CONFIG_PATH=~/.cogos/feishu/config.json`、`BASE_DIR`（默认 `~/.cogos/feishu/default`）、`DAEMON_PID/LOCK`、`SOCKET_PATH`、`LOG_PATH`、`DEVICE_PATH`、`BOTS_DIR`、`PROVIDERS_DIR`、`EVENTS_DIR`、`MONITOR_PERIOD`（默认 120s）、`DEFAULT_PROVIDER`。
- 方法：`load(force=False)`（读 config.json 设路径属性，导入时自动调）、`init(reset=False)`、`inited()`（判字段完整性）。
- 不变量：所有路径从 `BASE_DIR` 派生。
- 测试：`tests/test_config.py`（init/load/inited/add_provider/switch_provider）。

### commands.py — 命令注册框架
- 职责：`@define`/`@on_done` 装饰器注册命令与 CLI 回调，批量接 argparse。
- 核心：`define(name, mode, help, args_def)`、`on_done(name)`、`commands(mode=None)`、`build_argparse_subparsers`、`args_to_namespace`、`Args`（属性代理 `args.x → _fields["x"]`）。
- 不变量：新增命令需在 `DESCRIPTION` 补齐 help 文本（`@define` 注册后应出现在 `--help`）。
- 易错点：`args_def` 格式 `{ "flag|--flag": {default, help, dest} }`；`_do_stop()` 供 `cmd_stop`/`cmd_reset` 共用。
- 测试：`tests/feishu/test_commands.py`。

### cli.py — CLI 入口
- 职责：`CLI.run()`：`_parser → _parse`，无命令则 print_help；MODE_CLI 直调 `func`，MODE_DAEMON 走 `_forward_to_daemon`（`daemon_running` 检查 → `client.call` → `on_done`）。
- 不变量：`_GroupedFormatter` 隐藏 argparse 的 `{command}` 行。

### client.py — Unix Socket 客户端
- 职责：CLI→daemon 调用。`call(cmd, args)` 返回 `{ok, data}` 或 `{ok:false, reason}`；`heartbeat(timeout)` 健康检查；`_SockFile`（readline JSON + write + progress/prompt）。
- 不变量：`call` 内部处理 `progress`（打印）/`prompt`（input 回传）/`result`/`error`。

### daemon.py — daemon 进程
- 职责：长命 socket server。`main()`：flock 防脑裂 → 写 PID → 建 Unix socket server → serve_forever。
- 核心：`instance_running()`、`started_at`（uptime）、`_handle_client`（分发 hb-req/command）、`_handle_cli_client`（查注册表 → handler → result）。
- 不变量：SIGTERM/SIGINT → server.close() → 清理 sock + pid + 释放 lock。
- 测试：`tests/feishu/test_daemon.py`。

### monitor.py — monitor 守护
- 职责：独立进程（不依赖 CLI/daemon 框架），心跳检测 daemon，异常自动重启。
- 核心：`main()`、`_heartbeat_to_daemon`、`_start_daemon`（重试到成功）、`_monitor_exit`。
- 不变量：循环 `heartbeat ok → sleep(MONITOR_PERIOD)`，否则先 stop 再重启。
- 待补：monitor 启停命令（`monitor on/off`）。
- 测试：`tests/feishu/test_monitor.py`。

### protocol.py — 通信协议
- 职责：IPC 协议（CLI↔daemon，JSON-lines）+ 心跳协议（monitor↔daemon）。
- 消息：CLI→ `command`；→CLI `progress`/`prompt`/`result`/`error`；CLI→ `response`；心跳 `hb-req`/`hb-ack`。
- 核心：`proto.ipc.*`/`proto.hb.*`（消息构造 lambda）、`do_check`（类型校验）、`Interaction` 抽象接口（progress/prompt）。
- 不变量：daemon 侧 `_SockFile` 实现 `Interaction`。
- 测试：`tests/feishu/test_protocol.py`。

### service.py — 进程管理
- 职责：`InstanceLock`（flock 防脑裂）、`SysService`（systemctl --user）、`ManualService`（Popen + PID 文件）、`Service`（统一接口，自动选 systemd/manual）。
- 不变量：`Service(prog, pid_file, lock_path)`；`start(mode)` 空 mode 自动检测 systemd，manual 则 Popen + start_new_session；`stop()` 先抢锁防并发 → 停 → 等待 → 释放锁。
- 测试：`tests/feishu/test_service.py`。

### entry.py — 入口（待补）
- 职责：待补（推测入口/启动相关，未见于 README/code-structure）。
- 不变量：待补。

### core.py — 飞书 API 积木
- 职责：飞书 API 封装（`url` + `Lib`）。
- 易错点（bugfix 来源）：
  - OAuth 设备流 `archetype=PersonalAgent` 建的 bot 天生无 `application:application:patch` 自管理权限，PATCH scope 前须先发引导链接授权（`core.url.auth(app_id, permissions)`）。
  - `add_members`: `member_id_type` 是 query param（`params=`），不是 body（`json=`）。

### ws.py — WebSocket 连接管理
- 职责：`WSClient` + `WSManager`。
- 不变量：WSManager 在 daemon 启动时自动恢复。
- 状态：旧 code-structure 标 G3c 进行中，现为已实现（README 确认）。

### session.py — Session
- 职责：Session 持 bot dict（取代 app_id）。
- 不变量：bot_id 不可变（文件名 stem），name 可变（JSON 字段）。
- 状态：旧 code-structure 标「待编码」，实已实现。

### provider.py — provider 管理（待补）
- 职责：`setup-bs`/`switch-provider` 命令（add_provider/switch_provider）。
- 不变量：待补。
- 测试：`tests/test_config.py`（add_provider/switch_provider）。

### bs_provider.py — bs provider 设置流程
- 职责：`setup_provider` 走 OAuth → patch 授权 → `_configure_admin_bot` → Bitable。
- 不变量/易错点（bugfix 来源，一条因果链）：
  - patch 授权步骤：OAuth 后、`_configure_admin_bot` 前必须插 `url.auth(app_id, BOT_PATCH_PERMISSIONS)` 发链接等确认，否则 PATCH scope 被拒（`99991672`）。
  - 落盘时机：OAuth 后立即 `_save_admin_account` 落盘；开头检测 `bot-admin-{provider}.json` 已存在则跳过 OAuth（重试不泄漏）。
  - `_save_admin_account(bot_id, fields)`：幂等 merge 到 `bot-{bot_id}.json`（旧代码漏 `bot-` 前缀 → bitable_token/bitable_url 从未真正落盘）。
  - 重试语义：`patch_granted=True` 时跳过再次要授权；新增 `on_patch_permission(app_id, url)` 回调由卡片层提供。
- 测试：`tests/feishu/test_bs_provider.py`（幂等 merge / 新文件）。

### bs_card.py — 设置卡片交互
- 职责：`build_card` 渲染设置卡片；`handle_card_action` 处理按钮；`_run_setup` 提供回调。
- 不变量/易错点（bugfix 来源）：
  - `awaiting_patch` 态渲染「已完成授权」+「取消」按钮。
  - `confirm_patch` 处理；`cancel` 时也要唤醒等待中的 event。
  - `on_patch_permission` = `asyncio.Event` 阻塞，`wait_for` 600s 超时。
  - 异常 guard：用户主动取消不用 FAILED 覆盖 CANCELLED。
- 测试：`tests/feishu/test_bs_card.py`（awaiting_patch 按钮 / confirm 清标志 / cancel 清标志）。

### bs_setup.py — bs 安装（待补）
- 职责：待补（bs 安装流程，README 仅列名）。
- 不变量：待补。

### bs_cmd.py — bs 命令（待补）
- 职责：待补。
- 不变量：待补。

### bs_workspace.py — 工作区（待补）
- 职责：待补。
- 不变量：待补。

### bot_manifest.py — bot 清单/权限常量
- 职责：bot 清单与权限常量。
- 不变量：`BOT_PATCH_PERMISSIONS` 已定义（patch 授权所需权限集），须被 setup 流程实际调用（旧版定义未使用，是 patch 授权缺失的根因之一）。

### bitable_helper.py — Bitable 维格表助手
- 职责：Bitable 相关操作。
- 易错点（bugfix 来源）：bitable_token/bitable_url 依赖 `bot-{bot_id}.json` 落盘；旧 bug 因文件名缺 `bot-` 前缀导致 `resume_provider` 读不到 bitable。

### accounts.py — 账号管理
- 职责：`Speaker`/`create_bot`/`save_account`/`list_accounts`/`rename_account`。
- 易错点（bugfix 来源）：`save_account` 落盘时机影响重试可续性；账号文件为 `bot-{bot_id}.json`。
- 测试：`tests/feishu/test_accounts.py`。

### botmgr.py — bot 管理（待补）
- 职责：待补（bot 生命周期管理，未见于 README/code-structure）。
- 不变量：待补。

### handler.py — 事件处理（待补）
- 职责：待补（README 列于通信层，推测为飞书事件回调处理）。
- 不变量：待补。

### groupmgr.py — 群管理（待补）
- 职责：待补。
- 不变量：待补。

### env.py — 环境命令（待补）
- 职责：环境命令 `init`/`stop`/`reset`/`status`（旧 code-structure 目录布局）。
- 不变量：待补。
- 待核实：与 commands.py `_do_stop()` 的归属（旧布局 env.py 独立，新平铺后命令可能已整合进 commands）。

### device.py — 设备信息
- 职责：`_machine_id`（读 /etc/machine-id 或 fallback MAC）、`_collect`（instance_id = SHA256(machine_id:hostname)[:12]）、`_save`（原子写 device.json）、`load`/`init`/`show`。
- 易错点：`show()` 直接 print + 设备未初始化时 `sys.exit(1)`——作 CLI 命令可，作库函数不合适（需 dict 版可拆）。
- 测试：`tests/feishu/test_device.py`。

### debug.py — 调试命令
- 职责：`echo`（交互循环 `/help` `/quit` `/exit`）、`simulate-dead`。
- 不变量：echo 在 interactive 模式调用（旧 frame/echo.py）。
- 测试：`tests/feishu/test_echo.py`。

### purge.py — 清理（待补）
- 职责：待补（清理命令，README 列于通信层/Provider 尾部）。
- 不变量：待补。

### utils.py — 通用工具（待补）
- 职责：通用工具（`TmpFilePair`）。
- 不变量：待补。
