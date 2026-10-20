# 目录根收敛 · 三根 + 访问层归属（2026-10-20）

> 状态：**讨论已收敛，大部分落码**。承 `2026-10-19-selfdrive-body-discussion.md`（工具先行）+ `2026-10-20-content-access-unify.md`（内容访问统一）。本文件是三条线的「目录根」共同收敛点。已落：web 缓存放 `work_dir/web`（`e5dbcda`）、spool 删除 + phone download/send_file 走 agent_root（`e003135`）。待落：memory_dir 拆分、phone 消息缓存落点。
> 术语（本文件定）：`agent_root`（本地家）/ `machine_root`（机器内容根）/ `spool_root`（不可见中转）/ 意识层 LLM / 元层 LLM / 程序（代码）。

## 核心结论：三根 + 三层访问归属

目录根分**三个物理根**，但更关键的是**每个根归哪一层访问**（访问层归属固定，不是"可见性"）：

| 物理根 | 现状落点 | 归哪层访问 |
|---|---|---|
| **agent_root** | 本地（agent 的家） | 内部再分：`memory/`→**元层 LLM**；其余（cache/downloads/state）→**程序**。**意识层不可见** |
| **machine_root** | `config.work_dir`（可 sftp 远程） | **意识层 LLM** 经工具访问（body.file/terminal/vision PATH） |
| ~~spool_root~~ | `config.spool_dir` | **已删（`e003135`）**：phone 文件面并入 agent_root |

### 访问层（三种角色，固定）

1. **意识层 LLM**（六步循环本体）：只走工具，给相对路径/句柄、收内容，**看不到物理路径**。能碰 = machine_root（经 body.file/terminal/vision PATH）+ 缓存内容（经 FIG/WEB/chat 句柄）。
2. **元层 LLM**（记忆装配/整理）：只读 agent_root 下**记忆根目录**，不碰 agent_root 其他位置。对应 YZ 的「意识过程→记忆沉淀」构想（元层工具 file，未落码）。
3. **程序**（代码）：直接读写 cache/downloads/spool/state + 句柄物理落点，LLM 无感知。

### 关键判定（why）

- **可见性 ≠ 主轴，访问层归属才是**：意识层 agent 从不直接操作目录，它只走工具；"看得见"的永远是工具返回的内容与句柄，不是文件系统路径。早期把可见性当"agent 能否直接 file 操作"是错的。
- **LLM 分两种**：意识层 LLM（走工具）+ 元层 LLM（读记忆根），两者访问目录权限不同、固定。
- **慢无害、唯一边界 = 不阻塞**：机器是外部工具，慢无所谓，前提 = 访问都 await + 大文件读走 `stat` 预检（`get_bytes` 的 `max_bytes`，`fs.py:316`）。注意 `LocalBackend.read_bytes` 是同步 `Path.read_bytes()`（`fs.py:74`），本地大文件同样占 event loop，靠预检挡。远程机器慢的问题本轮不展开。

## 已定结论（随 coding 落码）

1. **phone 下载落 `agent_root/downloads`**：agent 自己定路径，缺省 `downloads/`。这是删 transfer 的必然结果（spool→machine 的桥没了，下载必须直接落 agent 可见位置）。
2. **send_file 对称**：从 agent 本地读任意路径（不再限 spool）。两端都走 agent 本地后，**spool 无独立存在理由 → 删（打 tag 保底，同 draft/transfer）**。
3. **web 缓存物理放 agent_root 下**（`work_dir/web`，与 `work_dir/vision` 并列），语义 = 句柄访问（`WEB:<id>`），意识层不直接 file 操作。不单设 cache_root。
4. **缓存/下载/记忆都落本地 agent_root**；machine_root 只是 `get_bytes` 的外部内容来源（vision 源文件在远程就 `get_bytes` 拉到本地缓存再解码）。

## 待定（悬置，不阻塞编码）

1. **phone 消息缓存落点**：agent 侧新建 inbox（`MSG:<id>` 句柄？），还是复用 phone store 的 `chats/`？影响 agent_root 下有哪些子目录。→ 留到 phone 消息缓存落码时定。
2. **memory_dir 拆分**：状态文件（profile/timers/segments）vs 记忆内容根，物理上是否拆两个子目录（如 `memory/state/` vs `memory/`）。→ 留到元层 file / memory 工具落码时定。
3. **web 缓存已定**：目录 `work_dir/web`、TTL 2h、fetch `format` 保留。**downloads 边界**仍留 phone 下载改造轮定（宽松 TTL vs agent 自管，`body.file` 无 delete 靠 terminal rm）。
4. **spool 删除（已落码 `e003135`）**：download 落 `agent_root/downloads`（缺省）、send_file 读 agent_root 任意路径、删 `phone_spool_list`/`phone_spool_delete` 与 `config.spool_dir`；与 phone 下载改造同轮完成。

## 被否 / 已排除

- 单设 `cache_root`（web/vision 缓存独立成根）：否，物理归 agent_root、句柄访问语义，省配置字段、与 vision 现状一致。
- phone 下载写**远程** machine-root：否，下载落**本地** agent_root；机器只是外部工具、内容经 get_bytes 拉取。
- 意识层直接访问 agent_root：否，意识层一律走工具，物理目录对意识层透明。
- 「可见性」作为主轴：否，改「访问层归属」。
