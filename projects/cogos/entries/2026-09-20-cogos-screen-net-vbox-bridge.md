# 2026-09-20 cogos 图形面网络：VBox 桥接收包 bug + Tailscale 绕行（#10）

> 背景：大图 capture 慢（Windows Surface 方向）。排查结论：**不是 screenlab / SSH / 协议，是 VirtualBox 7.2.x 桥接模式收包 bug**；且**Tailscale 实测可绕行**。细节交接 `work/A/checkpoint/handoff-screen-10.md`（含论坛佐证 t=114025 / t=109541、GitHub #690）。

## 现象（VM `192.168.1.13`/enp0s8 ↔ Surface `192.168.1.112`）

| 方向 | 吞吐 |
|---|---|
| 上传 VM→Surface | ~3MB/s（正常） |
| 下载 Surface→VM（原始 TCP） | ~64KB/s，且会卡死 |

- 换协议无效（sftp / `scp -O` / 原始 ssh 通道同量级）；ICMP 32~3000B 含分片 **0% 丢包** → 不是线路丢包。
- `enp0s8` 的 `rx_errors`/`rx_frame` 随传输增长；NAT 口（enp0s3）收公网 2MB/s 正常 → 问题限于**桥接口收包**。
- 机制（推测）：宿主网卡 **RSC（Recv Segment Coalescing）**把多段 TCP 合并成超长帧 → guest `e1000` 当超长帧丢弃。论坛贴出的 guest 统计正是 `rx_long_length_errors`。
- 升级 VBox 7.2.18 仍复现（7.2.8 也坏）。

## 定案：改用 Tailscale 走图形面（YZ 方向，本会话实测）

**实测对比（同条件、同一 NIC、背靠背）：**

| 路径 | 1MB | 4MB |
|---|---|---|
| 桥接 IP `192.168.1.112`（原始 TCP） | **16.4s** | ~70s |
| Tailscale `100.112.50.115` | **0.74s** | **1.05–1.20s** |

- `tailscale ping tablet-bbt8eqb4` → `via 192.168.1.112:41641`（**直连**，非 DERP 中继）。
- 计数器证实流量**仍走 enp0s8**（4MB 传输后 `enp0s8` rx +4.6MB，`enp0s3` 仅 +7KB）→ **不是"绕开了桥接口"**。
- 增量对照：原始 TCP 传输使 `rx_errors`/`rx_frame` **+165**；Tailscale 传输几乎不增。
- 解释（推测）：WireGuard 线上是 **UDP**，RSC 只合并 TCP → 超长帧路径不触发，故 bug 不显。
- 结论：**不需要 YZ 去宿主关 RSC**（原 §五 待办可降级为"若想根治原始 TCP 再考虑"）；Tailscale 直接可用，~4MB/s 对单帧大图（1–3MB）足够。

## 对 screenlab 的影响

- 属**环境层**，不改协议 / 传输层；客户端 endpoint 改走 tailnet IP（`100.112.50.115`）即可，`ssh -L` 照旧。
- 备注：tailnet 直连依赖同 LAN；若退化为 DERP 中继仍可用但吞吐/延迟另计，需留意。

## 状态

- 写于会话 #10 之后的一次追加讨论；`handoff-screen-10.md` §三/§五 的宿主关 RSC 建议**因本结论降级**（保留作原始 TCP 根治方案）。
- cogos 侧未改码；`install.ps1` 端口策略仍**未提交**。
