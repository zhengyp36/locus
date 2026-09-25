#!/usr/bin/env python3
"""ctx - 报告当前 Kilo 会话的上下文用量（一行，极省）。

用法:
    python3 tools/ctx.py              # 最近更新的会话（= 当前）
    python3 tools/ctx.py <session_id> # 指定会话

输出示例:
    ctx 160k/1000k (16%) msgs=123  handoff-screen-27.md 情况介绍  [/home/zhengyp/work/A/locus]
"""
import json
import os
import sqlite3
import sys

DB = os.path.expanduser("~/.local/share/kilo/kilo.db")
MODELS = os.path.expanduser("~/.cache/kilo/models.json")
FALLBACK_LIMIT = 1_000_000


def _find(obj, pred):
    if isinstance(obj, dict):
        if pred(obj):
            return obj
        for v in obj.values():
            r = _find(v, pred)
            if r:
                return r
    elif isinstance(obj, list):
        for x in obj:
            r = _find(x, pred)
            if r:
                return r
    return None


def limit_for(model_field):
    try:
        mid = (json.loads(model_field or "{}") or {}).get("id", "")
    except Exception:
        mid = ""
    if not mid:
        return FALLBACK_LIMIT
    try:
        data = json.load(open(MODELS))
    except Exception:
        return FALLBACK_LIMIT
    hit = _find(data, lambda d: d.get("id") == mid and isinstance(d.get("limit"), dict))
    if hit:
        return int(hit["limit"].get("context") or FALLBACK_LIMIT)
    return FALLBACK_LIMIT


def main():
    con = sqlite3.connect(DB)
    if len(sys.argv) > 1:
        row = con.execute(
            "select id,title,directory,model from session where id=?", (sys.argv[1],)
        ).fetchone()
    else:
        # 默认取"最近更新的会话"，但优先限定在**当前工作目录**，避免串到别的项目
        cwd = os.getcwd()
        row = con.execute(
            "select id,title,directory,model from session where directory=? "
            "order by time_updated desc limit 1",
            (cwd,),
        ).fetchone()
        if not row:
            row = con.execute(
                "select id,title,directory,model from session order by time_updated desc limit 1"
            ).fetchone()
    if not row:
        print("ctx: no session found")
        return 1
    sid, title, directory, model = row

    cur = 0
    for (_mid, data) in con.execute(
        "select id,data from message where session_id=? order by time_created desc limit 10",
        (sid,),
    ):
        try:
            t = (json.loads(data) or {}).get("tokens") or {}
        except Exception:
            continue
        tot = t.get("total") or (
            (t.get("input") or 0)
            + (t.get("output") or 0)
            + (t.get("reasoning") or 0)
            + ((t.get("cache") or {}).get("read") or 0)
        )
        if tot:
            cur = int(tot)
            break
    n = con.execute("select count(*) from message where session_id=?", (sid,)).fetchone()[0]
    lim = limit_for(model)
    pct = (100.0 * cur / lim) if lim else 0.0
    print(
        "ctx %.0fk/%.0fk (%.0f%%) msgs=%d  %s  [%s]"
        % (cur / 1000.0, lim / 1000.0, pct, n, title or "", directory or "")
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
