# checkpoint-5 — 上网能力设计缺口 + 搜索工具修复

## 当前问题

cogos 设计提到"上网"但未说明方法；且本轮多模态调研触发搜索工具失效，暴露"上网"是基础设施缺口，需记录为遗留问题并先修搜索。

## 上网能力（设计缺口，遗留）

### 可选途径盘点

| 途径 | 机制 | 反爬 | 成本/延迟 | 通用性 |
|---|---|---|---|---|
| 直抓 HTTP | curl 抓 URL→HTML→清洗喂 LLM | 高 | 低 | 低（SPA 拿不到） |
| 搜索 API | Bing/SerpAPI/Tavily/Exa/Brave | 无（付费接口） | 中（付费） | 中（仅搜索） |
| 浏览器 DOM 自动化 | Playwright/Puppeteer/Browser-MCP，CDP+选择器 | 中 | 中 | 高 |
| 视觉上网（computer-use） | 浏览器 + VLM 看截图定位动作 | 中低 | 高（每步 VLM） | 最高 |

### 关键辨析（YZ 观点 + 收敛）

- YZ 定调：终极道路 = agent 像人一样访问网页/应用（GUI agent），"真人如何用 agent 就如何用"。业界同向：OpenAI Operator / Anthropic Computer Use / Google Mariner / 字节 UI-TARS / 智谱 AutoGLM。
- 收敛：反爬不会消失，会从"操作判断"迁移到"身份判断"，信号分层 = 网络身份(IP 信誉) / 客户端身份(浏览器指纹) / 行为信号(轨迹节奏) / 账号信誉(历史 cookie 实名)。"像真人操作"要连网络身份也像真人（住宅代理+真实指纹+真实账号）才成立；"没有反爬"是极限态非默认态，长期猫鼠博弈。
- 视觉的价值在通用性，不是反爬解药（反爬看 IP/指纹/行为，不看"懂不懂鸭子"）。

### cogos 定位

- 上网 = CogUnit/CogExecutor 的 tool 能力，是 code-as-action 从"受控 tool call"扩到"受控 GUI 操作"；LLM-Service 只负责多模态输入透传（图片）。
- 上网经验（怎么注册/用某应用/绕过）沉淀为认知树"方法论"节点（可自我修订）。
- 工程：上网能力抽象成 WebTool 接口（后端可替换：搜索 API → 浏览器 DOM → 视觉 GUI），复用 LLM-Service"真假可替换"原则。阶段 1 只打地基（WebTool 接口占位 + LLM-Service 图片输入），不实现视觉上网。
- 另有一正交项：网络出口（墙外需代理），与"上网方式"独立，同属基础设施。

### 多模态对 LLM-Service 结论

- 图片：各家最强，chat 接口直接吃图（OpenAI/Claude/Gemini/DeepSeek `deepseek-v4-flash-vision-exp`/Qwen-VL）。阶段 1 唯一硬需求。
- 声音：ASR(Whisper)+TTS 独立接口，不在 chat 里。
- 视频：几乎无 chat 接口直接吃视频（Gemini 仅少量帧）。
- 结论：LLM-Service 阶段 1 只做图片模态，请求/响应结构预留多模态 content 数组，声音视频后置。

## 搜索工具修复

### 根因

1. DDG 反爬（主因）：走代理抓 `html.duckduckgo.com` 返回 bot 验证码页（HTTP 202），`extractResults` 解析 0 条。
2. ensure 锁误报（偶发）：并发调用同时跑 `xray_wrapper.sh ensure`，`mkdir ensure.lock` 原子锁导致非持锁者返回 "another ensure is in progress"（return 1），被误报为"代理不可用：所有节点均无法连接"。

### 修复

- 后端 DDG → Bing：`https://www.bing.com/search?q=<query>&count=N`，Chrome UA 返回 HTTP 200 正常结果。
- Bing 解析：`<li class="b_algo">` 切块；标题 `<h2><a href>标题</a></h2>`；摘要 `<p class="b_lineclampN">`；真实 URL 从 href `u=` base64 参数解码，fallback `<cite>`。
- ensureProxy：对 "another ensure is in progress" 等待 3s 重试（最多 3 次）。
- 多后端可切换：`BACKENDS` 数组（bing → duckduckgo），`backend` 参数 auto/bing/duckduckgo，auto 按序自动回退（成功即返回，全部失败报"所有后端均失败"）。
- DDG 状态：不是代码废了，是当前代理出口 IP 被 DDG 拉黑（先 202 验证码，后升级为 000 连接超时，稳定 12s）。换环境/住宅 IP 可能恢复，故保留为 fallback。

### 共享 IP 拉黑根因（YZ 讨论后）

