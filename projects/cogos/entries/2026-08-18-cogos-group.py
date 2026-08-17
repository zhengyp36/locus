import argparse
import asyncio
import json
import os
import re
import sys
import time
from datetime import datetime
from urllib.parse import urlencode

import aiohttp
import qrcode

REG_URL = "https://accounts.feishu.cn/oauth/v1/app/registration"
TOKEN_URL = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
CHAT_URL = "https://open.feishu.cn/open-apis/im/v1/chats"
MSG_URL = "https://open.feishu.cn/open-apis/im/v1/messages"
POLL_TIMEOUT = 600

try:
    from lark_oapi.core.enum import LogLevel
    from lark_oapi.event.dispatcher_handler import EventDispatcherHandler
    from lark_oapi.ws import Client as WSClient
except ImportError:
    print("请先安装 lark-oapi: pip install lark-oapi", file=sys.stderr)
    sys.exit(1)

bot1 = {
    'app_id' : 'cli_aa09845162789be5',
    'app_secret': ''
}

bot2 = {
    'app_id' : 'cli_aa0984b147f89bce',
    'app_secret': ''
}

bot3 = {
    'app_id' : 'cli_aa098519f4389bcd',
    'app_secret': ''
}

async def get_token(bot) -> str:
    app_id = bot['app_id']
    app_secret = bot['app_secret']
    async with aiohttp.ClientSession() as s:
        async with s.post(TOKEN_URL, json={"app_id": app_id, "app_secret": app_secret}) as r:
            data = await r.json()
            if data.get("code") != 0:
                raise RuntimeError(f"获取 token 失败: {data}")
            bot['token'] = data["tenant_access_token"]
            return data["tenant_access_token"]

async def create_chat(bot, name: str, chat_type: str = "public") -> str:
    token = bot['token']
    h = {"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=utf-8"}
    async with aiohttp.ClientSession() as s:
        async with s.post(CHAT_URL, json={"name": name, "chat_type": chat_type}, headers=h) as r:
            data = await r.json()
            if data.get("code") != 0:
                raise RuntimeError(f"建群失败: {data}")
            if 'group' not in bot:
                bot['group'] = []
            bot['group'].append((name, data["data"]["chat_id"]))
            return data["data"]["chat_id"]

async def enter_chat(bot, chat_id: str):
    token = bot['token']
    h = {"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=utf-8"}
    url = f"{CHAT_URL}/{chat_id}/members/me_join"
    async with aiohttp.ClientSession() as s:
        async with s.patch(url, json={}, headers=h) as r:
            data = await r.json()
            return data

async def invite(bot, chat_id: str, id_list, member_id_type: str):
    token = bot['token']
    h = {"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=utf-8"}
    url = f"{CHAT_URL}/{chat_id}/members?member_id_type={member_id_type}"
    async with aiohttp.ClientSession() as s:
        async with s.post(url, json={"id_list": id_list}, headers=h) as r:
            data = await r.json()
            return data

async def update_chat(bot, chat_id: str, chat_type: str):
    token = bot['token']
    h = {"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=utf-8"}
    url = f"{CHAT_URL}/{chat_id}"
    async with aiohttp.ClientSession() as s:
        async with s.put(url, json={"chat_type": chat_type}, headers=h) as r:
            data = await r.json()
            return data
