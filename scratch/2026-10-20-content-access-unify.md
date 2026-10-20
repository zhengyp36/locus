# 内容访问统一机制 · 方案（2026-10-20）

> 状态：**已落码（本轮 machine 域，commit `ee9f0ba`，已推送）**。承 `2026-10-19-selfdrive-body-discussion.md` 的「body 其余组待续」+ A 类落码（body.vision 挂 `see/mark/coord`）后检视发现的 bug：**vision `PATH` 路径根 ≠ file 机器根**。
> 术语：`content access`（内容获取）、`content root`（内容域）、`FIG`（本地缓存句柄）、`state root`（工具状态根）。
>
> **10-20 检视修订（三点，已与 YZ 对齐）**：
> 1. session 走 **needs_session 注入**（与 file 同构），不引入「装配层注入 get_bytes 闭包」。
> 2. vision 取图设**字节上限**（`stat size` 预检，解码前拒绝）。
> 3. **砍掉 `Capability.root` 字段**（无消费方 + 粒度放错，见 §root 字段被否）。

## 问题（为何统一）

1. `file.read` 走 fs channel，相对**机器根**（`machine_root`，后端 `LocalBackend`/`SftpBackend`）。
2. `vision.see PATH:<path>` 走 `image_ctx` 的 `add_src`，硬编码 `Path(path).read_bytes()`，相对**进程本地 cwd**。
3. 元层 `file`（未落码）应相对 **agent 记忆根**。

三个「根」散落三处。本地部署（`machine_root=work_dir`）下前两者重合，一旦 sftp 远程或元层 file 落码即踩坑。

## 抽象：统一「内容获取」，不统一「消费」

- **内容获取（统一）**：`get_bytes(path) -> bytes`，域由封装层决定。
- **内容消费（各自 impl）**：
  - `file.read` → get_bytes 后行分页/截断（现状已如此）。
  - `vision.see PATH` → get_bytes 后解码、落本地缓存、mint FIG（替换 `add_src` 读字节那一步）。
  - `vision.see FIG` → 不走 get_bytes，命中缓存（`images/<md5><ext>`）。

区分（已对齐）：

- **content root** = 能力访问「文件对象」的 base（machine/memory）。
- **state root** = 工具自己持久化在哪（image_ctx 的 `Domain.root`、DraftStore、Spool），impl 装配注入，不进 content root 语义。

## 分层：session 属于工具封装层，impl 通用

**session 是封装层概念，底层 impl 通用**（现状已如此，vision 需对齐）：

- 底层 `FsChannel(backend, base)` 不接 session；`get_bytes(path)` 只接 path（`fs.py:306`）。
- 封装层 `make_fs_specs` 的 `_read(id, path)` → `manager.get(id).fs`（`tools.py:61-78`）。
- meta_tool 用 `needs_session` 把 id 注入 `call_args`（`meta_tool.py:87-91`）。

vision 的 bug 本质 = `make_vision_specs` 这个封装层漏了「拿 session → 取 fs」这一步。修法 = `vision.see` 标 `needs_session=True`，`_see(id, ref, ...)` 在 PATH 分支拿 `session.fs.get_bytes`——与 file 完全同构，机制层零改动。

## FIG 是缓存句柄（与 file 的本质差异）

`add_src` 现状：`Path(path).read_bytes()` → 按 md5 落 `images/` → mint FIG。所以 `PATH` 回源、`FIG` 命中缓存不回源。file 无缓存（按行回源）、vision 必须缓存（图解码后回源无意义）——「附件投影/句柄」的自然结果，非缺陷。

## 关键事实（已核实，供实施直接引用）

