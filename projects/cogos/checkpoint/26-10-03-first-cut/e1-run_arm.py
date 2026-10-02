#!/usr/bin/env python3.11
"""E1 step-runner: run ONE case, ONE arm, N rounds; print every round.

手动用：一次只跑一条臂，逐拍人读。不是批量 harness。
"""
import asyncio
import sys

sys.path.insert(0, "/home/zhengyp/work/A/cogos")

from cogos.lm_service.client import LmClient, LmServiceError
from cogos.lm_service.config import Config

C1 = """你是运维诊断助手。你没有外部工具，只能依据下面给出的全部信息推理，不得引入未给出的信息。请给出故障根因，并给出你的推理过程。

现象：
ingest 服务每天 03:00–03:12 对"归档分片"的写入出现超时告警；其他分片、其他时段均正常。

已知信息：
E1. 该时段整体 QPS 比平时高约 30%，形成一个夜间小高峰。
E2. 最近两周没有任何部署或配置变更。
E3. 发生超时的分片分布，与"当天各地区活跃用户分布"不相关；只与"记录是否属于本季度待归档批次"强相关。
E4. 每天 03:00 有一条定时任务 archive_rotate，它对归档目录做一次旋转，并在一个大事务里更新 archive_meta 表，大事务持锁约 10 分钟。
E5. ingest 在写入归档分片之前，必须先读取 archive_meta 来决定路由。
E6. 非归档分片的写入路径不读取 archive_meta。

请给出根因。"""

T1 = """你是故障诊断助手。你没有外部工具，只能依据下面给出的全部信息推理，不得引入未给出的信息。请给出根因，并给出你的推理过程。

现象：
监控仪表盘显示，某在线服务在每个整点（HH:00）出现一次持续约 10 秒的 CPU 尖峰和接口延迟尖峰，其他时间完全平稳。运维初步怀疑"每小时有一个定时任务"。

已知信息：
E1. 应用代码及其依赖中，不存在任何按"每小时"触发的定时任务；也没有任何外部批处理或上游任务在整点调用它。
E2. 独立的用户侧指标系统（与监控系统不同源）显示，成功率与延迟在整点没有任何变化。
E3. 监控系统每 15 秒采集一个采样点，图表把相邻采样点用折线相连。
E4. 监控采集器在每分钟的 :00、:15、:30、:45 各采集一次；其中整点这次采集，恰好与采集器自身对一个大日志文件做轮转（rotation）发生在同一时刻，轮转会短暂占用采集器所在主机的 CPU。
E5. 图中"整点尖峰"的宽度恰好约等于一个采集周期（15 秒）。
E6. 尖峰期间，被监控服务自身进程的 CPU 使用率（由另一采集来源监控）保持平稳。

请给出根因。"""

T2 = """你是排班助手。你没有外部工具，只能依据下面给出的全部信息推理，不得引入未给出的信息、也不得增删条件。请给出一个满足全部条件的排班；若不存在这样的排班，请给出严格的理由。

任务：
为 3 名员工 A、B、C 安排下周一至周日（共 7 天）。每天恰好安排 1 名"主管"和 1 名"备班"（两人必须是不同的人），剩下的 1 人休息。

硬性条件：
C1. 一周内，A 担任主管恰好 2 天。
C2. 一周内，B 担任主管恰好 2 天。
C3. 一周内，C 担任主管恰好 3 天。
C4. A 与 B 从不在同一天上班（无论担任主管还是备班）。
C5. 一周内，C 担任备班恰好 3 天。

请给出排班，或说明为何不存在。"""

CASES = {"c1": C1, "t1": T1, "t2": T2}

ARMS = {
    "A": "继续。",
    "B": "请更仔细、更深入地继续分析。",
    "C": "对回目标：目标的哪些要求或约束还没有被满足、被验证？当前最不确定的一步是什么？请据此继续。",
    "D": "对回『我』：你此前承诺或预测了什么？哪条未了的线索被你丢了？你现在的立场与之前是否自洽？请据此继续。",
}


def _text(content):
    if not content:
        return ""
    return "".join(p.get("text", "") for p in content if isinstance(p, dict))


def _internal_key():
    cfg = Config()
    cfg.load()
    for ik in cfg.list_internal_keys():
        if ik["status"] == "active":
            return ik["id"]
    raise SystemExit("no active internal key")


async def main():
    case = sys.argv[1] if len(sys.argv) > 1 else "c1"
    arm = sys.argv[2] if len(sys.argv) > 2 else "A"
    rounds = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    task = CASES[case]
    client = LmClient(_internal_key())
    msgs = [{"role": "user", "content": task}]
    for r in range(rounds):
        try:
            resp = await client.chat(
                msgs, tier="basic", max_tokens=1500, temperature=0
            )
        except LmServiceError as e:
            print(f"[error round {r}] {e}")
            return
        text = _text(resp.get("content"))
        print(f"\n===== {case} / arm {arm} / round {r} =====")
        print(text)
        if resp.get("reasoning"):
            print(f"[reasoning] {resp['reasoning']}")
        print(f"[usage] {resp.get('usage')}")
        msgs.append({"role": "assistant", "content": text})
        if r < rounds - 1:
            msgs.append({"role": "user", "content": ARMS[arm]})


if __name__ == "__main__":
    asyncio.run(main())
