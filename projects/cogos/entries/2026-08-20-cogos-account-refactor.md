# 2026-08-20 — agent 账号本地特有字段去留 + 修改思路

与 YZ 讨论：`bot-{provider}-{number}.json` 有四个云端 agent_registry 没有的字段，属设计债。原则：没用就删，有用且可重建就重建，有用且不可重建才进云端。

## 四字段去留

| 字段 | 用途 | 结论 |
|---|---|---|
| bitable_token | Contact 通讯录 token，`_write_contact` 写 / `query_contact_chat_id` 读 | 有用+可重建：app_id/app_secret 列 agent 名下 bitable 匹配 `{number}-Contact`，不持久化、按需重建 |
| bitable_url | 仅展示（agent 场景代码不读，人想打开文档） | 派生值，删存储，用 `core.url.bitable_page(tenant_key, token)` 现算 |
| open_id(agent 自身) | 仅 `session.py:584` 填 `MessageSent.sender.open_id` | 基本没用，删（sender 留空安全） |
| patch_granted | 仅 `add_agent` resume 幂等（跳过重复 patch 授权） | 删（飞书 OAuth 重复授权幂等无害） |

注意区分：agent 账号文件的 open_id（自身身份，没用）≠ Contact bitable 里 contact 表的 open_id（peer 身份，有用，是 bitable 数据不是账号字段）。

## 修改思路（四块）

1. 新增重建函数 `find_contact_bitable(app_id, app_secret, number) -> str`：列 agent 名下 bitable 匹配 `{number}-Contact` 返回 app_token。放 `bh` 或 `bs_agent`。
2. 删字段（写入点 + 保留点一起）：
   - `add_agent` 241-251 删 open_id 写入（open_id 变量保留，仍传 `_configure_admin_bot`）
   - `add_agent` 269-272 删 patch_granted（含 216-229 resume 读判断）
   - `add_agent` 298-303 删 bitable_url
   - `refresh_agent_account` 420-434 删 open_id/patch_granted 的 `local.get(...)` 保留行
3. token 读取点改「缺失即重建」：`activate_agent` 511-516、`refresh_contact` 770-775、`query_contact_chat_id` 热路径；token 稳定，重建后写回本地缓存。
4. 展示点用 `bitable_page` 现算 url。

## 建议顺序

1. 先删 open_id/patch_granted/bitable_url（纯减法）
2. 再上重建函数 + token 读取点（重点测 activate/refresh/p2p 发送）
3. 最后 `term.py` `_load_pin` 改 `await AgentRef(...).ensure()`，清 `bs_agent` 读 agent 账号的 load_bot 错位点

## 关键待查证点

- 飞书「列某 app 名下 bitable」API 的鉴权（app token vs tenant token）。若不可行，bitable_token 改走进 agent_registry（云端）。
- tenant 字段保留（provider 层可拿，不算本地特有）。

## 验证

现有 459 测试需跑，activate/refresh 相关测试可能要随删字段调整。
