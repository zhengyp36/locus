# handoff｜P4 端口策略定案 + 大图慢的根因（VBox 桥接 RX bug）· 2026-09-20 #10

> **新会话任务**：本会话处理了 09 的遗留 ①②（`launch.py` 澄清 + 端口策略定案），并**定位"大图 capture 慢"的根因——不是 screenlab，是 VirtualBox 7.2.x 桥接收包 bug**。可接着做：① 等 YZ 在宿主网卡关 RSC 后**复测带宽**（命令见 §五），确认后回写结论；② `install.ps1` 端口策略改动**未提交**，待提交；③ 回写权威分册 `cogos/docs/design-agent-tools.md`（Windows 装配 + 本次 VBox 坑）；④ 清测试残留；⑤ 继续 P2/P3。
> **交接语**：读本文件即可开会话；细节读 `handoff-screen-09.md`（P4 落码 + 真机验收）、`checkpoint-6.md`（P4 决议）。
> **前序**：`handoff-screen-09.md` → 本文件。

## 本会话性质

讨论 + 一处小改动（`install.ps1` 端口策略）+ 大量只读网络排查。**未改 screenlab 传输层代码**。

## 已提交 / 工作区

- `56f186c` `feat(screenlab): add the pythonw headless entry point`（补 09 漏掉的 `launch.py`）
- **未提交**：`screenlab/install/install.ps1`（端口策略：默认 9911 + 占用回退）
- `handoff-screen-09.md` 已就地更正两处误记（见 §一）

## 一、澄清 09 的两处误记（已改正）

1. **`launch.py` 不是"另一并发会话产物"**：同一会话 17:58 写下（与"install.ps1 改用 launch.py"是同一条 tool 消息）；18:08 同一会话上下文丢失，误判成并发产物。session 表证实 16:53–18:13 只有一个会话、无子会话。已补提交 `56f186c`。
2. 09 里"自启 = `serve.cmd` + `launch.vbs`（wscript 隐藏窗口）"是**被淘汰的中间方案**（wscript 留孤儿进程）；最终方案是 **`pythonw -m screenlab.service.launch`**，`install.ps1` 早已如此。已改对。

## 二、端口策略定案（YZ 拍板，未提交）

**默认固定 9911、占用再探测。**

`install.ps1` 选端口优先级：显式 `-Port N` > 复用 `config.json` 里**仍空闲**的端口 > 从 `9911` 起 `Test-PortFree` 递增（至 9911+100）。
新增 `Test-PortFree`；`$DefaultPort = 9911`。客户端 endpoint 因此基本恒为 `tcp:127.0.0.1:9911`，可预写 `agent.json`。

## 三、大图 capture 慢的根因（本会话核心结论）

**不是 screenlab / SSH / 协议，是 VirtualBox 7.2.x 桥接模式的收包 bug。**

### 现象（VM `192.168.1.13`/enp0s8 ↔ Surface `192.168.1.112`）

| 方向 | 吞吐 |
|---|---|
| 上传 VM→Surface | ~3MB/s（正常） |
| 下载 Surface→VM | ~50–125KB/s，且会**卡死**（1MB 45s 都传不完） |

- 换协议无效：sftp / legacy `scp -O` / 原始 ssh 通道同量级。
- ICMP 32/1400/1472/3000 字节 **0% 丢包**（含分片）→ 不是线路丢包。
- 故障表现：TCP**收方向停顿**（VM 侧 `Recv-Q=0`、无重传），偶发 **Corrupted MAC**（`aes*-ctr`）。
- 关键计数：`enp0s8` 的 `rx_long_length_errors` 随传输增长（一次 4MB 传输：+908 errors / 3958 包 ≈ **23%**）。
- NAT 口（enp0s3）收公网 2MB/s 正常 → 问题限于**桥接口收包**。
- **升级到 VirtualBox 7.2.18 仍复现**（7.2.8 也坏；"≥7.2.6 就好"只是论坛单例，不成立）。

### 已知问题佐证

