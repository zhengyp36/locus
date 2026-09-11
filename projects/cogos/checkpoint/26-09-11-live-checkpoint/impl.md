# impl — img-tool 原语实现（交接新会话写代码）

> 状态：方案已全部拍板（见 checkpoint-1.md）。本文件是给新会话的实现蓝图，照做即可。
> 代码位置：本体仓库 `/home/zhengyp/work/A/cogos/`（包 `cogos/`）。

## 目标

实现 img-tool：视觉取图底层原语，纯文件 io、短命子进程、无状态。两个入口 `info` / `extract` + thin stub。这是四层（lm-service → cog-unit → cog-func → cog-actor）的第一步，只做 img-tool，不做 look_at/cog-func。

## 开发过程规则

- **写 TODO**：开发过程中未定/待调/暂缓项，在代码里标 `# TODO:`，不口头吞掉。
- **codebase 就地更新**：过程中对代码有新理解 → 就地更新 `../checkpoint/codebase.md`（认知变了就修正、过时去掉，不追加流水账）。
- **完成时飞书通知 YZ**：img-tool 实现 + 测试全绿后，跑 `python /home/zhengyp/work/A/locus/tools/feishu_notify.py "<文本>"`（默认 YZ），然后停下等指令。

## 拍板结论（勿翻案）

- `max_dim`：参数带默认，默认 **800**（max 边长口径，跟随官方文档）。
- 能力探测：每次处理前读 `MemAvailable`，比例 **0.6** 写死常量 + 可选 `IMGTOOL_MEM_FRACTION` 覆盖。
- extract 输出：写文件（调用者给 `--out` 完整路径），stdout 只回元数据 JSON；格式由 `--out` 后缀定；base64 编码归上层。
- 并发：flock 计数信号量，`IMGTOOL_CONCURRENCY`（默认 1），jitter sleep 50~200ms，`--wait-timeout`（默认 30s）。
- thin stub（`imgtool`）：async 接口封装起进程 + tempfile + 读回 + 清理，返回 `{ok, data(bytes), width, height, scale, format}`。
- flock 并发落在 img-cli 子进程内，stub 不碰；stub 用 `asyncio.create_subprocess_exec`。

## 文件划分

```
cogos/img_tool/
  __init__.py    # 导出：extract（async stub）、info（async stub）
  core.py        # 同步纯逻辑（可单测）：能力探测、region 解析、scale 推档、do_info/do_extract
  cli.py         # img-cli 入口：argparse + flock 抢槽 + 调 core + JSON 输出
  stub.py        # async 薄封装：起 img-cli 子进程 + tempfile + 读回 + 清理

tests/img_tool/
  __init__.py
  conftest.py    # fixture：用 Pillow 造小图（tmp_path）
  test_core.py   # 能力探测 / region 解析 / scale 推档 / do_extract 纯逻辑
  test_cli.py    # subprocess 跑 img-cli（info / extract / 抢槽超时）
  test_stub.py   # stub 异步封装（含 mock 子进程）
```

命名约定：组件/CLI 短横线 `img-tool`/`img-cli`；Python 包下划线 `img_tool`（与 `lm_service`/`cog_runtime` 一致）。

## 依赖变更

`pyproject.toml` 的 `[project] dependencies` 加 `"Pillow"`。当前没有 Pillow，必须加。

`[project.scripts]` 加一行：`img-cli = "cogos.img_tool.cli:main"`。

## core.py 逻辑（同步，无 asyncio）

### 能力探测

```python
EST_PEAK_CONST = 48 * 1024 * 1024   # 覆盖 Python/Pillow/JPEG 熵解码中间缓冲，调试观察调
MEM_FRACTION = float(os.environ.get("IMGTOOL_MEM_FRACTION", "0.6"))
```

- `Image.open(path)` 惰性读 `size`/`format`/`mode`（不 load）。
- 预估峰值 `est_peak = width*height*3 + file_size + EST_PEAK_CONST`。
- 读 `/proc/meminfo` 的 `MemAvailable`（kB），`budget = int(MemAvailable_kb * 1024 * MEM_FRACTION)`。
- 若 `est_peak > budget` → 返回错误态 `{"ok": False, "error": "image too large: needs ~{est_peak_mb}MB, budget ~{budget_mb}MB"}`（业务错误，非异常）。
- 参考实测：4000×3000 图理论像素缓冲 36MB，crop 原生实测峰值 67MB。

