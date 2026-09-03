# Handoff — cogos img-tool 原语实现 + 下一步 look_at（会话交接）

> 日期：2026-09-03。新会话加载本文 + `entries/2026-09-03-cogos-cogfunc-paradigm.md`（范式理论）+ 本体 `docs/vision-system-design.md` §14（视觉机制）+ `/home/zhengyp/work/A/checkpoint/codebase.md`（代码认知）即可恢复。当前处于「四层实现第一步 img-tool 落地完成，下一步 = cog-func（look_at）」。

## 本会话产出（勿翻案）

- 实现 img-tool 原语（四层第一步），全量 pytest 915 passed（基线 886 + 新增 29），飞书已通知 YZ。

## 四层进度

| 层 | 状态 |
|---|---|
| lm-service | ✅ 已有 |
| cog-unit / cog-runtime | ✅ 已有 |
| img-tool 原语 | ✅ 本会话实现 |
| cog-func（look_at） | ❌ 待实现 ← 下一步 |
| cog-actor | ❌ 待设计 |

## img-tool 实现要点（已完成，勿翻案）

- 位置：本体 `/home/zhengyp/work/A/cogos/cogos/img_tool/`（core.py / cli.py / stub.py / __init__.py）+ `tests/img_tool/`（29 测试）。
- **core.py**：同步纯逻辑。`estimate_peak` / `check_budget` / `budget_from_available` / `parse_meminfo` / `read_mem_available` / `parse_region`（归一化→像素 clamp）/ `pick_scale`（≤max_dim 恒 1.0 永不放大）/ `infer_format` / `do_info` / `do_extract`。常量 `EST_PEAK_CONST=48MB`、`MEM_FRACTION=0.6`（env `IMGTOOL_MEM_FRACTION` 覆盖）、`DEFAULT_MAX_DIM=800`。
- **cli.py**：`img-cli` 入口，子命令 `info <path>` / `extract <path> --out ...`。flock 计数信号量 `acquire_slot`（lockdir `/tmp/imgtool-locks-{uid}/`，N=`IMGTOOL_CONCURRENCY` 默认 1，jitter 50~200ms，`--wait-timeout` 默认 30）。stdout 单行 JSON；文件不存在/参数错→exit 1+stderr；业务错误态（图太大/空 region）→exit 0+`ok:false`。
- **stub.py**：async 封装 `info`/`extract`。`extract` 建 tempfile 作 `--out`→起子进程→读 bytes→unlink 清理→`{ok, data, width, height, scale, format}`。
- 依赖：pyproject 加 Pillow + `img-cli` script。**跑测试需 `python3.11`**（feishu 用 `X | None` 语法，3.9 import 报错）。

## 下一步：cog-func（look_at）

范围（「look_at 剖面」+ vision §14）：

- **能力集**：`info`/`extract` 注册为工具注入主 cu 上下文（tool registry 注册两个工具），复用 `CogRuntime.cu` 多轮续轮，不新建进程/服务/循环。
- **契约 prompt**：看清 = 缩 region 凑近（非放大）；看不清 → extract 更小 region；能力不足 → 第一人称转述「看不了」。
- **缓存句柄状态**（机制层维护，LLM 不感知 how）：`{path, full:{w,h}, seen:[{region,scale,conclusion}], calibration, budget}`。
- **视觉子系统机制**（vision §14，契约内嵌）：网格 4×4 定位 + `grid` 元数据（编号→坐标映射）、定标自校验探针、resize 鲁棒（精确给图 + usage 校准 + 相对定位）。

即 look_at = 一段看图契约 prompt + 缓存句柄结构 + 复用主 cu 循环，接 img-tool 两个原语。没有第四件东西。

## 关键文件

- 范式理论：`entries/2026-09-03-cogos-cogfunc-paradigm.md`
- 概念体系（三层 + 命名）：`docs/cogos-concept-system.md` §二/§九
- 视觉本体：`docs/vision-system-design.md` §14
- 代码认知：`/home/zhengyp/work/A/checkpoint/codebase.md`（已加 img_tool 段）
- img-tool 实现蓝图（已按此完成）：`/home/zhengyp/work/A/checkpoint/impl.md`
- 代码：`/home/zhengyp/work/A/cogos/cogos/img_tool/`

## 留白（下一步讨论/实现时定）

- look_at 的缓存句柄结构、契约 prompt 措辞、网格元数据注入方式均未落地，待实现时定。
- 视觉子系统「待拍板」项（纸载体、显著检测、f(W,H) 标定）见 vision-system-design.md 末尾，后置。
