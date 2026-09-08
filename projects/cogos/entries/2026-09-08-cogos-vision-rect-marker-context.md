# 2026-09-08 cogos 视觉 · 矩形/十字伪影 + 上下文管理重设计

会话：用 Xftp 截图 windows.png 测「agent 点击坐标精度」，顺手做工具原语 + 深挖视觉上下文管理。

## 坐标精度（单次前向不可信再坐实）
- windows.png = Xftp8 截图 1357×764。「工具(T)」真值归一化 ≈ [0.188,0.042]（像素 (255,32)）。
- 裸眼全屏：大方向对、小文字目标(菜单项)定不准，工具/帮助偏 ±20px。
- 模型非确定：同一图 工具(T) 一次给 [0.188] (准)、另次给 [0.55] (错 ~490px)。
- thinking 这次反而添乱：thinking 12.3s 把整图误读成"渐变背景+散乱方框"退回去猜 0.55；no-thinking 3.1s 给准 → 证明思考=非单调、不可靠，别当通则。
- 复读/parroting：模型连续 4 次发完全相同的 view + "还是模糊再凑近"，center 不变。

## 工具原语（已落地 + 接入 vf6）
- 矩形视野 + 中心十字(aim marker)：`Viewer.view_box(center,size,step,shape,mark,mark_pt)`，size 相对短边、归一化[0,1]、只缩不放大。圆=size[r,r]+circle，旧 view() 兼容。
- 接入 vf6：SYSTEM(center/size/radius、shape、mark)、map_to_pano 矩形链、exec_action 接 size/shape/mark、save_trail 画矩形+十字、new_view/annotate_label→size。冒烟：模型发出 shape=rect size[0.12,0.03]，crop 91×23。
- 矩形对表格/UI 净收益：聚焦文件列表行 rect 框整行、circle 只能 77×77 灰色读不了行。
- 原型 `vf_box_proto.py`；验证产物 `/tmp/kilo/vision/proto/` + `_aim_cmp.png`、`_menu_ruler.png`、`_crop_*.png`。

## 上下文管理重设计（定案，未实现；治复读/不膨胀的本）
- 图组织模型：上下文=串行消息流；图作为某条观察消息的附件，**出现一次**，下一轮不再发出(摘图块、留文字行)。图数有界：LIVE 张常驻(全景1+最新视图1，建议 LIVE=2)，更老的观察降级为文字行。contexts 只作动作轨迹+重看兜底，**不再每轮重灌组图**。
- 模型怎么"知道图变了/对了"：不靠记一堆旧图，靠 ①当前新鲜图 ②文字状态(我瞄哪/上步结论) ③可感知增量+十字(参数行 center 0.55→0.188；十字压住目标→"对了")。「变化」=最新图 vs 文字预期。
- 复读根因诊断：旧 run_step 每轮发 [system]+[历史含模型自己长文原文]+[frame_parts]+[user build_vision(全景+全部fovea重灌)]。三因: (a)模型自己长文原样回喂→续写模板 (b)每轮同批静态图+同一指令→无增量 (c)无收敛/增量信号→感知不到动作是否生效，反复同一计划。根在上下文组织+反馈信号，不在模型能力；单次前向不可信是放大器。
- 待实现：改 run_step + State → history 项带 kind(text/obs)、每条 view/open 生成一条 obs 消息、编译时 obs 留最新 LIVE 张带图其余文字、加薄动作状态行、budget LIFE=2/BUDGET≈20-24(待 YZ 定)、删 build_vision。

## 遗留/待办
- 落地上下文重设计(A/B 测工具(T)：复读次数、命中收敛 [0.188,0.042])。
- 交叉验证/读两遍/证据引用+不确定出口并入主流程。
- finish_reason=length 处理；shape/mark 默认值兜底(rect+mark true)。

## 关键文件
- 工具/测试：/tmp/kilo/vision/{vf6.py,vf_tool.py,vf_box_proto.py}、vf6_repl_out_new/windows.png。
- 上游交接 checkpoint/principle-exp/；本会话交接 `handoff-vf6-rect-marker-context.md`。
