import random
import subprocess
import sys
import time


def xdo(*a):
    subprocess.run(['xdotool', *[str(v) for v in a]], check=False,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


sx, sy = int(sys.argv[1]), int(sys.argv[2])
ex, ey = int(sys.argv[3]), int(sys.argv[4])
N = int(sys.argv[5]) if len(sys.argv) > 5 else 70
T = float(sys.argv[6]) if len(sys.argv) > 6 else 1.3
random.seed()


def smooth(u):
    return u * u * (3 - 2 * u)


xdo('mousemove', sx, sy)
time.sleep(0.25)
intervals = []
last = time.time()
for i in range(1, N + 1):
    u = i / N
    e = smooth(u)
    x = sx + (ex - sx) * e + random.uniform(-1.5, 1.5)
    y = sy + (ey - sy) * e + random.uniform(-1.5, 1.5)
    xdo('mousemove', int(x), int(y))
    dt = T / N * random.uniform(0.7, 1.4)
    time.sleep(dt)
    now = time.time()
    intervals.append(now - last)
    last = now

time.sleep(random.uniform(0.08, 0.2))
ox = ex + random.uniform(8, 22)
oy = ey + random.uniform(6, 16)
xdo('mousemove', int(ox), int(oy))
time.sleep(0.06)
xdo('mousemove', ex, ey)
time.sleep(0.1)
xdo('click', 1)

print("STEPS=%d target=(%d,%d) dur=%.2f interval min=%.4f max=%.4f avg=%.4f"
      % (N, ex, ey, T, min(intervals), max(intervals), sum(intervals) / len(intervals)))
