# Checkpoint 23 — Phone 默认接真机（移除 fake 默认）

## 当前问题

Phone 可用性评估发现两点瑕疵：默认 client 是 `FakeTelecomClient`、agent 接真机需 import `cogos.feishu`。第三点（get_members 兜底超时）遗留。

## 已做修改

- `cogos/phone/phone.py:17-22` — import 加 `FeishuTelecomClient`、删 `from cogos.phone.fake import FakeTelecomClient`
- `cogos/phone/phone.py:55` — `self._factory = client_factory or FeishuTelecomClient`（原 `FakeTelecomClient`）
- `tests/phone/test_phone.py:13-17` — `make_phone` 显式 `client_factory=FakeTelecomClient`

## 已读代码要点

- `cogos/feishu/telecom.py:237` `FeishuTelecomClient(Contact, pin)` — 真机实现，H→user_id / A→app_id 解析在 daemon 内
- `cogos/phone/fake.py:14` `FakeTelecomClient` — 测试/演示用，`deliver`/`deliver_members_changed` 模拟入站
- 分层：`TelecomClient`（通信设施，只暴露 `Contact`/`Chat`/`Message` 的 number/name）→ `Phone`（agent 直面，只认 `Number`/`title`）

## 关键结论 / 决策

- 分层定位确认正确：cogos-feishu 底层通信、Phone 直面 agent，agent 不碰 `cogos.feishu` 内部（open_id/app_id/user_id 不泄漏）。
- 默认 factory 改真机：agent 侧 `Phone()` 即接真机，无需 import `cogos.feishu`；测试/演示显式 `Phone(client_factory=FakeTelecomClient)` 隔离。

## 验证

- phone 67 passed；全量 642 passed。

## 遗留 / 坑

- get_members 首次进群同步拉成员 + 30s `REQUEST_TIMEOUT` 兜底排队（归因见 checkpoint-21/22），未动。
- `_send_to_chat` 调 client 私有 `_send_chat`（`phone.py:281`）跨层私有 API 耦合，功能正常。
