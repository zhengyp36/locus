# checkpoint-6 — Brave 搜索 API 接入 + fetch 问题定性

## 当前问题

search 走白嫖抓取（bing/ddg）因共享 IP 被拉黑，根治需付费 API（YZ 已拍板）；注册 Brave 并接入 proxy-search。

## Brave 结论（已打通）

- 注册完成，key 存 `~/.secrets/brave.key`（32 字节，BSA 前缀；全程未在日志暴露）。
- 端点：`GET https://api.search.brave.com/res/v1/web/search?q=<query>&count=<n>`；Header `X-Subscription-Token` + `Accept: application/json`。
- 直连 `api.search.brave.com:443` 超时（被墙），走代理 `http://127.0.0.1:10809` 成功。
- 免费档（YZ 从 dashboard 确认）：**50 req/s + 每月不限次数**，多 key 共享同一限额。
- 响应头：`x-ratelimit-limit: 50, 0` / `x-ratelimit-policy: 50;w=1, 0;w=2678400`（秒级窗口 w=1 限 50；月度窗口 w=2678400 秒 limit 0 = 不设限）。
- 影响：月度无限 → 缓存"省配额"动机失效，只剩"减请求/省延迟/防撞 50/s"；50 req/s 仍是硬限制。

## 接入 proxy-search（已完成）

改 `~/.config/kilo/tool/proxy-search.ts`：

- 加 `braveKey()`：`fs.readFileSync` 读 key，缺失返回 null。
- `Backend` 接口加可选 `headers?: () => Record<string,string>`。
- 加 `parseBrave`：`JSON.parse` → `web.results`（空则 fallback `discussions.results`）→ title/url/description，snippet 过 `cleanHtml`（Brave description 是 HTML 片段，需清洗）。
- `BACKENDS` 首位加 brave（auto 默认 brave 优先），bing/ddg 保留 fallback。
- execute 循环：brave key 缺失时 push error 并 continue；动态 headers 构造 curl `-H` 参数。
- description 后端列表更新为 brave / bing / duckduckgo。

验证：端到端模拟（读 key → curl 走代理 → parse）返回干净结构化结果；`parseBrave` + `cleanHtml` 对 snippet 清洗正确。

## fetch 问题（定性，未实施）

- Brave 只解决 search，无"抓取任意 URL 正文"端点（仅 web/image/video/news search + suggest/spellcheck）。
- fetch 可选：直抓（现状，共享 IP 会拉黑）/ 正文抽取 API（Jina Reader `r.jina.ai/<url>` 免费、Tavily Extract、Exa Contents）/ 浏览器 DOM 自动化 / 视觉上网（均后置）。
- 待 YZ 定 fetch 方案。

## 遗留 / 坑

- 缓存未做（月度无限后动机弱化；待 YZ 定 TTL 值、JSON vs sqlite）。
- fetch 方案未定。