### region 解析

`region` = 归一化 `(x, y, w, h)` ∈ [0,1]，默认 `(0, 0, 1, 1)` = 全图。

```python
left   = clamp(round(x * W), 0, W)
top    = clamp(round(y * H), 0, H)
right  = clamp(round((x + w) * W), left, W)
bottom = clamp(round((y + h) * H), top, H)
```

### scale 推档

crop 后区域最长边 `long_side = max(box_w, box_h)`：

- `long_side <= max_dim` → scale = 1.0（原生，不缩，永不放大）。
- `long_side > max_dim` → `scale = max_dim / long_side`（<1），降采样到 max_dim 内。

实现用 `crop.resize((round(w*scale), round(h*scale)), Image.Resampling.LANCZOS)`。设计原文是 draft 离散档（1/2/1/4/1/8），落地先用连续 resize 到 max_dim（简单、格式无关、满足「精确给=缩到封顶内」），scale 输出为实际比例。若 YZ 坚持离散 draft 档再改（注意：draft 只对 JPEG 高效，PNG/WebP 需全 decode）。

### do_info(path)

返回 `{"ok": True, "width", "height", "format", "mode", "file_size", "est_peak_mb", "budget_mb"}`；文件不存在/无法打开返回 `{"ok": False, "error": "..."}`。

### do_extract(path, region, max_dim, out)

1. 能力探测，超限返回错误态。
2. `Image.open` → region → crop（原生像素，触发全图 decode）→ scale 推档 → resize（如需要）。
3. 格式由 `out` 后缀推断（`.jpg/.jpeg`→JPEG，`.png`→PNG，缺省 JPEG）；`crop.save(out, format=fmt)`。
4. 返回 `{"ok": True, "path": out, "width", "height", "scale", "format"}`。

## cli.py（img-cli 入口，同步）

### flock 计数信号量（先抢槽，再干活）

- lock 目录：`/tmp/imgtool-locks-{os.getuid()}/`（`os.makedirs(exist_ok=True)`）。
- `N = int(os.environ.get("IMGTOOL_CONCURRENCY", "1"))`，slot 文件 `slot-0..slot-(N-1)`。
- 抢槽循环（`fcntl` + `random` + `time`）：

```python
deadline = time.monotonic() + wait_timeout
slots = list(range(N)); random.shuffle(slots)
while True:
    for s in slots:
        f = open(f"{lockdir}/slot-{s}", "a+")
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            f.close(); continue
        # 抢到：持 f 直到进程退出，flock 随 fd 关闭/进程退出内核自动释放（崩溃安全）
        return f
    if time.monotonic() >= deadline:
        raise SystemExit("busy: timeout waiting for slot")
    time.sleep(random.uniform(0.05, 0.2))
```

- `wait_timeout` 来自 `--wait-timeout`（默认 30）。超时必须远大于 jitter（30s vs ≤0.2s，充足）。

### 子命令

```
img-cli info <path> [--wait-timeout S] [--mem-fraction F]
img-cli extract <path> --out <path> [--region x,y,w,h] [--max-dim N] [--wait-timeout S] [--mem-fraction F]
```

- `--region` 默认 `0,0,1,1`，`--max-dim` 默认 800，`--mem-fraction` 覆盖环境变量。
- 结果 stdout 单行 JSON（`json.dumps(..., ensure_ascii=False)`）。
- 退出码约定：
  - `0` + `{"ok": true/false, ...}`：业务成功或「图太大」错误态（LLM 可转述）。
  - `1` + stderr：参数错、文件不存在、抢槽超时（异常，非业务错误态）。
- 抢槽超时走 `SystemExit("busy: ...")`（stderr + exit 1）。

## stub.py（imgtool 异步薄封装）

```python
async def info(path, *, wait_timeout=None, mem_fraction=None) -> dict
async def extract(path, *, region=(0,0,1,1), max_dim=None, out=None, wait_timeout=None) -> dict
```

