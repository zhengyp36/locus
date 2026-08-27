# checkpoint-10 — proxy-search/proxy-fetch 去直抓 + fetch 接 Jina

## 当前问题

按 YZ 指示：把直抓从 kilo 工具里去掉，search 只走 Brave API、fetch 走 Jina Reader；真正直抓用命令行手动 curl 即可。

## 已做修改

- `~/.config/kilo/tool/proxy-search.ts`：
  - 删除 bing/ddg 直抓后端 + `parseBing`/`parseDuckDuckGo`/`decodeBingUrl`/`BROWSER_UA`。
  - 删除 `backend` 参数与 `Backend`/`BACKENDS`/`BACKEND_NAMES`，execute 简化为单 Brave 调用（`parseBrave` + `cleanHtml` 保留）。
- `~/.config/kilo/tool/proxy-fetch.ts`：
  - 直抓 curl 替换为 Jina Reader `https://r.jina.ai/<url>`，Header `Authorization: Bearer <key>`（key 读 `~/.secrets/jina.key`）。
  - `format` 参数映射 `X-Return-Format`（markdown 默认 / text / html）。
  - `-w '\n__JINA_HTTP__%{http_code}'` 提取状态码；401/402/429/4xx 显式返回错误（fail-closed，不回退直抓）。
  - 删除 `stripHtml`/`htmlToMarkdown`/`stripInline`。

## 验证

- `bun build --no-bundle` 两文件语法通过。
- 端到端（走代理）：Jina fetch example.com → `__JINA_HTTP__200` + markdown；Brave search → 返回 JSON 结果。

## 关键结论

- 两个工具均无直抓，直抓降级为手动 curl 命令行。
- fail-closed 只做到「错误显式返回」，**未做** `x-usage-tokens` 累计计数闸门（checkpoint-8 方案：本地落盘累计 + ~9M 停用 + 飞书通知），仍待落地。

## 遗留

- fetch/search 缓存未做（checkpoint-5 方案，TTL / JSON vs sqlite 待定）。
- Jina fail-closed 计数闸门未落地。
