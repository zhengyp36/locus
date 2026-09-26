"""Launcher for the screen/1 daemon on Windows.

Started from the Startup folder so it runs inside the *interactive* session
of this user (Session 0 / sshd has no desktop). Listens on loopback TCP;
reach it from Linux with:  ssh -L 9911:127.0.0.1:9911 screen@HOST
"""
import datetime
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.chdir(HERE)

_log = open(os.path.join(HERE, "daemon.log"), "a", buffering=1, encoding="utf-8")
sys.stdout = sys.stderr = _log
print("--- start %s ---" % datetime.datetime.now())

from screenlab.cli import main  # noqa: E402

main(["--tcp", "127.0.0.1:9911", "daemon", "--blob-dir", os.path.join(HERE, "blobs")])
