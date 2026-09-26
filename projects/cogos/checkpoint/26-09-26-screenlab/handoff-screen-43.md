# handoff｜交接给新会话 · 2026-09-24 #43

> 接 #42。本会话 = **从目标推出 3a 最小认证闭环、冻结接口、定 slice 1**；唯一改动 = `../checkpoint/design-screen-assist.md`（**未 commit**）。**下一会话从 slice 1 实施起**。
> **规则 / 环境不在本文件**——见 **`screenlab-rules.md`**（先读）。

## 给新会话的第一句话

> 先读 **`screenlab-rules.md`** → 本文件 → **`design-screen-assist.md`**（§1 差异 / §2 流程 / **§3 身份 + §3.1 认证接口** / §4.2）→ **`spec-screen-1.md` §0.0**（唯一约束）。
> 本会话**没写代码**，做的是把认证模型定死、冻结接口：
> - **身份 = 公钥**（唯一）；**号码/名字退到通讯层（飞书）**，不进认证；**取消通讯录**，改真人机上一张**本地公钥登记表 `{pubkey → {name, alias}}`**。
> - **认证 = 同一 socket 的第 0 阶段**：`hello{pubkey}` → `challenge{request_id,nonce}` → `verify{request_id,sign}` → `result`；过了才进 `screen/1`。
> - **授权 = 真人本地确认**（v1：CLI/事件；弹窗后置，同一 hook）。
> - 独立包 **`screenlab/auth/`**，**与 `screen/1` 不混**；接口已冻结（`design-screen-assist.md` §3.1）。
> 下一步 = **slice 1**（见下）。

## 本会话已做（设计推演 + 冻结接口）

- **号码没必要**：一个 agent 可多号 → 号码不是身份；直接以**公钥**为标识；公钥公开、无泄露问题。连接时客户端发公钥，服务端**只认登记表里那条**（自报不当真），并用它验签证明持有私钥。
- **"要不要走一次飞书证号码" → 不要**：号码归属在**登记（存号码）那一次**由飞书锚定；连接时依赖飞书 = 逼真人机跑一个飞书 bot（非 Linux 平台负担大）+ 绑死飞书可用性。飞书只出现三处：发起 / 通道交换 / 公钥登记。
- **接入凭证 vs 授权 两层分开**：凭证 = agent 自持密钥（身份）；授权 = 真人本地点确认。避免与"无会话凭证、不交出账户"冲突。
- **通信录 → 公钥登记表**：键 = 公钥（唯一约束只在公钥）；`name / alias` 纯展示、可重（由真人自己定）；删条目 = 长期收回。
- **冻结接口（§3.1）**：`Registry` / `AuthServer(consent)` / `AuthClient` / `Key` / 协议 `screenlab-auth/1` / 编码与文件格式 / `--tcp --auth` 开关。
  - `add` 两模式：`overwrite=False` 默认，重复 → `raise DuplicateKey(existing)`；UI 先不覆盖、失败后按用户选择再 `overwrite=True`（`add` 本身不弹任何东西）。
- **定 slice 1 范围与验收**（见下）。**未写代码、未改仓库。**

## 下一步：slice 1（新会话照此实施）

1. **新增 `screenlab/auth/`**（`../cogos`）：`registry.py`、`server.py`、`client.py`、`protocol.py`、`__init__.py`。自带协议常量，只复用 `..proto.framing.Channel`。
2. **`service/daemon.py`**：`_serve_conn` 顶部插 auth 阶段（`AuthServer.serve`），**仅 `--tcp` 且显式 `--auth <registry>` 时启用**；通过后把 `Record` 挂到 `ConnState.identity`，继续原 screen/1 循环。
3. **`service/cli.py`**：加 `register` / `keygen` / `--auth` / `--consent {auto,stdin}`；新增 `attach` 子命令（调 `AuthClient`）。
4. **确认机制**：slice 1 先 `--consent auto`（直通）跑通密码学+连接层；**slice 2** 换 `stdin`/事件真人确认；**slice 3** 换弹窗（同一 `consent` 签名）。
5. **验收（先本地 127.0.0.1）**：
   - 正向：`keygen` → `register` → `attach` → `capture` 成功（对 `import -window root`）。
   - 负向：未登记公钥 → `unknown_key` deny；用**另一把私钥**签 → `bad_sign` deny；错/过期 nonce → deny。
   - 收回：停 server → client 下次调用得 `channel_closed`（顺带把 **G3** 的语义化错误带出来）。
6. **靶机 tailnet 部署后置**（slice 1 不依赖 VM）。**G1（`open --attach` 附着现有 `:N`）不在 slice 1**，本地冒烟可用现有 display。

## 状态 / 环境

- **唯一改动**：`../checkpoint/design-screen-assist.md`（**未 commit**）；本文件新增。
- **代码** `../cogos` @ `feat/screenlab-p2`（`90afbeb`）；工作区 `screenlab/install/surface` 有**未 commit 的 G2 修复**（`--onlyvisible`，待 YZ 同意提交）。
- **靶机** `surface-centos-9`（`100.100.137.78`）；宿主 VBox（Windows）`zhengyp@…`（rules 写 `100.100.112.50.115`、handoff#42 写 `100.112.50.115`，**以实际连通为准**）。
- **依赖**：Ed25519 用 `cryptography`（已随 asyncssh 装上，实测 49.0.0 可用），**不新增依赖**。
- **未决（不挡 slice 1）**：G4 clip 写路径；agent-tool 侧把 `attach` 暴露给 cogos agent（后置）。

## 纪律（沿用 `screenlab-rules.md`，本线重点）

- **由目标裁决**（§0.0）；能推的**自决并记录**，真不清才飞书升级后停下等。
- **命令走 `terminal_exec`**（非阻塞）；不用 `sleep`；**不提交**。
- **验收用公开入口 + 地面真值**（`import -window root`），不用自写 e2e。
- 交接阈值：上下文 ≥200K 或路径偏 → 写 handoff + 通知。

## 入口

- **规则 + 环境（先读）**：`screenlab-rules.md`
- **本线方案（本会话已改）**：`design-screen-assist.md`（§3.1 = 认证接口）
- **目标（唯一约束）**：`spec-screen-1.md` §0.0
- **#41 实验记录**：`screen-assist-exp-log.md`（三闸门 + G1–G4）
- 体系：`design-screen-system.md`；生命周期/命令层：`issue-screen-surface-lifecycle.md`
- 代码：`../cogos` @ `feat/screenlab-p2`
- 上一轮：#42 `handoff-screen-42.md`
