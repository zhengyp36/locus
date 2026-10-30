# 模型面向文本多语言资源库（已落码收口）

## 结论

把 cogos 所有「面向模型的语言」从代码剥离到语言资源库：按语言分目录，英文 canonical + 中文全量，启动时 `--lang` 切换，配套 hash manifest 同步检查。**选型已与 YZ 讨论定稿**，拆 3 步 handoff 到 cogos 新会话执行。

## 定稿口径

- **范围 = 全部搬、一刀切、不留尾巴**：`prompts`（system prompt/birth task/capability note）+ `body`/`memory`/`toolbox` 三个 meta-tool schema + 三个 catalog 能力文本 + **impl 工具（tools.py）的 description/prompt 也搬**（YZ 拍板；它们当前不进模型——模型只经 catalog help/call，impl 只被 `registry.call` 路由——但属契约声明、且 toolbox 是待接线的遗留非废代码，故全搬）。
- **边界：结构留代码、字符串叶子进库**。参数名/type/required/enum/impl 绑定是契约不是语言；只有 description/summary/returns/prompt/group desc/note 进库。
- **英文 canonical（唯一事实源），中文 zh 全量译本**；翻译 = 目的驱动重写 + 审核，非字面机器翻译。
- **同步机制 = content-hash manifest**（per-key × per-lang，机器生成、入库、不手改）。四函数 `scan/check/view/commit`；测试 import `check()`。**不变量 = manifest == 当前文件（无未落账变化），不是「所有语言同步」**；同步只是 view/commit 输出的建议，判断交开发，允许只改一种语言。
- `--lang` 贯穿 `assemble()`/`run.py`，默认 `en`。

## 被否方案（why）

- **en canonical + zh 存 hash(en) 的 source fingerprint**：硬性要求 zh==hash(en)，对合法单语言改动误报；且假设 en 是源头，与「允许只改一种语言」冲突。
- **AI 自动翻译流水线**：prompt 措辞有语义漂移，须目的驱动 + 审核，不做全自动。
- **覆盖回退（partial + fallback）**：中文视图会混英文，破坏「读中文」目的；全套同步才是对的。

## 术语

- TextBundle = 语言资源加载器（`t("key")` 取字符串）。
- manifest = per-key × per-lang 的 hash 清单（落账依据）。
- stamp/commit（CLI 落账）= 把当前文件 hash 写进 manifest；与 git 提交是两个动作。

## 落点清单（已勘查）

- `config.py`: `render_system_prompt`(158)、`render_overview`(173, 当前死代码)。
- `assemble.py`: `_BIRTH_TASK`(54)、`_CAPABILITY_NOTE`(59)。
- `body.py`/`memory.py`/`toolbox.py`: `_DESCRIPTION`/`_PROMPT`/`_SCHEMA`/`_RUN_NOTE`。
- `body_catalog.py`/`memory_catalog.py`/`toolbox_catalog.py`: `GROUPS`/`NOTES`/`Capability(summary/returns/参数描述)`。catalog 现为模块级单例，需改工厂函数收 TextBundle。
- `tools.py`: 19 factory / ~41 impl ToolDef 的 `description`+参数描述+`prompt`。

## 验证

`pytest`（testpaths=tests, asyncio_mode=auto），基线 1363 passed，每步结束必须全绿。

## 执行结果（10-31）

三步由 3 个会话完成（step1/3 跑在 cogos、step2 跑在 locus，目录方向有误但代码落点正确），全量 1377 passed 6 skipped。机制与抽取忠实：`TextBundle.t(key,**fmt)`、`sync`(scan/check/view/commit + manifest per-file×per-key×per-lang sha256)、catalog→`build_catalog(texts)` 工厂、meta-tool→`_schema(texts)`、impl 工具 `texts=` 贯穿、`--lang`(默认 en)。zh 全量（5 文件 en/zh key 集逐文件相等），译文目的驱动、质量高、代码字面量保留英文。

