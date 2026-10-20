# 元层 file 工具落码（2026-10-21）

> 状态：**已落码**（`bf216c0`，已 push）。承 `directory-roots`（元层 LLM 访问归属）＋ YZ「意识过程→记忆沉淀」构想（元层工具 file）。本件记元层 file 的设计结论＋落码＋残留，不重复构想正文。

## §1 结论

- 元层 file = `read/write/edit` 三操作，root = **agent_root** 硬约束，纯路径转换（**不调 chroot**）。
- **根内路径转换**：模型看到 `/memory/a.md` → `agent_root/memory/a.md`；前导 `/` = agent root（**非文件系统根**）；`/etc/passwd` 天然落到 `root/etc/passwd`（读不到系统文件）；唯一越界手段 `..`，报 `OutOfRoot`。
- **复用 FsChannel**：加 `root` 参数（与 `base` 正交——`base`＝body.file 相对前缀＋绝对放行，`root`＝元层硬约束）；元层实例 = `FsChannel(LocalBackend(), root=agent_root)`，session=None。
- 工具 = `make_meta_fs_specs(channel)` 产 `meta_read_file/meta_write_file/meta_edit_file`（**无 id**），组装逻辑与 body 相同。

## §2 关键判定（why）

- **与 body.file 几乎一样，差异只三处**（backend / base / session），FsChannel 构造参数已覆盖 → 复用不新写。
- **前导 `/` 是 root 表示、不是文件系统根** → 不能「拒绝绝对路径」，而是 `lstrip("/")` 后 join root；`/etc/passwd` 被重映射进 root，天然读不到系统文件。
- **越界只可能是 `..`** → `_is_under`（`commonpath`）一行检查，**报错不压回**（压回会让模型静默读错文件，与 memory「撞名只报错不提示」一致）。
- **不调 chroot**：纯路径转换（`lstrip` + `join` + `normpath` + `is_under`），无系统级机制。

## §3 落码

- `impl/fs.py`：`OutOfRoot` 异常 ＋ FsChannel `root` 参数 ＋ `_resolve` root 分支 ＋ `_is_under`。
- `tools.py`：`make_meta_fs_specs`（三操作，无 id，根内路径描述）。
- 测试：`test_impl_fs`（root 6 项：相对 / 前导 `/` 等价 / `..` 越界 read+write / 绝对路径重映射 / write+edit）＋ `test_tools`（meta 3 项：read / 越界 / write+edit）。

## §4 残留（非 bug，留元层 LLM 收口）

- 命名 `meta_` 前缀待元层 LLM 收口钉（body 代码是 `read_file` 平铺、tool-design 定稿是 `file.read` 点分层，记号不统一是已知待定）。
- spec 层组装逻辑与 `make_fs_specs` 复制（约 40 行），DRY 留元层 LLM 收口。
- symlink 逃逸暂不防（`commonpath` 不 resolve symlink；agent 自己的 root 无 symlink 场景）。

## §5 遗留（范围外）

- **装配未接**：元层 LLM 未实现，注册给谁 / 工具集形态未定；`agent_root` 在 `AgentConfig` 无字段，装配时用 `agent_dir`（`Agent.__init__` 入参）。
- **root = agent_root（非 memory_dir）**：directory-roots 旧口径「元层只读记忆根目录」据此更新——YZ 10-21 明确「记录该 agent 所有相关文件的目录」。

## §被否

- 拒绝绝对路径（前导 `/` 是 root 表示、非文件系统根）。
- 压回 root 内（静默读错文件 → 改报错）。
- chroot 系统调用（纯路径转换即可）。
- 新写独立 file impl（MemoryStore 式）→ 复用 FsChannel。
- 元层 file 提前接装配（元层 LLM 未实现，接装配＝提前钉形态）。
