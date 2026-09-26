#!/usr/bin/env python3.11
"""Summarise probe runs: probe stats + a11y event rates per window."""
import glob
import os
import re
import statistics as st

RUNS = os.path.join(os.path.dirname(__file__), "runs")


def parse_probe(path):
    cpu, fps, proc, frames, chg = [], [], [], 0, 0
    for ln in open(path):
        m = re.search(
            r"fps=([-\d.]+) avg_interval_ms=([\d.]+) avg_proc_ms=([\d.]+) "
            r"frames=(\d+) chg_frames=(\d+).*cpu=([\d.]+)%", ln)
        if not m:
            continue
        f = float(m.group(1))
        if f > 0:
            fps.append(f)
        proc.append(float(m.group(3)))
        frames = int(m.group(4))
        chg = int(m.group(5))
        cpu.append(float(m.group(6)))
    if not cpu:
        return None
    return dict(cpu_mean=st.mean(cpu), cpu_max=max(cpu), fps_mean=st.mean(fps) if fps else 0,
                proc_mean=st.mean(proc), frames=frames, chg=chg)


def parse_a11y(path):
    rates, total, per = [], 0, {}
    for ln in open(path):
        m = re.search(r"event_rate=([\d.]+)/s total=(\d+)", ln)
        if m:
            rates.append(float(m.group(1)))
            total = max(total, int(m.group(2)))
        m2 = re.search(r"DUMP total=(\d+) \| (.*)", ln)
        if m2:
            total = max(total, int(m2.group(1)))
            for kv in m2.group(2).split():
                if "=" in kv:
                    k, v = kv.split("=")
                    per[k] = int(v)
    return dict(rate_mean=st.mean(rates) if rates else 0, total=total, per=per)


print(f"{'window':<14}{'fps':>7}{'proc_ms':>9}{'cpu_mean':>10}{'cpu_max':>9}"
      f"{'frames':>8}{'chg_fr':>8}{'chg%':>7}{'a11y/s':>9}{'a11y_tot':>10}")
for tag in ("q270", "h540", "full", "clean", "final"):
    for kind in ("idle", "load"):
        p = sorted(glob.glob(f"{RUNS}/{tag}-{kind}-*-probe.txt"))
        a = sorted(glob.glob(f"{RUNS}/{tag}-{kind}-*-a11y.txt"))
        if not p:
            continue
        pr = parse_probe(p[-1])
        ar = parse_a11y(a[-1]) if a else None
        if not pr:
            continue
        chgp = 100.0 * pr["chg"] / pr["frames"] if pr["frames"] else 0
        print(f"{tag+'/'+kind:<14}{pr['fps_mean']:>7.1f}{pr['proc_mean']:>9.2f}"
              f"{pr['cpu_mean']:>10.1f}{pr['cpu_max']:>9.1f}{pr['frames']:>8}{pr['chg']:>8}"
              f"{chgp:>6.0f}%{(ar['rate_mean'] if ar else 0):>9.1f}"
              f"{(ar['total'] if ar else 0):>10}")

# a11y event-type mix on load windows
print("\na11y event mix (load):")
for tag in ("q270", "h540", "full"):
    a = sorted(glob.glob(f"{RUNS}/{tag}-load-*-a11y.txt"))
    if not a:
        continue
    ar = parse_a11y(a[-1])
    top = sorted(ar["per"].items(), key=lambda kv: -kv[1])[:8]
    print(f"  {tag}: total={ar['total']} " + " ".join(f"{k}={v}" for k, v in top))
