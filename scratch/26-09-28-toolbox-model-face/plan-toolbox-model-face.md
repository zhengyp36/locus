# plan｜cogos toolbox 模型面修订（run 语义 + cancel 暴露 + 参数名）· 2026-09-28

> **状态**：讨论已收口（YZ 同意），待执行会话。工作单目录 `scratch/26-09-28-toolbox-model-face/`。
> **权威**：`/home/zhengyp/work/B/cogos/docs/design-agent-tools.md`（§5.1 exec 语义 · §5.2 忠实输出靠重定向+文件 · §5.4 notify · §19 模型面命名）。
> **记忆依据**：`/home/zhengyp/work/B/locus/projects/cogos/entries/2026-09-28-cogos-toolbox-run-semantics.md`（N3/N4）· `...-model-prior-naming.md` · `...-behaviour-probe.md` · `...-fix.md`。
> **工位**：B。cwd `/home/zhengyp/work/B/cogos`。

## 0. 目标（锚）

- 消除 `run` 的"完成推断／静默截断"：`computer.command.run` 回归**发起即返回**（不取值），取值收敛到读类。
- 补全漏暴露的工具原语（cancel 类）。
- 模型面参数名对齐模型先验（`target→to`），不破坏跨能力一致。
- **不动 impl 语义**；只改 catalog/模型面 + run 组合。

## 1. 三界（防漂核心）

### 已定·照做（勿再议）
- `run` **保留名字**，改"发起即返回"、**不返回值**；取值＝`computer.file.read`（命令自己重定向）＋ `computer.command.observe`（屏态）；help 写清用法。
- `interrupt` **不并入** `cancel`；有 job 句柄的取消统一 `cancel`、**归类按发起面**。
- notify **不新建工具**；暴露 `run` 的**可选 notify 参数**（`term.notify` 已实现，机制只转发、**绝不自动检测命令结束**）。
- `to` **整族改**（`communication.message.send`／`communication.file.send`），**impl 不改**，catalog 层映射。
- 模型面名**不泄漏机制名**（同 fix 3 删 help"绑定"行）。

### 需自决并记录
- cancel 的 path/参数名（拟 `computer.web.cancel`／`communication.file.cancel`）、别名映射落点、help 文案。

### 必须停回讨论（不许自决）
- **批 0 验证**显示模型用不了 redirect+read 取值 → 停。
- 任何触及设计原则/主线的岔路（心跳、token 换判据、改目标）。
- 改名 `exec` 等已否项。

## 2. 批次（一批一会话；每批收工写 `handoff-0N.md`）

- **批 0｜验证闸（先于一切代码）**：用 `scripts/exp_agent_behaviour_probe.py` 验证模型能否用"发起即返回的 run + read/observe"完成取值。判据：能稳定取到输出、往返可接受。**不合即停回讨论**。
- **批 1｜N4**：加 `computer.web.cancel`(web_cancel) / `communication.file.cancel`(phone_cancel) catalog 条目 + 参数名 + help。
- **批 2｜N3**：run 去取值、删 `_run_composed`/`_observe_settled`、暴露 notify 参数、time_form 修正、help；**保留会话懒开 + `_wait_ready`**。
- **批 3｜`to`**：catalog 参数别名映射 + 整族改 + 复跑。

## 3. 验收（从目标推）

- 无"屏稳定"启发式（机制不再猜完成）。
- 模型能完成"跑命令取输出"（harness 复跑成功率/往返数）。
- `web.cancel`/`file.cancel` 可被调（单测或 harness）。
- `to` 首猜命中率↑（复跑对比）。
- 每批：`python3.11 -m pytest tests/agent`（＋全量）绿；harness n≥10。
- **不用仓库自写 e2e 当验收**；真机 e2e 仅在需要时。

## 4. 被否（勿再议）

token 换判据 · 加心跳/tick · 保留 run 取值+屏稳定 · 独立 notify 工具 · 每次命令自动 notify · 改名 exec · 模糊纠错/意图层 · 往常驻总览加能力清单。

## 5. 纪律 / 环境

- 不得 `--auto`；提交前跑测试；默认自主提交/推送（`rules/task.md`）。
- 发现设计问题 → 记 checkpoint，**不悄悄改设计**。
- **代码身份**：必须从 `/home/zhengyp/work/B/cogos` 的 cwd 跑，先验 `python3.11 -c "import cogos; print(cogos.__file__)"` 指向 B。
- **服务单例**：harness 连现有 lm-service，**不自起第二个**。
- 链式交接设上限。

## 6. 通知 YZ

- 完成或遇问题 → `/home/zhengyp/work/B/locus/tools/feishu_notify.py "..."` 通知 YZ（fire-and-forget）。

## 7. 产出

- cogos 代码提交（push）；locus 记忆更新（entries/current/index）。
