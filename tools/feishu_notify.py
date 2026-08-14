#!/usr/bin/env python3.11
"""Send a Feishu text message to a registered user (default: alias YZ).

Usage:
    tools/feishu_notify.py "text to send" [bot_name] [alias]
    echo "text to send" | tools/feishu_notify.py   # read message from stdin

Dependencies (kept outside this repo):
    ~/.secrets/feishu.key        -> {"bots": [{"name": ..., "app_id": ..., "app_secret": ...}]}
    ~/.secrets/feishu-users.json -> {"users": {"<alias>": {"user_id": "..."}}}
"""
import json
import sys
from pathlib import Path

import httpx

KEY = Path.home() / ".secrets" / "feishu.key"
USERS = Path.home() / ".secrets" / "feishu-users.json"
TOKEN_URL = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
MSG_URL = "https://open.feishu.cn/open-apis/im/v1/messages"


def get_token(bot_name):
    data = json.loads(KEY.read_text())
    for b in data["bots"]:
        if b["name"] == bot_name:
            r = httpx.post(
                TOKEN_URL,
                json={"app_id": b["app_id"], "app_secret": b["app_secret"]},
                timeout=10,
            ).json()
            if r.get("code") != 0:
                raise RuntimeError(f"token error: {r}")
            return r["tenant_access_token"]
    raise ValueError(f"bot {bot_name!r} not found in {KEY}")


def main():
    args = sys.argv[1:]
    if not args or args[0] == "-":
        text = sys.stdin.read().strip()
        args = args[1:]
    else:
        text = args[0]
        args = args[1:]
    bot_name = args[0] if args else "admin-cli-test"
    alias = args[1] if len(args) > 1 else "YZ"

    users = json.loads(USERS.read_text())["users"]
    if alias not in users:
        sys.exit(f"alias {alias!r} not found in {USERS}; known: {list(users)}")
    user_id = users[alias]["user_id"]

    token = get_token(bot_name)
    r = httpx.post(
        MSG_URL,
        params={"receive_id_type": "user_id"},
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        },
        json={
            "receive_id": user_id,
            "msg_type": "text",
            "content": json.dumps({"text": text}),
        },
        timeout=10,
    ).json()
    if r.get("code") != 0:
        sys.exit(f"send failed: {r}")
    print(json.dumps(r, ensure_ascii=False))


if __name__ == "__main__":
    main()
