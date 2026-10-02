# 26-10-03 第一刀证据

> 收口件 `entries/2026-10-03-cogos-first-cut-flow-claim.md` · `entries/2026-10-03-cogos-projection-experiment-e1.md`；本目录＝正式验收证据（原始数据，非叙述）。

- `first-cut-log.md` — 第一刀执行日志 / 决策点 D1–D8 / 环境侦察。
- `probe-result.json` — 语义探针（真 deepseek-v4-flash＋FakeTelecom，固定事件 × 两套『我』）：take→采纳=理（toolbox×4、外发1、段过程6）；ignore→采纳=不理（0/0）。`采纳 diverged`。
- `real_e2e_segment.jsonl` — 真实身份 e2e（真 daemon＋lm-service＋真 app `~/.cogos/agent/tangyu`；真机 `李恪 A0001 → 唐钰 A0005`，默认『我』）：采纳=不理、结=了、过程空、未回复。
- E1（投影必要性实验）：
  - `e1-experiment.md` — 命题/四臂/度量/用例（C1–C3、陷阱 T1/T2）。
  - `e1-results.md` — C1/T1/T2 均天花板；A vs C 不可分辨；C 膨胀负向观察。
  - `e1-run_arm.py` — 跑臂脚本。
  - `out-t1-A.txt` `out-t1-C.txt` `out-t2-A.txt` `out-t2-C.txt` — T1/T2 各臂 4 拍原始输出。
