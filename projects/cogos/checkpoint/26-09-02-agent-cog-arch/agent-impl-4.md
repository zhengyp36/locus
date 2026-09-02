# agent 工具层扩展（第二期）—— 上网工具 search / fetch

> 状态：已实施（真实 LLM 验证通过，代码已提交 cogos `14a3d01`）。
> 目标：给 agent 补「眼」——搜索（Brave）与抓取（Jina），让它在对话里能查资料、读网页。
> 架构主文档：`cogos/docs/webtool-design.md`（定位/三方式/阶段）。前一期：`agent-impl-3.md`（读写文件 + 执行命令）。代码认知：`codebase.md`。
> 参考实现：kilo 工具 `~/.config/kilo/tool/proxy-search.ts` / `proxy-fetch.ts`（Brave/Jina 调用细节照搬其语义，Python 化）。

## 目标与效果

- **离线（fake）**：注入一条消息 → LLM 可调用 `search` / `fetch`，工具返回结构化结果（`search_web`/`fetch_url` 被 monkeypatch 掉，不真发网络）。
- **真实**：与 agent 聊天时它能 `search` 查网页、`fetch` 读指定 URL 正文，结果作为 tool 返回给 LLM。验证走「不启动 agent」路径（起 lm-service server + LmClient + ToolRegistry 直连，见 codebase.md 真实部署段），需代理可用。

## 明确边界（不做）

- **不做真实身份访问**（agent 账号 cookie / 浏览器 DOM / 视觉 GUI）——webtool-design 的终极方式，后置。
- **不做缓存**、**不做 Jina fail-closed 计数闸门**（kilo 遗留项，本期不搬）。
- **不做图片输入**（多模态是 LLM-Service 的活，不在工具层）。
- 不做 ASR/TTS、视频。
- 不碰 cog_runtime。

## 配置 / 密钥

- Brave key：`~/.secrets/brave.key`，环境变量 `BRAVE_API_KEY` 可覆盖。
- Jina key：`~/.secrets/jina.key`，环境变量 `JINA_API_KEY` 可覆盖。
- 代理：读环境变量 `KILO_PROXY`，默认 `http://127.0.0.1:10809`。代理的「确保可用」（起 xray 等）是正交基础设施，由外部负责，工具层不调 ensure。

## 文件改动

```
cogos/agent/webtools.py    # 新增：search_web / fetch_url 两个 async 函数（HTTP 传输 + Brave/Jina 调用，可替换后端）
cogos/agent/tools.py       # 改：加 make_search_spec / make_fetch_spec 两个工厂（schema + 调 webtools）
cogos/agent/app.py         # 改：ToolRegistry 注册 6 个工具（send_msg/read_file/write_file/execute/search/fetch）
cogos/agent/consciousness.py # 改：toolset_names 默认改为六个工具名
cogos/agent/config.py      # 改：render_system_prompt 工具清单补 search/fetch 两行
```

依赖单向保持：`webtools` 只依赖 aiohttp + 标准库 + 密钥路径，不 import 其它 agent 层；`tools` 的 search/fetch 工厂只依赖 `webtools` 的两个函数。

## 接口契约

### webtools.py（两个 async 函数，返回统一 `{"ok": bool, ...}`）

```python
import aiohttp
from pathlib import Path

MAX_FETCH_SIZE = 50000      # fetch 正文截断字符数
SEARCH_TIMEOUT = 20.0       # Brave 超时（秒）
FETCH_TIMEOUT = 60.0        # Jina 超时（秒）
DEFAULT_PROXY = "http://127.0.0.1:10809"

async def search_web(query: str, count: int = 10, *, proxy: str | None = None) -> dict
async def fetch_url(url: str, fmt: str = "markdown", *, proxy: str | None = None) -> dict
```

`proxy` 缺省从 `KILO_PROXY` 环境变量取，再兜底 `DEFAULT_PROXY`。

**返回结构**：

- `search_web` 成功：`{"ok": True, "results": [{"title": "...", "url": "...", "snippet": "..."}, ...], "count": N}`
- `search_web` 无结果：`{"ok": True, "results": [], "count": 0}`（工具执行成功只是没结果，让 LLM 判断）
- `search_web` 失败：`{"ok": False, "reason": "..."}`（无 key / 网络 / HTTP 非 2xx）
- `fetch_url` 成功：`{"ok": True, "url": "...", "content": "...", "format": "markdown", "size": N, "truncated": false}`
- `fetch_url` 失败：`{"ok": False, "reason": "..."}`（无 key / 401 / 402 / 429 / 网络 / 空正文）

### tools.py（两个工厂，无参数）

```python
def make_search_spec() -> ToolSpec
def make_fetch_spec() -> ToolSpec
```

factory 内 fn 直接调 `webtools.search_web(...)` / `webtools.fetch_url(...)`，结果原样返回（已是 `{"ok":bool,...}`），异常兜底仍由 `ToolRegistry.call` 捕获。

### schema（给 LLM 看，description 中文，与既有工具一致）

```python
# search
{"name": "search", "description": "搜索网页，返回标题/URL/摘要列表（走 Brave Search API）",
 "parameters": {"type": "object",
   "properties": {"query": {"type": "string", "description": "搜索关键词，中英文均可"},
                   "count": {"type": "number", "description": "返回结果条数，默认 10，最大 20"}},
   "required": ["query"]}}

# fetch
{"name": "fetch", "description": "抓取一个网页 URL 的正文，返回清洗后的 markdown（走 Jina Reader）",
 "parameters": {"type": "object",
   "properties": {"url": {"type": "string", "description": "要抓取的网页完整 URL"},
                   "format": {"type": "string", "description": "返回格式：markdown（默认）/ text / html"}},
   "required": ["url"]}}
```

