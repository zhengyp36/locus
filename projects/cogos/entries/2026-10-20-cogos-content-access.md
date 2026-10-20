# 内容访问统一 · get_bytes 复用（2026-10-20）

> 状态：**已落码**（`ee9f0ba`，已推送）。承 `scratch/2026-10-20-content-access-unify.md`（已收口删除）。术语：`content access`（内容获取）、`content root`（内容域）、`state root`（工具状态根）→ glossary。

## §1 问题（三个「根」散落三处）

1. `file.read` 走 fs channel，相对**机器根**（`machine_root`）。
2. `vision.see PATH:<path>` 走 `image_ctx.add_src`，硬编码 `Path.read_bytes()`，相对**进程本地 cwd**。
3. 元层 `file`（未落码）应相对 **agent 记忆根**。

本地部署（machine_root=work_dir）下前两者重合，sftp 远程或元层 file 落码即踩坑。

## §2 抽象：统一「内容获取」，不统一「消费」

- **内容获取（统一）**：`get_bytes(path) -> bytes`，域由封装层决定。
- **内容消费（各自 impl）**：`file.read` → get_bytes 后分页/截断；`vision.see PATH` → get_bytes 后解码、落本地缓存、mint FIG；`vision.see FIG` → 不走 get_bytes，命中缓存。
- **content root**（能力访问「文件对象」的 base：machine/memory）≠ **state root**（工具自己持久化在哪：image_ctx `Domain.root`/DraftStore/Spool），impl 装配注入，不进 content root 语义。

## §3 分层：session 属于封装层，impl 通用

- 底层 `FsChannel(backend, base)` 不接 session；`get_bytes(path)` 只接 path（`fs.py:306`，注释 "transfer-facing raw byte access"，删 transfer 后改内容访问语义、接口保留）。
- 封装层 `make_fs_specs._read(id, path)` → `manager.get(id).fs`；meta_tool 用 `needs_session` 把 id 注入 `call_args`。
- **vision bug 本质**＝`make_vision_specs` 封装层漏了「拿 session → 取 fs」这一步。修法＝`vision.see` 标 `needs_session=True`，PATH 分支拿 `session.fs.get_bytes`——与 file 完全同构，机制层零改动。

## §4 FIG 是缓存句柄（与 file 的本质差异）

`add_src` 现状：`Path.read_bytes()` → 按 md5 落 `images/` → mint FIG。PATH 回源、FIG 命中缓存不回源。file 无缓存（按行回源）、vision 必须缓存（图解码后回源无意义）——「附件投影/句柄」的自然结果，非缺陷。

## §5 落码形状（已定）

1. 机制层**零改动**：复用 meta_tool 现有 `needs_session` 注入。
2. 数据层：`vision.see` 标 `needs_session=True`。
3. 封装层：`make_vision_specs(root, manager=None)`；`_see(ref, ..., id=None)` PATH 分支解析 ref → `manager.get(id).fs` → `stat size` 预检 → `get_bytes` → `add_src` from-bytes 预热。`manager` 缺省时 PATH 回退本地读（向后兼容，screen selftest 等本地绝对路径调用方）。
4. 底层：`FsChannel.get_bytes(path, *, max_bytes=None)`，vision 传图上限 `MAX_IMAGE_BYTES = 64MB`（`tools.py:25`），`stat` 后 `read_bytes` 前拒绝（零成本）。图比文本大合理，render 层另有 `check_budget` 兜底解码后 OOM。

## §被否

- **`Capability.root` 字段**（原方案声明能力所属内容域）：① 无运行时消费方（不进 help、meta_tool 不读、校验已降级）＝死字段，踩「形状自证 > 标签声明」判例（`time_form` 同款）；② 粒度放错——域边界是 toolset/catalog 级（body 全 machine、元层 file 全 memory），不存在单个 Catalog 内混域。本轮只有一个域，装配层写死一件事即可。
- **装配层注入 `get_bytes` 闭包**（原方案）：get_bytes 是底层通用接口，不该作注入物；要注入的是 session，走 `needs_session` 机制，与 file 同构、零新机制。
- **新建 `content.py` 抽 get_bytes**：`FsChannel.get_bytes` 已存在，直接复用。
- **改 `add_src` 现有签名**：会牵连 P1/P2/P4 验收，改为向后兼容的新增参数 `contents: bytes | None = None`（默认 None 走原 `Path.read_bytes()`，幂等键保持 `str(path)`）。
- 笼统「工具路径可配」：混淆 content root 与 state root，已拆开。
- 改 vision 的 `Domain.root` 来配根：那是状态目录，与 PATH 寻址根两码事。

## 遗留

- **needs_session 副作用（已知接受）**：vision.see 标 needs_session 后 FIG 分支也先开默认 terminal（虽然 FIG 不用 fs），与 file 同构、语义上「vision 是 machine 能力」可接受。
- **memory root 目录边界**：元层记忆落成形态由 memory 工具决定（未落码），root 边界届时再定；本轮只做 machine 域。
