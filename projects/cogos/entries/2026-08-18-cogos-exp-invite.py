import asyncio

import group


async def main():
    b1, b2 = group.bot1, group.bot2
    await group.get_token(b1)
    await group.get_token(b2)

    HUMAN = "125cf5a4"

    print("=== A: bot1 create chat, set public, invite bot2 (app_id) ===")
    cid = await group.create_chat(b1, "exp-invite-public", "private")
    print("created (private):", cid)
    r = await group.update_chat(b1, cid, "public")
    print("set public:", r)
    r = await group.invite(b1, cid, [b2["app_id"]], "app_id")
    print("invite bot2 (app_id) under public:", r)

    print("=== B: invite human (user_id) under public ===")
    r = await group.invite(b1, cid, [HUMAN], "user_id")
    print("invite human under public:", r)

    print("=== C: private chat invite human (user_id) ===")
    cid2 = await group.create_chat(b1, "exp-invite-private", "private")
    print("created (private):", cid2)
    r = await group.invite(b1, cid2, [HUMAN], "user_id")
    print("invite human under private:", r)


asyncio.run(main())
