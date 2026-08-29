# task-3 — lm-service 遗留三项

> 状态：待执行。工位 B 执行。自包含，干净会话读本文件 + `task-3-codebase.md` + 规格文档即可开工，无需工位 A 讨论上下文。

## 目标

搞定 lm-service 三项遗留：① internal_key 自带 base_url ② tool call 内部化 ③ 输出 content 归一 `content[]`。

## 前置

- 本体：`work/B/cogos`（clone 自 `git@github.com:zhengyp36/cogos-dev.git`）
- 记忆：`work/B/locus`（clone 自 `git@github.com:zhengyp36/locus.git`）
- 本文件位于 `locus/projects/cogos/tasks/task-3-lm-service-fixes.md`
- 代码认知：`work/B/checkpoint/codebase.md`（工位 B checkpoint 目录，**先通读，再动手**）
- 规格：`cogos/docs/design-lm-service-min.md`（冻结契约 2.3 / 响应归一 3.3）+ `design-cog-runtime-min.md`（4.x 与 lm-service 衔接）

## 契约钉死（防跑偏，先读后写）

### ① internal_key 自带 base_url（YZ 拍板方案 A）

- `LmClient.__init__(internal_key)`：**删 `base_url` 参数**。
- 服务端地址恒 = `http://{LM_SERVICE_HOST}:{LM_SERVICE_PORT}`（默认 `127.0.0.1:11434`，环境变量覆盖）。
- 上层只持 `internal_key` 句柄，不感知 lm-service 地址。
- 厂商 `base_url`（config 里 provider 级）**服务端已实现**（`resolve_internal_key` 返回 + `scheduler` 已用），本次不动。
- LmClient 测试指 fake 服务：靠环境变量 `LM_SERVICE_HOST`/`LM_SERVICE_PORT`，无需 fake LmClient 类。

### ② tool call 内部化（cogos 定规范，lm-service 组装厂商格式）

内部规范三块（`design-cog-runtime-min.md` 4.2）：

| 环节 | 内部形式 | lm-service 职责 |
|---|---|---|
| 工具集输入 | 结构化 schema（JSON Schema 等价） | 组装厂商 `tools` 格式（OpenAI 兼容 `{type:"function", function:{name, description, parameters}}`）|
| tool_calls 输出 | `[{id, name, args: dict}]` | parse `arguments`（JSON 字符串→dict）+ 归一统一 id |
| 结果回填 | `[result]`（按位置对应） | **归 cu**（lm-service 不维护对话、不补 id）|

钉死细节：

- `chat()` 加可选 `tools` 参数；`handler.py` 白名单加 `"tools"`。
- `tool_choice` 最小版**不传**（厂商默认 auto）；`strict` 字段**实施时确认 deepseek 是否支持**——支持才补，不支持则透传 schema 原样不强行补。
- 输出归一：`message.tool_calls` 提取 `{id, function:{name, arguments(str)}}` → `[{id, name, args: dict}]`；`arguments` parse 失败 → `LmServiceError(semantic)`（响应结构异常）。
- `finish_reason == "tool_calls"` 但 tool_calls 空 → `LmServiceError(semantic)`。
- `content` 与 `tool_calls` 并列可选，判续轮只看 `tool_calls`（上层 cu 判，lm-service 只透传）。

### ③ 输出 content 归一 content[]

- 输出 `content` 从 str 改 **list（消息数组，对称输入 material）**。
- 归一规则：`content` 为 string `"x"` → `[{"type":"text","text":"x"}]`；为 null/空 → `[]`；已是数组 → 原样透传。
- `CuResultOk.content` = done 轮 content（list）；完整历史走 `on_done(result, material)` 的 material 参数，两者正交。
- `recorder.py` / `scheduler.py` 记录 content 随之改（记录归一后的 list）。

### 契约变更显式声明

以上三处是**工位 A 拍板 + YZ 拍板的契约扩展**，非工位 B 擅自改。task-1 的「冻结契约」指 `LmClient.chat → 归一响应 + LmServiceError(category)` 的形状不变，本次只在形状内扩展字段（加 `tools` 入参 / 加 `tool_calls` 出参 / `content` 变 list）。**实施中若发现需改形状本身 → 停下，回工位 A 讨论。**

## 轮次清单（每轮：实现 → 验证 gate → 记 checkpoint → 通知 /undo）

| 轮 | 内容 | 验证 gate |
|---|---|---|
| 1 | ① 删 `LmClient` base_url 参数，服务端地址走环境变量/默认 | 现有 pytest 绿 + LmClient 构造签名无 base_url |
| 2 | ③ `parse_response` content 归一 list + recorder/scheduler 记录改 | mock 归一绿 |
| 3 | ② `tool_calls` 归一输出（parse arguments + id + finish_reason 校验）| mock tool_calls 归一绿 |
| 4 | ② `tools` 输入组装厂商格式（deepseek/openai）+ 白名单加 tools | mock 组装绿 |
| 5 | 全量回归 + 调试记录字段补齐 | 全量 pytest 绿 |

**停下点（轮 5 之后）**：真实 tool call 验证（deepseek 是否同构 openai 格式、arguments 真实 parse）需真实 api_key。**AI 不擅自获取/试账号**，mock 全绿后停下，飞书通知 YZ。

## 工程规范（防走偏）

- 三层命名 / 三文件对齐 / category 字符串枚举 / 错误响应格式沿用 task-1，见 `task-3-codebase.md`「关键约定」。
- mock patch 目标：`scheduler.PROVIDER_REGISTRY`（或 `ProviderBase.chat_completion`）。
- 改动最小化：不动 `config.py` 服务端 base_url 逻辑、不动 `router.py` 模态推断（tool 不改变模态推断——工具是 chat 语义，非模态）。

## checkpoint 工作法（精简）

- 每轮结束写 `../checkpoint/`（工位 B 自己的 `work/B/checkpoint/`）：`status.md` + 本轮 `checkpoint-N.md`（锚点优先，凝练可恢复）。
- 结构：当前问题 / 已做修改 `文件:行` / 关键结论 / 遗留坑。
- 每轮 `status.md` 显式写「下一轮：读规格第 X 节 + 代码认知 Y 锚点」。
- 轮结束飞书通知 YZ 执行 `/undo`，新轮读 `status.md` 恢复。