- 官方论坛 **t=114025** *VirtualBox 7.2.0 2.2 Mbit download restriction*：7.2.x + 桥接 = 下载慢/上传正常；贴出的 guest 统计正是 **`rx_length_errors` / `rx_long_length_errors`**；环境 Win 宿主 + RHEL/Rocky 9 guest。
- 官方论坛 **t=109541** *Bridgemode network very slow just in receive direction*。
- **GitHub VirtualBox/virtualbox#690**；Reddit `1n8gsdp`。
- 机制：宿主网卡 **RSC（Recv Segment Coalescing）**把多段合并成超长帧 → guest e1000 当超长帧丢弃（正对应 `rx_long_length_errors`），收方向持续重传/停顿，发方向不受影响。

### 待 YZ 在宿主侧的动作（改完我复测）

1. 宿主物理网卡关 **Recv Segment Coalescing (IPv4/IPv6)**（多人确认对 7.2.x 有效；副作用仅是极高吞吐下略多 CPU，可逆；可顺带关 LSO/RSS）：
   ```powershell
   Get-NetAdapter
   Get-NetAdapter | Set-NetAdapterAdvancedProperty -DisplayName "Recv Segment Coalescing (IPv4)" -DisplayValue "Disabled"
   Get-NetAdapter | Set-NetAdapterAdvancedProperty -DisplayName "Recv Segment Coalescing (IPv6)" -DisplayValue "Disabled"
   ```
2. 备选：建 **Hyper-V vSwitch** 再桥接；或**降级 VBox 到 7.1.x**。
3. 若 RSC 选项不存在（WiFi 网卡常见），走备选。

### 对 screenlab 的影响

环境层 bug，**不改协议/传输层**；链路恢复后大图 capture 应正常。若长期修不好：`max_dim` 降采样，或加可选 JPEG。

## 四、遗留 / 待裁决

1. `install.ps1`（端口策略）**未提交**、未真机复验。
2. 带宽根因待 YZ 关 RSC 后**复测确认**，再回写权威分册。
3. 回写 `cogos/docs/design-agent-tools.md`（Windows 装配细节 + VBox 桥接坑）。
4. 测试残留（§六），可清。
5. P2/P3（断连即终态、granted `stop`）仍未做。
6. Surface 现处**已 uninstall** 状态（无 daemon / 无任务 / 无目录）。

## 五、环境与复测命令

- **VM（本机）**：`10.0.2.15`(NAT, enp0s3) / `192.168.1.13`(桥接, enp0s8)；tailscale `100.79.86.84`；CentOS Stream 9，kernel 5.14 el9，网卡 `e1000`；firewalld active，**无免密 sudo**。
- **Surface**：`ssh screen@192.168.1.112`（key 免密）；tailnet `tablet-bbt8eqb4` = `100.112.50.115`（`ssh screen@100.112.50.115` 可用）。
- **cogos**：`/home/zhengyp/work/A/cogos`，分支 `feat/screenlab-p2`；测试 `python3.11 -m pytest tests/ -q`。

复测：
```bash
ssh -o BatchMode=yes screen@192.168.1.112 'ping -n 40 -l 1400 192.168.1.13'   # 基线：应 0% 丢包
time scp -q screen@192.168.1.112:bw1m.bin /tmp/kilo/bw/r1.bin                  # 下载 1MB（修复前 ~10s）
time scp -q screen@192.168.1.112:bw4m.bin /tmp/kilo/bw/r4.bin                  # 下载 4MB（修复前 ~70s）
grep enp0s8 /proc/net/dev                                                      # 看 rx_long_length_errors 增量
```

## 六、测试残留（可清）

- **VM**：`/tmp/kilo/bw/`（`256k.bin 1m.bin 4m.bin`、下载副本 `c1/r1/r4/d*`、`bwread.ps1`）；`~/.ssh/authorized_keys` 里本轮追加了 Surface 公钥（`screen@TABLET-BBT8EQB4`）。
- **Surface**：家目录 `bw256.bin bw1m.bin bw4m.bin bwread.ps1 httpd.ps1 httpkill.ps1`。

## 纪律

- 跑测试用 `python3.11 -m pytest`；结论先落 checkpoint/spec，定案再回写 `cogos/docs/design-agent-tools.md`。
- 目标侧叫"**服务**"不叫 agent；**认证不在协议里**；`screenlab/` 禁止 import cogos。
- 密码类只经文件与 `SSH_ASKPASS`，绝不落进命令行或工具输出。
- **验证重启**：本机（会断会话）不用；Surface 用注入 UI 或人工。
