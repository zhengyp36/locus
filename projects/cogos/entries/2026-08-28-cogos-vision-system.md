# 2026-08-28 · 视觉系统预研（过程与决策脉络）

结论已固化 `docs/vision-system-design.md`，此文只记脉络与决策背景，不重复结论。

## 脉络

底层三件讨论起步 → 多模态成为 lm-service 接口必答题（cp-11 调研各厂商多模态支持）→ 引出感知子系统如何组织（cp-12）→ 视觉信息如何进入意识（cp-14）。08-27 ~ 08-28。

## YZ 拍板记录

- 接口沿用 message/content 数组 + 内部 type 标签 + MediaRef；model 用 tier×modality 两正交维度（cp-11）。
- 资源索引不做：媒体资源管理层（去重/缓存/生命周期）不做，阶段 1 base64 内联（cp-12，覆盖 cp-11 末初步想法）。
- lm-service = 底层 io 抽象；cog-unit = 之上的调度（zio 流水线类比）。
- scale 旋钮不在意识手里：意识只发 range 意图，scale 归视觉子系统内部。
- 被 cp-14 覆盖的 cp-12 旧表述已删，以 cp-14 为准（原图+index 取代缩略图/中央凹类比）。

## 待拍板 6 项

index 编码格式 / 记忆图像骨架 / 存图 raw trace 边界 / 取图动作落点 / 纸形态 / 对焦判断实现。详见 docs/vision-system-design.md「待拍板」。

## 钩子

- 阶段 1 认知树 schema 预留感知事件结构（内容+通道+序位+同时组）→ 已挂 cogos-plan.md。
- 上网 = 工具层 = 身体（上网=眼）→ docs/webtool-design.md，设计意图/感知时看。
