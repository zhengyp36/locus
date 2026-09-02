# checkpoint-3 — 修复 reconnect 新建 client 后收不到消息

> bug：cogos-phone 启动时 card 连接失败，reconnect 后能发消息、但收不到对方消息。根因 + 修复。

## 当前问题

启动失败 → reconnect 成功 → 发送正常、收消息静默丢弃。

## 已做修改

- `cogos/phone/phone.py:406-414` — 新增 `_register_listeners(number, client)`，把「给单个 client 挂 `_make_on_msg`/disconnect/error/members_changed 回调」从 `listen` 循环里抽出来。
- `cogos/phone/phone.py:396-405` — `listen` 循环体改为调 `_register_listeners`。
- `cogos/phone/phone.py:138` — `_connect_card` 成功注册 client 后补 `await self._register_listeners(num, client)`。
- `cogos/tests/phone/test_phone.py` — 新增 `TestReconnect.test_reconnect_registers_listener_for_new_client`：flaky factory（第一次 startup 抛异常、第二次成功），add_card 失败 → listen → reconnect → deliver → 断言 on_msg 收到。

## 已读代码要点

- `phone.py:129-144` `_connect_card` — startup 失败提前 `return`，client 不进 `_clients`。
- `phone.py:396-405` `listen` — 只遍历当时的 `_clients` 注册一次回调。
- `phone.py:647-671` `reconnect` — `num not in self._clients` 分支走 `_connect_card` 新建 client，原先不补 listener。
- `telecom.py:250` `FeishuTelecomClient.__init__` — `_on_msg = _noop_on_msg`（默认丢弃）。
- `telecom.py:273-296` `startup` — 只 `_do_listen()` 启动 reader/heartbeat，不动 `_on_msg`。
- `telecom.py:404-420` `listen` — 才覆盖 `_on_msg`。
- `telecom.py:465` `_reader` — 收到消息 `self._spawn_callback(self._on_msg(...))`，若 noop 则丢弃。
- `telecom.py:467-473` `_handle_disconnect` — 清 `_sock`/`_tasks`，不清 `_on_msg`（故已有 client 断线 reconnect 不受影响）。

## 关键结论 / 决策

- 根因：收消息依赖 `client.listen` 注册的 `_on_msg` 回调；发送走 `_sock` 直写不依赖回调。reconnect 新建 client 时漏注册 → `_on_msg` 仍是 noop → reader 读到的消息被丢弃。
- 修复落点选 `_connect_card`（client 创建的唯一入口），对 add_card / reconnect 两条路径都生效；已有 client 断线 reconnect 走 `startup()` 分支、回调仍在，不受影响。

## 验证

- `python3.11 -m pytest tests/phone/test_phone.py -q` → 38 passed。
- `python3.11 -m pytest tests/ -q` → 787 passed（无回归）。

## 遗留 / 坑

- 无。reconnect 对已有 client 的 `startup()` 分支仍假设 `_on_msg` 已由更早的 `listen` 设置——若未来有「client 从未 listen 就断线」的路径，同样需补注册。
