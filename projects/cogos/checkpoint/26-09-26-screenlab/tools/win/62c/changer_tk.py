import ctypes, ctypes.wintypes as wt, json, os, sys, time

DIR = os.path.dirname(os.path.abspath(__file__))
MARK = os.path.join(DIR, "changer.marker")
DURATION = float(sys.argv[1]) if len(sys.argv) > 1 else 8.0
PERIOD = float(sys.argv[2]) if len(sys.argv) > 2 else 0.1


def write(m):
    t = MARK + ".tmp"
    with open(t, "w") as f:
        f.write(m)
    os.replace(t, MARK)


root_ok = True
try:
    import tkinter as tk
    root = tk.Tk()
except Exception as e:  # noqa
    root_ok = False

if not root_ok:
    write("END 0 0 NO_TK")
    sys.exit(0)

root.overrideredirect(True)
c = tk.Canvas(root, width=200, height=120, bg="black", highlightthickness=0)
c.pack()
rect = c.create_rectangle(0, 0, 200, 120, fill="#ff0000", outline="")
positions = [(40, 40), (400, 40), (40, 300), (500, 500), (700, 200)]
colors = ["#ff0000", "#00ff00", "#0000ff", "#ffff00", "#ff00ff"]

start = time.time()
i = 0
write("START %.3f" % start)


def step():
    global i
    if time.time() - start >= DURATION:
        write("END %.3f %d" % (time.time(), i))
        root.destroy()
        return
    x, y = positions[i % len(positions)]
    root.geometry("200x120+%d+%d" % (x, y))
    c.itemconfig(rect, fill=colors[i % len(colors)])
    c.coords(rect, 0, 0, 40 + (i % 5) * 30, 40 + (i % 3) * 20)
    i += 1
    write("TICK %.3f %d %d,%d" % (time.time(), i, x, y))
    root.after(int(PERIOD * 1000), step)


root.after(int(PERIOD * 1000), step)
root.mainloop()
write("EXIT %.3f %d" % (time.time(), i))
