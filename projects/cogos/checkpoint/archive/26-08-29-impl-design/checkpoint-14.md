# checkpoint-14 — 审核 design-lm-service-min.md：视觉模态 + 模态/tier 路由进最小版

## 当前问题

共同审核最小版设计稿，发现过度依赖蓝本 lm-service（单 model per account、content 仅字符串），视觉模态缺位、路由被整体后置。判定：视觉是最基本能力，模态/tier 路由逻辑成本低，均应收进最小版。

## 关键结论（YZ 拍板）

1. **视觉模态进最小版**：`content` 支持 `string | content[]`，image 走 base64 内联。理由：模态是 model 抽象的正交维度（codebase.md 已认可），读图是 lm-service 本职非工具（checkpoint-13「读图非工具」），纯文本跑通后接视觉会导致 material 结构返工。
2. **舍弃「单 model per account」**：account 挂 model 清单，每 model 声明 capability `{tier, modalities}`。
3. **模态推断 + tier 路由在 lm-service 内做**（成本低 = 过滤 + 排序，之前误判为高，是错把 checkpoint-5 跨厂商全局能力表/降级账号切换/must 完整结构的成本安到单 provider 简单场景）。
4. **路由语义两条失败路径**：
   - 模态 = 硬约束，唯一硬失败路径：传图但 account 无视觉 model → 报错，不可降级（不能为保 tier 丢图）。
   - tier = 软倾向，`must` 显式开关（默认 `false`）：`must=false` 模态满足前提下降级到现有档位；`must=true` 找不到匹配 tier 直接报错。
5. **新增 router 组件**：基于 `messages` 的 `content[]` 推断模态 + tier + must → 选 model。独立组件，不塞进 config（config 只挂清单 + capability 声明）。
6. **降级留痕**：`routed` 升级带实际 tier + `degraded` 降级信号（checkpoint-5「降级留痕不静默」，最小版允许降级则必须能回答「实际 tier ≠ 请求 tier」）。
7. **术语对齐**：`material` 是 cu 层叫法（checkpoint-12），到 lm-service 边界叫 `messages`/`content[]`。
8. **客户端接口抽象（必做，YZ 拍板）**：立 `LmClient` async 接口，cog-runtime 只 import 它、不拼 http/不关心传输。边界——import 的是**客户端库**，不是进程内直调核心：lm-service 必须独立进程（配额账本/并发闸门/key 隔离单点，ckpt-3/4/5 已拍死），`LmClient` 内部封装进程间通信，底层 http/socket 对 cog-runtime 透明。接口 async 呼应 design-cog-runtime.md「进程内零同步阻塞」。蓝本 `lm_call` 是手动拼请求的调试 CLI，需抽成正式 async 接口。
9. **socket 后置（YZ 拍板）**：不含 peercred 的 http→socket 修改量小（服务端 site 换 unix + 客户端 `UnixConnector`），但 socket 价值（多用户/多进程可达、peercred 收紧）在最小版本机单用户裸跑无收益；接口抽象已保证传输隔离，故下版换 socket 只改客户端库内部 + 服务端 site，cog-runtime 零改动。
10. **account 保留且有实质语义（YZ 拍板）**：account = 真实身份账户，一个账户可申请多个 api key（sk-...），但这些 key 的**并发度共享**——并发闸门（semaphore/RPM）按 account 归口一起算，否则多 key 会绕过并发上限。故 account 是并发/限流的归口单位，必须保留（蓝本 scheduler `(provider, account)` 池化正是此语义）。account 名由用户自填有区分度信息（如手机号后4位等身份标识），不用 `main` 占位名，信息用户自己明白即可。
11. **modalities 用集合非单值（YZ 拍板）**：视觉 model 通常 text+image 都支持，声明 `["text","image"]`，非 `type=image` 单值。
12. **配置：yaml + CLI 写 key（YZ 拍板）**：secret 与 config 分离——api_key（secret）走 CLI `api-key add` 写入（不进 shell history、自动 chmod 0600，aws configure 风格）；model 清单 + capability（config）手写 yaml（可注释、可读、可 diff；json 无注释是硬伤，env 塞不下嵌套结构）。环境变量口子后置。
13. **对外契约 vs 内部实现分界（YZ 拍板）**：internal_key + LmClient 已把「选 model」封进服务端内部，上层只看 cheap/expensive/vision 维度。对外契约冻结（`chat(messages, tier, must)` 签名、归一响应、routed 带 tier/degraded、错误 category、key 句柄）；内部实现先简后优（key 绑单 account、account 内自动路由、tie-break=注册顺序取第一个）；后置优化（跨厂商/跨账号全局能力表、成本/轮询 tie-break、显式档位映射）不影响上层，因契约已冻结。
14. **modalities 去 text（YZ 拍板）**：chat model 必然支持 text（恒真基线），modality 定位是能力开关，恒真开关不声明。modalities 只声明增量（超出 text 的），最小版仅 `image`；text 隐含默认。配套约定显式写进设计稿，否则 `modalities: []` 易误读为「什么都不支持」。
15. **routed 去 provider/model（YZ 拍板）**：对外 `routed` 只含 `tier` + `degraded`，剔除 provider/model——否则与「屏蔽差异、上层不碰厂商 model」目的矛盾，且与 ckpt-5 目标态 routed `{tier, modalities, cost}` 形状冲突。provider/model 的调试价值由服务端 `calls.jsonl` 承担（记录当次调用的厂商/模型/详细信息）。
16. **错误通道形态（YZ 拍板）**：`LmClient.chat` 失败抛 `LmServiceError(category, message)` 异常，cu try/except 读 category → done(失败态)。符合 ckpt-2「业务出口=同步返回/抛异常」+ design-cog-runtime 约束 3/4。**待续：错误清单系统梳理**（可能出现哪些错误、各归哪个 category），/undo 后继续讨论。
17. **超时落地（最小版）**：沿用蓝本 120s 单总超时，超时归 `retryable` 类别；超时作 LmClient 可配参数后置。呼应 ckpt-12「短输出不流式+单总超时」。

