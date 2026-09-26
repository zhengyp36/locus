# screenlab 工作规则与操作（稳定参考）

> 由 #37/#38 会话整理。**每个新会话先读本文件**；它不随 handoff 换代而丢。
> `handoff-screen-*.md` 只引用本文件，不重复规则。

## 纪律（YZ 定，务必沿用）

- **10 分钟闹钟**：动手前 `set_timer`（600s）。到点停下做两件事：
  ① 对照 `spec-screen-1.md §0.0` 查是否**偏航**，偏了就拉回；
  ② `/home/zhengyp/work/A/locus/tools/ctx.py` 查上下文，**≥150K 或逼近就自动交接**（见《自动交接与 attach》）；查完再设下一个。
- **YZ 在场讨论时不用闹钟**（并取消已设的）。
- **每完成一步** → 通知 YZ（`/home/zhengyp/work/A/locus/tools/feishu_notify.py`），**不等回复、立即下一步**。
  - ⚠️ 文本里含**双引号**会破坏参数解析 → 用**写文件 + stdin**：`feishu_notify.py - < msg.txt`。
- **命令走 `terminal_exec`（非阻塞，等唤醒事件）**；**不要用 `sleep` 结束命令**（被 YZ 纠正过的错）。预计 >5s 的不阻塞等待。
  - 长命令中途要回看进度/偏航，用 `terminal_notify(id, N)` 设**一次性唤醒**（命令仍在跑就在 N 秒后唤醒一次；命令结束也会发完成事件）——**不要用 `sleep` 干这事**。要多次醒来就每次重新 arm。
  - 终端管道若被后台进程持有 stdout 会**永久 busy**：`surface run` 已改走 `systemd-run`（即时返回、不持有），`clip` 写已重定向 stdio。若仍 busy，`terminal_cancel` 后另开。
- **裁决按目标，不甩锅给人**：只从 `spec-screen-1.md §0.0` + 易用性推；**能推的自决并记录**（先例：默认禁用 `--no-sandbox`）。
  - **裁决者是目标，不是 YZ**：只要有目标导出，就自决，**不得因"人可能有偏好"改问 YZ**；分歧也是拿目标论，不是拿人压。
  - **只在目标真不清时才升级**：判据 = §0.0 对该点无可导出，且不裁决就动不了 → 飞书通知 YZ 后**不空等**，转做不阻塞的（另一平台/另一子问题）；**全部阻塞**才停下等人（YZ 2026-09-26 定）。
  - 升级时写明：**卡在哪、§0.0 为何推不出、我倾向什么**。
- **提交**：默认不 `commit` / 不 `tag`。本阶段（screenlab 整合）**YZ 已授权过程中 commit/push**（`origin`），但**不 tag**；提交前先跑测试。（2026-09-26 YZ 定）
- **图不进上下文（针对图的数据，不是针对附件）**：进来的必须是**附件**（attachment，只在当次有效）；**图的数据**（像素/base64/文本化）**不得**直接进上下文——无意义且永久滞留、污染会话（#61 因此被删）。
  - 看图的正确方式 = **附件**；交接/引用图**只给路径**（如 `../checkpoint/tools/blobs/xxx.png`、`/tmp/kilo/xxx.png`），要人看就报路径。
  - 确需模型看图时用附件，并尽量裁剪/缩小。

## 自动交接与 attach

会话活在常驻 `kilo serve :4097`（`kilo-resident` 的 `residentctl.sh` 管）；**TUI 只是 viewer**——人随时 `attach-kilo` 接上看，attach 退出不影响会话（session 数据持久，可 resume）。

**交接 = 当前会话自己起后继，不等 YZ**：
1. 写 `handoff-screen-NN.md`：正文 + "给新会话的第一句话" 放**单个围栏代码块**（机器可取用，别掺别的）。
2. 就地更新滚动状态（`screen-assist-status.md` / `*-progress.md`）。
3. **交接即封笔**——本会话此后**不再处理任何异步事件**；交接前必须**主动关闭/转移所有属于本会话的异步事件源**，否则旧会话被自己的源叫醒、和后继抢着干。停干净后旧会话自然停在 idle、不再前进。
   - **session 内**：取消所有 pending timer（`list_timers`→`cancel_timer`）；关掉所有 terminal（`terminal_list`→`terminal_cancel`/`terminal_close`）；停掉所有 `background_process`；确认无挂起的 `terminal_notify`。
   - **bridge 侧（最易漏）**：该工程的飞书 bot / session pin（`state.json` 的 `sessions[bot]`）若仍指向旧会话，**飞书入站会唤醒旧会话**——须改指到后继（Feishu `/pin`，或走下面更优的建会话路径）。bridge `inbox` 里若还有本会话待派发事件，一并清掉/确认已消费。
   - **兜底**：交接后若仍被唤醒，开头先判"本会话已交接"，立即停止并把事件转给后继，不再干活。
   - **更优路径（避免手工 pin）**：让 bridge 走它的 `/new` 建新会话并注入首句——bot 绑定自动跟到后继，不产生"旧会话仍被飞书唤醒"。当前 bridge 未把 `/new`/pin 暴露为 control API，要自动做到这点需补一个端点（改代码）。