- `extract` 内部：`tempfile.NamedTemporaryFile(suffix=..., delete=False)` 建临时输出文件 → `asyncio.create_subprocess_exec("img-cli", "extract", ...)` → 读 stdout JSON → 读 `--out` 文件 bytes → `os.unlink` 清理 → 返回 `{"ok": True, "data": bytes, "width", "height", "scale", "format"}`。
- `info` 直接起子进程读 stdout JSON。
- 子进程失败（非零 exit）→ 返回 `{"ok": False, "error": stderr}`。
- 找 img-cli：优先 `sys.executable -m cogos.img_tool.cli`（开发环境免安装），fallback 到 PATH 上的 `img-cli`。可配环境变量 `IMGTOOL_CLI` 指定命令。

## 测试思路

总体：分三层测，全用真实 Pillow + 真实子进程（纯本地处理，不依赖外部服务，无需 mock LLM）。

### 可测性前提：core 拆纯函数

- `estimate_peak(w, h, file_size) -> int`：纯函数。
- `check_budget(est_peak, budget) -> bool`：纯函数，测边界（等于/略超/略低）。
- `parse_region(x,y,w,h, W,H) -> box`：纯函数。
- `pick_scale(long_side, max_dim) -> float`：纯函数。
- `_read_mem_available() -> int`：薄 IO，测试 monkeypatch 或喂 fake meminfo 文本测解析。
- `acquire_slot(lockdir, n, wait_timeout)`：并发逻辑单独抽出，好单测。

### core（单测，快）

- 能力探测：estimate_peak 公式、check_budget 边界、MemAvailable 解析（fake meminfo 文本）。
- region：归一化→像素、clamp（`x+w>1`、round、负值、零宽高）。
- scale：**永不放大**——小图 crop 后 scale 必须 1.0、尺寸不变；大图降采样后长边 = max_dim。
- 格式推断：`.jpg/.jpeg/.png/无后缀`。

### cli（子进程，集成）

- `info`/`extract` JSON 输出正确、exit code 约定：图太大 → `0 + ok:false`；文件不存在 → `1 + stderr`。
- flock：以 `acquire_slot` 单测为主；端到端冒烟——N=1 时手动占住 slot 再起第二个进程，配 `--wait-timeout 0.1` 验证超时退出。
- conftest：`@pytest.fixture` 用 Pillow 造小图（如 `Image.new("RGB", (64, 48))` 存 tmp_path），供各测试。
- 跑法：`subprocess.run([sys.executable, "-m", "cogos.img_tool.cli", ...])`。

### stub（async）

- 正常：`extract` 返回 bytes + 元数据，**断言临时文件已清理**（tmp 文件不存在）。
- 失败：mock 子进程非零退出 → `ok:false`。
- 子进程路径解析用 `sys.executable -m cogos.img_tool.cli`（开发免安装）。

### 重点坑

- flock 崩溃安全（进程被 kill 后锁自动释放）难在 CI 稳定测，靠 `acquire_slot` 单测 + 手工验证，不强求自动化。
- `_read_mem_available` 必须可注入，否则测试依赖真实 `/proc/meminfo` 不稳。
- 并发「排队」端到端难稳定复现（img-cli 短命跑得快），并发正确性重心放 `acquire_slot` 单测，CLI 层只做超时冒烟。

跑法：`pytest`（`asyncio_mode = auto`，与现有一致）。

## 验收

1. `python -m cogos.img_tool.cli info <图>` 输出尺寸 + 预算 JSON。
2. `python -m cogos.img_tool.cli extract <图> --out /tmp/o.jpg --region 0.5,0.5,0.5,0.5` 输出 `{ok, path, scale=1.0, ...}`，文件生成。
3. 大图超预算 → `{"ok": false, "error": "image too large..."}` + exit 0。
4. `await cogos.img_tool.extract(...)` 返回 bytes，临时文件已清理。
5. 全量 `pytest` 无回归（基线 886 passed）+ 新增 img_tool 测试绿。

## 遗留 / 坑

- EST_PEAK_CONST、MEM_FRACTION、max_dim 默认 800 均为经验初值，调试时观察调整。
- draft 离散档 vs 连续 resize：先连续 resize，若需 JPEG draft 省内存再演进。
- 本步不碰 look_at / cog-func / cog-actor，不注册进 agent registry。
- 找 img-cli 的路径解析（-m vs PATH）注意开发/部署差异。
