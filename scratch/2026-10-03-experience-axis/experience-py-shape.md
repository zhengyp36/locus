# experience.py 最小形状（讨论产物，非代码）

> 来源：`README.md`「认可口径」（10-03，YZ 认可）。**只出形状、不写代码**；升级现有 `SegmentStore`，**不重写**。
> 目标：把经历轴从"只写"推到"能读回"——最小 `retrieve`/`open_knots`，让"掐断回读→行为塌回反应式"可测。

## 数据

```
Segment (dict)
  id, t, host, 来源, 人[], 主题,
  内容, 预测, 后果, 过程,
  结(了|未了|挂起), thread, refs[(kind,id)]
```

- **L0**：`memory/segments.jsonl`（append-only，唯一真相）。复用/升级现有 `SegmentStore`。
- **不落盘派生**：索引、权重、工具、误差——启动扫 L0 重建。

## 索引（进程内，不落盘，可重建）

```
by_time    : 天然顺序（list，按 id/t）
by_person  : dict[str, list[id]]
open_knots : dict[结, list[id]]      # 结 ∈ {未了, 挂起}
by_thread  : dict[thread_id, list[id]]
```

## 接口

```
append(seg)                 # 写：L0 追加 + 更新索引
retrieve(keys, budget)      # keys={person?, thread?, knot?, since?}
                            # 各索引取 → 合并去重 → 近因排序 → budget 截断（权重=0）
open_knots()                # open_knots 索引，按近因
rebuild()                   # 从 L0 重建全部索引
```

## 不做（首版）

控制拍 · 误差切点 · 权重公式 · 主题/工具索引 · 后压/蒸馏 · 读时现整 · 回边。

## 挂点（现有代码）

- `cogos/agent/flow.py`：`SegmentStore` → 升级（`segment_from_flow` 补字段、`SegmentStore` → `experience`）。
- `cogos/agent/consciousness.py`：`on_done` / `on_tool_call` 落段点**不变**。
- `cogos/agent/app.py`：`me=...` 透传不变。

## 验收

- **机制**：`tests/agent` 通过；L0 append/reload 一致；索引 rebuild == 增量。
- **行为**：**掐断读侧回读 → 行为塌回反应式**（有读则受经历影响）。
- **自指**：`open_knots` **跨事件稳定**（未了张力真活起来）。
