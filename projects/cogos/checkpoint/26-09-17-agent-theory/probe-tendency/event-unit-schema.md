# 事件单元 · 最小 schema（实验 B，v0）

> 出自 `../next-experiments.md` 实验 B。初版即可，供实验 A 当"记忆条目"喂回。
> 原则（会话 #13 结论）：**不写结论、只写绑在事件上的因果痕迹；强度/权重是派生的，不手写；来源要标"发生过的"。**

## 字段

| 字段 | 说明 | 必填 |
|---|---|---|
| `id` | 回指原事件的指针（run/message id） | 是 |
| `scene` | 场景，一行归一化 + `tags`（**检索 key**） | 是 |
| `action` | 我的动作，含**通道**（content / send_message / agree / refuse / silent） | 是 |
| `outcome` | 世界回了什么 / 成或败 | 是 |
| `source` | `"经历"`，区别于指令/教学（机制写） | 是 |
| `contrast` | 旧做法→结果 vs 新做法→结果（**改变时才有**） | 否 |
| `intensity` | 弱/中/强，由 outcome 显式度 + 重复派生 | 派生 |
| `weight` | 该 (scene-class, action) 的有符号强度累积，派生 | 派生 |

## 已定的三件

1. **粒度**：一个事件 = 一次闭合的 `action → outcome`。`contrast` 是两条同类事件（旧/新）的**组内**聚合，不单列成一种单元。
2. **强度**：`intensity = valence × magnitude`，`valence∈{-1,0,+1}`、`magnitude`：泛泛回应=1（弱）、明确反馈=2（中）、点名得失=3（强）。`weight = Σ intensity`（同 scene-class + 同 action）。
3. **检索 key**：`scene` 一句归一化描述 + `tags`；初版按 `tags` 的**场景类**匹配，不做向量。留位给后续 embedding。

## 示例 JSON

```json
{
  "id": "evt-2026-09-14-0007",
  "scene": "他请我固定帮他做一件事",
  "tags": ["请求", "长期承诺", "同意与否"],
  "action": {"channel": "agree", "what": "答应"},
  "outcome": "他把这当成理所当然，我的时间被占住，没有回报",
  "source": "经历",
  "contrast": {
    "旧": {"action": "agree", "outcome": "时间被占住、无回报"},
    "新": null
  },
  "intensity": {"valence": -1, "magnitude": 3, "value": -3},
  "weight": -3
}
```

> 注：实验 A 的两条历史就是同一条 `scene` 下 `contrast` 的两个分支——`pos` 的 `intensity.valence=+1`，`neg` 的 `=-1`。A 直接按此格式渲染成 `[我的记忆 · 机制写]` 块。