**遗留尾巴（已核验，约 20 条机制/标签/错误文本未抽，破坏纯中文视图）**：
- `catalog.py` help 渲染标签 `:201/:231/:237/:235/:241/:245/:247/:251`（"Capabilities come in groups…"、"Params:"/"Returns:"/"required"/"optional"/"…more"）。
- `meta_tool.py` 错误串 `:49/:61/:70/:73/:78`（unknown command/path/capability、call needs name、not wired）。
- `tool_base.py` 校验错误串 `:252/:260/:272` + `_describe_params` 的 required/optional/(none)。
- `tools.py` reason 串 `:1334/:1340/:1343`（vision not wired / fs not exposed / no fs channel；`make_fs_specs` 同款）。
- `config.py` `render_overview`（死代码 `:187-193`）。
- 修法：补一个 `mechanism`/`errors` 分类进 texts 库，走同套 manifest，en+zh 各一份。

**流程教训**：handoff 应落到当前目录（locus＝读 AGENTS.md 的思考/工作目录），代码写到 cogos 本体下；不要 handoff 到 cogos（会读不到 locus 的协作 AGENTS.md）。

## 尾巴已补齐（10-31，全完成）

新增 `texts/{en,zh}/mechanism.json`（23 key），贯通 `catalog.py`/`meta_tool.py`/`tool_base.py`/`config.py render_overview`/`tools.py` reason 串。en/zh key 集逐文件相等（mechanism 23/23）、manifest 已落账（scan 空）、全量 1377 passed 6 skipped、zh 冒烟（help 输出/参数/返回/错误串）纯中文，代码类型 token（string/number 等契约）正确保留英文。**i18n 支线收口。**

## 遗留（已记录，未收）

- `tool_base.py:133` `f"unknown tool {name!r}"`（`ToolRegistry.execute` 的 `unknown_tool` error_detail）＋ `tool_base.py:113` `"tool error"`（`call` 兜底 reason）两条注册表级错误串，收尾会话发现但不在清单、未动。属真尾巴（人类可读、会进模型），但极小且只在防御/兜底路径。判断边界：`error_class`（unknown_tool/bad_args/tool_bug）是机器错误码、`str(e)` 是异常原文，留代码正确；仅上述两条静态散文待收。

## 执行记录（3 步已全部完成）

- **Step 1-2（已落）**：`texts/{lang}/` 框架（`bundle.py`/`sync.py`/`__init__.py`，四函数 scan/check/view/commit）+ `texts/en/{prompts,body,memory,toolbox}.json`；`config.py`/`body.py`/`memory.py`/`toolbox.py` 抽 schema 文本；三个 catalog 改工厂 `build_catalog(texts)`；`assemble.py` 穿 texts。基线 1377 passed, 6 skipped。
- **Step 3（本步，已落）**：`texts/en/impl.json`（167 key）+ `texts/zh/*` 全量（5 文件 × 402 key = 402，与 en 一一对应）；`tools.py` 19 个 `make_*_spec` factory 全部加 `texts=None`（默认 en）并抽 description/参数描述/prompt 到 `impl.<name>.{description,param.<p>,prompt}`；`assemble.py` 6 处 impl 调用穿 `texts=texts`。结构（参数名/type/required/enum/impl 绑定）留代码。
  - 特记：`impl.coord.description` 原文含中文 `@原图`，en canonical 改 `(original-image space)`；两处 limit 描述 `f"...{DEFAULT_LINE_LIMIT}...{MAX_LINE_LIMIT}"` 改模板 `{default}/{max}` 占位符（`texts.t(key, default=..., max=...)`）。
  - `make_fs_specs` 共享 `pair`（id/path）与 `make_meta_fs_specs` 共享 `path_prop` 均复用 `impl.read_file.param.*` / `impl.meta_read_file.param.path` 的 key（三工具同文）。
- **验证**：`commit()` 落账（新增 167 en-impl + 402 zh = 569 条）、`check()` 绿、zh 冒烟（`TextBundle("zh")` 全 402 key 可渲染 + make_body/memory/toolbox/impl spec 在 zh 下构造成功）、全量 `python3.11 -m pytest` → **1377 passed, 6 skipped**。
- **遗留**（不属本步范围，报 YZ）：`config.py:12 UNKNOWN_TIME = "未知时间"` 死代码（未引用）；`make_vision_specs` docstring 与 `coord` 相关注释仍含 image_ctx 字面量 `@原图`（代码注释非模型面向文本）。
- 已 commit `ac3d449`（10-31 收口提交）。
