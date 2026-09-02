# Status

> 工程：cogos（多 agent 运行时，飞书通信总线）。本体 `../cogos`。

## 当前状态

认知架构设计已定稿并深化（09-02）：`agent-prototype-design-v2.md`（完整自足版）整合了 v1 有效概念 + 09-01 晚 ~ 09-02 讨论结论。核心：**LLM 自管理上下文**（不做记忆系统，记忆 = 上下文的持久化/外溢）；cu = 覆盖式回合（循环到收敛，丢弃 cu_turn）；状态对象 context/intent/problem/gain；心智时间（语义判断交 LLM，留元层不进对象层）；scratch 草稿纸 + 目录 ID 化 + 脚注式引用与 cu 化展开；来源标注 sys/self/mem（进对象层）；对象层/元层分离；元层内省推/拉（[sys] 注入 + introspect）；张力驱动主题调度（未决项 = problem open 项）；模型分级（复杂度路由 basic/advanced）。**下一步进入实施**，顺序见「下一步」。

意识层细化第一期已实施完成并真实联调通过（`agent-impl-2.md`）：agent.json + profile.md 身份认知（含 pin）→ 幂等装卡/建联系人 → ToolRegistry + send_msg 工具 → 意识层接 LmClient（真实回复，oneshot 不续轮）→ 时间补齐 + 系统时间注入。全量回归 798 passed 无回归。

工具层扩展第一期已实施完成（`agent-impl-3.md`）：work_dir 边界 + read_file/write_file/execute 三外设工具，路径逃逸校验 + 二进制检测 + 超时 kill + 输出截断。全量回归 812 passed 无退化。真实 LLM 验证通过：不启动 agent，直接 LmClient + ToolRegistry 驱动三工具，read/write/execute 均正确调用并真实生效（`/tmp/kilo/verify_tools.py`）。

工具层扩展第二期已实施完成（`agent-impl-4.md`）：上网工具 search（Brave）+ fetch（Jina），aiohttp 显式代理 + 超时 + 截断 + 状态码语义。全量回归 831 passed 无退化。真实 LLM 验证通过：LLM 调 search 返回 asyncio 搜索结果、调 fetch 抓 example.com（`/tmp/kilo/verify_webtools.py`，需代理可用）。

真实账号联调成功（`checkpoint-5.md`）：唐钰 `COGOS002:A0005` 与 YZ `COGOS002:H0002` 多轮对话跑通，LLM 正确调 send_msg 工具回复。

代码已提交并推送 cogos 本体 `origin/master`：`14a3d01 feat(agent): add search/fetch web tools via aiohttp proxy`（含工具层第一期 read/write/execute + 第二期 search/fetch 全部改动）。工作区干净。

execute 三处 bug 已修并提交 `e3ed549 fix(agent): kill execute process group on timeout and stream-limit output`：进程组 kill + 流式限长 + 超时返回部分输出（带 timed_out/truncated）。全量回归 832 passed。

文档：

- `agent-prototype-design-v2.md` — 认知架构方案 v2，**完整自足设计主文档**（整合 v1 有效概念 + 09-01 晚 ~ 09-02 讨论结论：cu 覆盖式回合 / 状态对象 / 心智时间 / scratch 脚注引用与展开 / 目录 ID / 来源标注 / 元层内省与张力调度 / 模型分级）。读它即见全貌，不必翻别处。
- `agent-prototype-design.md` — 认知架构方案 v1，历史存档（场/意识层/推理 cu/元层/外设，`oneshot 不续轮`、`文档式结论` 已被 v2 推翻）。
- `agent-impl.md` — 架子实施交接（已完成）。
- `agent-impl-2.md` — 意识层细化第一期交接（已完成）。
- `agent-impl-3.md` — 工具层扩展第一期：读写文件 + 执行命令（已实施）。
- `agent-impl-4.md` — 工具层扩展第二期：上网工具 search/fetch（已实施）。
- `codebase.md` — 代码认知基线（phone / fake / lm_service / cog_runtime / agent 锚点）。

过程记录：`checkpoint-1.md`（认知节奏讨论）、`checkpoint-2.md`（架子实施）、`checkpoint-3.md`（reconnect 收消息 bug 修复）、`checkpoint-4.md`（真实入口 + 真实账号联调）、`checkpoint-5.md`（意识层第一期实施 + 真实联调）。

## 实施要点（给新会话）

