# checkpoint-1 — img-tool 封顶安全尺寸（讨论）

## 当前问题

img-tool 的 scale 自动推档需要一个「封顶」阈值；此阈值由谁定、什么口径。

## 已读代码要点

- 无（未写代码，纯方案讨论）

## 关键结论 / 决策

- YZ 提示：封顶不应由 LLM 判断（主观、不稳定）；提议「底层提供可配 + 默认，调用者可改变」。
- 拆两层，别混：
  - **img-tool 的 max_dim = 入参（非边界）**：extract 的参数，带默认值；调用者不传用默认，传了用传的，img-tool 内部无不可逾越上限。scale 推档只按入参机械执行。
  - **厂商真实封顶**：会漂移（文档 ~384 vs 实测 443 token），非常量。由 look_at 用 usage 校准探针动态测，测得的安全值作为 max_dim 传给 img-tool。
- 方向：封顶既不是 LLM 主观判断，也不是写死常量/硬边界，而是「img-tool 参数带默认、上层 usage 校准覆盖」。

### 决策（YZ 拍板）

- max_dim 口径 = max 边长；默认值 **800**，跟随官方文档 ~800×800（文档 384 token vs 实测 443 @1000×750），官方声明或已含余量。

## 遗留 / 坑

- max_dim 默认值、口径（max 边长 vs max_pixels）待定。
- usage 校准探针细节归 look_at（cog-func 层），不落 img-tool。

---

## 能力探测预算比例（讨论，已定）

### 当前问题

「MemAvailable × 比例」作预算上限，比例取多少、是否每次读。

### 结论 / 决策

- 每次处理前读 MemAvailable（动态快照，OOM 取决于当前剩余非总量），不缓存——短命进程无状态 + 值动态，缓存过期会误判 OOM；读 /proc/meminfo 微秒级，相对冷启动百 ms + crop 285ms 可忽略。
- 真正「只做一次」的是公式与系数（宽×高×3 + 压缩 + 常数、比例），静态写死。
- 数值先写死常量（比例默认 0.6），调试时观察实测峰值与预算余量再调；可选环境变量 IMGTOOL_MEM_FRACTION 覆盖，不搞复杂。

---

## extract 输出形态（讨论，已定）

### 当前问题

extract 的图像字节怎么交给调用者：base64 进 stdout JSON vs 写文件。

### 结论 / 决策

- 用文件：调用者给完整输出路径（--out），img-tool 写入，调用者读 + 清理。与「句柄 = path」哲学一致，纯文件→文件原语。
- extract stdout 只回元数据 JSON `{ok, path, width, height, scale, format}`；info 信息量小，直接 stdout JSON。
- 输出格式由扩展名定（Pillow save 后缀），默认 JPEG，无损可写 .png。
- base64 编码归上层（look_at 读文件转 base64 / lm-service MediaRef 归一），不落 img-tool。
- 再加一层 thin stub（imgtool 包，调用者 import）：封装起子进程 + tempfile 建临时文件 + 传 --out + 读回 bytes + 清理，返回干净结果 `{ok, data, width, height, scale, format}`，解放调用者文件维护。
  - stub 是 async 接口（asyncio.create_subprocess_exec），因为 look_at 跑在 asyncio 事件循环；img-cli 内部仍同步。
  - flock 并发留在 img-cli 内，stub 不碰。
  - YZ：这两个细节（async / flock 归属）无论要不要 stub 都该考虑，只是现在落进 stub。

---

## 并发排队上限（讨论，已定）

### 当前问题

flock 抢不到槽时等多久放弃。

### 结论 / 决策

- 等待上限 = 参数（带默认，调用者可传）：`--wait-timeout`（秒）默认 30，img-cli 收，imgtool stub 透传。与 max_dim 同模式。
- 超时必须远大于 jitter sleep 间隔，否则第一次醒来就超时等于没排队：jitter sleep 取 50~200ms，默认 30s 可重试上百次。
- 不做额外下限校验，先默认值 + 参数，观察再调。
