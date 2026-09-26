#!/usr/bin/env python3.11
"""Host driver for the screenlab Android screen-change probe.

Usage:
  drive.py start [--w W] [--h H] [--cell PX] [--thresh N]
  drive.py load  (--swipe N | --tap X Y:... ) [--interval-ms MS]
  drive.py collect [--tag LABEL]
  drive.py stop
  drive.py a11y-on
  drive.py a11y-off

Requires wifi adb device already connected (192.168.1.175:5555).
"""
import argparse
import re
import subprocess
import sys
import time

DEV = "192.168.1.175:5555"
PKG = "com.screenlab.probe"
ACT = f"{PKG}/.ProbeActivity"
A11Y = f"{PKG}/.ProbeA11yService"
ASSIST_A11Y = "com.screenlab.assist/.InjectService"
EXT = f"/sdcard/Android/data/{PKG}/files"
OUT = "/home/zhengyp/work/A/checkpoint/tools/android-probe/runs"


def sh(cmd, timeout=60):
    if isinstance(cmd, str):
        cmd = ["bash", "-lc", cmd]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return p.stdout


def adb(*args, **kw):
    return sh(["adb", "-s", DEV, *args], **kw)


def shell(cmd, **kw):
    return adb("shell", cmd, **kw)


def get_enabled_a11y():
    v = shell("settings get secure enabled_accessibility_services").strip()
    return "" if v in ("", "null") else v


def set_enabled_a11y(val):
    shell(f"settings put secure enabled_accessibility_services '{val}'")
    shell(f"settings put secure accessibility_enabled {1 if val else 0}")


def a11y_on():
    cur = get_enabled_a11y()
    parts = [p for p in cur.split(":") if p]
    if A11Y not in parts:
        parts.append(A11Y)
    set_enabled_a11y(":".join(parts))
    print("a11y ->", get_enabled_a11y(), "enabled=",
          shell("settings get secure accessibility_enabled").strip())


def a11y_off():
    cur = get_enabled_a11y()
    parts = [p for p in cur.split(":") if p and p != A11Y]
    set_enabled_a11y(":".join(parts))
    print("a11y ->", get_enabled_a11y())


def dump_ui():
    shell("uiautomator dump /sdcard/wd.xml >/dev/null 2>&1")
    return sh(["adb", "-s", DEV, "exec-out", "cat", "/sdcard/wd.xml"])


def tap_text(*texts, tries=25):
    """Poll the UI hierarchy and tap the first node whose text matches."""
    for _ in range(tries):
        xml = dump_ui()
        for t in texts:
            for m in re.finditer(r'text="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml):
                if t in m.group(1):
                    x = (int(m.group(2)) + int(m.group(4))) // 2
                    y = (int(m.group(3)) + int(m.group(5))) // 2
                    shell(f"input tap {x} {y}")
                    print(f"tapped '{m.group(1)}' at {x},{y}")
                    return True
        time.sleep(0.5)
    return False


def start(w, h, cell, thresh):
    a11y_on()
    shell(f"am force-stop {PKG}")
    shell("logcat -c")
    shell(f"rm -f {EXT}/probe-stats.txt {EXT}/a11y-stats.txt")
    shell(f"am start -n {ACT} --ei w {w} --ei h {h} --ei cell {cell} --ei thresh {thresh}")
    ok = tap_text("立即开始", "开始", "Start now", "Start", "允许", "Allow")
    if not ok:
        print("WARN: consent button not found; dumping for inspection")
        sys.stdout.write(dump_ui()[:4000])
    time.sleep(1.5)
    print(shell(f"dumpsys activity services {PKG} | grep -E 'ServiceRecord|isForeground' | head -5"))


def load_swipe(n, interval_ms):
    for i in range(n):
        shell("input swipe 540 1800 540 600 250")
        time.sleep(interval_ms / 1000.0)


def load_tap(spec, interval_ms):
    coords = []
    for part in spec.split(":"):
        x, y = part.split(",")
        coords.append((int(x), int(y)))
    for i in range(len(coords)):
        x, y = coords[i]
        shell(f"input tap {x} {y}")
        time.sleep(interval_ms / 1000.0)


def collect(tag):
    import os
    os.makedirs(OUT, exist_ok=True)
    ts = time.strftime("%H%M%S")
    base = f"{OUT}/{tag or 'run'}-{ts}"
    stats = sh(["adb", "-s", DEV, "exec-out", "cat", f"{EXT}/probe-stats.txt"],
               timeout=60) if False else shell(f"cat {EXT}/probe-stats.txt 2>/dev/null")
    a11y = shell(f"cat {EXT}/a11y-stats.txt 2>/dev/null")
    log = sh(["adb", "-s", DEV, "logcat", "-d", "-s", "screenprobe:V", "screenprobe.a11y:V"])
    with open(base + "-probe.txt", "w") as f:
        f.write(stats)
    with open(base + "-a11y.txt", "w") as f:
        f.write(a11y)
    with open(base + "-log.txt", "w") as f:
        f.write(log)
    print("saved", base, "probe lines:", len(stats.splitlines()),
          "a11y lines:", len(a11y.splitlines()))
    print("--- probe tail ---")
    print("\n".join(stats.splitlines()[-6:]))


def stop():
    shell(f"am broadcast -n {PKG}/.ProbeCmdReceiver -a com.screenlab.probe.CMD --es op stop")
    time.sleep(1)
    print(shell(f"pidof {PKG}") or "(probe stopped)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["start", "load", "collect", "stop", "a11y-on", "a11y-off"])
    ap.add_argument("--w", type=int, default=270)
    ap.add_argument("--h", type=int, default=578)
    ap.add_argument("--cell", type=int, default=24)
    ap.add_argument("--thresh", type=int, default=24)
    ap.add_argument("--swipe", type=int, default=0)
    ap.add_argument("--tap", default="")
    ap.add_argument("--n", type=int, default=0)
    ap.add_argument("--interval-ms", type=int, default=300)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    if a.cmd == "start":
        start(a.w, a.h, a.cell, a.thresh)
    elif a.cmd == "load":
        if a.tap:
            load_tap(a.tap, a.interval_ms)
        else:
            load_swipe(a.n or 10, a.interval_ms)
    elif a.cmd == "collect":
        collect(a.tag)
    elif a.cmd == "stop":
        stop()
    elif a.cmd == "a11y-on":
        a11y_on()
    elif a.cmd == "a11y-off":
        a11y_off()


if __name__ == "__main__":
    main()