## 已读要点

- `design-lm-service-min.md` 原稿 — 2.3 body `content` 为字符串；16 行「多模态 content[] 后置」；2.3 routed 仅 `{provider, model}`；2.1/2.3「单 model per account」。
- `codebase.md:12` — model 抽象两正交维度 tier × modality；`messages[]→{role, content[]}` 加 type 标签；MediaRef base64 内联。
- `checkpoint-5` — 路由模态（硬约束）> tier（软倾向）；降级留痕 routed；must/fallback 原为后置，本轮撤销后置、提前实现。

## 设计稿改动清单（→ 新版 design-lm-service-min.md）

1. 2.1 配置：account 挂 model 清单，每 model `{model, tier, modalities}`。
2. 2.2 internal_key：结构不变 `{id, group, provider, account, status}`，model 由路由决定。
3. 2.3 请求 body：`content` 改 `string | content[]`；新增 `tier`（`cheap|expensive`）、`must`（默认 false）。
4. 2.3 响应 routed：`{provider, model, tier, degraded}`。
5. 新增 3.x router 组件选 model；3.3 补视觉 content 映射（deepseek/openai）。
6. 16 行「不验证」清单删「多模态 content[]」「tier 匹配」「模态推断」。
7. 验收加「带图请求跑通一次」「模态+tier 路由 + 降级留痕」。
8. 新增 `LmClient` async 接口（客户端库，封装 http 传输）；socket 后置。

## 遗留 / 坑

- 蓝本 `deepseek.py`/`openai.py` 的 content 映射需确认视觉格式（openai 兼容 content[] + image_url base64；deepseek-vl 是否同构待实施确认）。
- 视觉 model 与文本 model 同 account 下共享 semaphore/RPM（scheduler `(provider, account)` 池化），视觉大请求挤占文本小请求并发——最小版不展开，后置配额/并发细分。
