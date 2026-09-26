# handoff｜交接：M2 图形路线（第十轮）· 2026-09-22 #23

> ➡️ 接续 `handoff-screen-22.md`（第九轮）。新会话从 #23 读起。
>
> **新会话只读四样，别多读**：
> 1. **目标（唯一约束）**：`handoff-screen-18.md` **§5.1**。
> 2. **本路线方案**：`handoff-screen-18.md` **§5.2 / §5.3 / 六 / 七**；**本轮新口径** `rationale-screen-a11y-drop.md`；两个 spec：`spec-screen-client-api.md`（动词面，带本轮修订横幅）、`spec-screen-ledger.md`（服务端账本）。
> 3. **读法纪律**：`handoff-screen-18.md` **§5.0**（双栏 + 反证句 + 作废即删名）。
> 4. **代码**：`cogos/screenlab/` + `cogos/agent/{tools.py, impl/graphics.py}`（分支 `feat/screenlab-p2`，本轮提交 `8f71d89`）。
>
> ⚠️ **本轮最大变化：a11y 已整个剥离**。`handoff-screen-22.md` §三/§四/§五·1·3·4 关于"树 = 可选语义索引"的口径**已被推翻**，别沿用；目标/方案读 §5.1 与本轮 `rationale-screen-a11y-drop.md`，不读 #22 那些段。
> ⚠️ `spec-screen-element-act.md` **整份作废**（历史/负结果参考）；别读 `handoff-15/16` 的目标与架构表述；别用 `screenlab/install/install.sh` 与 `*.service`（旧 systemd 路线，已废）。

## 一、目标（摘要，以 §5.1 为准）

每 agent 有若干账户（账户是归属单位）；账户有一块**可操作的图形界面**，发动作能读回结果；操作要**像真人、不被检测**（逐步加固）；默认**不抢物理屏**，需要时人能看到/介入；三种关系 = 自用 / 授权他 agent（显式可收回）/ 与真人双向；**一账户同一时刻一块界面，"要"是幂等的**；**agent 只面对客户端**。

## 二、本轮做了什么（2026-09-22 YZ）

**判定：不用 a11y。图/pointer 一条腿**——a11y 唯一独有的事（把语义声明给屏幕阅读器）不是我们要的能力；要的感知/落点/像真人，图 + pointer 全包，且只有真实指针事件能往上加固。

- **代码**：提交 `8f71d89`（`feat/screenlab-p2`，已推）；a11y 代码与其测试**归档在 `archive/a11y`**（已推 origin，可 `git show` / `cherry-pick`），不入主线。
- **连带作废**：`spec-screen-element-act.md` 整份；`spec-screen-client-api.md` §3 的 `element` 格 + §4·14 的"结构/树"一支。
- **负结果与理由**（7ms/节点、`showContextMenu` 无信息量、`do_action` 不产生指针事件、相关性裁剪=机制代判、平台四分五裂）：见 `rationale-screen-a11y-drop.md`，**别重踩**。

## 三、当前 Linux 状态（已齐）

- **目标 2 闭环**：`capture`（pixels / crop / `changed`+`since_hash` / `wait_stable` / blob→文件→路径）+ `act`（pointer/key/type/paste/scroll）；工具层 `screen_capture`/`screen_act` 走通。
- **目标 5/6 骨架**：`open/close/grant/revoke`、per-account ledger、通道可多条、位（capture/input）、ttl/once/revoke。
- **目标 7**：客户端不露 `snapshot_id`/`frame_hash`；工具面已收敛成图/pointer。
- **目标 4 的一半**：默认 `gnome-shell --headless --virtual-monitor`，不抢物理屏。
- **装配**：account-install / session-start / session-stop，幂等，账户自己的 systemd user bus。
- **验证**：`python3.11 -m pytest tests` → **1208 passed, 4 skipped**。

## 四、缺口清单（**待 YZ 讨论定方向**，不是待办）