- 拉黑基于出口 IP：DDG 看到的是 `c33s4` 服务器 IP，非用户设备；电脑/手机都走 s4 出口故一起被拦，换 server（c33s1/s2/s3/s5/s8 各自独立服务器=不同出口 IP）即通。
- justmysock 是共享节点，**非每账户固定 IP**：一个账户挂 c33s1~s8 多个服务器，每节点 IP 被海量用户共享；"每账户固定 IP"指独享 IP/专线套餐，普通节点不是。
- 影响面：共享 IP 一人滥用全遭殃，机场出口 IP 信誉天然差，这是反爬信号里"网络身份"最硬的一层。
- 坑：`xray_wrapper.sh ensure` 健康检查用 ipinfo.io（对 s4 通），检测不出站点级拉黑（DDG 只拉黑 s4），故一直停 s4、看似健康实则对 DDG 不可用。
- 结论：换后端治标不治本，Bing 同样会被拉黑，只是时间问题。

### 并发加剧 + 分层根治

- 并发搜索 = 同一 IP 短时间多请求，最明显非人信号，加速拉黑 + 触发 ensure 锁误报。
- 分层根治：身份层独享/住宅 IP（根治）/ 接口层搜索 API（根治，付费 SLA 不拉黑）/ 抓取层 HTML+类人化（缓解）。
- 判断：搜索 API 是工程正解，接进 WebTool 可替换设计，HTML 抓取降为兜底。
- 待拍板落地项：① proxy-search 加随机延迟+串行锁 ② 结果缓存（短 TTL）③ 搜索 API 后端接进 BACKENDS（需选一家 + 申请 key）。

## 遗留 / 坑

- 上网能力 = cogos 设计缺口，进遗留（阶段 1 只做 WebTool 占位 + 图片输入）。
- 共享 IP 会持续被拉黑，换后端治标不治本；待 YZ 拍板落地项（随机延迟+串行锁 / 结果缓存 / 搜索 API 后端）。

## 搜索后端正解调研（08-27，YZ 已拍板）

### 结论

- **YZ 拍板**：搜索走正常路径（付费 API），不做白嫖抓取，减少拉黑风险；缓存可用。
- **选型首选 Brave Search API**：免费 $5/月（≈1000 次/月）每月自动发放、注册不绑卡；postpaid 超出才按 $5/1k 计费。
- 成本判断：1000 次/月做主力不够（本轮 20min 已耗 ~14 次 search+fetch），做「兜底 + 缓存后主力」够；超出少量付费（$5~10/月）可接受。
- 备选：Bocha 博查（国内免魔法、中文稳）、Exa（$10/月免费 + Contents 抓正文强）、Tavily（1000 credits/月）。

### Brave 关键机制（已核实）

- 注册无需绑卡：表单仅 email/password/name/company/来源问卷（`api-dashboard.search.brave.com/register`）。
- 免费 credits 每月自动发 $5；未用完是否滚存，官方页面未明说（措辞 "every month"，大概率月重置）。
- 响应头实时报用量：`X-RateLimit-Remaining`（本秒剩余, 本月剩余）/ `X-RateLimit-Limit` / `X-RateLimit-Reset`（可精确算恢复时间）。
- **只有成功请求才计数计费**（429 等失败不计费）→ 限流本身不产生费用，可当安全阀。
- 客户端可读 `X-RateLimit-Remaining` 做配额硬执行，对接 cogos 资源级元控制（预算+硬执行）。

### 缓存方案（待动手）

- **必须落盘**：Kilo 工具每次 execute 是独立进程，内存缓存无效。
- proxy-fetch：键 = `url + format`，TTL 1h（静态文档可 24h）。
- proxy-search：键 = `query + count + backend`（query 归一化：小写/去空格），TTL 5~15min。
- 介质：JSON 文件 `~/.cache/kilo/web-cache/{fetch,search}/<md5(key)>.json` 存 `{t, v}`，或用 sqlite。倾向 JSON（无新依赖、低并发、写冲突少）。
- 命中即返回，**跳过 ensureProxy**（最大收益 = 不发 curl + 不触发 xray ensure 并发）。
- 只缓存成功结果，错误/空响应不缓存（404 可选 5min 负缓存）。

### 已读代码

- `~/.config/kilo/tool/proxy-search.ts` — `BACKENDS=[bing, duckduckgo]`，auto 按序回退；解析 bing `b_algo` / ddg `result__a`；`ensureProxy` 对 "another ensure is in progress" 3s 重试。**当前无任何持久化/缓存，无付费后端**。
- `~/.config/kilo/tool/proxy-fetch.ts` — curl 抓取 + `htmlToMarkdown`/`stripHtml` 转换，`MAX_BYTES` 50k；`ensureProxy` 无重试。
- 缓存与付费 API 后端均未接入，是两个独立改造点。

### 下一步

1. 注册 Brave 拿 API key（免费档即可，不绑卡）。
2. `proxy-search` 的 `BACKENDS` 接 Brave（官方 API，替换白嫖抓取）+ 加缓存。
3. 待 YZ 定：TTL 具体值、JSON vs sqlite。
