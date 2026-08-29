# checkpoint-5 — 轮 5：调试 jsonl 落盘 + admin calls 子命令

## 当前问题

服务端调试记录：每次调用 append 一行 jsonl 到 `~/.cogos/lm-service/calls.jsonl`（16 字段），并新增 `admin calls` 子命令做投影/过滤/计数/导出，方便人工定位（base64 图刷屏问题）。

## 已做修改

- `cogos/cogos/lm_service/recorder.py`：新建。`now_iso()` / `build_entry(**kw)`（16 字段固定顺序，status 必填其余可空）/ `CallRecorder.append`（mkdir + 单行 `json.dumps(default=str)` append）/ `read_calls`（逐行 parse，坏行跳过）。
- `cogos/cogos/lm_service/config.py`：加 `Config.calls_path` property（`self._dir / "calls.jsonl"`）。
- `cogos/cogos/lm_service/scheduler.py`：`Scheduler.__init__` 建 `CallRecorder(config.calls_path)`；新增 `_record(started, ik_id, body, ...)` 抽公共字段；`submit` 包 try/except，成功（status=ok）与 `ProviderError`（error_category=str(category)）与兜底 `Exception`（semantic）都落盘后 re-raise。
- `cogos/cogos/lm_service/admin.py`：新增 `calls` 子命令 + `_parse_ts`/`_entry_ts`/`_match`/`_cmd_calls`。参数 `--from/--to`（ISO 或 epoch）/`--limit`/`--offset`/`--fields`/`--filter key=value`（可重复）/`--count`/`--out`。`--count` 在 limit/offset 之前统计；输出 JSON 数组（indent=2）。

## 已读代码要点

- `handler.py:45-85`：验证/字段校验在 `scheduler.submit` 之前 return；`scheduler.submit` 是唯一进入 provider 的实际调用路径。
- `scheduler.py:114-137`（旧）：`submit` 无 try/except，错误直接抛到 handler；provider/model/selection 都在此作用域内 → 落盘点选这里字段最全。
- `providers/base.py:112-122`：`parse_response` 返回 `{content, finish_reason, usage, reasoning, raw}`，`usage` 已归一 `{prompt_tokens, completion_tokens}`。

## 关键结论/决策

- **落盘点 = `Scheduler.submit`**（非 handler）：provider/model/routed_tier/degraded/content/finish_reason/usage 全在，16 字段一次凑齐。handler 前置校验失败（缺字段/非 JSON/缺 key）**不落盘**——未到 provider、无 provider/model，HTTP 响应已带 category，记录无增量价值。
- **`ts` 存 ISO 字符串**（人类可读），`--from/--to` 支持 ISO + epoch 两格式（`_parse_ts` 先试 float 再试 `fromisoformat`）。
- **`--filter` 布尔用 `str(v).lower()==expected.lower()`**，字符串/数字用 `str(v)==expected`，避免 `--filter degraded=true` 撞 `"True"`。
- **`status` 取值 `ok`/`error`**；`error_category` 成功为 null。错误落盘后 re-raise，不改原控制流。

## 遗留/坑

- **gate 通过**：round5_gate.py 全绿（scheduler 成功/错误各 1 行字段齐全 + admin calls 的 count/fields/filter/out 全可用）+ 全量 pytest 668 passed 无回归。
- **正式 pytest 在轮 10**（mock 调试记录），本轮只 /tmp 脚本 gate。
- `build_parser` help 文本未更新（`admin` 组描述仍写 "api-key / internal-key"），下轮顺手补。