- **`FsChannel.get_bytes(path)` 已存在**（`cogos/agent/impl/fs.py:306`），注释 "transfer-facing raw byte access"——走 `_resolve(base)` + `_read_all(cap=False)` + backend，正是现成的内容获取接口。**复用它，不新建 `content.py`**。
- `FsChannel` 构造（`impl/terminal.py:509` `_make_fs`）：本地 `base=str(machine_root)`；远程 sftp `base=""`。挂 `session.fs`（懒创建，`impl/terminal.py:208`）。
- vision 装配点 `app.py:299` `make_vision_specs(self._work_dir / "vision")`；`make_vision_specs`（`tools.py:1229`）现状只接 state root，无 content 访问。
- `add_src`（`image_ctx/domain.py:101`）幂等键 = `str(path)`，`Source.path` 展示给模型。`image_ctx/tools.py:122` 的 `see` 里 PATH→`add_src`、FIG→`find_fig`。
- file 的 session 注入链：`read_file` impl `_read(id, path)` → `_channel(id)` → `manager.get(id).fs`（`tools.py:61-78`）。vision 对齐即复用此链。

## 落地形状（已定）

1. **机制层**：**零改动**。复用 meta_tool 现有 `needs_session` 注入（`meta_tool.py:87-91`）。
2. **数据层**：`body_catalog.py` / `toolbox_catalog.py` 的 `vision.see` 标 `needs_session=True`（PATH 回源需拿 machine fs；`file.*` 已标）。
3. **封装层**：`make_vision_specs(root, manager=None)`；`_see(ref, ..., id=None)` 的 PATH 分支：解析 ref 得 path → `manager.get(id).fs` → 按 `stat size` 预检上限 → `await fs.get_bytes(path)` → `add_src` from-bytes「预热」→ 走原 `see`（PATH 分支幂等命中预热后的 source）。**`manager` 缺省时 PATH 回退本地读**（向后兼容，供 screen selftest 等本地绝对路径调用方；生产 `app.py` 恒接 manager）。
4. **底层**：`FsChannel.get_bytes` 加可选 `max_bytes` 参数（默认不限制 = transfer 语义不变）；vision 传图上限，走 `_read_all` 的 `stat` 结果预检（解码前拒绝）。

## 改动清单（文件级，已落码 commit `ee9f0ba`）

1. `cogos/agent/body_catalog.py` / `toolbox_catalog.py`：`vision.see` 显式 `needs_session=True`。
2. `cogos/image_ctx/domain.py`：`add_src` 支持「from bytes」——**向后兼容**：新增可选参数 `contents: bytes | None = None`，默认 None 走原 `Path.read_bytes()`。幂等键保持 `str(path)`，`Source.path` 仍展示模型给的**原始 ref**（机器根相对路径，不 resolve，与 file.read 返回口径一致）。**勿改现有签名**（`tests/image_ctx/test_p1.py:29` 等 P1/P2/P4 验收直接依赖 `add_src(domain, path)`）。
3. `cogos/agent/tools.py`：`make_vision_specs(root, manager=None)`，`_see` 加 `id` 参数；PATH 分支回源（size 预检 → get_bytes → add_src from-bytes 预热）。
4. `cogos/agent/impl/fs.py`：`get_bytes(path, *, max_bytes=None)`，`max_bytes` 非 None 时 `_read_all` 按 `stat size` 拒绝。
5. `cogos/agent/app.py`：`make_vision_specs(self._work_dir / "vision", manager=self._computer_manager)`。
6. 测试：
   - `tests/agent/test_body.py`：补 vision PATH 相对机器根（非 cwd）的用例。
   - `tests/image_ctx/test_p1.py`：补 `add_src` from-bytes 用例（幂等、md5 落缓存）。
   - `tests/agent/test_tools.py`（若有 vision spec 测试）：补 `make_vision_specs(manager=...)` 路由 + 图上限拒绝用例。

## 待定点（已定 / 留后）