4. 自己起后继会话（`background_process` fire-and-forget，别阻塞本会话）：
   ```bash
   kilo run --attach http://127.0.0.1:4097 -u kilo -p kilo \
     --dir /home/zhengyp/work/A/locus --title "screenlab #NN" \
     "<handoff 第一句话原文>"
   ```
   不带 `-s` = 新 session；`-c` 续最近；`--dir` 必须显式给（attach 默认用 server cwd）。
5. 飞书通知 YZ：**已交接 + 新会话 title**（即 `--title` 的值，如 `screenlab #NN`）+ 如何 attach 旁观（`attach-kilo <session-id>`；`/sessions` 或 `kilo session list` 可按 title 找到）。标题先定好再起后继，保证通知里报的就是它。

- **异步唤醒与 sink（别误解）**：会话本身**不会自己跑**，只被 prompt 推动——attach 的 TUI 里有人在推/在看，就**不会自停**。bridge 的 sink 策略（AC4）只决定"要不要把异步事件自动注入一个**空闲**会话"，且任何唤醒源（`set_timer` / `terminal`）**创建时就 `markWatched`**（TTL 1h），正常都能唤醒。
  - 唯一会被压住的情况（窄）：唤醒源创建后 **>1h 才触发**（超长 timer / 超长命令且期间无 notify）→ 该次唤醒被压，只飞书通知 YZ（bot 无 `lastChatId` 还会静默）。
  - 对策：定时/交互控制在 ≤1h 内续 TTL，别设 >1h 的 timer 单独指望它；旧会话交接前照旧停掉自己的唤醒源（避免旧会话被自己的 timer 叫醒）。
- **权限**：后继会话**不得 `--auto`**——提交/推送/动目标仍走上方裁决（目标推不出就飞书升级后停）。全量放行只允许在窗口内由 YZ 显式开。
- **防失控**：链式交接设上限（连续 N 次无人应答即停并通知），别空转烧 token。
- **人 attach**：`attach-kilo`（`~/.local/bin`）或 `kilo attach http://127.0.0.1:4097 -u kilo -p kilo --dir <proj>`；`kilo session list --format json` 查在场 session。

## 判据与验收

- 一切从**目标 §0.0** 推；不从代码、不从"谁定的"推。
- **不用仓库自己的 e2e 当验收**（`roles_e2e` / `tool_loop_e2e` 是我们写的 = 自证）；以 agent 身份、只用文档公开入口真用，用 `import -window root` 抓屏做**地面真值**对照。

## 环境与操作

- **固化脚本优先**：`cogos/screenlab/tools/`（2026-09-26 整合期从 `../checkpoint/tools/` 归位；用法见其 `README.md`）。靶机地址/账户/坐标/密钥/部署/状态全在那里，`source env.sh` 后用 `sl_*` helper；**不要每会话重敲长命令或"找密码"**。新会话第一条：`tools/snapshot.sh`（一条命令拿到 repo + 靶机状态）。`../checkpoint/tools/` 为旧副本，勿再改（以 cogos 为准）。
- **靶机** `surface-centos-9`（100.100.137.78）。测试账户是环境事实，可删可重建，规则不绑死——用时先查 `loginctl list-sessions` + `who`（当前 = `human`, uid 1002, display `:0`）；`tools/env.sh` 里存当前值。
- **宿主 VBox（救机）**：`ssh zhengyp@100.112.50.115`（Windows；`VBoxManage.exe` 在 `C:\Program Files\Oracle\VirtualBox\`，ssh 里须全路径），`VBoxManage controlvm centos9 reset`。输入模拟**只有键盘**（`keyboardputscancode`，guest 内=物理），无鼠标。
- **root / 账户 / 部署 / 取文件**：一律走 helper——`sl_root`（单命令）、`sl_root_script`（多行 root 脚本）、`sl_remote_vars`（human 会话 env + `run` 包装）、`sl_pull`（把靶机文件拉回 `tools/blobs/`）。部署 = `tools/deploy.sh`；抓屏 = `tools/desktop.sh shot`。
- 本机 `python3` = 3.9（`cogos/feishu/config.py` 用 `X | None` 跑不了），一律 `/usr/bin/python3.11`。
- 已知噪声：sshd X11 转发占 TCP **6010/6011**（`zhengyp@pts/*` 的 `ssh -X`，**别杀**——这正是 F1/F1b 的诱因）；`vboxclient.service` 无限重启（与 screenlab 无关）。
- 靶机屏幕会 DPMS 熄灭/锁屏 → `xset s off -dpms` + XTEST 键唤醒；锁屏用 `loginctl unlock-session 3`（root）解开后抓屏。