- 新包 `cogos/agent/`：config / message / perception / consciousness / tools / webtools / app。
- agent 目录结构：`~/.cogos/agent/<name>/agent.json`（memory_dir/phone_dir 相对路径）+ `<memory_dir>/profile.md`（name/phone_number/pin/contacts）；`phone.json` 及 phone-data 自动生成在 `<phone_dir>/`，不混入 `~/.cogos/phone`。
- profile.md 的 `pin` 是真实装卡凭证（从 `~/.cogos/feishu/accounts/bot-<num>.json` 的 pin 取）；缺省用 `"pin"`（fake 下任意非空）。
- 真实启动顺序：`cogos-feishu init`（起 daemon+monitor，之前 systemd unit failed 需重跑 init）→ 起 lm-service server（127.0.0.1:11434）→ `LM_INTERNAL_KEY=ik_... python3.11 -m cogos.agent.app --agent <dir>`。
- internal_key 从环境变量 `LM_INTERNAL_KEY` 读；现成 key `ik_c47WkfAw7E5v6Ck8idMHgg`（deepseek/尾号b111）。
- 离线跑：`Agent(agent_dir, client_factory=FakeTelecomClient, lm_client=FakeLmClient)`；测试收消息用 `client.deliver(...)`。
- 关键坑：`add_card` 不幂等（`init_phone` 显式判断卡/联系人已存在）；消息 time 可能为空（感知层补 `chat.history()[-1].time`，兜底「未知时间」）；LLM 可能不调工具（system prompt 强制 + 无 tool_calls 兜底直发 source）。
- 工具层：ToolRegistry（name→schema+fn）；send_msg 参数 target(名字|号码)+content，失败回传 `{"ok":False,"reason"}`。外设工具 read_file/write_file/execute 由 work_dir 工厂生成，统一 `{"ok":bool,...}` 结构；read 截断 8000/二进制检测、write 自动建父目录、execute 30s 超时进程组 kill（`start_new_session`+`killpg`）+ 流式限长（stdout/stderr 各截断 4000 字节）+ 超时返回已捕获部分输出（带 `timed_out`/`truncated` 标志）。上网工具 search/fetch 由 webtools 工厂生成，key 从 `~/.secrets/{brave,jina}.key` 读、代理 `KILO_PROXY`（默认 127.0.0.1:10809）、aiohttp 必须显式传 `proxy=`。
- LmClient 契约：`chat(messages, *, ..., tools=[{name,description,parameters}])` → `{content:[...], tool_calls:[{id,name,args}], ...}`。
- 仍不碰 cog_runtime、不做群聊。

## 遗留（execute 外，待讨论设计，不随手改）

- 无取消/抢占：长命令一旦启动无法中断，只能等超时。
- 并发共享状态：多消息同时写 work_dir/memory 无锁，互相踩。
- 结果不回填/不总结：当前代码 oneshot 不续轮，工具结果不回喂 LLM。v2 已重新设计（cu 循环到收敛 + 覆盖式状态对象），此遗留随 v2 实施解决。
- 并发上下文隔离：加续轮时必须按消息隔离，否则 tool_call `id` 对不上报错。
- 同 sender 多消息回复乱序。
- LLM 调用无并发节流：多消息并发打后端，若有并发上限会爆。

## 下一步

设计已定稿（v2），进入实施。按 v2 §14 待定项，建议顺序（每步可验证）：

1. ~~工具层扩展第一期~~（已实施完成）。
2. ~~上网工具~~（已实施完成）。
3. **实施 v2 骨架**：状态对象 schema（`state.py`，context/intent/problem/gain + 心智时间标签，JSON 持久化）→ cu 循环（改 `consciousness.py`，oneshot → 循环到收敛，续轮消息拼接可复用 lm-service 的 `assemble_tool_messages`）。
4. **输出契约 + prompt**（改 `config.py` render_system_prompt：世界观+规则分离；最终输出 JSON，parse + schema 校验，失败重试一次再降级）。
5. **工具集**：scratch（草稿纸 + 版本化）、目录 ID 化（read/write/execute 加 dir 参数，替换 work_dir+_resolve）、翻聊天记录（chat_history）。
6. 之后：compact（特殊 cu + 受限工具集）、元层 cu（显著性/增益评估）、心智时间记账、模型分级路由。

新会话恢复：读本 status.md + `agent-prototype-design-v2.md` + `codebase.md` 即可，不必全量重读。

## 已封存（历史）

认知图设计探索 + 4K 聊天机器人 MVP 讨论，归档于 locus `projects/cogos/checkpoint/archive/26-09-01-cog-graph-sealed/`。
