# checkpoint-11 — 多模态调研 + LLM-Service 接口与 model 抽象

## 当前问题

LLM-Service 动手前，多模态成为必答题，需厘清接口形态（输入/输出/怎么用）与 model 封装方式。

## 调研结论（2026-08，各厂商多模态支持）

- 图片：8 家全覆盖（OpenAI / Anthropic / DeepSeek / Gemini / Qwen / GLM / Kimi / Grok）
- 视频：Gemini / Qwen / GLM / Kimi
- 音频：仅 Gemini 原生（OpenAI / xAI 走独立 realtime / voice API）
- PDF：Claude 原生 `document`；Gemini 走 File API；其余转图
- 内容块格式三系：OpenAI `image_url`/`file`；Anthropic `image`+`source`；Gemini `inline_data`/`file_data`
- DeepSeek 8-21 上线 `deepseek-v4-flash-vision-exp`（仅图片、实验），同时暴露 OpenAI + Anthropic 双兼容面；详情锚 `https://api-docs.deepseek.com/guides/vision/`。V4 系列仅 pro / flash 两个文本模型，vision 只长在 flash 档（无 pro-vision），证明模态能力是点状分布。

## 关键结论（概念收敛）

- 信息为主干；语言是信息的离散符号编码（可组合/可交流/可元表征），图片/声音是连续感知编码。
- LLM-Service = 无模态偏见的信息管道：输入一组信息、输出一组信息；语言只负责钉关系（role/字段/schema），不预设主次。
- 协议稳定不变：`messages[] → {role, content[]}`，加模态 = 加 content item 的 type 标签，外层结构不动。

## 接口设计（YZ 已认可）

- 沿用 message/content 数组；type 是 llm-service 自定义内部标签（text/image/audio/file），适配器翻译厂商标签。
- content item 统一 `{type, ...}`；媒体来源统一 MediaRef `{kind: base64|url|file, media_type, data}`。
- model 恢复为请求可选覆盖字段（不焊死在 key），但只在 key 授权集合内选；调用方不暴露厂商 model。
- 响应返回 `content[]` + `usage` + `routed`（实际档位+模态+成本），不返回厂商 model。

## model 抽象（能力抽象，YZ 认可方向）

- 两正交维度：档位 tier（cheap/expensive，强度轴，可扩展标签）vs 模态 modality（布尔开关，能力有无）。
- 模态走「能力声明 + 自动推断」：model 注册带 `{modalities:[...]}`，路由按 content 实际模态自动筛，调用方不指定"我要 vision"。
- 申请 internal_key 时配 `tiers`（cheap/expensive 可相同）；管理员配置层才暴露厂商 model。

## 待拍板

- tier 标签集合阶段 1 是否就落 cheap/expensive 两个？
- 模态组合无解时（text+image+audio 无单模型支持）：先报错 vs 拆解路由？

## 资源索引（多模态的必然伴生问题）

三种传递方式本质 = 值传递 vs 引用传递：
- base64 内联 = 值传递：同步无状态简单，但吃 48MiB 请求体、单图 32MiB、复用场景重复传。
- 外部 URL = 已有引用：不占请求体，但要公网可达（8192 字符 / 60s 下载超时）+ SSRF/隐私风险。
- Files file_id = 自注册引用：复用 + 突破大小（64MiB），但多一步异步上传 + 有存储配额/过期/状态句柄。

对设计影响（详见下轮讨论）：MediaRef 抽象归一三态；引入有状态"媒体资源管理层"（去重/缓存/大小策略/生命周期）；上传决策内化进 llm-service 不泄漏 file_id 概念；阶段 1 先 base64 内联、MediaRef 预留 url/file。