**A. 实质（对着目标）**
1. **目标 4 后半："需要时人能看到/介入"没做**。只有 pull 的 `capture`，没有实时观察口/推流，"喂给人看"的形态为空。（#22 §六·6）
2. **目标 3 加固一点没做**。真实指针事件这条腿在（XTEST），但"逐步加固"（**渲染落真 GPU**、时序/拟真）全空。**Linux 上最大缺口**，也是唯一"只有图/pointer 能走"的路。（#22 §六·9）
3. **真人侧接入（③a）没验**。本机只验了 agent↔agent；"真人在自己机器装服务、agent 接入"没走过。（#22 §六·7）

**B. 图主干两小件（代码里确认都没有）**
4. `act` 接受**上一次 crop 帧内**的坐标，服务端换算整屏（免模型做全局换算）。（#22 §三·6）
5. `capture(center,size,mark=x,y)` 出**带标记的局部图**（自检落点）。（#22 §三·6）

**C. 工程收尾**
6. blob 目录**无 GC**（`_store_blob` 只写不删），长期跑会涨。
7. `_geometry` 缓存后**不随分辨率变化失效**。
8. 授权粒度只到账户级（会话/窗口级是遗留）。（#22 §六·8）
9. 冷启动 ~1 分钟；空账户一键未做。（#22 §六·10）
10. 旧路线残留未退役（root 的 `Xvfb :99` + `/opt/screenlab`）。（#22 §八·13）

**一个判断（供讨论）**：要说"Linux 上能把活干完"，最小补丁是 **1 + 4 + 5**；要说"能对外交付、且符合目标 3 的前提"，必须先补 **2** 并验 **3**。

## 五、环境 & 常用命令

**环境事实见 `handoff-screen-22.md` §七/§八**（单/socket/display/xauth/跨身份姿势、已知坑 14 条，契约未变）；其中 **daemon pid 与 display 号以现测为准**，别照抄。

```bash
# 装配 + 起屏（root 或账户自己）
sudo bash cogos/screenlab/install/account-install.sh agent1
sudo bash cogos/screenlab/install/session-start.sh agent1 [--restart]

# 客户端（以该账户身份跑；跨机用隧道 + --tcp 127.0.0.1:9911）
runuser -u agent1 -- env PYTHONPATH=/home/agent1/.local/share python3 -m screenlab.service.cli \
  --socket /run/user/1003/screenlab.sock open
... capture [--center X,Y] [--size W,H] | act pointer --x 0.25 --y 0.35
... grant --bits capture,input --ttl 60 [--once] / revoke --credential <token>

# 单测（必须 3.11）
python3.11 -m pytest tests/screenlab -q
python3.11 -m pytest tests -q                    # → 1208 passed, 4 skipped

# 客户侧闭环 e2e（pixels/pointer；见 tests/screenlab/e2e/README.md）
sudo env PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPATH=/tmp/kilo/harness:/home/zhengyp/.local/lib/python3.11/site-packages \
  /usr/bin/python3.11 /tmp/kilo/harness/tool_loop_e2e.py --sock unix:/run/user/1003/screenlab.sock
```

## 六、纪律（沿用 #22 §九，实测有效）

- **双栏**：每条陈述标 `[目标]` / `[方案]`；**只有 `[目标]` 有否决权**。
- **目标段禁实现名词**；**方案段必须挂账**（满足目标的哪一条 + 代价）。
- **反证句自检**：说"因为已验/已定案/以前这么做"就暂停。
- **机制不代判**：不代判动作生效，**也不代判"看什么"**（相关性裁剪/骨架/大纲都属代判）。
- **作废即删名**：`热订阅` / `关闭重开` / `"形态（全桌面 vs 最小 X）"作选项` / `Xvfb 作起步形态` / `网络/NAT/打洞` / **`a11y` / `元素表` / `act element`**。
- 开工起 **10–15 分钟闹钟**；用 `terminal_exec`（非阻塞），**不要 sleep 轮询**；到点先落结论再继续。
- 一次只跑一条实验命令；sudo 密码只喂 stdin（`< ~/.secrets/centos.key`）。
