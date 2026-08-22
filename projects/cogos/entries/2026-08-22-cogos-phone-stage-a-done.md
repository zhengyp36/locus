# 2026-08-22 — Phone 阶段 A 落地并提交（领域层 + 持久化 + FakeTelecomClient）

> 本体 `~/codex/cogos`。impl-plan（docs/phone-impl-plan.md）Step 1-5 全部落地，阶段 A 完成，阶段 B（接 FeishuTelecomClient）待新会话讨论。

## 产物

- 新包 `cogos/phone/`：`model.py`（Number/Card/Contact/Chat/Msg 五类 + 序列化辅助）/ `store.py`（PhoneStore + `_atomic_write` 原子写 + `load_config`）/ `fake.py`（FakeTelecomClient 忠实 telecom 语义，send 回显自己消息）/ `phone.py`（Phone 主类：add_card/contacts/send 三重重载/listen/_make_on_msg 方向判定/sessions/create_group/shutdown + `default_card` 属性）。
- 测试 `tests/phone/`：test_model/test_store/test_fake/test_phone 共 50 例。
- 身份边界守住：`cogos/phone/` 无 open_id/app_id/user_id 字面量（fake.py `oc_fake_` 是 chat_id 前缀，plan 规定）；只 import telecom 抽象（`TContact/TChat/TMessage` 别名）。
- 阶段 B 注入点：`phone.py:46` `self._factory = FakeTelecomClient`，换 `FeishuTelecomClient`（同 `__init__(contact, pin)` 签名）即可。

## 提交

- `5f62bd8` fix(test): align bs_agent assertions with account refactor（account refactor 遗留断言，`saved[1]`→`saved[0]`，全量由 600 变 601）
- `599abf5` feat(phone): stage A domain layer + persistence + FakeTelecomClient
- 测试：`pytest tests/phone/` 50 passed；全量 `pytest tests/` **601 passed** 全绿；`py_compile` 通过。

## 下一步（阶段 B）

- 接 FeishuTelecomClient：`phone.py` `self._factory` 换真实现 + daemon 侧 app_id 解析（`add_card(number, pin)` 一步对接，app_id 在 daemon 侧解析）。待 YZ 新会话讨论。