## 关键实现细节（坑，务必照做）

1. **代理必须显式传**：直连被墙。aiohttp 默认 `trust_env=False`，**不会**读 `http_proxy` 环境变量，必须在 `ClientSession` 或 `session.get(..., proxy=proxy)` 显式传 `proxy`。proxy 解析：`proxy = proxy or os.environ.get("KILO_PROXY") or DEFAULT_PROXY`。

2. **Brave 请求**：
   ```python
   url = f"https://api.search.brave.com/res/v1/web/search?q={quote(query)}&count={n}"
   headers = {"Accept": "application/json", "X-Subscription-Token": key}
   # n = min(max(int(count), 1), 20)   # clamp 1..20
   ```
   响应 JSON：优先 `data["web"]["results"]`，为空则 `data["discussions"]["results"]`。每条取 `title` / `url` / `description`（snippet）。

3. **HTML 清洗**（title/snippet 里常带 `<b>`、`&amp;` 等）：移植 kilo `cleanHtml` 逻辑——去标签 + 解 `&amp; &lt; &gt; &quot; &#x27; &nbsp;` + `&#xNN;`/`&#NN;` 数字实体 + 压缩空白。做成 `_clean_html(text)`。

4. **Jina 请求**：
   ```python
   headers = {"Authorization": f"Bearer {key}"}
   if fmt != "markdown": headers["X-Return-Format"] = fmt   # text / html
   resp = await session.get(f"https://r.jina.ai/{url}", headers=headers, proxy=proxy)
   ```
   注意 Jina 的 `fmt` 只能是 markdown/text/html 三值之一，其余回退 markdown。

5. **Jina 状态码语义**（用 `resp.status` 判断，比 kilo 的 `curl -w` 干净）：`401` → `{"ok":False,"reason":"jina 401: invalid api key"}`；`402` → 余额不足；`429` → 限流；其它 `>=400` → reason 带 status + body 前 500 字符。非 2xx 一律 `ok:False`。

6. **fetch 截断**：`text = await resp.text()`，`content = text[:MAX_FETCH_SIZE]`，`truncated = len(text) > MAX_FETCH_SIZE`，`size = len(text)`。空正文 → `ok:False`。

7. **超时**：Brave `aiohttp.ClientTimeout(total=SEARCH_TIMEOUT)`，Jina `total=FETCH_TIMEOUT`。`aiohttp.ClientError` / `asyncio.TimeoutError` → `{"ok":False,"reason":"network/timeout: ..."}`。

8. **key 读取**：`_read_key(path, env)` → `os.environ.get(env)` 优先，否则读文件 `strip()`，文件缺失/空返回 `None`。`None` → `{"ok":False,"reason":"no brave/jina api key"}`（不抛断）。

9. **aiohttp session 生命周期**：每个调用内 `async with aiohttp.ClientSession(timeout=...) as session:`（与 lm_service/client.py 同款），不跨调用复用 session。

10. **toolset_names 默认**改为 `["send_msg", "read_file", "write_file", "execute", "search", "fetch"]`；`render_system_prompt` 工具清单补：
    ```
    - search：搜索网页
    - fetch：抓取网页 URL 正文
    ```

## 测试

照现有范式（`monkeypatch aiohttp.ClientSession`，见 `tests/lm_service/test_errors.py:160-184`）：

1. `test_webtools.py`（新增）：
   - `search_web`：正常解析（web.results）→ ok:true + 3 字段；HTML 清洗（`<b>x</b>&amp;`）；web 空回退 discussions；count clamp（0→1、99→20）；无 key → ok:false；HTTP 非 2xx → ok:false。
   - `fetch_url`：正常 markdown + size/truncated；truncated（>50000 字符）→ truncated:true；401/402/429 → ok:false + 对应 reason；空正文 → ok:false。
2. `test_tools.py` 补：
   - `make_search_spec` schema（name/description/required）；fn 透传（monkeypatch `webtools.search_web` 返回固定 dict）。
   - `make_fetch_spec` schema + 透传。
3. 全量回归 `python3.11 -m pytest tests/ -q` 无退化（基线 812 passed）。

测试通过 monkeypatch `webtools.search_web` / `webtools.fetch_url` 或 `aiohttp.ClientSession`，不真发网络。

## 完成标准

`Agent(agent_dir)`（fake）deliver 一条消息 → LLM 收到含 6 个工具 schema 的 `chat(tools=...)`；离线（monkeypatch）下 LLM 调 `search`/`fetch` 得到结构化结果。pytest 通过 + 全量无回归。

真实验证（可选，需代理可用）：起 lm-service server，LmClient + ToolRegistry 直连，让 LLM 调 `search`/`fetch` 真发网络，断言结果结构。代理由外部保证（`KILO_PROXY` 或 kilo 已起的代理）。

## 风险评估（结论：可进入开发）

| 风险 | 级别 | 对策 |
|---|---|---|
| 直连被墙，忘显式传 proxy | 高 | 必须显式 `proxy=`，不靠 trust_env |
| fetch 大页面撑爆上下文 | 中 | MAX_FETCH_SIZE 截断 + truncated 标记 |
| Brave/Jina key 泄露进日志 | 低 | key 只读内存，不进 schema/日志 |
| 真实网络不稳定影响 CI | 低 | 测试全走 monkeypatch，不真发网络 |
| 工具集默认改动影响既有测试 | 低 | 集中改 app.py + consciousness 默认，测试随契约更新 |

无阻塞性风险；坑均已列明，可直接进入开发。