- ✅ **vision 走同一 backend**：复用 `FsChannel.get_bytes`（远程图 = get_bytes 拉到内存→落缓存→解码，自动支持）。已定。
- ✅ **vision 取图设字节上限**（10-20 检视修订）：值已定 `MAX_IMAGE_BYTES = 64MB`（`tools.py:25`）。理由：图比文本大合理、render 层另有 `check_budget`（`render.py:170-177`）兜底解码后 OOM，get_bytes 上限只防「读入超大原始字节/假图」。在 `stat` 后、`read_bytes` 前拒绝（零成本）。
- ⏸ **needs_session 副作用（已知，接受）**：`vision.see` 标 `needs_session` 后，FIG 分支也会先 `session.get()` 开默认 terminal（虽然 FIG 不用 fs）。与 file 同构（file 整个能力 needs_session），语义上「vision 是 machine 能力、依赖 machine session」，可接受。
- ⏸ **memory root 目录边界**：元层记忆落成什么形态由 memory 工具决定（未落码），root 边界届时再定；本轮只做 machine 域。

## root 字段被否（10-20 检视）

原方案给 `Capability` 加 `root: str = "machine"`，用于声明能力所属内容域。**砍掉**，理由：

1. **无运行时消费方（死字段）**：root 不进 help（原定）、meta_tool 不读、启动一致性校验已降级取消。装配层接 get_bytes 是按具体 path 人肉写死，并不读 `Capability.root`。砍完校验与渲染后，root 只剩一个无代码读取的字符串——踩中「形状自证 > 标签声明」判例（`time_form` 同款）。
2. **粒度放错**：域边界是 toolset/catalog 级（body 全 machine、元层 file 全 memory），不存在单个 Catalog 内混域。若未来真需要区分域，放 Catalog/toolset 级或装配层，不逐能力声明。

本轮只有一个域（machine），装配层把 machine fs 接给 vision 是写死一件事，不需要声明性字段。等 memory 域落码时按「域边界 = toolset 边界」自然处理。

## 与清理线的关系（2026-10-20 追加）

本轮讨论收敛出**另一条工作线**：草稿（scratch_* 工具面）是 file 的冗余抽象（按 id 而非 path），transfer 是草稿的衍生物，两者都是不对模型暴露的死代码；web 长结果依赖 draft 且读不回。结论＝删 draft+transfer（打 tag 找回）、web 重实现为 `WEB:<id>` + 缓存目录（同 vision 的 FIG+images 模式）。**已落码 `e5dbcda`（tag `pre-prune-draft-transfer`）**。

对本文档的影响：`fs.py:306` `get_bytes` 的注释 "transfer-facing raw byte access" 在删 transfer 后要改为内容访问语义（保留接口本身）。

## 实施判断

- **可直接实施**，**本轮只做 machine 域**：目标是修「vision PATH 根 ≠ file 根」这个已存在 bug，只动改动清单 1–6 的 machine 部分。memory 域 + 元层 file 是另一个目标，留到元层 file 落码时。
- **新会话可实施**：锚点已在上方「关键事实」列出（文件+行号+现状）。唯一待定的是图上限值（`MAX_IMAGE_BYTES`），可自决（倾向 64MB，或沿用 file 的 10MB）。

## 被否 / 已排除

- 笼统「工具路径可配」：混淆 content root 与 state root，已拆开。
- 新建 `content.py` 抽 `get_bytes`：`FsChannel.get_bytes` 已存在，直接复用。
- 改 vision 的 Domain root 来配根：Domain root 是状态目录，与 PATH 寻址根两码事。
- **装配层注入 `get_bytes` 闭包**（原方案）：被 session 分层否决——`get_bytes` 是底层通用接口，不该作为注入物；要注入的是 session，走 meta_tool 现有 `needs_session` 机制，与 file 同构、零新机制、无装配时序问题。
- **`Capability.root` 字段**（原方案）：无消费方 + 粒度放错，见 §root 字段被否。
- 改 `add_src` 现有签名：会牵连 P1/P2/P4 验收，改为向后兼容的新增参数。
