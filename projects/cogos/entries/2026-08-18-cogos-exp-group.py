import asyncio

import group


async def main():
    b1, b2, b3 = group.bot1, group.bot2, group.bot3
    await group.get_token(b1)
    await group.get_token(b2)
    await group.get_token(b3)

    print("=== step1: bot1 create public chat ===")
    cid = await group.create_chat(b1, "exp-public-1", "public")
    print("chat_id:", cid)

    r = await group.enter_chat(b2, cid)
    print("bot2 enter (expect ok):", r)
    if r.get("code") != 0:
        print("STOP: bot2 enter failed")
        return

    print("=== step2: bot1 update to private ===")
    r = await group.update_chat(b1, cid, "private")
    print("update private:", r)

    r = await group.enter_chat(b3, cid)
    print("bot3 enter (expect fail):", r)

    print("=== step3: bot1 update back to public ===")
    r = await group.update_chat(b1, cid, "public")
    print("update public:", r)

    r = await group.enter_chat(b3, cid)
    print("bot3 enter (expect ok):", r)
    if r.get("code") != 0:
        print("STOP: bot3 enter failed")
        return

    print("=== step4: bot1 create private chat then update to public ===")
    cid2 = await group.create_chat(b1, "exp-private-2", "private")
    print("chat_id:", cid2)

    r = await group.update_chat(b1, cid2, "public")
    print("update to public (expect ok):", r)


asyncio.run(main())
